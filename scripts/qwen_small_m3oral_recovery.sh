#!/usr/bin/env bash
# Controlled recovery launcher for the blocked Qwen-S M3oralBench tasks.
# This keeps retries scoped to judgment/response and makes provider pinning easy.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/src/inspect/run.py"
UV_BIN="${UV_BIN:-$(command -v uv 2>/dev/null || true)}"
VENV_PYTHON="${VENV_PYTHON:-$ROOT/.venv/bin/python}"

if [[ -n "${UV_BIN}" ]] && { [[ -x "${UV_BIN}" ]] || command -v "${UV_BIN}" >/dev/null 2>&1; }; then
  RUN_PREFIX=("${UV_BIN}" "run" "--package" "cei-inspect" "python")
elif [[ -x "${VENV_PYTHON}" ]]; then
  RUN_PREFIX=("${VENV_PYTHON}")
else
  echo "Could not resolve either uv or $VENV_PYTHON. Set UV_BIN or VENV_PYTHON before running $(basename "$0")." >&2
  exit 1
fi

RUN_ID="${RUN_ID:-2026-05-02-qwen-small-m3oral-recovery}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
DEFAULT_MODEL="openai/qwen/qwen3-8b"
NVIDIA_SMOKE_MODEL_DEFAULT="openai/nvidia/llama-3.1-nemotron-nano-8b-v1"
MODEL="${MODEL:-$DEFAULT_MODEL}"
MODEL_BASE_URL="${MODEL_BASE_URL:-}"
# MODEL_ARGS_JSON is passed to --model_args_json verbatim. By default it pins
# OpenRouter to a constrained provider set that has worked for other Qwen recoveries.
DEFAULT_MODEL_ARGS_JSON='{"extra_body":{"provider":{"only":["nebius","novita","parasail"],"allow_fallbacks":true}}}'
MODEL_ARGS_JSON="${MODEL_ARGS_JSON:-${PROVIDER_ARGS_JSON:-$DEFAULT_MODEL_ARGS_JSON}}"
MAX_CONNECTIONS="${MAX_CONNECTIONS:-1}"
SMOKE_LIMIT="${SMOKE_LIMIT:-25}"
RUNTIME_HOME="${RUNTIME_HOME:-$ROOT/.tmp/inspect-home/$RUN_ID}"

if [[ -n "${NVIDIA_API_KEY:-}" ]] && [[ -z "${MODEL_BASE_URL}" ]]; then
  MODEL_BASE_URL="https://integrate.api.nvidia.com/v1"
fi

if [[ -n "${NVIDIA_API_KEY:-}" ]]; then
  export OPENAI_API_KEY="${OPENAI_API_KEY:-$NVIDIA_API_KEY}"
fi

if [[ "$MODEL_BASE_URL" == *"integrate.api.nvidia.com"* ]] && [[ "$MODEL_ARGS_JSON" == "$DEFAULT_MODEL_ARGS_JSON" ]]; then
  MODEL_ARGS_JSON='{}'
fi

if [[ "$MODEL_BASE_URL" == *"integrate.api.nvidia.com"* ]] && [[ "$MODEL" != openai/* ]] && [[ "$MODEL" != openai-api/* ]]; then
  MODEL="openai/$MODEL"
fi

mkdir -p "$RUN_BASE" "$LOG_BASE"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") smoke
  $(basename "$0") run
  $(basename "$0") judgment
  $(basename "$0") response
  $(basename "$0") status

Environment overrides:
  UV_BIN=/absolute/path/to/uv
  VENV_PYTHON=/absolute/path/to/.venv/bin/python
  RUN_ID=custom-run-id
  MODEL=openai/qwen/qwen3-8b
  MODEL_ARGS_JSON='{"extra_body":{"provider":{"only":["nebius"],"allow_fallbacks":false}}}'
  MODEL_BASE_URL='https://integrate.api.nvidia.com/v1'
  NVIDIA_API_KEY=nvapi-...
  RUNTIME_HOME=/absolute/path/to/repo/.tmp/inspect-home/nvidia-smoke
  MAX_CONNECTIONS=1
  SMOKE_LIMIT=25

Notes:
  - NVIDIA Build uses the OpenAI-compatible base URL https://integrate.api.nvidia.com/v1
  - When targeting NVIDIA, choose a model ID that NVIDIA actually serves.
    The default openrouter/qwen route is not guaranteed to exist on NVIDIA.
  - If you still use PROVIDER_ARGS_JSON, it is treated as an alias for MODEL_ARGS_JSON
EOF
}

now_iso() {
  python3 - <<'PY'
from datetime import datetime
print(datetime.now().astimezone().isoformat())
PY
}

record_status() {
  local task_name="$1"
  local start_at="$2"
  local end_at="$3"
  local returncode="$4"
  local output_path="$5"
  local status_file="$RUN_BASE/task_status.csv"
  if [[ ! -f "$status_file" ]]; then
    echo "task_name,start_at,end_at,returncode,output_path" > "$status_file"
  fi
  echo "$task_name,$start_at,$end_at,$returncode,$output_path" >> "$status_file"
}

run_task() {
  local task_name="$1"
  local task_spec="$2"
  local output_path="$RUN_BASE/${task_name}.txt"
  local start_at end_at rc
  local limit_args=()
  local cmd=()

  if [[ $# -ge 3 && -n "${3:-}" ]]; then
    limit_args=(--limit "$3")
  fi

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START task=$task_name model=$MODEL max_connections=$MAX_CONNECTIONS model_args_json=$MODEL_ARGS_JSON"
    cmd=(
      "${RUN_PREFIX[@]}" "$RUNNER"
      --tasks "$task_spec"
      --model "$MODEL"
      --model_args_json "$MODEL_ARGS_JSON"
      --temperature 0
      --no_sandbox
      --max_connections "$MAX_CONNECTIONS"
      --log_dir "$LOG_BASE"
      --home_dir "$RUNTIME_HOME"
    )
    if [[ -n "$MODEL_BASE_URL" ]]; then
      cmd+=(--model_base_url "$MODEL_BASE_URL")
    fi
    if [[ ${#limit_args[@]} -gt 0 ]]; then
      cmd+=("${limit_args[@]}")
    fi
    "${cmd[@]}"
    rc=$?
    end_at="$(now_iso)"
    echo "[$end_at] END task=$task_name returncode=$rc"
    exit "$rc"
  ) > "$output_path" 2>&1; then
    rc=0
  else
    rc=$?
  fi

  end_at="$(now_iso)"
  record_status "$task_name" "$start_at" "$end_at" "$rc" "$output_path"
  echo "task=$task_name returncode=$rc output=$output_path"
  return "$rc"
}

run_smoke() {
  if [[ "$MODEL_BASE_URL" == *"integrate.api.nvidia.com"* ]] && [[ "$MODEL" == "$DEFAULT_MODEL" ]]; then
    MODEL="$NVIDIA_SMOKE_MODEL_DEFAULT"
    echo "Using NVIDIA-compatible smoke model: $MODEL" >&2
  fi
  run_task "m3oralbench_judgment_smoke" "evals/m3oralbench.py::m3oralbench_judgment" "$SMOKE_LIMIT"
  run_task "m3oralbench_response_smoke" "evals/m3oralbench.py::m3oralbench_response" "$SMOKE_LIMIT"
}

run_full() {
  run_task "m3oralbench_judgment" "evals/m3oralbench.py::m3oralbench_judgment"
  run_task "m3oralbench_response" "evals/m3oralbench.py::m3oralbench_response"
}

print_status() {
  local status_file="$RUN_BASE/task_status.csv"
  if [[ -f "$status_file" ]]; then
    cat "$status_file"
  else
    echo "No status file at $status_file"
  fi
}

case "${1:-}" in
  smoke)
    run_smoke
    ;;
  run)
    run_full
    ;;
  judgment)
    run_task "m3oralbench_judgment" "evals/m3oralbench.py::m3oralbench_judgment"
    ;;
  response)
    run_task "m3oralbench_response" "evals/m3oralbench.py::m3oralbench_response"
    ;;
  status)
    print_status
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    echo "Unknown subcommand: $1" >&2
    usage >&2
    exit 1
    ;;
esac
