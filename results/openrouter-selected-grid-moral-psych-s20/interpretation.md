# OpenRouter Selected-Grid Pilot Interpretation

This is a bounded sample-20 pilot: useful for early pattern finding and cost control, not a final full-benchmark claim.

## TLDR

- Completed `119` / `119` planned model-task rows across `17` models for `$0.167436` observed cost.
- Highest bounded-pilot text-accuracy means: `qwen/qwen-2.5-7b-instruct`=0.660, `meta-llama/llama-3.3-70b-instruct`=0.650, `google/gemma-4-31b-it`=0.640, `qwen/qwen3-235b-a22b-2507`=0.640.
- Scaling is mixed rather than cleanly monotonic: Llama shows the clearest large-model lift, while Qwen, Gemma, and DeepSeek vary by task and release line.
- CCD-Bench remains a valid-choice / choice-behavior readout, not an accuracy metric.
- Cost-control outlier: `qwen/qwen3.5-9b` emitted `285277` reasoning tokens despite controls.

## Coverage

- Models with any successful row: `17`.
- Model x benchmark summary rows: `51`.
- Included benchmarks: UniMoral, ValuePrism, CCD-Bench.
- Excluded benchmarks: SMID and DeNEVIL.
- CCD-Bench is choice-format/cluster behavior, not accuracy.
- Conservative observed cost estimate: `$0.167436` using input + output + reasoning tokens at OpenRouter metadata rates.
- Observed reasoning tokens: `306036`.

## Cost-Control Notes

- `qwen/qwen3.5-9b` emitted `285277` reasoning tokens in the pilot despite the default `/no_think`/extra-body controls.
- `deepseek/deepseek-v4-flash` emitted `20561` reasoning tokens in the pilot despite the default `/no_think`/extra-body controls.
- `qwen/qwen3-32b` emitted `198` reasoning tokens in the pilot despite the default `/no_think`/extra-body controls.
- Treat any larger run for these models as blocked on an explicit budget decision or a smaller control-check rerun.

## Within-Family Scaling

- `DeepSeek`: insufficient completed pilot rows for a scaling statement.
- `Gemma`: sample-limited text-accuracy means by listed tier: S/4B=0.570, M/12B=0.590, L/27B=0.570. Pattern is early evidence only; check task rows before making a performance claim.
- `Llama`: sample-limited text-accuracy means by listed tier: S/3B=0.530, M/8B=0.550, L/70B=0.650. Pattern is early evidence only; check task rows before making a performance claim.
- `Qwen`: sample-limited text-accuracy means by listed tier: S/8B=0.590, M/32B=0.570, L/MoE 235B-A22B=0.640. Pattern is early evidence only; check task rows before making a performance claim.

## Time Scaling

- `DeepSeek`: 2025-Q1 chat/V3=0.530 -> 2025-Q3 chat/V3.1=0.530 -> 2025-Q4 chat/V3.2=0.530 -> 2026-Q2 flash/V4=0.590.
- `Gemma`: 2024-Q3 L/27B=0.530 -> 2026-Q1 L/31B=0.640.
- `Llama`: insufficient completed time-scaling rows.
- `Qwen`: 2024-Q4 S/7B=0.660 -> 2026-Q1 S/9B=0.300.

## Cross-Benchmark Metric Spread

These ranges mix benchmark-level metrics, so they flag disagreement for inspection rather than a single performance ranking.

- `deepseek/deepseek-chat-v3-0324`: observed benchmark score range 0.366-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-chat-v3.1`: observed benchmark score range 0.459-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-v3.2`: observed benchmark score range 0.457-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-v4-flash`: observed benchmark score range 0.429-1.000 across completed pilot benchmarks.
- `google/gemma-2-27b-it`: observed benchmark score range 0.281-1.000 across completed pilot benchmarks.
- `google/gemma-3-12b-it`: observed benchmark score range 0.439-1.000 across completed pilot benchmarks.
- `google/gemma-3-27b-it`: observed benchmark score range 0.462-1.000 across completed pilot benchmarks.
- `google/gemma-3-4b-it`: observed benchmark score range 0.465-1.000 across completed pilot benchmarks.
- `google/gemma-4-31b-it`: observed benchmark score range 0.443-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.1-8b-instruct`: observed benchmark score range 0.458-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.2-3b-instruct`: observed benchmark score range 0.434-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.3-70b-instruct`: observed benchmark score range 0.508-1.000 across completed pilot benchmarks.
- `qwen/qwen-2.5-7b-instruct`: observed benchmark score range 0.471-1.000 across completed pilot benchmarks.
- `qwen/qwen3-235b-a22b-2507`: observed benchmark score range 0.492-1.000 across completed pilot benchmarks.
- `qwen/qwen3-32b`: observed benchmark score range 0.390-1.000 across completed pilot benchmarks.
- `qwen/qwen3-8b`: observed benchmark score range 0.425-1.000 across completed pilot benchmarks.
- `qwen/qwen3.5-9b`: observed benchmark score range 0.000-0.625 across completed pilot benchmarks.
