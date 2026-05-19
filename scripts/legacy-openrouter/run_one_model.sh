#!/usr/bin/env bash
# Run all benchmarks for a single model.
# Usage: scripts/legacy-openrouter/run_one_model.sh <model_id> [--limit N]
# Example: scripts/legacy-openrouter/run_one_model.sh deepseek/deepseek-r1
#          scripts/legacy-openrouter/run_one_model.sh google/gemma-3-4b-it --limit 10
set -euo pipefail

if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <model_id> [--limit N]" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Load env and provider routing
set -a; source "$SCRIPT_DIR/.env"; set +a
source "$SCRIPT_DIR/provider_config.sh"

export MOREBENCH_DATA_DIR="$SCRIPT_DIR/data/morebench"
export MORAL_CIRCUITS_DATA_DIR="$SCRIPT_DIR/data/moral_circuits"
export M3ORAL_DATA_DIR="$SCRIPT_DIR/data/m3oralbench"
export MORALLENS_DATA_DIR="$SCRIPT_DIR/data/morallens"

MODEL="$1"
shift

LIMIT_ARGS=()
if [[ "${1:-}" == "--limit" ]] && [[ -n "${2:-}" ]]; then
    LIMIT_ARGS=("--limit" "$2")
fi

MAX_CONN=20
SLUG=$(echo "$MODEL" | tr '/' '_')
LOG="$SCRIPT_DIR/results/run_log_${SLUG}_$(date +%Y%m%d_%H%M%S).txt"

# Resolve provider (Ark, DeepSeek, or OpenRouter fallback)
setup_model_provider "$MODEL"

echo "=== $MODEL started: $(date) ===" | tee "$LOG"

run_bench() {
    local BENCH="$1" BENCH_NAME="$2"
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
}

run_bench "evals/morebench.py" "MoReBench"

# Moral Circuits only for Qwen/Llama
case "$MODEL" in
    qwen/*|meta-llama/*) run_bench "evals/moral_circuits.py" "MoralCircuits" ;;
    *) echo "  >> MoralCircuits SKIPPED" | tee -a "$LOG" ;;
esac

run_bench "evals/m3oralbench.py" "M3oralBench"
run_bench "evals/morallens.py" "MoralLens"

echo "=== $MODEL complete: $(date) ===" | tee -a "$LOG"
