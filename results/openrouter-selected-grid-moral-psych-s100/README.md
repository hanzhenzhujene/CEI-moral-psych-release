# OpenRouter Selected-Grid Moral-Psych Pipeline

OpenRouter pricing metadata fetched: `2026-05-27T16:57:24.556641+00:00` from `https://openrouter.ai/api/v1/models`.

Scope:
- Included benchmarks: UniMoral, ValuePrism / Value Kaleidoscope, CCD-Bench.
- Excluded benchmarks: SMID and DeNEVIL.
- Excluded provider/model family: MiniMax.
- Price cap: input <= $3.00/1M tokens and output <= $15.00/1M tokens, unless an existing baseline row is explicitly marked.
- CCD-Bench is reported as choice behavior / valid-choice coverage, not accuracy.
- ValuePrism rows are prompt-based classification, not Kaleido model replication.
- Qwen/DeepSeek live runs use a `/no_think` prompt prefix plus `reasoning.effort=none` by default for cost control; set `--reasoning-prompt-prefix ''` or override `--extra-body-json` to change this.
- Live run cost summaries count reasoning tokens conservatively as completion tokens when Inspect reports them.

Sample limit for this plan: `100` per task.
Eligible model count: `17`. Skipped model count: `0`.
Estimated total run cost for this plan: `$1.2000`.

Primary outputs:
- `benchmark_map.csv`: papers/repos/prompts/scorers and replication status.
- `model_grid.csv`: selected OpenRouter model grid and cap decision.
- `run_plan.csv`: model x task cost estimates and planned metadata.
- `result_summary.csv`: created after live runs.
- `completion_audit.md`: requirement-by-requirement status for this output folder.
- `openrouter-pricing-metadata.json`: compact pricing-source metadata for the selected model grid.
- `figures/cost_estimate.svg`: planned cost by model.
- `figures/pilot_scores.svg`: pilot scores after live runs.
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

Successful task logs: `119` / `119`.
Completed models: `17`. Completed tasks: `7`.
Conservative observed API cost estimate from Inspect logs: `$0.399078`.
Observed reasoning tokens: `21552`.
Models with reasoning tokens despite controls: `deepseek/deepseek-v4-flash, qwen/qwen3-32b`.

Interpretation helpers:
- `benchmark_summary.csv`: model x benchmark aggregate scores.
- `model_summary.csv`: model-level pilot aggregates and cost.
- `interpretation.md`: scaling/time/disagreement notes for completed pilot rows.
