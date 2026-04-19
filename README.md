# CEI Moral-Psych Benchmark Suite

[![CI Workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml)

A reproducible extension of the CEI evaluation harness plus Jenny Zhu's April 19, 2026 moral-psych benchmark report for five target papers:

- `UniMoral`
- `SMID`
- `Value Kaleidoscope`
- `CCD-Bench`
- `Denevil`

This repository serves two linked purposes:

1. A **benchmarking codebase** built on `Inspect AI` and `lm-evaluation-harness`.
2. A **mentor-ready research report** summarizing Jenny's current authoritative `Option 1` slice.

## Report Metadata

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Report date | `April 19, 2026` |
| Intended use | Group / research mentor update aligned to the April 14, 2026 plan |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Current closed release | `Option 1` |
| Model families in the closed release | `Qwen`, `DeepSeek`, `Gemma` |
| Supplementary local completion outside release | `Llama` small via `llama-3.2-11b-vision-instruct`, complete across `5` papers / `7` tasks |
| Prepared but not yet completed | `MiniMax` small route via `minimax-m2.1` + `minimax-01` |
| Provider / temperature | `OpenRouter`, `temperature=0` |
| Current cost note | `$25` current spend / budget note provided by Jenny |
| CI reference | [workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml), last verified passing run [24634450927](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927) |

Detailed report artifacts live in [`results/release/2026-04-19-option1/`](results/release/2026-04-19-option1/), including [`jenny-group-report.md`](results/release/2026-04-19-option1/jenny-group-report.md) and the tracked source snapshot [`source/authoritative-summary.csv`](results/release/2026-04-19-option1/source/authoritative-summary.csv).

## Release Snapshot

The current public release is the `2026-04-19 Option 1` package:

- `19 / 19` authoritative tasks complete
- `302,776` evaluated samples in the release package
- benchmark-faithful coverage for `UniMoral`, `SMID`, `Value Kaleidoscope`, and `CCD-Bench`
- a clearly labeled `FULCRA`-backed proxy for `Denevil` because the benchmark-faithful `MoralPrompt` export is still unavailable locally
- a completed supplementary `Llama` small line outside the closed release, covering all five benchmark papers across `102,886` samples

## Five Benchmarks Under Test

| Benchmark | Citation | Paper | Dataset / access | Modality | Tasks in repo | Current release scope |
| --- | --- | --- | --- | --- | --- | --- |
| `UniMoral` | Kumar et al. (ACL 2025 Findings) | [paper](https://aclanthology.org/2025.acl-long.294/) | [HF dataset](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | `unimoral_action_prediction`; `unimoral_moral_typology`; `unimoral_factor_attribution`; `unimoral_consequence_generation` | Action prediction only |
| `SMID` | Crone et al. (PLOS ONE 2018) | [paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project](https://osf.io/ngzwx/) | Vision | `smid_moral_rating`; `smid_foundation_classification` | Moral rating + foundation classification |
| `Value Kaleidoscope` | Sorensen et al. (AAAI 2024 / arXiv 2023) | [paper](https://arxiv.org/abs/2310.17681) | [HF dataset](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | `value_prism_relevance`; `value_prism_valence` | Relevance + valence |
| `CCD-Bench` | Rahman et al. (arXiv 2025) | [paper](https://arxiv.org/abs/2510.03553) | [repo](https://github.com/smartlab-nyu/CCD-Bench), [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | `ccd_bench_selection` | Selection |
| `Denevil` | Duan et al. (ICLR 2024 submission / arXiv 2023) | [paper](https://arxiv.org/abs/2310.11905) | no stable public `MoralPrompt` download verified | Text generation | `denevil_generation`; `denevil_fulcra_proxy_generation` | `FULCRA`-backed proxy only |

## Current Models In The Closed Release

| Family | Exact model route | Size hint | Modality | Benchmarks in release | Notes |
| --- | --- | --- | --- | --- | --- |
| `Qwen` | `openrouter/qwen/qwen3-8b` | 8B | Text | `UniMoral`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` proxy | Closed-slice text route |
| `Qwen` | `openrouter/qwen/qwen3-vl-8b-instruct` | 8B VL | Vision | `SMID` | Closed-slice vision route |
| `DeepSeek` | `openrouter/deepseek/deepseek-chat-v3.1` | provider route | Text | `UniMoral`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` proxy | No DeepSeek vision route in the current release |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | 4B | Text + Vision | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` proxy | Paid recovery route supersedes the stalled free-tier namespace |

## Next Step: Family x Size Expansion

| Family | Closed release status | Current route already present in repo | Small | Medium | Large |
| --- | --- | --- | --- | --- | --- |
| `Qwen` | included | `qwen3-8b`, `qwen3-vl-8b-instruct` | current 8B routes | TBD with group roster | TBD with group roster |
| `MiniMax` | prepared only, not in closed release | `minimax-m2.1`, `minimax-01` launchers present | current launcher wired; no formal local completion yet | TBD with group roster | TBD with group roster |
| `DeepSeek` | included | `deepseek-chat-v3.1` | TBD with group roster | TBD with group roster | TBD with group roster |
| `Llama` | completed locally, not promoted into closed release | `llama-3.2-11b-vision-instruct` completed locally | current 11B route complete across 5 papers / 7 tasks | TBD with group roster | TBD with group roster |
| `Gemma` | included | `gemma-3-4b-it` | current 4B route | TBD with group roster | TBD with group roster |

## Supplementary Local Expansion Progress

| Family | Status relative to closed release | Exact route | Papers | Tasks | Benchmark-faithful tasks | Proxy tasks | Samples | Benchmark-faithful macro accuracy | Note |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `Llama` | completed locally, outside the closed `Option 1` counts | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | 5 | 7 | 6 | 1 | 102,886 | 0.428 | combines the original namespace successes (`UniMoral` + `SMID` moral rating) with `recovery-v3` completions for the remaining five tasks after a temporary OpenRouter key-limit stall |
| `MiniMax` | prepared only, not yet completed locally | `minimax-m2.1` + `minimax-01` | 0 | 0 | 0 | 0 | 0 | n/a | small-route launchers are wired in the repo, but this family still needs its first formal paid run |

## Key Results

### Model-Level Release Summary

| Model family | Benchmark-faithful tasks | Proxy tasks | Samples | Benchmark-faithful macro accuracy* |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

`*` Macro accuracy is averaged over benchmark-faithful tasks with an explicit accuracy metric. `CCD-Bench` and `Denevil` are excluded from that average because the current release records completion / choice-validity for those tasks rather than a comparable accuracy target.

## What This Repo Contributes

Compared with the original CEI ETHICS runner, this repo adds:

- `Inspect AI` task implementations for five moral-psych benchmarks
- local dataset wiring for public, gated, and multimodal benchmarks
- reusable launchers for formal model sweeps
- cross-namespace status recovery for interrupted runs
- publication-ready release summaries, figures, and mentor-facing report tables generated from authoritative logs

Three release-level claims are directly supported by the tracked artifacts:

- the closed `Option 1` slice achieves complete coverage for the intended `Qwen`, `DeepSeek`, and `Gemma` tasks
- `Value Kaleidoscope` dominates sample volume in the current release
- `Denevil` remains clearly separated as a proxy line rather than a benchmark-faithful reproduction

### Figures

#### Coverage Matrix

![Coverage matrix](figures/release/option1_coverage_matrix.svg)

Green cells indicate benchmark-faithful coverage, amber marks the explicit `Denevil` proxy, and gray is reserved for models or tasks outside the closed release.

#### Accuracy Heatmap

![Accuracy heatmap](figures/release/option1_accuracy_heatmap.svg)

The heatmap shows only directly comparable accuracy-based tasks, which prevents `CCD-Bench` and `Denevil` from being overinterpreted as if they shared the same target metric.

#### Sample Volume

![Sample volume](figures/release/option1_sample_volume.svg)

Most samples come from `Value Kaleidoscope`, while the proxy-only `Denevil` contribution is isolated so readers can separate coverage from methodological faithfulness.

## Repository Layout

```text
CEI/
├── README.md
├── Makefile                          # one-command setup, testing, and release targets
├── pyproject.toml                    # uv workspace root
├── uv.lock                           # pinned environment lockfile
├── .env.example                      # API keys + local dataset paths
├── docs/
│   ├── README.md                     # doc index
│   ├── reproducibility.md            # release and benchmark reproduction guide
│   ├── data-access.md                # benchmark-by-benchmark dataset requirements
│   └── history/                      # archived process notes and mentor-facing briefs
├── .github/
│   └── workflows/ci.yml              # GitHub Actions regression checks
├── figures/
│   ├── README.md                     # figure-generation notes
│   └── release/                      # publication-ready SVG figures
├── results/
│   ├── README.md                     # results layout and retention policy
│   ├── lm-harness/                   # legacy ETHICS baseline outputs
│   ├── release/
│   │   └── 2026-04-19-option1/       # curated release tables, source snapshot, and markdown summaries
│   └── inspect/                      # raw local logs and full-run artifacts (gitignored)
├── scripts/
│   ├── README.md                     # script index
│   ├── build_authoritative_option1_status.py
│   ├── build_release_artifacts.py
│   ├── summarize_inspect_eval_progress.py
│   └── *_runs*.sh                    # formal run launchers
├── src/
│   ├── inspect/                      # Inspect AI benchmark implementations
│   └── lm-evaluation-harness/        # legacy ETHICS baseline path
└── tests/
```

## Quickstart

### 1. Setup

```bash
make setup
cp .env.example .env
```

If `uv` is installed but not on your shell `PATH`, you can override it with `make UV=/absolute/path/to/uv <target>`.

Populate `.env` with API keys and local dataset paths for the benchmarks you intend to run.

### 2. Verify the codebase

```bash
make test
```

### 3. Rebuild the release package

```bash
make release
```

This command regenerates the public package from the tracked authoritative snapshot already stored in the repo.

Expected outputs:

- `results/release/2026-04-19-option1/source/authoritative-summary.csv`
- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/topline-summary.md`
- `results/release/2026-04-19-option1/benchmark-catalog.csv`
- `results/release/2026-04-19-option1/model-summary.csv`
- `results/release/2026-04-19-option1/model-roster.csv`
- `results/release/2026-04-19-option1/supplementary-model-progress.csv`
- `results/release/2026-04-19-option1/future-model-plan.csv`
- `results/release/2026-04-19-option1/benchmark-summary.csv`
- `results/release/2026-04-19-option1/faithful-metrics.csv`
- `results/release/2026-04-19-option1/coverage-matrix.csv`
- `figures/release/option1_coverage_matrix.svg`
- `figures/release/option1_accuracy_heatmap.svg`
- `figures/release/option1_sample_volume.svg`

## Reproducing a Benchmark Run

The release package above is generated from completed local runs. To execute the harness itself, use the `Inspect AI` path in `src/inspect/`.

### Smoke run

```bash
make smoke
```

This runs a small `UniMoral` sanity check at `temperature=0` using the configured local dataset path.

### Example task-level run

```bash
uv run --package cei-inspect python src/inspect/run.py \
  --tasks src/inspect/evals/moral_psych.py::unimoral_action_prediction \
  --model openrouter/qwen/qwen3-8b \
  --temperature 0 \
  --limit 10 \
  --no_sandbox
```

### Maintainer-only provenance refresh

```bash
make refresh-authoritative
make release
```

Use this only if you also have the local raw `results/inspect/full-runs/` directories used to assemble the authoritative snapshot.

## Benchmark Scope and Caveats

### Benchmark-faithful in the current release

- `UniMoral`: action prediction
- `SMID`: moral rating, foundation classification
- `Value Kaleidoscope`: relevance, valence
- `CCD-Bench`: selection

### Proxy in the current release

- `Denevil`: `denevil_fulcra_proxy_generation`

The current `Denevil` line is a **proxy**, not a benchmark-faithful `MoralPrompt` reproduction. The README, release tables, and figures all preserve that distinction.

### Not yet part of the public release

- full large / medium / small sweeps for all target model families
- a benchmark-faithful `Denevil` run using `MoralPrompt`
- the prepared but not yet completed `MiniMax` family
- promotion of the completed local `Llama` small line into a future authoritative release snapshot, if the group wants it counted formally

## Data Access

Several datasets are not redistributable in the repo itself.

- `UniMoral` and `Value Kaleidoscope` require local exports or gated access
- `SMID` requires local image assets
- `Denevil` requires a local export for benchmark-faithful evaluation

Use `.env` rather than hard-coding local paths.

## Documentation

Start here if you are new to the repo:

- [`docs/reproducibility.md`](docs/reproducibility.md)
- [`docs/data-access.md`](docs/data-access.md)
- [`docs/legacy-baselines.md`](docs/legacy-baselines.md)
- [`docs/README.md`](docs/README.md)
- [`figures/README.md`](figures/README.md)
- [`scripts/README.md`](scripts/README.md)
- [`results/release/2026-04-19-option1/README.md`](results/release/2026-04-19-option1/README.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Acknowledgements

This repo builds on:

- `Inspect AI` from UK AISI
- `lm-evaluation-harness` from EleutherAI
- the CEI evaluation workflow used in Jenny's April 2026 moral-psych benchmark study
