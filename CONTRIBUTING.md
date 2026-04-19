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

## Before Opening a PR

Run:

```bash
make test
make release
```

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
