# OpenVINO Skills

`openvino-skills` is a Codex skill that turns local OpenVINO knowledge-base content into repeatable SOPs for model conversion, quantization, deployment, smoke testing, benchmarking, device selection, and troubleshooting.

The skill is designed for practical OpenVINO work rather than passive documentation lookup. It guides an agent through concrete routes such as exporting Hugging Face models to OpenVINO IR, compressing LLMs to INT4/INT8, deploying through OpenVINO Model Server, testing `/v3` OpenAI-compatible endpoints, and benchmarking CPU/GPU/NPU targets.

## What It Covers

- Model conversion with `ovc`, `openvino.convert_model`, and `optimum-cli export openvino`.
- INT4/INT8/NF4 and NNCF-oriented quantization decisions.
- Deployment through Python runtime, OpenVINO GenAI, OVMS Docker, OVMS bare metal, and KServe.
- Smoke tests for LLM, embedding, and OVMS chat endpoints.
- Benchmark workflows for LLM, embedding, and generic OpenVINO IR models.
- Device guidance for CPU, GPU, NPU, `AUTO`, and `AUTO:GPU,CPU`.
- Local model case notes for Qwen3, Qwen3 Embedding, Qwen3 Reranker, Gemma, GPT-OSS, and AWQ-style artifacts.

## Structure

```text
openvino-skills/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── convert-quantize-sop.md
│   ├── deploy-sop.md
│   ├── device-troubleshooting-sop.md
│   ├── local-model-cases.md
│   ├── model-playbooks.md
│   ├── npu-playbook.md
│   ├── report-template.md
│   └── test-benchmark-sop.md
└── scripts/
    ├── benchmark_openvino_model.py
    ├── inspect_openvino_artifact.py
    ├── openvino_probe.py
    ├── ovms_chat_smoke.py
    ├── search_openvino_kb.py
    ├── smoke_embedding.py
    └── smoke_llm.py
```

## Installation

Clone this repository into your Codex skills directory:

```bash
cd ~/.codex/skills
git clone https://github.com/zhao123xiao/openvino-skills.git openvino-skills
```

If your Codex home is on Windows-mounted storage, use that skills directory instead, for example:

```bash
cd /mnt/c/Users/赵晓晓/.codex/skills
git clone https://github.com/zhao123xiao/openvino-skills.git openvino-skills
```

Validate the skill if you have the system skill validator available:

```bash
~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/openvino-skills
```

## Example Prompts

```text
Use $openvino-skills to convert Qwen/Qwen3-Embedding-8B to INT4 OpenVINO and validate the output.
```

```text
Use $openvino-skills to deploy /mnt/d/models/ov/Qwen3-0.6B with OVMS and test the OpenAI-compatible chat endpoint.
```

```text
Use $openvino-skills to benchmark this OpenVINO model on CPU, GPU, and NPU, then report the tested devices and failures.
```

## Useful Scripts

Inspect a model artifact:

```bash
python3 scripts/inspect_openvino_artifact.py /mnt/d/models/ov/Qwen3-0.6B
```

Probe OpenVINO devices:

```bash
python3 scripts/openvino_probe.py
```

Run a small LLM smoke test:

```bash
python3 scripts/smoke_llm.py /mnt/d/models/ov/Qwen3-0.6B --device CPU
```

Run an embedding smoke test:

```bash
python3 scripts/smoke_embedding.py /mnt/d/models/ov/Qwen3-Embedding-8B-int4-ov
```

Benchmark a model:

```bash
python3 scripts/benchmark_openvino_model.py /mnt/d/models/ov/Qwen3-0.6B --kind llm --devices CPU --max-new-tokens 64 --repeats 3
```

## Notes

- The skill assumes local OpenVINO artifacts often live under `/mnt/d/models/ov`.
- Some references mention the local Chroma knowledge base at `/mnt/d/knowledge-base/chroma_data/chroma.sqlite3`; that path is specific to the original authoring environment.
- NPU support is intentionally conservative. Always run CPU smoke first, then NPU compile/smoke, and report the exact failure if NPU is unavailable or incompatible.
