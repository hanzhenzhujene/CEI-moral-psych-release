# Contributing

This repository mixes benchmark code, local run provenance, and a curated public
release package. The fastest way to keep contributions clean is to treat those
three layers differently.

## Setup

```bash
make setup
cp .env.example .env
```

If `uv` is installed outside your shell `PATH`, use:

```bash
make UV=/absolute/path/to/uv test
```

If `uv` is not on `PATH` but the repo `.venv` already exists, `make test`,
`make release`, `make refresh-authoritative`, `make smoke`, and `make audit`
fall back to `.venv/bin/python` automatically. `make setup` still requires
`uv`. If the fallback interpreter lives elsewhere, pass
`VENV_PYTHON=/absolute/path/to/python`.

## Before Opening a PR

Run:

```bash
make audit
```

That is equivalent to running `make test` followed by `make release`, and it is
the fastest public QA gate to use before a PR.

Use `make refresh-authoritative` only if you have the original local raw
`results/inspect/full-runs/` directories and intend to update the tracked
authoritative snapshot.

## Repository Conventions

- Put benchmark implementations under `src/inspect/evals/`
- Keep public-facing instructions in `README.md` and `docs/`
- Keep raw local run logs under `results/inspect/`; do not rely on them for public reproduction
- Keep the tracked release package under `results/release/2026-04-19-option1/`
- Preserve the distinction between benchmark-faithful and proxy evaluations in names, tables, and figures

## Data and Secrets

- Never commit `.env`
- Never hard-code private dataset paths in committed Python modules or docs
- Use `.env.example` to document new env vars

## Release-Facing Changes

If you change benchmark scope, task naming, or authoritative counts, also update:

- `README.md`
- `docs/reproducibility.md`
- `results/release/2026-04-19-option1/README.md`
- generated release tables and figures via `make release`
