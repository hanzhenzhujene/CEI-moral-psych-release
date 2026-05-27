# OpenRouter Low-Cost Completion Audit

Evidence level: `live run complete`.
Sample limit: `100` per task.
Planned model-task rows: `119`.
Eligible available models: `17`.
Planned estimated cost: `$1.2000`.
Full-objective status: Bounded sample-100 evidence only; this is not a final full-benchmark claim.

## Live Evidence

- Successful model-task rows: `119` / `119`.
- Completed models: `17`.
- Completed tasks: `7` / `7`.
- Completed sample counts observed: `100`.
- Observed API cost from parsed Inspect logs: `$0.399078`.
- Observed reasoning tokens: `21552`.

## Requirement Audit

| Requirement | Evidence | Status |
| :--- | :--- | :--- |
| Allowed benchmarks identified | `benchmark_map.csv` lists `CCD-Bench, UniMoral, ValuePrism` with paper, data/prompt route, scorer, metric, and replication status. | proven |
| SMID, DeNEVIL, and MiniMax excluded | Forbidden benchmarks present: `none`; MiniMax present: `False`. | proven |
| OpenRouter pricing fetched before planning | `openrouter-pricing-metadata.json` records the `/models` metadata fetch used for `model_grid.csv` and `run_plan.csv`. | proven |
| Per-model price cap enforced | Eligible available rows over cap without baseline exemption: `none`. | proven |
| Within-family and time-scaling grids selected | `model_grid.csv` contains `17` eligible available OpenRouter rows across the requested grid labels. | proven |
| Run selected models on the three allowed benchmarks | All `119` recorded model-task rows completed with `success`. | partial |
| Output model/family/size/release/benchmark/score/cost/replication tables | `run_plan.csv`, `result_summary.csv`, `benchmark_summary.csv`, and `model_summary.csv` provide the requested columns where live rows exist. | proven |
| Output plots | `figures/cost_estimate.svg` is generated for plans; `figures/pilot_scores.svg` is generated when scored rows exist. | proven |
| Summarize robust patterns | `interpretation.md` summarizes scaling, time-scaling, and cross-benchmark disagreement for completed rows. | partial |

## Unblock

Approve a full live run to turn this pilot into full selected-grid evidence. The current full-dataset selected-grid estimate is `$51.6126`. DeepSeek/Qwen reasoning-token leakage should be budgeted explicitly before that run.

## Approved Full-Run Command

Run only after explicit approval for the full selected-grid OpenRouter spend.

```bash
/opt/anaconda3/bin/python scripts/openrouter_low_cost_moral_psych.py run --full --output-dir results/openrouter-low-cost-moral-psych-full --max-connections 1 --max-total-estimated-cost 60 --yes
/opt/anaconda3/bin/python scripts/openrouter_low_cost_moral_psych.py summarize --full --output-dir results/openrouter-low-cost-moral-psych-full
```

The command keeps the live run bounded by `--max-total-estimated-cost 60`, uses `--max-connections 1` for provider stability, and keeps completed rows resumable through the default `--skip-existing-success` behavior.

Do not treat the bounded pilot as the full benchmark. It is a cost-controlled evidence package for early pattern finding and route validation.
