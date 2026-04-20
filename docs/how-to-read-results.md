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

## Reporting Rules Used Here

- `Qwen`, `DeepSeek`, and `Gemma` are inside the frozen `Option 1` snapshot.
- `Llama-S` is complete locally, but it is still outside the frozen snapshot counts.
- `MiniMax-S` has a formal attempt on disk, but the current run failed and should not be reported as complete.
- `Denevil` should be reported as `proxy` unless a real local `MoralPrompt` export becomes available and `denevil_generation` is rerun.

## Short Version

If you only need one sentence:

> The repo shows one closed public snapshot plus a larger in-progress matrix, and it clearly marks which lines are complete, which are proxy-only, and which still need reruns.
