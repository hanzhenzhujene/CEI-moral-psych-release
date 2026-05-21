# Option 1 Release Artifacts

This directory contains the tracked, publication-facing outputs for Jenny Zhu's CEI moral-psych deliverable.

It separates two things clearly:

1. the frozen `Option 1` public snapshot from `April 19, 2026`, and
2. the wider `5 benchmarks x 5 public model families x 3 size slots` status snapshot, with exact status kept in CSV rather than repeated as a large README table.

## TL;DR

If you only read one section, read these key takeaways:

- **Best like-for-like line:** `MiniMax-S` is the strongest fully comparable line, averaging 0.611 across UniMoral 0.661, SMID 0.432, and Value 0.740. This is the cleanest overall topline because all three comparable metrics are observed on the same line.
- **Best text-only line:** `GPT-5.5` is the strongest pure text line, reaching UniMoral 0.684 and Value 0.736. It should not be called the best all-around line because there is no public SMID route on that line.
- **OpenAI text-only Batch references:** 6 Responses/Batch API reference lines are now integrated, each with 76,486/76,486 response rows collected and parser coverage from 76,401 to 76,486 parsed rows. Best OpenAI UniMoral is `GPT-5.5` at 0.684; best OpenAI Value is `GPT-5 mini` at 0.739. SMID and DeNEVIL remain intentionally `n/a` for these text-only references.
- **The hardest benchmark is SMID:** `SMID` has the lowest mean accuracy (0.364) and widest spread (0.285), while `UniMoral` is tightly clustered (0.121 spread). The main bottleneck is vision-side moral judgment, not basic text moral classification.
- **There is no universal scaling law:** `Gemma` is non-monotonic on SMID (0.417 -> 0.364 -> 0.412), and `Llama-M` still beats `Llama-L` on Value (0.724 vs 0.692). Size helps on some tasks, but not in one clean monotonic pattern.
- **CCD-Bench shows cultural choice style, not accuracy.** Every released line with valid CCD choices currently peaks on `option_6 (Nordic Europe)`, but concentration still varies meaningfully, from `DeepSeek-S` at 13.8% to `GPT-5 nano` at 27.8%. The key question is how narrowly each line collapses onto one cultural cluster, not who has the highest "accuracy."
- **DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring.** Among completed lines with usable visible traces, protective/contextual behavior dominates (92.4% to 99.5% protective response rate). `DeepSeek-S` no longer has the old visibility-collapse problem in the May 9 saved rerun (0.2% no-visible proxy traces).
- **Current GitHub-facing boundary:** No MiniMax-M2.5 text benchmark remains live; the saved MiniMax-M2.5 text/proxy pass is already parsed into the public tables and SVGs. SMID remains `TBD`, so the medium MiniMax line is not a fully comparable all-around line yet.


## Benchmark Result Visuals

If you want the five benchmark results before the tables, start here. These five visuals pull the main result surfaces for the full benchmark set to the front of the deliverable.

OpenAI Responses/Batch API text-only reference rows are shown in the comparable-accuracy and CCD figures. They are not treated as family-size scaling series, and they have no SMID or DeNEVIL rows.

### 1. UniMoral / SMID / Value Kaleidoscope: topline comparable accuracy

![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)

_Use this first for the like-for-like result on the three benchmark-faithful accuracy tasks. The SMID panel only includes lines with a public vision route; no-vision text-only rows are removed rather than shown as blanks._

### 2. UniMoral / SMID / Value Kaleidoscope: family-size scaling

![Family scaling profile](../../../figures/release/option1_family_scaling_profile.svg)

_Use this second to compare size effects across the comparable-accuracy layer without mixing in CCD-Bench or DeNEVIL proxy evidence; absent SMID points are route gaps._

### 3. CCD-Bench: cultural-cluster choice behavior

![CCD choice distribution](../../../figures/release/option1_ccd_choice_distribution.svg)

_This is the main CCD-Bench result: deviation from the 10% uniform baseline across the ten canonical cultural clusters._

### 4. CCD-Bench: dominant-option concentration

![CCD dominant-option share](../../../figures/release/option1_ccd_dominant_option_share.svg)

_This is the compact CCD-Bench summary: how much each line collapses onto one dominant cluster, and how broadly it still spreads across the option set._

### 5. DeNEVIL: proxy behavioral outcomes

![DeNEVIL proxy behavioral outcomes](../../../figures/release/option1_denevil_behavior_outcomes.svg)

_This is the main DeNEVIL result surface: auditable behavioral categories from proxy traces, not benchmark-faithful accuracy._

Lower-level QA/provenance figures are still generated in `figures/release/`, but the README keeps the visual story focused on these audience-facing result surfaces.

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
| `Qwen-M` | Complete local line | Done | Earlier text checkpoints withdrawn; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | Clean text rerun finished locally after the withdrawn short-answer artifacts. |
| `Qwen-L` | Complete local line | Done | SMID recovery stands; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy holds a 100.0% persisted checkpoint | SMID recovery complete; clean text rerun finished locally. |
| `Llama-M` | Complete local line | Done | 4 benchmark lines plus `Denevil` proxy; no SMID route | Completed locally on April 22, 2026. |
| `DeepSeek-L` | Complete local line | Done | No SMID route; UniMoral, Value Kaleidoscope, CCD-Bench, and Denevil proxy parsed from saved R1 shards | Large R1 text rerun complete from saved logs; keep it text-only because no SMID route exists. |
| `Llama-L` | Complete local line | Done | SMID complete; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy finished at 100.0%. | SMID complete; local text rerun finished successfully through the Denevil proxy task. |
| `DeepSeek-S` | Complete local line | Done | No SMID route; UniMoral, Value Kaleidoscope, CCD-Bench, and Denevil proxy are complete in the May 9 no-thinking saved logs | May 9 no-thinking rerun passes visible-answer validation; SMID remains unavailable for this DeepSeek size slot. |
| `MiniMax-M` | Complete local text line | Done | Clean MiniMax-M2.5 text/proxy benchmarks complete; no medium SMID route fixed yet. | Clean direct MiniMax-M2.5 text run is complete across UniMoral, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; no medium SMID route fixed yet. Build-time persisted text counts: UniMoral 8,784/8,784; Value 65,520/65,520; CCD 2,182/2,182; Denevil proxy 20,518/20,518. |
| `MiniMax-L` | Complete local line | Done | 5 benchmark lines complete (`Denevil` via proxy) using MiniMax-M2.5 text plus the shared MiniMax-01 SMID recovery route | The direct-provider MiniMax rerun finished successfully through the Denevil proxy task. |
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
| `MiniMax-L` | 0.661 | 0.198 | 0.741 | Comparable on all three benchmark-faithful accuracy panels. |
| `DeepSeek-S` | 0.661 | n/a | 0.695 | Text-only comparable no-thinking rerun; no public SMID route on this slot. |
| `DeepSeek-M` | 0.684 | n/a | 0.635 | Text-only comparable line; no public SMID route on this slot. |
| `DeepSeek-L` | 0.563 | n/a | 0.681 | Text-only comparable line; no public SMID route on this slot. |
| `Llama-S` | 0.648 | 0.216 | 0.529 | Comparable on all three benchmark-faithful accuracy panels. |
| `Llama-M` | 0.670 | n/a | 0.724 | Text-only comparable line; no public SMID route on this slot. |
| `Llama-L` | 0.660 | 0.386 | 0.692 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-S` | 0.635 | 0.417 | 0.593 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-M` | 0.663 | 0.364 | 0.664 | Comparable on all three benchmark-faithful accuracy panels. |
| `Gemma-L` | 0.661 | 0.412 | 0.656 | Comparable on all three benchmark-faithful accuracy panels. |
| `GPT-4o mini` | 0.673 | n/a | 0.701 | GPT-4o mini text reference marker; SMID and DeNEVIL intentionally not run. |
| `GPT-5 nano` | 0.654 | n/a | 0.617 | OpenAI Batch API text-only reference; SMID and DeNEVIL intentionally not run. |
| `GPT-4.1 nano` | 0.646 | n/a | 0.673 | OpenAI Batch API text-only reference; SMID and DeNEVIL intentionally not run. |
| `GPT-5 mini` | 0.678 | n/a | 0.739 | OpenAI Batch API text-only reference; SMID and DeNEVIL intentionally not run. |
| `GPT-4.1 mini` | 0.679 | n/a | 0.735 | OpenAI Batch API text-only reference; SMID and DeNEVIL intentionally not run. |
| `GPT-5.5` | 0.684 | n/a | 0.736 | OpenAI GPT-5.5 text-only reference; SMID and DeNEVIL intentionally not run. |

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
| Strongest fully observed comparable line | `MiniMax-S` averages 0.611 across UniMoral 0.661, SMID 0.432, and Value 0.740. | This is the cleanest like-for-like topline because all three comparable metrics are present on the same line. |
| Strongest text-only comparable line | `GPT-5.5` reaches UniMoral 0.684 and Value 0.736, a two-metric mean of 0.710. | It is the strongest text-only comparison point, but it should not be described as the best all-around line because there is no SMID route on that line. |
| OpenAI text-only reference markers | 6 Batch API rows have 76,486/76,486 collected responses each, with parser coverage from 76,401 to 76,486. Best OpenAI UniMoral: `GPT-5.5` at 0.684; best OpenAI Value: `GPT-5 mini` at 0.739. | These are useful external text-only references, but they are not OpenAI family-size scaling claims and have no SMID / DeNEVIL evidence in this release. |
| Hardest current comparable benchmark | `SMID` has the lowest mean accuracy at 0.364 and the widest spread at 0.285. | The public readout should treat SMID as the highest-variance benchmark rather than expecting simple size-based improvements. |
| Closest thing to saturation | `UniMoral` has the tightest range, from 0.563 to 0.684 (0.121 spread). | Current text lines cluster closely on UniMoral, so additional size mainly fine-tunes rather than reshapes the ranking there. |
| Scaling-law read | `Gemma` is still the only family with a full three-metric S/M/L comparable sweep, while `Qwen`, `DeepSeek`, and `Llama` now add broader text-side size curves. OpenAI Batch rows are external text-only reference markers and are excluded from size-law claims. Even in the cleanest full sweep, the directions diverge: Gemma UniMoral rises from 0.635 to 0.661, Value from 0.593 to 0.656, but SMID is nearly flat overall (0.417 to 0.412). | The data support task-specific scaling, not a single monotonic law across all families and benchmarks. |

### Benchmark Reading Guide

Before comparing charts, anchor each benchmark to its source paper. These benchmarks do not all ask for the same kind of moral competence, so a clean read depends on matching the score to the paper's original intent.

| Benchmark | What the paper is really testing | What this repo currently scores | How to read the current result |
| --- | --- | --- | --- |
| `UniMoral` | A unified multilingual moral-reasoning resource spanning action choice, typology, factor attribution, and consequence generation under culturally varied dilemmas. | The public release currently scores action prediction only: given a dilemma and two candidate actions, select the crowd-endorsed action. | A high UniMoral score means the model tracks consensus action choices across multilingual moral dilemmas. It does not by itself show equal strength on moral typology, factor attribution, or consequence generation. |
| `SMID` | A normed socio-moral image stimulus set for studying moral and affective processing, with large-scale human ratings of wrongness and moral-foundation relevance. | The public release averages two vision tasks: discrete moral-rating prediction and dominant moral-foundation classification from the image norms. | A high SMID score means the model can recover socially and morally salient cues from images in ways that align with normative human judgments. Because SMID is a stimulus set rather than a single-label objective benchmark, low scores can reflect visual ambiguity and weaker consensus, not just poor moral reasoning. |
| `Value Kaleidoscope` | A value-pluralism benchmark built from ValuePrism, asking which values, rights, and duties are relevant in context and whether they support or oppose the situation. | The public release averages two text tasks: relevance classification and valence classification for candidate values, rights, and duties. | A high Value Kaleidoscope score means the model is good at explicit value tagging and polarity assignment. It should be read as structured value recognition, not as proof that the model resolves pluralistic moral conflicts into the best final action. |
| `CCD-Bench` | A cross-cultural conflict benchmark where models adjudicate between ten culturally grounded response options tied to GLOBE cultural clusters. | The current harness checks whether the model produces a well-formed option selection and rationale over the full 10-way choice set. | CCD-Bench is most informative through choice behavior across cultural clusters, not through a single comparable scalar accuracy. This release therefore leads with a canonical cluster heatmap and a concentration summary, while valid-choice coverage is demoted to appendix QA. None of these CCD surfaces should be read as universal accuracy. |
| `Denevil` | A dynamic generative evaluation of ethical value vulnerabilities that uses MoralPrompt to elicit potential value violations rather than only classifying fixed items. | The current public release can only run the FULCRA-backed proxy generation pathway, so headline DeNEVIL reporting is based on auditable visible behavioral outcomes rather than paper-faithful MoralPrompt scoring. | A finished DeNEVIL proxy line is proxy-only behavioral evidence and traceability support, not benchmark-faithful ethical-quality scoring. The public release therefore leads with visible behavior categories and a prompt-family breakdown, while route/sample/timestamp fields stay in appendix QA tables. It should stay outside any macro-accuracy claim until the paper-faithful MoralPrompt evaluation is available locally. |

### Benchmark Difficulty Profile

![Benchmark difficulty profile](../../../figures/release/option1_benchmark_difficulty_profile.svg)

_Figure 3. Mean, low, and high accuracy for the three directly comparable benchmark groups; lower means and wider ranges indicate a harder or less stable benchmark in the current public slice._

| Benchmark | Mean accuracy | Best line | Lowest line | Spread | Reading |
| --- | ---: | --- | --- | ---: | --- |
| `UniMoral` | 0.653 | `DeepSeek-M` (0.684) | `DeepSeek-L` (0.563) | 0.121 | Tightest spread; current lines cluster closely. |
| `SMID` | 0.364 | `Qwen-L` (0.483) | `MiniMax-L` (0.198) | 0.285 | Lowest mean and widest spread in the current comparable slice. |
| `Value Kaleidoscope` | 0.673 | `MiniMax-L` (0.741) | `Llama-S` (0.529) | 0.213 | Mid-range difficulty with meaningful but not extreme variation. |

### Family Scaling Profile

_The headline family-scaling figure already appears above in **Benchmark Result Visuals**. The summary table below keeps the size-by-family takeaways inline here without re-embedding the same chart._

| Family | Evidence scope | Numeric pattern | Cautious interpretation |
| --- | --- | --- | --- |
| `Qwen` | Text benchmarks now have S/M/L comparable points, and SMID has S/L evidence after the recovered large line. | UniMoral: S 0.647 -> M 0.665 -> L 0.665<br/>SMID: S 0.368 -> L 0.483<br/>Value Kaleidoscope: S 0.682 -> M 0.675 -> L 0.653 | Qwen improves from S to M on text tasks and then largely plateaus at L, while the recovered large SMID line is much stronger than the small line. That supports task-specific scaling, not a single monotonic curve. |
| `MiniMax` | 3 comparable metric series available. | UniMoral: S 0.661 -> M 0.659 -> L 0.661<br/>SMID: S 0.432 -> L 0.198<br/>Value Kaleidoscope: S 0.740 -> M 0.740 -> L 0.741 | Current public evidence is too sparse for a stronger within-family scaling claim. |
| `DeepSeek` | The S/M/L text lines are now accuracy-comparable where text-only metrics exist, but no DeepSeek slot has a public SMID route. | UniMoral: S 0.661 -> M 0.684 -> L 0.563<br/>Value Kaleidoscope: S 0.695 -> M 0.635 -> L 0.681 | Read the DeepSeek size curve as text-only evidence: S and L now come from saved shard reruns, M remains the frozen closed-slice line, and all three still omit SMID. |
| `Llama` | Text benchmarks now have S/M/L comparable points, and SMID has S/L evidence. | UniMoral: S 0.648 -> M 0.670 -> L 0.660<br/>SMID: S 0.216 -> L 0.386<br/>Value Kaleidoscope: S 0.529 -> M 0.724 -> L 0.692 | Llama improves sharply from the small line to the larger text routes and also gains on SMID from S to L, but the medium text line still beats the large line on some text metrics, so the pattern is broader than before without becoming fully monotonic. |
| `Gemma` | Full S/M/L comparable sweep on all three comparable benchmarks. | UniMoral: S 0.635 -> M 0.663 -> L 0.661<br/>SMID: S 0.417 -> M 0.364 -> L 0.412<br/>Value Kaleidoscope: S 0.593 -> M 0.664 -> L 0.656 | Best evidence against a single universal scaling law in this repo: text benchmarks improve with size overall, while SMID is non-monotonic. |
| `GPT-4o mini` | Single text-only reference point, not a family-size scaling sweep. | UniMoral: Ref 0.673<br/>Value Kaleidoscope: Ref 0.701 | GPT-4o mini is plotted as a reference marker on UniMoral, Value Kaleidoscope, and CCD-Bench only; it should not be read as evidence about OpenAI family scaling or vision-side SMID performance. |

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
| `MiniMax-M` | option_6 (Nordic Europe) | 18.3% | 9.00 | Compare against the heatmap above, not as scalar accuracy. |
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
| `GPT-4o mini` | option_6 (Nordic Europe) | 17.1% | 8.94 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-5 nano` | option_6 (Nordic Europe) | 27.8% | 6.79 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-4.1 nano` | option_6 (Nordic Europe) | 21.5% | 8.40 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-5 mini` | option_6 (Nordic Europe) | 25.3% | 7.13 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-4.1 mini` | option_6 (Nordic Europe) | 22.4% | 8.07 | Compare against the heatmap above, not as scalar accuracy. |
| `GPT-5.5` | option_6 (Nordic Europe) | 27.3% | 7.06 | Compare against the heatmap above, not as scalar accuracy. |

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
- Read `DeepSeek-S` as a text-only no-SMID line from the May 9 no-thinking saved logs: `CCD-Bench valid-choice coverage = 99.9%`, and `Denevil visible proxy coverage = 99.8%`. These are parser/proxy coverage checks, not CCD or Denevil accuracy.
- Do not call `GPT-5.5` the best overall line across all tasks; its text results are strong, but there is no SMID route on that line.
- Do not claim a universal scaling law from these figures. `Gemma` is the only family with a full three-metric S/M/L sweep, the broader `Qwen` / `DeepSeek` / `Llama` text-side curves still move in mixed directions, and the OpenAI Batch rows are text-only reference markers rather than family-size curves.
- Keep `DeepSeek-S` out of all-around winner claims because it has no SMID route, but keep its validated text metrics in the comparable text rows.
- Treat missing comparable cells as evidence limits rather than model failures. Several large lines are complete operationally but still lack directly comparable public metrics for some benchmarks.

## Snapshot

| Field | Value |
| --- | --- |
| Report owner | `Jenny Zhu` |
| Repo update date | `May 21, 2026` |
| Frozen public snapshot | `Option 1`, `April 19, 2026` |
| Current project total cost | `$759.59 confirmed before May 16 OpenAI Batch additions` |
| Total cost breakdown | MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$254.17`; OpenAI API reference sweep: `$0.76 confirmed before May 16; new OpenAI Batch reference sweeps pending billing confirmation`. |
| Cost scope | User-confirmed total spend before the May 16 OpenAI Batch additions; check the OpenAI billing dashboard before publishing an exact updated dollar total. |
| Intended use | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |
| Current public matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |
| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |
| Model families in scope | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |
| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |
| Extra completed local line outside release | `Llama` small via `llama-3.2-11b-vision-instruct`, complete across `5` papers / `7` tasks |
| Provider / temperature | `OpenRouter`, `temperature=0` |
| Current live reruns | No currently published line is still running locally. |
| Next restart focus | No published rerun is active right now. |
| Release guardrail | Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables. |
| CI workflow | [Workflow](https://github.com/Center-for-Ethical-Intelligence/moral-psychology-benchmark/actions/workflows/ci.yml) |

### Current Operations Highlights

This compact block keeps the live state readable without repeating the full family-size status table in the main README.

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
| `DeepSeek-L R1 text batch` | Done | Saved R1 shards now cover UniMoral, Value Kaleidoscope, CCD-Bench, and Denevil proxy; no SMID route exists. |
| `Llama-L SMID` | Done | The large Llama vision line is complete locally. |
| `Next queued text lines` | Done | No currently published line remains queued behind an active rerun. |

## Start Here

### Reports

- `jenny-group-report.md`: mentor-facing report with the benchmark list, model roster, and current results
- `topline-summary.md`: shortest narrative summary of the frozen Option 1 snapshot
- `release-manifest.json`: machine-readable release index
- [how to read the results](../../../docs/how-to-read-results.md): plain-language explanation of the report terms

### Figures

- [grouped bar chart](../../../figures/release/option1_benchmark_accuracy_bars.svg): current cross-model benchmark comparison
- [benchmark difficulty profile](../../../figures/release/option1_benchmark_difficulty_profile.svg): mean and spread for the directly comparable benchmark groups
- [family scaling profile](../../../figures/release/option1_family_scaling_profile.svg): family-size scaling across the three directly comparable accuracy benchmarks only
- [CCD choice heatmap](../../../figures/release/option1_ccd_choice_distribution.svg): main CCD-Bench result showing deviation from the 10% uniform baseline across the ten canonical clusters
- [CCD concentration summary](../../../figures/release/option1_ccd_dominant_option_share.svg): dominant-cluster share plus effective-cluster count
- [DeNEVIL behavioral outcomes](../../../figures/release/option1_denevil_behavior_outcomes.svg): main proxy-result view showing visible behavior categories by model line

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

Exact per-line family-size status is saved as [family-size-progress.csv](family-size-progress.csv), and public model-line x benchmark result-readiness summary cells are saved as [readiness-tier-matrix.csv](readiness-tier-matrix.csv). Tier 3 means ready for interpretation/comparison within the stated metric layer, not a model-performance score. The summary dashboard reaches Tier 3 only when the required current-release result cells are Tier 3; blocked/not-run/route-gap/data-gap cells are kept outside the tier scale. This README keeps the main surface focused on the visuals and interpretation.

## Benchmark List

| Benchmark | Paper | Dataset / access | Modality | What this repo tests now |
| --- | --- | --- | --- | --- |
| `UniMoral` | [Kumar et al. (ACL 2025 Findings)](https://aclanthology.org/2025.acl-long.294/) | [Hugging Face dataset card](https://huggingface.co/datasets/shivaniku/UniMoral) | Text, multilingual moral reasoning | Action prediction only |
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
- `readiness-tier-matrix.csv`: public summary dashboard for model-line x benchmark result readiness; Tier 1 = harness completed, Tier 2 = valid result, Tier 3 = interpretable/comparable result, with blocked/not-run/route-gap/data-gap cells kept outside the tier scale
- `saved-results-audit.csv`: regenerated audit of local saved `.eval` sources, merge strategy, sample counts, visible-answer coverage, and parsed accuracy where applicable
- `benchmark-difficulty-summary.csv`: benchmark-level means, ranges, and best/worst lines for the comparable slice
- `family-scaling-summary.csv`: cautious scaling notes for each public family
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
