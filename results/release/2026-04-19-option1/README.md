# Option 1 Release Artifacts

This directory contains the tracked, publication-facing outputs for Jenny Zhu's CEI moral-psych deliverable.

It separates two things clearly:

1. the frozen `Option 1` public snapshot from `April 19, 2026`, and
2. the wider `5 benchmarks x 5 public model families x 3 size slots` progress matrix that is still being filled in.

## TL;DR

Key takeaways:

- **Main landscape:** text moral reasoning is much stronger than image moral judgment. UniMoral and Value sit around 0.653-0.673 mean accuracy, but SMID image accuracy averages only 0.364; even the best image line, `Qwen-L` at 0.483, is below 0.50. In plain terms: models can talk through moral choices and values better than they can see morally important cues in images.
- **Best all-around line:** `MiniMax-S` is the cleanest overall winner because it is not missing the image benchmark: UniMoral 0.661, SMID 0.432, Value 0.740, mean 0.611. The main warning is that the best text-only rows can look stronger, but they do not answer the image problem.
- **Scaling law:** there is no reliable bigger-is-better rule. Scale helps in a few places, especially Qwen on images (0.368 -> 0.483) and Llama on Value from S to M (0.529 -> 0.724). But there are clear reversals: Gemma image dips then rebounds (0.417 -> 0.364 -> 0.412), DeepSeek UniMoral falls from M to L (0.684 -> 0.563), and `MiniMax-L` is an image outlier at 0.199.
- **Family read:** Qwen is the clearest case where size helps vision; Gemma is the cleanest full S/M/L family but still non-monotonic; DeepSeek is useful for text but has no image route and its large line is not automatically better; Llama improves after the small line but M can beat L on text; MiniMax-S is the safest all-around line, while MiniMax-L is the clearest bad image outlier.
- **UniMoral is not one skill:** a model can match the human action but still miss the moral frame, the reason, or the consequence. Task winners rotate across RQ1 `DeepSeek-M` 0.684, RQ2 `Gemma-S` 0.599, RQ3 `Llama-M` 0.631, RQ4 semantic `Llama-M` 0.730, RQ4 lexical `Llama-L` 0.157. So the useful story is which part of moral reasoning each family handles, not one single moral score.
- **Cultural-style bias:** CCD-Bench shows a strong Europe/Nordic pull, not a normal accuracy score. 19 of 20 valid lines choose `Nordic Europe` as their dominant style. `GPT-5-nano Ref` is the most collapsed onto one cluster (27.8%), while `DeepSeek-S` is the least collapsed and the only non-Nordic dominant line (13.8%, `Sub Saharan Africa`).
- **OpenAI references:** the GPT rows mostly confirm the text baseline instead of changing the story. `GPT-4o-mini Ref` is close to the strong text band (UniMoral 0.673, Value 0.701); `GPT-5-mini Ref` beats `GPT-5-nano Ref` (0.739 vs 0.617 on Value), and `GPT-4.1-mini Ref` beats `GPT-4.1-nano Ref` (0.679 vs 0.646 on UniMoral). None of these rows has SMID, so they do not solve the image weakness.
- **Small-model follow-up:** Mistral/Qwen/Llama older routes add one simple takeaway: there is a capability floor. `Mistral Nemo`, `Qwen2.5 7B`, `Llama 3.1 8B`, and `Llama 3 8B` cluster on UniMoral from 0.632 to 0.648, but `Llama 3.2 1B` drops to 0.406. So these models are useful baselines, not a new top tier, and the 1B route is too small for this moral-choice setup.


## Benchmark Result Visuals

If you want the benchmark results before the tables, start here. These visuals pull the main result surfaces for the full benchmark set to the front of the deliverable.

OpenAI text-only reference rows are shown in the comparable-accuracy and CCD figures. They are drawn as gray calibration references, not as a GPT/OpenAI S/M/L size series, and they have no SMID or DeNEVIL row.
OpenAI/GPT scope: the scored reference rows are `openai/gpt-4o-mini`, `openai/gpt-5-nano`, `openai/gpt-4.1-nano`, `openai/gpt-5-mini`, and `openai/gpt-4.1-mini`.

### 1. UniMoral RQ1-RQ4: family-size scaling and task readout

![UniMoral family-size scaling by RQ](../../../figures/release/option1_unimoral_family_scaling.svg)

_What it tests: UniMoral breaks moral reasoning into four human-facing steps: what action someone chooses, what moral frame the choice reflects, what factor shaped the choice, and what consequences the action may cause._

_Why it matters: moral psychology is about choices plus explanations, not just a right/wrong label. The figure shows that the winner changes across RQs, so the honest takeaway is not `larger model = better moral reasoner`; it is `different model families handle different parts of moral reasoning differently`._

![UniMoral RQ1-RQ3 exact-match accuracy](../../../figures/release/option1_unimoral_task_heatmap.svg)

_How to read it: RQ1, RQ2, and RQ3 all use exact-match accuracy, so the three classification surfaces stay comparable inside the same benchmark block. Higher means the model matched the human-labeled action, moral frame, or decision factor more often._

![UniMoral RQ4 generation quality](../../../figures/release/option1_unimoral_generation_quality.svg)

_How to read RQ4: UniMoral RQ4 shows consequence-generation quality, not accuracy. Higher is better for both metrics: BERTScore F1 measures whether the generated consequence is semantically close to the reference answer, while METEOR measures how much the wording overlaps with the reference. Llama is strongest overall._

### 2. SMID / Value Kaleidoscope: topline comparable accuracy

![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)

_What it tests: SMID asks whether a vision model can see morally important cues in images. Value Kaleidoscope asks whether a text model can spot which values, rights, or duties matter in a situation and whether they support or oppose the action._

_How to read it: UniMoral is handled in Figure 1; this chart starts at SMID for the like-for-like benchmark-faithful accuracy view. Hatched SMID rows for `DeepSeek-S`, `DeepSeek-M`, `DeepSeek-L`, `Qwen-M`, and `Llama-M` mean no public vision route, not an unparsed text result._

### 3. SMID / Value Kaleidoscope: family-size scaling

![Family scaling profile](../../../figures/release/option1_family_scaling_profile.svg)

_Why it matters: if scale helped moral perception and value recognition in a simple way, every line would climb from S to M to L. They do not. The useful read is where size helps, where it plateaus, and where it can even hurt._

_Use this next to compare size effects on SMID and Value after the combined UniMoral block, without mixing in CCD-Bench or DeNEVIL proxy evidence; missing SMID points are explicit route gaps._

### 4. CCD-Bench: cultural-cluster choice behavior

![CCD choice distribution](../../../figures/release/option1_ccd_choice_distribution.svg)

_What it tests: CCD-Bench puts models in value conflicts where ten answer options map to cultural clusters. The figure shows which cultural response styles each model over-selects or avoids relative to a 10% uniform baseline._

_Why it matters: this is not a single right-answer benchmark. It tells a moral-psych reader which culturally grounded response style a model tends to privilege when values conflict._

### 5. CCD-Bench: dominant-option concentration

![CCD dominant-option share](../../../figures/release/option1_ccd_dominant_option_share.svg)

_How to read it: this is the compact CCD-Bench summary, showing how much each line collapses onto one dominant cultural cluster and how broadly it still spreads across the option set._

### 6. DeNEVIL: proxy behavioral outcomes

![DeNEVIL proxy behavioral outcomes](../../../figures/release/option1_denevil_behavior_outcomes.svg)

_What it tests: DeNEVIL-style evaluation looks for value vulnerabilities under risky or ethically loaded prompts. In this release the paper-faithful MoralPrompt export is not local, so this figure reports auditable proxy behavior categories from saved traces._

_How to read it: protective refusals and corrective/contextual answers are the safer behaviors; risky continuations are the warning sign. This is behavior evidence from saved traces, not benchmark-faithful accuracy._

Lower-level QA/provenance figures are still generated in `figures/release/`, but the README keeps the visual story focused on these audience-facing result surfaces.

## Paper Result Comparison

![Paper result comparison](../../../figures/release/option1_paper_result_comparison.svg)

This is the replication/calibration bridge: it shows what each original paper actually reported, whether that paper had model-level results, and what the closest current release row can and cannot be compared against.

Read it strictly:

- `UniMoral` is the same benchmark family, but the paper tables use weighted F1 while the release leads with accuracy for RQ1-RQ3 and BERTScore F1/METEOR for RQ4.
- `SMID` is a human-normed image stimulus paper, so the original paper has no LLM accuracy table.
- `Value Kaleidoscope` uses Kaleido model evaluation in the paper; this release uses prompt-based ValuePrism relevance/valence rows, so it is not Kaleido model replication.
- `CCD-Bench` is the closest direct paper-vs-ours behavior comparison, but CCD-Bench is not accuracy.
- `DeNEVIL` is not paper-faithful MoralPrompt in this release; the local rows are proxy-only and not T3.

Full exact bridge: [paper-result-comparison.csv](paper-result-comparison.csv) includes paper table/source notes and source URLs.
Model-overlap map: [paper-model-overlap-map.csv](paper-model-overlap-map.csv) lists the paper-side model roster or evidence and the closest current row.

### Exact Paper Metric Bridge

| Benchmark | Paper source / metric note | Original paper exact result | Our closest current result | Status |
| :--- | :--- | :--- | :--- | :--- |
| UniMoral RQ1 action prediction | ACL Table 4 reports weighted F1 for Phi, Llama, and R1 across six languages and four prompting conditions; this row uses the strongest visible cell. | 66.38 (Phi-3.5-mini Instruct, English) | Best current release row: DeepSeek-M 0.684 | Same benchmark; different metric/model roster |
| UniMoral RQ2 moral typology | ACL Table 5 reports weighted F1 for moral-typology classification across the same three-model, six-language matrix. | 57.01 (Llama-3.1-8B Instruct, Spanish) | Best accuracy: Gemma-S 0.599; best weighted-F1 bridge: Llama-S 0.354 | Same benchmark; paper uses weighted F1 while the release headline uses accuracy |
| UniMoral RQ3 factor attribution | ACL Table 6 reports weighted F1 for factor-attribution analysis across the same three-model, six-language matrix. | 38.59 (Llama-3.1-8B Instruct, Russian) | Best accuracy: Llama-M 0.631; best weighted-F1 bridge: DeepSeek-S 0.264 | Same benchmark; paper uses weighted F1 while the release headline uses accuracy |
| UniMoral RQ4 consequence generation | ACL Table 7 reports BLEU, METEOR, and BERTScore for consequence generation by language and model; this row lists the strongest visible metric cells. | BLEU 3.29; METEOR 19.08; BERTScore 87.44 | BERTScore F1: Llama-M 0.730; METEOR: Llama-L 0.157; BLEU: Llama-M 0.0166 | Metric family overlaps; scorer scale and model roster differ |
| SMID | PLOS abstract and Study 2 participant section: image count, final participant count, total ratings, and mean ratings per image. | 2,941 images; 2,716 participants; 820,565 ratings; mean 34.88 ratings/image; averaged norms ICC >= .75 | Best current SMID average accuracy: Qwen-L 0.483; current mean 0.364 | No paper model leaderboard |
| Value Kaleidoscope / ValuePrism | AAAI/arXiv abstract plus Tables 2 and 3: ValuePrism size/quality, KaleidoSYS win rates versus GPT-4, and explanation/valence human evaluation. | ValuePrism has 218k value/rights/duties for 31k situations; 91% high-quality; KAL SYS 11B overall win rate 58.3 vs GPT-4, accuracy win 62.5; GPT-4 valence correctness 93.1 | Best current prompt-based Value average: MiniMax-L 0.741; best OpenAI text ref: GPT-5-mini Ref 0.739 | Same source family, not Kaleido model replication |
| CCD-Bench | CCD-Bench source analysis: model_summary_comparison.csv, cluster_frequency_comparison.csv, and multi_model_summary_report.txt from the public CCD-Bench analysis package. | 2,182 dilemmas; 17 LLMs; Mean cluster shares across the paper/source 17-model analysis: Nordic Europe 20.17%, Germanic Europe 12.36%, Sub-Saharan Africa 11.51%, Anglo 11.31%, Southern Asia 10.06%, Latin Europe 8.23%, Confucian Asia 7.40%, Latin America 7.23%, Middle East 5.80%, Eastern Europe 5.62%. Plural rationales 87.9%; position-bias Cramer's V 0.0586. | 19/20 current release rows are Nordic Europe dominant; GPT-5-nano Ref: option_6 (Nordic Europe) at 27.8%; effective clusters 6.79; DeepSeek-S: option_7 (Sub Saharan Africa) at 13.8%; effective clusters 9.57 | Direct behavioral comparison, but CCD-Bench is not accuracy |
| DeNEVIL / MoralPrompt | ICLR Table 1 / appendix Table 4 for MoralPrompt size and Table 16 for average generation results using ChatGPT prompts. | MoralPrompt has 2,397 prompts / 522 principles; ChatGPT-prompt Table 16 reports ChatGPT APV 65.20 +/- 26.45, GPT-4 APV 79.08 +/- 21.46, LLaMA-2-70B-chat APV 76.94 +/- 18.86 | APV/EVR/MVP n/a; strongest proxy protective-response rate is Qwen-M 99.5%; all DeNEVIL proxy rows remain not T3. | Blocked/proxy only; not paper-faithful MoralPrompt and not T3 |

### Model Overlap Map

| Benchmark | Paper model/evidence | Our matching or closest row | Overlap status | What to compare |
| :--- | :--- | :--- | :--- | :--- |
| UniMoral | Phi-3.5-mini Instruct | No exact current public row | Not run in this release | Run full paper-style UniMoral tasks if exact replication is needed. |
| UniMoral | Llama-3.1-8B Instruct | Saved/prior Llama 3.1 8B action-only follow-up | Saved/prior evidence, not a fresh full RQ1-RQ4 replication | Use only for action-prediction capability-floor context. |
| UniMoral | DeepSeek-R1-Distill-Llama-8B | DeepSeek-S | Close family label only; current row is the 70B distill recovery route, not the paper's exact 8B model | Do not call it exact replication. |
| SMID | Human norming sample | Qwen-L, MiniMax-S/L, Gemma S/M/L, Llama S/L vision rows | No paper model overlap | Compare model rows to human-norm labels, not to a paper model leaderboard. |
| Value Kaleidoscope / ValuePrism | Kaleido 60M/220M/770M/3B/11B | No Kaleido model row | Model-access gap | Current rows are prompt-based relevance/valence classification, not Kaleido generation/evaluation. |
| Value Kaleidoscope / ValuePrism | GPT-4 / GPT-3.5-turbo paper baselines | OpenAI text refs | Reference family only, not exact paper models | Use as current OpenAI calibration markers, not paper-baseline replication. |
| CCD-Bench | AI21 Jamba-1.6-large | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Claude 3.7 Sonnet | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Claude 4 Sonnet | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Command-R 08-2024 | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | DeepSeek-chat-v3-0324 | DeepSeek-M | Close model family, different version | Compare cautiously as cluster-behavior alignment. |
| CCD-Bench | Gemini 2.0 Flash 001 | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Gemini 2.5 Flash Preview 05-20 | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Llama-3.3-70B-Instruct | Llama-M | Closest direct current row | Compare cluster shares and effective-cluster concentration. |
| CCD-Bench | Llama-4-Maverick-17B-128E-Instruct | Llama-L | Closest direct current row with lower valid-choice coverage | Compare behavior; do not treat lower coverage as accuracy. |
| CCD-Bench | Microsoft Phi-4 | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | WizardLM-2-8x22B | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Mistral Nemo | May 13 exploratory Mistral Nemo | Saved/prior exploratory evidence outside the current family-size release table | Use as a clearly labeled follow-up row, not as a fresh rerun. |
| CCD-Bench | OpenAI ChatGPT-4o-latest | GPT-4o-mini Ref | OpenAI reference family only, not exact model variant | Useful as a calibration marker; not an OpenAI S/M/L family-size sweep. |
| CCD-Bench | OpenAI GPT-4.1 | GPT-4.1-mini Ref | OpenAI reference family only, not exact model variant | Useful as a calibration marker; not an OpenAI S/M/L family-size sweep. |
| CCD-Bench | Perplexity Sonar | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| CCD-Bench | Qwen2.5-72B-Instruct | Qwen-L | Closest Qwen family row only; text model version differs | Compare as family-level behavior only, not exact model replication. |
| CCD-Bench | Grok-2-1212 | No current row | Not run in this release | Add a matching route before making a paper-model replication claim. |
| DeNEVIL / MoralPrompt | ChatGPT, GPT-4, LLaMA2-70B-chat, and 24 other LLMs | No MoralPrompt row | Blocked data/scorer gap; proxy is not T3 | Do not compare DeNEVIL proxy categories to MoralPrompt APV/EVR/MVP. |


## Results First

This is the fastest way to read the deliverable: which lines already have usable results, what is directly comparable now, and where the current release snapshot stops.

| Line | Scope | Status | Coverage | Note |
| --- | --- | --- | --- | --- |
| `Qwen-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Qwen release line. |
| `DeepSeek-M` | Frozen Option 1 | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Primary medium DeepSeek release line: UniMoral 0.684, Value 0.635, CCD 2,177/2,182 valid choices, Denevil 20,514/20,518 visible proxy responses. |
| `Gemma-S` | Frozen Option 1 | Done | 5 benchmark lines complete (`Denevil` via proxy) | Primary small Gemma release line. |
| `Llama-S` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally, outside the frozen Option 1 counts. |
| `Gemma-M` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Gemma-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | Finished locally on April 21, 2026. |
| `Qwen-M` | Complete local line | Done | Earlier text checkpoints withdrawn; UniMoral action prediction done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Complete local line | Done | SMID recovery stands; UniMoral action prediction done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | SMID recovery complete; clean text rerun finished locally. |
| `Llama-M` | Complete local line | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Completed locally on April 22, 2026. |
| `DeepSeek-L` | Complete local line | Done | No SMID route; UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy parsed from saved R1 shards | Large R1 text rerun complete from saved logs; keep it text-only because no SMID route exists. |
| `Llama-L` | Complete local line | Done | SMID complete; UniMoral action prediction done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy finished at 100.0%. | SMID complete; local text rerun finished successfully through the Denevil proxy task. |
| `DeepSeek-S` | Complete local line | Done | No SMID route; UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy are complete in the May 9 no-thinking saved logs | May 9 no-thinking rerun passes visible-answer validation; SMID remains unavailable for this DeepSeek size slot. |
| `MiniMax-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) using MiniMax-M2.5 text plus the shared MiniMax-01 SMID recovery route | The direct-provider MiniMax rerun finished successfully through the Denevil proxy task. |
| `MiniMax-M` | Complete local text line | Done | Clean MiniMax-M2.5 text/proxy benchmarks complete; no medium SMID route fixed yet. | Clean direct MiniMax-M2.5 text run is complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; no medium SMID route fixed yet. Build-time persisted text counts: UniMoral action prediction 8,784/8,784; Value 65,520/65,520; CCD 2,182/2,182; Denevil proxy 20,518/20,518. |
| `MiniMax-S` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) | MiniMax-S now uses the clean direct MiniMax-M2.1 text rerun plus the completed MiniMax-01 SMID recovery route. |

### Current Comparable Accuracy Snapshot

The table below is intentionally limited to the three directly comparable accuracy metrics: `UniMoral`, `SMID`, and `Value Kaleidoscope`. `CCD-Bench` and `Denevil` are reported separately below as coverage / proxy evidence because neither benchmark currently supports a benchmark-faithful universal accuracy claim in this public release. `n/a` marks benchmarks that are route-missing, incomplete, or intentionally withheld after response-format validation.

Metric definition version: `2026-04-30`. The visible-answer parsing rules behind these columns are versioned explicitly so later scorer changes do not silently rewrite the public story.

| Line | UniMoral action | SMID average | Value Kaleidoscope average | Comparison note |
| :--- | ---: | ---: | ---: | --- |
| `Qwen-S` | 0.647 | 0.368 | 0.682 | Comparable on all three benchmark-faithful accuracy panels. |
| `Qwen-M` | 0.665 | n/a | 0.675 | Text-only comparable line; no public SMID route on this slot. |
| `Qwen-L` | 0.665 | 0.483 | 0.653 | Comparable on all three benchmark-faithful accuracy panels. |
| `MiniMax-S` | 0.661 | 0.432 | 0.740 | Comparable on all three benchmark-faithful accuracy panels. |
| `MiniMax-M` | 0.659 | n/a | 0.740 | Text-only comparable line; no public SMID route on this slot. |
| `MiniMax-L` | 0.661 | 0.199 | 0.741 | Comparable on all three benchmark-faithful accuracy panels. |
| `DeepSeek-S` | 0.661 | n/a | 0.695 | Text-only comparable no-thinking rerun; no public SMID route on this slot. |
| `DeepSeek-M` | 0.684 | n/a | 0.635 | Text-only comparable line; no public SMID route on this slot. |
| `DeepSeek-L` | 0.563 | n/a | 0.681 | Text-only comparable line; no public SMID route on this slot. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Comparable on all three benchmark-faithful accuracy panels. |
| `Llama-M` | 0.670 | n/a | 0.724 | Text-only comparable line; no public SMID route on this slot. |
| `Llama-L` | 0.660 | 0.386 | 0.692 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-M` | 0.663 | 0.364 | 0.664 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-L` | 0.661 | 0.412 | 0.656 | Comparable on all three benchmark-faithful accuracy panels. |
| `GPT-4o-mini Ref` | 0.673 | n/a | 0.701 | GPT-4o-mini Ref text-only OpenAI reference; outside the S/M/L family curves. |
| `GPT-5-nano Ref` | 0.654 | n/a | 0.617 | GPT-5-nano Ref text-only OpenAI reference; outside the S/M/L family curves. |
| `GPT-4.1-nano Ref` | 0.646 | n/a | 0.673 | GPT-4.1-nano Ref text-only OpenAI reference; outside the S/M/L family curves. |
| `GPT-5-mini Ref` | 0.678 | n/a | 0.739 | GPT-5-mini Ref text-only OpenAI reference; outside the S/M/L family curves. |
| `GPT-4.1-mini Ref` | 0.679 | n/a | 0.735 | GPT-4.1-mini Ref text-only OpenAI reference; outside the S/M/L family curves. |

_The topline comparable-accuracy chart already appears above in **Benchmark Result Visuals**. The table here keeps the exact numeric readout inline without repeating the same headline figure._

### DeepSeek S/M/L Log-Derived Readout

`DeepSeek-S`, `DeepSeek-M`, and `DeepSeek-L` all have explicit text-only results from saved logs. `DeepSeek-S` points at the May 9 no-thinking rerun artifacts, `DeepSeek-M` remains the frozen medium text-only line, and `DeepSeek-L` points at the saved R1 shard rerun. No DeepSeek line has a SMID vision route.

| Line | Comparable text accuracy | CCD-Bench saved choices | DeNEVIL proxy visibility | Public interpretation |
| --- | --- | --- | --- | --- |
| `DeepSeek-S` | UniMoral 0.661; Value 0.695 | 2,180 / 2,182 (99.9%) | 20,474 / 20,518 (99.8%) | Valid text-only no-thinking rerun from saved May 9 logs: UniMoral and Value Kaleidoscope are scored, CCD-Bench has near-complete parseable choices, and Denevil is proxy-only behavioral evidence. No SMID route exists. |
| `DeepSeek-M` | UniMoral 0.684; Value 0.635 | 2,177 / 2,182 (99.8%) | 20,514 / 20,518 (100.0%) | Valid text-only comparable line from existing logs: UniMoral and Value Kaleidoscope are scored, CCD-Bench has near-complete parseable choices, and Denevil is proxy-only behavioral evidence. No SMID route exists. |
| `DeepSeek-L` | UniMoral 0.563; Value 0.681 | 2,109 / 2,182 (96.7%) | 20,331 / 20,518 (99.1%) | Valid text-only large R1 rerun from saved shard logs: UniMoral and Value Kaleidoscope are scored, CCD-Bench has high parseable-choice coverage, and Denevil is proxy-only behavioral evidence. No SMID route exists. |
## Interpretation

These are the strongest claims the current public evidence supports. They use only the benchmarks with directly comparable accuracy metrics and keep `Denevil` proxy results out of any macro-accuracy claim.

### Interpretation At A Glance

| Claim | Evidence | Why it matters |
| --- | --- | --- |
| Strongest fully observed comparable line | `MiniMax-S` averages 0.611 across UniMoral action 0.661, SMID 0.432, and Value 0.740. | This is the cleanest all-around topline because it includes text moral reasoning, image moral perception, and value recognition on the same line. |
| Strongest text-only comparable line | `GPT-5-mini Ref` reaches UniMoral 0.678 and Value 0.739, a two-metric mean of 0.708. | This is the best answer if the PI asks about text moral reasoning only; it is not the all-around winner because SMID is missing. |
| OpenAI/GPT text references | 5 OpenAI rows are included. Best OpenAI UniMoral: `GPT-4.1-mini Ref` at 0.679; best OpenAI Value: `GPT-5-mini Ref` at 0.739. | These tell us where GPT-style text routes sit relative to the open-weight families; they do not make a GPT S/M/L scaling claim and do not cover SMID. |
| Small-model capability floor | May 13 follow-up: `Mistral Nemo` reaches 0.648 on UniMoral; the 7B-12B routes sit in a narrow 0.632-0.648 band; `Llama 3.2 1B` falls to 0.406 with only 73.6% answered. | This is the practical capacity warning: below the mid-sized instruction-model range, the model may stop reliably following human moral-choice tasks, but above that floor older routes can still be useful baselines. |
| Hardest current comparable benchmark | `SMID` has the lowest mean accuracy at 0.364 and the widest spread at 0.284. | The hard part is visual moral perception: models do not just need moral vocabulary, they need to read morally relevant cues in images. |
| Closest thing to saturation | `UniMoral` has the tightest range, from 0.563 to 0.684 (0.121 spread). | Most text models are already in the same band on the basic human-choice layer, so the more interesting story is which UniMoral subtask each model handles best. |
| Scaling-law read | `Gemma` is still the cleanest full S/M/L sweep. Even there, UniMoral rises from 0.635 to 0.661, Value rises from 0.593 to 0.656, but SMID is nearly flat overall (0.417 to 0.412). | The data say scale is useful but task-dependent. Bigger models are not automatically better moral reasoners across every benchmark. |

### Benchmark Reading Guide

Before comparing charts, anchor each benchmark to its source paper. These benchmarks do not all ask for the same kind of moral competence, so a clean read depends on matching the score to the paper's original intent.

| Benchmark readout | In plain language: what it asks | Why it matters for moral psychology | How to read this release |
| --- | --- | --- | --- |
| `UniMoral RQ1: action prediction` | Given a dilemma and two possible actions, predict which action the human annotator chose. | This is descriptive moral choice: it asks whether the model can track situated human decisions, not whether it can declare the one correct answer. | Higher accuracy means the model better matched human choices. Scores are close together, so RQ1 is a useful sanity check but not the whole story. |
| `UniMoral RQ2: moral typology` | Given the chosen action, label the reasoning style: deontological, utilitarian, rights-based, or virtuous. | The same action can come from different moral theories. This task checks whether the model can name the reasoning frame behind a choice. | Read this separately from RQ1: a model can guess the action while still misunderstanding the moral theory behind it. |
| `UniMoral RQ3: factor attribution` | Identify what shaped the decision, such as emotion, moral values, culture, responsibility, relationships, legality, politeness, or sacred values. | Moral psychology cares about why people choose, not only what they choose. RQ3 tests whether the model can recover those human explanation factors. | Higher accuracy means the model better identifies the reason behind the choice. Low or uneven scores mean the model may know the answer but not the human motive. |
| `UniMoral RQ4: consequence generation` | Generate likely consequences of the selected action. | Consequences connect moral choice to expected harm, benefit, social reaction, and future responsibility, which are central to moral reasoning. | Read RQ4 as generation quality. BERTScore F1 captures meaning overlap; METEOR captures wording overlap. Neither is the same as classification accuracy. |
| `SMID` | Look at real images and infer moral wrongness or the dominant moral foundation. | Moral judgment is often visual, social, and affective. SMID asks whether models can see morally relevant cues in concrete scenes, not only reason over text. | Higher accuracy means closer alignment with human image judgments. This is the current bottleneck because image-based moral cues are harder and more ambiguous than text labels. |
| `Value Kaleidoscope` | For a situation and a candidate value, right, or duty, decide whether it is relevant and whether it supports, opposes, or fits either way. | Pluralistic moral judgment often involves several values in tension. This benchmark checks whether the model can recognize that value structure before making any final decision. | Higher accuracy means better value tagging and polarity assignment. It shows whether the model sees the value structure, not whether it solved the whole ethical dilemma. |
| `CCD-Bench` | Choose among ten culturally grounded responses to a cross-cultural dilemma. | Cultural conflict is a moral-psych question because different communities may weigh duties, relationships, hierarchy, autonomy, and social harmony differently. | Do not read CCD-Bench as universal accuracy. Read it as style: which cultural cluster the model leans toward, and whether it collapses too strongly onto one option. |
| `DeNEVIL` | Probe how the model behaves when prompts try to surface unethical or value-violating content. | This matters for alignment: a model can classify moral labels well but still respond poorly when asked to generate risky behavior. | This release uses proxy traces, so read protective, contextual, risky, and empty-response categories as behavior evidence, not as paper-faithful DeNEVIL scoring. |

### Benchmark Difficulty Profile

![Benchmark difficulty profile](../../../figures/release/option1_benchmark_difficulty_profile.svg)

_Figure 3. Mean, low, and high accuracy for the three directly comparable benchmark groups; lower means and wider ranges indicate a harder or less stable benchmark in the current public slice._

| Benchmark | Mean accuracy | Best line | Lowest line | Spread | Reading |
| --- | ---: | --- | --- | ---: | --- |
| `UniMoral` | 0.653 | `DeepSeek-M` (0.684) | `DeepSeek-L` (0.563) | 0.121 | Tightest spread; current lines cluster closely. |
| `SMID` | 0.364 | `Qwen-L` (0.483) | `MiniMax-L` (0.199) | 0.284 | Lowest mean and widest spread in the current comparable slice. |
| `Value Kaleidoscope` | 0.673 | `MiniMax-L` (0.741) | `Llama-S` (0.529) | 0.213 | Mid-range difficulty with meaningful but not extreme variation. |

### Family Scaling Profile

_The headline family-scaling figure already appears above in **Benchmark Result Visuals**. The summary table below keeps the size-by-family takeaways inline here without re-embedding the same chart._

| Family | Evidence scope | Numeric pattern | Cautious interpretation |
| --- | --- | --- | --- |
| `Qwen` | Text benchmarks now have S/M/L comparable points, and SMID has S/L evidence after the recovered large line. | UniMoral: S 0.647 -> M 0.665 -> L 0.665<br/>SMID: S 0.368 -> L 0.483<br/>Value Kaleidoscope: S 0.682 -> M 0.675 -> L 0.653 | Qwen improves from S to M on text and then mostly plateaus. On SMID, the recovered L vision line is clearly stronger than S. That makes Qwen a case where scale helps some surfaces but not all of them. |
| `MiniMax` | 3 comparable metric series available. | UniMoral: S 0.661 -> M 0.659 -> L 0.661<br/>SMID: S 0.432 -> L 0.199<br/>Value Kaleidoscope: S 0.740 -> M 0.740 -> L 0.741 | Current public evidence is too sparse for a stronger within-family scaling claim; report the observed points and avoid turning route gaps into model failures. |
| `DeepSeek` | The S/M/L text lines are now accuracy-comparable where text-only metrics exist, but no DeepSeek slot has a public SMID route. | UniMoral: S 0.661 -> M 0.684 -> L 0.563<br/>Value Kaleidoscope: S 0.695 -> M 0.635 -> L 0.681 | DeepSeek should be discussed as a text-only curve. It is useful for UniMoral and Value comparisons, but it cannot support an all-around moral-psych claim because the image benchmark is absent. |
| `Llama` | Text benchmarks now have S/M/L comparable points, and SMID has S/L evidence. | UniMoral: S 0.648 -> M 0.670 -> L 0.660<br/>SMID: S 0.216 -> L 0.386<br/>Value Kaleidoscope: S 0.529 -> M 0.724 -> L 0.692 | Llama gets much better after the small line, especially on text, and S-to-L also helps SMID. But M still beats L on some text metrics, so the useful story is improvement after S, not a clean monotonic ladder. |
| `Gemma` | Full S/M/L comparable sweep on all three comparable benchmarks. | UniMoral: S 0.635 -> M 0.663 -> L 0.661<br/>SMID: S 0.417 -> M 0.364 -> L 0.412<br/>Value Kaleidoscope: S 0.593 -> M 0.664 -> L 0.656 | Gemma is the cleanest size test in this repo, and it still does not give a simple bigger-is-better story: text tasks improve overall, but SMID dips at M and rebounds at L. |
| `OpenAI Ref` | Five text-only reference rows, not an OpenAI family-size scaling sweep. | UniMoral: range 0.646-0.679<br/>best GPT-4.1-mini Ref 0.679<br/>Value Kaleidoscope: range 0.617-0.739<br/>best GPT-5-mini Ref 0.739 | The OpenAI rows are a sanity check for text-side performance. They show that the best GPT text refs are very competitive on UniMoral and Value, but they do not answer the vision question and should not be renamed as GPT S/M/L. |

### Small-Model Follow-Up: Capability Floor

The May 13 follow-up brings the older/smaller `Mistral`, `Qwen`, and `Llama` routes into the main interpretation. It is not a replacement for the current S/M/L release matrix; it answers a narrower question: where does moral-choice performance start to fall off?

**So what:** `Mistral Nemo` is the top follow-up line on UniMoral at 0.648, but `Qwen2.5 7B`, `Llama 3.1 8B`, and `Llama 3 8B` are close behind from 0.632 to 0.640. The real separation is `Llama 3.2 1B` at 0.406 with a lower answer rate. For reporting, say this as a capability-floor result: once models are around the 7B-12B instruction range, several older routes are competitive on text moral-choice/style checks; the 1B route is the line that clearly falls below the floor.

**Compared with the current main results:** this supports the same high-level story rather than changing it. Text moral-choice scores mostly live in a narrow band once the model is capable enough, so the more important differences are benchmark-specific: SMID remains the hard visual-moral bottleneck in the main matrix, while CCD-Bench remains a cultural-choice style readout instead of an accuracy race.

**CCD readout:** all five follow-up lines peak on `Nordic Europe`; the difference is concentration, not correctness. `Llama 3.2 1B` is the most diffuse at 15.9% dominant share, while `Mistral Nemo` is most concentrated at 25.3%. That means the small-model follow-up does not discover a new cultural direction; it shows how sharply each route collapses onto the same dominant cluster.

| Follow-up model | Size slot | UniMoral accuracy | CCD dominant cluster | CCD dominant share | Interpretation |
| --- | ---: | ---: | --- | ---: | --- |
| `Mistral Nemo` | 12B | 0.648 | Nordic Europe | 25.3% | Strongest follow-up line, but still part of the same mid-sized text band. |
| `Qwen2.5 7B` | 7B | 0.640 | Nordic Europe | 17.8% | Close to Mistral on UniMoral with less CCD concentration. |
| `Llama 3.1 8B` | 8B | 0.639 | Nordic Europe | 24.7% | Similar UniMoral score to Qwen and Llama 3; not a clean size ladder. |
| `Llama 3 8B` | 8B | 0.632 | Nordic Europe | 22.0% | Slightly lower but still inside the 7B-12B cluster. |
| `Llama 3.2 1B` | 1B | 0.406 | Nordic Europe | 15.9% | Clear low line; useful as the practical floor warning. |

![Additional model sweep UniMoral accuracy](../../../figures/exploratory/additional_model_sweep_unimoral_accuracy.svg)

![Additional model sweep scaling readout](../../../figures/exploratory/additional_model_sweep_scaling.svg)

![Additional model sweep CCD concentration](../../../figures/exploratory/additional_model_sweep_ccd_dominant_share.svg)

Full tables and provenance remain in [results/exploratory/2026-05-13-additional-model-sweep](../../../results/exploratory/2026-05-13-additional-model-sweep/).


### CCD-Bench Choice Behavior

CCD-Bench should not be flattened into a universal accuracy number. The paper asks models to choose among ten culturally grounded options, so the public headline result is now choice behavior: which canonical clusters each line over-indexes or under-indexes relative to a uniform 10% baseline, and how concentrated that choice pattern becomes on its dominant cluster.

CCD option order follows the paper's canonical cluster IDs: 1 = Anglo; 2 = Eastern Europe; 3 = Latin America; 4 = Latin Europe; 5 = Confucian Asia; 6 = Nordic Europe; 7 = Sub Saharan Africa; 8 = Southern Asia; 9 = Germanic Europe; 10 = Middle East.

_The two headline CCD figures already appear above in **Benchmark Result Visuals**. The full ten-option numeric table is published in `results/release/2026-04-19-option1/ccd-choice-distribution.csv`; the compact table below keeps the most PI-facing CCD readouts inline without turning parser coverage into the headline claim._

| Line | Dominant cluster | Top-cluster share | Effective clusters | Behavioral note |
| --- | --- | ---: | ---: | --- |
| `Qwen-S` | option_6 (Nordic Europe) | 19.2% | 8.91 | Compare against the heatmap above, not as scalar accuracy. |
| `Qwen-M` | option_6 (Nordic Europe) | 21.9% | 8.29 | Compare against the heatmap above, not as scalar accuracy. |
| `Qwen-L` | option_6 (Nordic Europe) | 23.4% | 7.97 | Compare against the heatmap above, not as scalar accuracy. |
| `MiniMax-S` | option_6 (Nordic Europe) | 17.3% | 9.20 | Compare against the heatmap above, not as scalar accuracy. |
| `MiniMax-M` | option_6 (Nordic Europe) | 18.3% | 9.01 | Compare against the heatmap above, not as scalar accuracy. |
| `MiniMax-L` | option_6 (Nordic Europe) | 18.7% | 9.02 | Compare against the heatmap above, not as scalar accuracy. |
| `DeepSeek-S` | option_7 (Sub Saharan Africa) | 13.8% | 9.57 | Compare against the heatmap above, not as scalar accuracy. |
| `DeepSeek-M` | option_6 (Nordic Europe) | 22.6% | 7.99 | Compare against the heatmap above, not as scalar accuracy. |
| `DeepSeek-L` | option_6 (Nordic Europe) | 20.7% | 8.68 | Compare against the heatmap above, not as scalar accuracy. |
| `Llama-S` | option_6 (Nordic Europe) | 23.9% | 7.24 | Compare against the heatmap above, not as scalar accuracy. |
| `Llama-M` | option_6 (Nordic Europe) | 20.6% | 8.03 | Compare against the heatmap above, not as scalar accuracy. |
| `Llama-L` | option_6 (Nordic Europe) | 23.5% | 7.67 | Compare against the heatmap above, not as scalar accuracy. |
| `Gemma-S` | option_6 (Nordic Europe) | 21.6% | 8.37 | Compare against the heatmap above, not as scalar accuracy. |
| `Gemma-M` | option_6 (Nordic Europe) | 18.6% | 8.89 | Compare against the heatmap above, not as scalar accuracy. |
| `Gemma-L` | option_6 (Nordic Europe) | 17.6% | 9.05 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-4o-mini Ref` | option_6 (Nordic Europe) | 17.1% | 8.94 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-5-nano Ref` | option_6 (Nordic Europe) | 27.8% | 6.79 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-4.1-nano Ref` | option_6 (Nordic Europe) | 21.5% | 8.40 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-5-mini Ref` | option_6 (Nordic Europe) | 25.3% | 7.13 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-4.1-mini Ref` | option_6 (Nordic Europe) | 22.4% | 8.07 | Compare against the heatmap above, not as scalar accuracy. |

### DeNEVIL Proxy Behavioral Evidence

**Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring.**

The repo still lacks a stable local `MoralPrompt` export, so paper-aligned APV / EVR / MVP are `n/a` in this public package. Instead, the release now leads with auditable behavioral outcomes over the FULCRA-backed proxy traces: protective refusals, redirects, corrective/contextual responses, direct task answers, potentially risky continuations, ambiguous visible answers, and empty traces.

The main DeNEVIL result surface is the visible-behavior mix across the full released proxy archive. Route/model provenance, sample volume, completion state, timestamps, and visible-response coverage are still exported in CSV/SVG artifacts, but they are not repeated in the README because they are QA/provenance rather than the audience-facing result story.

_The headline DeNEVIL behavioral-outcomes chart already appears above in **Benchmark Result Visuals**. This section keeps the explanatory framing and compact line-level behavior table without re-embedding low-level QA charts._

The compact behavior table below is the quickest line-level read.

| Line | Refusal | Redirect | Corrective/contextual | Direct answer | Risky continuation | Ambiguous | Empty | Dominant behavior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `Qwen-S` | 21.5% | 8.0% | 69.9% | 0.0% | 0.1% | 0.4% | 0.0% | Corrective / contextual response |
| `Qwen-M` | 22.1% | 8.4% | 69.0% | 0.0% | 0.2% | 0.3% | 0.0% | Corrective / contextual response |
| `Qwen-L` | 29.3% | 5.7% | 64.3% | 0.0% | 0.2% | 0.4% | 0.0% | Corrective / contextual response |
| `MiniMax-S` | 30.8% | 4.2% | 64.4% | 0.0% | 0.4% | 0.2% | 0.0% | Corrective / contextual response |
| `MiniMax-M` | 31.0% | 4.2% | 64.3% | 0.0% | 0.4% | 0.1% | 0.0% | Corrective / contextual response |
| `MiniMax-L` | 30.7% | 4.2% | 64.4% | 0.0% | 0.4% | 0.2% | 0.0% | Corrective / contextual response |
| `DeepSeek-S` | 20.8% | 4.9% | 72.5% | 0.0% | 1.4% | 0.2% | 0.2% | Corrective / contextual response |
| `DeepSeek-M` | 31.1% | 6.1% | 62.0% | 0.0% | 0.2% | 0.6% | 0.0% | Corrective / contextual response |
| `DeepSeek-L` | 37.8% | 5.3% | 51.9% | 0.0% | 0.7% | 3.5% | 0.9% | Corrective / contextual response |
| `Llama-S` | 41.0% | 1.3% | 56.5% | 0.0% | 0.1% | 1.2% | 0.0% | Corrective / contextual response |
| `Llama-M` | 26.0% | 1.8% | 70.5% | 0.0% | 0.1% | 1.6% | 0.0% | Corrective / contextual response |
| `Llama-L` | 22.9% | 1.4% | 74.7% | 0.0% | 0.2% | 0.8% | 0.0% | Corrective / contextual response |
| `Gemma-S` | 36.1% | 12.4% | 48.7% | 0.0% | 0.1% | 2.7% | 0.0% | Corrective / contextual response |
| `Gemma-M` | 43.3% | 4.1% | 44.9% | 0.0% | 0.0% | 7.6% | 0.0% | Corrective / contextual response |
| `Gemma-L` | 40.4% | 8.9% | 49.0% | 0.0% | 0.1% | 1.6% | 0.0% | Corrective / contextual response |

Low-level DeNEVIL QA/provenance artifacts remain exported in the release folder for audit, but the README does not embed the status, sample-volume, or visible-response-rate charts.

A few safe qualitative examples help clarify what the proxy traces actually look like in practice.

| Model line | Proxy prompt type | Shortened model output pattern | Interpretable signal |
| --- | --- | --- | --- |
| `Qwen-S` | Loaded social / political judgment | Corrective / contextual response | The visible trace gives a corrective or contextual answer, which is useful proxy behavior evidence even though the release does not claim paper-faithful Denevil scoring. |
| `Llama-L` | Illicit access / sabotage | Protective refusal | The visible trace refuses the request directly, which is a clear protective behavioral outcome in the proxy release. |
| `DeepSeek-S` | Loaded social / political judgment | No visible answer | This sample shows why the proxy package separates completed archives from the subset of traces that actually surface a visible public answer. |

### Reporting Guardrails

- Do not fold `Denevil` into any benchmark-faithful macro-accuracy claim; it remains proxy-only behavioral evidence and traceability support even when its completion status is `Done`.
- Read `CCD-Bench` in its dedicated choice-behavior figures, not in the family scaling line chart. `CCD-Bench` valid-choice coverage stays appendix QA only; the headline result is the cluster-selection heatmap and concentration summary.
- Read `Denevil` only through the dedicated proxy evidence package. Main figures show behavioral outcomes from released traces; sample counts, generated counts, route/model metadata, and timestamps stay in the appendix provenance tables. Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring.
- Read the CCD heatmap as deviation from a 10% uniform baseline over the paper's ten canonical cluster options. It compares cultural-choice behavior, not correctness against one universal target option.
- Read `DeepSeek-S` as a text-only no-SMID line from the May 9 no-thinking saved logs: `CCD-Bench valid-choice coverage = 99.9%` (2,180 / 2,182), and `Denevil visible proxy coverage = 99.8%` (20,474 / 20,518). These are parser/proxy coverage checks, not CCD or Denevil accuracy.
- Do not call `GPT-5-mini Ref` the best overall line across all tasks; its text results are strong, but there is no SMID route on that line.
- Do not claim a universal scaling law from these figures. `Gemma` is the only family with a full three-metric S/M/L sweep, the broader `Qwen` / `DeepSeek` / `Llama` text-side curves still move in mixed directions, and the OpenAI rows are text-reference markers rather than S/M/L size curves.
- Keep `DeepSeek-S` out of all-around winner claims because it has no SMID route, but keep its validated text metrics in the comparable text rows.
- Treat missing comparable cells as evidence limits rather than model failures. Several large lines are complete operationally but still lack directly comparable public metrics for some benchmarks.

## Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `May 26, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Current project total cost | `$870.30` |
| Total cost breakdown | MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$325.66`; OpenAI API reference sweep: `$39.98`. |
| Cost scope | User-confirmed total spend through the latest saved reruns parsed in this repo. |
| Intended use | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Current public matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Model families in scope | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |
| OpenAI reference markers | `GPT-4o-mini Ref`, `GPT-5-nano Ref`, `GPT-4.1-nano Ref`, `GPT-5-mini Ref`, and `GPT-4.1-mini Ref`; text-only refs, not OpenAI S/M/L scaling rows |
| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |
| Extra completed local line outside release | `Llama` small via `llama-3.2-11b-vision-instruct`, complete across `5` papers / `7` tasks |
| Provider / temperature | `OpenRouter`, `temperature=0` |
| Current live reruns | No currently published line is still running locally. |
| Next restart focus | No published rerun is active right now. |
| Release guardrail | Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables. |
| CI workflow | [Workflow](https://github.com/Center-for-Ethical-Intelligence/moral-psychology-benchmark/actions/workflows/ci.yml) |

### Current Operations Highlights

This compact block sits between the topline tables and the detailed progress matrix so the live state stays readable.

- Active open-source reruns: none are currently shown in the published matrix.
- Stalled or queued follow-up work: no published partial or queued follow-up line is waiting right now.
- Complete local lines beyond the frozen `Option 1` slice: `Llama-S`, `Gemma-M`, `Gemma-L`, `Qwen-M`, `Qwen-L`, `Llama-M`, `DeepSeek-L`, `Llama-L`, `DeepSeek-S`, `MiniMax-L`, and `MiniMax-S`.
- Release guardrails: Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables.

## Model Size Cheat Sheet

This is the quick lookup table for each family-size slot: the exact route name, the visible `B` count from the route when it exists, and whether that slot is text-only or split across text and vision.

| Family | Slot | Text route | Text size | Vision route | Vision size | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| `Qwen` | `S (Small)` | `openrouter/qwen/qwen3-8b` | `8B` | `openrouter/qwen/qwen3-vl-8b-instruct` | `8B` | Text benchmarks + SMID |
| `Qwen` | `M (Medium)` | `openrouter/qwen/qwen3-14b` | `14B` | `TBD` | `TBD` | Text benchmarks only |
| `Qwen` | `L (Large)` | `openrouter/qwen/qwen3-32b` | `32B` | `openrouter/qwen/qwen2.5-vl-72b-instruct (recovery complete)` | `72B` | Text benchmarks + SMID |
| `MiniMax` | `S (Small)` | `minimax-m2.1 (direct MiniMax API)` | `n/a` | `minimax-01 (SMID recovery route)` | `n/a` | Text benchmarks + SMID |
| `MiniMax` | `M (Medium)` | `minimax-m2.5 (direct MiniMax API clean run)` | `n/a` | `TBD` | `TBD` | Text benchmarks only |
| `MiniMax` | `L (Large)` | `openrouter/minimax/minimax-m2.5` | `Undisclosed` | `openrouter/minimax/minimax-01 (shared SMID recovery route)` | `Undisclosed` | Text benchmarks + SMID |
| `DeepSeek` | `S (Small)` | `openrouter/deepseek/deepseek-r1-distill-llama-70b (DeepInfra-pinned recovery route)` | `70B` | `-` | `-` | Text benchmarks only |
| `DeepSeek` | `M (Medium)` | `openrouter/deepseek/deepseek-chat-v3.1` | `Undisclosed` | `-` | `-` | Text benchmarks only |
| `DeepSeek` | `L (Large)` | `openrouter/deepseek/deepseek-r1` | `Undisclosed` | `-` | `-` | Text benchmarks only |
| `Llama` | `S (Small)` | `openrouter/meta-llama/llama-3.2-11b-vision-instruct` | `11B` | `same as text route` | `11B` | Text benchmarks + SMID |
| `Llama` | `M (Medium)` | `openrouter/meta-llama/llama-3.3-70b-instruct` | `70B` | `-` | `-` | Text benchmarks only |
| `Llama` | `L (Large)` | `openrouter/meta-llama/llama-4-maverick` | `Undisclosed` | `same as text route` | `Undisclosed` | Text benchmarks + SMID |
| `Gemma` | `S (Small)` | `openrouter/google/gemma-3-4b-it` | `4B` | `same as text route` | `4B` | Text benchmarks + SMID |
| `Gemma` | `M (Medium)` | `openrouter/google/gemma-3-12b-it` | `12B` | `same as text route` | `12B` | Text benchmarks + SMID |
| `Gemma` | `L (Large)` | `openrouter/google/gemma-3-27b-it` | `27B` | `same as text route` | `27B` | Text benchmarks + SMID |

_`Text size` and `Vision size` come from the route names. `Undisclosed` means the provider route name does not publish a `B` count._

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
| `DeepSeek-S text batch` | Done | May 9 no-thinking rerun passes visible-answer validation; SMID remains unavailable for this DeepSeek size slot. |
| `DeepSeek-L R1 text batch` | Done | Saved R1 shards now cover UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy; no SMID route exists. |
| `Llama-L SMID` | Done | The large Llama vision line is complete locally. |
| `Next queued text lines` | Done | No currently published line remains queued behind an active rerun. |

## Start Here

### Reports

- `jenny-group-report.md`: mentor-facing report with the benchmark list, progress matrix, model roster, and current results
- `topline-summary.md`: shortest narrative summary of the frozen Option 1 snapshot
- `release-manifest.json`: machine-readable release index
- [how to read the results](../../../docs/how-to-read-results.md): plain-language explanation of the report terms

### Figures

- [UniMoral RQ1-RQ3 accuracy](../../../figures/release/option1_unimoral_task_heatmap.svg): main classification view using one shared exact-match accuracy metric
- [UniMoral RQ4 generation quality](../../../figures/release/option1_unimoral_generation_quality.svg): separate generation-quality view using BERTScore F1 and METEOR
- [UniMoral family-size scaling](../../../figures/release/option1_unimoral_family_scaling.svg): RQ-by-RQ S/M/L line charts for the UniMoral result surface
- [grouped bar chart](../../../figures/release/option1_benchmark_accuracy_bars.svg): SMID/Value cross-model comparison after the UniMoral figures
- [benchmark difficulty profile](../../../figures/release/option1_benchmark_difficulty_profile.svg): mean and spread for the directly comparable benchmark groups
- [family scaling profile](../../../figures/release/option1_family_scaling_profile.svg): family-size scaling across SMID and Value only
- [CCD choice heatmap](../../../figures/release/option1_ccd_choice_distribution.svg): main CCD-Bench result showing deviation from the 10% uniform baseline across the ten canonical clusters
- [CCD concentration summary](../../../figures/release/option1_ccd_dominant_option_share.svg): dominant-cluster share plus effective-cluster count
- [DeNEVIL behavioral outcomes](../../../figures/release/option1_denevil_behavior_outcomes.svg): main proxy-result view showing visible behavior categories by model line

## Status Key

| Mark | Meaning |
| --- | --- |
| `Done` | Finished with a usable result. |
| `Proxy (not T3)` | Finished only with a substitute proxy dataset; proxy evidence is not a Tier 3 benchmark-faithful result. |
| `Live` | Currently running locally. |
| `Partial` | Started locally and produced some usable outputs, but the line is not yet complete. |
| `Error` | A formal attempt exists, but the current result is not usable. |
| `Queue` | Approved and queued next. |
| `TBD` | The family-size route is not frozen yet. |
| `-` | No run is planned on that line right now. |

## Family-Size Progress Matrix

This is the cleanest public-facing summary of the current published matrix.

| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | MoralBench | EMNLP Educator | Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `Qwen-S` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Frozen Option 1 line. |
| `Qwen-M` | Done | TBD | Done | Done | Proxy (not T3) | Done | Done | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | SMID recovery complete; clean text rerun finished locally. |
| `MiniMax-S` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Direct MiniMax-M2.1 text rerun complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; SMID uses the completed MiniMax-01 recovery route. |
| `MiniMax-M` | Done | TBD | Done | Done | Proxy (not T3) | Done | Done | Clean direct MiniMax-M2.5 text run is complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; no medium SMID route fixed yet. Build-time persisted text counts: UniMoral action prediction 8,784/8,784; Value 65,520/65,520; CCD 2,182/2,182; Denevil proxy 20,518/20,518. |
| `MiniMax-L` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Shared MiniMax-01 SMID recovery complete; the MiniMax-M2.5 text rerun is now fully persisted through the Denevil proxy task (100.0%). |
| `DeepSeek-S` | Done | - | Done | Done | Proxy (not T3) | Done | Done | No SMID route; May 9 no-thinking text rerun is complete and visible-answer validated. |
| `DeepSeek-M` | Done | - | Done | Done | Proxy (not T3) | Done | Done | Frozen medium text line; no SMID route was included. UniMoral 0.684, Value 0.635, CCD 2,177/2,182 valid choices, Denevil 20,514/20,518 visible proxy responses. |
| `DeepSeek-L` | Done | - | Done | Done | Proxy (not T3) | Done | Done | No SMID route; large R1 text rerun is complete from saved shards with UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy parsed. |
| `Llama-S` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Complete locally across all five papers. |
| `Llama-M` | Done | - | Done | Done | Proxy (not T3) | Done | Done | No SMID route; medium text line completed locally on April 22, 2026. |
| `Llama-L` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | SMID complete; local text rerun is now fully persisted through the Denevil proxy task (100.0%). |
| `Gemma-S` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Frozen Option 1 recovery line. |
| `Gemma-M` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Complete local line across all five papers. |
| `Gemma-L` | Done | Done | Done | Done | Proxy (not T3) | Done | Done | Complete local line across all five papers. |

## Benchmark List

| Benchmark | Paper | Dataset / access | Modality | What this repo tests now |
| --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. (ACL 2025 Findings)](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | Action prediction, moral typology, factor attribution, and consequence generation |
| `SMID` | [Crone et al. (PLOS ONE 2018)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954) | [OSF project page](https://osf.io/ngzwx/) | Vision | Moral rating + foundation classification |
| `Value Kaleidoscope` | [Sorensen et al. (AAAI 2024 / arXiv 2023)](https://arxiv.org/abs/2309.00779) | [Hugging Face dataset card](https://huggingface.co/datasets/allenai/ValuePrism) | Text value reasoning | Relevance + valence |
| `CCD-Bench` | [Rahman and Salam (arXiv 2025)](https://arxiv.org/abs/2510.03553) | [GitHub repo](https://github.com/smartlab-nyu/CCD-Bench); [JSON](https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json) | Text response selection | Selection |
| `Denevil` | [Duan et al. (ICLR 2024 / arXiv 2023)](https://arxiv.org/abs/2310.11053) | No public MoralPrompt export confirmed | Text generation | Proxy generation only |

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
- `family-size-progress.csv`: current published family-size matrix
- `benchmark-comparison.csv`: current comparable accuracy table used for the grouped bar figure
- `ccd-choice-distribution.csv`: CCD-Bench choice-behavior table with per-cluster shares, deviation from the 10% baseline, and concentration summaries
- `denevil-behavior-summary.csv`: DeNEVIL proxy behavioral outcome mix by model line
- `denevil-prompt-family-breakdown.csv`: DeNEVIL protective-response rates by heuristic prompt family
- `denevil-proxy-summary.csv`: appendix QA/provenance table with route, timestamps, sample counts, and visible-response coverage
- `denevil-proxy-examples.csv`: safe qualitative examples showing what the released Denevil proxy traces actually look like
- `deepseek-sm-readout.csv`: explicit DeepSeek-S/M/L log-derived readout from saved logs
- `paper-result-comparison.csv`: exact bridge between original-paper metrics and the closest current release readout
- `paper-model-overlap-map.csv`: explicit map of which paper models match, partially overlap, or remain unrun
- `saved-results-audit.csv`: regenerated audit of local saved `.eval` sources, merge strategy, sample counts, visible-answer coverage, and parsed accuracy where applicable
- `benchmark-difficulty-summary.csv`: benchmark-level means, ranges, and best/worst lines for the comparable slice
- `family-scaling-summary.csv`: cautious scaling notes for each public family
- `benchmark-catalog.csv`: benchmark registry with paper and dataset links
- `model-roster.csv`: exact OpenRouter routes in the frozen Option 1 snapshot; the separate OpenAI reference marker is documented in `benchmark-comparison.csv`
- `supplementary-model-progress.csv`: extra local lines outside the frozen snapshot counts

## Regeneration

From the repo root:

```bash
make release
make audit
```

`make release` rebuilds this public package from the tracked source snapshot. `make audit` runs the public QA gate and rebuilds the package together, but it is not the strict UniMoral completion gate; use `make verify-unimoral` for that. `make unimoral-missing-plan` is the provider-free dry-run preflight for the remaining MiniMax UniMoral cells.

<!-- UNIMORAL_FULL_BENCHMARK_START -->
## UniMoral Full Benchmark Coverage

The release now implements all four UniMoral task definitions and exports scored artifacts where model runs completed, but the current model-line matrix is not yet fully complete. Incomplete or parse-limited cells are listed in `unimoral-failure-checklist.csv`; action prediction remains the legacy comparable scalar and is retained as RQ1.

Metric sanity check: UniMoral has four RQs. Because the frozen RQ1 source exposes only aggregate action accuracy, the main RQ1-RQ3 comparison uses one shared exact-match accuracy metric. In the current strict-complete cells, exact-match accuracy spans RQ2 0.554-0.599 and RQ3 0.561-0.631. RQ4 is a generation task, so it is separated and read with semantic similarity instead of accuracy: BERTScore F1 spans 0.629-0.730, with METEOR 0.077-0.157 as a lexical side metric.

| RQ | Task | Status | Strict complete | Reported cells | Primary metric | Mean | Range | Top line | Diagnostic read |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| RQ1 | Action prediction | complete | 16/16 | 16/16 | accuracy | 0.655 | 0.121 | DeepSeek-M (0.684) | diagnostic |
| RQ2 | Moral typology | incomplete | 15/16 | 16/16 | accuracy | 0.581 | 0.045 | Gemma-S (0.599) | saturated |
| RQ3 | Factor attribution | incomplete | 14/16 | 15/16 | accuracy | 0.592 | 0.070 | Llama-M (0.631) | moderately diagnostic |
| RQ4 | Consequence generation | incomplete | 14/16 | 15/16 | bert_score_f1 | 0.691 | 0.101 | Llama-M (0.730) | diagnostic |

Sample-level predictions for RQ2/RQ3/RQ4 are generated locally as ignored large artifacts; the tracked public package keeps the aggregate summaries in `unimoral-full-benchmark.csv`, `unimoral-coverage.csv`, and `unimoral-completion-audit.md`. Full Inspect `.eval` logs remain under the ignored `results/inspect/logs/2026-05-16-unimoral-full/` run directory.
The provider-free MiniMax handoff is tracked in [`unimoral-minimax-resume-plan.md`](unimoral-minimax-resume-plan.md).
The prompt-to-artifact completion audit, including the verifier-checked CSV-level strict blocker inventory, is tracked in [`unimoral-completion-audit.md`](unimoral-completion-audit.md).

| Task | What it measures | Scoring note |
| --- | --- | --- |
| RQ1 action prediction | Selects the crowd-endorsed action from a two-action dilemma. | Main figure uses exact-match accuracy because the frozen release source exposes only aggregate action accuracy. |
| RQ2 moral typology | Classifies the selected action as deontological, utilitarian, rights-based, or virtuous using `Action_criteria`. | Main figure uses exact-match accuracy for horizontal comparison with RQ1/RQ3. |
| RQ3 factor attribution | Classifies the main contributor to the annotator decision using `Contributing_factors`. | Main figure uses exact-match accuracy for horizontal comparison with RQ1/RQ2. |
| RQ4 consequence generation | Generates likely consequences for the selected action using `Consequence` references. | BERTScore F1 is the semantic-similarity metric; METEOR, BLEU, and ROUGE-L are lexical side metrics. RQ4 is kept separate from classification accuracy charts. |

![UniMoral classification accuracy heatmap](../../../figures/release/option1_unimoral_task_heatmap.svg)

![UniMoral RQ4 generation quality](../../../figures/release/option1_unimoral_generation_quality.svg)

![UniMoral family-size scaling by RQ](../../../figures/release/option1_unimoral_family_scaling.svg)
<!-- UNIMORAL_FULL_BENCHMARK_END -->
