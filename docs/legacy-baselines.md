# Legacy Baselines

This repository contains two evaluation paths:

1. the modern `Inspect AI` moral-psych suite under `src/inspect/`
2. the older `lm-evaluation-harness` ETHICS baseline under `src/lm-evaluation-harness/`

## Why the Legacy Path Still Exists

The original CEI repo started from an ETHICS benchmark wrapper. That code still
matters for regression checks and for readers who want to compare the newer
Inspect-based moral-psych work against the earlier CEI baseline framing.

## What Lives Where

- code: `src/lm-evaluation-harness/`
- example outputs: `results/lm-harness/`
- tests: `tests/test_lm_harness_run.py`, `tests/test_lm_harness_tasks.py`

## Relationship to the Public Release

The closed `2026-04-19 Option 1` release package is built from the Inspect
moral-psych path, not from the legacy lm-evaluation-harness route.

Treat the lm-evaluation-harness code as:

- a legacy baseline implementation
- a useful regression surface
- not the primary public release deliverable for this repo
