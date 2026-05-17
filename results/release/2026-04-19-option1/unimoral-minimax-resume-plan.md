# UniMoral MiniMax Resume Plan

This file is a provider-free handoff for the remaining UniMoral RQ2/RQ3/RQ4 blockers. It documents the current MiniMax gaps without granting permission to run MiniMax.

Run these only after MiniMax runs are explicitly allowed and a valid `OPENROUTER_API_KEY` or direct MiniMax route is available.

## Current State

| Line | Task | Failure status | Saved coverage | Dry-run range plan |
| --- | --- | --- | --- | --- |
| `MiniMax-S` | `unimoral_moral_typology` | `complete_recovered_logs` | 3492/3492 logged; 3383/3492 parseable | 54 parse-gap ranges covering 109 samples |
| `MiniMax-S` | `unimoral_factor_attribution` | `complete_parse_gap` | 3492/3492 logged; 719/3492 parseable | 511 unmerged ranges covering 2773 samples; max_gap=3 gives 14 ranges covering 3436 samples |
| `MiniMax-S` | `unimoral_consequence_generation` | `parse_gap_dry_run` | 1782/1782 logged; 1781/1782 parseable | 1 parse-gap range covering 1 sample |
| `MiniMax-M` | `unimoral_factor_attribution` | `parse_gap_dry_run` | 3492/3492 logged; 3491/3492 parseable | 1 parse-gap range covering 1 sample |
| `MiniMax-M` | `unimoral_consequence_generation` | `complete_recovered_logs` | 1782/1782 logged; 1770/1782 parseable | 5 parse-gap ranges covering 12 samples |
| `MiniMax-L` | `unimoral_factor_attribution` | `partial` | 1800/3492 logged; 1784/3492 parseable | 8 missing/parse-gap ranges covering 1708 samples |
| `MiniMax-L` | `unimoral_consequence_generation` | `partial` | 0/1782 logged; 0/1782 parseable | 1 full-task range covering 1782 samples |

Rows marked `parse_gap_dry_run` were not severe enough to appear in `unimoral-failure-checklist.csv`, but the provider-free launcher dry-run still found parse-limited samples worth replacing during the MiniMax cleanup pass.

## Dry-Run Check

Use this before any provider call to refresh the planned ranges:

```bash
UNIMORAL_DRY_RUN=1 FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 UNIMORAL_ROUTE_MODE=openrouter MODEL_FILTER='MiniMax-S,MiniMax-M,MiniMax-L' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

For `MiniMax-S` factor attribution, the unmerged plan has 511 tiny ranges. The best practical dry-run setting observed on May 17, 2026 was:

```bash
UNIMORAL_DRY_RUN=1 FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 UNIMORAL_RERUN_UNPARSED_MAX_GAP=3 UNIMORAL_ROUTE_MODE=openrouter MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

## Recommended Execution

Run cells separately so a MiniMax failure does not hide which cell advanced:

### MiniMax-S / unimoral_moral_typology

```bash
UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_moral_typology' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `Use the dry-run command above to print the full 54-range list.`

### MiniMax-S / unimoral_factor_attribution

```bash
UNIMORAL_RERUN_UNPARSED_MAX_GAP=3 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `0 304;308 387;393 604;608 619;623 626;630 834;838 857;861 1026;1031 1238;1242 2369;2373 2651;2656 3077;3081 3472;3476 3492`

### MiniMax-S / unimoral_consequence_generation

```bash
UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_consequence_generation' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `1120 1121`

### MiniMax-M / unimoral_factor_attribution

```bash
UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-M' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `1981 1982`

### MiniMax-M / unimoral_consequence_generation

```bash
UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-M' TASK_FILTER='unimoral_consequence_generation' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `1111 1112;1172 1173;1334 1335;1465 1466;1468 1476`

### MiniMax-L / unimoral_factor_attribution

```bash
UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-L' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `379 380;715 717;721 722;725 1750;2774 2775;2811 2812;2814 2817;2818 3492`

### MiniMax-L / unimoral_consequence_generation

```bash
UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-L' TASK_FILTER='unimoral_consequence_generation' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `0 1782`

## After Reruns

Rebuild and verify the release artifacts:

```bash
/opt/anaconda3/bin/python scripts/build_unimoral_artifacts.py
/opt/anaconda3/bin/python scripts/verify_unimoral_completion.py
make audit VENV_PYTHON=/opt/anaconda3/bin/python
```

Strict completion requires `unimoral-failure-checklist.csv` to be empty and RQ1-RQ4 coverage to show 16/16 strict-complete model lines.
