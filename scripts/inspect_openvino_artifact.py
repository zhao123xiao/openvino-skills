#!/usr/bin/env python3
"""Inspect an OpenVINO artifact directory and print an actionable checklist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from path_utils import normalize_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect local OpenVINO model artifacts.")
    parser.add_argument("model_dir", type=Path)
    return parser.parse_args()


def paired_xml_bin(model_dir: Path) -> list[tuple[Path, Path | None]]:
    pairs = []
    for xml in sorted(model_dir.glob("*.xml")):
        bin_path = xml.with_suffix(".bin")
        pairs.append((xml, bin_path if bin_path.exists() else None))
    return pairs


def main() -> int:
    args = parse_args()
    model_dir = normalize_path(args.model_dir)
    if not model_dir.exists():
        print(f"ERROR model_dir_missing {model_dir}")
        return 2
    if not model_dir.is_dir():
        print(f"ERROR not_directory {model_dir}")
        return 2

    files = sorted(p for p in model_dir.iterdir() if p.is_file())
    total = sum(p.stat().st_size for p in files)
    print(f"model_dir: {model_dir}")
    print(f"file_count: {len(files)}")
    print(f"total_bytes: {total}")
    print(f"total_gib: {total / (1024 ** 3):.3f}")

    xml_pairs = paired_xml_bin(model_dir)
    print("\nir_pairs:")
    if not xml_pairs:
        print("  MISSING no .xml files found")
    for xml, bin_path in xml_pairs:
        status = "OK" if bin_path else "MISSING_BIN"
        size = bin_path.stat().st_size if bin_path else 0
        print(f"  {status} {xml.name} -> {xml.with_suffix('.bin').name} {size}")

    names = {p.name for p in files}
    tokenizer_markers = [
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "openvino_tokenizer.xml",
        "openvino_detokenizer.xml",
    ]
    config_markers = ["config.json", "generation_config.json", "openvino_config.json"]
    print("\ntokenizer_files:")
    for name in tokenizer_markers:
        print(f"  {'OK' if name in names else 'MISS'} {name}")
    print("\nconfig_files:")
    for name in config_markers:
        print(f"  {'OK' if name in names else 'MISS'} {name}")

    config_path = model_dir / "config.json"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            print("\nconfig_summary:")
            for key in ("model_type", "architectures", "hidden_size", "num_hidden_layers", "use_cache"):
                if key in cfg:
                    print(f"  {key}: {cfg[key]}")
        except Exception as exc:
            print(f"\nconfig_summary_error: {exc}")

    failures = []
    if not xml_pairs:
        failures.append("no_xml")
    failures.extend(f"missing_bin:{xml.name}" for xml, bin_path in xml_pairs if bin_path is None)
    if failures:
        print("\nstatus: FAIL")
        print("failures:", ", ".join(failures))
        return 1

    print("\nstatus: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
