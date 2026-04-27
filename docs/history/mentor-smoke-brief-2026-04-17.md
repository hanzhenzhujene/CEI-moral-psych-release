# Moral-Psych Smoke Batch Brief

Date: April 17, 2026

Prepared for: research mentor update

## Scope

This is a first-round smoke batch for the first four moral-psych benchmarks assigned in the April 14, 2026 meeting notes:

- UniMoral
- SMID
- Value Kaleidoscope
- CCD-Bench

The goal of this smoke batch was not to complete the full benchmark sweep. The goal was to validate end-to-end execution in the CEI Inspect harness, verify local dataset wiring, confirm OpenRouter model connectivity, and collect initial task-level signal before scaling to the full large / medium / small model sweep discussed on April 14, 2026.

## Meeting-Notes Alignment

The smoke batch followed the meeting-notes defaults from April 14, 2026:

- Harness: CEI Inspect
- Temperature: `0`
- Results/logging: Inspect logs written under `results/inspect/logs/`
- Model families targeted for smoke coverage: Qwen, MiniMax, DeepSeek, Gemma

Notes:

- `Colombo` was not available in the live OpenRouter model catalog when checked on April 17, 2026.
- `SMID` is image-based, so it was only run on vision-capable model routes.
- `Denevil` was not part of this smoke batch because the required MoralPrompt dataset is still missing locally.

## Smoke Configuration

To keep the smoke batch stable and mentor-readable, I used representative task-level coverage rather than every subtask in every file:

- `UniMoral`: `unimoral_action_prediction`
  - `UNIMORAL_LANGUAGE=English`
  - `UNIMORAL_MODE=np`
  - `limit=2`
- `Value Kaleidoscope`
  - `value_prism_relevance`
  - `value_prism_valence`
  - `limit=2`
- `CCD-Bench`
  - `ccd_bench_selection`
  - `limit=2`
- `SMID`
  - `smid_moral_rating`
  - `smid_foundation_classification`
  - `limit=2`

This was intentionally smaller than a full run. It is best interpreted as a readiness + sanity-check batch.

## Model Routes Used

Verified against the live OpenRouter model catalog on April 17, 2026:

- Qwen text: `openrouter/qwen/qwen3-8b`
- Qwen vision: `openrouter/qwen/qwen3-vl-8b-instruct`
- MiniMax text: `openrouter/minimax/minimax-m2.5:free`
- DeepSeek text: `openrouter/deepseek/deepseek-chat-v3.1`
- Gemma text/vision: `openrouter/google/gemma-3-4b-it:free`

## Results

### Completed Task-Level Smoke Results

| Family | Benchmark | Task | Metric | Value | Stderr | Status |
| --- | --- | --- | --- | ---: | ---: | --- |
| Qwen | UniMoral | `unimoral_action_prediction` | accuracy | 1.0 | 0.0 | completed |
| Qwen | Value Kaleidoscope | `value_prism_relevance` | accuracy | 0.5 | 0.5 | completed |
| Qwen | Value Kaleidoscope | `value_prism_valence` | accuracy | 1.0 | 0.0 | completed |
| Qwen | CCD-Bench | `ccd_bench_selection` | valid choice mean | 1.0 | 0.0 | completed |
| DeepSeek | UniMoral | `unimoral_action_prediction` | accuracy | 0.0 | 0.0 | completed |
| DeepSeek | Value Kaleidoscope | `value_prism_relevance` | accuracy | 0.0 | 0.0 | completed |
| DeepSeek | Value Kaleidoscope | `value_prism_valence` | accuracy | 0.5 | 0.5 | completed |
| DeepSeek | CCD-Bench | `ccd_bench_selection` | valid choice mean | 1.0 | 0.0 | completed |
| Gemma | UniMoral | `unimoral_action_prediction` | accuracy | 0.0 | 0.0 | completed |
| Gemma | Value Kaleidoscope | `value_prism_relevance` | accuracy | 0.5 | 0.5 | completed |
| Gemma | Value Kaleidoscope | `value_prism_valence` | accuracy | 0.5 | 0.5 | completed |
| Gemma | CCD-Bench | `ccd_bench_selection` | valid choice mean | 1.0 | 0.0 | completed |
| Qwen | SMID | `smid_moral_rating` | accuracy | 0.0 | 0.0 | completed |
| Qwen | SMID | `smid_foundation_classification` | accuracy | 0.5 | 0.5 | completed |
| Gemma | SMID | `smid_moral_rating` | accuracy | 0.5 | 0.5 | completed |
| Gemma | SMID | `smid_foundation_classification` | accuracy | 0.5 | 0.5 | completed |

### Blockers Observed During Smoke

- MiniMax
  - `openrouter/minimax/minimax-m2.5:free` timed out on `unimoral_action_prediction` during smoke.
  - The attempt produced an incomplete `.eval` artifact rather than a completed log.
  - I did not continue the rest of the MiniMax smoke matrix after that first timeout, because the issue appeared to be provider / queue instability rather than a harness bug.
- Colombo
  - No `colombo` family match was found in the live OpenRouter catalog checked on April 17, 2026.
- UniMoral full-task bundle
  - Running the entire `unimoral.py` file in one shot was less stable than running representative tasks individually.
  - For smoke purposes, task-level targeting was more reliable.

## Interpretation

What this smoke batch demonstrates:

- The CEI Inspect path is now operational for the first four moral-psych benchmarks.
- Local dataset setup is working for UniMoral, SMID, Value Kaleidoscope, and CCD-Bench.
- OpenRouter execution is confirmed for Qwen, DeepSeek, Gemma, and Qwen vision.
- The current harness can produce task-level logs, metrics, and sample traces suitable for later audit.

What this smoke batch does not demonstrate:

- It is not a statistically meaningful benchmark comparison.
- It does not replace the full large / medium / small family sweep requested in the April 14, 2026 meeting notes.
- It does not yet include Denevil.

## Artifacts

Primary summary artifact:

- `results/inspect/smoke-batch/2026-04-17-mentor-smoke-summary.csv`

Detailed run directories:

- `results/inspect/smoke-batch/2026-04-17-mentor-smoke-batch-v2`
- `results/inspect/smoke-batch/2026-04-17-mentor-smoke-batch-v3`

Inspect log directories:

- `results/inspect/logs/2026-04-17-mentor-smoke-batch-v2`
- `results/inspect/logs/2026-04-17-mentor-smoke-batch-v3`

## Repo / Validation Status

- Local test suite after the harness updates: `32 passed`

## Recommended Next Steps

1. Run the same representative smoke tasks on a non-free MiniMax route or at a lower-load time window to separate provider instability from model behavior.
2. Choose the exact large / medium / small variants for each live family and launch the full sweep with `temperature=0`.
3. Decide whether the full UniMoral run should include all subtasks or begin with action prediction first.
4. Resolve the missing MoralPrompt / Denevil dataset before expanding to the fifth benchmark.
