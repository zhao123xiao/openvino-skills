#!/usr/bin/env python3
"""Smoke-test an OVMS OpenAI-compatible chat endpoint."""

from __future__ import annotations

import argparse

from openai import OpenAI


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test OVMS /v3/chat/completions.")
    parser.add_argument("--base-url", default="http://localhost:8000/v3")
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", default="Say this is a test.")
    parser.add_argument("--max-tokens", type=int, default=32)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = OpenAI(base_url=args.base_url, api_key="unused")
    response = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": args.prompt}],
        max_tokens=args.max_tokens,
        stream=False,
    )
    print(f"base_url: {args.base_url}")
    print(f"model: {args.model}")
    print(response.choices[0].message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
