# UniMoral MiniMax Resume Plan

This file is a provider-free handoff for the remaining UniMoral RQ2/RQ3/RQ4 blockers. It documents the current MiniMax gaps without granting permission to run MiniMax.

Run these only after MiniMax runs are explicitly allowed, `UNIMORAL_ALLOW_MINIMAX=1` is set, and a valid `OPENROUTER_API_KEY` or direct MiniMax route is available.

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

## Parser Recovery Audit

A provider-free scan of the remaining MiniMax gaps found no safe scorer-only recovery path. Do not infer labels from hidden reasoning, prompt context, model IDs, or incomplete visible fragments.

| Line | Task | Unrecoverable saved-state evidence |
| --- | --- | --- |
| `MiniMax-S` | `unimoral_moral_typology` | 109 unparseable saved samples; all reasoning-only completions |
| `MiniMax-S` | `unimoral_factor_attribution` | 2773 unparseable saved samples; all reasoning-only completions |
| `MiniMax-S` | `unimoral_consequence_generation` | 1 unparseable saved sample; reasoning-only completion |
| `MiniMax-M` | `unimoral_factor_attribution` | 1 unparseable saved sample; reasoning-only completion |
| `MiniMax-M` | `unimoral_consequence_generation` | 12 unparseable saved samples; 3 reasoning-only and 9 provider/error-text records |
| `MiniMax-L` | `unimoral_factor_attribution` | 1692 missing samples plus 16 unparseable saved samples; remaining saved gaps are provider/error-text records or one incomplete visible fragment |
| `MiniMax-L` | `unimoral_consequence_generation` | 1782 missing samples; no usable saved samples to recover |

## Local Samplebuffer Audit

Inspect's local samplebuffer cache was also checked under `~/Library/Application Support/inspect_ai/samplebuffer/`. This found small interrupted-shard buffers, but no provider-free path to close the remaining MiniMax blockers.

| Line | Task | Buffered state | Release impact |
| --- | --- | --- | --- |
| `MiniMax-S` | `unimoral_moral_typology` | 3 DBs; 31 buffered samples; 11 scored samples | All scored rows already appear in `unimoral-sample-predictions.csv` |
| `MiniMax-M` | `unimoral_moral_typology` | 1 DB; 10 buffered samples; 9 scored samples | Non-blocking cell; no missing release rows |
| `MiniMax-M` | `unimoral_factor_attribution` | 1 DB; 15 buffered samples; 7 scored samples | Non-blocking cell; no missing release rows |
| `MiniMax-L` | `unimoral_moral_typology` | 3 DBs; 17 buffered samples; 3 scored samples | Non-blocking cell; no missing release rows |
| `MiniMax-L` | `unimoral_factor_attribution` | no matching factor-attribution samplebuffer DBs | Cannot recover the 1692 missing samples |
| `MiniMax-L` | `unimoral_consequence_generation` | no samplebuffer DB for `2026-05-17T03-30-30-00-00_unimoral-consequence-generation_Ax9iEsGjvHYpAKRrpnqexK.eval` | Cannot recover the 1782 missing samples |

The MiniMax trace files for the failed consequence-generation run contained request telemetry only. The eval config had `log_samples=true` but `log_model_api=false`, and no response-body fields such as `choices`, `messages`, `content`, `prompt`, `completion`, or `sample_id` were present in the MiniMax trace files.

The broader Inspect application-support trace directory was checked as well. Those global traces had no matching `MiniMax`, failed RQ4 eval ID, or response-body fields, so they do not provide an alternate recovery source.

Redacted shell-history and older-checkout breadcrumbs were checked too. The history points to UniMoral dataset setup under `~/Desktop/moral-psych-data/unimoral` and an older `~/Desktop/moral-psychology-benchmark` checkout, but not to completed RQ2/RQ3/RQ4 MiniMax result artifacts. The older checkout contains UniMoral RQ2/RQ3/RQ4 task-builder code and prompts, while its saved Inspect UniMoral logs are action-prediction runs only.

The sibling `~/Desktop/cei-jenny-main-sync` checkout was also inspected. Its release catalog reports UniMoral as "Action prediction only", and the checkout contains RQ2/RQ3/RQ4 task-builder code/prompts but no saved MiniMax RQ2/RQ3/RQ4 release artifacts or Inspect logs.

Local Time Machine snapshots were listed for May 17, 2026, but no browsable backup content was mounted under `/Volumes/.timemachine`. Do not attempt a snapshot restore or mount operation without explicit user approval.

The `results/inspect/full-runs/2026-05-16-unimoral-full/minimax_l/` transcripts were checked after a Spotlight index search. They contain run starts and one old `args[@]: unbound variable` shell failure for MiniMax-L factor attribution, but no model predictions. The current launcher keeps the empty-args expansion guarded under `set -u`, with a regression test in `tests/test_provider_config.py`.

Git LFS and ignored local payloads were checked. There are no Git LFS files or local LFS objects. The ignored MiniMax-L full-run `.eval` files match the release tables exactly: `unimoral_factor_attribution` has 1800 unique logged samples locally and 1800 release prediction rows, while `unimoral_consequence_generation` has 0 local samples and 0 release prediction rows. No ignored success shard was omitted from `unimoral-sample-predictions.csv`.

The MiniMax smoke/probe logs under `results/inspect/logs/2026-05-16-unimoral-smoke/` and `results/inspect/logs/2026-05-17-unimoral-smoke/` were checked. They contain 22 tiny MiniMax eval archives, map only to MiniMax-S/M model routes, and do not add any same-line sample IDs missing from the release tables. They should not be used to fill the MiniMax-L blockers.

Google Drive was searched for exported or shared UniMoral artifacts using exact and broad terms including `unimoral sample predictions`, `unimoral full benchmark`, `unimoral-rq4-bertscore`, `unimoral_factor_attribution`, `unimoral_consequence_generation`, `MiniMax-L factor attribution`, `MiniMax-L consequence generation`, `CEI moral psych release`, and the failed MiniMax-L consequence-generation eval ID. The only relevant hits were the May 2026 working doc/deck materials, which state the extra UniMoral tasks were still "not yet scored" or action items to check; no Drive result contained saved MiniMax RQ2/RQ3/RQ4 predictions or release CSV artifacts.

## Dry-Run Check

Use this before any provider call to refresh the planned ranges:

```bash
UNIMORAL_DRY_RUN=1 FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 UNIMORAL_ROUTE_MODE=openrouter MODEL_FILTER='MiniMax-S,MiniMax-M,MiniMax-L' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

For `MiniMax-S` factor attribution, the unmerged plan has 511 tiny ranges. The best practical dry-run setting observed on May 17, 2026 was:

```bash
UNIMORAL_DRY_RUN=1 FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 UNIMORAL_RERUN_UNPARSED_MAX_GAP=3 UNIMORAL_ROUTE_MODE=openrouter MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

A full MiniMax provider-free refresh with `UNIMORAL_RERUN_UNPARSED_MAX_GAP=3` on May 17, 2026 kept the same missing cells but merged nearby gaps for other cells too. Notable compact ranges were:

| Line | Task | `max_gap=3` dry-run ranges |
| --- | --- | --- |
| `MiniMax-S` | `unimoral_moral_typology` | `2613 2614;3298 3300;3304 3395;3399 3423;3431 3481;3485 3492` |
| `MiniMax-M` | `unimoral_consequence_generation` | `1111 1112;1172 1173;1334 1335;1465 1476` |
| `MiniMax-L` | `unimoral_factor_attribution` | `379 380;715 717;721 1750;2774 2775;2811 3492` |

Use these compact ranges only when you intentionally want to rerun a few already-parseable samples between close gaps to reduce process startup overhead.

A fresh provider-free preflight on May 17, 2026 at 15:05 America/New_York confirmed the same compact ranges and reported `key_state=missing` for the OpenRouter MiniMax route. No provider calls were made during that preflight.

## Recommended Execution

Run cells separately so a MiniMax failure does not hide which cell advanced:

### MiniMax-S / unimoral_moral_typology

```bash
UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_moral_typology' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `Use the dry-run command above to print the full 54-range list.`

### MiniMax-S / unimoral_factor_attribution

```bash
UNIMORAL_RERUN_UNPARSED_MAX_GAP=3 UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `0 304;308 387;393 604;608 619;623 626;630 834;838 857;861 1026;1031 1238;1242 2369;2373 2651;2656 3077;3081 3472;3476 3492`

### MiniMax-S / unimoral_consequence_generation

```bash
UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_consequence_generation' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `1120 1121`

### MiniMax-M / unimoral_factor_attribution

```bash
UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-M' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `1981 1982`

### MiniMax-M / unimoral_consequence_generation

```bash
UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-M' TASK_FILTER='unimoral_consequence_generation' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `1111 1112;1172 1173;1334 1335;1465 1466;1468 1476`

### MiniMax-L / unimoral_factor_attribution

```bash
UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-L' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
```

Range detail: `379 380;715 717;721 722;725 1750;2774 2775;2811 2812;2814 2817;2818 3492`

### MiniMax-L / unimoral_consequence_generation

```bash
UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='MiniMax-L' TASK_FILTER='unimoral_consequence_generation' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh
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
