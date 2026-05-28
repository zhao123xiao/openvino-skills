"""Path helpers for Windows and WSL OpenVINO workflows."""

from __future__ import annotations

import os
import re
from pathlib import Path


def normalize_path(path: str | Path) -> Path:
    """Convert Windows drive paths to WSL mount paths when running on POSIX."""

    raw = str(path)
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", raw)
    if os.name != "nt" and match:
        drive = match.group(1).lower()
        rest = match.group(2).replace("\\", "/")
        return Path(f"/mnt/{drive}/{rest}")
    return Path(raw)
