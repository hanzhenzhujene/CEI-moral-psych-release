# Exact UniMoral Same-Model Calibration: Llama 3.1 8B

This directory records the compact local evidence for the July 2026 exact UniMoral calibration pass on `meta-llama/llama-3.1-8b-instruct`.

Why this route was run:

- It is the only exact UniMoral paper-roster model currently available in the checked OpenRouter catalog.
- `Phi-3.5-mini Instruct` and `DeepSeek-R1-Distill-Llama-8B` were not available as exact OpenRouter routes at run time, so they were not substituted.
- The run fills a one-to-one model identity gap for UniMoral RQ1-RQ4, while keeping metric caveats explicit.

Run summary:

| Task | Stage | Samples | Metric | Score | Cost |
| --- | --- | ---: | --- | ---: | ---: |
| `unimoral_action_prediction` | `full` | 8784 | `accuracy` | 0.6219 | `$0.0467` |
| `unimoral_consequence_generation` | `full` | 1782 | `meteor_live` | 0.1212 | `$0.0100` |
| `unimoral_consequence_generation` | `full_offline` | 1782 | `bert_score_f1` | 0.6555 | `$0.0000` |
| `unimoral_factor_attribution` | `full` | 3492 | `accuracy` | 0.5948 | `$0.0241` |
| `unimoral_moral_typology` | `full` | 3492 | `accuracy` | 0.6022 | `$0.0223` |

Totals:

- Full-run completed samples: `17550`
- Full-run actual cost estimate: `$0.1031`
- Smoke-run actual cost estimate: `$0.000024`
- Reasoning tokens: `0` for all rows

Metric boundary:

- RQ1-RQ3 use exact-match accuracy in this repo.
- RQ4 now has both live METEOR and offline BERTScore F1 for this fresh exact run.
- This is exact same-model calibration for model identity, not a claim that the paper's weighted-F1 / METEOR / BERTScore table has been reproduced on the same scoring scale.

Raw Inspect `.eval` archives are kept local for audit. Public-facing docs should cite `calibration-summary.csv` and keep log paths repo-relative.
