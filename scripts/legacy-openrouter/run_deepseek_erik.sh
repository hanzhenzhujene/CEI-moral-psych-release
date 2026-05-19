#!/usr/bin/env bash
# Run Erik's benchmarks for DeepSeek models
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SCRIPT_DIR"

set -a; source "$SCRIPT_DIR/.env"; set +a

export MORALBENCH_DATA_DIR="$SCRIPT_DIR/data/moralbench"
export EMNLP_EDUCATOR_DATA_DIR="$SCRIPT_DIR/data/emnlp_educator"

mkdir -p "$SCRIPT_DIR/results"

run_model() {
    local ROUTE="$1"
    local MODEL_ID="$2"
    local PROVIDER_URL="$3"
    local API_KEY="$4"

    export OPENAI_API_KEY="$API_KEY"
    export OPENAI_BASE_URL="$PROVIDER_URL"

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

echo "=== DeepSeek Erik Benchmarks ==="
echo "Started: $(date)"

PIDS=()

# DeepSeek R1 via DeepSeek direct (deepseek-reasoner still works)
run_model "deepseek/deepseek-r1" "deepseek-reasoner" \
    "https://api.deepseek.com" "$DEEPSEEK_API_KEY" &
PIDS+=($!)
echo "  Launched deepseek-r1 via DeepSeek direct (PID ${PIDS[${#PIDS[@]}-1]})"

# DeepSeek R1-distill via OpenRouter (not on DeepSeek direct anymore)
run_model "deepseek/deepseek-r1-distill-70b" "deepseek/deepseek-r1-distill-llama-70b" \
    "https://openrouter.ai/api/v1" "$OPENROUTER_API_KEY" &
PIDS+=($!)
echo "  Launched deepseek-r1-distill-70b via OpenRouter (PID ${PIDS[${#PIDS[@]}-1]})"

# DeepSeek V3.1 via DeepSeek direct (deepseek-chat, bypasses Ark endpoint issue)
run_model "deepseek/deepseek-chat-v3.1" "deepseek-chat" \
    "https://api.deepseek.com" "$DEEPSEEK_API_KEY" &
PIDS+=($!)
echo "  Launched deepseek-v3.1 via DeepSeek direct (PID ${PIDS[${#PIDS[@]}-1]})"

echo ""
echo "3 models launched. PIDs: ${PIDS[*]}"

wait "${PIDS[@]}"
echo "=== All 3 models complete: $(date) ==="
