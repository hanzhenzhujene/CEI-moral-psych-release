#!/usr/bin/env bash
# Run all 7 benchmarks across all 15 model lines via OpenRouter.
# All models run in parallel, each with its own log file.
#
# Usage:
#   ./run_all_benchmarks.sh                    # run all 15 models
#   ./run_all_benchmarks.sh --limit 10         # limit samples per task
#   ./run_all_benchmarks.sh --models 3,5,7     # run only model indices 3, 5, 7
#   ./run_all_benchmarks.sh --max-conn 80      # override max_connections
# Note: -e omitted intentionally — background subshells handle errors via if/else
# DONE/FAILED pattern; -e in the parent would mask child exit codes from `wait`.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load env and provider routing
set -a; source "$SCRIPT_DIR/.env"; set +a
source "$SCRIPT_DIR/provider_config.sh"

# Data directories
export MOREBENCH_DATA_DIR="$SCRIPT_DIR/data/morebench"
export MORAL_CIRCUITS_DATA_DIR="$SCRIPT_DIR/data/moral_circuits"
export M3ORAL_DATA_DIR="$SCRIPT_DIR/data/m3oralbench"
export MORALLENS_DATA_DIR="$SCRIPT_DIR/data/morallens"
export MORALBENCH_DATA_DIR="$SCRIPT_DIR/data/moralbench"
export EMNLP_EDUCATOR_DATA_DIR="$SCRIPT_DIR/data/emnlp_educator"

# All 15 model routes via OpenRouter
ALL_MODELS=(
    "qwen/qwen3-8b"
    "qwen/qwen3-32b"
    "qwen/qwen3-235b-a22b"
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

BENCHMARKS=(
    "evals/morebench.py"
    "evals/moral_circuits.py"
    "evals/m3oralbench.py"
    "evals/morallens.py"
    "evals/moralbench.py"
    "evals/emnlp_educator.py"
    "evals/rules_broken.py"
)

BENCHMARK_NAMES=(
    "MoReBench"
    "MoralCircuits"
    "M3oralBench"
    "MoralLens"
    "MoralBench"
    "EMNLPEducator"
    "RulesBroken"
)

# Defaults
MAX_CONN=50
LIMIT_ARGS=()
MODEL_FILTER=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --limit)
            LIMIT_ARGS=("--limit" "$2")
            shift 2
            ;;
        --max-conn)
            MAX_CONN="$2"
            shift 2
            ;;
        --models)
            MODEL_FILTER="$2"
            shift 2
            ;;
        *)
            echo "Unknown arg: $1"
            exit 1
            ;;
    esac
done

# Select models to run
MODELS=()
if [[ -n "$MODEL_FILTER" ]]; then
    IFS=',' read -ra INDICES <<< "$MODEL_FILTER"
    for i in "${INDICES[@]}"; do
        idx=$((i - 1))
        if [[ $idx -ge 0 && $idx -lt ${#ALL_MODELS[@]} ]]; then
            MODELS+=("${ALL_MODELS[$idx]}")
        else
            echo "Warning: model index $i out of range (1-${#ALL_MODELS[@]})"
        fi
    done
else
    MODELS=("${ALL_MODELS[@]}")
fi

mkdir -p "$SCRIPT_DIR/results"

# --- Per-model runner ---
run_model() {
    local MODEL="$1"
    local SLUG
    SLUG=$(echo "$MODEL" | tr '/' '_')
    local LOG="$SCRIPT_DIR/results/run_log_${SLUG}_$(date +%Y%m%d_%H%M%S).txt"

    # Resolve provider (Ark, DeepSeek, or OpenRouter fallback)
    setup_model_provider "$MODEL"

    echo "=== $MODEL started: $(date) ===" | tee "$LOG"

    local BENCH_IDX=0
    for BENCH in "${BENCHMARKS[@]}"; do
        local BENCH_NAME="${BENCHMARK_NAMES[$BENCH_IDX]}"
        BENCH_IDX=$((BENCH_IDX + 1))

        # Skip RulesBroken if UniMoral data is not available
        if [[ "$BENCH_NAME" == "RulesBroken" && -z "${UNIMORAL_DATA_DIR:-}" ]]; then
            echo "  >> $BENCH_NAME SKIPPED (UNIMORAL_DATA_DIR not set)" | tee -a "$LOG"
            continue
        fi

        # Skip Moral Circuits for non-Qwen/Llama models
        if [[ "$BENCH_NAME" == "MoralCircuits" ]]; then
            case "$MODEL" in
                qwen/*|meta-llama/*) ;;
                *)
                    echo "  >> $BENCH_NAME SKIPPED (not applicable)" | tee -a "$LOG"
                    continue
                    ;;
            esac
        fi

        echo "  >> $BENCH_NAME started: $(date)" | tee -a "$LOG"

        (
            cd "$SCRIPT_DIR/src/inspect"
            if uv run --package cei-inspect python run.py \
                --tasks "$BENCH" \
                --model "openai/$EFFECTIVE_MODEL" \
                --no_sandbox \
                --max_connections "$MAX_CONN" \
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

# --- Launch all models in parallel ---
echo "=== CEI Benchmark Run ==="
echo "Started: $(date)"
echo "Models: ${#MODELS[@]} (max_connections=$MAX_CONN)"
echo "Benchmarks: ${#BENCHMARKS[@]}"
echo ""

PIDS=()
for MODEL in "${MODELS[@]}"; do
    run_model "$MODEL" &
    PIDS+=($!)
    echo "  Launched $MODEL (PID ${PIDS[-1]})"
done

echo ""
echo "All ${#MODELS[@]} models launched. PIDs: ${PIDS[*]}"
echo "Logs: results/run_log_*.txt"
echo ""

wait "${PIDS[@]}"
echo "=== All ${#MODELS[@]} models complete: $(date) ==="
