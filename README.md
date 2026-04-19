# CEI Moral-Psych Benchmark Suite

[![CI](https://github.com/nordbyerik/CEI/actions/workflows/ci.yml/badge.svg)](https://github.com/nordbyerik/CEI/actions/workflows/ci.yml)

A reproducible extension of the CEI evaluation harness for five moral-psychology benchmarks:

- `UniMoral`
- `SMID`
- `Value Kaleidoscope`
- `CCD-Bench`
- `Denevil`

This repository now serves two roles:

1. A **benchmarking codebase** built on `Inspect AI` and `lm-evaluation-harness`.
2. A **research release** summarizing the current authoritative `Option 1` benchmark slice completed in this workspace.

## Release Snapshot

The current public release is the `2026-04-19 Option 1` package:

- `19 / 19` authoritative tasks complete
- `302,776` evaluated samples in the release package
- benchmark-faithful coverage for `UniMoral`, `SMID`, `Value Kaleidoscope`, and `CCD-Bench`
- a clearly labeled `FULCRA`-backed proxy for `Denevil` because the benchmark-faithful `MoralPrompt` export is still unavailable locally

Release artifacts live in [`results/release/2026-04-19-option1/`](results/release/2026-04-19-option1/) and figures live in [`figures/release/`](figures/release/).
The tracked source snapshot that makes the public package reproducible lives in [`results/release/2026-04-19-option1/source/authoritative-summary.csv`](results/release/2026-04-19-option1/source/authoritative-summary.csv).

## What This Repo Contributes

Compared with the original CEI ETHICS runner, this repo adds:

- `Inspect AI` task implementations for five moral-psych benchmarks
- local dataset wiring for public, gated, and multimodal benchmarks
- reusable launchers for formal model sweeps
- cross-namespace status recovery for interrupted runs
- publication-ready release summaries and figures generated from authoritative logs

Three release-level claims are directly supported by the tracked artifacts:

- the closed `Option 1` slice achieves complete coverage for the intended `Qwen`, `DeepSeek`, and `Gemma` tasks
- `Value Kaleidoscope` dominates sample volume in the current release
- `Denevil` remains clearly separated as a proxy line rather than a benchmark-faithful reproduction

## Key Results

### Model-Level Release Summary

| Model family | Faithful tasks | Proxy tasks | Samples | Faithful macro accuracy* |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

`*` Macro accuracy is averaged over tasks with an explicit accuracy metric. `CCD-Bench` and `Denevil` are excluded from that average because the current release records completion / choice-validity for those tasks rather than a comparable accuracy target.

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
- `results/release/2026-04-19-option1/topline-summary.md`
- `results/release/2026-04-19-option1/model-summary.csv`
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
- the currently running `Llama` and `MiniMax` experiments, which remain outside the closed `Option 1` release package

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
