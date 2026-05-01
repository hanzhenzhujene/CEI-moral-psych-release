# Script Index

The public release has one canonical reporting path:

- run `make release` to regenerate the tracked deliverable
- run `make bootstrap` to verify the deliverable end to end

Everything below supports that path, but not every script is meant to be a public entrypoint.

## Reporting

- `build_authoritative_option1_status.py`: maintainer-only reconciliation step that rebuilds the frozen `Option 1` status table from raw local run folders.
- `build_release_artifacts.py`: the main public release builder. It converts the tracked frozen source snapshot into release-ready CSV, Markdown, JSON, and SVG outputs, including the README/report surfaces, comparable-accuracy figures, CCD-Bench choice-behavior artifacts, and DeNEVIL proxy evidence package.
- `summarize_inspect_eval_progress.py`: scans `.eval` artifacts and reports live progress from raw Inspect logs.

## Diagnostics

- `check_denevil_dataset.py`: validates whether a local `Denevil` file matches the paper-faithful `MoralPrompt` schema or only a proxy-compatible format.

## Formal Run Launchers

- `full_option1_runs.sh`: original `Option 1` launcher for `Qwen`, `DeepSeek`, and `Gemma`.
- `denevil_proxy_formal_runs.sh`: formal proxy launcher for the current local `Denevil` proxy path.
- `full_option1_runs_llama_small.sh`: current `Llama 3.2 11B Vision` small-model launcher.
- `full_option1_runs_minimax_small.sh`: current small-model `MiniMax` hybrid launcher.
- `family_size_text_expansion.sh`: sequential fixed-order launcher for the active non-image family-by-size expansion (`Gemma`, `Qwen`, `Llama`, `MiniMax`, plus a `DeepSeek` medium distill line).
- `family_size_image_expansion.sh`: sequential `SMID`-only image expansion launcher for the selected medium / large vision routes.
- `qwen_large_smid_recovery.sh`: safer `Qwen-L` `SMID` recovery launcher using `qwen2.5-vl-72b-instruct` plus explicit non-Alibaba provider routing.

These launchers are historical and operationally useful, but the public release package should be generated from `build_release_artifacts.py` rather than by reading raw run folders directly.

## Which scripts matter for which audience

- **Reviewer / collaborator:** usually only needs `make bootstrap` and `build_release_artifacts.py`
- **Contributor rerunning a benchmark:** usually needs one of the launchers plus `src/inspect/run.py`
- **Maintainer reconciling the frozen snapshot:** may need `build_authoritative_option1_status.py`

For portability, the launchers now support:

- `UV_BIN` for non-default `uv` locations
- `DATA_ROOT` for a shared benchmark data root
- benchmark-specific overrides such as `UNIMORAL_DATA_DIR` or `DENEVIL_DATA_FILE`
- `TASK_FILTER` on the Llama small launcher for targeted reruns or recovery batches
