# Python lab — Drivine investigation + AMD LoRA

Train a LoRA adapter on the curated Drivine instruction set using your GEEKOM AMD AI machine (ROCm / Ryzen AI).

## Setup on GEEKOM (gfx1150 / gfx1151)

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate

# Pick the wheel that matches your GPU architecture:
#   gfx1151 — GEEKOM A9 Mega / Max+ (Radeon 8060S)
#   gfx1150 — GEEKOM A9 Max (Radeon 890M)
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ \
  "torch[device-gfx1151]==2.14.0+rocm10.2.0"

pip install -e .
# Optional: seed a real Drivine SQLite graph
pip install -e '.[drivine]'
```

Raise shared GPU memory on Linux if needed (`amd-ttm`), add your user to `render` and `video`, then reboot.

## Commands

```bash
# Probe ROCm / PyTorch visibility
drivine-check-amd

# Export JSONL (optional; trainer also reads the JSON array)
drivine-export-jsonl

# Seed investigation graph (requires drivine[sqlite])
drivine-seed-graph

# LoRA SFT — defaults target geekom-a9-mega profile
drivine-train-lora --profile geekom-a9-mega

# Smoke on CPU without a GPU
drivine-train-lora --cpu --max-steps 2 --model Qwen/Qwen2.5-0.5B-Instruct

# Try the adapter
drivine-infer --adapter ../outputs/drivine-lora \
  --prompt "How does loadNearest work in Drivine?"
```

Set `DRIVINE_QLORA=1` only after a matching ROCm `bitsandbytes` is installed.

## Profiles

See `../data/amd_profiles.json` for GEEKOM defaults (rank, seq len, steps). Override any flag on the CLI.
