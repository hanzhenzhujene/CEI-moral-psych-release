#!/usr/bin/env bash
# Controlled recovery launcher for the Qwen-L SMID route. This pins the rerun to
# the multi-provider qwen2.5-vl-72b route and avoids the earlier Alibaba-backed
# qwen3-vl-32b moderation failure.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

RUN_ID="${RUN_ID:-2026-04-20-qwen-large-smid-recovery}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
SMID_DATA_DIR="${SMID_DATA_DIR:-$DATA_ROOT/smid}"
MODEL="${MODEL:-openrouter/qwen/qwen2.5-vl-72b-instruct}"
PROVIDER_ARGS_JSON="${PROVIDER_ARGS_JSON:-{\"provider\":{\"only\":[\"nebius\",\"novita\",\"parasail\"],\"allow_fallbacks\":true}}}"
SMOKE_LIMIT="${SMOKE_LIMIT:-25}"

mkdir -p "$RUN_BASE" "$LOG_BASE"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") smoke
  $(basename "$0") run
  $(basename "$0") status

Environment overrides:
  UV_BIN=/absolute/path/to/uv
  VENV_PYTHON=/absolute/path/to/.venv/bin/python
  DATA_ROOT=/absolute/path/to/data
  SMID_DATA_DIR=/absolute/path/to/smid
  RUN_ID=custom-run-id
  MODEL=openrouter/qwen/qwen2.5-vl-72b-instruct
  PROVIDER_ARGS_JSON='{"provider":{"only":["nebius","novita","parasail"],"allow_fallbacks":true}}'
  SMOKE_LIMIT=25
EOF
}

now_iso() {
  python3 - <<'PY'
from datetime import datetime
print(datetime.now().astimezone().isoformat())
PY
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
  local limit_args=()
  local cmd=()
  local output_path="$RUN_BASE/${task_name}.txt"
  local start_at end_at rc

  if [[ $# -ge 3 && -n "${3:-}" ]]; then
    limit_args=(--limit "$3")
  fi

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START task=$task_name model=$MODEL max_connections=1 model_args_json=$PROVIDER_ARGS_JSON"
    cmd=(
      "${RUN_PREFIX[@]}" "$RUNNER"
      --tasks "$task_spec"
      --model "$MODEL"
      --model_args_json "$PROVIDER_ARGS_JSON"
      --temperature 0
      --no_sandbox
      --max_connections 1
      --log_dir "$LOG_BASE"
    )
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
  return 0
}

run_smoke() {
  require_dir SMID_DATA_DIR
  export SMID_DATA_DIR="$SMID_DATA_DIR"
  run_task "smid_moral_rating_smoke" "src/inspect/evals/smid.py::smid_moral_rating" "$SMOKE_LIMIT"
  run_task "smid_foundation_classification_smoke" "src/inspect/evals/smid.py::smid_foundation_classification" "$SMOKE_LIMIT"
}

run_full() {
  require_dir SMID_DATA_DIR
  export SMID_DATA_DIR="$SMID_DATA_DIR"
  run_task "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating"
  run_task "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification"
}

show_status() {
  local status_file="$RUN_BASE/task_status.csv"
  if [[ -f "$status_file" ]]; then
    tail -n 10 "$status_file"
  else
    echo "state: not_started"
  fi
}

case "${1:-}" in
  smoke)
    run_smoke
    ;;
  run)
    run_full
    ;;
  status)
    show_status
    ;;
  *)
    usage
    ;;
esac
