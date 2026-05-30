#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${OPENROUTER_PYTHON:-${VENV_PYTHON:-python}}"
OUTPUT_DIR="${OPENROUTER_FULL_OUTPUT_DIR:-results/openrouter-low-cost-moral-psych-full}"
MAX_TOTAL_ESTIMATED_COST="${OPENROUTER_MAX_TOTAL_ESTIMATED_COST:-60}"
MAX_CONNECTIONS="${OPENROUTER_MAX_CONNECTIONS:-1}"

RUN_CMD=(
  "$PYTHON_BIN"
  scripts/openrouter_low_cost_moral_psych.py
  run
  --full
  --output-dir
  "$OUTPUT_DIR"
  --max-connections
  "$MAX_CONNECTIONS"
  --max-total-estimated-cost
  "$MAX_TOTAL_ESTIMATED_COST"
  --yes
)

SUMMARY_CMD=(
  "$PYTHON_BIN"
  scripts/openrouter_low_cost_moral_psych.py
  summarize
  --full
  --output-dir
  "$OUTPUT_DIR"
)

echo "OpenRouter low-cost full selected-grid run"
echo "  output_dir=$OUTPUT_DIR"
echo "  max_total_estimated_cost=$MAX_TOTAL_ESTIMATED_COST"
echo "  max_connections=$MAX_CONNECTIONS"
echo
printf 'Run command:'
printf ' %q' "${RUN_CMD[@]}"
printf '\n'
printf 'Summarize command:'
printf ' %q' "${SUMMARY_CMD[@]}"
printf '\n'

if [[ "${OPENROUTER_FULL_RUN_DRY_RUN:-0}" == "1" ]]; then
  echo "Dry run only; no provider calls were made."
  exit 0
fi

if [[ "${OPENROUTER_FULL_RUN_APPROVED:-0}" != "1" ]]; then
  cat >&2 <<EOF
Refusing to start cost-bearing OpenRouter calls.

Set OPENROUTER_FULL_RUN_APPROVED=1 only after approving the full selected-grid spend.
Current default guard: OPENROUTER_MAX_TOTAL_ESTIMATED_COST=$MAX_TOTAL_ESTIMATED_COST.

No provider calls were made.
EOF
  exit 2
fi

"${RUN_CMD[@]}"
"${SUMMARY_CMD[@]}"
