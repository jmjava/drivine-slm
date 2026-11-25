# drivine-slm

Drivine-domain track in the local coding SLM family.

| Sibling | Role |
| --- | --- |
| [jmjava/slm-setup](https://github.com/jmjava/slm-setup) | MCP bridge that serves a local model to Cursor, Copilot, and Claude |
| [jmjava/embabel-slm](https://github.com/jmjava/embabel-slm) | Embabel / Spring / Kotlin model program and harness |
| **jmjava/drivine-slm** (this repo) | Drivine graph-client corpus, investigation UI, and AMD LoRA recipes for the Halo host |
| [jmjava/weekend-lab-plan](https://github.com/jmjava/weekend-lab-plan) | Private machine plan (not a source copy) |

Training stays out of `slm-setup`. Delivery back into the bridge waits until a later operator decision, same rule as `embabel-slm`.

## Order (do not invert)

1. Curate and pin Drivine concepts + instruction pairs from [drivine.org](https://drivine.org/).
2. Score a clean official coding tag on those tasks via Ollama on the **GEEKOM Halo** (primary paper host as of 25 Nov 2026; A13 green).
3. Measure retrieval / prompt packing before weights when a harness exists.
4. Run one LoRA or QLoRA on the Halo (Ryzen AI Max+ / `gfx1151`) only for the gap that packing did not close. Downstairs NVIDIA is fallback only.

## What you get

1. **Lab UI** — concept map, searchable SFT dataset, GEEKOM / RDNA profiles.
2. **Corpus** — `data/drivine_instruct.json` (100 instruction pairs: API Q&A, Nest, stamps, Cypher compiler, Oracle, views, graph RAG).
3. **Python lab** — ROCm-friendly PEFT/TRL LoRA scripts + optional Drivine SQLite seed.

## Quick start (UI)

```bash
npm install
npm run dev
```

## Train on the Halo / GEEKOM AMD box

```bash
cd python
python3 -m venv .venv && source .venv/bin/activate

# Match silicon: gfx1151 = A9 Mega / Max+ (8060S); gfx1150 = A9 Max (890M)
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ \
  "torch[device-gfx1151]==2.14.0+rocm10.2.0"

pip install -e .
drivine-check-amd
drivine-train-lora --profile geekom-a9-mega
drivine-infer --adapter ../outputs/drivine-lora --prompt "How does loadNearest work in Drivine?"
```

Optional investigation graph:

```bash
pip install -e '.[drivine]'
drivine-seed-graph
```

Details: [`python/README.md`](python/README.md).

## Layout

| Path | Purpose |
| --- | --- |
| `src/` | Next.js investigation UI |
| `data/` | Concepts, instruction pairs, AMD profiles |
| `python/` | LoRA train / infer / AMD probe / Drivine seed |
| `outputs/` | Adapter checkpoints (gitignored) |

## Standing rules

- Prefer **LoRA + `adamw_torch`** on AMD; enable 4-bit only with a matching ROCm `bitsandbytes`.
- Do not commit model weights, LAN addresses, or a working `OLLAMA_BASE_URL`.
- Confirm API facts against current drivine.org docs before claiming a pass.
- Serving an adapter through `slm-setup` is a later step, not this repo's job.
