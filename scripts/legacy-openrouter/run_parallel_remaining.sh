#!/usr/bin/env bash
# DEPRECATED: Use scripts/legacy-openrouter/run_all_benchmarks.sh --models 4,5,6,7,8,9,10,11,12,13,14,15 instead.
# Run remaining 12 models — each model as its own parallel stream.
# Usage: scripts/legacy-openrouter/run_parallel_remaining.sh [--limit N]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SCRIPT_DIR"

# Load env and provider routing
set -a; source "$SCRIPT_DIR/.env"; set +a
source "$SCRIPT_DIR/provider_config.sh"

# Data directories
export MOREBENCH_DATA_DIR="$SCRIPT_DIR/data/morebench"
export MORAL_CIRCUITS_DATA_DIR="$SCRIPT_DIR/data/moral_circuits"
export M3ORAL_DATA_DIR="$SCRIPT_DIR/data/m3oralbench"
export MORALLENS_DATA_DIR="$SCRIPT_DIR/data/morallens"

# Parse args
LIMIT_ARGS=()
if [[ "${1:-}" == "--limit" ]] && [[ -n "${2:-}" ]]; then
    LIMIT_ARGS=("--limit" "$2")
    echo ">>> Running with --limit $2"
fi

BENCHMARKS=(
    "evals/morebench.py"
    "evals/moral_circuits.py"
    "evals/m3oralbench.py"
    "evals/morallens.py"
)

BENCHMARK_NAMES=(
    "MoReBench"
    "MoralCircuits"
    "M3oralBench"
    "MoralLens"
)

run_single_model() {
    local MODEL="$1"
    local SLUG=$(echo "$MODEL" | tr '/' '_')
    local LOG="$SCRIPT_DIR/results/run_log_${SLUG}_$(date +%Y%m%d_%H%M%S).txt"

    # Resolve provider (Ark, DeepSeek, or OpenRouter fallback)
    setup_model_provider "$MODEL"

    echo "=== $MODEL started: $(date) ===" | tee "$LOG"

    local BENCH_IDX=0
    for BENCH in "${BENCHMARKS[@]}"; do
        local BENCH_NAME="${BENCHMARK_NAMES[$BENCH_IDX]}"
        BENCH_IDX=$((BENCH_IDX + 1))

        # Skip Moral Circuits for non-Qwen/Llama models
        if [[ "$BENCH_NAME" == "MoralCircuits" ]]; then
            case "$MODEL" in
                qwen/*|meta-llama/*) ;;
                *)
                    echo "  >> $BENCH_NAME SKIPPED (not applicable): $(date)" | tee -a "$LOG"
                    continue
                    ;;
            esac
        fi

        echo "  >> $BENCH_NAME ($BENCH)" | tee -a "$LOG"
        echo "  >> Started: $(date)" | tee -a "$LOG"

        (
            cd "$SCRIPT_DIR/src/inspect"
            if uv run --package cei-inspect python run.py \
                --tasks "$BENCH" \
                --model "openai/$EFFECTIVE_MODEL" \
                --no_sandbox \
                --max_connections 50 \
                ${LIMIT_ARGS[@]+"${LIMIT_ARGS[@]}"} \
                2>&1 | tee -a "$LOG"; then
                echo "  >> $BENCH_NAME DONE: $(date)" | tee -a "$LOG"
            else
                echo "  >> $BENCH_NAME FAILED: $(date)" | tee -a "$LOG"
            fi
        )

        echo "" | tee -a "$LOG"
    done

    echo "=== $MODEL complete: $(date) ===" | tee -a "$LOG"
}

# All 12 remaining models
MODELS=(
    "deepseek/deepseek-r1-distill-llama-70b"
    "deepseek/deepseek-chat-v3.1"
    "deepseek/deepseek-r1"
    "meta-llama/llama-3.2-3b-instruct"
    "meta-llama/llama-3.1-8b-instruct"
    "meta-llama/llama-3.3-70b-instruct"
    "google/gemma-3-4b-it"
    "google/gemma-3-12b-it"
    "google/gemma-3-27b-it"
    "minimax/minimax-01"
    "minimax/minimax-m1"
    "minimax/minimax-m2.5"
)

echo "=== Launching 12 parallel model runs: $(date) ==="

PIDS=()
for MODEL in "${MODELS[@]}"; do
    run_single_model "$MODEL" &
    PIDS+=($!)
    echo "  Launched $MODEL (PID ${PIDS[-1]})"
done

echo ""
echo "All 12 models launched. PIDs: ${PIDS[*]}"
echo "Logs: results/run_log_*.txt"

wait "${PIDS[@]}"
echo "=== All 12 models complete: $(date) ==="
