# Family-Size Rerun Monitor Note

Snapshot time: April 22, 2026, 5:39 PM EDT  
Prepared during: automation monitoring pass

## Summary

This pass found a real orchestration problem in the watcher layer, fixed it, and then refreshed the public status after confirming newer live progress on the active text reruns.

At this snapshot:

- `Qwen-M`, `Qwen-L`, and `Llama-M` trace logs were still writing through about `5:19 PM ET`
- those latest trace tails still showed repeated `Model: generate ... enter/exit` activity plus fresh OpenRouter `200 OK` responses
- `Llama-M` still had no `job_done.txt`
- `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` still did not exist
- `Llama-M Denevil proxy` had advanced to `16,408 / 20,518` samples (`80.0%`) by `5:19 PM ET`
- the downstream launch path itself needed repair before it could be trusted for the next handoff

## Current Best Persisted Checkpoints

- `Qwen-M Denevil proxy`
  - `6,153 / 20,518` samples (`30.0%`)
  - last archive update: April 22, 2026, `4:47 PM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/2026-04-22T15-55-03-00-00_denevil-fulcra-proxy-generation_K73JcRxapGFA2KUirzF4mx.eval`
- `Qwen-L Denevil proxy`
  - `2,051 / 20,518` samples (`10.0%`)
  - last archive update: April 22, 2026, `4:42 PM ET`
  - source: `results/inspect/logs/2026-04-21-qwen-large-text-rerun-v1/qwen_32b_large/2026-04-22T18-43-26-00-00_denevil-fulcra-proxy-generation_4a4s8avJxQ5BWTK8KoMNxk.eval`
- `Llama-M Denevil proxy`
  - `16,408 / 20,518` samples (`80.0%`)
  - last archive update: April 22, 2026, `5:19 PM ET`
  - source: `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/2026-04-22T12-37-12-00-00_denevil-fulcra-proxy-generation_Q6QvJMTwVnLHjzU9UPvUra.eval`

The earlier fully persisted checkpoints still stood:

- `Qwen-M Value Prism Relevance`: `43,680 / 43,680` (`100.0%`) at `6:23 AM ET`
- `Qwen-M Value Prism Valence`: `21,840 / 21,840` (`100.0%`) at `10:48 AM ET`
- `Qwen-M CCD-Bench`: `2,182 / 2,182` (`100.0%`) at `11:55 AM ET`
- `Qwen-L Value Prism Relevance`: `43,680 / 43,680` (`100.0%`) at `9:10 AM ET`
- `Qwen-L Value Prism Valence`: `21,840 / 21,840` (`100.0%`) at `1:50 PM ET`
- `Qwen-L CCD-Bench`: `2,182 / 2,182` (`100.0%`) at `2:43 PM ET`
- `Llama-M Value Prism Relevance`: `43,680 / 43,680` (`100.0%`) at `3:54 AM ET`
- `Llama-M Value Prism Valence`: `21,840 / 21,840` (`100.0%`) at `7:53 AM ET`
- `Llama-M CCD-Bench`: `2,182 / 2,182` (`100.0%`) at `8:37 AM ET`

## Problem Found

The watcher layer had drifted into an unreliable state:

- multiple copies of the watcher scripts were running at once
- the on-disk `watcher.pid` files no longer matched a single authoritative live watcher
- the downstream launch path would have been harder to trust when `Llama-M` finally completed

This was an actual orchestration problem, not just stale cosmetic metadata.

## Fix Applied

This pass fixed the watcher layer directly:

- patched `results/inspect/full-runs/2026-04-21-next-text-launch-watch/watch_and_launch_llama_medium.sh`
- patched `results/inspect/full-runs/2026-04-21-deepseek-medium-launch-watch/watch_and_launch_deepseek_medium.sh`

The fix added:

- single-instance lock handling via a watcher lock directory plus `watcher.pid`
- explicit cleanup for lock and pid files on exit
- simpler target-running checks rather than the earlier more brittle inline polling path

After patching:

- all duplicate watcher processes were stopped
- the `DeepSeek-M` watcher was re-established as a single durable detached `screen` session: `cei-deepseek-watch`
- the repaired watcher now owns `results/inspect/full-runs/2026-04-21-deepseek-medium-launch-watch/watcher.pid`
- the `Llama-M` watcher was not left running, because `Llama-M` is already active and that earlier handoff phase is no longer needed

## Liveness Findings

Fresh trace evidence came from:

- `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-2747.log`
- `results/inspect/logs/2026-04-21-qwen-large-text-rerun-v1/qwen_32b_large/_inspect_traces/trace-53396.log`
- `results/inspect/logs/2026-04-21-llama-medium-text-v1/llama_70b_medium/_inspect_traces/trace-71026.log`

Those latest tails still showed successful OpenRouter traffic through about `5:19 PM ET`.

The repaired deepseek watcher was then confirmed live via:

- detached session: `screen -ls` -> `cei-deepseek-watch`
- live process owner: `bash results/inspect/full-runs/2026-04-21-deepseek-medium-launch-watch/watch_and_launch_deepseek_medium.sh`
- active pidfile: `results/inspect/full-runs/2026-04-21-deepseek-medium-launch-watch/watcher.pid`

## Operational Decision During This Pass

This pass still did not start a new downstream model run manually.

The correct gating reason remained:

- `Llama-M` is still actively running
- `Llama-M` still has not written `job_done.txt`
- `DeepSeek-M` should still be launched by the repaired watcher only after that clean completion marker exists

## Release Refresh During This Pass

This pass rebuilt the public release artifacts with:

- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`

That refresh updated:

- `CEI/README.md`
- `CEI/results/release/2026-04-19-option1/README.md`
- `CEI/results/release/2026-04-19-option1/jenny-group-report.md`
- `CEI/results/release/2026-04-19-option1/release-manifest.json`
- `CEI/results/release/2026-04-19-option1/family-size-progress.csv`
- `CEI/figures/release/option1_family_size_progress_overview.svg`

The refreshed public snapshot now shows:

- `Qwen-M Denevil proxy` at `30.0%`
- `Qwen-L Denevil proxy` at `10.0%`
- `Llama-M Denevil proxy` at `80.0%`
- live trace evidence through about `5:19 PM ET`
- watcher polling through about `5:37 PM ET`

This pass also re-verified:

- `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`

## Next Step

- keep monitoring until `Llama-M` writes `job_done.txt` or `DeepSeek-M` actually launches
- once `Llama-M` genuinely completes, confirm that the repaired watcher path creates the `DeepSeek-M` run directory and log it
- rebuild the release artifacts again after the next material persisted checkpoint or downstream launch lands

## Follow-up Pass: April 22, 2026, 6:03 PM EDT

This follow-up pass re-checked the live state after the watcher repair and refreshed the public snapshot again.

At this follow-up snapshot:

- `Qwen-M`, `Qwen-L`, and `Llama-M` trace logs were still actively writing through about `6:03 PM ET`
- those latest trace tails still showed fresh OpenRouter `200 OK` responses
- the repaired `DeepSeek-M` watcher was still live in detached `screen` session `cei-deepseek-watch`
- the repaired `DeepSeek-M` watcher log was still polling `llama_status medium=waiting` through about `6:01 PM ET`
- the earlier `Qwen -> Llama-M` handoff watcher had already exited cleanly at `5:37 PM ET` after logging `llama_70b_medium already_running; watcher_exit`
- `Llama-M` still had no `job_done.txt`
- `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` still did not exist
- no new persisted checkpoint had landed beyond the earlier `Qwen-M 30.0%`, `Qwen-L 10.0%`, and `Llama-M 80.0%` Denevil proxy archives
- this follow-up pass therefore did not start a new downstream model run

## Release Refresh During This Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, and `results/release/2026-04-19-option1/jenny-group-report.md` with live trace evidence through about `6:03 PM ET`
- corrected the public wording so only the saved master / worker PID markers remain described as stale; the repaired `DeepSeek-M` watcher is now described as live polling evidence instead

## Follow-up Pass: April 22, 2026, 7:03 PM EDT

This follow-up pass re-checked the same live reruns again after the earlier 6:03 PM snapshot and refreshed the public status because two Denevil proxy checkpoints materially advanced.

At this follow-up snapshot:

- `Qwen-M` trace logs were still actively writing through about `7:03 PM ET`
- `Qwen-L` trace logs were still actively writing through about `7:02 PM ET`
- `Llama-M` trace logs were still actively writing through about `7:03 PM ET`
- those latest trace tails still showed fresh OpenRouter `200 OK` responses on all three active reruns
- the repaired `DeepSeek-M` watcher log was still polling `llama_status medium=waiting` through about `7:01 PM ET`
- the earlier `Qwen -> Llama-M` handoff watcher still remained exited after its earlier `llama_70b_medium already_running; watcher_exit`
- `Llama-M` still had no `job_done.txt`
- `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` still did not exist
- this follow-up pass therefore still did not start a new downstream model run

The best persisted Denevil proxy checkpoints on disk now stand at:

- `Qwen-M Denevil proxy`: `8,204 / 20,518` samples (`40.0%`) at `6:44 PM ET`
- `Qwen-L Denevil proxy`: `2,051 / 20,518` samples (`10.0%`) at `4:42 PM ET`
- `Llama-M Denevil proxy`: `18,459 / 20,518` samples (`90.0%`) at `6:50 PM ET`

## Release Refresh During This 7:03 PM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, and `results/release/2026-04-19-option1/jenny-group-report.md` with live trace evidence through about `7:02-7:03 PM ET`
- refreshed the public Denevil checkpoint wording to `Qwen-M 40.0%`, `Qwen-L 10.0%`, and `Llama-M 90.0%`

## Follow-up Pass: April 22, 2026, 8:04 PM EDT

This follow-up pass re-checked the same live reruns again after the earlier 7:03 PM snapshot and refreshed the public status because the live trace condition changed materially even though the persisted checkpoints did not.

At this follow-up snapshot:

- `Qwen-M`, `Qwen-L`, and `Llama-M` trace logs still showed live Inspect writes through about `8:02 PM ET`
- the latest trace tails no longer showed fresh OpenRouter `200 OK` responses; all three active reruns were instead sitting in `APIConnectionError` retry backoff with a `30 minute` sleep window
- the saved master / worker PID markers still looked stale, but the `DeepSeek-M` handoff watcher log itself was still polling `llama_status medium=waiting` through about `8:03 PM ET`
- `Llama-M` still had no `job_done.txt`
- `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` still did not exist
- no new persisted Denevil proxy checkpoint had landed beyond `Qwen-M 40.0%`, `Qwen-L 10.0%`, and `Llama-M 90.0%`
- this follow-up pass therefore still did not start a new downstream model run

## Release Refresh During This 8:04 PM Follow-up Pass

- reran `python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, and `results/release/2026-04-19-option1/release-manifest.json`
- updated the public operations note so the live reruns are now described as trace writes in `connection-error retry backoff (30 minutes)` through about `8:02 PM ET`, with the watcher still polling through about `8:03 PM ET`

## Follow-up Pass: April 22, 2026, 9:07 PM EDT

This follow-up pass re-checked the same reruns again after the earlier 8:04 PM snapshot and found that the expected downstream handoff had already happened cleanly, so the public release text needed a real state-transition refresh rather than another pure liveness update.

At this follow-up snapshot:

- `Llama-M` full-run `master_status.txt` had flipped to `completed` at `8:40 PM ET`
- `Llama-M` now has `llama_70b_medium/job_done.txt`
- the repaired `DeepSeek-M` watcher log recorded `llama_status medium=done` at `8:42 PM ET`, then launched `deepseek_r1_qwen_32b_medium`, then exited cleanly
- `results/inspect/full-runs/2026-04-21-deepseek-medium-text-v1/` now exists and its `master_status.txt` is `running:deepseek_r1_qwen_32b_medium`
- fresh Inspect trace tails showed live OpenRouter `200 OK` responses through about `9:06 PM ET` for `Qwen-M`, `Qwen-L`, and `DeepSeek-M`
- the best persisted Denevil proxy checkpoints on disk had advanced to `10,255 / 20,518` samples (`50.0%`) for `Qwen-M` at `9:03 PM ET`, `4,102 / 20,518` samples (`20.0%`) for `Qwen-L` at `8:29 PM ET`, and `20,518 / 20,518` samples (`100.0%`) for `Llama-M` at `8:40 PM ET`
- `DeepSeek-M`'s first `UniMoral` attempt ended non-success after `55 / 8,784` samples at `8:47 PM ET`
- `DeepSeek-M` had already moved into `Value Prism Relevance`, with live traces but no persisted sample checkpoint on disk yet
- this follow-up pass therefore did not start a new downstream model run manually, because the repaired watcher had already launched the correct next run

## Release Refresh During This 9:07 PM Follow-up Pass

- patched `CEI/scripts/build_release_artifacts.py` so the release builder can detect `Llama-M` completion and `DeepSeek-M` launch from the on-disk run state instead of continuing to publish the stale queued wording
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, and `results/release/2026-04-19-option1/release-manifest.json`
- updated the public status tables so `Llama-M` is now marked complete, `DeepSeek-M` is now marked live, and the current operations note records the clean `Llama -> DeepSeek-M` handoff plus the current `DeepSeek-M` task-ledger caveat

## Follow-up Pass: April 22, 2026, 9:14 PM EDT

This follow-up pass re-checked the active reruns shortly after the 9:07 PM handoff refresh to see whether `DeepSeek-M` had written its first persisted downstream checkpoint or whether the public package needed another rebuild immediately.

At this follow-up snapshot:

- `Qwen-M` trace logs were still actively writing through about `9:14 PM ET` with fresh OpenRouter `200 OK` responses
- `Qwen-L` trace logs were still actively writing through about `9:14 PM ET` with fresh OpenRouter `200 OK` responses
- `DeepSeek-M` trace logs were still actively writing through about `9:14 PM ET` with fresh OpenRouter `200 OK` responses
- `DeepSeek-M` `master_status.txt` still showed `running:deepseek_r1_qwen_32b_medium`
- no new persisted `.eval` checkpoint had landed beyond the already-published `Qwen-M 50.0%`, `Qwen-L 20.0%`, and `Llama-M 100.0%` Denevil proxy archives
- `DeepSeek-M` still only had the earlier interrupted `UniMoral` archive plus the started `Value Prism Relevance` archive with no persisted sample checkpoint yet
- this follow-up pass therefore did not start any new downstream model run manually

## Release Refresh During This 9:14 PM Follow-up Pass

- did not rerun the public release builder this pass because no material persisted checkpoint changed after the 9:07 PM refresh
- kept the freshly rebuilt public README/report state from the earlier `Llama -> DeepSeek-M` handoff pass

## Follow-up Pass: April 22, 2026, 10:03 PM EDT

This follow-up pass re-checked the downstream state after the earlier 9:14 PM snapshot, found that the first `DeepSeek-M` attempt had already stopped non-success, and refreshed the public release package because the README/report still needed to describe that failure state accurately.

At this follow-up snapshot:

- `Qwen-M` trace logs still showed Inspect retry activity through about `10:02 PM ET`, but the latest tail was `APIConnectionError` retry backoff rather than a fresh OpenRouter `200 OK`
- `Qwen-L` trace logs still showed Inspect retry activity through about `10:02 PM ET`, but the latest tail was `APIConnectionError` retry backoff rather than a fresh OpenRouter `200 OK`
- `Llama-M` still remained the last cleanly completed text line, with `20,518 / 20,518` `Denevil` proxy samples (`100.0%`) persisted at `8:40 PM ET`
- `Qwen-M`'s saved `Denevil` proxy archive had advanced to `10,640 / 20,518` samples (`51.9%`) at `9:15 PM ET`, then ended with OpenRouter `403 Key limit exceeded (monthly limit)`
- `Qwen-L`'s saved `Denevil` proxy archive had advanced to `5,034 / 20,518` samples (`24.5%`) at `9:15 PM ET`, then ended with the same OpenRouter `403 Key limit exceeded (monthly limit)`
- `DeepSeek-M` top-level `master_status.txt` had flipped to `completed` at `9:15 PM ET`, but the job directory itself wrote `job_failed.txt`, so this was not a clean full-line completion
- `DeepSeek-M`'s first downstream attempt preserved `55 / 8,784` `UniMoral` action prediction samples (`0.6%`) at `8:47 PM ET`, then `999 / 43,680` `Value Prism Relevance` samples (`2.3%`) at `9:15 PM ET`, before later tasks hit the same OpenRouter monthly key-limit `403`
- this follow-up pass therefore did not start any new downstream model run manually

## Release Refresh During This 10:03 PM Follow-up Pass

- patched `CEI/scripts/build_release_artifacts.py` again so the release builder no longer marks a failed `DeepSeek-M` attempt as complete just because the run directory wrote a top-level `master_status.txt`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, and `results/release/2026-04-19-option1/release-manifest.json`
- updated the public status tables and operations note so `DeepSeek-M` is now reported as `Attempted local line / Partial`, the saved `Qwen-M` and `Qwen-L` `Denevil` archives are explicitly described as key-limit stops, and the queued-line note now says the next launches remain blocked on unresolved Qwen reruns plus an OpenRouter limit reset

## Follow-up Pass: April 22, 2026, 11:08 PM EDT

This follow-up pass re-checked the current chain after the earlier 10:03 PM snapshot, confirmed that no new clean downstream launch was available to start manually, and refreshed the public package again because the tracked README/report still did not reflect the newer `MiniMax-S` rerun state.

At this follow-up snapshot:

- `Qwen-M` trace logs still showed Inspect retry writes through about `11:02 PM ET`, but the latest tail remained `APIConnectionError` retry backoff rather than a fresh OpenRouter `200 OK`
- `Qwen-L` trace logs still showed Inspect retry writes through about `11:02 PM ET`, with the same connection-error retry-backoff condition rather than a fresh OpenRouter `200 OK`
- no new persisted `.eval` checkpoint landed for `Qwen-M`, `Qwen-L`, or `DeepSeek-M` beyond the earlier published `Qwen-M 51.9%`, `Qwen-L 24.5%`, `Llama-M 100.0%`, and `DeepSeek-M 2.3% Value Prism Relevance` checkpoints
- `Llama-M` still remained the last cleanly completed text line, with `job_done.txt` present and `20,518 / 20,518` `Denevil` proxy samples (`100.0%`) persisted at `8:40 PM ET`
- `DeepSeek-M` still remained a failed downstream attempt with `job_failed.txt`; this pass therefore did not start any further queued text line manually because the current handoff chain is blocked on the same OpenRouter limit / connectivity recovery
- a separate `MiniMax-S` rerun debug batch had already finished on disk under `results/inspect/full-runs/2026-04-22-minimax-small-rerun-debug/`
- that `MiniMax-S` rerun successfully completed both `SMID` tasks, finishing `smid_moral_rating` at `6:27 PM ET` and `smid_foundation_classification` at `8:39 PM ET`
- the same `MiniMax-S` text rerun preserved `5,478 / 8,784` `UniMoral` action prediction samples (`62.4%`) at `9:15 PM ET`, then later `Value Prism`, `CCD-Bench`, and `Denevil` text tasks stopped on OpenRouter monthly key-limit `403`
- this follow-up pass therefore did not start a new model run manually; it only refreshed the release builder and the public package so the current state is logged correctly

## Release Refresh During This 11:08 PM Follow-up Pass

- patched `CEI/scripts/build_release_artifacts.py` so the release builder now detects the `MiniMax-S` rerun artifacts, promotes `MiniMax-S` from pure `Error` to `Partial`, includes the recovered `SMID` metrics in the comparable snapshot, and updates the machine-readable manifest guardrails consistently
- patched `CEI/tests/test_release_artifacts.py` so the regression test now expects the refreshed `MiniMax-S` partial-rerun state and the added comparable `SMID` row
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/benchmark-comparison.csv`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/supplementary-model-progress.csv`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures

## Follow-up Pass: April 23, 2026, 12:08 AM EDT

This follow-up pass re-checked the chain after the 11:08 PM snapshot and found that the public package was now stale in a more concrete way: the Qwen reruns were no longer merely retrying, they had already exhausted their task lists and written finished run markers on disk.

At this follow-up snapshot:

- `Qwen-M` already had `qwen_14b_medium/job_done.txt` at `9:15:27 PM ET` on April 22, 2026
- `Qwen-M`'s final `denevil_fulcra_proxy_generation` task had exited non-success with recorded return code `2`, preserving `10,640 / 20,518` `Denevil` proxy samples (`51.9%`) at `9:15 PM ET`
- `Qwen-L` already had `qwen_32b_large/job_done.txt` at `9:15:29 PM ET` on April 22, 2026
- `Qwen-L`'s final `denevil_fulcra_proxy_generation` task had exited non-success with recorded return code `2`, preserving `5,034 / 20,518` `Denevil` proxy samples (`24.5%`) at `9:15 PM ET`
- `DeepSeek-M` still remained a failed downstream attempt with `job_failed.txt` at `9:15:47 PM ET`, after preserving `55 / 8,784` `UniMoral` action prediction samples (`0.6%`) and `999 / 43,680` `Value Prism Relevance` samples (`2.3%`)
- `Llama-M` still remained the last cleanly completed text line, with `job_done.txt` present and `20,518 / 20,518` `Denevil` proxy samples (`100.0%`) persisted at `8:40 PM ET`
- no active text rerun remained on disk at this point; the Qwen trace files were no longer authoritative liveness markers once the run directories had already written `job_done.txt`
- this follow-up pass therefore did not start a new model run manually, because the latest `Qwen-M`, `Qwen-L`, `DeepSeek-M`, and `MiniMax-S` task logs all end in the same OpenRouter monthly key-limit `403`, so a fresh queued launch would be expected to fail immediately

## Release Refresh During This 12:08 AM Follow-up Pass

- patched `CEI/scripts/build_release_artifacts.py` so the release builder now treats finished Qwen reruns with non-success final `Denevil` tasks as `Attempted local rerun / Partial` instead of continuing to publish them as live
- patched `CEI/tests/test_release_artifacts.py` so the regression test now expects the refreshed Qwen partial-state rows
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py --release-dir /tmp/cei-release-check --figure-dir /tmp/cei-figures-check`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures
- updated the public status tables and operations note so `Qwen-M` and `Qwen-L` are now published as finished partial reruns rather than live activity, `Llama-M` remains complete, `DeepSeek-M` remains partial, and the queue is now described as blocked on an OpenRouter limit reset rather than on still-running Qwen jobs

## Follow-up Pass: April 23, 2026, 12:30 AM EDT

This follow-up pass started after credits were added and re-checked whether the stalled text chain could be restarted cleanly rather than just republished as partial.

At this follow-up snapshot:

- the shell could now resolve `openrouter.ai` and `curl -I https://openrouter.ai/api/v1/models` returned `HTTP/2 200`
- the earlier live process list was still polluted by orphaned `Qwen-L` and `Llama-M` worker chains that were no longer reflected correctly in the release package
- those stale `Qwen-L` / `Llama-M` workers were killed first so the next restart would not race duplicate jobs against the same run trees
- an initial detached `nohup` retry path was not durable in this shell environment, so the clean rerun was relaunched instead in detached `screen` session `qwen_m_retry_20260423_0026`
- that relaunched `Qwen-M` against the correct existing run id `2026-04-21-qwen-medium-text-rerun-v1`
- the restarted job correctly skipped `UniMoral`, `Value Prism Relevance`, `Value Prism Valence`, and `CCD-Bench`, then resumed only `denevil_fulcra_proxy_generation`
- fresh trace evidence now comes from `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log`
- that live trace tail showed repeated `Model: generate ... enter/exit` events plus fresh OpenRouter `200 OK` responses through about `12:30 AM ET`
- `Qwen-M` remained actively running at snapshot time under live worker chain `46050 -> 46098 -> 46099`
- no new persisted `.eval` checkpoint had landed yet beyond the earlier published `10,640 / 20,518` `Denevil` proxy samples (`51.9%`) at `9:15 PM ET`, so this pass refreshed status wording but did not claim a newer saved checkpoint
- `Qwen-L` remained a stopped partial rerun, `DeepSeek-M` remained the earlier failed downstream attempt, and this pass intentionally did not start a second queued line while the revived `Qwen-M` rerun is still proving stable

## Release Refresh During This 12:30 AM Follow-up Pass

- patched `CEI/scripts/build_release_artifacts.py` so the release builder now recognizes a live rerun from an on-disk `worker.pid` + matching live process even when an older `job_done.txt` still exists in that run directory
- patched `CEI/scripts/build_release_artifacts.py` again so the queue note no longer describes `Qwen-M` as waiting for a future limit reset once the rerun is already back in flight
- patched `CEI/tests/test_release_artifacts.py` so the regression test now accepts either the earlier stopped-partial `Qwen-M` row or the newly revived live-rerun `Qwen-M` row, depending on real on-disk state
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so `Qwen-M` is now published as live again while `Qwen-L` remains partial

## Follow-up Pass: April 23, 2026, 1:05 AM EDT

This follow-up pass re-checked the restarted Qwen retry after the earlier 12:30 AM snapshot, fixed the stale run-marker issue that made the live state ambiguous, and refreshed the public package again with the newest on-disk evidence.

At this follow-up snapshot:

- `Qwen-M` trace logs were still actively writing through about `1:05 AM ET` with fresh OpenRouter `200 OK` responses
- the best persisted `Qwen-M Denevil proxy` archive still remained `10,640 / 20,518` samples (`51.9%`) at `9:15 PM ET` on April 22, 2026; no newer saved `.eval` checkpoint had landed yet
- the stored `Qwen-M` launcher pid files were already stale again in this sandboxed pass, so recent trace activity was the only trustworthy liveness signal
- `Qwen-L` no longer had comparable live evidence: its latest trace write was only about `12:22 AM ET`, its saved rerun remains partial, and its newest retry artifacts on disk were still zero-sample start-only `.eval` files rather than a new persisted checkpoint
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the `403` chain
- this follow-up pass therefore did not start a new queued model run manually, because the current live work is still `Qwen-M` and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 1:05 AM Follow-up Pass

- patched `CEI/scripts/family_size_text_expansion.sh` so a retry now clears stale `job_done.txt` / `job_failed.txt` markers before re-entering the task loop
- patched `CEI/scripts/build_release_artifacts.py` so the release builder can also treat very recent trace writes as live rerun evidence when `ps` / pid inspection is unavailable or stale
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures
- updated the public wording so `Qwen-M` stays published as the only live rerun, `Qwen-L` stays partial, `DeepSeek-M` stays partial, and the queued lines remain blocked behind the still-live `Qwen-M` retry rather than being launched prematurely

## Follow-up Pass: April 23, 2026, 2:02 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 1:05 AM snapshot, confirmed that it was still genuinely live rather than just carrying stale pid markers, and refreshed the public package again with the newer trace evidence.

At this follow-up snapshot:

- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `2:00 AM ET` with repeated OpenRouter `200 OK` responses
- the revived `Qwen-M` `Denevil` rerun had also started filling a new in-progress archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval`, which had reached `2,051 / 20,518` samples (`10.0%`) by about `1:22 AM ET`
- the earlier saved `Qwen-M` `Denevil` checkpoint still remained the best published persisted archive at `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026, so this pass did not claim a higher finished checkpoint yet
- `Qwen-L` still had no comparable live evidence beyond older trace writes around `12:22 AM ET`, and its saved rerun remains the same stopped partial line
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the prior `403` chain
- this follow-up pass therefore did not start a new queued model run manually, because the current live work is still `Qwen-M` and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 2:02 AM Follow-up Pass

- patched `CEI/scripts/build_release_artifacts.py` so the generated operations note no longer implies that the current monitoring pass was the one that restarted `Qwen-M`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `2:02 AM ET`

## Follow-up Pass: April 23, 2026, 4:01 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 2:02 AM snapshot, confirmed that it was still actively producing fresh provider responses, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `4:01 AM ET` with repeated OpenRouter `200 OK` responses
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` had reached `6,153 / 20,518` samples (`30.0%`) by about `3:56 AM ET`
- the earlier saved `Qwen-M` `Denevil` checkpoint still remained the best published persisted archive at `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026, so this pass still did not claim a higher finished checkpoint yet
- `Qwen-L` still had no comparable live evidence beyond older trace writes around `12:22 AM ET`, and its newer retry artifacts on disk still remained start-only zero-sample `.eval` files rather than a new persisted checkpoint
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the prior `403` chain
- this follow-up pass therefore did not start a new queued model run manually, because the current live work is still `Qwen-M` and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 4:01 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `4:01 AM ET`

## Follow-up Pass: April 23, 2026, 5:03 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 4:01 AM snapshot, confirmed that it was still actively producing fresh provider responses, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `5:03 AM ET` with repeated OpenRouter `200 OK` responses
- no newer saved `.eval` checkpoint had landed for the revived `Qwen-M` `Denevil` rerun beyond the in-progress archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval`, which still held `6,153 / 20,518` samples (`30.0%`) last updated around `3:56 AM ET`
- the best persisted `Qwen-M` `Denevil` archive on disk therefore still remained `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026
- `Qwen-L` still had no comparable live evidence beyond older trace writes around `12:22 AM ET`, and its newer retry artifacts on disk still remained start-only zero-sample `.eval` files rather than a new persisted checkpoint
- `DeepSeek-M` still remained the earlier failed downstream attempt with `job_failed.txt` and no newer persisted progress after the prior key-limit chain
- this follow-up pass therefore did not start a new queued model run manually, because `Qwen-M` is still the only active text rerun and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 5:03 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, and `results/release/2026-04-19-option1/jenny-group-report.md` so the public operations note now cites live `Qwen-M` evidence through about `5:03 AM ET`

## Follow-up Pass: April 23, 2026, 6:01 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 5:03 AM snapshot, confirmed that it was still actively producing fresh provider responses, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `6:01 AM ET` with repeated OpenRouter `200 OK` responses
- no newer saved `.eval` checkpoint had landed for the revived `Qwen-M` `Denevil` rerun beyond the in-progress archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval`, which still held `6,153 / 20,518` samples (`30.0%`) last updated around `3:56 AM ET`
- the best persisted `Qwen-M` `Denevil` archive on disk therefore still remained `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026
- `Qwen-L` still had no comparable live evidence beyond older trace writes around `12:22 AM ET`, and its newer retry artifacts on disk still remained start-only zero-sample `.eval` files rather than a new persisted checkpoint
- `DeepSeek-M` still remained the earlier failed downstream attempt with `job_failed.txt` and no newer persisted progress after the prior key-limit chain
- this follow-up pass therefore did not start a new queued model run manually, because `Qwen-M` is still the only active text rerun and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 6:01 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/family-size-progress.csv`, `results/release/2026-04-19-option1/benchmark-comparison.csv`, `results/release/2026-04-19-option1/supplementary-model-progress.csv`, `results/release/2026-04-19-option1/topline-summary.json`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `6:01 AM ET`

## Follow-up Pass: April 23, 2026, 7:02 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 6:01 AM snapshot, confirmed that it was still actively producing fresh provider responses, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `7:02 AM ET` with repeated OpenRouter `200 OK` responses
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` had reached `8,204 / 20,518` samples (`40.0%`) by about `6:35 AM ET`
- the earlier saved `Qwen-M` `Denevil` checkpoint still remained the best published persisted archive at `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026, so this pass still did not claim a higher finished checkpoint yet
- `Qwen-L` still had no comparable live evidence beyond retry-backoff trace writes around `12:22 AM ET`, and its newer retry artifacts on disk still remained start-only zero-sample `.eval` files rather than a new persisted checkpoint
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the prior `403` chain
- this follow-up pass therefore did not start a new queued model run manually, because the current live work is still `Qwen-M` and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 7:02 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `7:02 AM ET`

## Follow-up Pass: April 23, 2026, 8:02 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 7:02 AM snapshot, confirmed that it was still genuinely live in the detached retry session, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `8:01 AM ET` with repeated OpenRouter `200 OK` responses
- the latest wall clock check in this pass was `2026-04-23 08:02:11 EDT`, so the `Qwen-M` trace evidence was only seconds old at inspection time
- no newer saved `.eval` checkpoint had landed for the revived `Qwen-M` `Denevil` rerun beyond the in-progress archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval`, which still held `8,204 / 20,518` samples (`40.0%`) last updated around `6:35 AM ET`
- the best persisted `Qwen-M` `Denevil` archive on disk therefore still remained `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026
- `Qwen-L` still remained partial with no comparable newer persisted checkpoint, `DeepSeek-M` still remained the earlier failed downstream attempt, and this pass therefore did not start a new queued model run manually because `Qwen-M` is still the active text rerun

## Release Refresh During This 8:02 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `8:02 AM ET`

## Follow-up Pass: April 23, 2026, 9:01 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 8:02 AM snapshot, confirmed that it was still genuinely live in the detached retry session, and kept the queue parked because no clean completion or stall transition justified launching a different text line.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- the latest wall clock check in this pass was `2026-04-23 09:01:20 EDT`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `9:01 AM ET` with repeated OpenRouter `200 OK` responses only seconds before inspection
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` had advanced to `10,255 / 20,518` samples (`50.0%`) by about `9:01 AM ET`
- the earlier saved `Qwen-M` `Denevil` checkpoint still remained the best persisted archive on disk at `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026, so this pass still did not claim a higher finished checkpoint yet
- `Qwen-L` still had no comparable live evidence beyond older trace writes around `12:22 AM ET`, and its newer retry artifacts on disk still remained start-only zero-sample `.eval` files rather than a new persisted checkpoint
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the prior key-limit chain
- this follow-up pass therefore did not start a new queued model run manually, because `Qwen-M` is still the active text rerun and the next queue should not advance until that rerun actually stops or completes

## Release Refresh During This 9:01 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache python3 /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `9:02 AM ET`

## Follow-up Pass: April 23, 2026, 10:02 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 9:01 AM snapshot, confirmed that it was still genuinely live in the detached retry session, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- the latest wall clock check in this pass was `2026-04-23 10:02:10 EDT`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `10:01 AM ET` with repeated OpenRouter `200 OK` responses only seconds before inspection
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` still held `10,255 / 20,518` samples (`50.0%`) from the latest saved in-progress checkpoint
- the earlier saved `Qwen-M` `Denevil` checkpoint still remained the best persisted archive on disk at `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026, so this pass still did not claim a higher finished checkpoint yet
- `Qwen-L` still remained partial with no comparable newer persisted checkpoint, `DeepSeek-M` still remained the earlier failed downstream attempt, and this pass therefore did not start a new queued model run manually because `Qwen-M` is still the active text rerun

## Release Refresh During This 10:02 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache CEI/.venv/bin/python CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache CEI/.venv/bin/python -m pytest CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `10:02 AM ET`

## Follow-up Pass: April 23, 2026, 11:02 AM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 10:02 AM snapshot, confirmed that it was still genuinely live in the detached retry session, and refreshed the public package again because the published live-evidence window had moved materially.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- the latest wall clock check in this pass was `2026-04-23 11:02:35 EDT`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `11:02 AM ET` with repeated OpenRouter `200 OK` responses only seconds before inspection
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` still held `10,255 / 20,518` samples (`50.0%`) from the latest saved in-progress checkpoint
- the earlier saved `Qwen-M` `Denevil` checkpoint still remained the best persisted archive on disk at `10,640 / 20,518` samples (`51.9%`) from `9:15 PM ET` on April 22, 2026, so this pass still did not claim a higher finished checkpoint yet
- the saved `master.pid` and `worker.pid` markers for this rerun still looked stale in this sandboxed pass, so fresh trace writes remained the authoritative liveness signal
- `Qwen-L` still remained partial with no comparable newer persisted checkpoint, `DeepSeek-M` still remained the earlier failed downstream attempt, and this pass therefore did not start a new queued model run manually because `Qwen-M` is still the active text rerun

## Release Refresh During This 11:02 AM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `11:02 AM ET`

## Follow-up Pass: April 23, 2026, 12:02 PM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 11:02 AM snapshot, confirmed that it was still genuinely live in the detached retry session, and refreshed the public package again because the saved in-progress `Denevil` checkpoint had now advanced past the earlier published partial.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- the latest wall clock check in this pass was `2026-04-23 12:01:52 EDT`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `12:02 PM ET`, with the latest tail still showing fresh OpenRouter `200 OK` responses
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` had advanced to `12,306 / 20,518` samples (`60.0%`) by `11:58 AM ET`
- that in-progress `Qwen-M` archive now exceeds the earlier stopped partial archive `10,640 / 20,518` (`51.9%`) from `9:15 PM ET` on April 22, 2026, so the public release package needed a real checkpoint refresh rather than only a liveness timestamp refresh
- the saved `worker.pid` marker for this rerun still looked stale in this sandboxed pass, so the detached `screen` session plus fresh trace writes remained the authoritative liveness signals
- `Qwen-L` still remained partial with no comparable newer persisted checkpoint, and its latest trace evidence still only reached about `12:22 AM ET`
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the prior key-limit chain
- this follow-up pass therefore did not start a new queued model run manually because `Qwen-M` is still the active text rerun

## Release Refresh During This 12:02 PM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `12:02 PM ET` and the newer `60.0%` in-progress `Denevil` checkpoint

## Follow-up Pass: April 23, 2026, 1:03 PM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 12:02 PM snapshot, confirmed that it was still genuinely live in the detached retry session, and refreshed the public package again because the published live-evidence window had moved materially even though the latest persisted `Denevil` checkpoint had not advanced yet.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- the latest wall clock check in this pass was `2026-04-23 01:03:56 PM EDT`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `1:03 PM ET`, with the latest tail still showing fresh OpenRouter `200 OK` responses
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` still held `12,306 / 20,518` samples (`60.0%`) from the latest saved in-progress checkpoint at `11:58 AM ET`
- the saved `worker.pid` marker for this rerun still looked stale in this sandboxed pass, so the detached `screen` session plus fresh trace writes remained the authoritative liveness signals
- `Qwen-L` still remained partial with no comparable newer persisted checkpoint, and `DeepSeek-M` still remained the earlier failed downstream attempt
- this follow-up pass therefore did not start a new queued model run manually because `Qwen-M` is still the active text rerun and the downstream queue should not advance until that rerun actually stops or completes

## Release Refresh During This 1:03 PM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `1:03 PM ET` while the best saved in-progress `Denevil` checkpoint still remains `12,306 / 20,518` samples (`60.0%`) at `11:58 AM ET`

## Follow-up Pass: April 23, 2026, 2:02 PM EDT

This follow-up pass re-checked the restarted `Qwen-M` rerun after the earlier 1:03 PM snapshot, confirmed that it was still genuinely live in the detached retry session, and refreshed the public package again because the published live-evidence window had moved materially even though the latest persisted `Denevil` checkpoint still had not advanced yet.

At this follow-up snapshot:

- `screen -ls` still showed detached session `45130.qwen_m_retry_20260423_0026`
- the latest wall clock check in this pass was `2026-04-23 02:02:31 PM EDT`
- `Qwen-M` trace `results/inspect/logs/2026-04-21-qwen-medium-text-rerun-v1/qwen_14b_medium/_inspect_traces/trace-46099.log` was still writing through about `2:02 PM ET`, with the latest tail still showing fresh OpenRouter `200 OK` responses
- the revived in-progress `Qwen-M` `Denevil` archive `2026-04-23T04-25-21-00-00_denevil-fulcra-proxy-generation_buLyHdeN4AbwQDtcNwqG6u.eval` still held `12,306 / 20,518` samples (`60.0%`) from the latest saved in-progress checkpoint at `11:58 AM ET`
- `Qwen-L` still remained partial with no comparable newer persisted checkpoint, and its latest local trace evidence still only reached about `12:22 AM ET`
- `DeepSeek-M` still remained the earlier failed downstream attempt with no newer persisted progress after the prior key-limit chain
- this follow-up pass therefore did not start a new queued model run manually because `Qwen-M` is still the active text rerun and the downstream queue should not advance until that rerun actually stops or completes

## Release Refresh During This 2:02 PM Follow-up Pass

- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/scripts/build_release_artifacts.py`
- reran `PYTHONPYCACHEPREFIX=/tmp/pycache /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/.venv/bin/python -m pytest /Users/hanzhenzhu/Desktop/moral-psych-harness/CEI/tests/test_release_artifacts.py -q`
- refreshed `CEI/README.md`, `results/release/2026-04-19-option1/README.md`, `results/release/2026-04-19-option1/jenny-group-report.md`, `results/release/2026-04-19-option1/release-manifest.json`, and the regenerated release figures so the public note now cites live `Qwen-M` evidence through about `2:02 PM ET` while the best saved in-progress `Denevil` checkpoint still remains `12,306 / 20,518` samples (`60.0%`) at `11:58 AM ET`
