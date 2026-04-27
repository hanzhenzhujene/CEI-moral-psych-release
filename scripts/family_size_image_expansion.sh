#!/usr/bin/env bash
# Sequential launcher for the image-only family-by-size expansion. Jobs follow a
# fixed order using only routes with a clean medium or large vision-capable
# mapping.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
RUNNER="$ROOT/src/inspect/run.py"
UV_BIN="${UV_BIN:-$(command -v uv 2>/dev/null || true)}"
VENV_PYTHON="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"

if [[ -n "${UV_BIN}" ]] && { [[ -x "${UV_BIN}" ]] || command -v "${UV_BIN}" >/dev/null 2>&1; }; then
  RUN_PREFIX=("${UV_BIN}" "run" "--package" "cei-inspect" "python")
elif [[ -x "${VENV_PYTHON}" ]]; then
  RUN_PREFIX=("${VENV_PYTHON}")
else
  echo "Could not resolve either uv or $VENV_PYTHON. Set UV_BIN or VENV_PYTHON before running $(basename "$0")." >&2
  exit 1
fi

RUN_ID="${RUN_ID:-2026-04-19-family-size-image-expansion}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
MASTER_PIDFILE="$PID_DIR/master.pid"
CURRENT_JOB_FILE="$RUN_BASE/current_job.txt"
MASTER_STATUS_FILE="$RUN_BASE/master_status.txt"
SMID_DATA_DIR="${SMID_DATA_DIR:-$DATA_ROOT/smid}"

jobs=(
  gemma_27b_large_smid
  gemma_12b_medium_smid
  qwen_32b_large_smid
  llama_4_maverick_large_smid
)

mkdir -p "$RUN_BASE" "$LOG_BASE" "$PID_DIR"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") run <job>
  $(basename "$0") status

Jobs:
  ${jobs[*]}

Optional overrides:
  UV_BIN=/absolute/path/to/uv
  VENV_PYTHON=/absolute/path/to/.venv/bin/python
  DATA_ROOT=/absolute/path/to/data
  SMID_DATA_DIR=/absolute/path/to/smid
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

require_dir() {
  local var_name="$1"
  local path="${!var_name}"
  if [[ ! -d "$path" ]]; then
    echo "Missing directory for $var_name: $path" >&2
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
    gemma_27b_large_smid) echo "openrouter/google/gemma-3-27b-it" ;;
    gemma_12b_medium_smid) echo "openrouter/google/gemma-3-12b-it" ;;
    qwen_32b_large_smid) echo "openrouter/qwen/qwen3-vl-32b-instruct" ;;
    llama_4_maverick_large_smid) echo "openrouter/meta-llama/llama-4-maverick" ;;
    *)
      echo "Unknown job for model lookup: $job" >&2
      return 1
      ;;
  esac
}

run_task() {
  local job="$1"
  local task_name="$2"
  local task_spec="$3"
  local model="$4"

  local run_dir output_path log_dir start_at end_at rc
  run_dir="$(job_run_dir "$job")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$job"
  mkdir -p "$run_dir" "$log_dir"

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START job=$job task=$task_name model=$model max_connections=1"
    "${RUN_PREFIX[@]}" "$RUNNER" \
      --tasks "$task_spec" \
      --model "$model" \
      --temperature 0 \
      --no_sandbox \
      --max_connections 1 \
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
  local run_dir model
  run_dir="$(job_run_dir "$job")"
  mkdir -p "$run_dir"

  require_dir SMID_DATA_DIR
  export SMID_DATA_DIR="$SMID_DATA_DIR"
  model="$(job_model "$job")"

  echo "$job" > "$CURRENT_JOB_FILE"
  echo "running:$job:$(now_iso)" > "$MASTER_STATUS_FILE"
  echo "$$" > "$MASTER_PIDFILE"

  run_task "$job" "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating" "$model"
  run_task "$job" "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification" "$model"

  now_iso > "$run_dir/job_done.txt"
  echo "completed:$job:$(now_iso)" > "$MASTER_STATUS_FILE"
}

show_status() {
  local job run_dir status_file
  if [[ -f "$CURRENT_JOB_FILE" ]]; then
    echo "current_job: $(cat "$CURRENT_JOB_FILE")"
  fi
  if [[ -f "$MASTER_STATUS_FILE" ]]; then
    echo "master_status: $(cat "$MASTER_STATUS_FILE")"
  fi
  for job in "${jobs[@]}"; do
    run_dir="$(job_run_dir "$job")"
    status_file="$run_dir/task_status.csv"
    echo "[$job]"
    if [[ -f "$status_file" ]]; then
      tail -n 5 "$status_file" | sed 's/^/  /'
    else
      echo "  state: not_started"
    fi
    if [[ -f "$run_dir/job_done.txt" ]]; then
      echo "  completed_at: $(cat "$run_dir/job_done.txt")"
    fi
  done
}

case "${1:-}" in
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
