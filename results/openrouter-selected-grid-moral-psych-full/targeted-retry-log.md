# Targeted Retry Log

This file records bounded retries of selected non-success OpenRouter cells. It is operational evidence only; scored summaries change only when `result_summary.csv` gains successful eval rows.

## 2026-07-06 20:56 UTC

Purpose: retry a small set of recognizable Qwen/Gemma family gaps before attempting larger remaining routes. The batch prioritized CCD-Bench and UniMoral cells plus several ValuePrism valence cells with lower estimated spend than the remaining relevance routes.

Outcome: all eight routes returned OpenRouter `402 Insufficient credits` before producing successful rows. No scored rows were added, no raw completions were committed, and the selected-grid readout remains `102/119` successful model-task rows.

| Model | Task | Outcome |
| :--- | :--- | :--- |
| `qwen/qwen3-235b-a22b-2507` | `ccd_bench_selection` | OpenRouter `402 Insufficient credits` |
| `qwen/qwen3-235b-a22b-2507` | `value_prism_valence` | OpenRouter `402 Insufficient credits` |
| `qwen/qwen3-8b` | `value_prism_valence` | OpenRouter `402 Insufficient credits` |
| `google/gemma-3-12b-it` | `value_prism_valence` | OpenRouter `402 Insufficient credits` |
| `google/gemma-3-27b-it` | `value_prism_valence` | OpenRouter `402 Insufficient credits` |
| `google/gemma-4-31b-it` | `ccd_bench_selection` | OpenRouter `402 Insufficient credits` |
| `google/gemma-4-31b-it` | `unimoral_consequence_generation` | OpenRouter `402 Insufficient credits` |
| `google/gemma-4-31b-it` | `unimoral_action_prediction` | OpenRouter `402 Insufficient credits` |

Next action: add OpenRouter credits before retrying. After credits are available, retry named cells in this order: CCD-Bench cells first, UniMoral cells next, ValuePrism valence cells next, and ValuePrism relevance cells last because they have the largest sample count.

## 2026-07-06 21:14 UTC

Purpose: verify whether the cost-aware, faster route-first retry plan is currently runnable before launching any parallel full-task jobs. The probe used one sample only and did not produce a scored benchmark row.

Outcome: OpenRouter remains blocked by account credits, and the direct OpenAI paper route checked here is unavailable to the current API key. No scored rows were added, no raw completions were committed, and no full-task parallel batch was launched.

| Route | Task | Probe size | Outcome |
| :--- | :--- | :--- | :--- |
| `openrouter/qwen/qwen3-235b-a22b-2507` | `ccd_bench_selection` | 1 sample | OpenRouter `402 Insufficient credits` |
| `openai/chatgpt-4o-latest` | `ccd_bench_selection` | 1 sample | OpenAI `model_not_found` / no access for exact paper route |

Next action: after OpenRouter credits are available, retry the named OpenRouter cells in the same cost-aware order: CCD-Bench first, UniMoral next, ValuePrism valence next, and ValuePrism relevance last. Do not substitute `gpt-4o` for `chatgpt-4o-latest` in the paper-calibration bridge unless the team explicitly changes the same-model rule.

## 2026-07-07 00:43 UTC

Purpose: re-check whether the cost-aware selected-grid retry plan is unblocked before launching any parallel or full-task jobs. The probe used one sample only, prioritized the lowest-estimated-spend high-signal remaining cell, and did not produce a scored benchmark row.

Outcome: OpenRouter still returned `402 Insufficient credits` before completing the sample. No scored rows were added, no raw completions were committed, and no parallel full-task retry was launched.

| Route | Task | Probe size | Outcome |
| :--- | :--- | :--- | :--- |
| `openrouter/qwen/qwen3-235b-a22b-2507` | `ccd_bench_selection` | 1 sample | OpenRouter `402 Insufficient credits` |

Next action: add OpenRouter credits before retrying. Once credits are available, keep the same order: CCD-Bench cells first, UniMoral action/generation next, ValuePrism valence next, and ValuePrism relevance last because it has the largest sample count.
