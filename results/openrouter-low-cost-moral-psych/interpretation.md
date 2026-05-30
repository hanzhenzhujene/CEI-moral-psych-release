# OpenRouter Low-Cost Pilot Interpretation

This file summarizes the currently completed pilot rows only. Small sample limits are route-validation evidence, not final benchmark claims.

## Coverage

- Models with any successful row: `17`.
- Model x benchmark summary rows: `51`.
- Included benchmarks: UniMoral, ValuePrism, CCD-Bench.
- Excluded benchmarks: SMID and DeNEVIL.
- CCD-Bench is choice-format/cluster behavior, not accuracy.
- Conservative observed cost estimate: `$0.008199` using input + output + reasoning tokens at OpenRouter metadata rates.
- Observed reasoning tokens: `15046`.

## Cost-Control Notes

- `qwen/qwen3.5-9b` emitted `14084` reasoning tokens in the pilot despite the default `/no_think`/extra-body controls.
- `deepseek/deepseek-v4-flash` emitted `954` reasoning tokens in the pilot despite the default `/no_think`/extra-body controls.
- `qwen/qwen3-32b` emitted `8` reasoning tokens in the pilot despite the default `/no_think`/extra-body controls.
- Treat any larger run for these models as blocked on a smaller second pilot or an explicit budget override.

## Within-Family Scaling

- `DeepSeek`: pilot text-accuracy means by listed tier: chat/V3=0.400, chat/V3.1=0.400, chat/V3.2=0.200, flash/V4=0.800. Treat as route smoke until larger sample limits finish.
- `Gemma`: pilot text-accuracy means by listed tier: L/27B=0.400, L/27B=0.200, L/31B=0.400, M/12B=0.400, S/4B=0.400. Treat as route smoke until larger sample limits finish.
- `Llama`: pilot text-accuracy means by listed tier: L/70B=0.800, M/8B=0.200, S/3B=0.200. Treat as route smoke until larger sample limits finish.
- `Qwen`: pilot text-accuracy means by listed tier: L/MoE 235B-A22B=0.400, M/32B=0.400, S/7B=0.400, S/8B=0.400, S/9B=0.200. Treat as route smoke until larger sample limits finish.

## Time Scaling

- `DeepSeek`: 2025-Q1 chat/V3=0.400 -> 2025-Q3 chat/V3.1=0.400 -> 2025-Q4 chat/V3.2=0.200 -> 2026-Q2 flash/V4=0.800.
- `Gemma`: 2024-Q3 L/27B=0.400 -> 2026-Q1 L/31B=0.400.
- `Llama`: insufficient completed time-scaling rows.
- `Qwen`: 2024-Q4 S/7B=0.400 -> 2026-Q1 S/9B=0.200.

## Benchmark Disagreement

- `deepseek/deepseek-chat-v3-0324`: observed benchmark score range 0.250-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-chat-v3.1`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-v3.2`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `deepseek/deepseek-v4-flash`: observed benchmark score range 0.500-1.000 across completed pilot benchmarks.
- `google/gemma-2-27b-it`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `google/gemma-3-12b-it`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `google/gemma-3-27b-it`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `google/gemma-3-4b-it`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `google/gemma-4-31b-it`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.1-8b-instruct`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.2-3b-instruct`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `meta-llama/llama-3.3-70b-instruct`: observed benchmark score range 0.500-1.000 across completed pilot benchmarks.
- `qwen/qwen-2.5-7b-instruct`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `qwen/qwen3-235b-a22b-2507`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `qwen/qwen3-32b`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `qwen/qwen3-8b`: observed benchmark score range 0.000-1.000 across completed pilot benchmarks.
- `qwen/qwen3.5-9b`: observed benchmark score range 0.000-0.500 across completed pilot benchmarks.
