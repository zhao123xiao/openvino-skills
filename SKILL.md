---
name: openvino-skills
description: End-to-end OpenVINO standard operating procedures for model conversion, quantization/compression, deployment, smoke testing, benchmarking, device selection, and troubleshooting. Use when the user asks to deploy a model with OpenVINO, convert or quantize a Hugging Face/ONNX/TensorFlow/PyTorch model to OpenVINO IR, serve models with OpenVINO Model Server or OpenAI-compatible endpoints, test local OpenVINO artifacts, benchmark CPU/GPU/NPU/AUTO performance, or turn OpenVINO knowledge-base guidance into repeatable commands.
---

# OpenVINO SOP

## Core Rule

Treat OpenVINO work as a pipeline: lock inputs, convert or pull the model, validate files, run a smoke test, deploy, benchmark, then document the exact device/config/result. Do not jump straight to deployment before the artifact has been validated locally.

## Workflow Selector

1. **Convert or quantize a model**: read `references/convert-quantize-sop.md`.
2. **Deploy or serve a model**: read `references/deploy-sop.md`.
3. **Test or benchmark a model**: read `references/test-benchmark-sop.md`.
4. **Choose CPU/GPU/NPU/AUTO or debug failures**: read `references/device-troubleshooting-sop.md`.
5. **Start from a model/use-case type**: read `references/model-playbooks.md`.
6. **Use a known local model case**: read `references/local-model-cases.md`.
7. **Target NPU specifically**: read `references/npu-playbook.md`.
8. **Need exact local KB evidence**: run `scripts/search_openvino_kb.py` before finalizing commands.

For remote HPCCube model quantization and delivery to `D:\models\ov`, use the separate `openvino-model-quantization` skill.

## Required Preflight

Before making changes or running long jobs, record:

- Source model id/path and license/access constraints.
- Task type: `text-generation`, `feature-extraction`, `rerank`, `text-to-image`, `image-to-text`, ASR, CV classification/detection, or generic IR.
- Target artifact directory, usually under `/mnt/d/models/ov/<name>` for local Windows storage.
- Target device: `CPU`, `GPU`, `NPU`, `AUTO`, or explicit priority such as `AUTO:GPU,CPU`.
- Precision target: FP32/FP16, INT8, INT4, NF4, or already-compressed OpenVINO model.
- Deployment target: Python runtime, OpenVINO GenAI, OVMS Docker, OVMS bare metal, or KServe.

## Done Criteria

A task is not complete until these are reported:

- Final model path and key files (`.xml`/`.bin`, tokenizer files, `openvino_config.json` when applicable).
- Conversion/quantization command and major options.
- Device probe or target-device confirmation.
- Smoke-test command and result.
- Benchmark result when performance was part of the request.
- Deployment command or endpoint, including port, task, model name, and target device.

Use `references/report-template.md` for the final report shape when the task includes conversion, deployment, or benchmarking.

## Low-Friction Tools

- `scripts/inspect_openvino_artifact.py <MODEL_DIR>`: classify and check a local OpenVINO artifact folder.
- `scripts/openvino_probe.py`: print OpenVINO version and available devices.
- `scripts/smoke_llm.py <MODEL_DIR> --device CPU`: run a small Optimum causal-LM generation smoke test.
- `scripts/smoke_embedding.py <MODEL_DIR>`: run a small Optimum feature-extraction smoke test.
- `scripts/benchmark_openvino_model.py <MODEL_DIR> --kind llm --devices CPU GPU NPU`: run a repeatable local benchmark wrapper.
- `scripts/ovms_chat_smoke.py --model <MODEL_NAME>`: call OVMS `/v3/chat/completions`.
- `scripts/search_openvino_kb.py "query"`: search the local OpenVINO Chroma collection for exact examples.

## Local Knowledge Base

The SOP is distilled from the local OpenVINO Chroma collection:

- DB: `/mnt/d/knowledge-base/chroma_data/chroma.sqlite3`
- Collection: `openvino-kb`
- Mirrors: `/mnt/d/openvino-knowledge-base`, `/mnt/d/models/openvino-master`, `/mnt/d/models/openvino_notebooks-latest`

Use local KB search when exact flags, source examples, or current local conventions matter:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/search_openvino_kb.py "optimum-cli export openvino" --limit 6
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/search_openvino_kb.py "model_path rest_port task" --limit 6
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/search_openvino_kb.py "benchmark_app latency throughput" --limit 6
```
