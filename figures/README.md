# Figures

The publication-facing figures for the closed `2026-04-19 Option 1` release are generated into `figures/release/`.

- public entrypoints: `make bootstrap` or `make release`
- direct generators: `uv run python scripts/build_release_artifacts.py` and `python scripts/build_unimoral_artifacts.py`
- input snapshot: `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- outputs:

## Audience-Facing Result Figures

Open these first for a meeting, deck, or reviewer skim. They are the figures that support the main result story.

| Order | Figure | Use it for |
| ---: | --- | --- |
| 1 | `option1_unimoral_family_scaling.svg` | Task-specific UniMoral S/M/L movement across RQ1-RQ4. |
| 2 | `option1_unimoral_task_heatmap.svg` | UniMoral RQ1-RQ3 exact-match accuracy across model lines. |
| 3 | `option1_unimoral_generation_quality.svg` | UniMoral RQ4 generation quality with BERTScore F1 and METEOR. |
| 4 | `option1_benchmark_accuracy_bars.svg` | Benchmark-faithful SMID and Value accuracy after the separate UniMoral block. |
| 5 | `option1_benchmark_difficulty_profile.svg` | Comparable score spread and the SMID visual-moral bottleneck. |
| 6 | `option1_family_scaling_profile.svg` | Size effects on SMID and Value without mixing CCD or DeNEVIL. |
| 7 | `option1_ccd_choice_distribution.svg` | CCD-Bench cultural-cluster choice behavior, not accuracy. |
| 8 | `option1_denevil_behavior_outcomes.svg` | DeNEVIL proxy behavior outcomes from saved traces. |
| 9 | `option1_paper_result_comparison.svg` | Paper metric anchors beside current release rows with metric boundaries visible. |
| 10 | `option1_paper_result_alignment_map.svg` | Replication/calibration status: direct, partial, current-only, blocked, and proxy-only evidence. |

## UniMoral figures

- `option1_unimoral_four_task_dashboard.svg`: supporting UniMoral RQ1-RQ4 dashboard, showing coverage and metric boundaries
- `option1_unimoral_task_heatmap.svg`: main all-line view across RQ1-RQ3 using one shared exact-match accuracy metric, with family blocks and S/M/L badges
- `option1_unimoral_generation_quality.svg`: RQ4 consequence-generation quality view, using two reported generation metrics: BERTScore F1 for semantic similarity and METEOR for lexical overlap
- `option1_unimoral_family_scaling.svg`: RQ-by-RQ family-size line charts; read it as task-specific scaling, not as a single UniMoral scalar
- `option1_unimoral_task_spread.svg`: diagnostic exact-match accuracy spread readout for RQ1-RQ3; do not treat tight ranges as proof of benchmark saturation
- `option1_unimoral_task_rankings.svg`: per-task exact-match accuracy rankings for the completed UniMoral classification cells

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

## Replication / calibration figures

- `option1_paper_result_alignment_map.svg`: replication/calibration map showing paper-faithful overlap, current-only comparisons, blocked routes, and proxy-only evidence
- `option1_paper_model_calibration_bridge.svg`: strict same-model paper calibration bridge; exact model rows only, with near-family, blocked, proxy, and route-probe rows left in the ledger table
- `option1_paper_result_comparison.svg`: RQ-level paper-result comparison figure, with UniMoral RQ4 split into BERTScore F1 and METEOR rows

## Appendix QA / Provenance Figures

These are still public and useful, but they answer audit/provenance questions rather than headline performance questions.

- `option1_family_size_progress_overview.svg`: completion/progress QA across family-size rows
- `option1_accuracy_heatmap.svg`: compact availability/comparable-score heatmap for audit context
- `option1_coverage_matrix.svg`: coverage map showing paper-setup, proxy-only, and unavailable cells
- `option1_sample_volume.svg`: sample-volume QA by benchmark layer
- `option1_ccd_valid_choice_coverage.svg`: CCD parser/completion QA, not result ranking
- `option1_denevil_proxy_status_matrix.svg`: DeNEVIL proxy route/status provenance
- `option1_denevil_proxy_sample_volume.svg`: DeNEVIL proxy sample-volume provenance
- `option1_denevil_proxy_valid_response_rate.svg`: DeNEVIL visible-response coverage provenance
- `option1_denevil_proxy_pipeline.svg`: DeNEVIL proxy pipeline and limitation diagram

The figure set is intentionally split between:

- headline research figures that support the repo's claims, and
- appendix QA / provenance figures that explain what ran without pretending those support the same performance claims.

That split is especially important for `CCD-Bench` and `DeNEVIL`: headline figures show model behavior, while coverage, parsing, route, and trace-surfacing diagnostics stay in appendix-only visuals.

## Visual QA

Before pushing publication-facing figure changes, render every release SVG to PNG and inspect both a contact sheet and the key headline figures at full size. The visual pass should confirm:

- no clipped labels, overlapping legend text, or family-group boxes extending past their rows
- figure titles state the interpretation boundary (`accuracy`, `not accuracy`, `proxy`, or `appendix QA`) directly in the image
- the first UniMoral view shows RQ1-RQ3 exact-match accuracy clearly, with readable row labels and values
- UniMoral classification figures use exact-match accuracy only; RQ4 stays in a separate generation-metric chart
- appendix/provenance charts remain readable but do not become the primary evidence for accuracy claims

One local render command used for QA is:

```bash
mkdir -p /tmp/cei-figure-qa/png
for f in figures/release/*.svg; do
  rsvg-convert -w 1400 -o "/tmp/cei-figure-qa/png/$(basename "$f" .svg).png" "$f"
done
```

## Exploratory Figures

Follow-up model-sweep figures use `figures/exploratory/`.

- `additional_model_sweep_unimoral_accuracy.svg`: UniMoral accuracy for the May 13 additional-model sweep
- `additional_model_sweep_ccd_dominant_share.svg`: CCD-Bench dominant cultural-cluster concentration for the same sweep
- `additional_model_sweep_scaling.svg`: approximate model-size readout for the sweep, with CCD concentration encoded by point radius
