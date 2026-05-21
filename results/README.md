# Results Layout

## Tracked Release Artifacts

Curated, publication-facing artifacts live under:

- `results/release/`

These files are small, stable, and intended for version control.
The tracked `source/authoritative-summary.csv` snapshot inside the release directory is the public regeneration anchor for `make release`.
The tracked `release-manifest.json` file provides a machine-readable index for downstream tooling or dashboards.

The most useful public entry points are:

- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/README.md`
- `results/release/2026-04-19-option1/family-size-progress.csv`
- `results/release/2026-04-19-option1/readiness-tier-matrix.csv`
- `results/release/2026-04-19-option1/benchmark-comparison.csv`
- `results/release/2026-04-19-option1/ccd-choice-distribution.csv`
- `results/release/2026-04-19-option1/denevil-behavior-summary.csv`

## Exploratory Follow-Up Sweeps

Exploratory follow-up model-sweep readouts live under:

- `results/exploratory/2026-05-13-additional-model-sweep/`

The May 13 additional-model sweep is intentionally separate from the main
release matrix. It summarizes older or smaller OpenRouter routes on `UniMoral`
and `CCD-Bench`, with final UniMoral accuracy and CCD cultural-cluster
concentration tables.

## Public Result Layers

The current release separates three layers on purpose:

- **Comparable accuracy:** `benchmark-comparison.csv` plus the main bar/heatmap/scaling figures for `UniMoral`, `SMID`, and `Value Kaleidoscope`
- **Behavioral / distributional evidence:** `ccd-choice-distribution.csv` for CCD-Bench and `denevil-behavior-summary.csv` plus `denevil-prompt-family-breakdown.csv` for DeNEVIL
- **Appendix QA / provenance:** `denevil-proxy-summary.csv`, `denevil-proxy-examples.csv`, and the QA-only coverage / status figures
- **Result-readiness summary dashboard:** `readiness-tier-matrix.csv`, which summarizes model-line x benchmark readiness while keeping the metric layer explicit. Tier 1 = harness completed, Tier 2 = valid result, Tier 3 = interpretable/comparable result; blocked or missing cells are not assigned a tier.

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
