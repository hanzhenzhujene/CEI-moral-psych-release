#!/usr/bin/env bash
# Historical launcher for the original closed Option 1 sweep.
# It is retained for provenance and recovery, while public regeneration now flows through `make release`.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/src/inspect/run.py"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"
UV_BIN="${UV_BIN:-$(command -v uv 2>/dev/null || true)}"

if [[ -z "${UV_BIN}" ]] || { [[ ! -x "${UV_BIN}" ]] && ! command -v "${UV_BIN}" >/dev/null 2>&1; }; then
  echo "Could not resolve uv. Set UV_BIN=/absolute/path/to/uv before running $(basename "$0")." >&2
  exit 1
fi

RUN_ID="${RUN_ID:-2026-04-17-option1-full}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
LAUNCHER_STDOUT_DIR="$RUN_BASE/launcher"

TEXT_MAX_CONNECTIONS="${TEXT_MAX_CONNECTIONS:-8}"
VISION_MAX_CONNECTIONS="${VISION_MAX_CONNECTIONS:-2}"
GEMMA_TEXT_MODEL="${GEMMA_TEXT_MODEL:-openrouter/google/gemma-3-4b-it:free}"
GEMMA_VISION_MODEL="${GEMMA_VISION_MODEL:-openrouter/google/gemma-3-4b-it:free}"

UNIMORAL_DATA_DIR="${UNIMORAL_DATA_DIR:-$DATA_ROOT/unimoral}"
SMID_DATA_DIR="${SMID_DATA_DIR:-$DATA_ROOT/smid}"
CCD_BENCH_DATA_FILE="${CCD_BENCH_DATA_FILE:-$DATA_ROOT/ccd-bench/CCD-Bench.json}"
VALUEPRISM_RELEVANCE_FILE="${VALUEPRISM_RELEVANCE_FILE:-$DATA_ROOT/valueprism/relevance/relevance_test.csv}"
VALUEPRISM_VALENCE_FILE="${VALUEPRISM_VALENCE_FILE:-$DATA_ROOT/valueprism/valence/valence_test.csv}"

families=(
  qwen_text
  deepseek_text
  gemma_text
  qwen_smid
  gemma_smid
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
  UNIMORAL_DATA_DIR=/absolute/path/to/unimoral
  SMID_DATA_DIR=/absolute/path/to/smid
  CCD_BENCH_DATA_FILE=/absolute/path/to/CCD-Bench.json
  VALUEPRISM_RELEVANCE_FILE=/absolute/path/to/relevance.csv
  VALUEPRISM_VALENCE_FILE=/absolute/path/to/valence.csv
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

  local run_dir output_path log_dir start_at end_at rc
  run_dir="$(family_run_dir "$family")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$family"
  mkdir -p "$run_dir" "$log_dir"

  start_at="$(now_iso)"
  (
    echo "[$start_at] START family=$family task=$task_name model=$model max_connections=$max_connections"
    "$UV_BIN" run --package cei-inspect python "$RUNNER" \
      --tasks "$task_spec" \
      --model "$model" \
      --temperature 0 \
      --no_sandbox \
      --max_connections "$max_connections" \
      --log_dir "$log_dir"
    rc=$?
    end_at="$(now_iso)"
    echo "[$end_at] END family=$family task=$task_name returncode=$rc"
    exit "$rc"
  ) > "$output_path" 2>&1

  rc=$?
  end_at="$(now_iso)"
  record_status "$family" "$task_name" "$start_at" "$end_at" "$rc" "$output_path"
  return 0
}

run_family() {
  local family="$1"
  local run_dir
  run_dir="$(family_run_dir "$family")"
  mkdir -p "$run_dir"

  case "$family" in
    qwen_text)
      require_dir UNIMORAL_DATA_DIR
      require_file CCD_BENCH_DATA_FILE
      require_file VALUEPRISM_RELEVANCE_FILE
      require_file VALUEPRISM_VALENCE_FILE
      export UNIMORAL_DATA_DIR="$UNIMORAL_DATA_DIR"
      export CCD_BENCH_DATA_FILE="$CCD_BENCH_DATA_FILE"
      export UNIMORAL_LANGUAGE=all
      export UNIMORAL_MODE=np
      export VALUEPRISM_RELEVANCE_FILE="$VALUEPRISM_RELEVANCE_FILE"
      export VALUEPRISM_VALENCE_FILE="$VALUEPRISM_VALENCE_FILE"
      run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "openrouter/qwen/qwen3-8b" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "openrouter/qwen/qwen3-8b" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "openrouter/qwen/qwen3-8b" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "openrouter/qwen/qwen3-8b" "$TEXT_MAX_CONNECTIONS"
      ;;
    deepseek_text)
      require_dir UNIMORAL_DATA_DIR
      require_file CCD_BENCH_DATA_FILE
      require_file VALUEPRISM_RELEVANCE_FILE
      require_file VALUEPRISM_VALENCE_FILE
      export UNIMORAL_DATA_DIR="$UNIMORAL_DATA_DIR"
      export CCD_BENCH_DATA_FILE="$CCD_BENCH_DATA_FILE"
      export UNIMORAL_LANGUAGE=all
      export UNIMORAL_MODE=np
      export VALUEPRISM_RELEVANCE_FILE="$VALUEPRISM_RELEVANCE_FILE"
      export VALUEPRISM_VALENCE_FILE="$VALUEPRISM_VALENCE_FILE"
      run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "openrouter/deepseek/deepseek-chat-v3.1" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "openrouter/deepseek/deepseek-chat-v3.1" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "openrouter/deepseek/deepseek-chat-v3.1" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "openrouter/deepseek/deepseek-chat-v3.1" "$TEXT_MAX_CONNECTIONS"
      ;;
    gemma_text)
      require_dir UNIMORAL_DATA_DIR
      require_file CCD_BENCH_DATA_FILE
      require_file VALUEPRISM_RELEVANCE_FILE
      require_file VALUEPRISM_VALENCE_FILE
      export UNIMORAL_DATA_DIR="$UNIMORAL_DATA_DIR"
      export CCD_BENCH_DATA_FILE="$CCD_BENCH_DATA_FILE"
      export UNIMORAL_LANGUAGE=all
      export UNIMORAL_MODE=np
      export VALUEPRISM_RELEVANCE_FILE="$VALUEPRISM_RELEVANCE_FILE"
      export VALUEPRISM_VALENCE_FILE="$VALUEPRISM_VALENCE_FILE"
      run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$GEMMA_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$GEMMA_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$GEMMA_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$GEMMA_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS"
      ;;
    qwen_smid)
      require_dir SMID_DATA_DIR
      export SMID_DATA_DIR="$SMID_DATA_DIR"
      run_task "$family" "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating" "openrouter/qwen/qwen3-vl-8b-instruct" "$VISION_MAX_CONNECTIONS"
      run_task "$family" "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification" "openrouter/qwen/qwen3-vl-8b-instruct" "$VISION_MAX_CONNECTIONS"
      ;;
    gemma_smid)
      require_dir SMID_DATA_DIR
      export SMID_DATA_DIR="$SMID_DATA_DIR"
      run_task "$family" "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating" "$GEMMA_VISION_MODEL" "$VISION_MAX_CONNECTIONS"
      run_task "$family" "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification" "$GEMMA_VISION_MODEL" "$VISION_MAX_CONNECTIONS"
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

  nohup "$0" run "$family" > "$stdout_path" 2>&1 &
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
