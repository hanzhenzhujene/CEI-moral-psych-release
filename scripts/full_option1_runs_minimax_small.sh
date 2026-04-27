#!/usr/bin/env bash
# Historical launcher for the MiniMax small-model extension experiments.
# It preserves the original operational flow while remaining portable via env overrides.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
RUNNER="$ROOT/src/inspect/run.py"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"
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

RUN_ID="${RUN_ID:-2026-04-19-option1-minimax-small-hybrid}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
LAUNCHER_STDOUT_DIR="$RUN_BASE/launcher"

TEXT_MAX_CONNECTIONS="${TEXT_MAX_CONNECTIONS:-2}"
VISION_MAX_CONNECTIONS="${VISION_MAX_CONNECTIONS:-1}"
MINIMAX_TEXT_MODEL="${MINIMAX_TEXT_MODEL:-openrouter/minimax/minimax-m2.1}"
MINIMAX_VISION_MODEL="${MINIMAX_VISION_MODEL:-openrouter/minimax/minimax-01}"
MINIMAX_TEXT_NO_THINK="${MINIMAX_TEXT_NO_THINK:-0}"

UNIMORAL_DATA_DIR="${UNIMORAL_DATA_DIR:-$DATA_ROOT/unimoral}"
SMID_DATA_DIR="${SMID_DATA_DIR:-$DATA_ROOT/smid}"
DENEVIL_DATA_FILE="${DENEVIL_DATA_FILE:-$DATA_ROOT/denevil/data_hybrid.jsonl}"
CCD_BENCH_DATA_FILE="${CCD_BENCH_DATA_FILE:-$DATA_ROOT/ccd-bench/CCD-Bench.json}"
VALUEPRISM_RELEVANCE_FILE="${VALUEPRISM_RELEVANCE_FILE:-$DATA_ROOT/valueprism/relevance/relevance_test.csv}"
VALUEPRISM_VALENCE_FILE="${VALUEPRISM_VALENCE_FILE:-$DATA_ROOT/valueprism/valence/valence_test.csv}"

families=(
  minimax_text
  minimax_smid
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
  VENV_PYTHON=/absolute/path/to/.venv/bin/python
  DATA_ROOT=/absolute/path/to/data
  UNIMORAL_DATA_DIR=/absolute/path/to/unimoral
  SMID_DATA_DIR=/absolute/path/to/smid
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

family_model() {
  local family="$1"
  case "$family" in
    minimax_text)
      echo "$MINIMAX_TEXT_MODEL"
      ;;
    minimax_smid)
      echo "$MINIMAX_VISION_MODEL"
      ;;
    *)
      return 1
      ;;
  esac
}

family_reasoning_effort() {
  local family="$1"
  case "$family" in
    minimax_text)
      if [[ "$MINIMAX_TEXT_NO_THINK" == "1" ]]; then
        echo "none"
      else
        echo ""
      fi
      ;;
    *)
      echo ""
      ;;
  esac
}

family_model_args() {
  local family="$1"
  case "$family" in
    minimax_text)
      if [[ "$MINIMAX_TEXT_NO_THINK" == "1" ]]; then
        echo "reasoning_enabled=False"
      else
        echo ""
      fi
      ;;
    *)
      echo ""
      ;;
  esac
}

family_extra_body_json() {
  local family="$1"
  case "$family" in
    minimax_text)
      if [[ "$MINIMAX_TEXT_NO_THINK" == "1" ]]; then
        echo '{"chat_template_kwargs":{"enable_thinking":false}}'
      else
        echo ""
      fi
      ;;
    *)
      echo ""
      ;;
  esac
}

family_prompt_prefix() {
  local family="$1"
  case "$family" in
    minimax_text)
      if [[ "$MINIMAX_TEXT_NO_THINK" == "1" ]]; then
        echo "/no_think"
      else
        echo ""
      fi
      ;;
    *)
      echo ""
      ;;
  esac
}

family_min_max_tokens() {
  local family="$1"
  case "$family" in
    minimax_text)
      if [[ "$MINIMAX_TEXT_NO_THINK" == "1" ]]; then
        echo "128"
      else
        echo ""
      fi
      ;;
    *)
      echo ""
      ;;
  esac
}

is_running_pid() {
  local pid="$1"
  [[ -n "$pid" ]] || return 1
  python3 - "$pid" <<'PY'
from __future__ import annotations

import os
import sys

pid = int(sys.argv[1])
try:
    os.kill(pid, 0)
except ProcessLookupError:
    raise SystemExit(1)
except PermissionError:
    # The sandbox can deny kill(0) for live sibling processes. Treat EPERM as
    # a live process so keepalive logic doesn't fan out duplicate reruns.
    raise SystemExit(0)
except OSError:
    raise SystemExit(1)
else:
    raise SystemExit(0)
PY
}

find_live_family_pid() {
  local family="$1"
  local pidfile pid model
  pidfile="$PID_DIR/$family.pid"

  if [[ -f "$pidfile" ]]; then
    pid="$(cat "$pidfile")"
    if [[ -n "$pid" ]] && is_running_pid "$pid"; then
      echo "$pid"
      return 0
    fi
  fi

  model="$(family_model "$family" 2>/dev/null || true)"
  [[ -z "$model" ]] && return 0
  pgrep -f "src/inspect/run.py.*${model}" 2>/dev/null | head -n 1 || true
}

require_dir() {
  local var_name="$1"
  local path="${!var_name}"
  if [[ ! -d "$path" ]]; then
    echo "Missing directory for $var_name: $path" >&2
    exit 1
  fi
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
  local task_name="$2"
  local task_spec="$3"
  local model="$4"
  local max_connections="$5"

  local run_dir output_path log_dir start_at end_at rc reasoning_effort model_args extra_body_json prompt_prefix min_max_tokens
  run_dir="$(family_run_dir "$family")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$family"
  mkdir -p "$run_dir" "$log_dir"
  reasoning_effort="$(family_reasoning_effort "$family")"
  model_args="$(family_model_args "$family")"
  extra_body_json="$(family_extra_body_json "$family")"
  prompt_prefix="$(family_prompt_prefix "$family")"
  min_max_tokens="$(family_min_max_tokens "$family")"

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START family=$family task=$task_name model=$model max_connections=$max_connections reasoning_effort=${reasoning_effort:-default} model_args=${model_args:-default} extra_body_json=${extra_body_json:-default} prompt_prefix=${prompt_prefix:-default} min_max_tokens=${min_max_tokens:-default}"
    export PYTHONUNBUFFERED=1
    if [[ -n "$min_max_tokens" ]]; then
      export CEI_MIN_MAX_TOKENS="$min_max_tokens"
    else
      unset CEI_MIN_MAX_TOKENS || true
    fi
    if [[ -n "$prompt_prefix" ]]; then
      export CEI_PROMPT_PREFIX="$prompt_prefix"
    else
      unset CEI_PROMPT_PREFIX || true
    fi
    "${RUN_PREFIX[@]}" "$RUNNER" \
      --tasks "$task_spec" \
      --model "$model" \
      --temperature 0 \
      --no_sandbox \
      --max_connections "$max_connections" \
      --log_dir "$log_dir" \
      ${model_args:+--model_args "$model_args"} \
      ${extra_body_json:+--extra_body_json "$extra_body_json"} \
      ${reasoning_effort:+--reasoning_effort "$reasoning_effort"}
    rc=$?
    end_at="$(now_iso)"
    echo "[$end_at] END family=$family task=$task_name returncode=$rc"
    exit "$rc"
  ) > "$output_path" 2>&1; then
    rc=0
  else
    rc=$?
  fi

  end_at="$(now_iso)"
  record_status "$family" "$task_name" "$start_at" "$end_at" "$rc" "$output_path"
  return 0
}

run_family() {
  local family="$1"
  local run_dir existing_pid
  run_dir="$(family_run_dir "$family")"
  mkdir -p "$run_dir"

  existing_pid="$(find_live_family_pid "$family" || true)"
  if [[ -n "$existing_pid" && "$existing_pid" != "$$" ]]; then
    echo "[$(now_iso)] SKIP family=$family reason=already_running pid=$existing_pid"
    return 0
  fi

  case "$family" in
    minimax_text)
      require_dir UNIMORAL_DATA_DIR
      require_file CCD_BENCH_DATA_FILE
      require_file DENEVIL_DATA_FILE
      require_file VALUEPRISM_RELEVANCE_FILE
      require_file VALUEPRISM_VALENCE_FILE
      export UNIMORAL_DATA_DIR="$UNIMORAL_DATA_DIR"
      export CCD_BENCH_DATA_FILE="$CCD_BENCH_DATA_FILE"
      export DENEVIL_DATA_FILE="$DENEVIL_DATA_FILE"
      export UNIMORAL_LANGUAGE=all
      export UNIMORAL_MODE=np
      export VALUEPRISM_RELEVANCE_FILE="$VALUEPRISM_RELEVANCE_FILE"
      export VALUEPRISM_VALENCE_FILE="$VALUEPRISM_VALENCE_FILE"
      run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "denevil_fulcra_proxy_generation" "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" "$MINIMAX_TEXT_MODEL" 2
      ;;
    minimax_smid)
      require_dir SMID_DATA_DIR
      export SMID_DATA_DIR="$SMID_DATA_DIR"
      run_task "$family" "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating" "$MINIMAX_VISION_MODEL" "$VISION_MAX_CONNECTIONS"
      run_task "$family" "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification" "$MINIMAX_VISION_MODEL" "$VISION_MAX_CONNECTIONS"
      ;;
    *)
      echo "Unknown family: $family" >&2
      return 1
      ;;
  esac

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
  local family pidfile pid run_dir status_file live_pid
  for family in "${families[@]}"; do
    pidfile="$PID_DIR/$family.pid"
    run_dir="$(family_run_dir "$family")"
    status_file="$run_dir/task_status.csv"

    echo "[$family]"
    live_pid="$(find_live_family_pid "$family")"
    if [[ -n "$live_pid" ]]; then
      echo "  state: running"
      echo "  pid: $live_pid"
    elif [[ -f "$pidfile" ]]; then
      pid="$(cat "$pidfile")"
      echo "  state: stopped"
      echo "  pid: $pid"
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
