# Figures

The publication-facing figures for the closed `2026-04-19 Option 1` release are generated into `figures/release/`.

- public entrypoints: `make bootstrap` or `make release`
- direct generator: `uv run python scripts/build_release_artifacts.py`
- input snapshot: `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- outputs:
  - `option1_family_size_progress_overview.svg`
  - `option1_benchmark_difficulty_profile.svg`
  - `option1_family_scaling_profile.svg`
  - `option1_coverage_matrix.svg`
  - `option1_accuracy_heatmap.svg`
  - `option1_benchmark_accuracy_bars.svg`
  - `option1_sample_volume.svg`

These SVGs are designed to be README-ready and paper-slide friendly without requiring notebook-only plotting code.
