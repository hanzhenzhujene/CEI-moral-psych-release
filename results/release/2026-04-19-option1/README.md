# Option 1 Release Artifacts

This directory contains the tracked, publication-facing outputs for Jenny Zhu's closed `2026-04-19 Option 1` release.

## Report Metadata

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Report date | `April 19, 2026` |
| Intended use | Group / mentor-facing report aligned to the April 14, 2026 moral-psych benchmark plan. |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Current closed release | `Option 1` |
| Model families in the closed release | `Qwen`, `DeepSeek`, `Gemma` |
| Supplementary local completion outside release | `Llama` small via `llama-3.2-11b-vision-instruct`, complete across `5` papers / `7` tasks |
| Prepared but not yet completed | `MiniMax` small route via `minimax-m2.1 + minimax-01` |
| Provider / temperature | `OpenRouter`, `temperature=0` |
| Current cost note | $35 baseline spend before the active family-size expansion launch on April 19, 2026, plus an approved image add-on queue projected at about $2.42 total (below the $5 cap). |
| CI reference | [Workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml); last verified successful run: [run 24634450927](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927) |

## Open These First

- `jenny-group-report.md`: the mentor-facing report with paper links, dataset access links, model roster, and interpretation notes
- `topline-summary.md`: the quickest narrative summary of counts and guardrails
- `release-manifest.json`: machine-readable entrypoint for downstream tooling, dashboards, or scripted checks
- [coverage figure](../../../figures/release/option1_coverage_matrix.svg): visual summary of faithful vs proxy coverage
- [accuracy figure](../../../figures/release/option1_accuracy_heatmap.svg): comparable accuracy snapshot across the closed release

## Regeneration

From the repo root:

```bash
make release
make audit
```

`make release` rebuilds the tracked public package from the committed source snapshot. `make audit` is the one-command public QA gate that runs tests and rebuilds the package together.

## Active Expansion Queues

- text-only family-size expansion: `results/inspect/full-runs/2026-04-19-family-size-text-expansion`
- image add-on queue under the $5 cap: `results/inspect/full-runs/2026-04-19-family-size-image-expansion`
- status labels: `Active` = running now, `Queued` = approved and waiting, `Complete` = finished

## Image Add-On Under The $5 Cap

These image jobs are limited to `SMID`, use only routes with a clean medium or large vision-capable mapping, and stay below a combined projected add-on spend of about `$2.42`.

| Family | Size slot | Image route | Benchmark | Estimated full-run cost | Status | Note |
| --- | --- | --- | --- | ---: | --- | --- |
| `Gemma` | Large | `openrouter/google/gemma-3-27b-it` | `SMID` | `$0.06` | Active | Cheapest selected image add-on route; running first in the capped SMID queue. |
| `Gemma` | Medium | `openrouter/google/gemma-3-12b-it` | `SMID` | `$0.07` | Queued | Queued after Gemma 27B in the same image-only run. |
| `Qwen` | Large | `openrouter/qwen/qwen3-vl-32b-instruct` | `SMID` | `$0.16` | Queued | Large Qwen image checkpoint under the same $5 cap. |
| `Llama` | Large | `openrouter/meta-llama/llama-4-maverick` | `SMID` | `$2.14` | Queued | Selected because the projected full SMID pass stays below the cap. |

Excluded from this capped image queue:

- DeepSeek: no vision route in the current family-size plan.
- Qwen medium: no clean Qwen medium VL route was locked for this pass.
- Llama medium: the chosen 70B route is text-only.
- MiniMax image: the shared `minimax-01` route projects to about $3.49 by itself and does not map cleanly onto separate medium / large size slots.

## Files

- `source/authoritative-summary.csv`: tracked source snapshot used to regenerate this release package
- `source/README.md`: provenance note for the tracked source snapshot
- `jenny-group-report.md`: mentor-ready narrative report with benchmark, model, and future-plan tables
- `topline-summary.md`: concise release narrative and topline counts
- `topline-summary.json`: machine-readable counterpart of the topline narrative
- `release-manifest.json`: machine-readable index of release files, counts, and interpretation guardrails
- `benchmark-catalog.csv`: benchmark registry with papers, dataset links, modalities, and release scope
- `model-summary.csv`: per-model task counts, sample counts, and macro accuracy
- `model-roster.csv`: exact OpenRouter model routes used in the closed release
- `supplementary-model-progress.csv`: local expansion status for families intentionally kept outside the closed release counts
- `future-model-plan.csv`: current family-by-size expansion plan
- `benchmark-summary.csv`: per-benchmark coverage and sample volume
- `faithful-metrics.csv`: task-level metrics for benchmark-faithful tasks
- `coverage-matrix.csv`: matrix used to render the release coverage figure

## Benchmark Registry

| Benchmark | Paper | Dataset / access | Modality | Tasks in repo | Current release scope |
| --- | --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. (ACL 2025 Findings)](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | `unimoral_action_prediction; unimoral_moral_typology; unimoral_factor_attribution; unimoral_consequence_generation` | Action prediction only |
| `SMID` | [Crone et al. (PLOS ONE 2018)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | `smid_moral_rating; smid_foundation_classification` | Moral rating + foundation classification |
| `Value Kaleidoscope` | [Sorensen et al. (AAAI 2024 / arXiv 2023)](https://arxiv.org/abs/2310.17681) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | `value_prism_relevance; value_prism_valence` | Relevance + valence |
| `CCD-Bench` | [Rahman et al. (arXiv 2025)](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | `ccd_bench_selection` | Selection |
| `Denevil` | [Duan et al. (ICLR 2024 submission / arXiv 2023)](https://arxiv.org/abs/2310.11905) | No stable public MoralPrompt download verified | Text generation | `denevil_generation; denevil_fulcra_proxy_generation` | FULCRA-backed proxy generation only |

## Current Model Roster

| Family | Exact model route | Modality | Benchmarks in release | Samples | Note |
| --- | --- | --- | --- | ---: | --- |
| `Qwen` | `openrouter/qwen/qwen3-8b` | Text | CCD-Bench; Denevil; UniMoral; Value Kaleidoscope | 97,004 | Closed-slice text route for UniMoral, Value Kaleidoscope, CCD-Bench, and Denevil proxy. |
| `Qwen` | `openrouter/qwen/qwen3-vl-8b-instruct` | Vision | SMID | 5,882 | Closed-slice vision route for SMID. |
| `DeepSeek` | `openrouter/deepseek/deepseek-chat-v3.1` | Text | CCD-Bench; Denevil; UniMoral; Value Kaleidoscope | 97,004 | Closed-slice DeepSeek route. No separate SMID vision route is present in the release. |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | Text + Vision | CCD-Bench; Denevil; SMID; UniMoral; Value Kaleidoscope | 102,886 | Paid recovery route that superseded the stalled free-tier Gemma namespace. |

## Model Summary

| Model family | Benchmark-faithful tasks | Proxy tasks | Samples | Benchmark-faithful macro accuracy |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

## Supplementary Local Expansion Status

| Family | Status relative to closed release | Exact route | Benchmark lines done | Benchmark lines still missing | Papers | Tasks | Samples | Benchmark-faithful macro accuracy | Note |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `Llama` | Completed locally, outside the closed Option 1 counts | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy | Benchmark-faithful Denevil via MoralPrompt | 5 | 7 | 102,886 | 0.428 | Combines the original 2026-04-19-option1-llama32-11b-vision successes (UniMoral + SMID moral rating) with recovery-v3 completions for the remaining five tasks after a temporary OpenRouter key-limit stall. |
| `MiniMax` | Prepared only, not yet completed locally | `minimax-m2.1 + minimax-01` | None yet | UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy; Benchmark-faithful Denevil via MoralPrompt | 0 | 0 | 0 | n/a | Small-route launchers are wired in the repo, but this family still needs its first formal paid run before it can be compared against the closed release models. |

## Benchmark Summary

| Benchmark | Unique task types | Evaluated lines | Models covered | Samples | Modes |
| --- | ---: | ---: | ---: | ---: | --- |
| `UniMoral` | 1 | 3 | 3 | 26,352 | benchmark_faithful |
| `SMID` | 2 | 4 | 2 | 11,764 | benchmark_faithful |
| `Value Kaleidoscope` | 2 | 6 | 3 | 196,560 | benchmark_faithful |
| `CCD-Bench` | 1 | 3 | 3 | 6,546 | benchmark_faithful |
| `Denevil` | 1 | 3 | 3 | 61,554 | proxy |

## Interpretation Guardrails

- Treat `Denevil` as a proxy line in this release.
- Treat the completed local `Llama` small line as supplementary evidence unless and until it is promoted into a new authoritative snapshot.
- Treat the release outputs here as authoritative for the closed `Option 1` slice.
- Use the raw `results/inspect/` tree only for local debugging or provenance checks.
