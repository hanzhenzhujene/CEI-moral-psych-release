# Family-Size Rerun Monitor Note

Snapshot time: April 22, 2026, 11:05 EDT  
Prepared during: automation monitoring pass

## Summary

This pass found real continued progress on all three live text reruns, but still not a clean downstream handoff point.

At this snapshot:

- `Qwen-M`, `Qwen-L`, and `Llama-M` Inspect trace logs were still actively writing through about `11:04 AM ET`
- those trace tails still showed repeated `Model: generate ... enter/exit` activity plus fresh OpenRouter `200 OK` responses
- the handoff watcher logs were still polling through about `11:03 AM ET`
- the watcher state still remained `qwen_status medium=waiting large=waiting` and `llama_status medium=waiting`
- `Llama-M` still had no `job_done.txt`
- no `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` directory existed yet
- this pass therefore did not start a new downstream model run

The current best persisted checkpoints on disk were:

- `Qwen-M Value Prism Relevance`
  - `43,680 / 43,680` samples (`100.0%`)
  - last archive update: April 22, 2026, `6:23 AM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/2026-04-22T02-31-09-00-00_value-prism-relevance_cLye7qhYMBoDtYr8srZooZ.eval`
- `Qwen-M Value Prism Valence`
  - `21,840 / 21,840` samples (`100.0%`)
  - last archive update: April 22, 2026, `10:48 AM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/2026-04-22T10-23-14-00-00_value-prism-valence_nGfSSMUFufbXfH8o4xkLFA.eval`
- `Qwen-M CCD-Bench`
  - `436 / 2,182` samples (`20.0%`)
  - last archive update: April 22, 2026, `11:01 AM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/2026-04-22T14-48-23-00-00_ccd-bench-selection_eF9BHqER6GWnqBXt9mcXPR.eval`
- `Qwen-L Value Prism Relevance`
  - `43,680 / 43,680` samples (`100.0%`)
  - last archive update: April 22, 2026, `9:10 AM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-large-text-rerun-v1/qwen_32b_large/2026-04-22T02-08-20-00-00_value-prism-relevance_T9Rhe6tbcx7jVePrjMD84e.eval`
- `Qwen-L Value Prism Valence`
  - `4,368 / 21,840` samples (`20.0%`)
  - last archive update: April 22, 2026, `10:47 AM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-large-text-rerun-v1/qwen_32b_large/2026-04-22T13-10-57-00-00_value-prism-valence_DeWKbs9wKV9W94MfTimfgw.eval`
- `Llama-M Value Prism Relevance`
  - `43,680 / 43,680` samples (`100.0%`)
  - last archive update: April 22, 2026, `3:54 AM ET`
  - source: `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/2026-04-22T03-20-26-00-00_value-prism-relevance_53p55q9CgT3nMqwgWDaT3G.eval`
- `Llama-M Value Prism Valence`
  - `21,840 / 21,840` samples (`100.0%`)
  - last archive update: April 22, 2026, `7:53 AM ET`
  - source: `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/2026-04-22T07-54-53-00-00_value-prism-valence_Mh2PtrLZVKcpnc7yQVCuHe.eval`
- `Llama-M CCD-Bench`
  - `2,182 / 2,182` samples (`100.0%`)
  - last archive update: April 22, 2026, `8:37 AM ET`
  - source: `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/2026-04-22T11-53-03-00-00_ccd-bench-selection_iAvQYCyPEkGEqnYpGhy4r4.eval`
- `Llama-M Denevil proxy`
  - `4,102 / 20,518` samples (`20.0%`)
  - last archive update: April 22, 2026, `10:59 AM ET`
  - source: `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/2026-04-22T12-37-12-00-00_denevil-fulcra-proxy-generation_Q6QvJMTwVnLHjzU9UPvUra.eval`

## Liveness Findings

This pass again treated the saved PID marker files as unreliable and used live trace / watcher writes instead.

Fresh live evidence came from:

- `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-88327.log`
- `results/inspect/logs/2026-04-21-qwen-large-text-rerun-v1/qwen_32b_large/_inspect_traces/trace-73721.log`
- `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/_inspect_traces/trace-71026.log`

Those trace tails were still writing through about `11:04 AM ET` and still showed successful OpenRouter traffic.

The handoff watcher logs also continued moving through about `11:03 AM ET`:

- `results/inspect/full-runs/2026-04-21-next-text-launch-watch/watcher.log`
- `results/inspect/full-runs/2026-04-21-deepseek-medium-launch-watch/watcher.log`

Their latest entries still reported:

- `qwen_status medium=waiting large=waiting`
- `llama_status medium=waiting`

That watcher state remained correct rather than contradictory:

- `results/inspect/full-runs/2026-04-21-llama-medium-text-v1/llama_70b_medium/job_done.txt` was still absent
- `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` still did not exist

## Operational Decision During This Monitoring Pass

This pass did not start a new downstream model run.

The gating reason remained:

- `Llama-M` was still actively running
- `Llama-M` had persisted a real `Denevil` checkpoint at `20.0%`, but it still had not written `job_done.txt`
- the chained DeepSeek watcher therefore still had no clean completion signal to act on

## Release Refresh During This Pass

This pass updated the live release builder so the generated public status pages now explicitly surface:

- `Qwen-M` moving past `Value Prism Valence` and into a live `CCD-Bench` archive
- `Qwen-L` at a live `20.0%` persisted `Value Prism Valence` checkpoint
- `Llama-M` at a live `20.0%` persisted `Denevil` proxy checkpoint

The builder change was made in:

- `CEI/scripts/build_release_artifacts.py`

After that change, this pass rebuilt the tracked public artifacts with:

- `python3 scripts/build_release_artifacts.py`

That refresh propagated the current live monitor snapshot into:

- `CEI/README.md`
- `CEI/results/release/2026-04-19-option1/README.md`
- `CEI/results/release/2026-04-19-option1/jenny-group-report.md`
- `CEI/results/release/2026-04-19-option1/family-size-progress.csv`
- `CEI/results/release/2026-04-19-option1/release-manifest.json`
- `CEI/figures/release/option1_family_size_progress_overview.svg`

This pass also verified the release artifact test with:

- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m pytest CEI/tests/test_release_artifacts.py -q`

## Next Step

- keep monitoring until `Llama-M` writes `job_done.txt` or `DeepSeek-M` actually launches
- once `Llama-M` genuinely completes, confirm that the watcher path creates the `DeepSeek-M` run directory and log it
- rebuild the release artifacts again after the next material persisted checkpoint or downstream launch lands
