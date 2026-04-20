# Reproducibility Guide

This document describes both:

1. how to recreate the **public release artifacts**, and
2. how to run a small **benchmark smoke test** with the harness.

## Environment

The canonical environment is the checked-in `uv.lock` file.

### Setup

```bash
make setup
cp .env.example .env
```

If `uv` is installed outside your shell `PATH`, use `make UV=/absolute/path/to/uv <target>`.

Fill in `.env` with:

- model API keys such as `OPENROUTER_API_KEY`
- local dataset paths such as `UNIMORAL_DATA_DIR` and `SMID_DATA_DIR`

For benchmark-by-benchmark data expectations, see [`data-access.md`](data-access.md).

## Test Suite

```bash
make test
```

This validates:

- the legacy ETHICS path
- the `Inspect AI` CLI wrapper
- the moral-psych dataset adapters
- the benchmark task builders for `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, and `Denevil`

For the public QA gate used in CI, run:

```bash
make audit
```

This is the fastest end-to-end public check because it runs the full test suite and refreshes the tracked release artifacts in one command.

## Rebuild the Public Release

```bash
make release
```

This target regenerates the public release package from the tracked authoritative snapshot committed under `results/release/2026-04-19-option1/source/`.

### Expected Outputs

Release tables:

- `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/topline-summary.md`
- `results/release/2026-04-19-option1/benchmark-catalog.csv`
- `results/release/2026-04-19-option1/benchmark-comparison.csv`
- `results/release/2026-04-19-option1/model-summary.csv`
- `results/release/2026-04-19-option1/model-roster.csv`
- `results/release/2026-04-19-option1/supplementary-model-progress.csv`
- `results/release/2026-04-19-option1/family-size-progress.csv`
- `results/release/2026-04-19-option1/future-model-plan.csv`
- `results/release/2026-04-19-option1/benchmark-summary.csv`
- `results/release/2026-04-19-option1/faithful-metrics.csv`
- `results/release/2026-04-19-option1/coverage-matrix.csv`
- `results/release/2026-04-19-option1/release-manifest.json`

Figures:

- `figures/release/option1_coverage_matrix.svg`
- `figures/release/option1_accuracy_heatmap.svg`
- `figures/release/option1_benchmark_accuracy_bars.svg`
- `figures/release/option1_sample_volume.svg`

## Refresh the Tracked Authoritative Snapshot

Maintainers who still have the raw April 2026 full-run folders can refresh the tracked source snapshot with:

```bash
make refresh-authoritative
make release
```

This step depends on local raw files under `results/inspect/full-runs/` and is therefore not required for ordinary public reproduction.

## Run a Minimal Harness Smoke Test

```bash
make smoke
```

This command runs:

- benchmark: `UniMoral`
- task: `unimoral_action_prediction`
- temperature: `0`
- sample limit: `2`

### Expected Output Location

- raw inspect logs: `results/inspect/logs/smoke/`

## Run a Specific Benchmark Task

Example:

```bash
uv run --package cei-inspect python src/inspect/run.py \
  --tasks src/inspect/evals/moral_psych.py::value_prism_relevance \
  --model openrouter/qwen/qwen3-8b \
  --temperature 0 \
  --limit 10 \
  --no_sandbox
```

The `src/inspect/evals/moral_psych.py` registry is the convenience entrypoint for the moral-psych suite when you want one file that exposes tasks spanning multiple benchmark modules.

## Notes on Scope

The current public release is a closed `Option 1` slice, not the full intended family-by-size matrix.

Two points are especially important for correct interpretation:

- `Denevil` is currently a `FULCRA`-backed proxy line rather than a benchmark-faithful `MoralPrompt` reproduction.
- `Llama` small is complete locally across all five benchmark papers, but it is tracked as supplementary local evidence rather than folded into the closed `Option 1` counts.
- `MiniMax` small has a formal local attempt on disk, but the current run failed and should not yet be treated as a completed comparison point.
