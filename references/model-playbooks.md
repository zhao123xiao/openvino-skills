# Model Playbooks

Use this file first when the user names a model family or use case. It converts local OpenVINO documentation into direct operating routes.

## Quick Matrix

| Use case | Convert route | Quantization route | Test route | Deploy route |
| --- | --- | --- | --- | --- |
| Chat/LLM | `optimum-cli export openvino --task text-generation` or pull existing `OpenVINO/*-ov` | INT4 for local disk/CPU/GPU; NPU only when model is known compatible | `scripts/smoke_llm.py`, then token/s benchmark | OVMS `--task text_generation` + `/v3/chat/completions` |
| Embedding/RAG | `--task feature-extraction` | INT4/INT8 if embedding quality is acceptable; verify vector shape and downstream quality | `scripts/smoke_embedding.py` | OVMS `/v3/embeddings`; CPU/GPU, NPU only for supported embedding models |
| Reranker | Prefer OpenVINO/Cohere-ready model or inspect architecture | INT4 only after ranking-quality spot check | Cohere rerank request against `/v3/rerank` | OVMS Cohere-compatible rerank endpoint |
| Text-to-image | `--task text-to-image --trust-remote-code` | INT4 with smaller group size often used; validate image endpoint | image generation endpoint smoke | OVMS `/v3/images/generations` |
| VLM/image-to-text | Use model-specific Optimum/OpenVINO GenAI route | Treat quantization as model-specific; do not assume NPU | OpenAI chat with image data URL | OVMS `/v3/chat/completions` with multimodal message |
| ASR/Whisper | Use model-specific OpenVINO/GenAI route | Prefer known supported precision first | audio transcription smoke | OVMS `/v3/audio/transcriptions` |
| CV ONNX/TensorFlow | `ovc` or `openvino.convert_model` | PTQ/INT8 if calibration data exists; otherwise validate FP16 first | generic IR compile + sample input; `benchmark_app` | OVMS classic `/v1` or `/v2` APIs |

## LLM Playbook

Preflight:

- Choose `text-generation`.
- Prefer existing `OpenVINO/<model>-int4-ov` if available and suitable.
- For local exports, default output under `/mnt/d/models/ov/<model>-int4-ov`.

Convert:

```bash
optimum-cli export openvino \
  --model <hf-model-or-local-path> \
  --task text-generation \
  --weight-format int4 \
  --sym \
  --group-size 128 \
  --ratio 1.0 \
  /mnt/d/models/ov/<target>
```

Validate:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/inspect_openvino_artifact.py /mnt/d/models/ov/<target>
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_llm.py /mnt/d/models/ov/<target> --device CPU
```

Deploy:

```bash
docker run -d --rm -v /mnt/d/models/ov/<target>:/model -p 8000:8000 openvino/model_server:latest \
  --model_path /model --model_name <name> --rest_port 8000 --task text_generation --target_device CPU
```

Smoke endpoint:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/ovms_chat_smoke.py --model <name>
```

## Embedding Playbook

Convert:

```bash
optimum-cli export openvino \
  --model <hf-model-or-local-path> \
  --task feature-extraction \
  --weight-format int4 \
  --sym \
  --group-size 128 \
  --ratio 1.0 \
  /mnt/d/models/ov/<target>
```

Validate:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_embedding.py /mnt/d/models/ov/<target>
```

Acceptance:

- Report `last_hidden_state` shape.
- Report dtype.
- If the model will be used in retrieval, perform a small retrieval-quality spot check outside OpenVINO before declaring the compression acceptable.

Deploy:

- Serve through OVMS `/v3/embeddings` when the model is configured as an embedding endpoint.
- NPU embedding support exists for selected models; compile-test before committing to NPU.

## Reranker Playbook

Start with deployment needs:

- If the user needs an API, prefer OVMS Cohere-compatible `/v3/rerank`.
- If the user needs a local library call, inspect the model architecture and choose the correct Optimum class.

Endpoint smoke:

```bash
python3 - <<'PY'
import cohere
client = cohere.Client(base_url="http://localhost:8000/v3", api_key="not_used")
resp = client.rerank(
    model="<model-name>",
    query="openvino deployment",
    documents=["OpenVINO can deploy optimized models.", "Bananas are yellow."],
    top_n=2,
)
print(resp)
PY
```

Acceptance:

- Confirm result ordering makes sense on at least one obvious positive/negative pair.
- Report endpoint path `/v3/rerank` and model name.

## Image Generation Playbook

Convert:

```bash
optimum-cli export openvino \
  --model <hf-model-or-local-path> \
  --task text-to-image \
  --trust-remote-code \
  --weight-format int4 \
  --group-size 64 \
  --ratio 1.0 \
  /mnt/d/models/ov/<target>
```

Endpoint smoke:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v3", api_key="unused")
resp = client.images.generate(
    model="<model-name>",
    prompt="three red cubes on a table",
    size="512x512",
    extra_body={"num_inference_steps": 3, "rng_seed": 45},
)
print(resp.data[0].b64_json[:80])
```

Acceptance:

- Decode one image and verify it is non-empty.
- Report generated size and inference settings.

## CV ONNX/TensorFlow Playbook

Convert:

```bash
ovc /path/to/model.onnx --output_model /mnt/d/models/ov/<target>/openvino_model.xml
```

Validate:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/inspect_openvino_artifact.py /mnt/d/models/ov/<target>
benchmark_app -m /mnt/d/models/ov/<target>/openvino_model.xml -d CPU -hint latency -t 30
```

Acceptance:

- Confirm input/output names and shapes.
- Run one representative sample if preprocessing is known.
