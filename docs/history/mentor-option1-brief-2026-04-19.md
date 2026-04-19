# Moral-Psych Option 1 Status Brief

Snapshot time: April 19, 2026, 07:46 EDT  
Prepared for: research mentor update

## Executive Summary

Jenny's current CEI deliverable now has a clean authoritative status layer across the fragmented run namespaces.

As of April 19, 2026:

- the current CEI `Option 1` slice is now authoritatively complete
- all authoritative `Qwen`, `DeepSeek`, and `Gemma` lines in this slice are complete
- the final `Qwen` and `DeepSeek` `Denevil` proxy recoveries have closed successfully
- the current package now lands at `19 / 19` authoritative tasks complete

This means the current run package is now strong enough for a clean closed-slice mentor update, with a clear description of what is done and what is still out of scope relative to the April 14 plan.

The package is now stronger than the earlier draft because it also separates:

- authoritative flushed benchmark status
- live recovery heartbeat history from the last active `Denevil` monitoring window

## What This Deliverable Covers

This brief reflects the current CEI `Option 1` moral-psych slice that Jenny actually ran in this workspace.

That slice currently includes:

- `UniMoral`
  - `unimoral_action_prediction`
- `SMID`
  - `smid_moral_rating`
  - `smid_foundation_classification`
- `Value Kaleidoscope`
  - `value_prism_relevance`
  - `value_prism_valence`
- `CCD-Bench`
  - `ccd_bench_selection`
- `Denevil`
  - currently represented by the explicit `FULCRA`-backed proxy task `denevil_fulcra_proxy_generation`

## How This Relates To The April 14 Meeting Plan

The April 14, 2026 meeting notes set a broader goal:

- use temperature `0`
- run the assigned moral-psych benchmarks in Eric's CEI harness
- compare agreed model families including `Qwen`, `Minimax`, `DeepSeek`, `Colombo`, and `Gemma`
- use `large`, `medium`, and `small` sizes within each family where possible

The current workspace deliverable does **not** yet cover that full matrix.

What has been completed so far is the first robust formal slice:

- one `Qwen` route
- one `DeepSeek` route
- one `Gemma` route
- the `Option 1` task subset above

No formal `Minimax` or `Colombo` run artifacts are present in the current CEI results tree. The only `Minimax` artifact visible locally is an earlier smoke output, not a formal full run.

## Current Authoritative Status

The authoritative cross-namespace status table is here:

- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.csv`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.md`

The companion live-monitoring view is here:

- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/live-heartbeat.csv`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/live-heartbeat.md`

At the current snapshot:

- authoritative tasks tracked: `19`
- authoritative successes: `19`
- authoritative active tasks: `0`
- authoritative errors: `0`

### Benchmark-Line View

| Model Family | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil |
| --- | --- | --- | --- | --- | --- |
| `Qwen` | success | success | success | success | success (`proxy`) |
| `DeepSeek` | success | not in current scope | success | success | success (`proxy`) |
| `Gemma` | success | success | success | success | success (`proxy`) |

Interpretation:

- `Qwen` now has every non-Denevil `Option 1` task completed after the recovery namespace fixed the earlier April 18, 2026 `402` credit interruption.
- `DeepSeek` has completed every non-Denevil task that was part of this slice.
- `Gemma` is fully complete for the current slice, including the `Denevil` proxy line.
- `Qwen` and `DeepSeek` have also now completed the `Denevil` proxy recovery line, closing the current `Option 1` slice.

## Recovery Closure Note

During active monitoring earlier on April 19, 2026, the two `Denevil` recoveries were still showing older flushed archive counts while their traces were healthy.

That ambiguity has now been resolved.

Direct inspection of the authoritative `.eval` archives now shows:

- `Qwen`
  - `20518 / 20518`
  - status refreshed to `success`
- `DeepSeek`
  - `20518 / 20518`
  - status refreshed to `success`

Interpretation:

- the recoveries were not stalled
- the old `59.98%` state was a stale summary artifact, not the true final outcome
- the recovery namespace summary has now been refreshed from the completed `.eval` archives

## Which Namespaces Are Authoritative

The results are split across multiple namespaces because the work had to be recovered in stages.

These are the namespaces that now matter:

- `2026-04-17-option1-full-funded`
  - authoritative for `DeepSeek` text tasks
  - authoritative for `Qwen` `unimoral_action_prediction`
  - authoritative for `Qwen` `value_prism_relevance`
  - authoritative for `Qwen` `SMID`
- `2026-04-17-option1-full-funded-gemma-paid-v2`
  - authoritative for all current `Gemma` text and `Gemma` `SMID` tasks
  - supersedes the earlier free-tier `Gemma` namespace
- `2026-04-18-option1-full-funded-qwen-recovery-v1`
  - authoritative for recovered `Qwen` `value_prism_valence`
  - authoritative for recovered `Qwen` `ccd_bench_selection`
- `2026-04-18-denevil-fulcra-proxy-formal-v3`
  - authoritative for `Gemma` `Denevil` proxy success
- `2026-04-18-denevil-fulcra-proxy-recovery-v1`
  - authoritative for the completed `Qwen` and `DeepSeek` `Denevil` proxy recovery jobs

Namespaces that should now be treated as audit history rather than live truth:

- the original pre-credit and mid-failure run directories
- the stalled free-tier `Gemma` artifacts
- the older `Denevil formal` attempts that were superseded by recovery runs

## Denevil Caveat

The `Denevil` line is still the biggest methodological caveat in the current package.

What is true:

- the harness path is implemented and working
- a reproducible `FULCRA`-backed proxy task exists
- `Gemma` has completed that proxy line
- `Qwen` and `DeepSeek` have now also completed that same proxy line

What is **not** true:

- this is not yet a benchmark-faithful reproduction of the paper's `MoralPrompt` evaluation setup

Current blocker:

- the local workspace does not have a public `MoralPrompt` export in the format expected by `denevil_generation`

So the correct reporting language is:

- "`Denevil` is currently represented by a `FULCRA`-backed proxy generation task."

The incorrect reporting language would be:

- "we fully reproduced the paper-faithful `MoralPrompt` benchmark"

## Reliability Notes

The current package is much more reliable than the earlier April 17, 2026 state for three reasons:

- OpenRouter credit failures were explicitly separated from clean reruns rather than being mixed into one namespace
- the free-tier `Gemma` stall was diagnosed as a provider-rate-limit problem and recovered onto the paid route
- `Qwen` post-credit recovery tasks were rerun in a dedicated recovery namespace instead of reusing partial failed artifacts

This means the authoritative summary now has a clear rule:

- choose the clean successful namespace when it exists
- choose the later recovery namespace when it supersedes an earlier provider-failure attempt

## Current Remaining Work

There is no remaining authoritative run work inside the current `Option 1` slice.

The slice is now closed at `19 / 19` authoritative tasks complete.

## Recommended Next Steps

Important follow-up steps after the current slice closes:

1. Decide whether the paper requires a benchmark-faithful `Denevil` result. If yes, obtain a real `MoralPrompt` export and run `denevil_generation`.
2. Expand beyond the current first slice into the broader April 14 plan:
   - formal `Minimax` runs
   - formal `Colombo` runs
   - size-tier sweeps (`large`, `medium`, `small`) where available
3. Freeze the final model roster and naming convention for the full comparison matrix before scaling further.
4. Use the authoritative summary machinery added here as the source of truth instead of hand-tracking multiple namespaces.

## Suggested Mentor Wording

One safe concise way to report this package is:

> We have now closed the CEI moral-psych `Option 1` slice at `19 / 19` authoritative tasks complete across `Qwen`, `DeepSeek`, and `Gemma`. This includes the current `FULCRA`-backed `Denevil` proxy line for all three model routes. We should still label `Denevil` as a proxy rather than a benchmark-faithful `MoralPrompt` reproduction, and the next methodological decision is whether to obtain a true `MoralPrompt` export before scaling to additional model families and size tiers.

## Key Artifacts

Master authoritative status package:

- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.csv`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.md`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/live-heartbeat.csv`
- `results/inspect/full-runs/2026-04-19-option1-authoritative-status/live-heartbeat.md`

Current `Qwen` recovery summary:

- `results/inspect/full-runs/2026-04-18-option1-full-funded-qwen-recovery-v1/progress-summary.csv`

Current `Denevil` recovery summary:

- `results/inspect/full-runs/2026-04-18-denevil-fulcra-proxy-recovery-v1/progress-summary.csv`

Earlier funded status brief:

- `docs/history/mentor-full-run-brief-2026-04-17-funded.md`

Earlier `Denevil` proxy note:

- `docs/history/mentor-denevil-proxy-brief-2026-04-18.md`
