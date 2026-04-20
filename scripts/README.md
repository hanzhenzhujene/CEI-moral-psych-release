# Script Index

## Reporting

- `build_authoritative_option1_status.py`: maintainer-only reconciliation step that rebuilds the authoritative `Option 1` status table from raw local run folders.
- `build_release_artifacts.py`: converts the tracked authoritative source snapshot into release-ready CSV, Markdown, JSON, and SVG outputs, including Jenny's benchmark registry, model roster, and future-plan report tables.
- `summarize_inspect_eval_progress.py`: scans `.eval` artifacts and reports live progress from raw Inspect logs.

## Diagnostics

- `check_denevil_dataset.py`: validates whether a local `Denevil` file matches the benchmark-faithful `MoralPrompt` schema or only a proxy-compatible format.

## Formal Run Launchers

- `full_option1_runs.sh`: original `Option 1` launcher for `Qwen`, `DeepSeek`, and `Gemma`.
- `denevil_proxy_formal_runs.sh`: formal proxy launcher for the `FULCRA`-backed `Denevil` path.
- `full_option1_runs_llama_small.sh`: current `Llama 3.2 11B Vision` small-model launcher.
- `full_option1_runs_minimax_small.sh`: current small-model `MiniMax` hybrid launcher.
- `family_size_text_expansion.sh`: sequential fixed-order launcher for the active non-image family-by-size expansion (`Gemma`, `Qwen`, `Llama`, `MiniMax`, plus a `DeepSeek` medium distill line).
- `family_size_image_expansion.sh`: sequential `SMID`-only image expansion launcher for the selected medium / large vision routes.

These launchers are historical and operationally useful, but the public release package should be generated from `build_release_artifacts.py` rather than by reading raw run folders directly.

For portability, the launchers now support:

- `UV_BIN` for non-default `uv` locations
- `DATA_ROOT` for a shared benchmark data root
- benchmark-specific overrides such as `UNIMORAL_DATA_DIR` or `DENEVIL_DATA_FILE`
- `TASK_FILTER` on the Llama small launcher for targeted reruns or recovery batches
