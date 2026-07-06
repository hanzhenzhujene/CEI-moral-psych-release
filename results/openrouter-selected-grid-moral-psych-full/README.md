# OpenRouter Selected-Grid Moral-Psych Pipeline

OpenRouter pricing metadata fetched: `2026-05-28T00:37:09.154648+00:00` from `https://openrouter.ai/api/v1/models`.

Scope:
- Included benchmarks: UniMoral, ValuePrism / Value Kaleidoscope, CCD-Bench.
- Excluded benchmarks: SMID and DeNEVIL.
- Excluded provider/model family: MiniMax.
- Price cap: input <= $3.00/1M tokens and output <= $15.00/1M tokens, unless an existing baseline row is explicitly marked.
- CCD-Bench is reported as choice behavior / valid-choice coverage, not accuracy.
- ValuePrism rows are prompt-based classification, not Kaleido model replication.
- Qwen/DeepSeek live runs use a `/no_think` prompt prefix plus `reasoning.effort=none` by default for cost control; set `--reasoning-prompt-prefix ''` or override `--extra-body-json` to change this.
- Live run cost summaries count reasoning tokens conservatively as completion tokens when Inspect reports them.

Sample limit for this plan: `full dataset` per task.
Eligible model count: `17`. Skipped model count: `0`.
Estimated total run cost for this plan: `$51.6126`.

Primary outputs:
- `benchmark_map.csv`: papers/repos/prompts/scorers and replication status.
- `model_grid.csv`: selected OpenRouter model grid and cap decision.
- `run_plan.csv`: model x task cost estimates and planned metadata.
- `result_summary.csv`: created after live runs.
- `completion_audit.md`: requirement-by-requirement status for this output folder.
- `openrouter-pricing-metadata.json`: compact pricing-source metadata for the selected model grid.
- `figures/within_family_scaling.svg`: S/M/L scaling view for Qwen, Gemma, and Llama.
- `figures/time_scaling.svg`: older-vs-newer route view for Qwen, DeepSeek, and available Gemma rows.
- `figures/benchmark_score_matrix.svg`: model x benchmark matrix with metric caveats visible.
- `figures/pilot_scores.svg`: detailed task matrix after live runs.
- `figures/cost_estimate.svg`: planning/accounting appendix by model.
- Raw Inspect `.eval` logs under `logs/` are local-only by default and intentionally ignored; commit them only with an explicit artifact contract.

## Allowed Benchmarks

| Benchmark | Task count | Paper / status |
| :--- | ---: | :--- |
| UniMoral | 4 | Kumar et al. (ACL Findings 2025); Benchmark-faithful task; paper model roster only partially available in current grid. |
| ValuePrism | 2 | Sorensen et al. (AAAI 2024); Closest feasible prompt-classification route; not Kaleido model replication. |
| CCD-Bench | 1 | Rahman and Salam (arXiv 2025); Benchmark-faithful route for choice behavior; compare cluster shares, not correctness. |

## Selected Models

| Model | Family | Size/tier | Release period | Grid | Price cap |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `qwen/qwen3-8b` | Qwen | S/8B | 2025-Q2 | within-family scaling | eligible |
| `qwen/qwen3-32b` | Qwen | M/32B | 2025-Q2 | within-family scaling | eligible |
| `qwen/qwen3-235b-a22b-2507` | Qwen | L/MoE 235B-A22B | 2025-Q3 | within-family scaling | eligible |
| `google/gemma-3-4b-it` | Gemma | S/4B | 2025-Q1 | within-family scaling | eligible |
| `google/gemma-3-12b-it` | Gemma | M/12B | 2025-Q1 | within-family scaling | eligible |
| `google/gemma-3-27b-it` | Gemma | L/27B | 2025-Q1 | within-family scaling | eligible |
| `meta-llama/llama-3.2-3b-instruct` | Llama | S/3B | 2024-Q3 | within-family scaling | eligible |
| `meta-llama/llama-3.1-8b-instruct` | Llama | M/8B | 2024-Q3 | within-family scaling | eligible |
| `meta-llama/llama-3.3-70b-instruct` | Llama | L/70B | 2024-Q4 | within-family scaling | eligible |
| `qwen/qwen-2.5-7b-instruct` | Qwen | S/7B | 2024-Q4 | time scaling | eligible |
| `qwen/qwen3.5-9b` | Qwen | S/9B | 2026-Q1 | time scaling | eligible |
| `google/gemma-2-27b-it` | Gemma | L/27B | 2024-Q3 | time scaling | eligible |
| `google/gemma-4-31b-it` | Gemma | L/31B | 2026-Q1 | time scaling | eligible |
| `deepseek/deepseek-chat-v3-0324` | DeepSeek | chat/V3 | 2025-Q1 | time scaling | eligible |
| `deepseek/deepseek-chat-v3.1` | DeepSeek | chat/V3.1 | 2025-Q3 | time scaling | eligible |
| `deepseek/deepseek-v3.2` | DeepSeek | chat/V3.2 | 2025-Q4 | time scaling | eligible |
| `deepseek/deepseek-v4-flash` | DeepSeek | flash/V4 | 2026-Q2 | time scaling | eligible |

## Live Run Snapshot

Recorded terminal states: `119` / `119` planned model-task rows.
Successful scored rows: `102`. Provider/error rows: `13`. Cancelled/stale-route rows: `4`.
Attempted models: `17`. Models with at least one scored row: `16`. Completed tasks represented: `7`.
Success-row API cost estimate from Inspect logs: `$16.393879`.
All recorded provider cost estimate, including blocked partial rows: `$18.166308`.
Observed reasoning tokens: `1284967`.
Models with reasoning tokens despite controls: `deepseek/deepseek-v4-flash, google/gemma-4-31b-it, qwen/qwen3-32b`.
Non-success rows are documented as provider/filter/stale-route limits and excluded from scored summaries.

Interpretation helpers:
- `benchmark_summary.csv`: model x benchmark aggregate scores.
- `model_summary.csv`: model-level aggregates and success-row cost.
- `interpretation.md`: scaling/time/disagreement notes for completed scored rows.
- `figures/within_family_scaling.svg`: direct S/M/L family-size visual.
- `figures/time_scaling.svg`: older-vs-newer route visual.
- `figures/benchmark_score_matrix.svg`: benchmark comparison matrix; CCD is labeled as valid-choice coverage.

## Figures To Open First

Use these as the visual path through the follow-up. They are text-only follow-up figures, not replacements for the frozen release figures.

![Within-family scaling](figures/within_family_scaling.svg)

_First: S/M/L movement for Qwen, Gemma, and Llama on completed text-classification rows._

![Time scaling](figures/time_scaling.svg)

_Second: older-vs-newer OpenRouter routes for Qwen, DeepSeek, and available Gemma rows._

![Benchmark comparison matrix](figures/benchmark_score_matrix.svg)

_Third: model x benchmark comparison; CCD-Bench is valid-choice behavior, not correctness or accuracy._
