#!/usr/bin/env bash
# Historical launcher for the formal FULCRA-backed Denevil proxy run.
# It preserves the original operational flow while remaining portable via env overrides.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
RUNNER="$ROOT/src/inspect/run.py"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"
UV_BIN="${UV_BIN:-$(command -v uv 2>/dev/null || true)}"

if [[ -z "${UV_BIN}" ]] || { [[ ! -x "${UV_BIN}" ]] && ! command -v "${UV_BIN}" >/dev/null 2>&1; }; then
  echo "Could not resolve uv. Set UV_BIN=/absolute/path/to/uv before running $(basename "$0")." >&2
  exit 1
fi

RUN_ID="${RUN_ID:-2026-04-18-denevil-fulcra-proxy-formal}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
LAUNCHER_STDOUT_DIR="$RUN_BASE/launcher"

TEXT_MAX_CONNECTIONS="${TEXT_MAX_CONNECTIONS:-2}"
DENEVIL_DATA_FILE="${DENEVIL_DATA_FILE:-$DATA_ROOT/denevil/data_hybrid.jsonl}"
QWEN_MODEL="${QWEN_MODEL:-openrouter/qwen/qwen3-8b}"
DEEPSEEK_MODEL="${DEEPSEEK_MODEL:-openrouter/deepseek/deepseek-chat-v3.1}"
GEMMA_MODEL="${GEMMA_MODEL:-openrouter/google/gemma-3-4b-it}"

families=(
  qwen_proxy
  deepseek_proxy
  gemma_proxy
)

mkdir -p "$RUN_BASE" "$LOG_BASE" "$PID_DIR" "$LAUNCHER_STDOUT_DIR"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") launch
  $(basename "$0") run <family>
  $(basename "$0") status

Families:
  ${families[*]}

Optional overrides:
  UV_BIN=/absolute/path/to/uv
  DATA_ROOT=/absolute/path/to/data
  DENEVIL_DATA_FILE=/absolute/path/to/fulcra_proxy.jsonl
EOF
}

now_iso() {
  python3 - <<'PY'
from datetime import datetime
print(datetime.now().astimezone().isoformat())
PY
}

family_run_dir() {
  local family="$1"
  echo "$RUN_BASE/$family"
}

is_running_pid() {
  local pid="$1"
  kill -0 "$pid" 2>/dev/null
}

require_file() {
  local var_name="$1"
  local path="${!var_name}"
  if [[ ! -f "$path" ]]; then
    echo "Missing file for $var_name: $path" >&2
    exit 1
  fi
}

record_status() {
  local family="$1"
  local task_name="$2"
  local start_at="$3"
  local end_at="$4"
  local returncode="$5"
  local output_path="$6"
  local status_file
  status_file="$(family_run_dir "$family")/task_status.csv"
  if [[ ! -f "$status_file" ]]; then
    echo "task_name,start_at,end_at,returncode,output_path" > "$status_file"
  fi
  echo "$task_name,$start_at,$end_at,$returncode,$output_path" >> "$status_file"
}

run_task() {
  local family="$1"
  local model="$2"

  local run_dir output_path log_dir start_at end_at rc
  run_dir="$(family_run_dir "$family")"
  output_path="$run_dir/denevil_fulcra_proxy_generation.txt"
  log_dir="$LOG_BASE/$family"
  mkdir -p "$run_dir" "$log_dir"

  start_at="$(now_iso)"
  (
    export DENEVIL_DATA_FILE="$DENEVIL_DATA_FILE"
    echo "[$start_at] START family=$family task=denevil_fulcra_proxy_generation model=$model max_connections=$TEXT_MAX_CONNECTIONS data_file=$DENEVIL_DATA_FILE"
    "$UV_BIN" run --package cei-inspect python "$RUNNER" \
      --tasks "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" \
      --model "$model" \
      --temperature 0 \
      --no_sandbox \
      --max_connections "$TEXT_MAX_CONNECTIONS" \
      --log_dir "$log_dir"
    rc=$?
    end_at="$(now_iso)"
    echo "[$end_at] END family=$family task=denevil_fulcra_proxy_generation returncode=$rc"
    exit "$rc"
  ) > "$output_path" 2>&1

  rc=$?
  end_at="$(now_iso)"
  record_status "$family" "denevil_fulcra_proxy_generation" "$start_at" "$end_at" "$rc" "$output_path"
  return 0
}

run_family() {
  local family="$1"
  local run_dir model
  run_dir="$(family_run_dir "$family")"
  mkdir -p "$run_dir"
  require_file DENEVIL_DATA_FILE

  case "$family" in
    qwen_proxy)
      model="$QWEN_MODEL"
      ;;
    deepseek_proxy)
      model="$DEEPSEEK_MODEL"
      ;;
    gemma_proxy)
      model="$GEMMA_MODEL"
      ;;
    *)
      echo "Unknown family: $family" >&2
      return 1
      ;;
  esac

  run_task "$family" "$model"
  now_iso > "$run_dir/family_done.txt"
}

launch_family() {
  local family="$1"
  local pidfile pid stdout_path
  pidfile="$PID_DIR/$family.pid"
  stdout_path="$LAUNCHER_STDOUT_DIR/${family}.out"

  if [[ -f "$pidfile" ]]; then
    pid="$(cat "$pidfile")"
    if is_running_pid "$pid"; then
      echo "$family already running (pid $pid)"
      return 0
    fi
  fi

  nohup "$SCRIPT_PATH" run "$family" > "$stdout_path" 2>&1 &
  pid=$!
  echo "$pid" > "$pidfile"
  echo "$family launched (pid $pid)"
}

show_status() {
  local family pidfile pid run_dir status_file
  for family in "${families[@]}"; do
    pidfile="$PID_DIR/$family.pid"
    run_dir="$(family_run_dir "$family")"
    status_file="$run_dir/task_status.csv"

    echo "[$family]"
    if [[ -f "$pidfile" ]]; then
      pid="$(cat "$pidfile")"
      if is_running_pid "$pid"; then
        echo "  state: running"
        echo "  pid: $pid"
      else
        echo "  state: stopped"
        echo "  pid: $pid"
      fi
    else
      echo "  state: not_launched"
    fi

    if [[ -f "$status_file" ]]; then
      echo "  recent:"
      tail -n 5 "$status_file" | sed 's/^/    /'
    fi
    if [[ -f "$run_dir/family_done.txt" ]]; then
      echo "  completed_at: $(cat "$run_dir/family_done.txt")"
    fi
  done
}

case "${1:-}" in
  launch)
    for family in "${families[@]}"; do
      launch_family "$family"
    done
    ;;
  run)
    if [[ $# -lt 2 ]]; then
      usage
      exit 1
    fi
    run_family "$2"
    ;;
  status)
    show_status
    ;;
  *)
    usage
    exit 1
    ;;
esac
