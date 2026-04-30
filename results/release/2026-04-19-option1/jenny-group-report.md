# Jenny Zhu Moral-Psych Benchmark Report

Updated: `April 30, 2026`

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
| `Llama-L` | Complete local line | Done | SMID complete; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy finished at 100.0%. | SMID complete; local text rerun finished successfully through the Denevil proxy task. |
| `DeepSeek-M` | Complete local line | Done | No SMID route; UniMoral, Value Kaleidoscope, and CCD-Bench are fully persisted; Denevil proxy finished at 100.0%. | Local text rerun finished successfully on April 29, 2026 through the Denevil proxy task. |

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
| `Llama-L` | n/a | 0.386 | n/a | SMID is complete locally, and the local text rerun now finishes through the Denevil proxy task. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Frozen Option 1 recovery line. |
| `Gemma-M` | 0.663 | 0.364 | 0.664 | Complete local medium line with both text and SMID image results finished. |
| `Gemma-L` | 0.661 | 0.412 | 0.656 | Complete local large line with both text and SMID image results finished. |

![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)

_Topline comparable-accuracy chart. Benchmark-level accuracy comparison across the latest available lines, with unavailable or withdrawn benchmark-line pairs shown explicitly._

## Interpretation

These are the strongest claims the current public evidence supports. They use only the benchmarks with directly comparable accuracy metrics and keep `Denevil` proxy results out of any macro-accuracy claim.

### Interpretation At A Glance

| Claim | Evidence | Why it matters |
| --- | --- | --- |
| Strongest fully observed comparable line | `Gemma-L` averages 0.576 across UniMoral 0.661, SMID 0.412, and Value 0.656. | This is the cleanest like-for-like topline because all three comparable metrics are present on the same line. |
| Strongest text-only comparable line | `DeepSeek-L` reaches UniMoral 0.684 and Value 0.635, a two-metric mean of 0.659. | It is the strongest text-only comparison point, but it should not be described as the best all-around line because there is no SMID route in this slice. |
| Hardest current comparable benchmark | `SMID` has the lowest mean accuracy at 0.361 and the widest spread at 0.200. | The public readout should treat SMID as the highest-variance benchmark rather than expecting simple size-based improvements. |
| Closest thing to saturation | `UniMoral` has the tightest range, from 0.635 to 0.684 (0.048 spread). | Current text lines cluster closely on UniMoral, so additional size mainly fine-tunes rather than reshapes the ranking there. |
| Scaling-law read | `Gemma` is the only family with a full S/M/L comparable sweep, and its metrics move in different directions: UniMoral rises from 0.635 to 0.661, Value from 0.593 to 0.656, but SMID is nearly flat overall (0.417 to 0.412). | The data support task-specific scaling, not a single monotonic law across all families and benchmarks. |

### Benchmark Reading Guide

Before comparing charts, anchor each benchmark to its source paper. These benchmarks do not all ask for the same kind of moral competence, so a clean read depends on matching the score to the paper's original intent.

| Benchmark | What the paper is really testing | What this repo currently scores | How to read the current result |
| --- | --- | --- | --- |
| `UniMoral` | A unified multilingual moral-reasoning resource spanning action choice, typology, factor attribution, and consequence generation under culturally varied dilemmas. | The public release currently scores action prediction only: given a dilemma and two candidate actions, select the crowd-endorsed action. | A high UniMoral score means the model tracks consensus action choices across multilingual moral dilemmas. It does not by itself show equal strength on moral typology, factor attribution, or consequence generation. |
| `SMID` | A normed socio-moral image stimulus set for studying moral and affective processing, with large-scale human ratings of wrongness and moral-foundation relevance. | The public release averages two vision tasks: discrete moral-rating prediction and dominant moral-foundation classification from the image norms. | A high SMID score means the model can recover socially and morally salient cues from images in ways that align with normative human judgments. Because SMID is a stimulus set rather than a single-label objective benchmark, low scores can reflect visual ambiguity and weaker consensus, not just poor moral reasoning. |
| `Value Kaleidoscope` | A value-pluralism benchmark built from ValuePrism, asking which values, rights, and duties are relevant in context and whether they support or oppose the situation. | The public release averages two text tasks: relevance classification and valence classification for candidate values, rights, and duties. | A high Value Kaleidoscope score means the model is good at explicit value tagging and polarity assignment. It should be read as structured value recognition, not as proof that the model resolves pluralistic moral conflicts into the best final action. |
| `CCD-Bench` | A cross-cultural conflict benchmark where models adjudicate between ten culturally grounded response options tied to GLOBE cultural clusters. | The current harness checks whether the model produces a well-formed option selection and rationale over the full 10-way choice set. | CCD-Bench is most informative through preference patterns and rationale content across cultural clusters, not through a single comparable scalar accuracy. In this release, completion means structured coverage of the task, not that one culture-indexed option is universally correct. |
| `Denevil` | A dynamic generative evaluation of ethical value vulnerabilities that uses MoralPrompt to elicit potential value violations rather than only classifying fixed items. | The current public release can only run the FULCRA-backed proxy generation pathway, with completion measured as a successful generated response rather than paper-faithful MoralPrompt scoring. | A finished Denevil proxy line is a coverage and provenance signal, not an ethical-quality score. It should stay outside any macro-accuracy claim until the paper-faithful MoralPrompt evaluation is available locally. |

### Benchmark Difficulty Profile

![Benchmark difficulty profile](../../../figures/release/option1_benchmark_difficulty_profile.svg)

_Figure 3. Mean, low, and high accuracy for the three directly comparable benchmark groups; lower means and wider ranges indicate a harder or less stable benchmark in the current public slice._

| Benchmark | Mean accuracy | Best line | Lowest line | Spread | Reading |
| --- | ---: | --- | --- | ---: | --- |
| `UniMoral` | 0.656 | `DeepSeek-L` (0.684) | `Gemma-S` (0.635) | 0.048 | Tightest spread; current lines cluster closely. |
| `SMID` | 0.361 | `Gemma-S` (0.417) | `Llama-S` (0.216) | 0.200 | Lowest mean and widest spread in the current comparable slice. |
| `Value Kaleidoscope` | 0.626 | `Qwen-S` (0.682) | `Llama-S` (0.529) | 0.154 | Mid-range difficulty with meaningful but not extreme variation. |

### Family Scaling Profile

![Family scaling profile](../../../figures/release/option1_family_scaling_profile.svg)

_Figure 4. Size-slot trajectories for the currently comparable rows. Missing points are missing evidence, not zeroes; dashed connectors skip absent intermediate size slots._

| Family | Evidence scope | Numeric pattern | Cautious interpretation |
| --- | --- | --- | --- |
| `Qwen` | Only the small line is currently in the comparable table. | UniMoral: S 0.647<br/>SMID: S 0.368<br/>Value Kaleidoscope: S 0.682 | Enough for cross-family comparison, not enough for a within-family scaling claim. |
| `DeepSeek` | Only the large text line is currently comparable, and there is still no public SMID route. | UniMoral: L 0.684<br/>Value Kaleidoscope: L 0.635 | Strong text-only comparison point, but not a size curve. |
| `Llama` | Only SMID has both small and large comparable points. | UniMoral: S 0.648<br/>SMID: S 0.216 -> L 0.386<br/>Value Kaleidoscope: S 0.529 | The large vision route clearly helps on SMID, but the current public table still does not support an across-benchmark Llama scaling claim. |
| `Gemma` | Full S/M/L comparable sweep on all three comparable benchmarks. | UniMoral: S 0.635 -> M 0.663 -> L 0.661<br/>SMID: S 0.417 -> M 0.364 -> L 0.412<br/>Value Kaleidoscope: S 0.593 -> M 0.664 -> L 0.656 | Best evidence against a single universal scaling law in this repo: text benchmarks improve with size overall, while SMID is non-monotonic. |

### Reporting Guardrails

- Do not fold `Denevil` into any benchmark-faithful macro-accuracy claim; it remains proxy-only even when its completion status is `Done`.
- Do not call `DeepSeek-L` the best overall line across all tasks; its text results are strong, but there is no SMID route in the current public slice.
- Do not claim a universal scaling law from these figures. `Gemma` is the only family with a full S/M/L comparable sweep, and even there the benchmark directions diverge.
- Treat missing comparable cells as evidence limits rather than model failures. Several large lines are complete operationally but still lack directly comparable public metrics for some benchmarks.

## Report Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `April 30, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Tracked published-cost floor | `$40.73` |
| Cost scope | Frozen-snapshot plus tracked public-release bookkeeping only; later local reruns are intentionally excluded from this static cost field. |
| Purpose | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Current public matrix | `5 benchmarks x 4 model families x 3 size slots = 60 family-size-benchmark cells` |
| Benchmarks being tracked | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Model families in scope | `Qwen`, `DeepSeek`, `Llama`, `Gemma` |
| What the frozen snapshot actually covers | one closed `Option 1` slice across `Qwen`, `DeepSeek`, and `Gemma` |
| Extra completed local line outside release | `Llama` small complete via `llama-3.2-11b-vision-instruct` across `5` papers / `7` tasks |
| Run provider / temperature | `OpenRouter`, `temperature=0` |
| Current live reruns | No currently published line is still running locally. |
| Next restart focus | No published rerun is active right now. |
| Release guardrail | Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables. |
| CI workflow | [CI workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml) |
| Total evaluated samples in this release | `302,776` |

### Current Operations Highlights

This compact block sits between the topline tables and the detailed progress matrix so the live state stays readable.

- Active open-source reruns: none are currently shown in the published matrix.
- Stalled or queued follow-up work: no published partial line is waiting right now.
- Complete local lines beyond the frozen `Option 1` slice: `Llama-S`, `Gemma-M`, `Gemma-L`, `Qwen-M`, `Qwen-L`, `Llama-M`, `Llama-L`, and `DeepSeek-M`.
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
| `DeepSeek-M text batch` | Done | Local text rerun finished successfully on April 29, 2026 through the Denevil proxy task. |
| `Llama-L SMID` | Done | The large Llama vision line is complete locally. |
| `Next queued text lines` | Queue | No currently published line remains queued behind an active rerun. |

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
| `Value Kaleidoscope` | Sorensen et al. (AAAI 2024 / arXiv 2023) | [paper](https://arxiv.org/abs/2309.00779) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | Relevance + valence |
| `CCD-Bench` | Rahman and Salam (arXiv 2025) | [paper](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | Selection |
| `Denevil` | Duan et al. (ICLR 2024 / arXiv 2023) | [paper](https://arxiv.org/abs/2310.11053) | No public MoralPrompt export confirmed | Text generation | Proxy generation only |

## Model Families And Size Routes

| Family | Small route | Medium route | Large route |
| --- | --- | --- | --- |
| `Qwen` | Text: `openrouter/qwen/qwen3-8b`<br/>Vision: `openrouter/qwen/qwen3-vl-8b-instruct` | `openrouter/qwen/qwen3-14b` | Text: `openrouter/qwen/qwen3-32b`<br/>Vision: `openrouter/qwen/qwen2.5-vl-72b-instruct (recovery complete)` |
| `DeepSeek` | No distinct small OpenRouter route exposed | `openrouter/deepseek/deepseek-r1-distill-llama-70b (DeepInfra-pinned recovery route)` | `openrouter/deepseek/deepseek-chat-v3.1` |
| `Llama` | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | `openrouter/meta-llama/llama-3.3-70b-instruct` | `openrouter/meta-llama/llama-4-maverick` |
| `Gemma` | `openrouter/google/gemma-3-4b-it` | `openrouter/google/gemma-3-12b-it` | `openrouter/google/gemma-3-27b-it` |

## Full Family-Size Progress Matrix

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | --- |
| `Qwen-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 line. |
| `Qwen-M` | Done | TBD | Done | Done | Proxy | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Done | Done | Done | Done | Proxy | SMID recovery complete; clean text rerun finished locally. |
| `DeepSeek-S` | TBD | - | TBD | TBD | TBD | No distinct small DeepSeek route is fixed yet. |
| `DeepSeek-M` | Done | - | Done | Done | Proxy | No SMID route; local text rerun finished successfully through the Denevil proxy task (100.0%). |
| `DeepSeek-L` | Done | - | Done | Done | Proxy | Frozen large text line; no SMID route was included. |
| `Llama-S` | Done | Done | Done | Done | Proxy | Complete locally across all five papers. |
| `Llama-M` | Done | - | Done | Done | Proxy | No SMID route; medium text line completed locally on April 22, 2026. |
| `Llama-L` | Done | Done | Done | Done | Proxy | SMID complete; local text rerun is now fully persisted through the Denevil proxy task (100.0%). |
| `Gemma-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 recovery line. |
| `Gemma-M` | Done | Done | Done | Done | Proxy | Complete local line across all five papers. |
| `Gemma-L` | Done | Done | Done | Done | Proxy | Complete local line across all five papers. |

## Supporting Figures

Figures 1 through 4 are already embedded above in context; this gallery keeps the remaining visuals together without repeating them.

| Figure | Why it matters | File |
| --- | --- | --- |
| Figure 1 | Latest line-level progress across the current published family-size matrix. | [option1_family_size_progress_overview.svg](../../../figures/release/option1_family_size_progress_overview.svg) |
| Figure 2 | Cross-model comparison for the benchmarks that share a directly comparable accuracy metric. | [option1_benchmark_accuracy_bars.svg](../../../figures/release/option1_benchmark_accuracy_bars.svg) |
| Figure 3 | Benchmark-level difficulty and spread across the current comparable slice. | [option1_benchmark_difficulty_profile.svg](../../../figures/release/option1_benchmark_difficulty_profile.svg) |
| Figure 4 | Family-by-size scaling profile for the currently comparable rows. | [option1_family_scaling_profile.svg](../../../figures/release/option1_family_scaling_profile.svg) |
| Figure 5 | Heatmap of the latest available comparable metrics, including incomplete-benchmark treatment. | [option1_accuracy_heatmap.svg](../../../figures/release/option1_accuracy_heatmap.svg) |
| Figure 6 | Coverage view of which benchmark lines are paper-setup, proxy-only, or not in the frozen release. | [option1_coverage_matrix.svg](../../../figures/release/option1_coverage_matrix.svg) |
| Figure 7 | Sample concentration by benchmark with paper-setup versus proxy volume separated. | [option1_sample_volume.svg](../../../figures/release/option1_sample_volume.svg) |

![Accuracy heatmap](../../../figures/release/option1_accuracy_heatmap.svg)

_Figure 5. Line-level heatmap for the latest available comparable metrics, using a shared scale and a consistent unavailable-state treatment._

![Coverage matrix](../../../figures/release/option1_coverage_matrix.svg)

_Figure 6. Coverage matrix showing which benchmark lines are paper-setup, proxy-only, or absent from the frozen release._

![Sample volume by benchmark](../../../figures/release/option1_sample_volume.svg)

_Figure 7. Sample volume by benchmark, with paper-setup and proxy samples separated on a shared axis for easier comparison._

## Frozen Option 1 Summary

| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |
| :--- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

## Safe One-Sentence Framing

> This repository contains Jenny Zhu's CEI moral-psych benchmark deliverable for five target papers, with a frozen Option 1 snapshot over Qwen, DeepSeek, and Gemma, an extra completed Llama small line outside the frozen counts, and a clearly labeled family-size progress matrix for the broader five-family plan.
