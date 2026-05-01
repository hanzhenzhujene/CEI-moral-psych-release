# Figures

The publication-facing figures for the closed `2026-04-19 Option 1` release are generated into `figures/release/`.

- public entrypoints: `make bootstrap` or `make release`
- direct generator: `uv run python scripts/build_release_artifacts.py`
- input snapshot: `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- outputs:

## Headline comparison figures

- `option1_family_size_progress_overview.svg`: line-level completion overview across the published family-size matrix
- `option1_benchmark_accuracy_bars.svg`: benchmark-faithful comparable-accuracy comparison for `UniMoral`, `SMID`, and `Value Kaleidoscope`
- `option1_benchmark_difficulty_profile.svg`: benchmark-level mean / range summary for the comparable slice
- `option1_family_scaling_profile.svg`: family-size comparison for the comparable accuracy layer only
- `option1_accuracy_heatmap.svg`: compact heatmap of the currently comparable benchmark results
- `option1_coverage_matrix.svg`: release-level coverage map showing paper-setup, proxy-only, and unavailable cells
- `option1_sample_volume.svg`: where the evaluated sample volume is concentrated

## CCD-Bench figures

- `option1_ccd_choice_distribution.svg`: main CCD result, showing deviation from the 10% uniform baseline across the ten canonical cultural clusters
- `option1_ccd_dominant_option_share.svg`: compact CCD summary showing dominant-cluster concentration and effective cluster breadth
- `option1_ccd_valid_choice_coverage.svg`: appendix QA only, showing parseable visible `1-10` choice coverage

## DeNEVIL figures

- `option1_denevil_behavior_outcomes.svg`: main DeNEVIL proxy result, showing visible behavioral outcomes from released traces
- `option1_denevil_prompt_family_heatmap.svg`: secondary DeNEVIL view showing protective-response rates by heuristic prompt family
- `option1_denevil_proxy_status_matrix.svg`: appendix QA / provenance table for route, timestamps, sample counts, and limitations
- `option1_denevil_proxy_sample_volume.svg`: appendix QA sample-volume chart
- `option1_denevil_proxy_valid_response_rate.svg`: appendix QA visible-response coverage chart
- `option1_denevil_proxy_pipeline.svg`: one-slide diagram of the public proxy pipeline and its limitations

The figure set is intentionally split between:

- headline research figures that support the repo's claims, and
- appendix QA / provenance figures that explain what ran without pretending those support the same performance claims.

That split is especially important for `CCD-Bench` and `DeNEVIL`: headline figures show model behavior, while coverage, parsing, route, and trace-surfacing diagnostics stay in appendix-only visuals.
