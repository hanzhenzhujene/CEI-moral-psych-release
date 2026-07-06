# Evaluation Methodology

This page is the shortest rigorous explanation of what this repo measures, what is directly comparable, and what should **not** be over-claimed from the current release.

Current public metric definition version: `2026-04-30`.

This version locks in the stricter visible-answer parsing rules described below, so later parser or scorer changes must show up as an explicit version bump rather than a silent metric rewrite.

## Result-Readiness Tiers

The release exports a generated result-readiness summary dashboard at `results/release/2026-04-19-option1/readiness-tier-matrix.csv`.

- `Tier 1`: the harness completed for the result cell.
- `Tier 2`: the result is valid.
- `Tier 3`: the result is interpretable and ready for comparison within the stated metric layer.

Missing evidence is not a tier. Route gaps, data gaps, not-run cells, and blocked cells are represented separately as blocker/status values.

The canonical Tier unit is a result cell:

`model_id / provider_route / size_slot x benchmark x subtask_or_RQ x metric_layer x sample_set`

The public `readiness-tier-matrix.csv` is a summary view at `model_line x benchmark`. It carries lower-level fields where the release builder can infer them, plus a `lower_level_limitations` field where the public row is only a summary of text/vision routes or source artifacts. It is not the canonical low-level ledger. If a benchmark summary uses multiple required subtasks, the summary reaches Tier 3 only when all required current-release cells are Tier 3; blocked cells receive no Tier. If the release intentionally exposes only one metric layer for a benchmark, the summary applies only to that metric layer.

Tier is about result readiness. It is not model performance, not a family-level label, and not a claim that a Tier 3 model is "better" than another model. The metric layers below answer "what kind of evidence is this?"

## Metric Layers

This repo currently exposes three different kinds of result:

1. `Benchmark-faithful accuracy / classification / generation metrics`
   - Used for: `UniMoral`, `SMID`, `Value Kaleidoscope`
   - Interpretation: the model produced a benchmark answer that can be scored against a benchmark target.
   - Safe comparisons: across models within the same benchmark, and cautiously across families when the same route type exists.

2. `Choice-distribution behavior`
   - Used for: `CCD-Bench` in the public release
   - Current definition: distribution over the paper's ten canonical cultural-cluster options, plus dominant-option share and effective cluster count.
   - Interpretation: the model surfaced a parseable visible choice, then showed a measurable cultural-choice pattern over the ten options.
   - Not the same as: cultural-choice quality, rationale quality, or benchmark accuracy.
   - QA gate: valid-choice coverage is still exported, but it is a parser/coverage check rather than the headline CCD metric.

3. `Proxy behavior`
   - Used for: `Denevil` in the public release
   - Current definition: line-level mix of protective refusals, redirects, corrective/contextual responses, direct answers, risky continuations, ambiguous answers, and empty visible traces.
   - Interpretation: the model returned auditable behavior on released FULCRA-backed proxy prompts.
   - Not the same as: paper-faithful `MoralPrompt` performance or ethical-quality scoring.
   - QA/provenance fields: sample volume, visible generated-response count, visible-response rate, best persisted checkpoint percentage, proxy route metadata, timestamps, and safe examples remain exported, but DeNEVIL does not receive Tier 3 paper-faithful readiness in this release.

## Output Parsing Controls

The current code deliberately uses stricter answer extraction than earlier iterations of this repo.

- `UniMoral` action prediction now looks for an explicit `a` / `b` choice instead of matching any stray article-like token.
- `UniMoral` moral typology and factor attribution use label-membership parsing against the official RQ2/RQ3 label sets and report exact-match accuracy as the primary release metric.
- `UniMoral` consequence generation extracts the explicit generated consequence and reports two generation metrics: BERTScore F1 for semantic similarity and METEOR for lexical overlap.
- `Value Kaleidoscope` now resolves `not relevant` before `relevant`, and `Either` before `Supports` / `Opposes`, so overlapping phrases do not get misclassified by regex order.
- `CCD-Bench` coverage now expects a structured visible `1-10` choice rather than blindly trusting the first integer mentioned anywhere in the completion.
- `SMID` moral rating now expects a bounded visible integer rather than any incidental digit captured by a loose regex.

These controls matter because many modern provider routes emit hidden reasoning plus a short visible answer. Public comparisons in this repo are based on the **saved visible answer**, not on hidden reasoning traces.

## Comparison Rules

Use these rules when writing claims from the current release:

- Compare legacy `UniMoral` action prediction, `SMID`, and `Value Kaleidoscope` as accuracy-style benchmark results.
- Read the expanded `UniMoral` RQ2/RQ3/RQ4 artifacts separately: RQ2/RQ3 are classification tasks scored by exact-match accuracy, and RQ4 is a generation task scored with BERTScore F1 plus METEOR.
- Treat `CCD-Bench` as two separate public surfaces: valid-choice coverage, then choice-distribution / dominant-option concentration among valid visible selections. Do not collapse those into a scalar accuracy claim.
- Treat `Denevil` as proxy-only coverage and traceability evidence unless and until the repo exposes a paper-aligned comparable scalar for it.
- Do not fold `Denevil` into any macro-accuracy average.
- Do not promote a text-only line into an all-around winner without a matching `SMID` route.
- Treat withheld cells as evidence limits, not model failures.

## Failure Modes The Repo Explicitly Guards Against

- `Empty visible answers`: a run can consume tokens and even emit hidden reasoning while still failing to place a usable answer in the saved visible output field.
- `Reasoning-only traces`: hidden reasoning is not treated as a valid public answer.
- `Route mismatch`: some provider routes are text-only, some are vision-capable, and some have no stable public route for a benchmark-size slot.
- `Proxy drift`: `Denevil` is still a proxy path in this repo, so completion there cannot be interpreted as benchmark-faithful ethical robustness.
- `Mixed UniMoral task types`: the legacy `UniMoral` scalar in older tables is RQ1/action prediction only. The full UniMoral package has separate RQ1/RQ2/RQ3/RQ4 artifacts and a failure checklist for any provider cells that are incomplete or parse-limited.

## How To Read DeepSeek-M

`DeepSeek-M` is the clearest example of why these controls exist.

- Its top-row text metrics are withheld because the saved short-answer artifacts collapse into empty visible answers.
- Its `CCD-Bench` bottom-row value should be read as a **formatting / answer-surfacing failure**, not as proof that the model selected the wrong cultural option on every prompt.
- Its `Denevil` bottom-row value should be read as **visible-response coverage**, not as paper-faithful ethical scoring.

## What Would Make The Design Stronger

The current repo is careful about not overclaiming, but the next rigorous upgrades are still clear:

- add a paper-aligned `CCD-Bench` choice-quality metric instead of relying on coverage alone
- obtain a paper-faithful local `MoralPrompt` export for `Denevil`
- lock more provider routes so each family-size cell has a stable rerunnable configuration
- keep bumping the public metric-definition version whenever a parser or scorer changes materially

Until those upgrades land, the safest public stance is: accuracy claims live on the top row, coverage claims live on the bottom row, and the two should not be merged into a single scalar story.

## UniMoral RQ4 Note

The current UniMoral release table is no longer an RQ1-only surface. `results/release/2026-04-19-option1/unimoral-full-benchmark.csv` reports RQ1-RQ4 separately: RQ1-RQ3 use exact-match accuracy, and RQ4 consequence generation appears as two presentation rows per model line, `bert_score_f1` and `meteor`.

The reference UniMoral RQ4 consequence-generation script reports BLEU, METEOR, and BERTScore F1. In `references/UniMoral/RQ4.py`, METEOR and BERTScore F1 are computed against each available human-written consequence for the same sample, the best reference score is kept, and those best per-sample scores are averaged.

METEOR is mostly lexical: it rewards overlapping or closely related words between the generated consequence and the reference. BERTScore F1 is embedding-based: it compares contextual Transformer token embeddings, so it can reward paraphrases that use different wording. With the local `bert-score` defaults, English uses `roberta-large`, Chinese uses `bert-base-chinese`, and Spanish/Arabic/Russian/Hindi fall back to `bert-base-multilingual-cased`.

The release CSV also retains BLEU and ROUGE-L diagnostic columns for RQ4, but the public README and main RQ4 figure use BERTScore F1 plus METEOR as the two headline generation metrics. Do not compare RQ4 magnitudes directly with RQ1-RQ3 accuracy, and do not collapse RQ1-RQ4 into one universal moral score.
