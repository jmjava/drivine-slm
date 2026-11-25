# Drivine LoRA Lab

Investigate [drivine.org](https://drivine.org/) and fine-tune a local LoRA adapter on a **GEEKOM AMD AI** machine (Ryzen AI / Radeon `gfx1150` · `gfx1151`).

## What you get

1. **Lab UI** — browse Drivine concepts, the instruction dataset, and AMD training profiles.
2. **Curated SFT data** — `data/drivine_instruct.json` (API Q&A, views, Cypher, graph RAG, AMD tips).
3. **Python training lab** — ROCm-friendly PEFT/TRL LoRA scripts plus an optional Drivine SQLite seed.

## Quick start (UI)

```bash
npm install
npm run dev
```

Open the printed local URL. The UI ships with sample data only — training happens on your GEEKOM.

## Train on GEEKOM AMD

```bash
cd python
python3 -m venv .venv && source .venv/bin/activate

# Match your silicon (example: A9 Mega / Max+ → gfx1151)
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ \
  "torch[device-gfx1151]==2.14.0+rocm10.2.0"

pip install -e .
drivine-check-amd
drivine-train-lora --profile geekom-a9-mega
drivine-infer --adapter ../outputs/drivine-lora --prompt "How does loadNearest work in Drivine?"
```

Optional investigation graph with drivine-python:

```bash
pip install -e '.[drivine]'
drivine-seed-graph
```

Full notes: [`python/README.md`](python/README.md).

## Layout

| Path | Purpose |
| --- | --- |
| `src/` | Next.js investigation UI |
| `data/` | Concepts, instruction pairs, AMD profiles |
| `python/` | LoRA train / infer / AMD probe / Drivine seed |
| `outputs/` | Adapter checkpoints (gitignored) |

## Notes

- Prefer **LoRA + `adamw_torch`** on AMD; turn on 4-bit QLoRA only with a matching ROCm `bitsandbytes`.
- Raise shared GPU memory (`amd-ttm` on Linux) before larger models.
- Dataset rows are study aids — confirm APIs against current drivine.org docs.
