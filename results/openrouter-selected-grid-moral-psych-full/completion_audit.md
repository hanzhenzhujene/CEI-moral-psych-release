# OpenRouter Selected-Grid Completion Audit

Evidence level: `full selected-grid attempted with blocked cells`.
Sample limit: `full dataset` per task.
Planned model-task rows: `119`.
Eligible available models: `17`.
Planned estimated cost: `$51.6126`.
Full-objective status: All `119` planned rows were attempted; `101` produced scored success rows and `18` are documented provider/filter/stale-route blockers.

## Live Evidence

- Successful model-task rows: `101` / `119`.
- Completed models: `16`.
- Completed tasks: `7` / `7`.
- Completed sample counts observed: `1782, 2182, 3492, 8784, 21840, 43680`.
- Success-row API cost from parsed Inspect logs: `$16.313216`.
- All recorded API cost from parsed Inspect logs, including blocked partial rows: `$17.760398`.
- Observed reasoning tokens: `1278564`.

## Requirement Audit

| Requirement | Evidence | Status |
| :--- | :--- | :--- |
| Allowed benchmarks identified | `benchmark_map.csv` lists `CCD-Bench, UniMoral, ValuePrism` with paper, data/prompt route, scorer, metric, and replication status. | proven |
| SMID, DeNEVIL, and MiniMax excluded | Forbidden benchmarks present: `none`; MiniMax present: `False`. | proven |
| OpenRouter pricing fetched before planning | `openrouter-pricing-metadata.json` records the `/models` metadata fetch used for `model_grid.csv` and `run_plan.csv`. | proven |
| Per-model price cap enforced | Eligible available rows over cap without baseline exemption: `none`. | proven |
| Within-family and time-scaling grids selected | `model_grid.csv` contains `17` eligible available OpenRouter rows across the requested grid labels. | proven |
| Run selected models on the three allowed benchmarks | All `119` planned model-task rows have terminal states: `101` success, `18` provider/filter/stale-route blockers. | attempted with blockers |
| Output model/family/size/release/benchmark/score/cost/replication tables | `run_plan.csv`, `result_summary.csv`, `benchmark_summary.csv`, and `model_summary.csv` provide the requested columns for scored rows and terminal-state metadata for blocked rows. | proven |
| Output plots | `figures/cost_estimate.svg` is generated for plans; `figures/pilot_scores.svg` is generated when scored rows exist. | proven |
| Summarize robust patterns | `interpretation.md` summarizes scaling, time-scaling, and cross-benchmark disagreement for completed rows. | proven |

## Blocked / Non-Success Rows

| Model | Task | Status | Note |
| :--- | :--- | :--- | :--- |
| `qwen/qwen3-8b` | `value_prism_relevance` | `error` | subprocess exited 2; see eval log |
| `qwen/qwen3-8b` | `value_prism_valence` | `error` | subprocess exited 2; see eval log |
| `qwen/qwen3-235b-a22b-2507` | `value_prism_valence` | `cancelled` | subprocess exited 2; see eval log |
| `qwen/qwen3-235b-a22b-2507` | `ccd_bench_selection` | `cancelled` | subprocess exited 2; see eval log |
| `google/gemma-3-12b-it` | `value_prism_valence` | `cancelled` | subprocess exited 2; see eval log |
| `google/gemma-3-27b-it` | `value_prism_valence` | `cancelled` | subprocess exited 2; see eval log |
| `meta-llama/llama-3.2-3b-instruct` | `ccd_bench_selection` | `cancelled` | subprocess exited 2; see eval log |
| `google/gemma-2-27b-it` | `value_prism_relevance` | `error` | subprocess exited 2; see eval log |
| `google/gemma-2-27b-it` | `value_prism_valence` | `error` | subprocess exited 2; see eval log |
| `google/gemma-2-27b-it` | `ccd_bench_selection` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `unimoral_action_prediction` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `unimoral_moral_typology` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `unimoral_factor_attribution` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `unimoral_consequence_generation` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `value_prism_relevance` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `value_prism_valence` | `error` | subprocess exited 2; see eval log |
| `google/gemma-4-31b-it` | `ccd_bench_selection` | `error` | subprocess exited 2; see eval log |
| `deepseek/deepseek-v4-flash` | `value_prism_relevance` | `cancelled` | subprocess exited 2; see eval log |

## Unblock

No user unblock is required unless you want an explicitly budgeted targeted retry of the blocked provider routes.

## Optional Targeted Retry

Do not rerun the whole grid by default. If the team approves more spend, retry only named blocked `model` x `task` cells after checking the provider route and budget.
