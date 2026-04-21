# Option 1 Release Artifacts

This directory contains the tracked, publication-facing outputs for Jenny Zhu's CEI moral-psych deliverable.

It separates two things clearly:

1. the frozen `Option 1` public snapshot from `April 19, 2026`, and
2. the wider `5 benchmarks x 5 model families x 3 size slots` progress matrix that is still being filled in.

## Results First

This is the fastest way to read the deliverable: which lines already have usable results, what is directly comparable now, and where the current release snapshot stops.

| Line | Scope | Status | Coverage | Note |
| --- | --- | --- | --- | --- |
| `Qwen-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Qwen release line. |
| `DeepSeek-L` | Frozen Option 1 | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Primary large DeepSeek release line. |
| `Gemma-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Gemma release line. |
| `Llama-S` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally, outside the frozen Option 1 counts. |
| `Gemma-M` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Gemma-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Qwen-M` | Partial local line | Partial | UniMoral and Value Kaleidoscope relevance done; Value Kaleidoscope valence live | The underlying worker is still active; the stale signal came from an overwritten launcher PID file. |
| `Qwen-L` | Partial local line | Partial | SMID and UniMoral done; Value Kaleidoscope relevance live | The underlying worker is still active; the stale signal came from an overwritten launcher PID file. |
| `MiniMax-S` | Attempted local line | Error | No usable benchmark line completed | OpenRouter key-limit failures interrupted both text and image paths. |

### Latest Family-Size Progress Snapshot

This stacked overview is the quickest visual read on the current 15-line plan: complete lines, active resumptions, and still-queued gaps.

![Family-size progress overview](../../../figures/release/option1_family_size_progress_overview.svg)

_Latest family-size progress overview. Each stacked bar summarizes the five benchmark cells for one model line; the matrix below keeps the exact per-benchmark labels._

### Current Comparable Accuracy Snapshot

Only benchmarks with directly comparable accuracy metrics are shown here. `CCD-Bench` and `Denevil` are excluded because they do not share the same target metric across lines.

| Line | UniMoral action | SMID average | Value Kaleidoscope average | Coverage note |
| :--- | ---: | ---: | ---: | --- |
| `Qwen-S` | 0.647 | 0.368 | 0.682 | Frozen Option 1 line. |
| `DeepSeek-L` | 0.684 | n/a | 0.635 | Frozen large-class text line. No SMID vision route was included. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Complete locally across all five papers, but still outside the frozen Option 1 snapshot counts. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Frozen Option 1 recovery line. |

![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)

_Topline comparable-accuracy chart. Benchmark-level accuracy comparison across the currently completed comparable lines, with unavailable benchmark-line pairs shown explicitly._

## Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `April 21, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Current cost to date | `$40.73` |
| Intended use | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Agreed target matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Agreed model families | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |
| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |
| Extra completed local line outside release | `Llama` small via `llama-3.2-11b-vision-instruct`, complete across `5` papers / `7` tasks |
| MiniMax small status | formal attempt exists, but the current run failed and is not counted as complete |
| Provider / temperature | `OpenRouter`, `temperature=0` |
| Current operations note | Updated April 21, 2026. The frozen public snapshot remains Option 1 from April 19. Gemma-M and Gemma-L text are now complete locally. The current live Qwen restart has Qwen-M value_prism_valence at 6,552 / 21,840 persisted samples (30.0%) and Qwen-L value_prism_relevance at 4,368 / 43,680 persisted samples (10.0%); both workers are live and still actively calling OpenRouter. The Llama-M and DeepSeek-M watcher chain is armed and polling every three minutes for the first clean Qwen completion. |
| CI reference | [Workflow](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml); last verified successful run: [run 24634450927](https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927) |

## Local Expansion Checkpoint

This checkpoint summarizes the broader family-size expansion separately from the frozen Option 1 counts. It is a curated snapshot rather than a live dashboard.

| Line or batch | Status | Note |
| --- | --- | --- |
| `Qwen-L SMID recovery` | Done | Completed April 20, 2026 via openrouter/qwen/qwen2.5-vl-72b-instruct after the earlier qwen3-vl-32b moderation stop. |
| `Gemma-L text batch` | Done | Completed April 21, 2026. UniMoral, Value Kaleidoscope, CCD-Bench, and the Denevil proxy task all finished successfully. |
| `Gemma-M text batch` | Done | Completed April 21, 2026. The medium text route now has a full local line across all five benchmark papers. |
| `Qwen-M text batch` | Live | UniMoral and Value Kaleidoscope relevance completed successfully. The restarted valence worker has flushed 6,552 / 21,840 persisted samples (30.0%) and is still actively running. |
| `Qwen-L text batch` | Live | UniMoral completed successfully. The restarted relevance worker has flushed 4,368 / 43,680 persisted samples (10.0%) and is still actively running. |
| `Llama-M text batch` | Prep | The watcher is armed and polling every three minutes for the first clean Qwen completion. |
| `DeepSeek-M text batch` | Prep | The chained watcher is armed behind Llama-M and polling every three minutes. |
| `Llama-L SMID` | Done | The large Llama vision line is complete locally. |
| `Next queued text lines` | Queue | Llama-L, MiniMax-M, and MiniMax-L remain fully queued. Qwen-M and Qwen-L are still live, and the Llama-M / DeepSeek-M auto-launch watchers are armed and polling. |

## Start Here

### Reports

- `jenny-group-report.md`: mentor-facing report with the benchmark list, progress matrix, model roster, and current results
- `topline-summary.md`: shortest narrative summary of the frozen Option 1 snapshot
- `release-manifest.json`: machine-readable release index
- [how to read the results](../../../docs/how-to-read-results.md): plain-language explanation of the report terms

### Figures

- [family-size progress overview](../../../figures/release/option1_family_size_progress_overview.svg): latest line-level status across the full 15-line plan
- [grouped bar chart](../../../figures/release/option1_benchmark_accuracy_bars.svg): current cross-model benchmark comparison
- [accuracy heatmap](../../../figures/release/option1_accuracy_heatmap.svg): task-level view of comparable metrics
- [coverage matrix](../../../figures/release/option1_coverage_matrix.svg): frozen Option 1 coverage only
- [sample volume chart](../../../figures/release/option1_sample_volume.svg): where the evaluated samples are concentrated

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

This is the cleanest repo-level summary of where the full `5 x 5 x 3` plan stands today.

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | --- |
| `Qwen-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 line. |
| `Qwen-M` | Done | TBD | Live | Queue | Queue | UniMoral and Value Kaleidoscope relevance are done; the restarted valence worker is still live with a 6,552 / 21,840 persisted checkpoint. |
| `Qwen-L` | Done | Done | Live | Queue | Queue | SMID and UniMoral are done; the restarted relevance worker is still live with a 4,368 / 43,680 persisted checkpoint. |
| `MiniMax-S` | Error | Error | Error | Error | Error | Attempted, but key-limit failures made the line unusable. |
| `MiniMax-M` | Queue | TBD | Queue | Queue | Queue | Text queued; no medium SMID route is fixed yet. |
| `MiniMax-L` | Queue | TBD | Queue | Queue | Queue | Text queued; no large SMID route is fixed yet. |
| `DeepSeek-S` | TBD | - | TBD | TBD | TBD | OpenRouter currently exposes 32B distill and larger DeepSeek routes only; no separate small line is fixed yet. |
| `DeepSeek-M` | Queue | - | Queue | Queue | Queue | No vision route is in scope. The chained watcher is armed and waiting for Llama-M to finish. |
| `DeepSeek-L` | Done | - | Done | Done | Proxy | Frozen large text line; no SMID route was included. |
| `Llama-S` | Done | Done | Done | Done | Proxy | Complete locally across all five papers. |
| `Llama-M` | Queue | - | Queue | Queue | Queue | No SMID run is planned. The watcher is armed and waiting for the first clean Qwen completion. |
| `Llama-L` | Queue | Done | Queue | Queue | Queue | SMID done; text is still queued. |
| `Gemma-S` | Done | Done | Done | Done | Proxy | Frozen Option 1 recovery line. |
| `Gemma-M` | Done | Done | Done | Done | Proxy | Complete locally across all five papers, with Denevil covered through the same proxy route used elsewhere in this deliverable. |
| `Gemma-L` | Done | Done | Done | Done | Proxy | Complete locally across all five papers, with Denevil covered through the same proxy route used elsewhere in this deliverable. |

## Benchmark List

| Benchmark | Paper | Dataset / access | Modality | What this repo tests now |
| --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. (ACL 2025 Findings)](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | Action prediction only |
| `SMID` | [Crone et al. (PLOS ONE 2018)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | Moral rating + foundation classification |
| `Value Kaleidoscope` | [Sorensen et al. (AAAI 2024 / arXiv 2023)](https://arxiv.org/abs/2310.17681) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | Relevance + valence |
| `CCD-Bench` | [Rahman et al. (arXiv 2025)](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | Selection |
| `Denevil` | [Duan et al. (ICLR 2024 submission / arXiv 2023)](https://arxiv.org/abs/2310.11905) | No public MoralPrompt export confirmed | Text generation | Proxy generation only |

## Supporting Figures

| Figure | Why it matters | File |
| --- | --- | --- |
| Figure 1 | Latest line-level progress across the full five-family by three-size plan. | [option1_family_size_progress_overview.svg](../../../figures/release/option1_family_size_progress_overview.svg) |
| Figure 2 | Cross-model comparison for the benchmarks that share a directly comparable accuracy metric. | [option1_benchmark_accuracy_bars.svg](../../../figures/release/option1_benchmark_accuracy_bars.svg) |
| Figure 3 | Task-level heatmap for the frozen comparable metrics, including unavailable-task treatment. | [option1_accuracy_heatmap.svg](../../../figures/release/option1_accuracy_heatmap.svg) |
| Figure 4 | Coverage view of which benchmark lines are paper-setup, proxy-only, or not in the frozen release. | [option1_coverage_matrix.svg](../../../figures/release/option1_coverage_matrix.svg) |
| Figure 5 | Sample concentration by benchmark with paper-setup versus proxy volume separated. | [option1_sample_volume.svg](../../../figures/release/option1_sample_volume.svg) |

![Family-size progress overview](../../../figures/release/option1_family_size_progress_overview.svg)

_Figure 1. Latest family-size progress overview. Each stacked bar summarizes the five benchmark cells for one model line; use the table below for the exact per-benchmark labels._

![Accuracy heatmap](../../../figures/release/option1_accuracy_heatmap.svg)

_Figure 3. Task-level accuracy heatmap for the frozen Option 1 slice, using a shared scale and a consistent unavailable-state treatment._

![Coverage matrix](../../../figures/release/option1_coverage_matrix.svg)

_Figure 4. Coverage matrix showing which benchmark lines are paper-setup, proxy-only, or absent from the frozen release._

![Sample volume by benchmark](../../../figures/release/option1_sample_volume.svg)

_Figure 5. Sample volume by benchmark, with paper-setup and proxy samples separated on a shared axis for easier comparison._

## Frozen Option 1 Model Summary

| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |
| :--- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

## Files

- `source/authoritative-summary.csv`: tracked frozen source snapshot for the April 19 release
- `jenny-group-report.md`: mentor-ready markdown report
- `topline-summary.md`: concise release narrative
- `release-manifest.json`: machine-readable index of counts, files, and caveats
- `family-size-progress.csv`: 15-line matrix for the full five-family by three-size plan
- `benchmark-comparison.csv`: current comparable accuracy table used for the grouped bar figure
- `benchmark-catalog.csv`: benchmark registry with paper and dataset links
- `model-roster.csv`: exact OpenRouter routes in the frozen Option 1 snapshot
- `supplementary-model-progress.csv`: extra local lines outside the frozen snapshot counts

## Regeneration

From the repo root:

```bash
make release
make audit
```

`make release` rebuilds this public package from the tracked source snapshot. `make audit` runs the public QA gate and rebuilds the package together.

## Interpretation Notes

- The full `5 x 5 x 3` plan is the target matrix, not a claim of completed coverage.
- The frozen `Option 1` snapshot still only includes `Qwen`, `DeepSeek`, and `Gemma`.
- `Llama-S` is complete locally and is shown in comparison tables, but it remains outside the frozen snapshot counts.
- `MiniMax-S` has a formal attempt on disk, but it is still an error line rather than a finished comparison point.
- `Denevil` is still proxy-only in the current public release because the paper-faithful `MoralPrompt` export is not available locally.
