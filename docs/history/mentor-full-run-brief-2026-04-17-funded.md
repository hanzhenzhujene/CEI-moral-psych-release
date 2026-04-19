# Moral-Psych Full-Run Status Brief (Post-Credit Rerun)

Snapshot time: April 17, 2026, 19:55 EDT
Prepared for: research mentor update

## Executive Summary

After adding OpenRouter credits, I launched a clean rerun of the first formal `Option 1` moral-psych batch in the CEI Inspect harness.

This rerun is materially healthier than the earlier attempt:

- the prior `402 insufficient credits` failure mode is no longer appearing
- direct OpenRouter probe calls now succeed for Qwen, DeepSeek, and Gemma routes
- the rerun is actively writing fresh Inspect artifacts under a new funded-run directory
- multiple benchmark routes have now crossed buffered logging thresholds and are progressing normally
- the original free-tier Gemma lane was later diagnosed as an OpenRouter rate-limit stall rather than a harness bug
- Gemma has now been recovered onto the paid `google/gemma-3-4b-it` route in a fresh namespace

## What Changed Since the Earlier Full-Run Attempt

Earlier on April 17, 2026, the original full batch failed because the OpenRouter account attached to the configured API key returned `402` account-credit errors.

After credits were added, I did the following:

- terminated stale pre-credit processes so they would not consume the newly added credits
- preserved the old failed run directory for auditability
- launched a clean rerun into a new run namespace: `2026-04-17-option1-full-funded`
- after diagnosing the Gemma stall, launched a separate paid Gemma recovery namespace: `2026-04-17-option1-full-funded-gemma-paid-v2`

## Post-Credit Provider Check

I verified the updated OpenRouter account state with direct API probes before relying on the full rerun:

- `qwen/qwen3-8b` -> `OK`
- `deepseek/deepseek-chat-v3.1` -> `OK`
- `google/gemma-3-4b-it:free` -> `OK`

Interpretation:

- credits are now active enough for direct model calls
- the previous `402` blocker has been resolved at the provider/account layer

## Current Funded Rerun Scope

Families in the active rerun:

- `qwen_text`
- `deepseek_text`
- `gemma_text`
- `qwen_smid`
- `gemma_smid`

The original funded namespace remains the main record for the Qwen and DeepSeek families.

Gemma should now be interpreted through the paid recovery namespace rather than the earlier free-tier namespace, because the earlier Gemma traces were stuck in repeated OpenRouter retries and the old `.eval` snapshots are no longer the authoritative view of live Gemma progress.

## Live Status Snapshot

As of April 17, 2026, 19:55 EDT:

Main funded namespace `2026-04-17-option1-full-funded`:

| Family | Task | Status | Progress | Notes |
| --- | --- | --- | ---: | --- |
| DeepSeek text | `unimoral_action_prediction` | success | `8784 / 8784` (`100.0%`) | Completed successfully |
| DeepSeek text | `value_prism_relevance` | success | `43680 / 43680` (`100.0%`) | Completed successfully |
| DeepSeek text | `value_prism_valence` | running | `8736 / 21840` (`40.0%`) | Progressing normally |
| Qwen text | `unimoral_action_prediction` | success | `8784 / 8784` (`100.0%`) | Completed successfully |
| Qwen text | `value_prism_relevance` | running | `8736 / 43680` (`20.0%`) | Progressing normally |
| Qwen vision | `smid_moral_rating` | success | `2941 / 2941` (`100.0%`) | Completed successfully |
| Qwen vision | `smid_foundation_classification` | success | `2941 / 2941` (`100.0%`) | Completed successfully |

Paid Gemma recovery namespace `2026-04-17-option1-full-funded-gemma-paid-v2`:

| Family | Task | Status | Progress | Notes |
| --- | --- | --- | ---: | --- |
| Gemma text | `unimoral_action_prediction` | success | `8784 / 8784` (`100.0%`) | Completed successfully after relaunch on paid Gemma |
| Gemma text | `value_prism_relevance` | running | `4368 / 43680` (`10.0%`) | Progressing on the paid route |
| Gemma vision | `smid_moral_rating` | success | `2941 / 2941` (`100.0%`) | Completed successfully after relaunch on paid Gemma |
| Gemma vision | `smid_foundation_classification` | running | `0 / 2941` visible so far | Active on the paid route; still below first flush threshold |

## Gemma Diagnosis And Recovery

The earlier Gemma stall was traced to the OpenRouter free-tier route rather than to the CEI harness itself.

What the Inspect trace logs showed:

- repeated `HTTP 429 Too Many Requests` responses on `openrouter/google/gemma-3-4b-it:free`
- explicit OpenRouter error messages including `free-models-per-day-high-balance` and `free-models-per-min`
- `X-RateLimit-Remaining: 0` on the free route
- an automatic Inspect backoff of `1800` seconds between retries

Interpretation:

- the free Gemma route had exhausted its available quota
- the jobs looked superficially "running" because Inspect was sleeping and retrying
- this was a provider/quota issue, not a task-definition or model-format issue

Recovery steps taken on April 17, 2026:

- stopped the stalled free-route Gemma runners
- confirmed that `openrouter/google/gemma-3-4b-it` succeeds through the same OpenAI-compatible client path used by Inspect
- confirmed that the paid Gemma route also accepts the SMID image input format
- relaunched Gemma into `2026-04-17-option1-full-funded-gemma-paid-v2`
- reduced Gemma concurrency for the recovery launch:
  - text `max_connections=4`
  - vision `max_connections=1`

Recovery result so far:

- the paid Gemma traces now show repeated `HTTP 200 OK` responses instead of `429`s
- Gemma text has completed `UniMoral` and advanced into `ValuePrism relevance`
- Gemma vision has completed `SMID moral rating` and advanced into `SMID foundation classification`

## Important Monitoring Note

The Inspect logs for these tasks are buffered. That means progress is not written sample-by-sample for every task.

For this rerun:

- `SMID` is configured with a logging buffer of roughly `294` samples
- `UniMoral action` is configured with a logging buffer of roughly `878` samples

As a result, a task can be genuinely running while still showing `0` completed samples in the `.eval` snapshot until it reaches its first flush boundary.

This is why a task can remain at `0` completed samples in the `.eval` snapshot even while it is genuinely active.

For Gemma specifically, there are now two separate interpretations:

- in the older free-tier namespace, a `0` snapshot was eventually shown to be a misleading symptom of quota exhaustion plus long retry backoff
- in the newer paid recovery namespace, a `0` snapshot can still simply mean the task has not crossed its first flush threshold yet

## Operational Interpretation

What this funded rerun now demonstrates:

- the OpenRouter credit issue has been addressed
- the funded rerun launched cleanly
- the harness is producing fresh post-credit artifacts
- the Qwen and DeepSeek families are progressing normally through later text tasks
- the Qwen vision family has completed both SMID tasks
- the Gemma failure mode has been diagnosed concretely at the provider/quota layer
- the paid Gemma recovery route is working and has already completed one text task plus one vision task

What is not yet demonstrated at this exact snapshot:

- full completion of any family
- later-task completion for the recovered paid Gemma family
- downstream tasks after the current `ValuePrism relevance` / `SMID foundation classification` stage
- a benchmark-faithful `Denevil` launch, because the local `data/denevil` directory currently contains FULCRA-style dialogue data rather than the MoralPrompt export expected by the harness

## Artifacts

Funded rerun progress snapshot:

- `results/inspect/full-runs/2026-04-17-option1-full-funded/progress-summary.csv`
- `results/inspect/full-runs/2026-04-17-option1-full-funded/progress-summary.md`

Paid Gemma recovery progress snapshot:

- `results/inspect/full-runs/2026-04-17-option1-full-funded-gemma-paid-v2/progress-summary.csv`
- `results/inspect/full-runs/2026-04-17-option1-full-funded-gemma-paid-v2/progress-summary.md`

Funded rerun raw outputs:

- `results/inspect/full-runs/2026-04-17-option1-full-funded/`

Funded rerun Inspect logs:

- `results/inspect/logs/2026-04-17-option1-full-funded/`

Paid Gemma recovery Inspect logs:

- `results/inspect/logs/2026-04-17-option1-full-funded-gemma-paid-v2/`

Reusable progress summarizer:

- `scripts/summarize_inspect_eval_progress.py`

Denevil dataset compatibility check:

- `results/inspect/full-runs/2026-04-17-option1-full-funded/denevil-dataset-check.txt`

Earlier pre-credit failure brief:

- `docs/history/mentor-full-run-brief-2026-04-17.md`

## Immediate Next Step

The current best next step is to continue monitoring the Qwen and DeepSeek main funded families plus the paid Gemma recovery family as they advance through `ValuePrism` and `SMID foundation classification`, while keeping the old free-tier Gemma namespace only as an audit trail of the diagnosed provider-rate-limit stall.
