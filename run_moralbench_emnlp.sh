#!/usr/bin/env bash
# Run MoralBench + EMNLP Educator benchmarks (MoralBench + EMNLP Educator) for models with working providers.
# Each model runs in parallel; benchmarks run sequentially per model.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load env with export-all so HF_TOKEN propagates to subprocesses
set -a; source "$SCRIPT_DIR/.env"; set +a

# Source provider routing
source "$SCRIPT_DIR/provider_config.sh"

# Data directories
export MORALBENCH_DATA_DIR="$SCRIPT_DIR/data/moralbench"
export EMNLP_EDUCATOR_DATA_DIR="$SCRIPT_DIR/data/emnlp_educator"

BENCHMARKS=(
    "evals/moralbench.py"
    "evals/emnlp_educator.py"
)

BENCHMARK_NAMES=(
    "MoralBench"
    "EMNLPEducator"
)

MAX_CONN=50
mkdir -p "$SCRIPT_DIR/results"

run_model() {
    local MODEL_ROUTE="$1"
    local PROVIDER_URL="$2"
    local API_KEY="$3"
    local MODEL_ID="$4"
    local EXTRA_BODY="${5:-}"

    export OPENAI_API_KEY="$API_KEY"
    export OPENAI_BASE_URL="$PROVIDER_URL"

    local SLUG
    SLUG=$(echo "$MODEL_ROUTE" | tr '/' '_')
    local LOG="$SCRIPT_DIR/results/run_moralbench_emnlp_${SLUG}.txt"

    echo "=== $MODEL_ROUTE ($MODEL_ID) started: $(date) ===" | tee "$LOG"

    for i in "${!BENCHMARKS[@]}"; do
        local BENCH="${BENCHMARKS[$i]}"
        local BENCH_NAME="${BENCHMARK_NAMES[$i]}"

        echo "  >> $BENCH_NAME started: $(date)" | tee -a "$LOG"

        (
            cd "$SCRIPT_DIR/src/inspect"
            local EXTRA_ARGS=""
            if [[ -n "$EXTRA_BODY" ]]; then
                EXTRA_ARGS="--extra_body_json $EXTRA_BODY"
            fi
            # shellcheck disable=SC2086
            if uv run --package cei-inspect python run.py \
                --tasks "$BENCH" \
                --model "openai/$MODEL_ID" \
                --no_sandbox \
                --max_connections "$MAX_CONN" \
                $EXTRA_ARGS \
                2>&1 | tee -a "$LOG"; then
                echo "  >> $BENCH_NAME DONE: $(date)" | tee -a "$LOG"
            else
                echo "  >> $BENCH_NAME FAILED: $(date)" | tee -a "$LOG"
            fi
        )

        echo "" | tee -a "$LOG"
    done

    echo "=== $MODEL_ROUTE complete: $(date) ===" | tee -a "$LOG"
}

echo "=== MoralBench + EMNLP Educator Benchmarks ==="
echo "Started: $(date)"
echo "Running models with working providers only"
echo "Benchmarks: MoralBench (4 tasks), EMNLP Educator (4 tasks)"
echo ""

PIDS=()

# DashScope models (need enable_thinking=false for Qwen3)
(run_model "qwen/qwen3-8b" \
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" \
    "$DASHSCOPE_API_KEY" \
    "qwen3-8b" \
    '{"enable_thinking":false}') &
PIDS+=($!)
echo "  Launched qwen3-8b via DashScope (PID ${PIDS[${#PIDS[@]}-1]})"

(run_model "qwen/qwen3-32b" \
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" \
    "$DASHSCOPE_API_KEY" \
    "qwen3-32b" \
    '{"enable_thinking":false}') &
PIDS+=($!)
echo "  Launched qwen3-32b via DashScope (PID ${PIDS[${#PIDS[@]}-1]})"

# Together
(run_model "qwen/qwen3-235b" \
    "https://api.together.xyz/v1" \
    "$TOGETHER_API_KEY" \
    "Qwen/Qwen3-235B-A22B-Instruct-2507-tput") &
PIDS+=($!)
echo "  Launched qwen3-235b via Together (PID ${PIDS[${#PIDS[@]}-1]})"

# MiniMax direct
(run_model "minimax/minimax-01" \
    "https://api.minimax.io/v1" \
    "$MINIMAX_API_KEY" \
    "MiniMax-Text-01") &
PIDS+=($!)
echo "  Launched minimax-01 via MiniMax (PID ${PIDS[${#PIDS[@]}-1]})"

(run_model "minimax/minimax-m2.5" \
    "https://api.minimax.io/v1" \
    "$MINIMAX_API_KEY" \
    "MiniMax-M2.5") &
PIDS+=($!)
echo "  Launched minimax-m2.5 via MiniMax (PID ${PIDS[${#PIDS[@]}-1]})"

echo ""
echo "5 models launched. PIDs: ${PIDS[*]}"
echo ""
echo "SKIPPED (provider issues):"
echo "  - DeepSeek R1, R1-distill, V3.1: insufficient balance / Ark needs endpoint IDs"
echo "  - Llama 3.2-3b, 3.1-8b, 3.3-70b: OpenRouter out of credits"
echo "  - Gemma 3-4b, 3-12b, 3-27b: models removed from Google AI Studio"
echo "  - MiniMax-M1: OpenRouter out of credits"
echo ""
echo "Logs: results/run_moralbench_emnlp_*.txt"
echo ""

wait "${PIDS[@]}"
echo "=== All 5 models complete: $(date) ==="
