#!/usr/bin/env bash
# Sequential launcher for the non-image family-by-size expansion matrix.
# Jobs run in a fixed execution order so monitoring stays predictable.

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

RUN_ID="${RUN_ID:-2026-04-19-family-size-text-expansion}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
LAUNCHER_STDOUT_DIR="$RUN_BASE/launcher"
MASTER_PIDFILE="$PID_DIR/master.pid"
CURRENT_JOB_FILE="$RUN_BASE/current_job.txt"
MASTER_STATUS_FILE="$RUN_BASE/master_status.txt"

UNIMORAL_DATA_DIR="${UNIMORAL_DATA_DIR:-$DATA_ROOT/unimoral}"
DENEVIL_DATA_FILE="${DENEVIL_DATA_FILE:-$DATA_ROOT/denevil/data_hybrid.jsonl}"
CCD_BENCH_DATA_FILE="${CCD_BENCH_DATA_FILE:-$DATA_ROOT/ccd-bench/CCD-Bench.json}"
VALUEPRISM_RELEVANCE_FILE="${VALUEPRISM_RELEVANCE_FILE:-$DATA_ROOT/valueprism/relevance/relevance_test.csv}"
VALUEPRISM_VALENCE_FILE="${VALUEPRISM_VALENCE_FILE:-$DATA_ROOT/valueprism/valence/valence_test.csv}"

# Cheapest-first rough order based on current OpenRouter pricing and the observed
# token profile of the completed non-image Llama line.
jobs=(
  gemma_27b_large
  gemma_12b_medium
  qwen_14b_medium
  qwen_32b_large
  llama_70b_medium
  llama_4_maverick_large
  minimax_m2_5_medium
  deepseek_r1_qwen_32b_medium
  minimax_m2_7_large
)

mkdir -p "$RUN_BASE" "$LOG_BASE" "$PID_DIR" "$LAUNCHER_STDOUT_DIR"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") launch
  $(basename "$0") run-all
  $(basename "$0") run <job>
  $(basename "$0") status

Jobs:
  ${jobs[*]}

Optional overrides:
  UV_BIN=/absolute/path/to/uv
  VENV_PYTHON=/absolute/path/to/.venv/bin/python
  DATA_ROOT=/absolute/path/to/data
  RUN_ID=custom-run-id
  JOB_FILTER=comma,separated,job_names
  SKIP_COMPLETED=1
EOF
}

now_iso() {
  python3 - <<'PY'
from datetime import datetime
print(datetime.now().astimezone().isoformat())
PY
}

job_run_dir() {
  local job="$1"
  echo "$RUN_BASE/$job"
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
  local job="$1"
  local task_name="$2"
  local start_at="$3"
  local end_at="$4"
  local returncode="$5"
  local output_path="$6"
  local status_file
  status_file="$(job_run_dir "$job")/task_status.csv"
  if [[ ! -f "$status_file" ]]; then
    echo "task_name,start_at,end_at,returncode,output_path" > "$status_file"
  fi
  echo "$task_name,$start_at,$end_at,$returncode,$output_path" >> "$status_file"
}

job_model() {
  local job="$1"
  case "$job" in
    gemma_27b_large) echo "openrouter/google/gemma-3-27b-it" ;;
    gemma_12b_medium) echo "openrouter/google/gemma-3-12b-it" ;;
    qwen_14b_medium) echo "openrouter/qwen/qwen3-14b" ;;
    qwen_32b_large) echo "openrouter/qwen/qwen3-32b" ;;
    llama_70b_medium) echo "openrouter/meta-llama/llama-3.3-70b-instruct" ;;
    llama_4_maverick_large) echo "openrouter/meta-llama/llama-4-maverick" ;;
    minimax_m2_5_medium) echo "openrouter/minimax/minimax-m2.5" ;;
    deepseek_r1_qwen_32b_medium) echo "openrouter/deepseek/deepseek-r1-distill-qwen-32b" ;;
    minimax_m2_7_large) echo "openrouter/minimax/minimax-m2.7" ;;
    *)
      echo "Unknown job for model lookup: $job" >&2
      return 1
      ;;
  esac
}

job_max_connections() {
  local job="$1"
  case "$job" in
    gemma_27b_large|gemma_12b_medium|qwen_14b_medium|qwen_32b_large|llama_70b_medium)
      echo 2
      ;;
    *)
      echo 1
      ;;
  esac
}

run_task() {
  local job="$1"
  local task_name="$2"
  local task_spec="$3"
  local model="$4"
  local max_connections="$5"

  local run_dir output_path log_dir start_at end_at rc
  run_dir="$(job_run_dir "$job")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$job"
  mkdir -p "$run_dir" "$log_dir"

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START job=$job task=$task_name model=$model max_connections=$max_connections"
    "${RUN_PREFIX[@]}" "$RUNNER" \
      --tasks "$task_spec" \
      --model "$model" \
      --temperature 0 \
      --no_sandbox \
      --max_connections "$max_connections" \
      --log_dir "$log_dir"
    rc=$?
    end_at="$(now_iso)"
    echo "[$end_at] END job=$job task=$task_name returncode=$rc"
    exit "$rc"
  ) > "$output_path" 2>&1; then
    rc=0
  else
    rc=$?
  fi

  end_at="$(now_iso)"
  record_status "$job" "$task_name" "$start_at" "$end_at" "$rc" "$output_path"
  return 0
}

run_job() {
  local job="$1"
  local run_dir model max_connections
  run_dir="$(job_run_dir "$job")"
  mkdir -p "$run_dir"

  if [[ "${SKIP_COMPLETED:-0}" == "1" && -f "$run_dir/job_done.txt" ]]; then
    echo "[$(now_iso)] SKIP job=$job reason=already_completed"
    return 0
  fi

  model="$(job_model "$job")"
  max_connections="$(job_max_connections "$job")"

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

  echo "$job" > "$CURRENT_JOB_FILE"
  echo "running:$job:$(now_iso)" > "$MASTER_STATUS_FILE"

  run_task "$job" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$model" "$max_connections"
  run_task "$job" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$model" "$max_connections"
  run_task "$job" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$model" "$max_connections"
  run_task "$job" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$model" "$max_connections"
  run_task "$job" "denevil_fulcra_proxy_generation" "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" "$model" 1

  now_iso > "$run_dir/job_done.txt"
}

selected_jobs() {
  if [[ -z "${JOB_FILTER:-}" ]]; then
    printf '%s\n' "${jobs[@]}"
    return 0
  fi

  python3 - "$JOB_FILTER" "${jobs[@]}" <<'PY'
import sys
requested = [part.strip() for part in sys.argv[1].split(",") if part.strip()]
allowed = sys.argv[2:]
allowed_set = set(allowed)
for name in requested:
    if name not in allowed_set:
        raise SystemExit(f"Unknown job in JOB_FILTER: {name}")
    print(name)
PY
}

run_all() {
  local job
  while IFS= read -r job; do
    [[ -z "$job" ]] && continue
    run_job "$job"
  done < <(selected_jobs)

  rm -f "$CURRENT_JOB_FILE"
  echo "completed:$(now_iso)" > "$MASTER_STATUS_FILE"
}

launch_master() {
  local pid stdout_path
  stdout_path="$LAUNCHER_STDOUT_DIR/master.out"

  if [[ -f "$MASTER_PIDFILE" ]]; then
    pid="$(cat "$MASTER_PIDFILE")"
    if is_running_pid "$pid"; then
      echo "master already running (pid $pid)"
      return 0
    fi
  fi

  nohup "$SCRIPT_PATH" run-all > "$stdout_path" 2>&1 &
  pid=$!
  echo "$pid" > "$MASTER_PIDFILE"
  echo "master launched (pid $pid)"
}

show_status() {
  local pid job run_dir status_file
  echo "[master]"
  if [[ -f "$MASTER_PIDFILE" ]]; then
    pid="$(cat "$MASTER_PIDFILE")"
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
  if [[ -f "$MASTER_STATUS_FILE" ]]; then
    echo "  status: $(cat "$MASTER_STATUS_FILE")"
  fi
  if [[ -f "$CURRENT_JOB_FILE" ]]; then
    echo "  current_job: $(cat "$CURRENT_JOB_FILE")"
  fi

  while IFS= read -r job; do
    [[ -z "$job" ]] && continue
    run_dir="$(job_run_dir "$job")"
    status_file="$run_dir/task_status.csv"
    echo "[$job]"
    if [[ -f "$status_file" ]]; then
      echo "  recent:"
      tail -n 5 "$status_file" | sed 's/^/    /'
    else
      echo "  recent: none"
    fi
    if [[ -f "$run_dir/job_done.txt" ]]; then
      echo "  completed_at: $(cat "$run_dir/job_done.txt")"
    fi
  done < <(selected_jobs)
}

case "${1:-}" in
  launch)
    launch_master
    ;;
  run-all)
    run_all
    ;;
  run)
    if [[ $# -lt 2 ]]; then
      usage
      exit 1
    fi
    run_job "$2"
    ;;
  status)
    show_status
    ;;
  *)
    usage
    ;;
esac
