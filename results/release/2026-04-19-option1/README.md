# Option 1 Release Artifacts

This directory contains the tracked, publication-facing outputs for the closed `2026-04-19 Option 1` release.

## Files

- `source/authoritative-summary.csv`: tracked source snapshot used to regenerate this release package
- `source/README.md`: provenance note for the tracked source snapshot
- `topline-summary.md`: concise release narrative and topline counts
- `topline-summary.json`: machine-readable counterpart of the topline narrative
- `release-manifest.json`: machine-readable index of release files, counts, and interpretation guardrails
- `model-summary.csv`: per-model task counts, sample counts, and macro accuracy
- `benchmark-summary.csv`: per-benchmark coverage and sample volume
- `faithful-metrics.csv`: task-level metrics for benchmark-faithful tasks
- `coverage-matrix.csv`: matrix used to render the release coverage figure

## Model Summary

| Model family | Faithful tasks | Proxy tasks | Samples | Faithful macro accuracy |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

## Benchmark Summary

| Benchmark | Tasks | Models covered | Samples | Modes |
| --- | ---: | ---: | ---: | --- |
| `UniMoral` | 3 | 3 | 26,352 | benchmark_faithful |
| `SMID` | 4 | 2 | 11,764 | benchmark_faithful |
| `Value Kaleidoscope` | 6 | 3 | 196,560 | benchmark_faithful |
| `CCD-Bench` | 3 | 3 | 6,546 | benchmark_faithful |
| `Denevil` | 3 | 3 | 61,554 | proxy |

## Interpretation Guardrails

- Treat `Denevil` as a proxy line in this release.
- Treat the release outputs here as authoritative for the closed `Option 1` slice.
- Use the raw `results/inspect/` tree only for local debugging or provenance checks.
