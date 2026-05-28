#!/usr/bin/env python3
"""Small deterministic Optimum OpenVINO causal-LM smoke test."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from optimum.intel.openvino import OVModelForCausalLM
from transformers import AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test an OpenVINO causal LM export.")
    parser.add_argument("model_dir", type=Path)
    parser.add_argument("--device", default="CPU")
    parser.add_argument("--prompt", default="Say hello in one short sentence.")
    parser.add_argument("--max-new-tokens", type=int, default=32)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = args.model_dir / "config.json"
    use_cache = True
    if config_path.exists():
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        use_cache = cfg.get("use_cache", True)

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir,
        local_files_only=True,
        trust_remote_code=True,
        fix_mistral_regex=True,
    )
    model = OVModelForCausalLM.from_pretrained(
        args.model_dir,
        local_files_only=True,
        trust_remote_code=True,
        device=args.device,
        use_cache=use_cache,
    )

    inputs = tokenizer(args.prompt, return_tensors="pt")
    input_tokens = inputs["input_ids"].shape[-1]
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
    text = tokenizer.decode(outputs[0][input_tokens:], skip_special_tokens=True).strip()

    print(f"model_dir: {args.model_dir}")
    print(f"device: {args.device}")
    print(f"use_cache: {use_cache}")
    print(f"input_tokens: {input_tokens}")
    print(f"new_tokens: {new_tokens}")
    print(f"elapsed_sec: {elapsed:.3f}")
    print(f"tokens_per_sec: {new_tokens / elapsed if elapsed > 0 else 0:.3f}")
    print(f"response: {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
