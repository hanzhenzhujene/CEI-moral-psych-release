# OpenRouter Low-Cost Completion Audit

Evidence level: `plan only`.
Sample limit: `full dataset` per task.
Planned model-task rows: `119`.
Eligible available models: `17`.
Planned estimated cost: `$51.6126`.
Full-objective status: Planned, not yet run.

## Live Evidence

- Successful model-task rows: `0` / `0`.
- Completed models: `0`.
- Completed tasks: `0` / `7`.
- Completed sample counts observed: `none`.
- Observed API cost from parsed Inspect logs: `$0.000000`.
- Observed reasoning tokens: `0`.

## Requirement Audit

| Requirement | Evidence | Status |
| :--- | :--- | :--- |
| Allowed benchmarks identified | `benchmark_map.csv` lists `CCD-Bench, UniMoral, ValuePrism` with paper, data/prompt route, scorer, metric, and replication status. | proven |
| SMID, DeNEVIL, and MiniMax excluded | Forbidden benchmarks present: `none`; MiniMax present: `False`. | proven |
| OpenRouter pricing fetched before planning | `openrouter-pricing-metadata.json` records the `/models` metadata fetch used for `model_grid.csv` and `run_plan.csv`. | proven |
| Per-model price cap enforced | Eligible available rows over cap without baseline exemption: `none`. | proven |
| Within-family and time-scaling grids selected | `model_grid.csv` contains `17` eligible available OpenRouter rows across the requested grid labels. | proven |
| Run selected models on the three allowed benchmarks | No live model calls are recorded in this output folder. | partial |
| Output model/family/size/release/benchmark/score/cost/replication tables | `benchmark_map.csv`, `model_grid.csv`, and `run_plan.csv` are present; scored result tables are created only after live rows exist. | planned only |
| Output plots | `figures/cost_estimate.svg` is generated for plans; `figures/pilot_scores.svg` is generated when scored rows exist. | cost plot only |
| Summarize robust patterns | `interpretation.md` summarizes scaling, time-scaling, and cross-benchmark disagreement for completed rows. | not run |

## Unblock

Approve the full live run before spending approximately `$51.6126` plus any provider-side reasoning-token overhead.

## Approved Full-Run Command

Run only after explicit approval for the full selected-grid OpenRouter spend.

```bash
# no-call preview
OPENROUTER_FULL_RUN_DRY_RUN=1 scripts/run_openrouter_low_cost_full.sh

# live full run after spend approval
OPENROUTER_FULL_RUN_APPROVED=1 scripts/run_openrouter_low_cost_full.sh
```

The guarded launcher keeps the live run bounded by `OPENROUTER_MAX_TOTAL_ESTIMATED_COST=60` by default, uses `OPENROUTER_MAX_CONNECTIONS=1` for provider stability, writes to `results/openrouter-low-cost-moral-psych-full`, and keeps completed rows resumable through the planner's default `--skip-existing-success` behavior.

Do not treat this plan as completed benchmark evidence.
