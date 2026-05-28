# OpenVINO Skills

`openvino-skills` 是一个 Codex skill，用来把本地 OpenVINO 知识库中的内容固化为可重复执行的 SOP，覆盖模型转换、量化、部署、冒烟测试、Benchmark、设备选择和排障。

该 skill 的目标不是复述官方文档，而是降低 OpenVINO 实操门槛：引导 agent 走固定路线，例如将 Hugging Face 模型导出为 OpenVINO IR、将 LLM 压缩为 INT4/INT8、通过 OpenVINO Model Server 部署服务、测试 `/v3` OpenAI-compatible endpoint，以及评估 CPU/GPU/NPU 性能。

默认使用中文输出说明、进度、结论和排障建议；命令、代码、模型 ID、文件路径和 API 名称保持原样。

## 覆盖范围

- 使用 `ovc`、`openvino.convert_model` 和 `optimum-cli export openvino` 进行模型转换。
- INT4、INT8、NF4 和 NNCF 相关量化/压缩决策。
- 通过 Python runtime、OpenVINO GenAI、OVMS Docker、OVMS bare metal 和 KServe 部署。
- LLM、Embedding 和 OVMS chat endpoint 的 smoke test。
- LLM、Embedding 和通用 OpenVINO IR 模型的 Benchmark 流程。
- CPU、GPU、NPU、`AUTO`、`AUTO:GPU,CPU` 的设备选择建议。
- Qwen3、Qwen3 Embedding、Qwen3 Reranker、Gemma、GPT-OSS 和 AWQ 类本地模型案例。

## 目录结构

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

## 安装

克隆到 Codex skills 目录：

```bash
cd ~/.codex/skills
git clone https://github.com/zhao123xiao/openvino-skills.git openvino-skills
```

如果 Codex home 在 Windows 挂载目录中，可以使用对应路径，例如：

```bash
cd /mnt/c/Users/赵晓晓/.codex/skills
git clone https://github.com/zhao123xiao/openvino-skills.git openvino-skills
```

如果本地有系统 skill 校验器，可以运行：

```bash
~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/openvino-skills
```

## 示例提示词

```text
Use $openvino-skills 用中文把 Qwen/Qwen3-Embedding-8B 转成 INT4 OpenVINO，并验证输出产物。
```

```text
Use $openvino-skills 用中文将 /mnt/d/models/ov/Qwen3-0.6B 通过 OVMS 部署，并测试 OpenAI-compatible chat endpoint。
```

```text
Use $openvino-skills 用中文 benchmark 这个 OpenVINO 模型在 CPU、GPU、NPU 上的表现，并报告可用设备和失败原因。
```

## 常用脚本

检查模型产物：

```bash
python3 scripts/inspect_openvino_artifact.py /mnt/d/models/ov/Qwen3-0.6B
```

探测 OpenVINO 设备：

```bash
python3 scripts/openvino_probe.py
```

运行 LLM smoke test：

```bash
python3 scripts/smoke_llm.py /mnt/d/models/ov/Qwen3-0.6B --device CPU
```

运行 Embedding smoke test：

```bash
python3 scripts/smoke_embedding.py /mnt/d/models/ov/Qwen3-Embedding-8B-int4-ov
```

运行 Benchmark：

```bash
python3 scripts/benchmark_openvino_model.py /mnt/d/models/ov/Qwen3-0.6B --kind llm --devices CPU --max-new-tokens 64 --repeats 3
```

## 注意事项

- 该 skill 默认假设本地 OpenVINO 模型常放在 `/mnt/d/models/ov`。
- 部分 reference 会提到本地 Chroma 知识库 `/mnt/d/knowledge-base/chroma_data/chroma.sqlite3`，这是原始构建环境中的路径。
- NPU 支持保持保守策略：先跑 CPU smoke，再跑 NPU compile/smoke；如果 NPU 不可用或模型不兼容，需要报告准确失败原因。
