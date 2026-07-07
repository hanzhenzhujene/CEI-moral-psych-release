# Results Layout

## Open First

| Need | Open | Boundary |
| --- | --- | --- |
| Primary result tables | [`unimoral-full-benchmark.csv`](release/2026-04-19-option1/unimoral-full-benchmark.csv), [`smid-results.csv`](release/2026-04-19-option1/smid-results.csv), [`value-kaleidoscope-results.csv`](release/2026-04-19-option1/value-kaleidoscope-results.csv) | Main comparable accuracy entry points; UniMoral RQ4 has separate BERTScore F1 and METEOR rows. |
| Behavioral/proxy result tables | [`ccd-choice-distribution.csv`](release/2026-04-19-option1/ccd-choice-distribution.csv), [`denevil-behavior-summary.csv`](release/2026-04-19-option1/denevil-behavior-summary.csv) | CCD-Bench is cultural-choice behavior; DeNEVIL is proxy behavior. |
| Visual reading path | [`../README.md#visual-read-in-90-seconds`](../README.md#visual-read-in-90-seconds), then [`../figures/README.md`](../figures/README.md) | Start with the five-figure talk track; the figure index separates audience-facing figures from secondary QA/provenance figures. |
| Readiness and progress | [`readiness-tier-matrix.csv`](release/2026-04-19-option1/readiness-tier-matrix.csv), [`family-size-progress.csv`](release/2026-04-19-option1/family-size-progress.csv) | Tier is result readiness, not model quality. |
| Paper calibration / replication | [`paper-result-alignment.csv`](release/2026-04-19-option1/paper-result-alignment.csv), [`paper-model-calibration-ledger.csv`](release/2026-04-19-option1/paper-model-calibration-ledger.csv), [`paper-model-calibration-bridge.csv`](release/2026-04-19-option1/paper-model-calibration-bridge.csv) | Same-model rows, blocked routes, current-only rows, and proxy-only evidence stay separate. |
| OpenRouter selected-grid follow-up | [`openrouter-selected-grid-moral-psych-full/README.md`](openrouter-selected-grid-moral-psych-full/README.md), [`result_summary.csv`](openrouter-selected-grid-moral-psych-full/result_summary.csv), [`targeted-retry-log.md`](openrouter-selected-grid-moral-psych-full/targeted-retry-log.md) | Separate text-only follow-up; not folded into the frozen Option 1 ranking surface. |

## Tracked Release Artifacts

Curated, publication-facing artifacts live under:

- `results/release/`

These files are small, stable, and intended for version control.
The tracked `source/authoritative-summary.csv` snapshot inside the release directory is the public regeneration anchor for `make release`.
The tracked `release-manifest.json` file provides a machine-readable index for downstream tooling or dashboards.

The most useful public entry points are:

- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/README.md`
- `results/release/2026-04-19-option1/unimoral-full-benchmark.csv`
- `results/release/2026-04-19-option1/smid-results.csv`
- `results/release/2026-04-19-option1/value-kaleidoscope-results.csv`
- `results/release/2026-04-19-option1/ccd-choice-distribution.csv`
- `results/release/2026-04-19-option1/denevil-behavior-summary.csv`
- `results/release/2026-04-19-option1/readiness-tier-matrix.csv`
- `results/release/2026-04-19-option1/family-size-progress.csv`

## Exploratory Follow-Up Sweeps

Exploratory follow-up model-sweep readouts live under:

- `results/exploratory/2026-05-13-additional-model-sweep/`

The May 13 additional-model sweep is intentionally separate from the main
release matrix. It summarizes older or smaller OpenRouter routes on `UniMoral`
and `CCD-Bench`, with final UniMoral accuracy and CCD cultural-cluster
concentration tables.

## OpenRouter Selected-Grid Follow-Up

The completed text-only selected-grid follow-up lives under:

- `results/openrouter-selected-grid-moral-psych-full/`

Use it for OpenRouter-accessible text routes across `UniMoral RQ1-RQ4`, `ValuePrism`, and `CCD-Bench`.
It is separate from the frozen Option 1 ranking surface and excludes `SMID`, `DeNEVIL`, and `MiniMax`.

Open these first:

- `results/openrouter-selected-grid-moral-psych-full/README.md`
- `results/openrouter-selected-grid-moral-psych-full/interpretation.md`
- `results/openrouter-selected-grid-moral-psych-full/completion_audit.md`
- `results/openrouter-selected-grid-moral-psych-full/targeted-retry-log.md`
- `results/openrouter-selected-grid-moral-psych-full/result_summary.csv`
- `results/openrouter-selected-grid-moral-psych-full/benchmark_summary.csv`
- `results/openrouter-selected-grid-moral-psych-full/model_summary.csv`

Visual entry points:

- `results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg`
- `results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg`
- `results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg`
- `results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg`

## Public Result Layers

The current release separates three layers on purpose:

- **Comparable accuracy:** `unimoral-full-benchmark.csv`, `smid-results.csv`, and `value-kaleidoscope-results.csv`; `benchmark-comparison.csv` is a supporting generated summary for figures, not the main data entry point
- **Behavioral / distributional evidence:** `ccd-choice-distribution.csv` for CCD-Bench and `denevil-behavior-summary.csv` plus `denevil-prompt-family-breakdown.csv` for DeNEVIL
- **Secondary QA / provenance:** `denevil-proxy-summary.csv`, `denevil-proxy-examples.csv`, and the QA-only coverage / status figures
- **Result-readiness summary dashboard:** `readiness-tier-matrix.csv`, which summarizes model-line x benchmark readiness while keeping the metric layer explicit. Tier 1 = harness completed, Tier 2 = valid result, Tier 3 = interpretable/comparable result; blocked or missing cells are not assigned a tier.
- **OpenRouter text-only follow-up:** `results/openrouter-selected-grid-moral-psych-full/result_summary.csv`, `benchmark_summary.csv`, and `model_summary.csv` summarize the separate selected-grid follow-up; `within_family_scaling.svg`, `time_scaling.svg`, `benchmark_score_matrix.svg`, and `pilot_scores.svg` are the visual entry points; `completion_audit.md` and `targeted-retry-log.md` document provider/credit blockers; CCD-Bench is valid-choice behavior, not accuracy.

This split keeps the public package honest: coverage, parser health, route provenance, and timestamps remain inspectable, but they are not promoted into headline performance claims.

## Legacy Baseline Outputs

Older ETHICS baseline outputs live under:

- `results/lm-harness/`

These files document the legacy `lm-evaluation-harness` path retained in the
repo for comparison and regression purposes.

## Local Raw Outputs

Large local artifacts are intentionally treated as ephemeral:

- `results/inspect/logs/`
- `results/inspect/full-runs/`
- `results/inspect/smoke-batch/`

Those directories are useful for local monitoring and debugging, but they are not the primary public deliverable for this repo.
