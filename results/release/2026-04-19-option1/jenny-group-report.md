# Jenny Zhu Moral-Psych Benchmark Report

Updated: `April 27, 2026`

Frozen public snapshot referenced here: `Option 1`, `April 19, 2026`

This report covers Jenny Zhu's five assigned moral-psych benchmark papers under the April 14, 2026 group plan. It separates the frozen public snapshot from the broader published family-size expansion work that is still being filled in.

## Results First

This section is the fastest summary for a mentor or collaborator: which lines already have usable results, what is directly comparable now, and which local expansions are complete versus partial.

| Line | Scope | Status | Coverage | Note |
| --- | --- | --- | --- | --- |
| `Qwen-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Qwen release line. |
| `DeepSeek-L` | Frozen Option 1 | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Primary large DeepSeek release line. |
| `Gemma-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Gemma release line. |
| `Llama-S` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally, outside the frozen Option 1 counts. |
| `Gemma-M` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Gemma-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Qwen-M` | Complete local line | Done | Earlier text checkpoints withdrawn; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Complete local line | Done | SMID recovery stands; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | SMID recovery complete; clean text rerun finished locally. |
| `Llama-M` | Complete local line | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Completed locally on April 22, 2026. |
| `Llama-L` | Attempted local line | Partial | SMID complete; UniMoral done; Value Prism Relevance preserved a 99.3% checkpoint before the run stalled. | SMID complete; text rerun is paused because OpenRouter credits are exhausted after a 99.3% Value Prism Relevance checkpoint. |
| `DeepSeek-M` | Attempted local line | Partial | No vision route; downstream attempt preserved earlier partial checkpoints, but the latest retry stopped immediately on OpenRouter credit exhaustion | Downstream attempt is currently blocked because OpenRouter credits are exhausted. |

### Latest Family-Size Progress Snapshot

This stacked overview is the quickest visual read on the current published four-family matrix.

![Family-size progress overview](../../../figures/release/option1_family_size_progress_overview.svg)

_Latest family-size progress overview. Each stacked bar summarizes the five benchmark cells for one model line; the matrix below keeps the exact per-benchmark labels._

### Current Comparable Accuracy Snapshot

Only benchmarks with a directly comparable accuracy metric are shown below. `CCD-Bench` and `Denevil` are excluded because they do not share the same accuracy target across lines. Rows include every line with at least one current comparable result; `n/a` marks benchmarks that are either incomplete on that line or intentionally withdrawn after response-format validation.

| Line | UniMoral action | SMID average | Value Kaleidoscope average | Coverage note |
| :--- | ---: | ---: | ---: | --- |
| `Qwen-S` | 0.647 | 0.368 | 0.682 | Frozen Option 1 line. |
| `DeepSeek-L` | 0.684 | n/a | 0.635 | Frozen large-class text line. No SMID vision route was included. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Complete locally across all five papers, but still outside the frozen Option 1 snapshot counts. SMID splits to 0.099 moral rating / 0.334 foundation classification, so the low average is a real task result. |
| `Llama-L` | n/a | 0.386 | n/a | SMID is complete locally, and the latest text attempt later reached a 27.4% Denevil proxy checkpoint before stalling. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Frozen Option 1 recovery line. |
| `Gemma-M` | 0.663 | 0.364 | 0.664 | Complete local medium line with both text and SMID image results finished. |
| `Gemma-L` | 0.661 | 0.412 | 0.656 | Complete local large line with both text and SMID image results finished. |

![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)

_Topline comparable-accuracy chart. Benchmark-level accuracy comparison across the latest available lines, with unavailable or withdrawn benchmark-line pairs shown explicitly._

## Report Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `April 27, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Current cost to date | `$40.73` |
| Purpose | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Current public matrix | `5 benchmarks x 4 model families x 3 size slots = 60 family-size-benchmark cells` |
| Benchmarks being tracked | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Model families in scope | `Qwen`, `DeepSeek`, `Llama`, `Gemma` |
| What the frozen snapshot actually covers | one closed `Option 1` slice across `Qwen`, `DeepSeek`, and `Gemma` |
| Extra completed local line outside release | `Llama` small complete via `llama-3.2-11b-vision-instruct` across `5` papers / `7` tasks |
| Run provider / temperature | `OpenRouter`, `temperature=0` |
| Current live reruns | No currently published line is still running locally. |
| Next restart focus | Add OpenRouter credits, then relaunch `Llama-L`. |
| Release guardrail | Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables. |
| CI status reference | [CI workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml); latest verified passing run: [24634450927](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927) |
| Total evaluated samples in this release | `302,776` |

### Current Operations Highlights

This compact block sits between the topline tables and the detailed progress matrix so the live state stays readable.

- Active open-source reruns: none are currently shown in the published matrix.
- Stalled or queued follow-up work: `Llama-L` (SMID complete; text rerun is paused because OpenRouter credits are exhausted after a 99.3% Value Prism Relevance checkpoint) and `DeepSeek-M` (Downstream attempt is currently blocked because OpenRouter credits are exhausted).
- Complete local lines beyond the frozen `Option 1` slice: `Llama-S`, `Gemma-M`, `Gemma-L`, `Qwen-M`, `Qwen-L`, and `Llama-M`.
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
| `DeepSeek-M text batch` | Partial | Downstream attempt is currently blocked because OpenRouter credits are exhausted. |
| `Llama-L SMID` | Done | The large Llama vision line is complete locally. |
| `Next queued text lines` | Queue | `Llama-L` remains the next visible follow-up. |

Plain-language terms: [`docs/how-to-read-results.md`](../../../docs/how-to-read-results.md)

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

## The Five Papers / Benchmarks Under Test

| Benchmark | Citation | Paper link | Dataset / access link | Modality | What this repo tests now |
| --- | --- | --- | --- | --- | --- |
| `UniMoral` | Kumar et al. (ACL 2025 Findings) | [paper](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | Action prediction only |
| `SMID` | Crone et al. (PLOS ONE 2018) | [paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | Moral rating + foundation classification |
| `Value Kaleidoscope` | Sorensen et al. (AAAI 2024 / arXiv 2023) | [paper](https://arxiv.org/abs/2310.17681) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | Relevance + valence |
| `CCD-Bench` | Rahman et al. (arXiv 2025) | [paper](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | Selection |
| `Denevil` | Duan et al. (ICLR 2024 submission / arXiv 2023) | [paper](https://arxiv.org/abs/2310.11905) | No public MoralPrompt export confirmed | Text generation | Proxy generation only |

## Model Families And Size Routes

| Family | Small route | Medium route | Large route |
| --- | --- | --- | --- |
| `Qwen` | Text: `openrouter/qwen/qwen3-8b`<br/>Vision: `openrouter/qwen/qwen3-vl-8b-instruct` | `openrouter/qwen/qwen3-14b` | Text: `openrouter/qwen/qwen3-32b`<br/>Vision: `openrouter/qwen/qwen2.5-vl-72b-instruct (recovery complete)` |
| `DeepSeek` | No distinct small OpenRouter route exposed | `openrouter/deepseek/deepseek-r1-distill-qwen-32b` | `openrouter/deepseek/deepseek-chat-v3.1` |
| `Llama` | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | `openrouter/meta-llama/llama-3.3-70b-instruct` | `openrouter/meta-llama/llama-4-maverick` |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | `openrouter/google/gemma-3-12b-it` | `openrouter/google/gemma-3-27b-it` |

## Full Family-Size Progress Matrix

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | --- |
| `Qwen-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 line. |
| `Qwen-M` | Done | TBD | Done | Done | Proxy | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Done | Done | Done | Done | Proxy | SMID recovery complete; clean text rerun finished locally. |
| `DeepSeek-S` | TBD | - | TBD | TBD | TBD | No distinct small DeepSeek route is fixed yet. |
| `DeepSeek-M` | Partial | - | Partial | Partial | Partial | No vision route; downstream attempt is currently blocked because OpenRouter credits are exhausted. |
| `DeepSeek-L` | Done | - | Done | Done | Proxy | Frozen large text line; no SMID route was included. |
| `Llama-S` | Done | Done | Done | Done | Proxy | Complete locally across all five papers. |
| `Llama-M` | Done | - | Done | Done | Proxy | No SMID route; medium text line completed locally on April 22, 2026. |
| `Llama-L` | Done | Done | Partial | Done | Partial | SMID complete; text rerun is paused because OpenRouter credits are exhausted after a 99.3% Value Prism Relevance checkpoint. |
| `Gemma-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 recovery line. |
| `Gemma-M` | Done | Done | Done | Done | Proxy | Complete local line across all five papers. |
| `Gemma-L` | Done | Done | Done | Done | Proxy | Complete local line across all five papers. |

## Supporting Figures

Figures 1 and 2 are already embedded above in context; this gallery keeps the remaining visuals together without repeating them.

| Figure | Why it matters | File |
| --- | --- | --- |
| Figure 1 | Latest line-level progress across the current published family-size matrix. | [option1_family_size_progress_overview.svg](../../../figures/release/option1_family_size_progress_overview.svg) |
| Figure 2 | Cross-model comparison for the benchmarks that share a directly comparable accuracy metric. | [option1_benchmark_accuracy_bars.svg](../../../figures/release/option1_benchmark_accuracy_bars.svg) |
| Figure 3 | Heatmap of the latest available comparable metrics, including incomplete-benchmark treatment. | [option1_accuracy_heatmap.svg](../../../figures/release/option1_accuracy_heatmap.svg) |
| Figure 4 | Coverage view of which benchmark lines are paper-setup, proxy-only, or not in the frozen release. | [option1_coverage_matrix.svg](../../../figures/release/option1_coverage_matrix.svg) |
| Figure 5 | Sample concentration by benchmark with paper-setup versus proxy volume separated. | [option1_sample_volume.svg](../../../figures/release/option1_sample_volume.svg) |

![Accuracy heatmap](../../../figures/release/option1_accuracy_heatmap.svg)

_Figure 3. Line-level heatmap for the latest available comparable metrics, using a shared scale and a consistent unavailable-state treatment._

![Coverage matrix](../../../figures/release/option1_coverage_matrix.svg)

_Figure 4. Coverage matrix showing which benchmark lines are paper-setup, proxy-only, or absent from the frozen release._

![Sample volume by benchmark](../../../figures/release/option1_sample_volume.svg)

_Figure 5. Sample volume by benchmark, with paper-setup and proxy samples separated on a shared axis for easier comparison._

## Frozen Option 1 Summary

| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |
| :--- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

## Interpretation Notes

- The current public matrix covers 4 families: `Qwen`, `DeepSeek`, `Llama`, `Gemma`.
- `Llama-S` is complete locally and should be reported as an extra completed local line outside the frozen Option 1 counts.
- `DeepSeek` does not yet have a frozen SMID vision route in this deliverable.
- `Denevil` is still proxy-only in the public release because the original paper-faithful `MoralPrompt` export is not available locally.

## Safe One-Sentence Framing

> This repository contains Jenny Zhu's CEI moral-psych benchmark deliverable for five target papers, with a frozen Option 1 snapshot over Qwen, DeepSeek, and Gemma, an extra completed Llama small line outside the frozen counts, and a clearly labeled family-size progress matrix for the broader five-family plan.
