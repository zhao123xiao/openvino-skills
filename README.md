<!--
╔══════════════════════════════════════════════════════════════════════╗
║  DreamSeed 种梦计划 — AI创造者大赛  官方 README 模板                ║
║                                                                      ║
║  使用说明：                                                          ║
║  1. 将本模板放在参赛仓库根目录 README.md 的顶部                       ║
║  2. 头图使用 DreamField 官方公开活动图片地址                         ║
║  3. 请保留 DREAMFIELD_README_HEADER_START / END 标识                 ║
║  4. 分割线以下供创作者自由编写项目内容                               ║
╚══════════════════════════════════════════════════════════════════════╝
-->

<!-- DREAMFIELD_README_HEADER_START -->

<p align="center">
  <a href="https://www.dreamfield.top">
    <img src="https://www.dreamfield.top/dream-field/contest-readme/assets/dreamseed-readme-banner.png" alt="DreamSeed 种梦计划参赛作品" width="100%" />
  </a>
</p>

<!-- DREAMFIELD_README_HEADER_END -->

---

# OpenVINO Skills

`openvino-skills` 是一份面向 Codex Agent 的 OpenVINO 标准作业流程技能包。它把 OpenVINO 官方文档中分散的模型转换、量化/压缩、部署、测试、Benchmark、设备选择和排障经验，整理成可重复执行的 SOP，让 Agent 不只是“解释 OpenVINO”，而是按固定步骤完成真实模型交付。

默认使用中文输出说明、进度、结论和排障建议；命令、模型 ID、API 名称、文件名和 OpenVINO 技术术语保持原样，避免影响可执行性。

## 这个 Skill 解决什么问题

很多 OpenVINO 任务失败不是因为单条命令写错，而是流程顺序不稳定：模型还没检查就部署，CPU 还没 smoke test 就上 NPU，Benchmark 混进首次编译时间，或者 Windows/WSL 路径混用。这个 skill 将这些容易出错的步骤固化为一条流水线：

```text
确认输入 -> 转换/量化 -> 检查产物 -> 设备探测 -> 冒烟测试 -> 部署服务 -> Benchmark -> 输出报告
```

每次执行任务时，Agent 都需要先锁定源模型、任务类型、目标设备、精度目标、产物目录和部署方式，再选择对应 SOP 文件与辅助脚本。

## 能力范围

| 场景 | 固化后的处理方式 |
| --- | --- |
| Hugging Face LLM 转 OpenVINO | 使用 `optimum-cli export openvino --task text-generation`，按 INT4/INT8/FP16 目标导出并验证 tokenizer 与 IR 文件 |
| Embedding/RAG 模型转换 | 使用 `--task feature-extraction`，检查向量维度、输出类型和后续检索质量 |
| Reranker 模型部署 | 优先验证排序语义，再考虑 OVMS Cohere-compatible `/v3/rerank` |
| ONNX/TensorFlow/Paddle/TFLite 模型转换 | 使用 `ovc` 或 `openvino.convert_model` 生成 `.xml/.bin`，再运行 generic IR compile 与 `benchmark_app` |
| INT4/INT8/NF4 压缩 | 根据模型类型、目标设备和准确率风险选择 Optimum/NNCF 路线 |
| OpenVINO Model Server 部署 | 覆盖 OVMS Docker、bare metal、GenAI task、OpenAI-compatible `/v3` endpoint |
| 本地产物测试 | 使用内置 smoke 脚本检查 LLM、Embedding、OVMS chat endpoint 和通用 IR |
| Benchmark | 按 CPU/GPU/NPU/AUTO 设备策略进行重复测试，并区分首次编译与稳定推理 |
| NPU 验证 | 先 CPU smoke，再 NPU compile/smoke；动态 shape、模型兼容性和 INT4 支持都必须显式确认 |
| Windows/WSL 路径 | 用户说明默认 `D:\models\ov\<model>`；只有在 WSL/Linux 命令中使用 `/mnt/d/models/ov/<model>` |

## 目录结构

```text
openvino-skills/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── convert-quantize-sop.md
│   ├── deploy-sop.md
│   ├── device-troubleshooting-sop.md
│   ├── local-model-cases.md
│   ├── model-playbooks.md
│   ├── npu-playbook.md
│   ├── path-conventions.md
│   ├── report-template.md
│   └── test-benchmark-sop.md
└── scripts/
    ├── benchmark_openvino_model.py
    ├── inspect_openvino_artifact.py
    ├── openvino_probe.py
    ├── ovms_chat_smoke.py
    ├── path_utils.py
    ├── smoke_embedding.py
    └── smoke_llm.py
```

## SOP 文件说明

| 文件 | 什么时候读取 | 主要内容 |
| --- | --- | --- |
| `SKILL.md` | skill 触发后首先读取 | 工作流选择器、预检清单、完成标准、低门槛工具入口 |
| `references/convert-quantize-sop.md` | 需要转换或量化模型时 | 路线选择、产物命名、`ovc`、Optimum export、INT4/INT8/NF4、NNCF、验证要求 |
| `references/deploy-sop.md` | 需要部署或提供 API 时 | Python runtime、OVMS Docker、OVMS bare metal、GenAI endpoint、KServe 草案 |
| `references/test-benchmark-sop.md` | 需要测试或跑性能时 | 文件校验、设备探测、LLM/Embedding/OVMS smoke、`benchmark_app`、GenAI benchmark |
| `references/device-troubleshooting-sop.md` | 需要选设备或排障时 | CPU/GPU/NPU/AUTO 策略、自动批处理、模型缓存、常见失败处理 |
| `references/model-playbooks.md` | 从模型类型出发时 | LLM、Embedding、Reranker、Text-to-image、VLM、ASR、CV 的执行路线 |
| `references/local-model-cases.md` | 使用本机已有模型时 | `D:\models\ov` 和 `D:\openvino-models` 下常见模型的测试策略 |
| `references/npu-playbook.md` | 明确目标是 NPU 时 | NPU 入口条件、适合/高风险模型、静态 shape、验证报告 |
| `references/path-conventions.md` | 涉及 Windows/WSL 路径时 | Windows 路径与 WSL 路径的转换规则 |
| `references/report-template.md` | 任务收尾时 | 转换、验证、部署、Benchmark、下一步建议的报告模板 |

## 内置脚本

这些脚本用于把高频检查动作变成可执行工具，减少 Agent 临时拼命令造成的偏差。

| 脚本 | 用途 |
| --- | --- |
| `scripts/inspect_openvino_artifact.py` | 检查 OpenVINO 产物目录，识别 `.xml/.bin`、tokenizer、配置文件和常见缺失项 |
| `scripts/openvino_probe.py` | 输出 OpenVINO 版本与可用设备 |
| `scripts/smoke_llm.py` | 对 Optimum OpenVINO CausalLM 模型执行短文本生成 smoke test |
| `scripts/smoke_embedding.py` | 对 Optimum OpenVINO feature-extraction 模型执行 embedding smoke test |
| `scripts/benchmark_openvino_model.py` | 对 LLM、Embedding 或 generic IR 执行可重复 Benchmark |
| `scripts/ovms_chat_smoke.py` | 调用 OVMS `/v3/chat/completions` 做服务端 smoke test |
| `scripts/path_utils.py` | 在 WSL 中把 `D:\...` 形式路径转换为 `/mnt/d/...` |

## 安装

在 Linux/WSL 环境中安装到 Codex skills 目录：

```bash
cd ~/.codex/skills
git clone https://github.com/zhao123xiao/openvino-skills.git openvino-skills
```

如果 Codex home 位于 Windows 用户目录的 WSL 挂载路径中：

```bash
cd /mnt/c/Users/赵晓晓/.codex/skills
git clone https://github.com/zhao123xiao/openvino-skills.git openvino-skills
```

可选校验：

```bash
~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/openvino-skills
```

## 使用方式

在 Codex 中显式调用：

```text
Use $openvino-skills 用中文把 Qwen/Qwen3-Embedding-8B 转成 INT4 OpenVINO，并验证输出产物。
```

```text
Use $openvino-skills 用中文将 D:\models\ov\Qwen3-0.6B 通过 OVMS 部署，并测试 OpenAI-compatible chat endpoint。
```

```text
Use $openvino-skills 用中文 benchmark 这个 OpenVINO 模型在 CPU、GPU、NPU 上的表现，并报告可用设备和失败原因。
```

也可以直接描述目标，触发条件包括：OpenVINO 模型部署、模型测试、模型转换、模型量化、OVMS 服务、OpenAI-compatible endpoint、CPU/GPU/NPU Benchmark、NPU 排障等。

## 常用命令

用户沟通中优先使用 Windows 路径，例如 `D:\models\ov\Qwen3-0.6B`。下面命令是在 WSL/Linux shell 中执行，因此示例使用 `/mnt/d/...`。

检查模型产物：

```bash
python3 scripts/inspect_openvino_artifact.py /mnt/d/models/ov/Qwen3-0.6B
```

脚本也接受 Windows 路径，并会在 WSL 中自动转换：

```bash
python3 scripts/inspect_openvino_artifact.py 'D:\models\ov\Qwen3-0.6B'
```

探测 OpenVINO 设备：

```bash
python3 scripts/openvino_probe.py
```

运行 LLM smoke test：

```bash
python3 scripts/smoke_llm.py /mnt/d/models/ov/Qwen3-0.6B --device CPU --max-new-tokens 32
```

运行 Embedding smoke test：

```bash
python3 scripts/smoke_embedding.py /mnt/d/models/ov/Qwen3-Embedding-8B-int4-ov
```

运行 LLM Benchmark：

```bash
python3 scripts/benchmark_openvino_model.py /mnt/d/models/ov/Qwen3-0.6B --kind llm --devices CPU --max-new-tokens 64 --repeats 3
```

测试 OVMS chat endpoint：

```bash
python3 scripts/ovms_chat_smoke.py --base-url http://127.0.0.1:8000 --model qwen3
```

## 完成标准

一次 OpenVINO 任务完成时，Agent 应该输出以下信息：

- 最终模型路径，例如 `D:\models\ov\<model>`，以及关键文件是否存在。
- 转换或量化命令，包括任务类型、精度、压缩参数和输出目录。
- OpenVINO 版本、可用设备和最终选择的目标设备。
- smoke test 命令与结果。
- 如果涉及性能目标，给出 Benchmark 命令、设备、重复次数、tokens/s 或 latency/throughput 指标。
- 如果涉及部署，给出部署方式、端口、模型名、endpoint、目标设备和 endpoint smoke 结果。
- 如果失败，给出最小可复现命令和下一步排障方向。

## 路径约定

默认面向 Windows 用户说明路径：

```text
D:\models\ov\<model>
D:\openvino-models\<model>
C:\Users\赵晓晓\.codex\skills\openvino-skills
```

只有在 WSL/Linux 命令、Docker volume、shell 变量中才使用挂载路径：

```bash
MODEL_DIR=/mnt/d/models/ov/Qwen3-0.6B
docker run --rm -v /mnt/d/models/ov/Qwen3-0.6B:/model openvino/model_server:latest
```

原生 Windows 命令不应包含 `/mnt/...`。

## 适合的任务示例

- “把这个 Hugging Face 模型转成 OpenVINO INT4，并放到 `D:\models\ov`。”
- “检查 `D:\models\ov\Qwen3-0.6B` 这个 OpenVINO 产物能不能跑。”
- “用 OVMS 部署这个 LLM，并测试 `/v3/chat/completions`。”
- “帮我判断这个模型适不适合跑 NPU，如果不适合请给出原因。”
- “对 CPU、GPU、NPU 分别跑一次 Benchmark，输出可复现命令和结果表。”
- “把 OpenVINO 的模型部署、测试、量化流程整理成 Agent 可执行的 SOP。”

## 设计原则

- 先验证产物，再部署服务。
- 先 CPU baseline，再尝试 GPU/NPU/AUTO。
- NPU 不做默认承诺，必须通过 compile/smoke test 证明。
- Embedding 和 Reranker 不只看 shape，还要做语义或排序 sanity check。
- Benchmark 要说明设备、精度、输入、重复次数和是否包含首次编译。
- 报告要能让下一位执行者复现，不只给结论。
