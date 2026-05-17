# UniMoral Completion Audit

Status: **not achieved**.

Objective: complete UniMoral RQ2/RQ3/RQ4 for the existing release model set, update code/results/figures/docs, validate consistency, and commit/push a clean branch.

## Prompt-to-Artifact Checklist

| Requirement | Evidence artifact or command | Current evidence | Status |
| --- | --- | --- | --- |
| RQ2/RQ3/RQ4 task definitions exist | `src/inspect/evals/unimoral.py`, `src/inspect/evals/moral_psych.py`, `scripts/verify_unimoral_task_builders.py` | Provider-free task-builder verification covers RQ1-RQ4 registry entries. | structurally covered |
| Results cover existing model set | `unimoral-coverage.csv`, `unimoral-full-benchmark.csv`, strict `scripts/verify_unimoral_completion.py` | unimoral_action_prediction 16/16 complete, unimoral_moral_typology 15/16 incomplete, unimoral_factor_attribution 14/16 incomplete, unimoral_consequence_generation 14/16 incomplete | incomplete |
| Sample-level predictions are complete for RQ2/RQ3/RQ4 | `unimoral-sample-predictions.csv` | 136782 rows present; strict expected count is 140256. | incomplete |
| Known failures are empty | `unimoral-failure-checklist.csv` | 5 rows: MiniMax-S unimoral_moral_typology complete_recovered_logs 3492/3492 parsed=3383; MiniMax-S unimoral_factor_attribution complete_parse_gap 3492/3492 parsed=719; MiniMax-M unimoral_consequence_generation complete_recovered_logs 1782/1782 parsed=1770; MiniMax-L unimoral_factor_attribution partial 1800/3492 parsed=1784; MiniMax-L unimoral_consequence_generation partial 0/1782 parsed=0. | incomplete |
| Figures and release docs rebuild from tracked artifacts | `scripts/build_unimoral_artifacts.py`, `make audit` | Structural release gate allows documented incomplete cells until MiniMax blockers are resolved. | covered with caveat |
| MiniMax is not run without explicit authorization | `make unimoral-missing-plan`, `scripts/run_unimoral_missing_tasks.sh`, `tests/test_provider_config.py` | `make unimoral-missing-plan` is dry-run only; non-dry-run MiniMax lines require `UNIMORAL_ALLOW_MINIMAX=1`; current user instruction forbids MiniMax runs. | guarded |
| Secrets or credentials are not introduced | Branch diff credential-pattern scan against `origin/main...HEAD` | No literal provider keys or tokens were found; provider key references are environment-variable names only. | covered |
| Clean committed branch | `git status --short --branch`, `git rev-list --left-right --count HEAD...@{upstream}` | Post-generation check required: this generated artifact cannot prove the final commit/push state; the final operator report must cite clean status and 0/0 ahead-behind after the last push. | external final check |

## CSV-Level Strict Blockers

Total strict sample prediction gap: **3474** rows.

- `MiniMax-S` `unimoral_moral_typology`: no sample-count gap (3492/3492) but status `complete_recovered_logs` prevents strict completion.
- `MiniMax-S` `unimoral_factor_attribution`: no sample-count gap (3492/3492) but status `complete_parse_gap` prevents strict completion.
- `MiniMax-M` `unimoral_consequence_generation`: no sample-count gap (1782/1782) but status `complete_recovered_logs` prevents strict completion.
- `MiniMax-L` `unimoral_factor_attribution`: 1692 sample predictions missing (1800/3492); status `partial`.
- `MiniMax-L` `unimoral_consequence_generation`: 1782 sample predictions missing (0/1782); status `partial`.

## Completion Gate

Strict completion is blocked by MiniMax-only saved-artifact gaps. Do not mark the objective complete while `scripts/verify_unimoral_completion.py` fails, `unimoral-failure-checklist.csv` is nonempty, or `unimoral-coverage.csv` has incomplete RQ2/RQ3/RQ4 rows.

No MiniMax provider calls are made by generating this audit.
