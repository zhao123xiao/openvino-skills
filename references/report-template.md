# Report Template

Use this shape for final answers after OpenVINO conversion, deployment, testing, or benchmarking.

## Conversion / Quantization

- Source model:
- Target directory:
- Task:
- Precision:
- Command:
- Key output files:
- Size:
- Notes/warnings:

## Validation

- OpenVINO version:
- Available devices:
- Tested device:
- Smoke command:
- Smoke result:
- Failure or caveat:

## Deployment

- Runtime: Python / GenAI / OVMS Docker / OVMS bare metal / KServe
- Model name:
- Endpoint:
- Device:
- Command:
- Endpoint smoke result:

## Benchmark

- Model path:
- Precision:
- Device:
- Shape/batch:
- Hint/config:
- Duration:
- Latency:
- Throughput:
- Tokens/sec or first-token latency for GenAI:
- Benchmark command:
- Failed devices and errors:

## Next Action

- State the next concrete action only when it is useful, such as running a longer benchmark, adding calibration data, or trying another device.
