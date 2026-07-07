# Paper Result Calibration and Comparison

This page answers one reviewer question: what did the original benchmark papers contain, what did this repo run, and which comparisons are safe?

Use it as an evidence-status map, not as a leaderboard. Current benchmark rows, paper-faithful replication, saved prior artifacts, route probes, and proxy evidence are different evidence types.

## Open First

| Need | Open |
| --- | --- |
| Same-model bar chart for exact CCD-Bench paper-model rows | [same-model CCD calibration bar chart](../figures/release/option1_paper_result_alignment_map.svg) |
| Visual bridge for exact same-model calibration only | [paper-model calibration bridge](../figures/release/option1_paper_model_calibration_bridge.svg) |
| Machine-readable alignment table | [paper-result-alignment.csv](../results/release/2026-04-19-option1/paper-result-alignment.csv) |
| RQ-level paper/result comparison table | [paper-result-comparison.csv](../results/release/2026-04-19-option1/paper-result-comparison.csv) |
| Paper-model overlap table | [paper-model-overlap-map.csv](../results/release/2026-04-19-option1/paper-model-overlap-map.csv) |
| Same-model calibration planning ledger | [paper-model-calibration-ledger.csv](../results/release/2026-04-19-option1/paper-model-calibration-ledger.csv) |
| Strict same-model bridge table | [paper-model-calibration-bridge.csv](../results/release/2026-04-19-option1/paper-model-calibration-bridge.csv) |
| Context-only paper result table | [paper result context figure](../figures/release/option1_paper_result_comparison.svg) |
| Planning / route-status notes | [calibration-replication.md](calibration-replication.md), [paper-model-replication-map.md](paper-model-replication-map.md) |

## Visual Summary

![Same-model CCD calibration bar chart](../figures/release/option1_paper_result_alignment_map.svg)

_Same-model CCD calibration bar chart: only the 11 exact CCD-Bench rows with a shared Nordic-share metric are plotted.
Current-only, blocked, metric-mismatched, DeNEVIL/proxy, SMID human-norm, and Value/Kaleido non-rerun evidence stays in the tables._

![Paper-model calibration bridge](../figures/release/option1_paper_model_calibration_bridge.svg)

_Model bridge: only exact same-model evidence is plotted; near-family, blocked, proxy, and route-probe rows stay in the ledger table._

The broader [paper result context figure](../figures/release/option1_paper_result_comparison.svg) is still available for paper-metric anchors, but it is not a same-model calibration bar comparison.

## TL;DR

| Benchmark | Current comparison status | Reader rule |
| --- | --- | --- |
| `UniMoral` | Fresh exact Llama 3.1 8B overlap now exists for RQ1-RQ4; paper metric anchors are tracked separately. | Call it metric-bridged same-model calibration, not reproduced paper weighted-F1/BERTScore tables. |
| `SMID` | No original LLM roster found locally. | Compare current vision-capable rows only. |
| `Value Kaleidoscope / ValuePrism` | Current rows are prompt-based ValuePrism tasks. | Do not call them Kaleido model replication. |
| `CCD-Bench` | The strict same-model bridge now has 11 exact CCD distribution rows; the ledger keeps unavailable and non-exact routes separate. | Never describe CCD-Bench as accuracy. |
| `DeNEVIL / MoralPrompt` | Current evidence is FULCRA proxy behavior only. | No paper-faithful MoralPrompt comparison until the data path exists. |

## What This Means

- The strongest paper-to-current bridge is now UniMoral Llama 3.1 8B model identity: RQ1-RQ4 were rerun on the exact paper-roster model, while metric-scale caveats remain explicit.
- The cleanest same-model behavior bridge is now CCD-Bench: the strict bridge keeps current `Llama-4-Maverick-17B-128E-Instruct`
  plus fresh exact reruns for `Mistral Nemo`, `Llama-3.3-70B-Instruct`, `DeepSeek-chat-v3-0324`, `Qwen2.5-72B-Instruct`,
  `OpenAI GPT-4.1`, `Command-R 08-2024`, `Microsoft Phi-4`, `WizardLM-2-8x22B`, `Perplexity Sonar`, and `Claude 4 Sonnet`.
  Unavailable and non-exact routes are tracked in the ledger rather than plotted as same-model calibration.
- The current ValuePrism rows are useful current benchmark evidence, but Kaleido model replication remains blocked until the gated model route is run.
- SMID and DeNEVIL answer different questions from their source papers in this release: SMID is a current model-vs-human-norm layer, and DeNEVIL is proxy-only audit evidence.
- For review, cite the CSV/figure pair that matches the claim: use `paper-result-alignment.csv` for status, the calibration ledger for exact model-name/run planning,
  the calibration bridge for one-to-one model overlap, and the RQ-level CSV for paper metric anchors.

## Benchmark Cards

### UniMoral

- Paper/reference side: original setup has multiple RQs. The reference roster names Phi-3.5 mini, Llama 3.1 8B, and DeepSeek-R1-Distill-Llama-8B.
- Current repo side: all eligible text rows have UniMoral action accuracy. DeepSeek-M and GPT-5.5 both reach `0.683629`.
- Calibration evidence: fresh exact Llama 3.1 8B UniMoral rerun completed locally with RQ1 accuracy `0.621926`,
  RQ2 accuracy `0.602234`, RQ3 accuracy `0.594788`, RQ4 live METEOR `0.121226`, and RQ4 offline BERTScore F1 `0.655539`.
- Direct comparison: partial. Visible paper metric anchors are tracked in the RQ-level CSV, but the release headline uses exact-match accuracy while the paper tables
  report weighted F1/BLEU/METEOR/BERTScore cells on a different scale. The fresh run now has the repo-side RQ4 BERTScore F1
  and METEOR metrics, but it should still be read as metric-bridged calibration rather than reproduced paper table values.
- Reviewer takeaway: use UniMoral as the clearest same-model paper-calibration bridge, but keep metric caveats and RQ2/RQ3/RQ4 separation visible.

### SMID

- Paper/reference side: SMID is a normed image stimulus set; no original LLM model roster was identified locally.
- Current repo side: the release reports a vision-route average over moral-rating prediction and foundation classification.
- Current anchor: Qwen-L is the strongest current SMID row at `0.482829`.
- Direct comparison: no paper-model comparison. Only current model-to-model comparison is supported.
- Reviewer takeaway: ask which current vision route best recovers human norm labels, not whether the repo beats a paper model.

### Value Kaleidoscope / ValuePrism

- Paper/reference side: the paper route is the Kaleido model family: small, base, large, xl, and xxl.
- Current repo side: the release reports prompt-based LLM relevance and valence classification.
- Current anchors: MiniMax-L `0.741197`, MiniMax-S `0.739942`, MiniMax-M `0.739778`, GPT-5 mini `0.738897`, GPT-5.5 `0.735646`.
- Direct comparison: no. These are related ValuePrism tasks, not Kaleido model replication.
- Reviewer takeaway: keep these current value results, but mark direct Kaleido replication as blocked until gated model access and a separate execution path are run.

### CCD-Bench

- Paper/reference side: the original surface is ten-cluster cultural choice behavior, not correctness.
- Current repo side: the release reports choice distributions, dominant-cluster share, valid-choice coverage, and effective clusters.
- Current GPT-5.5 anchor: `2,182/2,182` valid choices; dominant option 6 at `27.268561%`; effective clusters `7.058620`.
- Fresh exact anchors: Mistral Nemo has `2,182/2,182` valid choices, Nordic Europe `25.5729%`, and effective clusters `7.237951`;
  WizardLM-2-8x22B has `2,182/2,182` valid choices, Nordic Europe `23.6480%`, and effective clusters `7.498376`.
- Direct comparison: partial but expanded. Distribution and concentration can be compared for exact same-model `Mistral Nemo`,
  `Llama-3.3-70B-Instruct`, `Llama-4-Maverick-17B-128E-Instruct`, `DeepSeek-chat-v3-0324`, `Qwen2.5-72B-Instruct`, `OpenAI GPT-4.1`,
  `Command-R 08-2024`, `Microsoft Phi-4`, `WizardLM-2-8x22B`, `Perplexity Sonar`, and `Claude 4 Sonnet` rows.
  Unavailable and non-exact routes are not one-to-one calibration rows, and accuracy is not a CCD metric.
- Reviewer takeaway: use the behavior/concentration map, not a leaderboard.

### DeNEVIL / MoralPrompt

- Paper/reference side: the paper-faithful MoralPrompt data path is missing locally.
- Current repo side: the release reports FULCRA-backed proxy visible-behavior categories and prompt-family breakdowns.
- Current anchor: proxy archive has `20,518` prompts per released proxy line.
- Direct comparison: no. Current evidence is proxy-only.
- Reviewer takeaway: keep DeNEVIL outside macro-accuracy and paper-replication claims until a real MoralPrompt export exists.

## Model Overlap Summary

| Benchmark | Same-model overlap | Missing or blocked paper side | Current context only |
| --- | --- | --- | --- |
| `UniMoral` | Fresh exact Llama 3.1 8B RQ1-RQ4 rerun. | Phi-3.5 mini and DeepSeek-R1-Distill-Llama-8B exact paper routes. | Qwen, MiniMax, DeepSeek, Llama, Gemma, and OpenAI text refs including GPT-5.5. |
| `SMID` | None found. | Original LLM roster is not identified locally. | Current vision-capable Qwen, MiniMax, Llama, and Gemma rows where routes exist. |
| `Value Kaleidoscope / ValuePrism` | None. | Kaleido small/base/large/xl/xxl gated route. | All current prompt-based LLM rows and OpenAI text refs. |
| `CCD-Bench` | 11 exact CCD rows in the strict bridge. | Unavailable exact paper routes stay ledger-only. | Current family rows are context unless exact identity matches. |
| `DeNEVIL / MoralPrompt` | None for paper-faithful DeNEVIL. | MoralPrompt paper-faithful data path. | Current FULCRA-backed proxy rows. |

## Metric Reading Rules

| Benchmark | Is this accuracy? | How to read quality |
| --- | --- | --- |
| `UniMoral` | Current RQ1-RQ3 use exact-match accuracy; RQ4 uses BERTScore F1 and METEOR. | Compare paper and release values only with metric/model caveats. |
| `SMID` | Yes for the repo's moral-rating and foundation-classification tasks. | Scores are modest; image ambiguity and norm consensus are part of the interpretation. |
| `Value Kaleidoscope / ValuePrism` | Yes for prompt-based relevance and valence labels. | High scores mean good value tagging and polarity assignment, not Kaleido replication. |
| `CCD-Bench` | No universal accuracy score. | Read dominant cluster, dominant share, effective clusters, and deviation from the uniform baseline. |
| `DeNEVIL / MoralPrompt` | No paper-faithful score. | Read proxy behavior categories only. |

## Guardrails

- GPT-5.5 is text-only and does not cover all benchmarks.
- CCD-Bench is behavior/distribution evidence, not accuracy or correctness.
- DeNEVIL proxy rows are not paper-faithful MoralPrompt replication.
- Route probes are route checks, not performance results.
- Saved/prior artifacts are not fresh reruns.
- Prompt-based ValuePrism rows are not Kaleido model replication.
- Missing cells are route gaps, data gaps, model-access gaps, or proxy boundaries; they are not poor model performance.
