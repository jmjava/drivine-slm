# drivine-slm

Drivine-domain track in the local coding SLM family.

| Sibling | Role |
| --- | --- |
| [jmjava/slm-setup](https://github.com/jmjava/slm-setup) | MCP bridge that serves a local model to Cursor, Copilot, and Claude |
| [jmjava/embabel-slm](https://github.com/jmjava/embabel-slm) | Embabel / Spring / Kotlin model program and harness |
| **jmjava/drivine-slm** (this repo) | Drivine graph-client corpus, investigation UI, and AMD LoRA recipes for the Halo host |
| [jmjava/slm-kiln](https://github.com/jmjava/slm-kiln) | Kiln runtime for GGUFs this track (and embabel-slm) export — not a trainer |
| [jmjava/weekend-lab-plan](https://github.com/jmjava/weekend-lab-plan) | Private machine plan (not a source copy) |

Training stays out of `slm-setup`. Delivery back into the bridge waits until a later operator decision, same rule as `embabel-slm`.

## Paper

Confirmatory **Part C** (Drivine) is pre-registered with Embabel **Part B** under one combined dose ladder on a **742-task** holdout (**371 Embabel + 371 Drivine**). The paper trains **one combined LoRA adapter** on admitted Embabel+Drivine examples drawn from a single ordered list at six nested prefixes (500 through 16,000). The sole confirmatory contrast is **16,000 vs 500** examples at training seed **20260227**; seeds **20260228** and **20260229** are mandatory robustness replications. Model S / M / L tags are chosen on **Embabel DEV only** and are reused for Drivine scoring. Normative protocol: [embabel-slm `docs/protocol/preregistration.md`](https://github.com/jmjava/embabel-slm/blob/main/docs/protocol/preregistration.md) (`study_id`: `two-domain-example-dose-v1`).

This repo supplies the Drivine corpus, the **pilot executable runner** (`python/drivine_runner`, known-good/known-bad stdlib tasks + tests), and local lab tooling. **Confirmatory harness is incomplete:** Drivine package/JVM oracles, the ~20 pilot executable development set, the **371-task** confirmatory holdout, Ollama batch wiring, and **all confirmatory scored rows remain 0**. Pilot tasks under `benchmarks/pilot/` are for harness development only and must not support confirmatory claims.

`data/drivine_instruct.json` (100 pairs) is **training/DEV only**; it is excluded from the confirmatory holdout by the same near-duplicate rule and is not a scored benchmark.

### Pilot harness (executable tasks)

```bash
PYTHONPATH=python python -m drivine_runner validate --task benchmarks/pilot/pilot-query-001/task.json
PYTHONPATH=python python -m drivine_runner run \
  --task benchmarks/pilot/pilot-query-001/task.json \
  --answer benchmarks/pilot/pilot-query-001/answers/good.md
PYTHONPATH=python python -m drivine_runner self-test
```

Task specs use versioned JSON (`task_spec_version`: `1`); see `python/drivine_runner/task_spec.schema.json`.

### Local lab order (UI / Halo training — not the paper adapter pipeline)

1. Curate and pin Drivine concepts + instruction pairs from [drivine.org](https://drivine.org/).
2. Use the investigation UI and `python/` LoRA scripts for local experimentation on the **GEEKOM Halo** (primary paper host as of 25 Nov 2026; A13 green).
3. Paper training, retrieval packs, and holdout scoring run from **embabel-slm** and **slm-kiln** on the combined dose recipe; they are separate from the ad hoc `drivine-train-lora` path in this repo.

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
| `python/` | LoRA train / infer / AMD probe / Drivine seed / `drivine_runner` harness |
| `benchmarks/pilot/` | Stdlib-only pilot tasks (not the 371-task holdout) |
| `outputs/` | Adapter checkpoints (gitignored) |

## Standing rules

- Prefer **LoRA + `adamw_torch`** on AMD; enable 4-bit only with a matching ROCm `bitsandbytes`.
- Do not commit model weights, LAN addresses, or a working `OLLAMA_BASE_URL`.
- Confirm API facts against current drivine.org docs before claiming a pass.
- Serving an adapter through `slm-setup` is a later step, not this repo's job.
