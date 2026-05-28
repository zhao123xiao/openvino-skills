#!/usr/bin/env python3
"""Small Optimum OpenVINO feature-extraction smoke test."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from optimum.intel.openvino import OVModelForFeatureExtraction
from path_utils import normalize_path
from transformers import AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test an OpenVINO embedding export.")
    parser.add_argument("model_dir", type=Path)
    parser.add_argument("--text", action="append", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_dir = normalize_path(args.model_dir)
    texts = args.text or ["hello openvino", "中文向量测试"]
    tokenizer = AutoTokenizer.from_pretrained(
        model_dir,
        local_files_only=True,
        trust_remote_code=True,
        fix_mistral_regex=True,
    )
    model = OVModelForFeatureExtraction.from_pretrained(
        model_dir,
        local_files_only=True,
        trust_remote_code=True,
        compile=False,
    )
    inputs = tokenizer(texts, padding=True, return_tensors="pt")
    output = model(**inputs)
    hidden = output.last_hidden_state
    sample = hidden[0, -1].detach().cpu().numpy()
    print(f"model_dir: {model_dir}")
    print(f"tokenizer: {tokenizer.__class__.__name__}")
    print(f"shape: {tuple(hidden.shape)}")
    print(f"dtype: {hidden.dtype}")
    print(f"sample_norm: {float(np.linalg.norm(sample)):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
