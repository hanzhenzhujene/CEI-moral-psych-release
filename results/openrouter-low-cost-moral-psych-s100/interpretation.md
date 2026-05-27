# OpenRouter Low-Cost Pilot Interpretation

This is a bounded sample-100 pilot: useful for early pattern finding and cost control, not a final full-benchmark claim.

## TLDR

- Completed `119` / `119` planned model-task rows across `17` models for `$0.399078` observed cost.
- Highest bounded-pilot text-accuracy means: `meta-llama/llama-3.3-70b-instruct`=0.712, `deepseek/deepseek-v4-flash`=0.674, `google/gemma-3-27b-it`=0.666, `google/gemma-3-12b-it`=0.662.
- Scaling is mixed rather than cleanly monotonic: Llama shows the clearest large-model lift, while Qwen, Gemma, and DeepSeek vary by task and release line.
- CCD-Bench remains a valid-choice / choice-behavior readout, not an accuracy metric.
- Cost-control caveat: `deepseek/deepseek-v4-flash` emitted `20674` reasoning tokens despite controls.

## Coverage

- Models with any successful row: `17`.
- Model x benchmark summary rows: `51`.
- Included benchmarks: UniMoral, ValuePrism, CCD-Bench.
- Excluded benchmarks: SMID and DeNEVIL.
- CCD-Bench is choice-format/cluster behavior, not accuracy.
- Conservative observed cost estimate: `$0.399078` using input + output + reasoning tokens at OpenRouter metadata rates.
- Observed reasoning tokens: `21552`.

## Benchmark Guide

- UniMoral action, moral-typology, and factor-attribution rows are accuracy-style text classification tasks.
- UniMoral consequence generation is a live METEOR-style generation score; do not compare its magnitude directly with accuracy rows.
- ValuePrism rows are prompt-based relevance/valence classification, not Kaleido model replication.
- CCD-Bench is valid-choice coverage and choice-format behavior, not correctness or accuracy.

## Cost-Control Notes

- `deepseek/deepseek-v4-flash` emitted `20674` reasoning tokens despite controls; larger runs need an explicit budget decision or a control-check rerun.
- `qwen/qwen3-32b` emitted `878` residual reasoning tokens despite controls; this was bounded in the current pilot but should be monitored.

## Within-Family Scaling

- `DeepSeek`: no S/M/L within-family grid in this plan; covered under time scaling instead.
- `Gemma`: sample-limited text-accuracy means by listed tier: S/4B=0.630, M/12B=0.662, L/27B=0.666. Pattern is early evidence only; check task rows before making a performance claim.
- `Llama`: sample-limited text-accuracy means by listed tier: S/3B=0.576, M/8B=0.592, L/70B=0.712. Pattern is early evidence only; check task rows before making a performance claim.
- `Qwen`: sample-limited text-accuracy means by listed tier: S/8B=0.622, M/32B=0.598, L/MoE 235B-A22B=0.660. Pattern is early evidence only; check task rows before making a performance claim.
- Takeaway: Llama has the clearest size-scaling lift in this pilot; Gemma improves mildly; Qwen is non-monotonic because the 32B row trails both 8B and the 235B MoE on the text-accuracy mean.

## Time Scaling

- `DeepSeek`: 2025-Q1 chat/V3=0.590 -> 2025-Q3 chat/V3.1=0.624 -> 2025-Q4 chat/V3.2=0.624 -> 2026-Q2 flash/V4=0.674.
- `Gemma`: 2024-Q3 L/27B=0.584 -> 2026-Q1 L/31B=0.656.
- `Llama`: insufficient completed time-scaling rows.
- `Qwen`: 2024-Q4 S/7B=0.642 -> 2026-Q1 S/9B=0.652.
- Takeaway: DeepSeek and Gemma improve on the text-accuracy mean, while Qwen changes only slightly; task-level rows still show reversals, especially on UniMoral action/consequence and ValuePrism valence.

## Cross-Benchmark Metric Spread

These ranges mix benchmark-level metrics, so they flag disagreement for inspection rather than a single performance ranking.
The most useful comparison is within a benchmark/metric column, then across related models.

- `deepseek/deepseek-chat-v3-0324`: observed benchmark score range 0.399-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-chat-v3.1`: observed benchmark score range 0.490-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-v3.2`: observed benchmark score range 0.500-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-v4-flash`: observed benchmark score range 0.506-1.000 across completed pilot benchmarks.
- `google/gemma-2-27b-it`: observed benchmark score range 0.367-1.000 across completed pilot benchmarks.
- `google/gemma-3-12b-it`: observed benchmark score range 0.480-1.000 across completed pilot benchmarks.
- `google/gemma-3-27b-it`: observed benchmark score range 0.485-1.000 across completed pilot benchmarks.
- `google/gemma-3-4b-it`: observed benchmark score range 0.468-1.000 across completed pilot benchmarks.
- `google/gemma-4-31b-it`: observed benchmark score range 0.447-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.1-8b-instruct`: observed benchmark score range 0.477-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.2-3b-instruct`: observed benchmark score range 0.454-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.3-70b-instruct`: observed benchmark score range 0.531-1.000 across completed pilot benchmarks.
- `qwen/qwen-2.5-7b-instruct`: observed benchmark score range 0.475-1.000 across completed pilot benchmarks.
- `qwen/qwen3-235b-a22b-2507`: observed benchmark score range 0.502-0.860 across completed pilot benchmarks.
- `qwen/qwen3-32b`: observed benchmark score range 0.411-1.000 across completed pilot benchmarks.
- `qwen/qwen3-8b`: observed benchmark score range 0.453-1.000 across completed pilot benchmarks.
- `qwen/qwen3.5-9b`: observed benchmark score range 0.469-1.000 across completed pilot benchmarks.
