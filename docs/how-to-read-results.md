# How To Read The Results

This repo uses a few status words repeatedly. This page explains them in plain language.

## Core Ideas

- `Frozen snapshot`: the public result package we are treating as closed and stable for reporting. In this repo, that is `Option 1` from `April 19, 2026`.
- `Text-reference row`: a completed text-only reference row, such as the OpenAI rows, that is promoted into text-capable result tables but intentionally has no SMID or DeNEVIL coverage.
- `Selected-grid follow-up`: the separate OpenRouter text-only follow-up under `results/openrouter-selected-grid-moral-psych-full/`. It has terminal states for all planned model-task rows, but blocked/provider rows stay outside scored summaries.
- `Exploratory sweep`: an older or smaller follow-up sweep kept outside the frozen release matrix and read as supporting context rather than the main ranking surface.
- `Paper setup`: the benchmark line follows the same intended task setup as the paper we are testing.
- `Proxy`: the benchmark line is useful, but it does not use the paper's original setup exactly. In this repo, `Denevil` is currently proxy-only because the original `MoralPrompt` export is not available locally.

## Result Packages

| Package | Where it lives | What to use it for | Boundary |
| --- | --- | --- | --- |
| Frozen Option 1 release | `results/release/2026-04-19-option1/` | Main public tables, figures, readiness tiers, and release report. | Closed snapshot; do not treat every later follow-up as part of its counts. |
| OpenAI text-reference rows | `docs/openai-reference-runs.md` and benchmark-specific release CSVs | Text-only OpenAI comparison context, including promoted GPT-5.5. | No SMID, no DeNEVIL, and not paper-model calibration. |
| OpenRouter selected-grid follow-up | `results/openrouter-selected-grid-moral-psych-full/` | Text-only scaling/time-scaling readout across UniMoral, ValuePrism, and CCD-Bench. | Separate from the frozen ranking surface; excludes SMID, DeNEVIL, and MiniMax. |
| Exploratory follow-up sweep | `results/exploratory/2026-05-13-additional-model-sweep/` | Supporting older/smaller route context. | Not the headline release matrix. |

## Visual Reading Order

For a presentation, deck, or reviewer skim, open [`figures/README.md`](../figures/README.md) first. It gives the ordered figure list and separates audience-facing visuals from appendix/provenance visuals.

| Question | Open first | Boundary |
| --- | --- | --- |
| What is the main task-specific moral-reasoning result? | `figures/release/option1_unimoral_family_scaling.svg` | Read UniMoral RQ1-RQ4 separately; do not collapse them into one score. |
| Which text classification rows are strongest? | `figures/release/option1_unimoral_task_heatmap.svg` | RQ1-RQ3 are exact-match accuracy only. |
| Which model is strongest on consequence generation? | `figures/release/option1_unimoral_generation_quality.svg` | RQ4 uses BERTScore F1 and METEOR, not accuracy. |
| Where is the visual-moral bottleneck? | `figures/release/option1_benchmark_accuracy_bars.svg` and `figures/release/option1_benchmark_difficulty_profile.svg` | SMID and Value are comparable accuracy panels; UniMoral has its own RQ block. |
| What does CCD-Bench show? | `figures/release/option1_ccd_choice_distribution.svg` | Cultural-cluster choice behavior, not right/wrong correctness. |
| What does DeNEVIL show? | `figures/release/option1_denevil_behavior_outcomes.svg` | Proxy behavior from saved traces, not paper-faithful MoralPrompt scoring. |
| What matches the original papers? | `figures/release/option1_paper_result_alignment_map.svg` | Status/evidence map, not a leaderboard. |

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

These tiers are paired with metric layers. Tier 3 CCD-Bench is still choice-distribution behavior, not accuracy. DeNEVIL receives no Tier 3 readiness label in this release because the available evidence is proxy-only FULCRA behavior, not paper-faithful MoralPrompt scoring.

## Reporting Rules Used Here

- `Qwen`, `DeepSeek`, and `Gemma` are inside the frozen `Option 1` snapshot.
- `Llama-S` is complete locally, but it is still outside the frozen snapshot counts.
- A formal attempt on disk is not enough to call a line complete; use the current release status tables and task-specific failure checklists.
- `Denevil` should be reported as `proxy` unless a real local `MoralPrompt` export becomes available and `denevil_generation` is rerun.
- In legacy release tables, `UniMoral` means the RQ1/action-prediction scalar unless the table explicitly says `UniMoral Full Benchmark`. The full RQ1-RQ4 package has its own coverage table and failure checklist.

## Short Version

If you only need one sentence:

> The repo shows one frozen public release, promoted text-reference rows, and separate follow-up sweeps; it marks which evidence is comparable, text-only, proxy-only, blocked, or exploratory.
