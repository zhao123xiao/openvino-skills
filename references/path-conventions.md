# Path Conventions

默认向用户展示 Windows 路径。只有在 WSL/Linux shell 命令中执行时，才使用 `/mnt/<drive>/...` 形式。

## Default Paths

| Purpose | Windows path | WSL path |
| --- | --- | --- |
| Local OpenVINO models | `D:\models\ov\<model>` | `/mnt/d/models/ov/<model>` |
| Alternate local model root | `D:\openvino-models\<model>` | `/mnt/d/openvino-models/<model>` |
| Codex skill folder on Windows mount | `C:\Users\赵晓晓\.codex\skills\openvino-skills` | `/mnt/c/Users/赵晓晓/.codex/skills/openvino-skills` |

## Rules

- User-facing summaries and final reports should prefer Windows paths such as `D:\models\ov\Qwen3-0.6B`.
- Bash examples running inside WSL should define a WSL variable, for example `MODEL_DIR=/mnt/d/models/ov/Qwen3-0.6B`.
- Python helper scripts in this skill accept both Windows and WSL paths. On WSL, `D:\models\ov\Qwen3-0.6B` is normalized to `/mnt/d/models/ov/Qwen3-0.6B`.
- Docker commands running from WSL should mount WSL paths, for example `-v /mnt/d/models/ov/Qwen3-0.6B:/model`.
- Native Windows commands should not contain `/mnt/...`.

## Example

Report this to the user:

```text
模型路径：D:\models\ov\Qwen3-0.6B
```

Run this in WSL:

```bash
MODEL_DIR=/mnt/d/models/ov/Qwen3-0.6B
python3 scripts/inspect_openvino_artifact.py "$MODEL_DIR"
```

Or pass the Windows path directly to the skill helper:

```bash
python3 scripts/inspect_openvino_artifact.py 'D:\models\ov\Qwen3-0.6B'
```
