# NPU Playbook

Use this when the user specifically wants NPU or when a local machine has an available `NPU` device.

## NPU Gate

Proceed only if all pass:

1. `openvino_probe.py` lists `NPU`.
2. The model is known or likely to support static shapes.
3. CPU smoke passes first.
4. A small NPU compile/generation test passes.

If any gate fails, report the exact failing gate and fall back to CPU or GPU.

## Good Candidates

- Small LLMs explicitly optimized for NPU.
- Qwen3/Qwen2.5 small embedding or coder models mentioned as NPU-supported in local docs.
- Whisper/ASR or GenAI pipelines only when current local docs and package versions support the target model.

## Risky Candidates

- Generic INT4 exports with no NPU-specific guidance.
- Dynamic-shape models without `--shape` or `--batch_size`.
- Large MoE/LLM models.
- Multimodal component folders where only some components can compile.

## NPU Export/Deploy Rules

- Prefer pre-compressed OpenVINO models known to support NPU.
- For OVMS, set static shape via `--batch_size` or `--shape` when the model has dynamic inputs.
- Keep a CPU-validated artifact unchanged; do not overwrite it while experimenting with NPU.

OVMS NPU example:

```bash
ovms --model_path /path/to/model --model_name <name> --rest_port 8000 --task text_generation --target_device NPU --batch_size 1
```

## NPU Validation

Run:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/openvino_probe.py
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_llm.py /mnt/d/models/ov/<target> --device CPU --max-new-tokens 16
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_llm.py /mnt/d/models/ov/<target> --device NPU --max-new-tokens 16
```

For embeddings:

```bash
python3 /mnt/c/Users/赵晓晓/.codex/skills/openvino-skills/scripts/smoke_embedding.py /mnt/d/models/ov/<target>
```

If the embedding helper does not expose device selection for the needed class, write a one-off compile test rather than claiming NPU support.

## NPU Report

Always include:

- `openvino_probe.py` output summary.
- CPU smoke result.
- NPU smoke result or exact compile error.
- Static shape/batch setting used.
- Fallback recommendation.
