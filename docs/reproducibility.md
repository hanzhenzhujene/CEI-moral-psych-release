# Reproducibility Guide

This document describes both:

1. how to recreate the **public release artifacts**, and
2. how to run a small **benchmark smoke test** with the harness.

## Public QA First

For a clean-checkout verification of the public QA deliverable, run:

```bash
make bootstrap
```

This is the shortest trustworthy public-QA path for reviewers and collaborators. It:

- installs the pinned environment from `uv.lock`
- runs the full test suite
- rebuilds the tracked release package from the committed authoritative snapshot

It does **not** require API keys or local benchmark datasets.
It is not the strict UniMoral completion gate; use `make verify-unimoral` for that.

## Environment

The canonical environment is the checked-in `uv.lock` file.

### Setup

```bash
make setup
```

If `uv` is installed outside your shell `PATH`, use `make UV=/absolute/path/to/uv <target>`.
If `uv` is not on `PATH` but the checked-in `.venv` already exists, runner-backed targets including `make test`, `make release`, `make refresh-authoritative`, `make smoke`, `make audit`, `make bootstrap`, and `make unimoral-missing-plan` will fall back to `.venv/bin/python` automatically. `make setup` still requires `uv`. If the fallback interpreter lives somewhere else, pass `VENV_PYTHON=/absolute/path/to/python`. If neither runner is available, the Makefile now stops immediately with a clear setup error instead of a raw shell failure.

If you want to run a live benchmark task rather than just regenerate the public release, create `.env`:

```bash
cp .env.example .env
```

Fill in only the values you need, such as:

- model API keys such as `OPENROUTER_API_KEY`
- local dataset paths such as `UNIMORAL_DATA_DIR` and `SMID_DATA_DIR`

For benchmark-by-benchmark data expectations, see [`data-access.md`](data-access.md).
For plain-language report terms such as `proxy`, `live`, and `frozen snapshot`, see [`how-to-read-results.md`](how-to-read-results.md).
For the comparison rules that separate accuracy metrics from coverage or proxy-only signals, see [`evaluation-methodology.md`](evaluation-methodology.md).

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

This is the fastest end-to-end public QA check because it runs the full test suite and refreshes the tracked release artifacts in one command. It allows documented incomplete UniMoral cells; strict UniMoral completion is checked separately with `make verify-unimoral`.

## Rebuild the Public Release

```bash
make release
```

This target regenerates the public release package from the tracked authoritative snapshot committed under `results/release/2026-04-19-option1/source/`.
In environments like this desktop workspace, that command now works even when `uv` itself is not on `PATH`, as long as `.venv/bin/python` is present.

### Expected Outputs

Release tables:

- `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/topline-summary.md`
- `results/release/2026-04-19-option1/benchmark-catalog.csv`
- `results/release/2026-04-19-option1/benchmark-comparison.csv`
- `results/release/2026-04-19-option1/ccd-choice-distribution.csv`
- `results/release/2026-04-19-option1/denevil-behavior-summary.csv`
- `results/release/2026-04-19-option1/denevil-prompt-family-breakdown.csv`
- `results/release/2026-04-19-option1/denevil-proxy-summary.csv`
- `results/release/2026-04-19-option1/denevil-proxy-examples.csv`
- `results/release/2026-04-19-option1/model-summary.csv`
- `results/release/2026-04-19-option1/model-roster.csv`
- `results/release/2026-04-19-option1/supplementary-model-progress.csv`
- `results/release/2026-04-19-option1/family-size-progress.csv`
- `results/release/2026-04-19-option1/readiness-tier-matrix.csv`
- `results/release/2026-04-19-option1/benchmark-difficulty-summary.csv`
- `results/release/2026-04-19-option1/family-scaling-summary.csv`
- `results/release/2026-04-19-option1/future-model-plan.csv`
- `results/release/2026-04-19-option1/benchmark-summary.csv`
- `results/release/2026-04-19-option1/faithful-metrics.csv`
- `results/release/2026-04-19-option1/coverage-matrix.csv`
- `results/release/2026-04-19-option1/release-manifest.json`

Figures:

- `figures/release/option1_unimoral_four_task_dashboard.svg`
- `figures/release/option1_unimoral_task_heatmap.svg`
- `figures/release/option1_unimoral_task_spread.svg`
- `figures/release/option1_unimoral_task_rankings.svg`
- `figures/release/option1_family_size_progress_overview.svg`
- `figures/release/option1_benchmark_accuracy_bars.svg`
- `figures/release/option1_benchmark_difficulty_profile.svg`
- `figures/release/option1_family_scaling_profile.svg`
- `figures/release/option1_ccd_choice_distribution.svg`
- `figures/release/option1_ccd_dominant_option_share.svg`
- `figures/release/option1_ccd_valid_choice_coverage.svg`
- `figures/release/option1_denevil_behavior_outcomes.svg`
- `figures/release/option1_denevil_prompt_family_heatmap.svg`
- `figures/release/option1_denevil_proxy_status_matrix.svg`
- `figures/release/option1_denevil_proxy_sample_volume.svg`
- `figures/release/option1_denevil_proxy_valid_response_rate.svg`
- `figures/release/option1_denevil_proxy_pipeline.svg`
- `figures/release/option1_coverage_matrix.svg`
- `figures/release/option1_accuracy_heatmap.svg`
- `figures/release/option1_sample_volume.svg`

Headline interpretation artifacts now include:

- `unimoral-full-benchmark.csv` + `option1_unimoral_four_task_dashboard.svg` for the UniMoral RQ1-RQ4 task surfaces
- `ccd-choice-distribution.csv` + `option1_ccd_choice_distribution.svg` for CCD-Bench cultural-cluster behavior
- `denevil-behavior-summary.csv` + `option1_denevil_behavior_outcomes.svg` for DeNEVIL proxy behavioral outcomes
- `readiness-tier-matrix.csv` for the generated model-line x benchmark result-readiness summary dashboard
- appendix QA artifacts such as `denevil-proxy-summary.csv` and `option1_denevil_proxy_status_matrix.svg` for provenance, route, and visible-response diagnostics

## Refresh the Tracked Authoritative Snapshot

Maintainers who still have the raw April 2026 full-run folders can refresh the tracked source snapshot with:

```bash
make refresh-authoritative
make release
```

This step depends on local raw files under `results/inspect/full-runs/` and is therefore not required for ordinary public reproduction.

## Run a Minimal Harness Smoke Test

```bash
make setup
cp .env.example .env
make smoke
```

This command runs:

- benchmark: `UniMoral`
- task: `unimoral_action_prediction`
- temperature: `0`
- sample limit: `2`

The smoke target intentionally stays on the small RQ1/action-prediction task.
For provider-free coverage of the full UniMoral registry, run
`make verify-unimoral-task-builders`; it instantiates RQ1/RQ2/RQ3/RQ4 through
`src/inspect/evals/moral_psych.py` using a tiny temporary fixture. For release
artifacts, `make verify-unimoral-artifacts` checks the generated RQ1-RQ4 tables,
sample predictions, BERTScore export, figures, manifest entries, documented
failure checklist, and the completion audit's CSV-level strict blocker inventory.
For provider-free planning of the remaining UniMoral MiniMax cells, run
`make unimoral-missing-plan`; it wraps the missing-task launcher with
`UNIMORAL_DRY_RUN=1` and prints planned ranges without granting MiniMax execution
permission.

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
The UniMoral entries exposed there are:

- `unimoral_action_prediction`
- `unimoral_moral_typology`
- `unimoral_factor_attribution`
- `unimoral_consequence_generation`

## Notes on Scope

The current public release is a closed `Option 1` slice, not the full intended family-by-size matrix.

Two points are especially important for correct interpretation:

- `Denevil` is currently a proxy line rather than the paper's original `MoralPrompt` setup.
- `Llama` small is complete locally across all five benchmark papers, but it is tracked as an extra local result rather than folded into the closed `Option 1` counts.
- A formal local attempt on disk is not enough to treat a cell as complete; use the generated release status tables and task-specific failure checklists.
