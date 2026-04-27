# Denevil Proxy Run Note

Prepared: April 18, 2026
Prepared for: research mentor update

## Summary

The original `Denevil` benchmark path in the CEI harness remains blocked by the absence of a public, benchmark-faithful `MoralPrompt` export.

To avoid leaving the fifth benchmark line empty, I launched a clearly labeled proxy batch using the locally available `FULCRA` dialogue dataset under `data/denevil/`.

This proxy batch should be interpreted as:

- a harness-complete fallback for the fifth benchmark slot
- useful for generation behavior comparison across models
- not a paper-faithful replacement for the original `MoralPrompt` benchmark

## Why The Original Path Is Still Blocked

The benchmark-faithful task `denevil_generation` expects a local `MoralPrompt` export with a prompt-like field such as `prompt`, `instruction`, `question`, or `text`.

The local `data/denevil/data_hybrid.jsonl` file is not that format. It is a `FULCRA` dialogue dataset with fields such as:

- `dialogue`
- `query_source`
- `response_source`
- `value_items`
- `value_types`

The public project materials I could verify expose `FULCRA`, but not a stable public download of the `MoralPrompt` dataset used in the DeNEVIL paper.

## What We Did Instead

I added an explicit proxy task:

- `src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation`

This task:

- reads the local `FULCRA` dialogue rows
- extracts the `Human:` side of the dialogue as the prompt
- runs the same response-generation harness flow
- preserves the original `FULCRA` metadata in the sample record

This keeps the benchmark limitation explicit while still letting us run a formal, reproducible batch for the fifth line.

## Formal Proxy Batch

Run namespace:

- `2026-04-18-denevil-fulcra-proxy-formal-v3`

Families launched:

- `qwen_proxy`
  - model: `openrouter/qwen/qwen3-8b`
- `deepseek_proxy`
  - model: `openrouter/deepseek/deepseek-chat-v3.1`
- `gemma_proxy`
  - model: `openrouter/google/gemma-3-4b-it`

Data file:

- `/absolute/path/to/data_hybrid.jsonl`

Task:

- `denevil_fulcra_proxy_generation`

## How To Interpret These Results

Appropriate interpretation:

- this fills the missing fifth benchmark line operationally
- this is suitable for internal progress tracking and model-behavior comparison
- this should be reported as a `FULCRA-backed Denevil proxy`, not as the original `MoralPrompt` benchmark

Inappropriate interpretation:

- do not claim this is the exact published `Denevil / MoralPrompt` evaluation setup
- do not compare these results one-to-one with paper numbers as if the underlying dataset were identical

## Supporting Artifacts

Proxy validator / rationale:

- `results/inspect/full-runs/2026-04-17-option1-full-funded/denevil-dataset-check.txt`

Proxy smoke validation log:

- `results/inspect/logs/debug-denevil-fulcra-proxy/`

Formal proxy run outputs:

- `results/inspect/full-runs/2026-04-18-denevil-fulcra-proxy-formal-v3/`
- `results/inspect/logs/2026-04-18-denevil-fulcra-proxy-formal-v3/`

Current progress snapshot for the formal proxy batch:

- `results/inspect/full-runs/2026-04-18-denevil-fulcra-proxy-formal-v3/progress-summary.csv`
- `results/inspect/full-runs/2026-04-18-denevil-fulcra-proxy-formal-v3/progress-summary.md`
