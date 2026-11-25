from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path

from drivine_lab.paths import PROFILES_PATH


def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=20)
        return out.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"(unavailable: {exc})"


def probe() -> dict:
    info: dict = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "rocm_smi": shutil.which("rocm-smi"),
        "amd_smi": shutil.which("amd-smi"),
        "torch": None,
        "hip_available": False,
        "device_count": 0,
        "devices": [],
        "advice": [],
    }

    try:
        import torch

        hip = bool(getattr(torch.version, "hip", None))
        cuda_like = torch.cuda.is_available()
        info["torch"] = {
            "version": torch.__version__,
            "hip": getattr(torch.version, "hip", None),
            "cuda_is_available": cuda_like,
        }
        info["hip_available"] = hip or cuda_like
        if cuda_like:
            info["device_count"] = torch.cuda.device_count()
            for i in range(info["device_count"]):
                props = torch.cuda.get_device_properties(i)
                info["devices"].append(
                    {
                        "index": i,
                        "name": torch.cuda.get_device_name(i),
                        "total_memory_gb": round(props.total_memory / (1024**3), 2),
                    }
                )
    except ImportError:
        info["advice"].append("Install AMD ROCm PyTorch wheels for your gfx target before training.")

    if info["rocm_smi"]:
        info["rocm_smi_report"] = _run(["rocm-smi"])
    if info["amd_smi"]:
        info["amd_smi_report"] = _run(["amd-smi", "static"])

    profiles = json.loads(Path(PROFILES_PATH).read_text(encoding="utf-8"))
    names = " | ".join(f"{p['name']} ({p['gfx']})" for p in profiles)
    info["known_geekom_profiles"] = names

    if not info["hip_available"]:
        info["advice"].append(
            "No HIP/ROCm device visible to PyTorch. On GEEKOM, install the gfx1150/gfx1151 wheel from AMD's index and ensure the user is in render,video groups."
        )
    else:
        info["advice"].append(
            "Device visible. Prefer LoRA + adamw_torch; enable 4-bit QLoRA only with a matching ROCm bitsandbytes."
        )

    return info


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Probe AMD/ROCm readiness for LoRA training.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)
    info = probe()
    if args.json:
        print(json.dumps(info, indent=2))
        return

    print("Drivine LoRA lab — AMD probe")
    print(f"  platform: {info['platform']}")
    print(f"  python:   {info['python']}")
    if info["torch"]:
        print(f"  torch:    {info['torch']['version']} (hip={info['torch']['hip']})")
        print(f"  cuda API available (ROCm): {info['torch']['cuda_is_available']}")
    else:
        print("  torch:    not installed")
    for d in info["devices"]:
        print(f"  device[{d['index']}]: {d['name']} ({d['total_memory_gb']} GB)")
    print(f"  profiles: {info['known_geekom_profiles']}")
    for tip in info["advice"]:
        print(f"  advice:   {tip}")


if __name__ == "__main__":
    main()
