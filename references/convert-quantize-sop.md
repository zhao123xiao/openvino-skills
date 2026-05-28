# Convert And Quantize SOP

## Decision Tree

1. If the source is already an OpenVINO IR or OpenVINO organization model with `.xml`/`.bin`, skip conversion and validate.
2. If the source is a Hugging Face transformer, embedding, reranker, VLM, ASR, or diffusion model, prefer Optimum Intel / `optimum-cli export openvino`.
3. If the source is ONNX, TensorFlow SavedModel, TensorFlow Lite, Paddle, or another converter-supported graph, use `ovc`.
4. If the source is PyTorch or JAX/Flax, use Python API: `openvino.convert_model` then `openvino.save_model`.
5. If size/performance is the objective, choose NNCF/Optimum compression before deployment, then rerun smoke tests and benchmark.

## Route Table

| Source | Default route | Output to expect | First validation |
| --- | --- | --- | --- |
| `OpenVINO/*-ov` on Hugging Face | Pull or copy as-is | Existing OpenVINO IR plus tokenizer/config | `inspect_openvino_artifact.py` |
| Hugging Face LLM/chat | `optimum-cli export openvino --task text-generation` | `openvino_model.xml/bin`, tokenizer files | `smoke_llm.py` |
| Hugging Face embedding | `--task feature-extraction` | `openvino_model.xml/bin`, tokenizer files | `smoke_embedding.py` |
| Diffusion/text-to-image | `--task text-to-image --trust-remote-code` | multiple component IRs | OVMS image endpoint smoke |
| ONNX/TensorFlow/Paddle/TFLite | `ovc` | `.xml/.bin` pair | generic compile + `benchmark_app` |
| PyTorch/JAX model in code | `openvino.convert_model` + `openvino.save_model` | `.xml/.bin` pair | generic compile + sample input |

## Artifact Naming

Use descriptive target folders:

- `<model>-fp16-ov`
- `<model>-int8-ov`
- `<model>-int4-ov`
- `<model>-int4-cw-ov` for channel-wise INT4 where applicable

Prefer writing to a temporary directory and renaming only after validation.

## Generic IR Conversion

Use `ovc` for converter-supported model files:

```bash
ovc /path/to/source_model.onnx --output_model /mnt/d/models/ov/my-model-fp16-ov/openvino_model.xml
```

Use Python API when the model lives in code or PyTorch/JAX:

```python
import openvino as ov

ov_model = ov.convert_model(model, example_input=example_input)
ov.save_model(ov_model, "/mnt/d/models/ov/my-model-fp16-ov/openvino_model.xml")
```

Validate that the `.xml` and `.bin` pair exists after saving.

## Hugging Face And GenAI Export

Use `optimum-cli export openvino` for Hugging Face models:

```bash
optimum-cli export openvino \
  --model <hf-model-id-or-local-path> \
  --task text-generation \
  --weight-format fp16 \
  /mnt/d/models/ov/<target-name>
```

Common task mapping:

- Causal LLM/chat model: `text-generation`.
- Embedding model: `feature-extraction`.
- Diffusion text-to-image: `text-to-image`.
- ASR/Whisper: verify against model docs and use the matching Optimum/OpenVINO task.
- Reranker: inspect model architecture. Generative rerankers often use `text-generation`; classifier/cross-encoder rerankers may need a different path.

## INT4/INT8 Weight Compression

Choose compression by deployment target:

| Target | Default precision | Notes |
| --- | --- | --- |
| CPU local LLM | INT4 first, INT8 fallback | Validate quality and tokens/sec. |
| GPU local/OVMS | INT4 or FP16 | Test both if quality/performance matters. |
| NPU | Known NPU-optimized model first | Do not assume generic INT4 export compiles. |
| Embedding/RAG | INT4/INT8 only after retrieval spot check | Shape passing is not enough. |
| CV with calibration data | INT8/PTQ | Use representative data when accuracy matters. |
| Accuracy-critical or unknown | FP16 baseline first | Quantize only after baseline works. |

For LLM-style Hugging Face export:

```bash
optimum-cli export openvino \
  --model <hf-model-id-or-local-path> \
  --task text-generation \
  --weight-format int4 \
  --sym \
  --group-size 128 \
  --ratio 1.0 \
  /mnt/d/models/ov/<target-name>
```

For text-to-image examples from the local KB, use:

```bash
optimum-cli export openvino \
  --model <hf-model-id-or-local-path> \
  --task text-to-image \
  --trust-remote-code \
  --weight-format int4 \
  --group-size 64 \
  --ratio 1.0 \
  /mnt/d/models/ov/<target-name>
```

Use INT8 when accuracy risk is low but INT4 is too aggressive or unsupported:

```bash
optimum-cli export openvino \
  --model <hf-model-id-or-local-path> \
  --task <task> \
  --weight-format int8 \
  /mnt/d/models/ov/<target-name>
```

## NNCF Paths

Use NNCF when the task is specifically post-training quantization, weight compression, or QAT:

- PTQ supports OpenVINO, PyTorch, TorchFX, and ONNX style workflows.
- Weights compression supports symmetric INT8, symmetric/asymmetric INT4, NF4, mixed precision, and grouped weights.
- QAT and LoRA QAT are training-time workflows; only use them when the user expects training/fine-tuning.

For NPU-oriented LLMs, prefer known pre-compressed OpenVINO models or channel-wise/NF4 guidance from the model's docs. Do not assume every INT4 export runs on NPU.

## Required Validation

After conversion or compression:

```bash
find /mnt/d/models/ov/<target-name> -maxdepth 1 -type f -printf '%f %s\n' | sort
du -sh /mnt/d/models/ov/<target-name>
```

Expected files by type:

- Generic IR/CV: at least one `.xml` and matching `.bin`.
- LLM/embedding/reranker: `openvino_model.xml`, `openvino_model.bin`, tokenizer files, config files, and often `openvino_config.json`.
- GenAI tokenized models may include `openvino_tokenizer.*` and `openvino_detokenizer.*`.
- Multimodal models may contain several component IR files such as language, text embedding, vision embedding, tokenizer, or detokenizer models.

Run the relevant smoke test from `test-benchmark-sop.md` before deployment.

Minimal local validation command:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/inspect_openvino_artifact.py /mnt/d/models/ov/<target-name>
```

If this fails, do not deploy. Fix missing files or rerun export first.
