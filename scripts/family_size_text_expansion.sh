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
MINIMAX_TEXT_NO_THINK="${MINIMAX_TEXT_NO_THINK:-0}"

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

latest_eval_file() {
  local job="$1"
  local log_dir="$LOG_BASE/$job"
  ls -1t "$log_dir"/*.eval 2>/dev/null | head -n 1 || true
}

latest_eval_file_in_dir() {
  local log_dir="$1"
  ls -1t "$log_dir"/*.eval 2>/dev/null | head -n 1 || true
}

show_live_eval_progress_from_log_dir() {
  local log_dir="$1"
  local eval_path
  eval_path="$(latest_eval_file_in_dir "$log_dir")"
  [[ -z "$eval_path" ]] && return 0

  python3 - "$eval_path" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zipfile import BadZipFile, ZipFile

eval_path = Path(sys.argv[1])


def read_json(zf: ZipFile, member: str) -> dict | list | None:
    try:
        return json.loads(zf.read(member).decode("utf-8"))
    except KeyError:
        return None


try:
    with ZipFile(eval_path) as zf:
        names = zf.namelist()
        start = read_json(zf, "_journal/start.json") or {}
        header = read_json(zf, "header.json") or {}
        base = header or start
        meta = base.get("eval", {}) if isinstance(base, dict) else {}
        task = str(meta.get("task", eval_path.stem))
        model = str(meta.get("model", ""))
        total = int(meta.get("dataset", {}).get("samples", 0) or 0)
        completed = sum(1 for name in names if name.startswith("samples/") and name.endswith(".json"))
        updated_at = datetime.fromtimestamp(eval_path.stat().st_mtime).astimezone().isoformat()
        status = str(header.get("status", "running")) if header else "running"

        print(f"  live_eval: {eval_path.name}")
        print(f"  live_task: {task}")
        if model:
            print(f"  live_model: {model}")
        if total:
            progress_pct = completed / total * 100.0
            print(f"  persisted_progress: {completed}/{total} ({progress_pct:.1f}%)")
            chunk_size = total // 10
            if chunk_size and completed and completed % chunk_size == 0 and status == "running":
                print("  note: Inspect writes this archive in chunked flushes, so file updates can pause while requests keep running.")
        else:
            print(f"  persisted_samples: {completed}")
        print(f"  live_eval_updated_at: {updated_at}")

        if header and status != "success":
            error = header.get("error")
            if isinstance(error, dict) and error.get("message"):
                print(f"  live_error: {error['message']}")
except BadZipFile:
    print(f"  live_eval: {eval_path.name}")
    print("  note: eval archive is still being finalized")
PY
}

show_live_eval_progress() {
  local job="$1"
  show_live_eval_progress_from_log_dir "$LOG_BASE/$job"
}

job_run_dir() {
  local job="$1"
  echo "$RUN_BASE/$job"
}

job_pid_file() {
  local job="$1"
  echo "$(job_run_dir "$job")/worker.pid"
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
    # The sandbox can block direct signals to sibling workers even when the
    # process is still live, so EPERM counts as "running".
    raise SystemExit(0)
except OSError:
    raise SystemExit(1)
else:
    raise SystemExit(0)
PY
}

find_live_job_pid() {
  local job="$1"
  local pid_file pid model log_dir

  pid_file="$(job_pid_file "$job")"
  if [[ -f "$pid_file" ]]; then
    pid="$(cat "$pid_file")"
    if [[ -n "$pid" ]] && is_running_pid "$pid"; then
      echo "$pid"
      return 0
    fi
  fi

  model="$(job_model "$job")"
  log_dir="$LOG_BASE/$job"
  python3 - "$model" "$log_dir" <<'PY'
from __future__ import annotations

import subprocess
import sys

model = sys.argv[1]
log_dir = sys.argv[2]

try:
    completed = subprocess.run(
        ["ps", "-axo", "pid=,command="],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=2,
        check=False,
    )
except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
    raise SystemExit(1)

for raw in completed.stdout.splitlines():
    line = raw.strip()
    if not line or "src/inspect/run.py" not in line:
        continue
    if model not in line or log_dir not in line:
        continue
    pid, _, _ = line.partition(" ")
    if pid:
        print(pid)
        raise SystemExit(0)

raise SystemExit(1)
PY
  if [[ -d "$log_dir/_inspect_traces" ]]; then
    python3 - "$log_dir" <<'PY'
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

log_dir = Path(sys.argv[1])
trace_paths = sorted(
    (path for path in (log_dir / "_inspect_traces").glob("*.log") if path.is_file()),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)

for path in trace_paths:
    try:
        completed = subprocess.run(
            ["lsof", "-Fpc", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        continue

    current_pid = ""
    for raw in completed.stdout.splitlines():
        if not raw:
            continue
        tag, value = raw[0], raw[1:]
        if tag == "p":
            current_pid = value
        elif tag == "c" and current_pid and "python" in value.lower():
            print(current_pid)
            raise SystemExit(0)

raise SystemExit(1)
PY
  fi
}

find_live_job_process_any_run() {
  local job="$1"
  local model
  model="$(job_model "$job")"
  python3 - "$model" "$job" <<'PY'
from __future__ import annotations

import re
import subprocess
import sys

model = sys.argv[1]
job = sys.argv[2]
pattern = re.compile(r"--log_dir\s+(\S+/results/inspect/logs/([^/\s]+)/" + re.escape(job) + r")\b")

try:
    completed = subprocess.run(
        ["ps", "-axo", "pid=,command="],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=2,
        check=False,
    )
except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
    raise SystemExit(1)

for raw in completed.stdout.splitlines():
    line = raw.strip()
    if not line or "src/inspect/run.py" not in line or model not in line:
        continue
    match = re.match(r"(\d+)\s+(.*)", line)
    if not match:
        continue
    pid, command = match.groups()
    log_match = pattern.search(command)
    if not log_match:
        continue
    log_dir, run_id = log_match.groups()
    print(f"{pid}\t{run_id}\t{log_dir}")
    raise SystemExit(0)

raise SystemExit(1)
PY
  python3 - "$ROOT/results/inspect/logs" "$job" <<'PY'
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

logs_root = Path(sys.argv[1])
job = sys.argv[2]

trace_paths = sorted(
    (
        path
        for path in logs_root.glob(f"*/{job}/_inspect_traces/*.log")
        if path.is_file()
    ),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)

for path in trace_paths:
    try:
        completed = subprocess.run(
            ["lsof", "-Fpc", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        continue

    current_pid = ""
    for raw in completed.stdout.splitlines():
        if not raw:
            continue
        tag, value = raw[0], raw[1:]
        if tag == "p":
            current_pid = value
        elif tag == "c" and current_pid and "python" in value.lower():
            run_id = path.parents[2].name
            log_dir = path.parents[1]
            print(f"{current_pid}\t{run_id}\t{log_dir}")
            raise SystemExit(0)

raise SystemExit(1)
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

task_completed_successfully() {
  local job="$1"
  local task_name="$2"
  local status_file
  status_file="$(job_run_dir "$job")/task_status.csv"

  [[ -f "$status_file" ]] || return 1

  awk -F, -v task="$task_name" '
    $1 == task && $4 == 0 { found = 1 }
    END { exit found ? 0 : 1 }
  ' "$status_file"
}

run_or_skip_task() {
  local job="$1"
  local task_name="$2"
  local task_spec="$3"
  local model="$4"
  local max_connections="$5"

  if task_completed_successfully "$job" "$task_name"; then
    echo "[$(now_iso)] SKIP job=$job task=$task_name reason=already_completed"
    return 0
  fi

  run_task "$job" "$task_name" "$task_spec" "$model" "$max_connections"
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
    qwen_32b_large)
      echo "${QWEN_32B_LARGE_MAX_CONNECTIONS:-2}"
      ;;
    gemma_27b_large|gemma_12b_medium|qwen_14b_medium|llama_70b_medium)
      echo 2
      ;;
    *)
      echo 1
      ;;
  esac
}

job_reasoning_effort() {
  local job="$1"
  case "$job" in
    qwen_14b_medium|qwen_32b_large)
      echo "none"
      ;;
    minimax_m2_5_medium|minimax_m2_7_large)
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

job_model_args() {
  local job="$1"
  case "$job" in
    qwen_14b_medium|qwen_32b_large)
      echo "reasoning_enabled=False"
      ;;
    minimax_m2_5_medium|minimax_m2_7_large)
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

job_model_args_json() {
  local job="$1"
  case "$job" in
    llama_4_maverick_large)
      echo '{"provider":{"ignore":["novita"],"allow_fallbacks":true}}'
      ;;
    *)
      echo ""
      ;;
  esac
}

job_extra_body_json() {
  local job="$1"
  case "$job" in
    qwen_14b_medium|qwen_32b_large)
      echo '{"chat_template_kwargs":{"enable_thinking":false}}'
      ;;
    minimax_m2_5_medium|minimax_m2_7_large)
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

job_prompt_prefix() {
  local job="$1"
  case "$job" in
    qwen_14b_medium|qwen_32b_large)
      echo "/no_think"
      ;;
    minimax_m2_5_medium|minimax_m2_7_large)
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

job_min_max_tokens() {
  local job="$1"
  case "$job" in
    qwen_14b_medium|qwen_32b_large)
      echo "128"
      ;;
    minimax_m2_5_medium|minimax_m2_7_large)
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

run_task() {
  local job="$1"
  local task_name="$2"
  local task_spec="$3"
  local model="$4"
  local max_connections="$5"

  local run_dir output_path log_dir start_at end_at rc reasoning_effort model_args model_args_json extra_body_json prompt_prefix min_max_tokens
  run_dir="$(job_run_dir "$job")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$job"
  mkdir -p "$run_dir" "$log_dir"
  reasoning_effort="$(job_reasoning_effort "$job")"
  model_args="$(job_model_args "$job")"
  model_args_json="$(job_model_args_json "$job")"
  extra_body_json="$(job_extra_body_json "$job")"
  prompt_prefix="$(job_prompt_prefix "$job")"
  min_max_tokens="$(job_min_max_tokens "$job")"

  start_at="$(now_iso)"
  if (
    set +e
    echo "[$start_at] START job=$job task=$task_name model=$model max_connections=$max_connections reasoning_effort=${reasoning_effort:-default} model_args=${model_args:-default} model_args_json=${model_args_json:-default} extra_body_json=${extra_body_json:-default} prompt_prefix=${prompt_prefix:-default} min_max_tokens=${min_max_tokens:-default}"
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
      ${model_args_json:+--model_args_json "$model_args_json"} \
      ${extra_body_json:+--extra_body_json "$extra_body_json"} \
      ${reasoning_effort:+--reasoning_effort "$reasoning_effort"}
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
  return "$rc"
}

run_job() {
  local job="$1"
  local run_dir model max_connections worker_pid_file job_failed existing_worker_pid
  run_dir="$(job_run_dir "$job")"
  mkdir -p "$run_dir"
  worker_pid_file="$(job_pid_file "$job")"
  job_failed=0

  existing_worker_pid="$(find_live_job_pid "$job" || true)"
  if [[ -n "$existing_worker_pid" && "$existing_worker_pid" != "$$" ]]; then
    echo "[$(now_iso)] SKIP job=$job reason=already_running worker_pid=$existing_worker_pid"
    return 0
  fi

  echo "$$" > "$worker_pid_file"

  if [[ "${SKIP_COMPLETED:-0}" == "1" && -f "$run_dir/job_done.txt" ]]; then
    echo "[$(now_iso)] SKIP job=$job reason=already_completed"
    rm -f "$worker_pid_file"
    return 0
  fi

  # Clear stale terminal markers before a retry so monitoring does not report
  # a rerun as both "done" and "running" at the same time.
  rm -f "$run_dir/job_done.txt" "$run_dir/job_failed.txt"

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

  run_or_skip_task "$job" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$model" "$max_connections" || job_failed=1
  run_or_skip_task "$job" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$model" "$max_connections" || job_failed=1
  run_or_skip_task "$job" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$model" "$max_connections" || job_failed=1
  run_or_skip_task "$job" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$model" "$max_connections" || job_failed=1
  run_or_skip_task "$job" "denevil_fulcra_proxy_generation" "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" "$model" 1 || job_failed=1

  if [[ "$job_failed" == "0" ]]; then
    now_iso > "$run_dir/job_done.txt"
    rm -f "$run_dir/job_failed.txt"
    echo "completed:$job:$(now_iso)" > "$MASTER_STATUS_FILE"
  else
    now_iso > "$run_dir/job_failed.txt"
    rm -f "$run_dir/job_done.txt"
    echo "failed:$job:$(now_iso)" > "$MASTER_STATUS_FILE"
  fi
  rm -f "$worker_pid_file"
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
  local pid job run_dir status_file current_job worker_pid pid_file
  local current_run_has_live_elsewhere=0
  echo "[master]"
  echo "  run_id: $RUN_ID"
  if [[ -f "$MASTER_PIDFILE" ]]; then
    pid="$(cat "$MASTER_PIDFILE")"
    if is_running_pid "$pid"; then
      echo "  state: running"
      echo "  pid: $pid"
    elif [[ -f "$CURRENT_JOB_FILE" ]]; then
      current_job="$(cat "$CURRENT_JOB_FILE")"
      worker_pid="$(find_live_job_pid "$current_job" || true)"
      if [[ -n "$worker_pid" ]]; then
        echo "  state: worker_running_no_master"
        echo "  stale_master_pid: $pid"
        echo "  worker_pid: $worker_pid"
      else
        echo "  state: stopped"
        echo "  pid: $pid"
      fi
    else
      echo "  state: stopped"
      echo "  pid: $pid"
    fi
  elif [[ -f "$MASTER_STATUS_FILE" ]] && grep -q '^running:' "$MASTER_STATUS_FILE"; then
    echo "  state: active_no_master_pid"
  else
    echo "  state: not_launched"
  fi
  if [[ -f "$MASTER_STATUS_FILE" ]]; then
    echo "  status: $(cat "$MASTER_STATUS_FILE")"
  fi
  if [[ -f "$CURRENT_JOB_FILE" ]]; then
    current_job="$(cat "$CURRENT_JOB_FILE")"
    echo "  current_job: $current_job"
  fi

  while IFS= read -r job; do
    [[ -z "$job" ]] && continue
    run_dir="$(job_run_dir "$job")"
    status_file="$run_dir/task_status.csv"
    pid_file="$(job_pid_file "$job")"
    worker_pid="$(find_live_job_pid "$job" || true)"
    local live_elsewhere=""
    local worker_run_id=""
    local worker_log_dir=""
    echo "[$job]"
    if [[ -n "$worker_pid" ]]; then
      echo "  worker_state: running"
      echo "  worker_pid: $worker_pid"
    else
      live_elsewhere="$(find_live_job_process_any_run "$job" 2>/dev/null || true)"
      if [[ -n "$live_elsewhere" ]]; then
        IFS=$'\t' read -r worker_pid worker_run_id worker_log_dir <<< "$live_elsewhere"
      fi
      if [[ -n "$worker_run_id" && "$worker_run_id" != "$RUN_ID" ]]; then
          current_run_has_live_elsewhere=1
          echo "  worker_state: running_elsewhere"
          echo "  worker_pid: $worker_pid"
          echo "  worker_run_id: $worker_run_id"
          echo "  worker_log_dir: $worker_log_dir"
          echo "  note: set RUN_ID=$worker_run_id to inspect this rerun directly"
      elif [[ -f "$pid_file" ]]; then
      echo "  worker_state: stale_pid"
      echo "  worker_pid: $(cat "$pid_file")"
    fi
    fi
    if [[ -f "$status_file" ]]; then
      echo "  recent:"
      tail -n 5 "$status_file" | sed 's/^/    /'
    else
      echo "  recent: none"
    fi
    if [[ -f "$run_dir/job_done.txt" ]]; then
      echo "  completed_at: $(cat "$run_dir/job_done.txt")"
    elif [[ "$job" == "${current_job:-}" ]]; then
      show_live_eval_progress "$job"
    elif [[ -n "$worker_log_dir" ]]; then
      show_live_eval_progress_from_log_dir "$worker_log_dir"
    fi
  done < <(selected_jobs)

  if (( current_run_has_live_elsewhere > 0 )); then
    echo "  note: current RUN_ID is not the live rerun for at least one selected job"
  fi
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
