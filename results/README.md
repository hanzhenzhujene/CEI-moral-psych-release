# Results Layout

## Tracked Release Artifacts

Curated, publication-facing artifacts live under:

- `results/release/`

These files are small, stable, and intended for version control.
The tracked `source/authoritative-summary.csv` snapshot inside the release directory is the public regeneration anchor for `make release`.
The tracked `release-manifest.json` file provides a machine-readable index for downstream tooling or dashboards.

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
- `results/cache/`

Those directories are useful for local monitoring and debugging, but they are not the primary public deliverable for this repo.
