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
