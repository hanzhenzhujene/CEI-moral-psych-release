# Jenny Moral-Psych Runbook

## What The April 14 Notes Mean For This Repo

This repo is now set up so you can run your five assigned moral-psych benchmarks through the `Inspect` harness path in CEI.

From the meeting notes, the operational defaults are:

- Use Eric's CEI repo as the shared harness base.
- Set `temperature=0`.
- Start with the agreed model roster and compare large, medium, and small variants.
- Save results through Inspect logs under `results/inspect/logs/`.
- Use `inspect` when the benchmark needs more flexible prompting or custom scoring.

## Benchmarks Added

The following Inspect task files now exist under `src/inspect/evals/`:

- `unimoral.py`
  - `unimoral_action_prediction`
  - `unimoral_moral_typology`
  - `unimoral_factor_attribution`
  - `unimoral_consequence_generation`
- `smid.py`
  - `smid_moral_rating`
  - `smid_foundation_classification`
- `denevil.py`
  - `denevil_generation`
- `value_kaleidoscope.py`
  - `value_prism_relevance`
  - `value_prism_valence`
- `ccd_bench.py`
  - `ccd_bench_selection`

## Data Requirements

Some of these datasets are public, while others are gated or image-based.

- `UniMoral`
  - Set `UNIMORAL_DATA_DIR` to a folder containing files like `English_long.csv`, `English_short.csv`, `Arabic_long.csv`, etc.
  - The harness also supports `UNIMORAL_LANGUAGE=all|English|Arabic|Chinese|Hindi|Russian|Spanish`.
  - Default prompt mode is `UNIMORAL_MODE=np`.
- `SMID`
  - Set `SMID_DATA_DIR` to a folder containing `SMID_norms.csv` plus the image files or `image.zip`.
  - Use a vision-capable model.
- `Denevil`
  - Set `DENEVIL_DATA_FILE` to a local CSV, JSON, or JSONL export of MoralPrompt.
  - If you only have the local `FULCRA` dialogue data under `data/denevil/`, you can run the explicit proxy task `denevil_fulcra_proxy_generation`. This is useful for harness plumbing and exploratory generation, but it is not the benchmark-faithful `MoralPrompt` evaluation from the paper.
- `Value Kaleidoscope`
  - Set `VALUEPRISM_RELEVANCE_FILE` and `VALUEPRISM_VALENCE_FILE` to the local relevance / valence CSV exports, or authenticate for the gated Hugging Face dataset and let the harness call `load_dataset("allenai/ValuePrism", "relevance" | "valence")`.
- `CCD-Bench`
  - No local dataset is required by default. The harness will download and cache the official public JSON.

## Setup

```bash
cd /path/to/CEI
uv sync
```

If you want to use OpenRouter with Inspect:

```bash
export OPENROUTER_API_KEY="..."
```

`src/inspect/run.py` will auto-load `CEI/.env` and `CEI/.env.local` if those files exist.

## Current Authoritative Status Package

Because the April 17-19, 2026 work was recovered across multiple namespaces, the cleanest source of truth is now the generated authoritative status package rather than any single run folder.

At the latest refreshed checkpoint, the current `Option 1` slice is closed at `19 / 19` authoritative tasks complete.

Rebuild it with:

```bash
cd /path/to/CEI
python3 scripts/build_authoritative_option1_status.py
```

Current outputs:

- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.csv`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.md`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/live-heartbeat.csv`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/live-heartbeat.md`

Interpret them this way:

- `authoritative-summary.*`
  - use these for mentor-facing benchmark status and for any statement about what is officially complete
- `live-heartbeat.*`
  - use these to monitor still-running jobs when the `.eval` archive has not yet flushed fresh sample files
  - these files are monitoring signals, not replacements for the authoritative flushed counts

Current authoritative namespaces:

- `2026-04-17-option1-full-funded`
- `2026-04-17-option1-full-funded-gemma-paid-v2`
- `2026-04-18-option1-full-funded-qwen-recovery-v1`
- `2026-04-18-denevil-fulcra-proxy-formal-v3`
- `2026-04-18-denevil-fulcra-proxy-recovery-v1`

## Core Commands

Run a smoke test for one benchmark:

```bash
cd /path/to/CEI/src/inspect
uv run --package cei-inspect \
  python run.py \
  --tasks evals/unimoral.py \
  --model openrouter/qwen/qwen-2.5-72b-instruct \
  --temperature 0 \
  --limit 5 \
  --no_sandbox
```

Run only the UniMoral action-prediction task by task name:

```bash
cd /path/to/CEI/src/inspect
UNIMORAL_DATA_DIR="/absolute/path/to/Final_data" \
UNIMORAL_LANGUAGE=English \
UNIMORAL_MODE=np \
uv run --package cei-inspect \
  python run.py \
  --tasks unimoral_action_prediction \
  --model openrouter/qwen/qwen-2.5-72b-instruct \
  --temperature 0 \
  --no_sandbox
```

Run SMID with a vision model:

```bash
cd /path/to/CEI/src/inspect
SMID_DATA_DIR="/absolute/path/to/SMID" \
uv run --package cei-inspect \
  python run.py \
  --tasks evals/smid.py \
  --model openrouter/openai/gpt-4o \
  --temperature 0 \
  --limit 10 \
  --no_sandbox
```

Run Value Kaleidoscope against a local export:

```bash
cd /path/to/CEI/src/inspect
VALUEPRISM_RELEVANCE_FILE="/absolute/path/to/relevance_train.csv" \
VALUEPRISM_VALENCE_FILE="/absolute/path/to/valence_train.csv" \
uv run --package cei-inspect \
  python run.py \
  --tasks evals/value_kaleidoscope.py \
  --model openrouter/google/gemma-3-27b-it \
  --temperature 0 \
  --limit 50 \
  --no_sandbox
```

Run CCD-Bench fully:

```bash
cd /path/to/CEI/src/inspect
uv run --package cei-inspect \
  python run.py \
  --tasks evals/ccd_bench.py \
  --model openrouter/deepseek/deepseek-chat-v3-0324 \
  --temperature 0 \
  --no_sandbox
```

Run the local FULCRA-backed Denevil proxy now:

```bash
cd /path/to/CEI
DENEVIL_DATA_FILE="/absolute/path/to/data_hybrid.jsonl" \
uv run --package cei-inspect python src/inspect/run.py \
  --tasks src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation \
  --model openrouter/google/gemma-3-4b-it \
  --temperature 0 \
  --limit 10 \
  --no_sandbox
```

Run the benchmark-faithful Denevil path once a true MoralPrompt export is available:

```bash
cd /path/to/CEI
DENEVIL_DATA_FILE="/absolute/path/to/moralprompt.jsonl" \
uv run --package cei-inspect python src/inspect/run.py \
  --tasks src/inspect/evals/denevil.py::denevil_generation \
  --model openrouter/google/gemma-3-4b-it \
  --temperature 0 \
  --limit 10 \
  --no_sandbox
```

## Suggested Model Sweep

The meeting notes pointed to these families:

- Qwen
- Minimax
- DeepSeek
- Colombo
- Gemma

A practical way to run them is one family at a time, always keeping `--temperature 0`, and tracking large, medium, and small variants in the same spreadsheet or notebook.

## Notes On Scoring

- `UniMoral`
  - Action prediction, moral typology, and factor attribution are scored directly.
  - Consequence generation uses max ROUGE-L against available reference consequences.
- `SMID`
  - Moral rating is scored as integer match against rounded normative ratings.
  - Foundation classification is scored against the dominant normative foundation.
- `Denevil`
  - The current harness focuses on prompt execution and response capture. This is the least turnkey benchmark of the five because the paper's core evaluation depends on the MoralPrompt export and judge logic.
  - `denevil_fulcra_proxy_generation` is an exploratory fallback only. Use it to validate the harness path against the local FULCRA dialogue data, not as a paper-faithful substitute.
- `Value Kaleidoscope`
  - The harness turns ValuePrism into two structured tasks: relevance and valence.
- `CCD-Bench`
  - The harness validates the selected option format and preserves the option order in sample metadata so you can analyze cluster preferences from the logs.

## Fastest First Run

If you want the fastest path to momentum, start in this order:

1. `ccd_bench.py`
2. `value_kaleidoscope.py`
3. `unimoral.py`
4. `smid.py`
5. `denevil.py`

That order minimizes gating and asset friction.
