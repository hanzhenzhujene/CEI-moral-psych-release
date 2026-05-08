#!/usr/bin/env bash
# Run Erik's benchmarks for MiniMax models with low concurrency
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

set -a; source "$SCRIPT_DIR/.env"; set +a

export MORALBENCH_DATA_DIR="$SCRIPT_DIR/data/moralbench"
export EMNLP_EDUCATOR_DATA_DIR="$SCRIPT_DIR/data/emnlp_educator"
export OPENAI_API_KEY="$MINIMAX_API_KEY"
export OPENAI_BASE_URL="https://api.minimax.io/v1"

mkdir -p "$SCRIPT_DIR/results"

run_minimax() {
    local MODEL_ID="$1"
    local SLUG="$2"
    local LOG="$SCRIPT_DIR/results/run_erik_minimax_${SLUG}.txt"

    echo "=== minimax/$SLUG ($MODEL_ID) started: $(date) ===" | tee "$LOG"

    cd "$SCRIPT_DIR/src/inspect"

    echo "  >> MoralBench started: $(date)" | tee -a "$LOG"
    if uv run --package cei-inspect python run.py \
        --tasks "evals/moralbench.py" \
        --model "openai/$MODEL_ID" \
        --no_sandbox \
        --max_connections 3 \
        2>&1 | tee -a "$LOG"; then
        echo "  >> MoralBench DONE: $(date)" | tee -a "$LOG"
    else
        echo "  >> MoralBench FAILED: $(date)" | tee -a "$LOG"
    fi

    echo "  >> EMNLPEducator started: $(date)" | tee -a "$LOG"
    if uv run --package cei-inspect python run.py \
        --tasks "evals/emnlp_educator.py" \
        --model "openai/$MODEL_ID" \
        --no_sandbox \
        --max_connections 3 \
        2>&1 | tee -a "$LOG"; then
        echo "  >> EMNLPEducator DONE: $(date)" | tee -a "$LOG"
    else
        echo "  >> EMNLPEducator FAILED: $(date)" | tee -a "$LOG"
    fi

    echo "=== minimax/$SLUG complete: $(date) ===" | tee -a "$LOG"
}

MODEL_ID="${1:-MiniMax-Text-01}"
SLUG="${2:-minimax-01}"

run_minimax "$MODEL_ID" "$SLUG"
