# Device And Troubleshooting SOP

## Device Selection

- `CPU`: safest baseline and first smoke-test target.
- `GPU`: useful for throughput and some GenAI workloads; requires runtime drivers and device access.
- `NPU`: useful for supported low-power GenAI workloads; requires static shapes and compatible model/export.
- `AUTO`: lets OpenVINO choose and fall back across devices.
- `AUTO:GPU,CPU`: explicit priority when GPU should be tried before CPU.

Always start with:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/openvino_probe.py
```

## NPU Rules

OpenVINO Model Server notes that NPU executes models with static input and output shapes. If the model has dynamic shape, reset shape with `--batch_size` or `--shape` where supported.

Example:

```bash
ovms --model_path model --model_name resnet --port 9000 --target_device NPU --batch_size 1
```

Do not assume any INT4 model is NPU-compatible. Prefer models explicitly optimized for NPU or verify with a compile smoke test.

## GPU Rules

For Linux Docker:

```bash
--device=/dev/dri --group-add=$(stat -c "%g" /dev/dri/render* | head -n 1)
```

For WSL2 Docker, use `/dev/dxg` and mount `/usr/lib/wsl` when needed.

If GPU compile fails, rerun on CPU to separate model correctness from device/runtime issues.

## Performance Hints

- `LATENCY`: optimize response time.
- `THROUGHPUT`: optimize aggregate throughput.
- `CUMULATIVE_THROUGHPUT`: with `AUTO:GPU,CPU`, can load the model to multiple devices.

OVMS example:

```bash
--plugin_config '{"PERFORMANCE_HINT": "CUMULATIVE_THROUGHPUT"}' --target_device AUTO:GPU,CPU
```

Avoid combining `NUM_STREAMS` and `PERFORMANCE_HINT` unless the exact plugin docs say the combination is valid.

## Automatic Batching

Automatic batching can improve utilization by grouping requests transparently. It applies to static models and is commonly associated with GPU throughput configurations. Avoid using it blindly with dynamic-shape models.

Example:

```bash
--plugin_config '{"AUTO_BATCH_TIMEOUT": 200}' --target_device "BATCH:CPU(16)"
```

## Model Cache

Model cache can speed up repeated model loading, especially on GPU:

```bash
--cache_dir /path/to/cache
```

Cache files are tied to model/server version, device, hardware, and shape parameters. Dynamic/auto shapes can regenerate many cache files and consume disk space.

## Common Failures

- Missing `.bin` for `.xml`: conversion/export incomplete.
- Tokenizer missing: Hugging Face/GenAI export incomplete; rerun export or copy tokenizer files.
- `NPU` compile failure: check static shape, precision, and model family support; try CPU to isolate.
- Docker GPU unavailable: check `/dev/dri` or `/dev/dxg` mount and group permissions.
- OVMS starts but endpoint fails: verify `--task`, `--model_name`, model repository path, and `/v3` vs `/v1`/`/v2` API choice.
- Low throughput: check batch/shape, performance hint, device, model precision, and whether benchmark is measuring first-run compile time.
- Image/VLM URL input rejected: OVMS VLM pipelines may block remote image URLs by default; use base64 data URLs or configure allowed domains deliberately.
- Cache grows unexpectedly: disable cache or fix static shapes before re-enabling cache.

## Escalation Path

1. Reduce to CPU smoke test.
2. Compile only, without service layer.
3. Run with minimal sample input.
4. Re-enable target device.
5. Re-enable service/deployment.
6. Benchmark only after functional correctness is stable.
