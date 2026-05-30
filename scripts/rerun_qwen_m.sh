#!/usr/bin/env bash
# Re-run Qwen3-32B (Qwen-M) WITHOUT enable_thinking=false.
#
# Context: The original runs used enable_thinking=false via DashScope, which caused
# ultra-short outputs (~3 tokens/sample) on Qwen3-32B. This re-run omits that flag
# so the model generates full responses. The scorers already have strip_think_blocks()
# from PR #23, so any <think> blocks will be handled correctly.
#
# Affected T1 cells (8+):
#   - MoralBench: mfq_agreement, vignette_agreement, mfq_compare, vignette_compare
#   - MoralLens: cot, posthoc, double_standard
#   - MoReBench: advisor, agent
#   - Moral Circuits: judgment, reasoning
#
# Usage:
#   bash scripts/rerun_qwen_m.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/src/inspect/run.py"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"

cd "$ROOT"

# Load env
set -a; source "$ROOT/.env" 2>/dev/null || true; source "$ROOT/.env.local" 2>/dev/null || true; set +a

# Provider: DashScope (same as before, but WITHOUT enable_thinking=false)
export OPENAI_API_KEY="${DASHSCOPE_API_KEY:?DASHSCOPE_API_KEY not set}"
export OPENAI_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
MODEL="openai/qwen3-32b"

# Data directories
export MORALBENCH_DATA_DIR="${MORALBENCH_DATA_DIR:-$DATA_ROOT/moralbench}"
export MORALLENS_DATA_DIR="${MORALLENS_DATA_DIR:-$DATA_ROOT/morallens}"
export MOREBENCH_DATA_DIR="${MOREBENCH_DATA_DIR:-$DATA_ROOT/morebench}"
export MORAL_CIRCUITS_DATA_DIR="${MORAL_CIRCUITS_DATA_DIR:-$DATA_ROOT/moral_circuits}"

MAX_CONN=20
RUN_ID="2026-05-19-qwen-m-rerun"
LOG_DIR="$ROOT/results/inspect/logs/$RUN_ID"
mkdir -p "$LOG_DIR"

# Resolve runner
if command -v uv >/dev/null 2>&1; then
  RUN_PREFIX=(uv run --package cei-inspect python)
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  RUN_PREFIX=("$ROOT/.venv/bin/python")
else
  echo "No uv or .venv/bin/python found" >&2; exit 1
fi

run_task() {
    local task_spec="$1"
    local task_name="$2"
    local log_file="$LOG_DIR/${task_name}.log"

    echo "=== $task_name started: $(date) ==="
    if "${RUN_PREFIX[@]}" "$RUNNER" \
        --tasks "$task_spec" \
        --model "$MODEL" \
        --no_sandbox \
        --max_connections "$MAX_CONN" \
        --log_dir "$LOG_DIR" \
        2>&1 | tee "$log_file"; then
        echo "=== $task_name DONE: $(date) ==="
    else
        echo "=== $task_name FAILED: $(date) ==="
    fi
    echo ""
}

echo "=========================================="
echo " Qwen-M (Qwen3-32B) Re-run"
echo " WITHOUT enable_thinking=false"
echo " Started: $(date)"
echo "=========================================="
echo ""

# MoralBench (4 tasks)
run_task "evals/moralbench.py::moralbench_mfq_agreement" "moralbench_mfq_agreement"
run_task "evals/moralbench.py::moralbench_vignette_agreement" "moralbench_vignette_agreement"
run_task "evals/moralbench.py::moralbench_mfq_compare" "moralbench_mfq_compare"
run_task "evals/moralbench.py::moralbench_vignette_compare" "moralbench_vignette_compare"

# MoralLens (3 tasks)
run_task "evals/morallens.py::morallens_cot" "morallens_cot"
run_task "evals/morallens.py::morallens_posthoc" "morallens_posthoc"
run_task "evals/morallens.py::morallens_double_standard" "morallens_double_standard"

# MoReBench (2 tasks)
run_task "evals/morebench.py::morebench_advisor" "morebench_advisor"
run_task "evals/morebench.py::morebench_agent" "morebench_agent"

# Moral Circuits (2 tasks)
run_task "evals/moral_circuits.py::moral_circuits_judgment" "moral_circuits_judgment"
run_task "evals/moral_circuits.py::moral_circuits_reasoning" "moral_circuits_reasoning"

echo "=========================================="
echo " Qwen-M re-run complete: $(date)"
echo " Logs: $LOG_DIR"
echo "=========================================="
