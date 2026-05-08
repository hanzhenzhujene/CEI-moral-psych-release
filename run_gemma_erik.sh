#!/usr/bin/env bash
# Run Erik's benchmarks for Gemma 3 models via OpenRouter
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

set -a; source "$SCRIPT_DIR/.env"; set +a

export MORALBENCH_DATA_DIR="$SCRIPT_DIR/data/moralbench"
export EMNLP_EDUCATOR_DATA_DIR="$SCRIPT_DIR/data/emnlp_educator"
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

mkdir -p "$SCRIPT_DIR/results"

run_model() {
    local ROUTE="$1"
    local MODEL_ID="$2"
    local SLUG
    SLUG=$(echo "$ROUTE" | tr '/' '_')
    local LOG="$SCRIPT_DIR/results/run_erik_${SLUG}.txt"

    echo "=== $ROUTE ($MODEL_ID) started: $(date) ===" | tee "$LOG"

    cd "$SCRIPT_DIR/src/inspect"

    for bench_entry in "evals/moralbench.py:MoralBench" "evals/emnlp_educator.py:EMNLPEducator"; do
        local BENCH="${bench_entry%%:*}"
        local NAME="${bench_entry#*:}"

        echo "  >> $NAME started: $(date)" | tee -a "$LOG"
        if uv run --package cei-inspect python run.py \
            --tasks "$BENCH" \
            --model "openai/$MODEL_ID" \
            --no_sandbox \
            --max_connections 50 \
            2>&1 | tee -a "$LOG"; then
            echo "  >> $NAME DONE: $(date)" | tee -a "$LOG"
        else
            echo "  >> $NAME FAILED: $(date)" | tee -a "$LOG"
        fi
    done

    echo "=== $ROUTE complete: $(date) ===" | tee -a "$LOG"
}

echo "=== Gemma Erik Benchmarks (via OpenRouter) ==="
echo "Started: $(date)"

PIDS=()

run_model "google/gemma-3-4b" "google/gemma-3-4b-it" &
PIDS+=($!)
echo "  Launched gemma-3-4b (PID ${PIDS[${#PIDS[@]}-1]})"

run_model "google/gemma-3-12b" "google/gemma-3-12b-it" &
PIDS+=($!)
echo "  Launched gemma-3-12b (PID ${PIDS[${#PIDS[@]}-1]})"

run_model "google/gemma-3-27b" "google/gemma-3-27b-it" &
PIDS+=($!)
echo "  Launched gemma-3-27b (PID ${PIDS[${#PIDS[@]}-1]})"

echo ""
echo "3 models launched. PIDs: ${PIDS[*]}"

wait "${PIDS[@]}"
echo "=== All 3 models complete: $(date) ==="
