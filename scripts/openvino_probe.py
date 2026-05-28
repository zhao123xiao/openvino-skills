#!/usr/bin/env python3
"""Print OpenVINO version, available devices, and key device properties."""

from __future__ import annotations

import importlib.metadata as metadata

import openvino as ov


def main() -> int:
    try:
        print("openvino", metadata.version("openvino"))
    except metadata.PackageNotFoundError:
        print("openvino version unknown")

    core = ov.Core()
    print("available_devices", core.available_devices)

    for device in core.available_devices:
        print(f"\n[{device}]")
        for prop in ("FULL_DEVICE_NAME", "SUPPORTED_PROPERTIES", "OPTIMIZATION_CAPABILITIES"):
            try:
                print(prop, core.get_property(device, prop))
            except Exception as exc:
                print(prop, f"ERROR: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
