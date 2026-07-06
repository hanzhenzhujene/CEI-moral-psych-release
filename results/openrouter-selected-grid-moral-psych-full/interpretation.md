# OpenRouter Full Selected-Grid Interpretation

This is the full selected-grid readout for the allowed text-only tasks. Every planned model-task row has a recorded terminal state; provider errors, content-filter blocks, and stale-route cancellations are evidence limits, not scored model results.

## TLDR

- Recorded terminal states for `119` planned model-task rows: `102` success, `13` provider/error, `4` cancelled or stale-route.
- Success-row API cost is `$16.393879`; all recorded provider cost, including blocked partial rows, is `$18.166308`.
- Highest completed text-accuracy means: `meta-llama/llama-3.3-70b-instruct`=0.670, `qwen/qwen3.5-9b`=0.642, `google/gemma-3-12b-it`=0.629, `google/gemma-3-27b-it`=0.621.
- Scaling is mixed rather than cleanly monotonic: Llama shows the clearest large-model lift, while Qwen, Gemma, and DeepSeek vary by task and release line.
- CCD-Bench remains a valid-choice / choice-behavior readout, not an accuracy metric.
- Cost-control caveat: `deepseek/deepseek-v4-flash` emitted `1171189` reasoning tokens despite controls.

## Coverage

- Models with any successful row: `16`.
- Models with any recorded terminal state: `17`.
- Model x benchmark summary rows: `44`.
- Included benchmarks: UniMoral, ValuePrism, CCD-Bench.
- Excluded benchmarks: SMID and DeNEVIL.
- CCD-Bench is choice-format/cluster behavior, not accuracy.
- Conservative success-row cost estimate: `$16.393879` using input + output + reasoning tokens at OpenRouter metadata rates.
- Conservative all-recorded cost estimate: `$18.166308` including blocked partial rows with parsed token usage.
- Observed reasoning tokens: `1284967`.

## Benchmark Guide

- UniMoral action, moral-typology, and factor-attribution rows are accuracy-style text classification tasks.
- UniMoral consequence generation is a live METEOR-style generation score; do not compare its magnitude directly with accuracy rows.
- ValuePrism rows are prompt-based relevance/valence classification, not Kaleido model replication.
- CCD-Bench is valid-choice coverage and choice-format behavior, not correctness or accuracy.

## Cost-Control Notes

- `deepseek/deepseek-v4-flash` emitted `1171189` reasoning tokens despite controls; targeted reruns need an explicit budget decision or a control-check rerun.
- `qwen/qwen3-32b` emitted `107375` reasoning tokens despite controls; targeted reruns need an explicit budget decision or a control-check rerun.
- `google/gemma-4-31b-it` emitted `6403` reasoning tokens despite controls; targeted reruns need an explicit budget decision or a control-check rerun.

## Blocked Cells

These rows are excluded from scored summaries; they document provider-route, content-filter, or stale-route limits.

- `qwen/qwen3-8b` / `value_prism_relevance`: `error`.
- `qwen/qwen3-8b` / `value_prism_valence`: `error`.
- `qwen/qwen3-235b-a22b-2507` / `value_prism_valence`: `cancelled`.
- `qwen/qwen3-235b-a22b-2507` / `ccd_bench_selection`: `error`.
- `google/gemma-3-12b-it` / `value_prism_valence`: `cancelled`.
- `google/gemma-3-27b-it` / `value_prism_valence`: `cancelled`.
- `google/gemma-2-27b-it` / `value_prism_relevance`: `error`.
- `google/gemma-2-27b-it` / `value_prism_valence`: `error`.
- `google/gemma-2-27b-it` / `ccd_bench_selection`: `error`.
- `google/gemma-4-31b-it` / `unimoral_action_prediction`: `error`.
- `google/gemma-4-31b-it` / `unimoral_moral_typology`: `error`.
- `google/gemma-4-31b-it` / `unimoral_factor_attribution`: `error`.
- `google/gemma-4-31b-it` / `unimoral_consequence_generation`: `error`.
- `google/gemma-4-31b-it` / `value_prism_relevance`: `error`.
- `google/gemma-4-31b-it` / `value_prism_valence`: `error`.
- `google/gemma-4-31b-it` / `ccd_bench_selection`: `error`.
- `deepseek/deepseek-v4-flash` / `value_prism_relevance`: `cancelled`.

## Within-Family Scaling

- `DeepSeek`: no S/M/L within-family grid in this plan; covered under time scaling instead.
- `Gemma`: full selected-grid text-accuracy means by listed tier: S/4B=0.599, M/12B=0.629, L/27B=0.621. Check task rows before making a performance claim.
- `Llama`: full selected-grid text-accuracy means by listed tier: S/3B=0.568, M/8B=0.570, L/70B=0.670. Check task rows before making a performance claim.
- `Qwen`: full selected-grid text-accuracy means by listed tier: S/8B=0.589, M/32B=0.598, L/MoE 235B-A22B=0.586. Check task rows before making a performance claim.
- Takeaway: Llama has the clearest size-scaling lift; Gemma improves mildly then flattens; Qwen is non-monotonic because the 32B row trails both 8B and the 235B MoE on the text-accuracy mean.

## Time Scaling

- `DeepSeek`: 2025-Q1 chat/V3=0.601 -> 2025-Q3 chat/V3.1=0.618 -> 2025-Q4 chat/V3.2=0.603 -> 2026-Q2 flash/V4=0.609.
- `Gemma`: insufficient completed time-scaling rows.
- `Llama`: insufficient completed time-scaling rows.
- `Qwen`: 2024-Q4 S/7B=0.582 -> 2026-Q1 S/9B=0.642.
- Takeaway: DeepSeek is not monotonic over time, Qwen's small-model time line improves, and Gemma's time-scaling rows are limited by provider-route blockers.

## Cross-Benchmark Metric Spread

These ranges mix benchmark-level metrics, so they flag disagreement for inspection rather than a single performance ranking.
The most useful comparison is within a benchmark/metric column, then across related models.

- `deepseek/deepseek-chat-v3-0324`: observed benchmark score range 0.446-1.000 across completed benchmark summaries.
- `deepseek/deepseek-chat-v3.1`: observed benchmark score range 0.481-1.000 across completed benchmark summaries.
- `deepseek/deepseek-v3.2`: observed benchmark score range 0.481-0.996 across completed benchmark summaries.
- `deepseek/deepseek-v4-flash`: observed benchmark score range 0.487-1.000 across completed benchmark summaries.
- `google/gemma-3-12b-it`: observed benchmark score range 0.485-1.000 across completed benchmark summaries.
- `google/gemma-3-27b-it`: observed benchmark score range 0.480-1.000 across completed benchmark summaries.
- `google/gemma-3-4b-it`: observed benchmark score range 0.477-1.000 across completed benchmark summaries.
- `meta-llama/llama-3.1-8b-instruct`: observed benchmark score range 0.487-1.000 across completed benchmark summaries.
- `meta-llama/llama-3.2-3b-instruct`: observed benchmark score range 0.470-1.000 across completed benchmark summaries.
- `meta-llama/llama-3.3-70b-instruct`: observed benchmark score range 0.511-1.000 across completed benchmark summaries.
- `qwen/qwen-2.5-7b-instruct`: observed benchmark score range 0.472-1.000 across completed benchmark summaries.
- `qwen/qwen3-235b-a22b-2507`: observed benchmark score range 0.463-0.626 across completed benchmark summaries.
- `qwen/qwen3-32b`: observed benchmark score range 0.451-1.000 across completed benchmark summaries.
- `qwen/qwen3-8b`: observed benchmark score range 0.470-1.000 across completed benchmark summaries.
- `qwen/qwen3.5-9b`: observed benchmark score range 0.481-1.000 across completed benchmark summaries.
