#!/usr/bin/env python3
"""Benchmark common local OpenVINO artifact types with repeatable output."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from path_utils import normalize_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark an OpenVINO model artifact.")
    parser.add_argument("model_dir", type=Path)
    parser.add_argument("--kind", choices=["llm", "embedding", "generic"], required=True)
    parser.add_argument("--devices", nargs="+", default=["CPU"])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--prompt", default="请用一句话介绍 OpenVINO。")
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--shape", help="Shape string for benchmark_app generic mode.")
    parser.add_argument("--hint", default="latency", help="benchmark_app -hint value for generic mode.")
    parser.add_argument("--seconds", type=int, default=30, help="benchmark_app duration for generic mode.")
    return parser.parse_args()


def load_config(model_dir: Path) -> dict:
    path = model_dir / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def bench_llm(args: argparse.Namespace) -> int:
    from optimum.intel.openvino import OVModelForCausalLM
    from transformers import AutoTokenizer

    cfg = load_config(args.model_dir)
    use_cache = cfg.get("use_cache", True)
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir,
        local_files_only=True,
        trust_remote_code=True,
        fix_mistral_regex=True,
    )
    inputs = tokenizer(args.prompt, return_tensors="pt")
    input_tokens = inputs["input_ids"].shape[-1]

    print("kind: llm")
    print(f"model_dir: {args.model_dir}")
    print(f"prompt_tokens: {input_tokens}")
    print(f"max_new_tokens: {args.max_new_tokens}")
    print(f"repeats: {args.repeats}")
    print(f"warmup: {args.warmup}")

    for device in args.devices:
        print(f"\n[{device}]")
        try:
            model = OVModelForCausalLM.from_pretrained(
                args.model_dir,
                local_files_only=True,
                trust_remote_code=True,
                device=device,
                use_cache=use_cache,
            )
            timings: list[float] = []
            token_counts: list[int] = []
            for idx in range(args.warmup + args.repeats):
                t0 = time.perf_counter()
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                )
                elapsed = time.perf_counter() - t0
                new_tokens = outputs.shape[-1] - input_tokens
                if idx >= args.warmup:
                    timings.append(elapsed)
                    token_counts.append(new_tokens)
            total_time = sum(timings)
            total_tokens = sum(token_counts)
            print(f"status: OK")
            print(f"avg_elapsed_sec: {total_time / len(timings):.3f}")
            print(f"avg_new_tokens: {total_tokens / len(token_counts):.1f}")
            print(f"tokens_per_sec: {total_tokens / total_time if total_time > 0 else 0:.3f}")
        except Exception as exc:
            print("status: FAIL")
            print(f"error: {exc}")
    return 0


def bench_embedding(args: argparse.Namespace) -> int:
    from optimum.intel.openvino import OVModelForFeatureExtraction
    from transformers import AutoTokenizer

    texts = ["hello openvino", "中文向量测试", "vector search benchmark"]
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir,
        local_files_only=True,
        trust_remote_code=True,
        fix_mistral_regex=True,
    )
    encoded = tokenizer(texts, padding=True, return_tensors="pt")

    print("kind: embedding")
    print(f"model_dir: {args.model_dir}")
    print(f"batch: {len(texts)}")
    print(f"repeats: {args.repeats}")
    print(f"warmup: {args.warmup}")

    for device in args.devices:
        print(f"\n[{device}]")
        try:
            model = OVModelForFeatureExtraction.from_pretrained(
                args.model_dir,
                local_files_only=True,
                trust_remote_code=True,
                device=device,
            )
            timings: list[float] = []
            shape = None
            for idx in range(args.warmup + args.repeats):
                t0 = time.perf_counter()
                output = model(**encoded)
                elapsed = time.perf_counter() - t0
                shape = tuple(output.last_hidden_state.shape)
                if idx >= args.warmup:
                    timings.append(elapsed)
            total = sum(timings)
            print("status: OK")
            print(f"shape: {shape}")
            print(f"avg_elapsed_sec: {total / len(timings):.3f}")
            print(f"batches_per_sec: {len(timings) / total if total > 0 else 0:.3f}")
            print(f"texts_per_sec: {len(timings) * len(texts) / total if total > 0 else 0:.3f}")
        except Exception as exc:
            print("status: FAIL")
            print(f"error: {exc}")
    return 0


def bench_generic(args: argparse.Namespace) -> int:
    xml_files = sorted(args.model_dir.glob("*.xml"))
    if not xml_files:
        print(f"ERROR no .xml files in {args.model_dir}")
        return 2
    model_xml = args.model_dir / "openvino_model.xml"
    if not model_xml.exists():
        model_xml = xml_files[0]
    if not shutil.which("benchmark_app"):
        print("ERROR benchmark_app not found in PATH")
        return 2

    print("kind: generic")
    print(f"model_xml: {model_xml}")
    for device in args.devices:
        print(f"\n[{device}]")
        cmd = [
            "benchmark_app",
            "-m",
            str(model_xml),
            "-d",
            device,
            "-hint",
            args.hint,
            "-t",
            str(args.seconds),
        ]
        if args.shape:
            cmd.extend(["-shape", args.shape])
        print("command:", " ".join(cmd))
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(proc.stdout)
        print(f"exit_code: {proc.returncode}")
    return 0


def main() -> int:
    args = parse_args()
    args.model_dir = normalize_path(args.model_dir)
    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")
    if not args.model_dir.exists():
        raise SystemExit(f"model_dir does not exist: {args.model_dir}")
    if args.kind == "llm":
        return bench_llm(args)
    if args.kind == "embedding":
        return bench_embedding(args)
    return bench_generic(args)


if __name__ == "__main__":
    raise SystemExit(main())
