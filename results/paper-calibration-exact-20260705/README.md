# Exact Same-Model Calibration Run Summary

This directory keeps the compact public evidence from the July 2026 exact same-model CCD-Bench calibration pass.

- `run-manifest.csv` records the planned exact OpenRouter model routes and paper anchors.
- `calibration-summary.csv` records smoke/full status, valid-choice counts, dominant cluster share, effective cluster count, and token/cost accounting.
- `run-metadata.json` records task metadata and selected routes.

Raw Inspect `.eval` logs and launcher scratch files are intentionally not committed.
They may contain local filesystem paths and raw model responses; the release builder uses the summarized rows above for public documentation.
