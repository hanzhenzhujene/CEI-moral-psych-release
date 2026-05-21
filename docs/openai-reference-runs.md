# OpenAI Reference Runs

This note documents the completed OpenAI text-reference rows and the promoted GPT-5.5 text-only follow-up.

## Completed Reference Rows

The current release builder includes six completed text-only OpenAI reference rows in `benchmark-comparison.csv`, `ccd-choice-distribution.csv`, and the generated `readiness-tier-matrix.csv` summary:

- `GPT-4o mini`
- `GPT-5 nano`
- `GPT-4.1 nano`
- `GPT-5 mini`
- `GPT-4.1 mini`
- `GPT-5.5`

Each completed full text sweep covers 76,486 selected examples across UniMoral action prediction, ValuePrism relevance, ValuePrism valence, and CCD-Bench selection. The release now labels the GPT-5 subset as a text-only S/M/L reference series: `GPT-5 nano` is S, `GPT-5 mini` is M, and `GPT-5.5` is L. These rows intentionally omit SMID and DeNEVIL, so the GPT-5 S/M/L read is text-only size context rather than all-benchmark OpenAI coverage.

## GPT-5.5 Promotion Status

As of May 21, 2026, official OpenAI documentation identifies GPT-5.5 as the current latest model for the latest-model endpoint guidance. The repo-local GPT-5.5 work used the same OpenAI text harness path as the completed reference rows:

- `openai_smoke_benchmark.py`
- `/v1/responses`
- Batch API request preparation
- eligible text-only tasks only

The existing harness sent `reasoning.effort: minimal` for `gpt-5*` routes, but GPT-5.5 rejected that value. A runtime compatibility wrapper mapped the lightweight setting to `reasoning.effort: none`; the 4-sample gate then passed with 4/4 parsed project rows.

The full GPT-5.5 text batch was prepared at workspace-level `outputs/openai-smoke/full-gpt-5-5-text-none-20260521-005408-subagent-b/` with 76,486 requests. It is now promoted through `scripts/build_release_artifacts.py` as a completed text-only OpenAI reference row:

- chunk 01 failed with `token_limit_exceeded` against the GPT-5.5 enqueued-token limit
- chunk 02 completed and was collected: 8,000/8,000 rows parsed successfully
- smaller retry chunks were prepared for the 68,486 rows not covered by completed chunk 02, using 1,000 requests per chunk
- retry chunks 001-069 completed and were collected: 68,486/68,486 rows parsed successfully
- retry chunk 004 was initially blocked by `billing_hard_limit_reached`; after the billing issue was cleared, the same non-overlapping row range was submitted and collected successfully
- final `predictions.jsonl` and `project_results.jsonl` files each contain 76,486 rows

Local integrity checks on May 21, 2026 found 76,486 unique sample ids, zero JSON parse errors, and 76,486 successful `project_results.jsonl` rows. Task counts match the expected text-only sweep: 8,784 UniMoral action-prediction rows, 43,680 ValuePrism relevance rows, 21,840 ValuePrism valence rows, and 2,182 CCD-Bench selection rows. The manifest still records the original oversized chunk 01 as a failed submission attempt, but all retry chunks needed for the final artifact completed with zero failed requests.

The promoted GPT-5.5 row is scoped exactly like the other OpenAI text references: it has UniMoral, ValuePrism, and CCD-Bench text-only evidence; it has no SMID row and no DeNEVIL row. In the public family-scaling figure it is the OpenAI GPT-5 text-only L slot, paired with `GPT-5 nano` as S and `GPT-5 mini` as M; this should not be described as all-benchmark OpenAI family coverage.

Reference: [OpenAI latest model guide](https://developers.openai.com/api/docs/guides/latest-model).
