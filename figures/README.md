# Figures

The publication-facing figures for the closed `2026-04-19 Option 1` release are generated into `figures/release/`.

- public entrypoints: `make bootstrap` or `make release`
- direct generators: `uv run python scripts/build_release_artifacts.py` and `python scripts/build_unimoral_artifacts.py`
- input snapshot: `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- outputs:

## Audience-Facing Result Figures

Open these first for a meeting, deck, or reviewer skim. They are the figures that support the main result story.

| Order | Open | Use it for | Read it as |
| ---: | --- | --- | --- |
| 1 | [UniMoral family-size scaling](release/option1_unimoral_family_scaling.svg) | Task-specific UniMoral S/M/L movement across RQ1-RQ4. | Task-by-task scaling, not one overall moral score. |
| 2 | [UniMoral task heatmap](release/option1_unimoral_task_heatmap.svg) | UniMoral RQ1-RQ3 exact-match accuracy across model lines. | Classification accuracy only; RQ4 is separate. |
| 3 | [UniMoral RQ4 generation quality](release/option1_unimoral_generation_quality.svg) | UniMoral RQ4 generation quality with BERTScore F1 and METEOR. | Higher-better generation overlap, not accuracy. |
| 4 | [Comparable accuracy bars](release/option1_benchmark_accuracy_bars.svg) | Benchmark-faithful SMID and Value accuracy after the separate UniMoral block. | Main comparable accuracy view after UniMoral. |
| 5 | [Comparable score spread](release/option1_benchmark_difficulty_profile.svg) | Comparable score spread and the SMID visual-moral bottleneck. | Bottleneck/spread view, not a new metric. |
| 6 | [Family scaling profile](release/option1_family_scaling_profile.svg) | Size effects on SMID and Value without mixing CCD or DeNEVIL. | Size trends only where metrics are comparable. |
| 7 | [CCD choice distribution](release/option1_ccd_choice_distribution.svg) | CCD-Bench cultural-cluster choice behavior. | Cultural-choice behavior, not accuracy. |
| 8 | [DeNEVIL behavior outcomes](release/option1_denevil_behavior_outcomes.svg) | DeNEVIL proxy behavior outcomes from saved traces. | Proxy behavior evidence, not MoralPrompt scoring. |
| 9 | [Paper-result comparison](release/option1_paper_result_comparison.svg) | Paper metric anchors beside current release rows with metric boundaries visible. | Evidence map with metric caveats. |
| 10 | [Same-model CCD calibration bars](release/option1_paper_result_alignment_map.svg) | Paper/source Nordic-share bars beside the 11 exact current CCD-Bench reruns or verified rows. | Same-model behavior comparison, not accuracy. |

## Figure Bundles

Use these smaller bundles when you do not need the full figure set. Each bundle keeps metric types separate so a deck or reviewer skim does not accidentally mix accuracy, generation quality, choice behavior, proxy evidence, and calibration status.

| Use case | Open these figures | Boundary |
| --- | --- | --- |
| 3-slide executive read | [UniMoral family-size scaling](release/option1_unimoral_family_scaling.svg), [Comparable accuracy bars](release/option1_benchmark_accuracy_bars.svg), [CCD choice distribution](release/option1_ccd_choice_distribution.svg) | Text reasoning, SMID/Value accuracy, and CCD behavior are three different result layers. |
| UniMoral deep dive | [family-size scaling](release/option1_unimoral_family_scaling.svg), [task heatmap](release/option1_unimoral_task_heatmap.svg), [RQ4 generation quality](release/option1_unimoral_generation_quality.svg) | RQ1-RQ3 are exact-match accuracy; RQ4 uses BERTScore F1 and METEOR. |
| Calibration / replication review | [paper-result comparison](release/option1_paper_result_comparison.svg), [same-model CCD bars](release/option1_paper_result_alignment_map.svg), [same-model bridge](release/option1_paper_model_calibration_bridge.svg) | The bar chart plots only the 11 exact CCD same-model rows; current-only, blocked, metric-mismatched, and proxy evidence stay in tables. |
| Appendix audit | [coverage matrix](release/option1_coverage_matrix.svg), [sample volume](release/option1_sample_volume.svg), [CCD valid-choice coverage](release/option1_ccd_valid_choice_coverage.svg), [DeNEVIL proxy status matrix](release/option1_denevil_proxy_status_matrix.svg) | These explain what ran and parsed; they are not the headline result figures. |
| OpenRouter follow-up | [selected-grid family scaling](../results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg), [selected-grid time scaling](../results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg), [selected-grid benchmark matrix](../results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg) | Separate text-only follow-up; excludes SMID, DeNEVIL, and MiniMax. |

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

- `option1_paper_result_alignment_map.svg`: same-model calibration bar chart for the 11 exact CCD-Bench paper-model rows with a shared Nordic-share metric
- `option1_paper_model_calibration_bridge.svg`: strict same-model paper calibration bridge; exact model rows only, with near-family, blocked, proxy, and route-probe rows left in the ledger table
- `option1_paper_result_comparison.svg`: RQ-level paper-result comparison figure, with UniMoral RQ4 split into BERTScore F1 and METEOR rows

## OpenRouter selected-grid follow-up figures

These figures are separate from the frozen `2026-04-19 Option 1` ranking surface. They summarize the text-only OpenRouter follow-up across UniMoral RQ1-RQ4, ValuePrism relevance/valence, and CCD-Bench. SMID, DeNEVIL, and MiniMax are excluded.

- `../results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg`: main follow-up view for Qwen, Gemma, and Llama S/M/L movement on completed text-classification rows
- `../results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg`: older-vs-newer OpenRouter route view for Qwen, DeepSeek, and available Gemma rows
- `../results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg`: model x benchmark matrix; read CCD-Bench as valid-choice behavior, not correctness
- `../results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg`: detailed task matrix for audit/provenance rather than the first presentation visual
- `../results/openrouter-selected-grid-moral-psych-full/figures/cost_estimate.svg`: planning/accounting appendix only

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
