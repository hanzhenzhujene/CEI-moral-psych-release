# CEI Moral-Psych Benchmark Suite

[![CI](https://github.com/Center-for-Ethical-Intelligence/moral-psychology-benchmark/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Center-for-Ethical-Intelligence/moral-psychology-benchmark/actions/workflows/ci.yml)

This repo is Jenny Zhu's CEI moral-psych benchmark deliverable for five assigned benchmark papers.

> Current project total cost: `$759.59` (MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$254.17`; OpenAI API reference sweep: `$0.76`.)

It combines three things in one clean public surface:

1. a reproducible benchmarking codebase built on `Inspect AI` and `lm-evaluation-harness`
2. a frozen `Option 1` snapshot for the first formal public release
3. a clearly labeled progress matrix for the current `5 benchmarks x 5 public model families x 3 size slots` plan

## TL;DR

If you only read one section, read these key takeaways:

- **Best like-for-like line:** `MiniMax-S` is the strongest fully comparable line, averaging 0.611 across UniMoral 0.661, SMID 0.432, and Value 0.740. This is the cleanest overall topline because all three comparable metrics are observed on the same line.
- **Best text-only line:** `MiniMax-M` is the strongest pure text line, reaching UniMoral 0.659 and Value 0.740. It should not be called the best all-around line because there is no public SMID route on that line.
- **GPT4-only reference line:** `GPT4 only` is added as a single text-only reference point with 76,486/76,486 parsed prompts: UniMoral 0.673, Value 0.701, and CCD-Bench 100.0% valid-choice coverage. It is not a size-family curve, and SMID / DeNEVIL remain intentionally `n/a`.
- **The hardest benchmark is SMID:** `SMID` has the lowest mean accuracy (0.364) and widest spread (0.285), while `UniMoral` is tightly clustered (0.121 spread). The main bottleneck is vision-side moral judgment, not basic text moral classification.
- **There is no universal scaling law:** `Gemma` is non-monotonic on SMID (0.417 -> 0.364 -> 0.412), and `Llama-M` still beats `Llama-L` on Value (0.724 vs 0.692). Size helps on some tasks, but not in one clean monotonic pattern.
- **CCD-Bench shows cultural choice style, not accuracy.** Every released line with valid CCD choices currently peaks on `option_6 (Nordic Europe)`, but concentration still varies meaningfully, from `DeepSeek-S` at 13.8% to `Llama-S` at 23.9%. The key question is how narrowly each line collapses onto one cultural cluster, not who has the highest "accuracy."
- **DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring.** Among completed lines with usable visible traces, protective/contextual behavior dominates (92.4% to 99.5% protective response rate). `DeepSeek-S` no longer has the old visibility-collapse problem in the May 9 saved rerun (0.2% no-visible proxy traces).
- **Current GitHub-facing boundary:** No MiniMax-M2.5 text benchmark remains live; the saved MiniMax-M2.5 text/proxy pass is already parsed into the public tables and SVGs. SMID remains `TBD`, so the medium MiniMax line is not a fully comparable all-around line yet.


## Latest Additional Model Sweep

The May 13 additional-model sweep tests older or smaller OpenRouter routes on `UniMoral` and `CCD-Bench` to check whether they produce a different pattern from the main model matrix. Full tables and provenance are in [results/exploratory/2026-05-13-additional-model-sweep](results/exploratory/2026-05-13-additional-model-sweep/).

**Model-wise:** Mistral Nemo is the top UniMoral line at 0.648, but Qwen2.5 7B, Llama 3.1 8B, and Llama 3 8B are close behind from 0.632 to 0.640. Llama 3.2 1B is the clear weak line at 0.406, with a lower answer rate as well.

**Benchmark-wise:** UniMoral gives a clear performance separation between the very small 1B route and the stronger 7B-12B cluster. CCD-Bench gives a style/concentration readout rather than a correctness score: all models peak on Nordic Europe, but Llama 3.2 1B is most diffuse (15.9% dominant share; 9.12 effective clusters), while Mistral Nemo is most concentrated (25.3%; 7.22 effective clusters).

**Scaling-wise:** There is no clean monotonic scaling law. The move from 1B to 7B+ matters a lot, but above that threshold the 7B-12B models cluster closely rather than improving smoothly with size. This looks more like a capability floor than a simple bigger-is-better trend.

**Bottom line:** The additional sweep does not overturn the main release story. It adds one useful detail: very small models can fall off sharply, while several older or mid-sized instruction routes remain competitive on the selected text/style checks.

![Additional model sweep UniMoral accuracy](figures/exploratory/additional_model_sweep_unimoral_accuracy.svg)

![Additional model sweep CCD concentration](figures/exploratory/additional_model_sweep_ccd_dominant_share.svg)

![Additional model sweep scaling readout](figures/exploratory/additional_model_sweep_scaling.svg)

## Research Goal

This repo asks a simple question with a careful release contract: how far do current open-source model families get on five moral-psych benchmark papers once we separate benchmark-faithful accuracy from distributional or proxy-only evidence?

The public package is designed to support two kinds of reading at once:

- a like-for-like comparison on the benchmarks that really do share a comparable accuracy interpretation
- a transparent, non-overclaiming read on benchmarks like `CCD-Bench` and `DeNEVIL`, where the right public result is model behavior or proxy evidence rather than a single accuracy scalar

## Method Overview

The release follows one consistent evaluation logic:

1. `UniMoral`, `SMID`, and `Value Kaleidoscope` are the comparable-accuracy layer. They drive the main topline ranking and the scaling summary.
2. `CCD-Bench` is reported as cultural-cluster choice behavior: which options each line over-selects, and how concentrated that choice pattern becomes.
3. `DeNEVIL` is reported as proxy behavioral evidence from released traces because local `MoralPrompt` scoring is unavailable; it is therefore excluded from macro-accuracy claims by design.
4. Every public table, report, and SVG is regenerated from a tracked authoritative snapshot through one builder, so the repo publishes a coherent frozen release rather than a hand-edited dashboard.

## Benchmark Result Visuals

If you want the five benchmark results before the tables, start here. These five visuals pull the main result surfaces for the full benchmark set to the front of the deliverable.

`GPT4 only` is shown as a single text-only reference marker in the comparable-accuracy and CCD figures. It is not treated as a GPT4 S/M/L scaling series, and it has no SMID or DeNEVIL row.

### 1. UniMoral / SMID / Value Kaleidoscope: topline comparable accuracy

![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)

_Use this first for the like-for-like result on the three benchmark-faithful accuracy tasks. Hatched SMID rows for `DeepSeek-S`, `DeepSeek-M`, `DeepSeek-L`, `Qwen-M`, and `Llama-M` mean no public vision route, not an unparsed text result._

### 2. UniMoral / SMID / Value Kaleidoscope: family-size scaling

![Family scaling profile](figures/release/option1_family_scaling_profile.svg)

_Use this second to compare size effects across the comparable-accuracy layer without mixing in CCD-Bench or DeNEVIL proxy evidence; missing SMID points are explicit route gaps._

### 3. CCD-Bench: cultural-cluster choice behavior

![CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)

_This is the main CCD-Bench result: deviation from the 10% uniform baseline across the ten canonical cultural clusters._

### 4. CCD-Bench: dominant-option concentration

![CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)

_This is the compact CCD-Bench summary: how much each line collapses onto one dominant cluster, and how broadly it still spreads across the option set._

### 5. DeNEVIL: proxy behavioral outcomes

![DeNEVIL proxy behavioral outcomes](figures/release/option1_denevil_behavior_outcomes.svg)

_This is the main DeNEVIL result surface: auditable behavioral categories from proxy traces, not benchmark-faithful accuracy._

Lower-level QA/provenance figures are still generated in `figures/release/`, but the README keeps the visual story focused on these audience-facing result surfaces.

## Public Quickstart

This repo has two distinct entrypoints:

| Goal | Command | Requires secrets or local datasets? |
| --- | --- | --- |
| Verify the public deliverable end to end | `make bootstrap` | No |
| Run a live benchmark smoke test | `make setup && cp .env.example .env && make smoke` | Yes |

`make bootstrap` is the reviewer-safe path. It rebuilds the tracked release package and runs the full QA gate from a clean checkout without requiring `OPENROUTER_API_KEY` or local benchmark data.

## Navigate This Repo

| If you want to... | Start here |
| --- | --- |
| Read the shortest mentor-facing report | [Jenny's group report](results/release/2026-04-19-option1/jenny-group-report.md) |
| Open the frozen release appendix | [Release appendix](results/release/2026-04-19-option1/README.md) |
| See the model lineup | [Models](#models) |
| Understand which files are frozen, generated, or local-only | [Repo Architecture](docs/repo-architecture.md) |
| Understand which metrics are accuracy, coverage, or proxy-only | [Evaluation Methodology](docs/evaluation-methodology.md) |
| Cite the repo as a software artifact | [CITATION.cff](CITATION.cff) |
| Understand how raw runs become public artifacts | [Data Flow](#data-flow) |
| Go straight to the five benchmark visuals | [Benchmark Result Visuals](#benchmark-result-visuals) |
| Read the May 13 additional-model follow-up | [Latest Additional Model Sweep](#latest-additional-model-sweep) |
| Jump straight to the live summary | [Results First](#results-first) |
| Check the exact full-matrix status | [Family-Size Progress Matrix](#family-size-progress-matrix) |
| Rebuild or verify the public package locally | [Reproducibility](#reproducibility) |

## Repository Layout

```text
CEI/
├── README.md                               # repo landing page and live status snapshot
├── docs/                                   # reading guides, reproducibility, and data-access notes
├── figures/release/                        # tracked SVG figures for the public package
├── results/release/2026-04-19-option1/     # frozen release package and report artifacts
├── results/inspect/                        # local Inspect AI run outputs and progress logs
├── scripts/                                # active launchers, recovery helpers, and release builders
├── scripts/legacy-openrouter/              # archived one-off OpenRouter launchers
├── src/                                    # inspect-ai and lm-eval-harness task code
├── tests/                                  # regression, hygiene, and release artifact tests
├── tools/legacy_openrouter/                # archived standalone OpenRouter/TrolleyBench tools
├── Makefile                                # setup, test, release, and audit entry points
└── pyproject.toml                          # project metadata and Python tooling
```

If you want the shortest explanation of which files are generated, frozen, or intentionally local-only, start with [docs/repo-architecture.md](docs/repo-architecture.md).

## Models

Every evaluation line in this repo is mapped onto a family-size slot and served through `OpenRouter`. Text routes cover `UniMoral`, `Value Kaleidoscope`, `CCD-Bench`, and `Denevil`; any slot with a vision route also covers `SMID`.

> `Small`, `Medium`, and `Large` are this repo's planning slots for the project matrix. They are not meant as a universal vendor taxonomy.

| Family | Small slot | Medium slot | Large slot | Coverage |
| --- | --- | --- | --- | --- |
| `Qwen` | **Text:** `qwen3-8b`<br/>**Vision:** `qwen3-vl-8b-instruct` | **Text:** `qwen3-14b` | **Text:** `qwen3-32b`<br/>**Vision:** `qwen2.5-vl-72b-instruct (recovery complete)` | Text benchmarks on `S/M/L`; SMID on `S/L`. |
| `MiniMax` | **Text:** `minimax-m2.1 (direct MiniMax API)`<br/>**Vision:** `minimax-01 (SMID recovery route)` | **Text:** `minimax-m2.5 (direct MiniMax API clean run)` | **Text:** `minimax-m2.5`<br/>**Vision:** `minimax-01 (shared SMID recovery route)` | Text benchmarks on `S/M/L`; SMID on `S/L`. |
| `DeepSeek` | **Text:** `deepseek-r1-distill-llama-70b (DeepInfra-pinned recovery route)` | **Text:** `deepseek-chat-v3.1` | **Text:** `deepseek-r1` | Text benchmarks on `S/M/L`. |
| `Llama` | **Text / Vision:** `llama-3.2-11b-vision-instruct` | **Text:** `llama-3.3-70b-instruct` | **Text / Vision:** `llama-4-maverick` | Text benchmarks on `S/M/L`; SMID on `S/L`. |
| `Gemma` | **Text / Vision:** `gemma-3-4b-it` | **Text / Vision:** `gemma-3-12b-it` | **Text / Vision:** `gemma-3-27b-it` | Text benchmarks and SMID on `S/M/L`. |

_Exact per-line status lives below in Results First and the Family-Size Progress Matrix._

## Data Flow

This is the shortest mental model for how raw benchmark inputs become the public package in this repo.

```text
Benchmark inputs
  data/, local benchmark dirs, provider URLs
      |
      v
Task builders
  src/inspect/evals/*.py
  Normalize prompts, scorers, and sample metadata
      |
      v
Runner
  src/inspect/run.py
  scripts/family_size_text_expansion.sh
  Apply model route, temperature, concurrency, and rerun controls
      |
      v
OpenRouter
  Execute the selected text or vision model calls
      |
      v
Inspect outputs
  results/inspect/logs/
  results/inspect/full-runs/
  Save .eval archives, traces, progress checkpoints, and watcher state
      |
      +--> Release builder
              scripts/build_release_artifacts.py
                  |
                  v
              Public outputs
                README.md
                results/release/...
                figures/release/...
```

Raw evaluation artifacts stay under `results/inspect/`; the public-facing README, report, CSV tables, and SVG figures are regenerated from those artifacts by `scripts/build_release_artifacts.py`.

## Results First

This is the fastest way to understand the deliverable: which lines already have usable results, what is directly comparable now, and which family-size expansions are complete versus partial.

In the legacy status and comparable-accuracy tables below, `UniMoral` refers to the original RQ1 action-prediction scalar unless a table explicitly says `UniMoral Full Benchmark`. The full RQ1-RQ4 coverage table later in this README is the source of truth for typology, factor attribution, and consequence generation status.

| Line | Scope | Status | Coverage | Note |
| --- | --- | --- | --- | --- |
| `Qwen-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Qwen release line. |
| `DeepSeek-M` | Frozen Option 1 | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Primary medium DeepSeek release line: UniMoral 0.684, Value 0.635, CCD 2,177/2,182 valid choices, Denevil 20,514/20,518 visible proxy responses. |
| `Gemma-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Gemma release line. |
| `Llama-S` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally, outside the frozen Option 1 counts. |
| `Gemma-M` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Gemma-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Qwen-M` | Complete local line | Done | Earlier text checkpoints withdrawn; UniMoral action prediction done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Complete local line | Done | SMID recovery stands; UniMoral action prediction done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | SMID recovery complete; clean text rerun finished locally. |
| `Llama-M` | Complete local line | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Completed locally on April 22, 2026. |
| `DeepSeek-L` | Complete local line | Done | No SMID route; UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy parsed from saved R1 shards | Large R1 text rerun complete from saved logs; keep it text-only because no SMID route exists. |
| `Llama-L` | Complete local line | Done | SMID complete; UniMoral action prediction done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy finished at 100.0%. | SMID complete; local text rerun finished successfully through the Denevil proxy task. |
| `DeepSeek-S` | Complete local line | Done | No SMID route; UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy are complete in the May 9 no-thinking saved logs | May 9 no-thinking rerun passes visible-answer validation; SMID remains unavailable for this DeepSeek size slot. |
| `MiniMax-M` | Complete local text line | Done | Clean MiniMax-M2.5 text/proxy benchmarks complete; no medium SMID route fixed yet. | Clean direct MiniMax-M2.5 text run is complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; no medium SMID route fixed yet. Build-time persisted text counts: UniMoral action prediction 8,784/8,784; Value 65,520/65,520; CCD 2,182/2,182; Denevil proxy 20,518/20,518. |
| `MiniMax-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) using MiniMax-M2.5 text plus the shared MiniMax-01 SMID recovery route | The direct-provider MiniMax rerun finished successfully through the Denevil proxy task. |
| `MiniMax-S` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | MiniMax-S now uses the clean direct MiniMax-M2.1 text rerun plus the completed MiniMax-01 SMID recovery route. |

### Current Comparable Accuracy Snapshot

The table below is intentionally limited to the three directly comparable accuracy metrics: `UniMoral`, `SMID`, and `Value Kaleidoscope`. `CCD-Bench` and `Denevil` are reported separately below as coverage / proxy evidence because neither benchmark currently supports a benchmark-faithful universal accuracy claim in this public release. `n/a` marks benchmarks that are route-missing, incomplete, or intentionally withheld after response-format validation.

Metric definition version: `2026-04-30`. The visible-answer parsing rules behind these columns are versioned explicitly so later scorer changes do not silently rewrite the public story.

| Line | UniMoral action | SMID average | Value Kaleidoscope average | Comparison note |
| :--- | ---: | ---: | ---: | --- |
| `Qwen-S` | 0.647 | 0.368 | 0.682 | Comparable on all three benchmark-faithful accuracy panels. |
| `Qwen-M` | 0.665 | n/a | 0.675 | Text-only comparable line; no public SMID route on this slot. |
| `Qwen-L` | 0.665 | 0.483 | 0.653 | Comparable on all three benchmark-faithful accuracy panels. |
| `MiniMax-S` | 0.661 | 0.432 | 0.740 | Comparable on all three benchmark-faithful accuracy panels. |
| `MiniMax-M` | 0.659 | n/a | 0.740 | Text-only comparable line; no public SMID route on this slot. |
| `MiniMax-L` | 0.661 | 0.198 | 0.741 | Comparable on all three benchmark-faithful accuracy panels. |
| `DeepSeek-S` | 0.661 | n/a | 0.695 | Text-only comparable no-thinking rerun; no public SMID route on this slot. |
| `DeepSeek-M` | 0.684 | n/a | 0.635 | Text-only comparable line; no public SMID route on this slot. |
| `DeepSeek-L` | 0.563 | n/a | 0.681 | Text-only comparable line; no public SMID route on this slot. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Comparable on all three benchmark-faithful accuracy panels. |
| `Llama-M` | 0.670 | n/a | 0.724 | Text-only comparable line; no public SMID route on this slot. |
| `Llama-L` | 0.660 | 0.386 | 0.692 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-M` | 0.663 | 0.364 | 0.664 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-L` | 0.661 | 0.412 | 0.656 | Comparable on all three benchmark-faithful accuracy panels. |
| `GPT4 only` | 0.673 | n/a | 0.701 | GPT4-only text reference marker; SMID and DeNEVIL intentionally not run. |

_The topline comparable-accuracy chart already appears above in **Benchmark Result Visuals**. The table here keeps the exact numeric readout inline without repeating the same headline figure._

### DeepSeek S/M/L Log-Derived Readout

`DeepSeek-S`, `DeepSeek-M`, and `DeepSeek-L` all have explicit text-only results from saved logs. `DeepSeek-S` points at the May 9 no-thinking rerun artifacts, `DeepSeek-M` remains the frozen medium text-only line, and `DeepSeek-L` points at the saved R1 shard rerun. No DeepSeek line has a SMID vision route.

| Line | Comparable text accuracy | CCD-Bench saved choices | DeNEVIL proxy visibility | Public interpretation |
| --- | --- | --- | --- | --- |
| `DeepSeek-S` | UniMoral 0.661; Value 0.695 | 2,180 / 2,182 (99.9%) | 20,474 / 20,518 (99.8%) | Valid text-only no-thinking rerun from saved May 9 logs: UniMoral and Value Kaleidoscope are scored, CCD-Bench has near-complete parseable choices, and Denevil is proxy-only behavioral evidence. No SMID route exists. |
| `DeepSeek-M` | UniMoral 0.684; Value 0.635 | 2,177 / 2,182 (99.8%) | 20,514 / 20,518 (100.0%) | Valid text-only comparable line from existing logs: UniMoral and Value Kaleidoscope are scored, CCD-Bench has near-complete parseable choices, and Denevil is proxy-only behavioral evidence. No SMID route exists. |
| `DeepSeek-L` | UniMoral 0.563; Value 0.681 | 2,109 / 2,182 (96.7%) | 20,331 / 20,518 (99.1%) | Valid text-only large R1 rerun from saved shard logs: UniMoral and Value Kaleidoscope are scored, CCD-Bench has high parseable-choice coverage, and Denevil is proxy-only behavioral evidence. No SMID route exists. |
## Interpretation

These are the strongest claims the current public evidence supports. They use only the benchmarks with directly comparable accuracy metrics and keep `Denevil` proxy results out of any macro-accuracy claim.

### Interpretation At A Glance

| Claim | Evidence | Why it matters |
| --- | --- | --- |
| Strongest fully observed comparable line | `MiniMax-S` averages 0.611 across UniMoral 0.661, SMID 0.432, and Value 0.740. | This is the cleanest like-for-like topline because all three comparable metrics are present on the same line. |
| Strongest text-only comparable line | `MiniMax-M` reaches UniMoral 0.659 and Value 0.740, a two-metric mean of 0.699. | It is the strongest text-only comparison point, but it should not be described as the best all-around line because there is no SMID route on that line. |
| GPT4-only reference marker | `GPT4 only` parses 76,486/76,486 prompts, reaches UniMoral 0.673 and Value 0.701; CCD-Bench valid-choice coverage is 100.0%. | This is a useful external text-only reference, but it is not a GPT4 size-series claim and has no SMID / DeNEVIL evidence in this release. |
| Hardest current comparable benchmark | `SMID` has the lowest mean accuracy at 0.364 and the widest spread at 0.285. | The public readout should treat SMID as the highest-variance benchmark rather than expecting simple size-based improvements. |
| Closest thing to saturation | `UniMoral` has the tightest range, from 0.563 to 0.684 (0.121 spread). | Current text lines cluster closely on UniMoral, so additional size mainly fine-tunes rather than reshapes the ranking there. |
| Scaling-law read | `Gemma` is still the only family with a full three-metric S/M/L comparable sweep, while `Qwen`, `DeepSeek`, and `Llama` now add broader text-side size curves. `GPT4 only` is a single reference point and is excluded from size-law claims. Even in the cleanest full sweep, the directions diverge: Gemma UniMoral rises from 0.635 to 0.661, Value from 0.593 to 0.656, but SMID is nearly flat overall (0.417 to 0.412). | The data support task-specific scaling, not a single monotonic law across all families and benchmarks. |

### Benchmark Reading Guide

Before comparing charts, anchor each benchmark to its source paper. These benchmarks do not all ask for the same kind of moral competence, so a clean read depends on matching the score to the paper's original intent.

| Benchmark | What the paper is really testing | What this repo currently scores | How to read the current result |
| --- | --- | --- | --- |
| `UniMoral` | A unified multilingual moral-reasoning resource spanning action choice, typology, factor attribution, and consequence generation under culturally varied dilemmas. | This repo now implements all four UniMoral task definitions. Action prediction remains the legacy comparable scalar; RQ2/RQ3/RQ4 completion status is tracked in the UniMoral coverage and failure artifacts. | A high action-prediction score means the model tracks consensus action choices across multilingual moral dilemmas. The added RQ2/RQ3/RQ4 artifacts should be read separately because several provider cells remain incomplete or parse-limited. |
| `SMID` | A normed socio-moral image stimulus set for studying moral and affective processing, with large-scale human ratings of wrongness and moral-foundation relevance. | The public release averages two vision tasks: discrete moral-rating prediction and dominant moral-foundation classification from the image norms. | A high SMID score means the model can recover socially and morally salient cues from images in ways that align with normative human judgments. Because SMID is a stimulus set rather than a single-label objective benchmark, low scores can reflect visual ambiguity and weaker consensus, not just poor moral reasoning. |
| `Value Kaleidoscope` | A value-pluralism benchmark built from ValuePrism, asking which values, rights, and duties are relevant in context and whether they support or oppose the situation. | The public release averages two text tasks: relevance classification and valence classification for candidate values, rights, and duties. | A high Value Kaleidoscope score means the model is good at explicit value tagging and polarity assignment. It should be read as structured value recognition, not as proof that the model resolves pluralistic moral conflicts into the best final action. |
| `CCD-Bench` | A cross-cultural conflict benchmark where models adjudicate between ten culturally grounded response options tied to GLOBE cultural clusters. | The current harness checks whether the model produces a well-formed option selection and rationale over the full 10-way choice set. | CCD-Bench is most informative through choice behavior across cultural clusters, not through a single comparable scalar accuracy. This release therefore leads with a canonical cluster heatmap and a concentration summary, while valid-choice coverage is demoted to appendix QA. None of these CCD surfaces should be read as universal accuracy. |
| `Denevil` | A dynamic generative evaluation of ethical value vulnerabilities that uses MoralPrompt to elicit potential value violations rather than only classifying fixed items. | The current public release can only run the FULCRA-backed proxy generation pathway, so headline DeNEVIL reporting is based on auditable visible behavioral outcomes rather than paper-faithful MoralPrompt scoring. | A finished DeNEVIL proxy line is proxy-only behavioral evidence and traceability support, not benchmark-faithful ethical-quality scoring. The public release therefore leads with visible behavior categories and a prompt-family breakdown, while route/sample/timestamp fields stay in appendix QA tables. It should stay outside any macro-accuracy claim until the paper-faithful MoralPrompt evaluation is available locally. |

### Benchmark Difficulty Profile

![Benchmark difficulty profile](figures/release/option1_benchmark_difficulty_profile.svg)

_Figure 3. Mean, low, and high accuracy for the three directly comparable benchmark groups; lower means and wider ranges indicate a harder or less stable benchmark in the current public slice._

| Benchmark | Mean accuracy | Best line | Lowest line | Spread | Reading |
| --- | ---: | --- | --- | ---: | --- |
| `UniMoral` | 0.653 | `DeepSeek-M` (0.684) | `DeepSeek-L` (0.563) | 0.121 | Tightest spread; current lines cluster closely. |
| `SMID` | 0.364 | `Qwen-L` (0.483) | `MiniMax-L` (0.198) | 0.285 | Lowest mean and widest spread in the current comparable slice. |
| `Value Kaleidoscope` | 0.673 | `MiniMax-L` (0.741) | `Llama-S` (0.529) | 0.213 | Mid-range difficulty with meaningful but not extreme variation. |

### Family Scaling Profile

_The headline family-scaling figure already appears above in **Benchmark Result Visuals**. The summary table below keeps the size-by-family takeaways inline here without re-embedding the same chart._

| Family | Evidence scope | Numeric pattern | Cautious interpretation |
| --- | --- | --- | --- |
| `Qwen` | Text benchmarks now have S/M/L comparable points, and SMID has S/L evidence after the recovered large line. | UniMoral: S 0.647 -> M 0.665 -> L 0.665<br/>SMID: S 0.368 -> L 0.483<br/>Value Kaleidoscope: S 0.682 -> M 0.675 -> L 0.653 | Qwen improves from S to M on text tasks and then largely plateaus at L, while the recovered large SMID line is much stronger than the small line. That supports task-specific scaling, not a single monotonic curve. |
| `MiniMax` | 3 comparable metric series available. | UniMoral: S 0.661 -> M 0.659 -> L 0.661<br/>SMID: S 0.432 -> L 0.198<br/>Value Kaleidoscope: S 0.740 -> M 0.740 -> L 0.741 | Current public evidence is too sparse for a stronger within-family scaling claim. |
| `DeepSeek` | The S/M/L text lines are now accuracy-comparable where text-only metrics exist, but no DeepSeek slot has a public SMID route. | UniMoral: S 0.661 -> M 0.684 -> L 0.563<br/>Value Kaleidoscope: S 0.695 -> M 0.635 -> L 0.681 | Read the DeepSeek size curve as text-only evidence: S and L now come from saved shard reruns, M remains the frozen closed-slice line, and all three still omit SMID. |
| `Llama` | Text benchmarks now have S/M/L comparable points, and SMID has S/L evidence. | UniMoral: S 0.648 -> M 0.670 -> L 0.660<br/>SMID: S 0.216 -> L 0.386<br/>Value Kaleidoscope: S 0.529 -> M 0.724 -> L 0.692 | Llama improves sharply from the small line to the larger text routes and also gains on SMID from S to L, but the medium text line still beats the large line on some text metrics, so the pattern is broader than before without becoming fully monotonic. |
| `Gemma` | Full S/M/L comparable sweep on all three comparable benchmarks. | UniMoral: S 0.635 -> M 0.663 -> L 0.661<br/>SMID: S 0.417 -> M 0.364 -> L 0.412<br/>Value Kaleidoscope: S 0.593 -> M 0.664 -> L 0.656 | Best evidence against a single universal scaling law in this repo: text benchmarks improve with size overall, while SMID is non-monotonic. |
| `GPT4 only` | Single text-only reference point, not a family-size scaling sweep. | UniMoral: Ref 0.673<br/>Value Kaleidoscope: Ref 0.701 | GPT4 only is plotted as a reference marker on UniMoral action prediction, Value Kaleidoscope, and CCD-Bench only; it should not be read as evidence about GPT4 family scaling or vision-side SMID performance. |

### CCD-Bench Choice Behavior

CCD-Bench should not be flattened into a universal accuracy number. The paper asks models to choose among ten culturally grounded options, so the public headline result is now choice behavior: which canonical clusters each line over-indexes or under-indexes relative to a uniform 10% baseline, and how concentrated that choice pattern becomes on its dominant cluster.

CCD option order follows the paper's canonical cluster IDs: 1 = Anglo; 2 = Eastern Europe; 3 = Latin America; 4 = Latin Europe; 5 = Confucian Asia; 6 = Nordic Europe; 7 = Sub Saharan Africa; 8 = Southern Asia; 9 = Germanic Europe; 10 = Middle East.

_The two headline CCD figures already appear above in **Benchmark Result Visuals**. The full ten-option numeric table is published in `results/release/2026-04-19-option1/ccd-choice-distribution.csv`; the compact table below keeps the most PI-facing CCD readouts inline without turning parser coverage into the headline claim._

| Line | Dominant cluster | Top-cluster share | Effective clusters | Behavioral note |
| --- | --- | ---: | ---: | --- |
| `Qwen-S` | option_6 (Nordic Europe) | 19.2% | 8.91 | Compare against the heatmap above, not as scalar accuracy. |
| `Qwen-M` | option_6 (Nordic Europe) | 21.9% | 8.29 | Compare against the heatmap above, not as scalar accuracy. |
| `Qwen-L` | option_6 (Nordic Europe) | 23.4% | 7.97 | Compare against the heatmap above, not as scalar accuracy. |
| `MiniMax-S` | option_6 (Nordic Europe) | 17.3% | 9.20 | Compare against the heatmap above, not as scalar accuracy. |
| `MiniMax-M` | option_6 (Nordic Europe) | 18.3% | 9.00 | Compare against the heatmap above, not as scalar accuracy. |
| `MiniMax-L` | option_6 (Nordic Europe) | 18.7% | 9.02 | Compare against the heatmap above, not as scalar accuracy. |
| `DeepSeek-S` | option_7 (Sub Saharan Africa) | 13.8% | 9.57 | Compare against the heatmap above, not as scalar accuracy. |
| `DeepSeek-M` | option_6 (Nordic Europe) | 22.6% | 7.99 | Compare against the heatmap above, not as scalar accuracy. |
| `DeepSeek-L` | option_6 (Nordic Europe) | 20.7% | 8.68 | Compare against the heatmap above, not as scalar accuracy. |
| `Llama-S` | option_6 (Nordic Europe) | 23.9% | 7.24 | Compare against the heatmap above, not as scalar accuracy. |
| `Llama-M` | option_6 (Nordic Europe) | 20.6% | 8.03 | Compare against the heatmap above, not as scalar accuracy. |
| `Llama-L` | option_6 (Nordic Europe) | 23.5% | 7.67 | Compare against the heatmap above, not as scalar accuracy. |
| `Gemma-S` | option_6 (Nordic Europe) | 21.6% | 8.37 | Compare against the heatmap above, not as scalar accuracy. |
| `Gemma-M` | option_6 (Nordic Europe) | 18.6% | 8.89 | Compare against the heatmap above, not as scalar accuracy. |
| `Gemma-L` | option_6 (Nordic Europe) | 17.6% | 9.05 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT4 only` | option_6 (Nordic Europe) | 17.1% | 8.94 | Compare against the heatmap above, not as scalar accuracy. |

### DeNEVIL Proxy Behavioral Evidence

**Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring.**

The repo still lacks a stable local `MoralPrompt` export, so paper-aligned APV / EVR / MVP are `n/a` in this public package. Instead, the release now leads with auditable behavioral outcomes over the FULCRA-backed proxy traces: protective refusals, redirects, corrective/contextual responses, direct task answers, potentially risky continuations, ambiguous visible answers, and empty traces.

The main DeNEVIL result surface is the visible-behavior mix across the full released proxy archive. Route/model provenance, sample volume, completion state, timestamps, and visible-response coverage are still exported in CSV/SVG artifacts, but they are not repeated in the README because they are QA/provenance rather than the audience-facing result story.

_The headline DeNEVIL behavioral-outcomes chart already appears above in **Benchmark Result Visuals**. This section keeps the explanatory framing and compact line-level behavior table without re-embedding low-level QA charts._

The compact behavior table below is the quickest line-level read.

| Line | Refusal | Redirect | Corrective/contextual | Direct answer | Risky continuation | Ambiguous | Empty | Dominant behavior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `Qwen-S` | 21.5% | 8.0% | 69.9% | 0.0% | 0.1% | 0.4% | 0.0% | Corrective / contextual response |
| `Qwen-M` | 22.1% | 8.4% | 69.0% | 0.0% | 0.2% | 0.3% | 0.0% | Corrective / contextual response |
| `Qwen-L` | 29.3% | 5.7% | 64.3% | 0.0% | 0.2% | 0.4% | 0.0% | Corrective / contextual response |
| `MiniMax-S` | 30.8% | 4.2% | 64.4% | 0.0% | 0.4% | 0.2% | 0.0% | Corrective / contextual response |
| `MiniMax-M` | 31.0% | 4.2% | 64.3% | 0.0% | 0.4% | 0.1% | 0.0% | Corrective / contextual response |
| `MiniMax-L` | 30.7% | 4.2% | 64.4% | 0.0% | 0.4% | 0.2% | 0.0% | Corrective / contextual response |
| `DeepSeek-S` | 20.8% | 4.9% | 72.5% | 0.0% | 1.4% | 0.2% | 0.2% | Corrective / contextual response |
| `DeepSeek-M` | 31.1% | 6.1% | 62.0% | 0.0% | 0.2% | 0.6% | 0.0% | Corrective / contextual response |
| `DeepSeek-L` | 37.8% | 5.3% | 51.9% | 0.0% | 0.7% | 3.5% | 0.9% | Corrective / contextual response |
| `Llama-S` | 41.0% | 1.3% | 56.5% | 0.0% | 0.1% | 1.2% | 0.0% | Corrective / contextual response |
| `Llama-M` | 26.0% | 1.8% | 70.5% | 0.0% | 0.1% | 1.6% | 0.0% | Corrective / contextual response |
| `Llama-L` | 22.9% | 1.4% | 74.7% | 0.0% | 0.2% | 0.8% | 0.0% | Corrective / contextual response |
| `Gemma-S` | 36.1% | 12.4% | 48.7% | 0.0% | 0.1% | 2.7% | 0.0% | Corrective / contextual response |
| `Gemma-M` | 43.3% | 4.1% | 44.9% | 0.0% | 0.0% | 7.6% | 0.0% | Corrective / contextual response |
| `Gemma-L` | 40.4% | 8.9% | 49.0% | 0.0% | 0.1% | 1.6% | 0.0% | Corrective / contextual response |

Low-level DeNEVIL QA/provenance artifacts remain exported in the release folder for audit, but the README does not embed the status, sample-volume, or visible-response-rate charts.

A few safe qualitative examples help clarify what the proxy traces actually look like in practice.

| Model line | Proxy prompt type | Shortened model output pattern | Interpretable signal |
| --- | --- | --- | --- |
| `Qwen-S` | Loaded social / political judgment | Corrective / contextual response | The visible trace gives a corrective or contextual answer, which is useful proxy behavior evidence even though the release does not claim paper-faithful Denevil scoring. |
| `Llama-L` | Illicit access / sabotage | Protective refusal | The visible trace refuses the request directly, which is a clear protective behavioral outcome in the proxy release. |
| `DeepSeek-S` | Loaded social / political judgment | No visible answer | This sample shows why the proxy package separates completed archives from the subset of traces that actually surface a visible public answer. |

### Reporting Guardrails

- Do not fold `Denevil` into any benchmark-faithful macro-accuracy claim; it remains proxy-only behavioral evidence and traceability support even when its completion status is `Done`.
- Read `CCD-Bench` in its dedicated choice-behavior figures, not in the family scaling line chart. `CCD-Bench` valid-choice coverage stays appendix QA only; the headline result is the cluster-selection heatmap and concentration summary.
- Read `Denevil` only through the dedicated proxy evidence package. Main figures show behavioral outcomes from released traces; sample counts, generated counts, route/model metadata, and timestamps stay in the appendix provenance tables. Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring.
- Read the CCD heatmap as deviation from a 10% uniform baseline over the paper's ten canonical cluster options. It compares cultural-choice behavior, not correctness against one universal target option.
- Read `DeepSeek-S` as a text-only no-SMID line from the May 9 no-thinking saved logs: `CCD-Bench valid-choice coverage = 99.9%`, and `Denevil visible proxy coverage = 99.8%`. These are parser/proxy coverage checks, not CCD or Denevil accuracy.
- Do not call `MiniMax-M` the best overall line across all tasks; its text results are strong, but there is no SMID route on that line.
- Do not claim a universal scaling law from these figures. `Gemma` is the only family with a full three-metric S/M/L sweep, the broader `Qwen` / `DeepSeek` / `Llama` text-side curves still move in mixed directions, and `GPT4 only` is only a single text-reference marker.
- Keep `DeepSeek-S` out of all-around winner claims because it has no SMID route, but keep its validated text metrics in the comparable text rows.
- Treat missing comparable cells as evidence limits rather than model failures. Several large lines are complete operationally but still lack directly comparable public metrics for some benchmarks.

## Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `May 15, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Current project total cost | `$759.59` |
| Total cost breakdown | MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$254.17`; OpenAI API reference sweep: `$0.76`. |
| Cost scope | User-confirmed total spend through the latest saved reruns parsed in this repo. |
| Intended use | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Current public matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Model families in scope | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |
| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |
| Extra completed local line | `Llama-S`, complete locally across `5` papers / `7` tasks |
| Run setting | `OpenRouter` + direct `MiniMax` + `OpenAI`, `temperature=0` |
| Current live reruns | No currently published line is still running locally. |
| Next restart focus | No published rerun is active right now. |
| Release guardrail | Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables. |

### Current Operations Highlights

This compact block sits between the topline tables and the detailed progress matrix so the live state stays readable.

- Active open-source reruns: none are currently shown in the published matrix.
- Stalled or queued follow-up work: no published partial or queued follow-up line is waiting right now.
- Complete local lines beyond the frozen `Option 1` slice: `Llama-S`, `Gemma-M`, `Gemma-L`, `Qwen-M`, `Qwen-L`, `Llama-M`, `DeepSeek-L`, `Llama-L`, `DeepSeek-S`, `MiniMax-L`, and `MiniMax-S`.
- Release guardrails: Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables.

## Local Expansion Checkpoint

This checkpoint summarizes the broader family-size expansion separately from the frozen Option 1 counts. It is a curated snapshot rather than a live dashboard.

| Line or batch | Status | Note |
| --- | --- | --- |
| `Qwen-L SMID recovery` | Done | Recovered via qwen2.5-vl-72b-instruct after the earlier moderation stop. |
| `Gemma-L text batch` | Done | Completed April 21 with a full local large text line. |
| `Gemma-M text batch` | Done | Completed April 21 with a full local medium text line. |
| `Qwen-M text batch` | Done | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L text batch` | Done | SMID recovery complete; clean text rerun finished locally. |
| `Llama-M text batch` | Done | Completed April 22 with a full medium text line. |
| `DeepSeek-S text batch` | Done | May 9 no-thinking rerun passes visible-answer validation; SMID remains unavailable for this DeepSeek size slot. |
| `DeepSeek-L R1 text batch` | Done | Saved R1 shards now cover UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy; no SMID route exists. |
| `Llama-L SMID` | Done | The large Llama vision line is complete locally. |
| `Next queued text lines` | Done | No currently published line remains queued behind an active rerun. |

## Status Key

| Mark | Meaning |
| --- | --- |
| `Done` | Finished with a usable result. |
| `Proxy` | Finished, but only with a substitute proxy dataset instead of the paper's original setup. |
| `Live` | Currently running locally. |
| `Partial` | Started locally and produced some usable outputs, but the line is not yet complete. |
| `Error` | A formal attempt exists, but the current result is not usable. |
| `Queue` | Approved and queued next. |
| `TBD` | The family-size route is not frozen yet. |
| `-` | No run is planned on that line right now. |

## Family-Size Progress Matrix

This is the main public status table for the current published matrix.

Here, the `UniMoral` column tracks the legacy action-prediction release line. See `UniMoral Full Benchmark Coverage` for the separate RQ2/RQ3/RQ4 completion matrix.

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | --- |
| `Qwen-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 line. |
| `Qwen-M` | Done | TBD | Done | Done | Proxy | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Done | Done | Done | Done | Proxy | SMID recovery complete; clean text rerun finished locally. |
| `MiniMax-S` | Done | Done | Done | Done | Proxy | Direct MiniMax-M2.1 text rerun complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; SMID uses the completed MiniMax-01 recovery route. |
| `MiniMax-M` | Done | TBD | Done | Done | Proxy | Clean direct MiniMax-M2.5 text run is complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; no medium SMID route fixed yet. Build-time persisted text counts: UniMoral action prediction 8,784/8,784; Value 65,520/65,520; CCD 2,182/2,182; Denevil proxy 20,518/20,518. |
| `MiniMax-L` | Done | Done | Done | Done | Proxy | Shared MiniMax-01 SMID recovery complete; the MiniMax-M2.5 text rerun is now fully persisted through the Denevil proxy task (100.0%). |
| `DeepSeek-S` | Done | - | Done | Done | Proxy | No SMID route; May 9 no-thinking text rerun is complete and visible-answer validated. |
| `DeepSeek-M` | Done | - | Done | Done | Proxy | Frozen medium text line; no SMID route was included. UniMoral 0.684, Value 0.635, CCD 2,177/2,182 valid choices, Denevil 20,514/20,518 visible proxy responses. |
| `DeepSeek-L` | Done | - | Done | Done | Proxy | No SMID route; large R1 text rerun is complete from saved shards with UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy parsed. |
| `Llama-S` | Done | Done | Done | Done | Proxy | Complete locally across all five papers. |
| `Llama-M` | Done | - | Done | Done | Proxy | No SMID route; medium text line completed locally on April 22, 2026. |
| `Llama-L` | Done | Done | Done | Done | Proxy | SMID complete; local text rerun is now fully persisted through the Denevil proxy task (100.0%). |
| `Gemma-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 recovery line. |
| `Gemma-M` | Done | Done | Done | Done | Proxy | Complete local line across all five papers. |
| `Gemma-L` | Done | Done | Done | Done | Proxy | Complete local line across all five papers. |

The same matrix is also saved as [family-size-progress.csv](results/release/2026-04-19-option1/family-size-progress.csv).

## The Five Benchmark Papers

| Benchmark | Paper | Dataset / access | Modality | What this repo tests now |
| --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. (ACL 2025 Findings)](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | Action prediction plus RQ2/RQ3/RQ4 artifacts with coverage caveats |
| `SMID` | [Crone et al. (PLOS ONE 2018)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | Moral rating + foundation classification |
| `Value Kaleidoscope` | [Sorensen et al. (AAAI 2024 / arXiv 2023)](https://arxiv.org/abs/2309.00779) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | Relevance + valence |
| `CCD-Bench` | [Rahman and Salam (arXiv 2025)](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | Selection |
| `Denevil` | [Duan et al. (ICLR 2024 / arXiv 2023)](https://arxiv.org/abs/2310.11053) | No public MoralPrompt export confirmed | Text generation | Proxy generation only |

## Reproducibility

This repo exposes two reproducibility layers on purpose: a public no-secret verification path for reviewers, and a live-run path for contributors who have API keys plus local datasets.

### 1. Public verification first

```bash
make bootstrap
```

This is the default reproducibility path for the research deliverable. It installs the pinned environment, runs the full test suite, and rebuilds the tracked release artifacts from the committed authoritative snapshot.

It does **not** require `.env`, API keys, or local benchmark datasets.

For UniMoral-specific provider-free checks, `make verify-unimoral-task-builders` verifies the RQ1-RQ4 registry entries with a tiny temporary fixture, and `make verify-unimoral-artifacts` checks the generated full-benchmark artifacts while allowing documented incomplete cells.
The UniMoral artifact builder can refresh docs and figures from the tracked UniMoral CSVs when the ignored raw `.eval` logs are not present.

### 2. Live benchmark smoke test

```bash
make setup
cp .env.example .env
make smoke
```

Populate `.env` only with the API keys and dataset paths needed for the benchmarks you want to run, such as `OPENROUTER_API_KEY`, `UNIMORAL_DATA_DIR`, and `SMID_DATA_DIR`.
If `uv` is not on `PATH` but the repo `.venv` already exists, `make test`, `make release`, `make audit`, and `make bootstrap` fall back to `.venv/bin/python` automatically. `make setup` still requires `uv`. If neither runner is available, those targets fail early with a clear setup error; you can also override the fallback path with `VENV_PYTHON=/absolute/path/to/python`.

### 3. Rebuild the public package directly

```bash
make release
```

This regenerates the tracked release package from the frozen source snapshot under `results/release/2026-04-19-option1/source/`. For the full public QA gate, use `make bootstrap` rather than stitching together `make test` and `make release` by hand.

Expected high-level outputs:

- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/family-size-progress.csv`
- `results/release/2026-04-19-option1/benchmark-comparison.csv`
- `results/release/2026-04-19-option1/ccd-choice-distribution.csv`
- `results/release/2026-04-19-option1/denevil-behavior-summary.csv`
- `results/release/2026-04-19-option1/denevil-prompt-family-breakdown.csv`
- `results/release/2026-04-19-option1/denevil-proxy-summary.csv`
- `results/release/2026-04-19-option1/denevil-proxy-examples.csv`
- `results/release/2026-04-19-option1/deepseek-sm-readout.csv`
- `results/release/2026-04-19-option1/saved-results-audit.csv`
- `results/release/2026-04-19-option1/benchmark-difficulty-summary.csv`
- `results/release/2026-04-19-option1/family-scaling-summary.csv`
- `results/release/2026-04-19-option1/release-manifest.json`
- `figures/release/option1_benchmark_accuracy_bars.svg`
- `figures/release/option1_benchmark_difficulty_profile.svg`
- `figures/release/option1_family_scaling_profile.svg`
- `figures/release/option1_ccd_choice_distribution.svg`
- `figures/release/option1_ccd_dominant_option_share.svg`
- `figures/release/option1_denevil_behavior_outcomes.svg`

For the full reproduction notes, see [docs/reproducibility.md](docs/reproducibility.md). For the repo layer map, see [docs/repo-architecture.md](docs/repo-architecture.md).

## Citation

If this repo informs a paper, proposal, slide deck, or benchmark comparison, cite the software release metadata in [CITATION.cff](CITATION.cff) and cite the benchmark papers listed above in [The Five Benchmark Papers](#the-five-benchmark-papers).

## Important Notes

- The current public matrix covers 5 families: `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma`.
- `Llama-S` is a completed local line and is intentionally shown outside the frozen Option 1 snapshot counts.
- `Denevil` is still proxy-only in the public release because the original paper-faithful `MoralPrompt` export is not available locally; proxy-only coverage and traceability evidence; moralprompt unavailable; not benchmark-faithful ethical-quality scoring.
- The detailed appendix lives in [results/release/2026-04-19-option1/](results/release/2026-04-19-option1/).

<!-- UNIMORAL_FULL_BENCHMARK_START -->
## UniMoral Full Benchmark Coverage

The release now implements all four UniMoral task definitions and exports scored artifacts where model runs completed, but the current model-line matrix is not yet fully complete. Incomplete or parse-limited cells are listed in `unimoral-failure-checklist.csv`; action prediction remains the legacy comparable scalar and is retained as RQ1.

| RQ | Task | Status | Strict complete | Reported cells | Primary metric | Mean | Range | Top line | Diagnostic read |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| RQ1 | Action prediction | complete | 16/16 | 16/16 | accuracy | 0.655 | 0.121 | DeepSeek-M (0.684) | diagnostic |
| RQ2 | Moral typology | incomplete | 15/16 | 16/16 | official_weighted_f1 | 0.315 | 0.080 | Llama-S (0.354) | moderately diagnostic |
| RQ3 | Factor attribution | incomplete | 14/16 | 15/16 | official_weighted_f1 | 0.256 | 0.022 | DeepSeek-S (0.264) | saturated |
| RQ4 | Consequence generation | incomplete | 14/16 | 15/16 | meteor | 0.116 | 0.081 | Llama-L (0.157) | moderately diagnostic |

Sample-level predictions for RQ2/RQ3/RQ4 are exported in `unimoral-sample-predictions.csv`; full Inspect `.eval` logs remain under the ignored `results/inspect/logs/2026-05-16-unimoral-full/` run directory.
The provider-free MiniMax handoff is tracked in [`unimoral-minimax-resume-plan.md`](results/release/2026-04-19-option1/unimoral-minimax-resume-plan.md).
The prompt-to-artifact completion audit is tracked in [`unimoral-completion-audit.md`](results/release/2026-04-19-option1/unimoral-completion-audit.md).

| Task | What it measures | Scoring note |
| --- | --- | --- |
| RQ1 action prediction | Selects the crowd-endorsed action from a two-action dilemma. | Accuracy from the existing release matrix. |
| RQ2 moral typology | Classifies the selected action as deontological, utilitarian, rights-based, or virtuous using `Action_criteria`. | Official-style weighted F1 is the primary release metric; exact-match membership accuracy is exported beside it. |
| RQ3 factor attribution | Classifies the main contributor to the annotator decision using `Contributing_factors`. | Official-style weighted F1 is the primary release metric; exact-match membership accuracy is exported beside it. |
| RQ4 consequence generation | Generates likely consequences for the selected action using `Consequence` references. | METEOR is the primary live scalar; BLEU and ROUGE-L are exported beside it. Official BERTScore F1 is exported in `unimoral-rq4-bertscore.csv` and merged into completed RQ4 rows when present. |

![UniMoral task heatmap](figures/release/option1_unimoral_task_heatmap.svg)

![UniMoral task spread](figures/release/option1_unimoral_task_spread.svg)

![UniMoral task rankings](figures/release/option1_unimoral_task_rankings.svg)
<!-- UNIMORAL_FULL_BENCHMARK_END -->
