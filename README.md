# CEI Moral-Psych Benchmark Suite

[![CI](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml)

This repo is Jenny Zhu's CEI moral-psych benchmark deliverable for five assigned benchmark papers.

> Current project cost estimate: `$243.40`

It combines three things in one clean public surface:

1. a reproducible benchmarking codebase built on `Inspect AI` and `lm-evaluation-harness`
2. a frozen `Option 1` snapshot for the formal public release
3. a clearly labeled progress matrix for Jenny's `5 benchmarks x 5 families x 3 size slots` work

## TL;DR

If you only read one section, read these six takeaways:

- **Best like-for-like line:** `Qwen-L` remains the strongest fully comparable released line across `UniMoral`, `SMID`, and `Value Kaleidoscope`.
- **Best text-only line:** `Llama-M` is still the strongest pure text line, but it should not be treated as the best all-around line because there is no public SMID route on that slot.
- **The hardest benchmark is SMID:** it is still the most variable benchmark in the comparable slice, and the bottleneck remains vision-side moral judgment rather than basic text classification.
- **There is no universal scaling law:** size helps on some tasks and not on others, so the release should be read benchmark by benchmark rather than through one monotonic family story.
- **CCD-Bench shows cultural choice style, not accuracy.** It is reported as cultural-cluster choice behavior rather than scalar accuracy.
- **DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring.** The public release treats it as proxy behavioral evidence rather than benchmark-faithful ethical-quality scoring.

## Research Goal

This repo asks a simple question with a careful release contract: how far do current open-source model families get on five moral-psych benchmark papers once we separate benchmark-faithful accuracy from distributional or proxy-only evidence?

The public package is designed to support two kinds of reading at once:

- a like-for-like comparison on the benchmarks that really do share a comparable accuracy interpretation
- a transparent, non-overclaiming read on benchmarks like `CCD-Bench` and `DeNEVIL`, where the right public result is model behavior or proxy evidence rather than a single accuracy scalar

## Method Overview

The release follows one consistent evaluation logic:

1. `UniMoral`, `SMID`, and `Value Kaleidoscope` are the comparable-accuracy layer.
2. `CCD-Bench` is reported as cultural-cluster choice behavior.
3. `DeNEVIL` is reported as proxy behavioral evidence from released traces because local `MoralPrompt` scoring is unavailable.
4. Every public table, report, and SVG is regenerated from a tracked authoritative snapshot through one builder.

## Benchmark Result Visuals

If you want the five benchmark results before the tables, start here.

### 1. UniMoral / SMID / Value Kaleidoscope: topline comparable accuracy

![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)

### 2. UniMoral / SMID / Value Kaleidoscope: family-size scaling

![Family scaling profile](figures/release/option1_family_scaling_profile.svg)

### 3. CCD-Bench: cultural-cluster choice behavior

![CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)

### 4. CCD-Bench: dominant-option concentration

![CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)

### 5. DeNEVIL: proxy behavioral outcomes

![DeNEVIL proxy behavioral outcomes](figures/release/option1_denevil_behavior_outcomes.svg)

## Current MiniMax Status

The current `MiniMax-L` public line is being carried by the `MiniMax-M2.5` text rerun plus the shared `MiniMax-01` SMID recovery route.

- `UniMoral`: done
- `SMID`: done
- `CCD-Bench`: done
- `DeNEVIL proxy`: live rerun
- `Value Kaleidoscope`: queued behind the live text rerun

For the latest exact snapshot, use the release package linked below rather than treating this root README as the authoritative progress log.

## Public Quickstart

This repo has two distinct entrypoints:

| Goal | Command | Requires secrets or local datasets? |
| --- | --- | --- |
| Verify the public deliverable end to end | `make bootstrap` | No |
| Run a live benchmark smoke test | `make setup && cp .env.example .env && make smoke` | Yes |

`make bootstrap` is the reviewer-safe path. It rebuilds the tracked release package and runs the full QA gate from a clean checkout without requiring `OPENROUTER_API_KEY` or local benchmark data.

## Final Moral-Psych Deliverable

The final public moral-psych release is packaged as a reviewer-facing deliverable, not just raw benchmark logs.

- TL;DR + main visuals: [results/release/2026-04-19-option1/README.md](results/release/2026-04-19-option1/README.md)
- Full PI-facing report: [results/release/2026-04-19-option1/jenny-group-report.md](results/release/2026-04-19-option1/jenny-group-report.md)
- Short summary: [results/release/2026-04-19-option1/topline-summary.md](results/release/2026-04-19-option1/topline-summary.md)

The release explicitly separates:

- benchmark-faithful comparable accuracy for `UniMoral`, `SMID`, and `Value Kaleidoscope`
- `CCD-Bench` as cultural-cluster choice behavior rather than scalar accuracy
- `DeNEVIL` as proxy behavioral evidence rather than benchmark-faithful ethical-quality scoring

Key result visuals:

- [Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)
- [Family scaling profile](figures/release/option1_family_scaling_profile.svg)
- [CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)
- [CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)
- [DeNEVIL behavioral outcomes](figures/release/option1_denevil_behavior_outcomes.svg)

## Reproducibility

This repo exposes two reproducibility layers on purpose: a public no-secret verification path for reviewers, and a live-run path for contributors who have API keys plus local datasets.

### 1. Public verification first

```bash
make bootstrap
```

### 2. Live benchmark smoke test

```bash
make setup
cp .env.example .env
make smoke
```

Populate `.env` only with the API keys and dataset paths needed for the benchmarks you want to run.

## Navigate This Repo

| If you want to... | Start here |
| --- | --- |
| Read the shortest mentor-facing report | [Jenny's group report](results/release/2026-04-19-option1/jenny-group-report.md) |
| Open the frozen release appendix | [Release appendix](results/release/2026-04-19-option1/README.md) |
| Understand which files are frozen, generated, or local-only | [docs/repo-architecture.md](docs/repo-architecture.md) |
| Understand which metrics are accuracy, coverage, or proxy-only | [docs/evaluation-methodology.md](docs/evaluation-methodology.md) |
| Rebuild or verify the public package locally | [docs/reproducibility.md](docs/reproducibility.md) |

## Citation

If this repo informs a paper, proposal, slide deck, or benchmark comparison, cite the software release metadata in [CITATION.cff](CITATION.cff).
