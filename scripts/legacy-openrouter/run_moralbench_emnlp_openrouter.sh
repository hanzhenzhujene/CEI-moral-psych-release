#!/usr/bin/env bash
# Run MoralBench + EMNLP Educator benchmarks for OpenRouter models
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
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
    local LOG="$SCRIPT_DIR/results/run_moralbench_emnlp_${SLUG}.txt"

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

echo "=== OpenRouter MoralBench + EMNLP Educator Benchmarks ==="
echo "Started: $(date)"

PIDS=()

run_model "llama/llama-3.2-3b" "meta-llama/llama-3.2-3b-instruct" &
PIDS+=($!)
echo "  Launched llama-3.2-3b (PID ${PIDS[${#PIDS[@]}-1]})"

run_model "llama/llama-3.1-8b" "meta-llama/llama-3.1-8b-instruct" &
PIDS+=($!)
echo "  Launched llama-3.1-8b (PID ${PIDS[${#PIDS[@]}-1]})"

run_model "llama/llama-3.3-70b" "meta-llama/llama-3.3-70b-instruct" &
PIDS+=($!)
echo "  Launched llama-3.3-70b (PID ${PIDS[${#PIDS[@]}-1]})"

run_model "minimax/minimax-m1" "minimax/minimax-m1" &
PIDS+=($!)
echo "  Launched minimax-m1 (PID ${PIDS[${#PIDS[@]}-1]})"

echo ""
echo "4 models launched. PIDs: ${PIDS[*]}"
echo "Logs: results/run_moralbench_emnlp_*.txt"

wait "${PIDS[@]}"
echo "=== All 4 models complete: $(date) ==="
