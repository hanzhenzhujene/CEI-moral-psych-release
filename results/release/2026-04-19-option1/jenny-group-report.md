# Jenny Zhu Moral-Psych Benchmark Report

Updated: `April 20, 2026`

Frozen public snapshot referenced here: `Option 1`, `April 19, 2026`

This report covers Jenny Zhu's five assigned moral-psych benchmark papers under the April 14, 2026 group plan. It separates the frozen public snapshot from the broader family-size expansion work that is still being filled in.

## Report Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `April 20, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Current cost to date | `$35` |
| Purpose | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Full target matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |
| Benchmarks being tracked | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Agreed model families | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |
| What the frozen snapshot actually covers | one closed `Option 1` slice across `Qwen`, `DeepSeek`, and `Gemma` |
| Extra completed local line outside release | `Llama` small complete via `llama-3.2-11b-vision-instruct` across `5` papers / `7` tasks |
| MiniMax small status | formal attempt exists, but the current line failed and is not counted as complete |
| Run provider / temperature | `OpenRouter`, `temperature=0` |
| Current operations note | This repo was updated on April 20, 2026. The frozen public snapshot remains Option 1 from April 19, 2026. The family-size image queue has completed, the active text queue is currently on the Gemma-L Denevil proxy task, and the Qwen-L SMID recovery route is now prepared with qwen2.5-vl-72b plus a non-Alibaba provider allowlist. |
| CI status reference | [CI workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml); latest verified passing run: [24634450927](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927) |
| Total evaluated samples in this release | `302,776` |

Plain-language terms: [`docs/how-to-read-results.md`](../../../docs/how-to-read-results.md)

## Progress Legend

- `done`: benchmark line finished with a usable result
- `proxy`: finished, but only with a substitute proxy dataset instead of the paper's original setup
- `live`: currently running
- `error`: formal attempt exists, but the current result is not usable
- `queue`: approved and queued next
- `tbd`: family-size route is not frozen yet
- `-`: no run is planned on that line right now

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
| `Qwen` | `text: openrouter/qwen/qwen3-8b; vision: openrouter/qwen/qwen3-vl-8b-instruct` | `openrouter/qwen/qwen3-14b` | `text: openrouter/qwen/qwen3-32b; vision: openrouter/qwen/qwen2.5-vl-72b-instruct (recovery prep)` |
| `MiniMax` | `text: openrouter/minimax/minimax-m2.1; vision: openrouter/minimax/minimax-01` | `openrouter/minimax/minimax-m2.5` | `openrouter/minimax/minimax-m2.7` |
| `DeepSeek` | `TBD` | `openrouter/deepseek/deepseek-r1-distill-qwen-32b` | `openrouter/deepseek/deepseek-chat-v3.1` |
| `Llama` | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | `openrouter/meta-llama/llama-3.3-70b-instruct` | `openrouter/meta-llama/llama-4-maverick` |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | `openrouter/google/gemma-3-12b-it` | `openrouter/google/gemma-3-27b-it` |

## Full Family-Size Progress Matrix

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |
| --- | --- | --- | --- | --- | --- | --- |
| `Qwen-S` | done | done | done | done | proxy | Frozen Option 1 line. |
| `Qwen-M` | queue | tbd | queue | queue | queue | Text route is queued. No medium vision route is locked for SMID yet. |
| `Qwen-L` | queue | error | queue | queue | queue | Large text route is still queued. The first Qwen-L SMID attempt failed quickly on Alibaba moderation, and a safer qwen2.5-vl-72b recovery route is now prepared with non-Alibaba provider routing. |
| `MiniMax-S` | error | error | error | error | error | Formal small-model run was attempted, but the line hit OpenRouter key-limit errors and is not counted as complete. |
| `MiniMax-M` | queue | tbd | queue | queue | queue | Text route is queued. Separate medium vision route is not fixed yet. |
| `MiniMax-L` | queue | tbd | queue | queue | queue | Text route is queued. Separate large vision route is not fixed yet. |
| `DeepSeek-S` | tbd | - | tbd | tbd | tbd | A smaller DeepSeek baseline has not been frozen yet. No vision route is in scope. |
| `DeepSeek-M` | queue | - | queue | queue | queue | Medium text route is queued. No vision route is in scope. |
| `DeepSeek-L` | done | - | done | done | proxy | Frozen Option 1 large-class text line. No SMID vision route was included. |
| `Llama-S` | done | done | done | done | proxy | Complete locally across all five papers, but not folded into the frozen Option 1 counts. |
| `Llama-M` | queue | - | queue | queue | queue | Text-only medium route is queued. No SMID run is planned on this line. |
| `Llama-L` | queue | done | queue | queue | queue | Large Llama SMID is complete. The text route is still queued. |
| `Gemma-S` | done | done | done | done | proxy | Frozen Option 1 recovery line. |
| `Gemma-M` | queue | done | queue | queue | queue | Gemma-M SMID is complete. The text route is still queued behind the active Gemma-L run. |
| `Gemma-L` | done | done | done | done | live | Large Gemma has finished UniMoral, SMID, Value Kaleidoscope, and CCD-Bench. Only the Denevil proxy task is still live. |

## Current Comparable Accuracy Snapshot

Only benchmarks with a directly comparable accuracy metric are shown below. `CCD-Bench` and `Denevil` are excluded because they do not share the same accuracy target across lines.

| Line | UniMoral action | SMID average | Value Kaleidoscope average | Coverage note |
| --- | ---: | ---: | ---: | --- |
| `Qwen-S` | 0.647 | 0.368 | 0.682 | Frozen Option 1 line. |
| `DeepSeek-L` | 0.684 | n/a | 0.635 | Frozen large-class text line. No SMID vision route was included. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Complete locally across all five papers, but still outside the frozen Option 1 snapshot counts. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Frozen Option 1 recovery line. |

![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)

## Frozen Option 1 Summary

| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

## Interpretation Notes

- The `5 x 5 x 3` matrix is the target plan, not a claim that all 75 cells are already complete.
- `Llama-S` is complete locally and should be reported as an extra completed local line outside the frozen Option 1 counts.
- `MiniMax-S` should currently be reported as a failed formal attempt, not as a completed benchmark line.
- `DeepSeek` does not yet have a frozen SMID vision route in this deliverable.
- `Denevil` is still proxy-only in the public release because the original paper-faithful `MoralPrompt` export is not available locally.

## Safe One-Sentence Framing

> This repository contains Jenny Zhu's CEI moral-psych benchmark deliverable for five target papers, with a frozen Option 1 snapshot over Qwen, DeepSeek, and Gemma, an extra completed Llama small line outside the frozen counts, and a clearly labeled family-size progress matrix for the broader five-family plan.
