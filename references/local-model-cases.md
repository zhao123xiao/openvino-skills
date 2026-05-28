# Local Model Cases

Use this file when the user points to a model already under `/mnt/d/models/ov` or `/mnt/d/openvino-models`. These are not universal truths; they are local starting points that should still be validated with the smoke scripts.

## Local Inventory

| Local path | Likely kind | First action | Notes |
| --- | --- | --- | --- |
| `/mnt/d/models/ov/Qwen3-0.6B` | LLM | `inspect_openvino_artifact.py`, then `smoke_llm.py --device CPU` | Small baseline for fast smoke tests. |
| `/mnt/d/models/ov/Qwen3-8B-int4-cw` | LLM | LLM smoke, then CPU/GPU benchmark | `cw` implies channel-wise INT4; test NPU only after CPU works. |
| `/mnt/d/models/ov/Qwen3-30B-A3B-int4` | MoE/LLM | inspect first, then long-memory-aware smoke | Large model; avoid casual multi-device benchmarks. |
| `/mnt/d/models/ov/Qwen3-Embedding-0.6B-fp16-ov` | Embedding | `smoke_embedding.py` | Good NPU candidate only if compile test passes. |
| `/mnt/d/models/ov/Qwen3-Embedding-8B-int4-ov` | Embedding | `smoke_embedding.py` and retrieval spot check | Known local artifact around 4 GiB. |
| `/mnt/d/models/ov/Qwen3-Reranker-0.6B-fp16-ov` | Reranker | inspect, then rerank-specific local/API smoke | Prefer ranking sanity check over shape-only validation. |
| `/mnt/d/models/ov/Qwen3-Reranker-8B-INT4` | Reranker | inspect and ranking sanity check | Treat as heavyweight; benchmark after functionality. |
| `/mnt/d/models/ov/gemma-4-E4B-int8` | Multimodal/GenAI | inspect component IRs, then model-specific smoke | Contains multiple component models. |
| `/mnt/d/models/ov/gpt-oss-20b-int4` | LLM | inspect and CPU smoke before any service deployment | Large model; use cautious max token counts. |
| `/mnt/d/openvino-models/qwen3.5-4b-ov-awq` | Multimodal/LLM-family AWQ | inspect component IRs, then task-specific smoke | Do not assume generic `OVModelForCausalLM` works until inspected. |

## Default Local Commands

Artifact inspection:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/inspect_openvino_artifact.py /mnt/d/models/ov/<model>
```

LLM smoke:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_llm.py /mnt/d/models/ov/<model> --device CPU --max-new-tokens 32
```

Embedding smoke:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_embedding.py /mnt/d/models/ov/<model>
```

LLM benchmark across safe devices:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/benchmark_openvino_model.py /mnt/d/models/ov/<model> --kind llm --devices CPU --max-new-tokens 64 --repeats 3
```

## Case Rules

- Always inspect before picking a smoke class. Component-heavy folders may not be a simple CausalLM export.
- For embedding/reranker models, a shape-only pass is insufficient; do a semantic or ranking spot check when the model will serve RAG.
- For large LLMs, keep smoke prompts short and `max_new_tokens` low before a benchmark.
- For NPU, read `npu-playbook.md` and compile-test; do not infer compatibility from folder name or precision.
