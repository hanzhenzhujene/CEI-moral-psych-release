# Repo Architecture

This repo is easiest to trust when you read it as **three layers with different evidence guarantees**.

## 1. Frozen Public Release Layer

These are the files a reviewer can treat as the stable public deliverable:

- `README.md`
- `results/release/2026-04-19-option1/`
- `figures/release/`
- `docs/`

This layer is designed to be:

- version-controlled
- rebuildable from committed inputs
- readable without local benchmark data

If you only want to verify that the public package is internally consistent, run:

```bash
make bootstrap
```

That one command installs the pinned environment, runs the tests, and rebuilds the public release package.

## 2. Tracked Release Source Layer

The committed regeneration anchor is:

- `results/release/2026-04-19-option1/source/authoritative-summary.csv`

This file is the source of truth for `make release`. It exists so the public package can be regenerated in CI and by external readers **without** the original local run folders.

The main builder is:

- `scripts/build_release_artifacts.py`

That script turns the authoritative snapshot into:

- release README and report markdown
- benchmark and model CSV tables
- machine-readable manifest JSON
- publication-facing SVG figures

## 3. Local Raw Run Layer

These directories are operational rather than publication-facing:

- `results/inspect/logs/`
- `results/inspect/full-runs/`
- `results/inspect/smoke-batch/`

They may contain richer or newer local evidence, but they are intentionally treated as **ephemeral local provenance**, not as the public reproduction boundary.

That distinction matters because some local rerun evidence is trustworthy enough to inform the curated release, while some local artifacts are withheld from public comparison charts after validation.

## Execution Paths

### Public verification

Use this when you want a clean-checkout QA pass:

```bash
make bootstrap
```

### Public artifact regeneration only

Use this when the environment is already set up and you only want to rebuild the publication package:

```bash
make release
```

### Live harness smoke test

Use this only when you have secrets and local benchmark data:

```bash
make setup
cp .env.example .env
make smoke
```

### Maintainer-only authoritative refresh

Use this only if you still have the raw full-run folders referenced by the historical sweep:

```bash
make refresh-authoritative
make release
```

## Code Layout

- `src/inspect/`: Inspect AI harness entrypoints plus benchmark task builders
- `src/lm-evaluation-harness/`: retained ETHICS baseline path
- `scripts/`: operational launchers, recovery helpers, and release builders
- `tests/`: regression checks for harness tasks, release artifacts, Makefile behavior, and repo hygiene

## What Is Intentionally Not Claimed

- `Denevil` is not treated as a benchmark-faithful scalar accuracy result in the public package.
- `DeepSeek-M` is not forced into comparable accuracy charts when its saved short-answer rerun artifacts fail validation.
- The broader local family-size sweep is not silently folded into the frozen `Option 1` snapshot.

Those guardrails are part of the deliverable, not exceptions to it.
