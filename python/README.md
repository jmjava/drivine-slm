# Python lab — drivine-slm on AMD

Train a LoRA adapter on the curated Drivine instruction set using the Halo /
GEEKOM AMD AI host (ROCm / Ryzen AI). This package is the training side of
[drivine-slm](https://github.com/jmjava/drivine-slm); serving stays in
[slm-setup](https://github.com/jmjava/slm-setup).

## Setup (gfx1150 / gfx1151)

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate

# Pick the wheel that matches your GPU architecture:
#   gfx1151 — Halo / A9 Mega / Max+ (Radeon 8060S)
#   gfx1150 — A9 Max (Radeon 890M)
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ \
  "torch[device-gfx1151]==2.14.0+rocm10.2.0"

pip install -e .
# Optional: seed a real Drivine SQLite graph
pip install -e '.[drivine]'
```

Raise shared GPU memory on Linux if needed (`amd-ttm`), add your user to
`render` and `video`, then reboot.

## Commands

```bash
drivine-check-amd
drivine-export-jsonl
drivine-seed-graph
drivine-train-lora --profile geekom-a9-mega
drivine-train-lora --cpu --max-steps 2 --model Qwen/Qwen2.5-0.5B-Instruct
drivine-infer --adapter ../outputs/drivine-lora \
  --prompt "How does loadNearest work in Drivine?"
```

Set `DRIVINE_QLORA=1` only after a matching ROCm `bitsandbytes` is installed.

## Profiles

See `../data/amd_profiles.json` for Halo / GEEKOM defaults. Override any flag
on the CLI.
