# How To Read The Results

This repo uses a few status words repeatedly. This page explains them in plain language.

## Core Ideas

- `Frozen snapshot`: the public result package we are treating as closed and stable for reporting. In this repo, that is `Option 1` from `April 19, 2026`.
- `Local expansion run`: a newer or larger run that exists locally but is not yet folded into the frozen public snapshot.
- `Paper setup`: the benchmark line follows the same intended task setup as the paper we are testing.
- `Proxy`: the benchmark line is useful, but it does not use the paper's original setup exactly. In this repo, `Denevil` is currently proxy-only because the original `MoralPrompt` export is not available locally.

## Progress Table Labels

- `done`: this benchmark line finished and the result is usable
- `proxy`: this line finished, but only with a substitute setup rather than the paper's original setup
- `live`: this line is running right now
- `error`: this line was attempted, but the current result should not be treated as complete
- `queue`: this line is approved and waiting to run
- `tbd`: the model route or size slot has not been finalized yet
- `-`: this line is not planned right now

## Tier Labels

The generated dashboard `results/release/2026-04-19-option1/readiness-tier-matrix.csv` uses result-readiness tiers:

- `Tier 1`: harness completed
- `Tier 2`: result is valid
- `Tier 3`: result is interpretable and ready for comparison within the stated metric layer

Blocked, not-run, route-gap, and data-gap cells are not assigned a tier. They are listed with separate status fields.

The dashboard is a public summary at `model_line x benchmark`. The canonical internal unit is lower level: `model_id / provider_route / size_slot x benchmark x subtask_or_RQ x metric_layer x sample_set`. A tier is not a model score, not a model-family score, and not a benchmark-only label.

These tiers are paired with metric layers. Tier 3 CCD-Bench is still choice-distribution behavior, not accuracy, and Tier 3 DeNEVIL in this release is proxy behavior/provenance, not paper-faithful MoralPrompt scoring.

## Reporting Rules Used Here

- `Qwen`, `DeepSeek`, and `Gemma` are inside the frozen `Option 1` snapshot.
- `Llama-S` is complete locally, but it is still outside the frozen snapshot counts.
- `MiniMax-S` is complete in the current generated release tables via the direct MiniMax-M2.1 text rerun plus the MiniMax-01 SMID recovery route.
- `MiniMax-M` has text results but no medium SMID route yet, so it should not be described as a full five-benchmark comparison line.
- `Denevil` should be reported as `proxy` unless a real local `MoralPrompt` export becomes available and `denevil_generation` is rerun.

## Short Version

If you only need one sentence:

> The repo shows one closed public snapshot plus a larger in-progress matrix, and it clearly marks which lines are complete, which are proxy-only, and which still need reruns.
