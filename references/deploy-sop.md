# Deploy SOP

## Deployment Decision

Choose one path:

- **Python Runtime**: best for local scripts, application integration, and debugging.
- **OpenVINO GenAI**: best for local LLM/VLM/image/speech pipelines when GenAI APIs fit.
- **OpenVINO Model Server Docker**: best for local or server REST/gRPC serving.
- **OVMS bare metal**: best when Docker is unavailable or Windows binary deployment is required.
- **KServe/Kubernetes**: best for managed cluster deployment.

## Endpoint Matrix

| Use case | OVMS task/config | Endpoint | Client |
| --- | --- | --- | --- |
| Chat/LLM | `--task text_generation` | `/v3/chat/completions` or `/v3/completions` | OpenAI client |
| Embedding | embedding model config | `/v3/embeddings` | OpenAI client |
| Reranker | rerank model config | `/v3/rerank` | Cohere client or HTTP |
| Text-to-image | image generation graph/task | `/v3/images/generations` | OpenAI image client |
| Image edit/inpaint | image edit graph/task | `/v3/images/edits` | multipart/OpenAI-style client |
| ASR/Whisper | speech-to-text task | `/v3/audio/transcriptions` | OpenAI audio-style client |
| Classic CV/IR | model repository path | `/v1` TFS or `/v2` KServe | REST/gRPC |

## Python Runtime Pattern

Probe devices first:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/openvino_probe.py
```

Then load and compile with an explicit device:

```python
import openvino as ov

core = ov.Core()
model = core.read_model("/mnt/d/models/ov/<target>/openvino_model.xml")
compiled = core.compile_model(model, "CPU")
```

For Hugging Face Optimum exports, use the matching Optimum class, for example `OVModelForCausalLM` for text generation or `OVModelForFeatureExtraction` for embeddings.

## OVMS Basic Model Deployment

Docker:

```bash
docker run -d --rm \
  -v /path/to/models:/models \
  -p 9000:9000 -p 8000:8000 \
  openvino/model_server:latest \
  --model_path /models/<model-folder> \
  --model_name <model-name> \
  --port 9000 \
  --rest_port 8000 \
  --log_level DEBUG
```

Bare metal:

```bash
ovms \
  --model_path /path/to/model \
  --model_name <model-name> \
  --port 9000 \
  --rest_port 8000 \
  --log_level DEBUG
```

## OVMS GenAI Deployment

For an existing local GenAI model:

```bash
docker run -d --rm \
  -v /path/to/model:/model \
  -p 8000:8000 \
  openvino/model_server:latest \
  --model_path /model \
  --model_name <model-name> \
  --rest_port 8000 \
  --task text_generation \
  --target_device CPU \
  --log_level DEBUG
```

For direct Hugging Face/OpenVINO pull mode:

```bash
docker run --rm \
  -v /path/to/model-repository:/models:rw \
  -p 8000:8000 \
  openvino/model_server:latest \
  --pull \
  --source_model OpenVINO/Qwen3-8B-int4-ov \
  --model_repository_path /models \
  --model_name qwen3-8b-int4-ov \
  --task text_generation \
  --target_device CPU \
  --rest_port 8000
```

On GPU Docker hosts, pass device access and use a GPU image/tag when required:

```bash
docker run --rm -d \
  --device=/dev/dri \
  --group-add=$(stat -c "%g" /dev/dri/render* | head -n 1) \
  -u $(id -u):$(id -g) \
  -v /path/to/model:/model \
  -p 8000:8000 \
  openvino/model_server:latest-gpu \
  --model_path /model \
  --model_name <model-name> \
  --rest_port 8000 \
  --task text_generation \
  --target_device GPU
```

For WSL2 GPU Docker, use `/dev/dxg` and mount `/usr/lib/wsl` when the environment requires it.

## OpenAI-Compatible Client Smoke

OVMS GenAI exposes OpenAI-compatible endpoints under `/v3`.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v3", api_key="unused")
response = client.chat.completions.create(
    model="<model-name>",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=False,
)
print(response.choices[0].message)
```

For VLM, encode images as base64 data URLs in `messages[].content`. For image generation, call `client.images.generate()` against the same `/v3` base URL when the served task supports it.

Embedding smoke:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v3", api_key="unused")
resp = client.embeddings.create(model="<model-name>", input=["hello", "openvino"])
print(len(resp.data), len(resp.data[0].embedding))
```

Rerank smoke:

```python
import cohere

client = cohere.Client(base_url="http://localhost:8000/v3", api_key="not_used")
resp = client.rerank(
    model="<model-name>",
    query="openvino deployment",
    documents=["OpenVINO serves optimized models.", "The sky is blue."],
)
print(resp)
```

## Metrics And Cache

Enable metrics when operating a service:

```bash
--rest_port 8000 --metrics_enable
```

Use model cache deliberately:

```bash
--cache_dir /path/to/cache
```

Cache is most useful for repeated GPU model loading. It may not help CPU and can grow unexpectedly with dynamic or auto shapes, so test before production.

## KServe Sketch

For OpenVINO Model Server KServe deployments, set the runtime and task explicitly:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: qwen3-8b-int4-ov
spec:
  predictor:
    model:
      runtime: kserve-openvino
      modelFormat:
        name: huggingface
      args:
        - --source_model=OpenVINO/Qwen3-8B-int4-ov
        - --model_repository_path=/tmp
        - --task=text_generation
        - --target_device=CPU
      resources:
        requests:
          cpu: "16"
          memory: "8G"
        limits:
          cpu: "16"
          memory: "8G"
```
