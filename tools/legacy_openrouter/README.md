# Legacy OpenRouter Tools

This folder contains the older standalone OpenRouter runner utilities that used to live in the repository root:

- `run_benchmark.py`: single-turn JSONL prompt runner
- `run_trolleybench.py`: multi-turn TrolleyBench runner
- `eval_trolleybench.py`: TrolleyBench scoring helper
- `export_results.py`: TrolleyBench export helper
- `client.py` / `config.py`: shared OpenRouter client and model map for these legacy tools

The current public moral-psych release uses the Inspect AI harness under `src/inspect/` plus `scripts/build_release_artifacts.py`. Keep these tools for historical continuity and Joseph-side TrolleyBench experiments, but do not treat them as the canonical Jenny release path.
