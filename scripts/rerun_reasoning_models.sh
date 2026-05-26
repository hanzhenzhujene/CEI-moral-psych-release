#!/usr/bin/env bash
# Re-run reasoning models on tasks affected by <think> block contamination.
#
# Context: PR #23 added strip_think_blocks() to all 16 Inspect AI scorers, but
# affected cells have not been re-run yet. This script re-runs the 4 reasoning
# models on their affected tasks with the fixed scorers.
#
# Models:
#   - DeepSeek-R1 (deepseek-reasoner) via DeepSeek API
#   - DeepSeek-R1-distill-70B via DeepSeek API
#   - MiniMax-M1 (MiniMax-Text-01) via MiniMax API
#   - MiniMax-M2.5 via MiniMax API
#
# Affected tasks (~30 cells):
#   - EMNLP: cpst, hexaco (all 4 models)
#   - MoralBench: mfq_agreement, vignette_agreement, mfq_compare, vignette_compare (all 4)
#   - MoralLens: cot, posthoc, double_standard (varies by model)
#   - MoReBench: advisor, agent (R1-distill, M1, M2.5)
#
# Usage:
#   bash scripts/rerun_reasoning_models.sh [model]
#   bash scripts/rerun_reasoning_models.sh deepseek-r1
#   bash scripts/rerun_reasoning_models.sh all

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/src/inspect/run.py"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"

cd "$ROOT"

# Load env
set -a; source "$ROOT/.env" 2>/dev/null || true; source "$ROOT/.env.local" 2>/dev/null || true; set +a

# Data directories
export MORALBENCH_DATA_DIR="${MORALBENCH_DATA_DIR:-$DATA_ROOT/moralbench}"
export EMNLP_EDUCATOR_DATA_DIR="${EMNLP_EDUCATOR_DATA_DIR:-$DATA_ROOT/emnlp_educator}"
export MORALLENS_DATA_DIR="${MORALLENS_DATA_DIR:-$DATA_ROOT/morallens}"
export MOREBENCH_DATA_DIR="${MOREBENCH_DATA_DIR:-$DATA_ROOT/morebench}"

MAX_CONN=20
RUN_ID="2026-05-19-reasoning-model-rerun"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"

# Resolve runner
if command -v uv >/dev/null 2>&1; then
  RUN_PREFIX=(uv run --package cei-inspect python)
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  RUN_PREFIX=("$ROOT/.venv/bin/python")
else
  echo "No uv or .venv/bin/python found" >&2; exit 1
fi

run_task() {
    local model_label="$1"
    local task_spec="$2"
    local task_name="$3"
    local log_dir="$4"
    local log_file="$log_dir/${task_name}.log"

    echo "  >> $task_name started: $(date)"
    if "${RUN_PREFIX[@]}" "$RUNNER" \
        --tasks "$task_spec" \
        --model "$CURRENT_MODEL" \
        --no_sandbox \
        --max_connections "$MAX_CONN" \
        --log_dir "$log_dir" \
        2>&1 | tee "$log_file"; then
        echo "  >> $task_name DONE: $(date)"
    else
        echo "  >> $task_name FAILED: $(date)"
    fi
}

run_deepseek_r1() {
    local label="deepseek-r1"
    local log_dir="$LOG_BASE/$label"
    mkdir -p "$log_dir"

    export OPENAI_API_KEY="${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY not set}"
    export OPENAI_BASE_URL="https://api.deepseek.com"
    CURRENT_MODEL="openai/deepseek-reasoner"

    echo "=== DeepSeek-R1 ($CURRENT_MODEL) started: $(date) ==="

    # EMNLP (2 tasks)
    run_task "$label" "evals/emnlp_educator.py::emnlp_cpst_personality" "emnlp_cpst" "$log_dir"
    run_task "$label" "evals/emnlp_educator.py::emnlp_hexaco_personality" "emnlp_hexaco" "$log_dir"

    # MoralBench (4 tasks)
    run_task "$label" "evals/moralbench.py::moralbench_mfq_agreement" "moralbench_mfq_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_agreement" "moralbench_vignette_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_mfq_compare" "moralbench_mfq_compare" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_compare" "moralbench_vignette_compare" "$log_dir"

    # MoralLens double-standard only (the known T1 cell)
    run_task "$label" "evals/morallens.py::morallens_double_standard" "morallens_double_standard" "$log_dir"

    echo "=== DeepSeek-R1 complete: $(date) ==="
    echo ""
}

run_deepseek_r1_distill() {
    local label="deepseek-r1-distill"
    local log_dir="$LOG_BASE/$label"
    mkdir -p "$log_dir"

    export OPENAI_API_KEY="${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY not set}"
    export OPENAI_BASE_URL="https://api.deepseek.com"
    CURRENT_MODEL="openai/deepseek-r1-distill-llama-70b"

    echo "=== DeepSeek-R1-distill ($CURRENT_MODEL) started: $(date) ==="

    # EMNLP (2 tasks)
    run_task "$label" "evals/emnlp_educator.py::emnlp_cpst_personality" "emnlp_cpst" "$log_dir"
    run_task "$label" "evals/emnlp_educator.py::emnlp_hexaco_personality" "emnlp_hexaco" "$log_dir"

    # MoralBench (4 tasks)
    run_task "$label" "evals/moralbench.py::moralbench_mfq_agreement" "moralbench_mfq_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_agreement" "moralbench_vignette_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_mfq_compare" "moralbench_mfq_compare" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_compare" "moralbench_vignette_compare" "$log_dir"

    # MoralLens (cot + double_standard — both T1)
    run_task "$label" "evals/morallens.py::morallens_cot" "morallens_cot" "$log_dir"
    run_task "$label" "evals/morallens.py::morallens_double_standard" "morallens_double_standard" "$log_dir"

    # MoReBench (2 tasks)
    run_task "$label" "evals/morebench.py::morebench_advisor" "morebench_advisor" "$log_dir"
    run_task "$label" "evals/morebench.py::morebench_agent" "morebench_agent" "$log_dir"

    echo "=== DeepSeek-R1-distill complete: $(date) ==="
    echo ""
}

run_minimax_m1() {
    local label="minimax-m1"
    local log_dir="$LOG_BASE/$label"
    mkdir -p "$log_dir"

    export OPENAI_API_KEY="${MINIMAX_API_KEY:?MINIMAX_API_KEY not set}"
    export OPENAI_BASE_URL="https://api.minimax.io/v1"
    CURRENT_MODEL="openai/MiniMax-Text-01"

    echo "=== MiniMax-M1 ($CURRENT_MODEL) started: $(date) ==="

    # EMNLP (2 tasks)
    run_task "$label" "evals/emnlp_educator.py::emnlp_cpst_personality" "emnlp_cpst" "$log_dir"
    run_task "$label" "evals/emnlp_educator.py::emnlp_hexaco_personality" "emnlp_hexaco" "$log_dir"

    # MoralBench (4 tasks)
    run_task "$label" "evals/moralbench.py::moralbench_mfq_agreement" "moralbench_mfq_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_agreement" "moralbench_vignette_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_mfq_compare" "moralbench_mfq_compare" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_compare" "moralbench_vignette_compare" "$log_dir"

    # MoralLens CoT (T1 cell)
    run_task "$label" "evals/morallens.py::morallens_cot" "morallens_cot" "$log_dir"

    # MoReBench (2 tasks)
    run_task "$label" "evals/morebench.py::morebench_advisor" "morebench_advisor" "$log_dir"
    run_task "$label" "evals/morebench.py::morebench_agent" "morebench_agent" "$log_dir"

    echo "=== MiniMax-M1 complete: $(date) ==="
    echo ""
}

run_minimax_m25() {
    local label="minimax-m2.5"
    local log_dir="$LOG_BASE/$label"
    mkdir -p "$log_dir"

    export OPENAI_API_KEY="${MINIMAX_API_KEY:?MINIMAX_API_KEY not set}"
    export OPENAI_BASE_URL="https://api.minimax.io/v1"
    CURRENT_MODEL="openai/MiniMax-M2.5"

    echo "=== MiniMax-M2.5 ($CURRENT_MODEL) started: $(date) ==="

    # EMNLP (2 tasks)
    run_task "$label" "evals/emnlp_educator.py::emnlp_cpst_personality" "emnlp_cpst" "$log_dir"
    run_task "$label" "evals/emnlp_educator.py::emnlp_hexaco_personality" "emnlp_hexaco" "$log_dir"

    # MoralBench (4 tasks)
    run_task "$label" "evals/moralbench.py::moralbench_mfq_agreement" "moralbench_mfq_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_agreement" "moralbench_vignette_agreement" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_mfq_compare" "moralbench_mfq_compare" "$log_dir"
    run_task "$label" "evals/moralbench.py::moralbench_vignette_compare" "moralbench_vignette_compare" "$log_dir"

    # MoralLens (all 3 tasks)
    run_task "$label" "evals/morallens.py::morallens_cot" "morallens_cot" "$log_dir"
    run_task "$label" "evals/morallens.py::morallens_posthoc" "morallens_posthoc" "$log_dir"
    run_task "$label" "evals/morallens.py::morallens_double_standard" "morallens_double_standard" "$log_dir"

    # MoReBench (2 tasks)
    run_task "$label" "evals/morebench.py::morebench_advisor" "morebench_advisor" "$log_dir"
    run_task "$label" "evals/morebench.py::morebench_agent" "morebench_agent" "$log_dir"

    echo "=== MiniMax-M2.5 complete: $(date) ==="
    echo ""
}

# Allow running a single model or all
TARGET="${1:-all}"

echo "=========================================="
echo " Reasoning Model Re-run (PR #23 scorer fix)"
echo " Target: $TARGET"
echo " Started: $(date)"
echo "=========================================="
echo ""

case "$TARGET" in
    deepseek-r1)        run_deepseek_r1 ;;
    deepseek-r1-distill) run_deepseek_r1_distill ;;
    minimax-m1)         run_minimax_m1 ;;
    minimax-m2.5)       run_minimax_m25 ;;
    all)
        run_deepseek_r1
        run_deepseek_r1_distill
        run_minimax_m1
        run_minimax_m25
        ;;
    *)
        echo "Unknown model: $TARGET"
        echo "Usage: $0 [deepseek-r1|deepseek-r1-distill|minimax-m1|minimax-m2.5|all]"
        exit 1
        ;;
esac

echo "=========================================="
echo " Reasoning model re-run complete: $(date)"
echo " Logs: $LOG_BASE"
echo "=========================================="
