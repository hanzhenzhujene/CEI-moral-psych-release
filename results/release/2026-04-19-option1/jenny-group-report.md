# Jenny Zhu Moral-Psych Benchmark Report

Date: `April 19, 2026`

This report captures Jenny Zhu's current CEI moral-psych benchmarking deliverable for the five-paper group scope agreed in the April 14, 2026 meeting notes. It is intentionally a report on the first closed slice, not a claim that the full five-family by three-size matrix has already been completed.

## Report Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Report date | `April 19, 2026` |
| Purpose | Group / mentor-facing report aligned to the April 14, 2026 moral-psych benchmark plan. |
| Benchmarks being tracked | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| What this release actually covers | One closed `Option 1` slice across `Qwen`, `DeepSeek`, and `Gemma` |
| Supplementary local completion outside release | `Llama` small complete via `llama-3.2-11b-vision-instruct` across `5` papers / `7` tasks |
| Prepared but not yet completed | `MiniMax` small route via `minimax-m2.1 + minimax-01` |
| Run provider / temperature | `OpenRouter`, `temperature=0` |
| Current cost note | $35 baseline spend before the active family-size expansion launch on April 19, 2026, plus an approved image add-on queue projected at about $2.42 total (below the $5 cap). |
| CI status reference | [CI workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml); latest verified passing run: [24634450927](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927) |
| Total evaluated samples in this release | `302,776` |

## Active Local Expansion Queues

- text-only family-size expansion: `results/inspect/full-runs/2026-04-19-family-size-text-expansion`
- image add-on queue under the $5 cap: `results/inspect/full-runs/2026-04-19-family-size-image-expansion`
- status labels: `Active` = running now, `Queued` = approved and waiting, `Complete` = finished

## The Five Papers / Benchmarks Under Test

| Benchmark | Citation | Paper link | Dataset / access link | Modality | Tasks implemented in this repo | Current release scope |
| --- | --- | --- | --- | --- | --- | --- |
| `UniMoral` | Kumar et al. (ACL 2025 Findings) | [paper](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | `unimoral_action_prediction; unimoral_moral_typology; unimoral_factor_attribution; unimoral_consequence_generation` | Action prediction only |
| `SMID` | Crone et al. (PLOS ONE 2018) | [paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | `smid_moral_rating; smid_foundation_classification` | Moral rating + foundation classification |
| `Value Kaleidoscope` | Sorensen et al. (AAAI 2024 / arXiv 2023) | [paper](https://arxiv.org/abs/2310.17681) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | `value_prism_relevance; value_prism_valence` | Relevance + valence |
| `CCD-Bench` | Rahman et al. (arXiv 2025) | [paper](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | `ccd_bench_selection` | Selection |
| `Denevil` | Duan et al. (ICLR 2024 submission / arXiv 2023) | [paper](https://arxiv.org/abs/2310.11905) | No stable public MoralPrompt download verified | Text generation | `denevil_generation; denevil_fulcra_proxy_generation` | FULCRA-backed proxy generation only |

## What Models Are Actually In The Closed Release

| Family | Exact model route | Size hint | Modality | Benchmarks in release | Tasks | Samples |
| --- | --- | --- | --- | --- | --- | ---: |
| `Qwen` | `openrouter/qwen/qwen3-8b` | 8B | Text | CCD-Bench; Denevil; UniMoral; Value Kaleidoscope | `ccd_bench_selection; denevil_fulcra_proxy_generation; unimoral_action_prediction; value_prism_relevance; value_prism_valence` | 97,004 |
| `Qwen` | `openrouter/qwen/qwen3-vl-8b-instruct` | 8B VL | Vision | SMID | `smid_foundation_classification; smid_moral_rating` | 5,882 |
| `DeepSeek` | `openrouter/deepseek/deepseek-chat-v3.1` | Provider route | Text | CCD-Bench; Denevil; UniMoral; Value Kaleidoscope | `ccd_bench_selection; denevil_fulcra_proxy_generation; unimoral_action_prediction; value_prism_relevance; value_prism_valence` | 97,004 |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | 4B | Text + Vision | CCD-Bench; Denevil; SMID; UniMoral; Value Kaleidoscope | `ccd_bench_selection; denevil_fulcra_proxy_generation; smid_foundation_classification; smid_moral_rating; unimoral_action_prediction; value_prism_relevance; value_prism_valence` | 102,886 |

## Closed Release Coverage

| Model family | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil |
| --- | --- | --- | --- | --- | --- |
| `Qwen` | benchmark-faithful | benchmark-faithful | benchmark-faithful | benchmark-faithful | proxy |
| `DeepSeek` | benchmark-faithful | not in closed scope | benchmark-faithful | benchmark-faithful | proxy |
| `Gemma` | benchmark-faithful | benchmark-faithful | benchmark-faithful | benchmark-faithful | proxy |

## Release Results Summary

| Model family | Benchmark-faithful tasks | Proxy tasks | Samples | Benchmark-faithful macro accuracy |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

| Benchmark | Unique task types | Evaluated lines | Models covered | Samples | Modes |
| --- | ---: | ---: | ---: | ---: | --- |
| `UniMoral` | 1 | 3 | 3 | 26,352 | benchmark_faithful |
| `SMID` | 2 | 4 | 2 | 11,764 | benchmark_faithful |
| `Value Kaleidoscope` | 2 | 6 | 3 | 196,560 | benchmark_faithful |
| `CCD-Bench` | 1 | 3 | 3 | 6,546 | benchmark_faithful |
| `Denevil` | 1 | 3 | 3 | 61,554 | proxy |

## Supplementary Local Progress Outside The Closed Release

| Family | Status relative to closed release | Exact route | Benchmark lines done | Benchmark lines still missing | Papers | Tasks | Benchmark-faithful tasks | Proxy tasks | Samples | Benchmark-faithful macro accuracy | Note |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `Llama` | Completed locally, outside the closed Option 1 counts | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy | Benchmark-faithful Denevil via MoralPrompt | 5 | 7 | 6 | 1 | 102,886 | 0.428 | Combines the original 2026-04-19-option1-llama32-11b-vision successes (UniMoral + SMID moral rating) with recovery-v3 completions for the remaining five tasks after a temporary OpenRouter key-limit stall. |
| `MiniMax` | Prepared only, not yet completed locally | `minimax-m2.1 + minimax-01` | None yet | UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy; Benchmark-faithful Denevil via MoralPrompt | 0 | 0 | 0 | 0 | 0 | n/a | Small-route launchers are wired in the repo, but this family still needs its first formal paid run before it can be compared against the closed release models. |

## Interpretation Notes

- This report is Jenny's current first formal release slice, not yet the full five-family by three-size comparison matrix.
- `Denevil` is represented only by the explicit `FULCRA`-backed proxy run in the closed release. It should not be reported as a benchmark-faithful `MoralPrompt` reproduction.
- `DeepSeek` has no `SMID` entries in the closed slice because no DeepSeek vision route was included in the authoritative package.
- `Gemma` results in the closed release come from the paid recovery route and supersede the earlier stalled free-tier namespace.
- `Llama` small is complete locally across all five benchmark papers, but it is intentionally treated as supplementary local evidence rather than folded into the closed `Option 1` counts.

## Next Step: Expand To Family x Size Comparisons

| Family | Closed release status | Current route already present in repo | Small | Medium | Large | Immediate next step |
| --- | --- | --- | --- | --- | --- | --- |
| `Qwen` | Included in Option 1 | qwen3-8b + qwen3-vl-8b-instruct | Current 8B text + 8B vision routes complete in the release | openrouter/qwen/qwen3-14b scheduled in the cost-ordered non-image expansion run | openrouter/qwen/qwen3-32b scheduled after qwen3-14b in the same text-only run | Let the medium / large text-only lines finish, then decide whether Qwen also needs larger vision checkpoints. |
| `MiniMax` | Prepared only, not in Option 1 | minimax-m2.1 + minimax-01 launcher present | Current small hybrid launcher exists, but the formal small line is still not closed | openrouter/minimax/minimax-m2.5 scheduled in the non-image expansion run | openrouter/minimax/minimax-m2.7 scheduled last among the current cost-ordered text-only jobs | After the medium / large text jobs finish, decide whether to formalize the small hybrid line too. |
| `DeepSeek` | Included in Option 1 | deepseek-chat-v3.1 | Closed release already uses a large-class DeepSeek route; a smaller baseline is still not frozen | openrouter/deepseek/deepseek-r1-distill-qwen-32b scheduled for the non-image expansion run | openrouter/deepseek/deepseek-chat-v3.1 already complete in the closed release | If the group wants a stricter S/M/L ladder, add a smaller DeepSeek distill route after the current medium run. |
| `Llama` | Completed locally, not promoted into Option 1 | llama-3.2-11b-vision-instruct completed locally | Current 11B route complete across 5 papers / 7 tasks | openrouter/meta-llama/llama-3.3-70b-instruct scheduled in the non-image expansion run | openrouter/meta-llama/llama-4-maverick scheduled after the 70B line in the same text-only queue | Let the 70B and Maverick text-only lines finish, then decide whether to promote Llama into the next authoritative snapshot. |
| `Gemma` | Included in Option 1 | gemma-3-4b-it | Current 4B route | openrouter/google/gemma-3-12b-it scheduled in the cost-ordered non-image expansion run | openrouter/google/gemma-3-27b-it scheduled first in the same text-only queue | Use the 12B and 27B text-only results to decide whether larger Gemma vision work is worth the extra cost. |

## Image Add-On Under The $5 Cap

The active image queue only targets `SMID`, only uses medium / large routes with a clean vision mapping, and stays below a combined projected add-on spend of about `$2.42`.

| Family | Size slot | Image route | Estimated full-run cost | Status | Note |
| --- | --- | --- | ---: | --- | --- |
| `Gemma` | Large | `openrouter/google/gemma-3-27b-it` | `$0.06` | Active | Cheapest selected image add-on route; running first in the capped SMID queue. |
| `Gemma` | Medium | `openrouter/google/gemma-3-12b-it` | `$0.07` | Queued | Queued after Gemma 27B in the same image-only run. |
| `Qwen` | Large | `openrouter/qwen/qwen3-vl-32b-instruct` | `$0.16` | Queued | Large Qwen image checkpoint under the same $5 cap. |
| `Llama` | Large | `openrouter/meta-llama/llama-4-maverick` | `$2.14` | Queued | Selected because the projected full SMID pass stays below the cap. |

Excluded from this image queue:

- DeepSeek: no vision route in the current family-size plan.
- Qwen medium: no clean Qwen medium VL route was locked for this pass.
- Llama medium: the chosen 70B route is text-only.
- MiniMax image: the shared `minimax-01` route projects to about $3.49 by itself and does not map cleanly onto separate medium / large size slots.

## Deliverable Positioning

A safe one-sentence framing for this repository is:

> This repository contains Jenny Zhu's April 19, 2026 CEI moral-psych benchmark report for five target papers, with a closed `Option 1` release over `Qwen`, `DeepSeek`, and `Gemma`, a completed supplementary `Llama` small line, and reproducible scripts plus structured next steps for expanding to the planned family-by-size matrix.
