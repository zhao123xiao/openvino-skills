# Test And Benchmark SOP

## Test Order

1. Check files exist.
2. Probe OpenVINO devices.
3. Load/compile the model.
4. Run a tiny deterministic inference.
5. If serving, hit the endpoint.
6. Benchmark only after the smoke test passes.
7. Write results with `references/report-template.md`.

## File Validation

```bash
MODEL_DIR=/mnt/d/models/ov/<target-name>
du -sh "$MODEL_DIR"
find "$MODEL_DIR" -maxdepth 1 -type f -printf '%f %s\n' | sort
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/inspect_openvino_artifact.py "$MODEL_DIR"
```

Look for missing tokenizer/config files on GenAI models and missing `.bin` pairs for `.xml` files.

## Device Probe

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/openvino_probe.py
```

Report `available_devices` and the device actually used in testing.

## Generic IR Smoke Test

```python
import openvino as ov

core = ov.Core()
model = core.read_model("/mnt/d/models/ov/<target>/openvino_model.xml")
compiled = core.compile_model(model, "CPU")
print("inputs", [i.get_any_name() for i in compiled.inputs])
print("outputs", [o.get_any_name() for o in compiled.outputs])
```

For real validation, feed a representative sample input matching the model shape and dtype.

## Causal LM Smoke Test

Preferred reusable command:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_llm.py /mnt/d/models/ov/<target> --device CPU
```

Equivalent inline pattern:

```python
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM

model_dir = "/mnt/d/models/ov/<target>"
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, trust_remote_code=True)
model = OVModelForCausalLM.from_pretrained(model_dir, local_files_only=True, device="CPU", trust_remote_code=True)
inputs = tokenizer("Say hello in one short sentence.", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=32, do_sample=False)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Embedding Smoke Test

Preferred reusable command:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_embedding.py /mnt/d/models/ov/<target>
```

Equivalent inline pattern:

```python
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForFeatureExtraction

model_dir = "/mnt/d/models/ov/<target>"
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, trust_remote_code=True)
model = OVModelForFeatureExtraction.from_pretrained(model_dir, local_files_only=True, compile=False)
inputs = tokenizer(["hello openvino", "中文向量测试"], padding=True, return_tensors="pt")
out = model(**inputs)
print("last_hidden_state", tuple(out.last_hidden_state.shape), out.last_hidden_state.dtype)
```

## OVMS Endpoint Smoke Test

For GenAI chat:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/ovms_chat_smoke.py --model <model-name>
```

For classic REST/KServe APIs, call the documented `/v1` or `/v2` endpoint for the model's input format.

## Benchmark App

Use OpenVINO `benchmark_app` for generic IR performance:

```bash
benchmark_app -m /mnt/d/models/ov/<target>/openvino_model.xml -d CPU -hint latency -t 30
benchmark_app -m /mnt/d/models/ov/<target>/openvino_model.xml -d GPU -hint throughput -t 30
```

For dynamic inputs, pass explicit shape:

```bash
benchmark_app -m model.xml -d CPU -shape "input[1,3,224,224]" -hint latency -t 30
```

Always report:

- OpenVINO version.
- Model path and precision.
- Device and performance hint.
- Shape/batch size.
- Test duration.
- Latency, throughput, and any first-token/token-per-second metrics for GenAI.

## GenAI Benchmarking

For text generation, record:

- Prompt tokens.
- Generated tokens.
- First-token latency if measured.
- Total generation time.
- Tokens/sec.
- Device and cache/use_cache settings.

Preferred local benchmark wrapper:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/benchmark_openvino_model.py \
  /mnt/d/models/ov/<target> \
  --kind llm \
  --devices CPU GPU NPU \
  --max-new-tokens 64 \
  --repeats 3
```

Embedding benchmark:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/benchmark_openvino_model.py \
  /mnt/d/models/ov/<target> \
  --kind embedding \
  --devices CPU GPU \
  --repeats 5
```

Generic IR wrapper around `benchmark_app`:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/benchmark_openvino_model.py \
  /mnt/d/models/ov/<target> \
  --kind generic \
  --devices CPU GPU \
  --hint latency \
  --seconds 30
```

Use local helper scripts under `/mnt/d/scripts/openvino` when they match the model family, but read them before reuse.
