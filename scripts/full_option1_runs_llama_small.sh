#!/usr/bin/env bash
# Historical launcher for the Llama small-model extension experiments.
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

RUN_ID="${RUN_ID:-2026-04-19-option1-llama32-11b-vision}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
LAUNCHER_STDOUT_DIR="$RUN_BASE/launcher"

TEXT_MAX_CONNECTIONS="${TEXT_MAX_CONNECTIONS:-4}"
VISION_MAX_CONNECTIONS="${VISION_MAX_CONNECTIONS:-1}"
LLAMA_MODEL="${LLAMA_MODEL:-openrouter/meta-llama/llama-3.2-11b-vision-instruct}"
TASK_FILTER="${TASK_FILTER:-}"

UNIMORAL_DATA_DIR="${UNIMORAL_DATA_DIR:-$DATA_ROOT/unimoral}"
SMID_DATA_DIR="${SMID_DATA_DIR:-$DATA_ROOT/smid}"
DENEVIL_DATA_FILE="${DENEVIL_DATA_FILE:-$DATA_ROOT/denevil/data_hybrid.jsonl}"
CCD_BENCH_DATA_FILE="${CCD_BENCH_DATA_FILE:-$DATA_ROOT/ccd-bench/CCD-Bench.json}"
VALUEPRISM_RELEVANCE_FILE="${VALUEPRISM_RELEVANCE_FILE:-$DATA_ROOT/valueprism/relevance/relevance_test.csv}"
VALUEPRISM_VALENCE_FILE="${VALUEPRISM_VALENCE_FILE:-$DATA_ROOT/valueprism/valence/valence_test.csv}"

families=(
  llama_text
  llama_smid
  llama_proxy
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
  DENEVIL_DATA_FILE=/absolute/path/to/fulcra_proxy.jsonl
  TASK_FILTER=task_a,task_b
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

task_is_selected() {
  local task_name="$1"
  local candidate
  if [[ -z "$TASK_FILTER" ]]; then
    return 0
  fi

  IFS=',' read -r -a selected_tasks <<< "$TASK_FILTER"
  for candidate in "${selected_tasks[@]}"; do
    if [[ "$candidate" == "$task_name" ]]; then
      return 0
    fi
  done
  return 1
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
  local max_connections="$4"

  local run_dir output_path log_dir start_at end_at rc
  run_dir="$(family_run_dir "$family")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$family"
  mkdir -p "$run_dir" "$log_dir"

  if ! task_is_selected "$task_name"; then
    printf '[%s] SKIP family=%s task=%s reason=task_filter=%s\n' "$(now_iso)" "$family" "$task_name" "$TASK_FILTER" > "$output_path"
    return 0
  fi

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START family=$family task=$task_name model=$LLAMA_MODEL max_connections=$max_connections"
    "$UV_BIN" run --package cei-inspect python "$RUNNER" \
      --tasks "$task_spec" \
      --model "$LLAMA_MODEL" \
      --temperature 0 \
      --no_sandbox \
      --max_connections "$max_connections" \
      --log_dir "$log_dir"
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
  local run_dir
  run_dir="$(family_run_dir "$family")"
  mkdir -p "$run_dir"

  case "$family" in
    llama_text)
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
      run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$TEXT_MAX_CONNECTIONS"
      run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$TEXT_MAX_CONNECTIONS"
      ;;
    llama_smid)
      require_dir SMID_DATA_DIR
      export SMID_DATA_DIR="$SMID_DATA_DIR"
      run_task "$family" "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating" "$VISION_MAX_CONNECTIONS"
      run_task "$family" "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification" "$VISION_MAX_CONNECTIONS"
      ;;
    llama_proxy)
      require_file DENEVIL_DATA_FILE
      export DENEVIL_DATA_FILE="$DENEVIL_DATA_FILE"
      run_task "$family" "denevil_fulcra_proxy_generation" "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" 2
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
