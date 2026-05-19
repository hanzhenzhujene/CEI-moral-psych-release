# Legacy OpenRouter Launchers

This folder keeps older one-off OpenRouter / direct-provider launchers out of the repository root.

These scripts are retained for provenance and maintainer recovery work. They are not the canonical public release path. For the public deliverable, prefer:

```bash
make bootstrap
make release
```

The scripts resolve the repository root relative to this folder, so they should still be run from the repo root as:

```bash
scripts/legacy-openrouter/run_all_benchmarks.sh --limit 10
```
