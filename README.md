# CEI Moral-Psych Benchmark Suite

[![CI](https://img.shields.io/github/actions/workflow/status/hanzhenzhujene/CEI-moral-psych-release/ci.yml?branch=main&label=CI)](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml)

This repo is Jenny Zhu's CEI moral-psych benchmark deliverable for five assigned benchmark papers.

It combines three things in one clean public surface:

1. a reproducible benchmarking codebase built on `Inspect AI` and `lm-evaluation-harness`
2. a frozen `Option 1` snapshot for the first formal public release
3. a clearly labeled progress matrix for the larger `5 benchmarks x 5 model families x 3 size slots` plan

Quick links:

- [Jenny's group report](results/release/2026-04-19-option1/jenny-group-report.md)
- [Release appendix](results/release/2026-04-19-option1/README.md)
- [Frozen source snapshot](results/release/2026-04-19-option1/source/authoritative-summary.csv)
- [Reproducibility guide](docs/reproducibility.md)

## Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `April 20, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Group plan target | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Clarified model families used here | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |
| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |
| Supplementary completed line | `Llama-S`, complete locally across all five papers |
| MiniMax small status | formal attempt exists, but the current line failed and is not counted as complete |
| Run setting | `OpenRouter`, `temperature=0` |

## Progress Legend

- `done`: benchmark line finished with a usable result
- `proxy`: finished, but only with a substitute proxy dataset instead of the paper's original setup
- `live`: currently running
- `error`: formal attempt exists, but the current result is not usable
- `queue`: approved and queued next
- `tbd`: family-size route is not frozen yet
- `-`: no run is planned on that line right now

## Family-Size Progress Matrix

This is the main repo-level status table for the full group plan.

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |
| --- | --- | --- | --- | --- | --- | --- |
| `Qwen-S` | done | done | done | done | proxy | Frozen Option 1 line. |
| `Qwen-M` | queue | tbd | queue | queue | queue | Text route is queued. No medium vision route is locked for SMID yet. |
| `Qwen-L` | queue | queue | queue | queue | queue | Text and vision checkpoints are both queued. |
| `MiniMax-S` | error | error | error | error | error | Formal small-model run was attempted, but the line hit OpenRouter key-limit errors and is not counted as complete. |
| `MiniMax-M` | queue | tbd | queue | queue | queue | Text route is queued. Separate medium vision route is not fixed yet. |
| `MiniMax-L` | queue | tbd | queue | queue | queue | Text route is queued. Separate large vision route is not fixed yet. |
| `DeepSeek-S` | tbd | - | tbd | tbd | tbd | A smaller DeepSeek baseline has not been frozen yet. No vision route is in scope. |
| `DeepSeek-M` | queue | - | queue | queue | queue | Medium text route is queued. No vision route is in scope. |
| `DeepSeek-L` | done | - | done | done | proxy | Frozen Option 1 large-class text line. No SMID vision route was included. |
| `Llama-S` | done | done | done | done | proxy | Complete locally across all five papers, but not folded into the frozen Option 1 counts. |
| `Llama-M` | queue | - | queue | queue | queue | Text-only medium route is queued. No SMID run is planned on this line. |
| `Llama-L` | queue | queue | queue | queue | queue | Large text and SMID vision checkpoints are both queued. |
| `Gemma-S` | done | done | done | done | proxy | Frozen Option 1 recovery line. |
| `Gemma-M` | queue | queue | queue | queue | queue | Text and SMID queues are both approved but not started yet. |
| `Gemma-L` | done | live | live | queue | queue | Large Gemma is the actively running family-size checkpoint right now. |

The same matrix is also saved as [family-size-progress.csv](results/release/2026-04-19-option1/family-size-progress.csv).

## The Five Benchmark Papers

| Benchmark | Paper | Dataset / access | Modality | What this repo tests now |
| --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. (ACL 2025 Findings)](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | Action prediction |
| `SMID` | [Crone et al. (PLOS ONE 2018)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | Moral rating and foundation classification |
| `Value Kaleidoscope` | [Sorensen et al. (AAAI 2024 / arXiv 2023)](https://arxiv.org/abs/2310.17681) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | Relevance and valence |
| `CCD-Bench` | [Rahman et al. (arXiv 2025)](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench), [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | Selection |
| `Denevil` | [Duan et al. (ICLR 2024 submission / arXiv 2023)](https://arxiv.org/abs/2310.11905) | paper-faithful `MoralPrompt` export not available locally | Text generation | Proxy-only generation line for now |

## Model Families And Size Routes

| Family | Small route | Medium route | Large route |
| --- | --- | --- | --- |
| `Qwen` | `text: openrouter/qwen/qwen3-8b; vision: openrouter/qwen/qwen3-vl-8b-instruct` | `openrouter/qwen/qwen3-14b` | `text: openrouter/qwen/qwen3-32b; vision: openrouter/qwen/qwen3-vl-32b-instruct` |
| `MiniMax` | `text: openrouter/minimax/minimax-m2.1; vision: openrouter/minimax/minimax-01` | `openrouter/minimax/minimax-m2.5` | `openrouter/minimax/minimax-m2.7` |
| `DeepSeek` | `TBD` | `openrouter/deepseek/deepseek-r1-distill-qwen-32b` | `openrouter/deepseek/deepseek-chat-v3.1` |
| `Llama` | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | `openrouter/meta-llama/llama-3.3-70b-instruct` | `openrouter/meta-llama/llama-4-maverick` |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | `openrouter/google/gemma-3-12b-it` | `openrouter/google/gemma-3-27b-it` |

## Current Comparable Accuracy Snapshot

Only benchmarks with a directly comparable accuracy metric are shown below. `CCD-Bench` and `Denevil` are intentionally excluded from this comparison table because they do not share the same target metric across lines.

| Line | UniMoral action | SMID average | Value Kaleidoscope average | Coverage note |
| --- | ---: | ---: | ---: | --- |
| `Qwen-S` | 0.647 | 0.368 | 0.682 | Frozen Option 1 line. |
| `DeepSeek-L` | 0.684 | n/a | 0.635 | Frozen large-class text line. No SMID vision route was included. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Complete locally across all five papers, but still supplementary to the frozen Option 1 snapshot. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Frozen Option 1 recovery line. |

The underlying table is saved as [benchmark-comparison.csv](results/release/2026-04-19-option1/benchmark-comparison.csv).

![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)

## Reproducibility

### 1. Setup

```bash
make setup
cp .env.example .env
```

Populate `.env` with API keys such as `OPENROUTER_API_KEY` and local benchmark paths such as `UNIMORAL_DATA_DIR` and `SMID_DATA_DIR`.

### 2. Verify the repo

```bash
make test
```

### 3. Rebuild the public package

```bash
make release
```

This regenerates the tracked release package from the frozen source snapshot under `results/release/2026-04-19-option1/source/`.

Expected high-level outputs:

- `results/release/2026-04-19-option1/jenny-group-report.md`
- `results/release/2026-04-19-option1/family-size-progress.csv`
- `results/release/2026-04-19-option1/benchmark-comparison.csv`
- `results/release/2026-04-19-option1/release-manifest.json`
- `figures/release/option1_benchmark_accuracy_bars.svg`
- `figures/release/option1_coverage_matrix.svg`

For the full reproduction notes, see [docs/reproducibility.md](docs/reproducibility.md).

## Important Notes

- The full `5 x 5 x 3` matrix is the target plan, not a claim that all 75 cells are already complete.
- `Llama-S` is a completed local line and is intentionally shown as supplementary to the frozen Option 1 snapshot.
- `MiniMax-S` should currently be reported as a failed formal attempt, not as a completed comparison point.
- `Denevil` is still proxy-only in the public release because the original paper-faithful `MoralPrompt` export is not available locally.
- The detailed appendix lives in [results/release/2026-04-19-option1/](results/release/2026-04-19-option1/).
