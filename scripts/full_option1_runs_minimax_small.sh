#!/usr/bin/env bash
# Historical launcher for the MiniMax small-model extension experiments.
# It preserves the original operational flow while remaining portable via env overrides.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
RUNNER="$ROOT/src/inspect/run.py"
PROVIDER_CONFIG="$ROOT/provider_config.sh"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"
UV_BIN="${UV_BIN:-$(command -v uv 2>/dev/null || true)}"
VENV_PYTHON="${VENV_PYTHON:-$ROOT/.venv/bin/python}"

# Keep task specs and relative artifact paths stable even when the launcher is
# invoked from outside the repo root (for example via nohup or another script).
cd "$ROOT"

load_env_file() {
  local env_file="$1"
  if [[ -f "$env_file" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$env_file"
    set +a
  fi
}

load_env_file "$ROOT/.env"
load_env_file "$ROOT/.env.local"

if [[ -f "$PROVIDER_CONFIG" ]]; then
  # shellcheck source=/dev/null
  source "$PROVIDER_CONFIG"
fi

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
MINIMAX_TEXT_MODEL="${MINIMAX_TEXT_MODEL:-openrouter/minimax/minimax-m2.5}"
MINIMAX_VISION_MODEL="${MINIMAX_VISION_MODEL:-openrouter/minimax/minimax-01}"
TASK_FILTER="${TASK_FILTER:-}"

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

family_log_dir() {
  local family="$1"
  echo "$LOG_BASE/$family"
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

family_has_selected_tasks() {
  local family="$1"
  local task_name
  while IFS= read -r task_name; do
    [[ -n "$task_name" ]] || continue
    if task_is_selected "$task_name"; then
      return 0
    fi
  done < <(family_expected_tasks "$family" || true)
  return 1
}

find_live_family_pid() {
  local family="$1"
  local pidfile pid log_dir

  pidfile="$PID_DIR/$family.pid"
  if [[ -f "$pidfile" ]]; then
    pid="$(cat "$pidfile")"
    if [[ -n "$pid" ]] && is_running_pid "$pid"; then
      echo "$pid"
      return 0
    fi
  fi

  log_dir="$(family_log_dir "$family")"
  python3 - "$log_dir" <<'PY'
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

log_dir = Path(sys.argv[1]).resolve()

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
    if str(log_dir) not in line:
        continue
    pid, _, _ = line.partition(" ")
    if pid:
        print(pid)
        raise SystemExit(0)

raise SystemExit(1)
PY
  if [[ $? -eq 0 ]]; then
    return 0
  fi

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
    if [[ $? -eq 0 ]]; then
      return 0
    fi
  fi
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

task_status_has_success() {
  local family="$1"
  local task_name="$2"
  local status_file
  status_file="$(family_run_dir "$family")/task_status.csv"
  [[ -f "$status_file" ]] || return 1

  python3 - "$status_file" "$task_name" <<'PY'
from __future__ import annotations

import csv
import sys

status_file = sys.argv[1]
task_name = sys.argv[2]

with open(status_file, newline="") as handle:
    for row in csv.DictReader(handle):
        if row.get("task_name") == task_name and row.get("returncode") == "0":
            raise SystemExit(0)

raise SystemExit(1)
PY
}

task_logged_sample_progress() {
  local log_dir="$1"
  local task_name="$2"

  python3 - "$log_dir" "$task_name" <<'PY'
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

root = Path(sys.argv[1])
task_name = sys.argv[2]
sample_ids: set[str] = set()
total = 0

if root.exists():
    for path in root.glob("*.eval"):
        try:
            with zipfile.ZipFile(path) as zf:
                try:
                    meta = json.loads(zf.read("_journal/start.json"))
                except KeyError:
                    continue
                if meta.get("eval", {}).get("task") != task_name:
                    continue
                total = max(total, int(meta.get("eval", {}).get("dataset", {}).get("samples", 0) or 0))
                for name in zf.namelist():
                    if not (name.startswith("samples/") and name.endswith(".json")):
                        continue
                    sample_name = name[len("samples/") : -len(".json")]
                    if "_epoch_" in sample_name:
                        sample_name = sample_name.split("_epoch_", 1)[0]
                    sample_ids.add(sample_name)
        except Exception:
            continue

print(f"{len(sample_ids)} {total}")
PY
}

family_expected_tasks() {
  local family="$1"
  case "$family" in
    minimax_text)
      printf '%s\n' \
        ccd_bench_selection \
        denevil_fulcra_proxy_generation \
        value_prism_valence \
        value_prism_relevance \
        unimoral_action_prediction
      ;;
    minimax_smid)
      printf '%s\n' \
        smid_moral_rating \
        smid_foundation_classification
      ;;
    *)
      return 1
      ;;
  esac
}

family_status_is_successful() {
  local family="$1"
  local status_file
  if ! family_has_selected_tasks "$family"; then
    return 0
  fi
  status_file="$(family_run_dir "$family")/task_status.csv"
  [[ -f "$status_file" ]] || return 1

  python3 - "$family" "$status_file" "$TASK_FILTER" <<'PY'
from __future__ import annotations

import csv
import sys

family = sys.argv[1]
status_file = sys.argv[2]
task_filter = {task.strip() for task in sys.argv[3].split(",") if task.strip()}
expected = {
    "minimax_text": [
        "ccd_bench_selection",
        "denevil_fulcra_proxy_generation",
        "value_prism_valence",
        "value_prism_relevance",
        "unimoral_action_prediction",
    ],
    "minimax_smid": [
        "smid_moral_rating",
        "smid_foundation_classification",
    ],
}[family]

if task_filter:
    expected = [task_name for task_name in expected if task_name in task_filter]

latest: dict[str, str] = {}
with open(status_file, newline="") as handle:
    for row in csv.DictReader(handle):
        task_name = row.get("task_name", "")
        if task_name:
            latest[task_name] = row.get("returncode", "")

for task_name in expected:
    if latest.get(task_name) != "0":
        raise SystemExit(1)
PY
}

normalize_routing_model() {
  local model="$1"
  model="${model#openrouter/}"
  model="${model#openai/}"
  echo "$model"
}

configure_routed_model() {
  local requested_model="$1"
  local provider_entry

  ROUTED_REQUESTED_MODEL="$requested_model"
  ROUTED_CANONICAL_MODEL="$(normalize_routing_model "$requested_model")"
  ROUTED_PROVIDER="openrouter"
  ROUTED_PROVIDER_MODEL="$ROUTED_CANONICAL_MODEL"
  ROUTED_KEY_VAR="OPENROUTER_API_KEY"
  ROUTED_BASE_URL="https://openrouter.ai/api/v1"
  ROUTED_MODEL="openai/$ROUTED_CANONICAL_MODEL"

  if declare -F setup_model_provider >/dev/null 2>&1; then
    setup_model_provider "$ROUTED_CANONICAL_MODEL"
    ROUTED_MODEL="openai/$EFFECTIVE_MODEL"
    ROUTED_BASE_URL="${OPENAI_BASE_URL:-$ROUTED_BASE_URL}"
    if provider_entry=$(resolve_provider "$ROUTED_CANONICAL_MODEL" 2>/dev/null); then
      ROUTED_PROVIDER="${provider_entry%%|*}"
      ROUTED_PROVIDER_MODEL="${provider_entry#*|}"
      ROUTED_KEY_VAR="$(provider_key_var "$ROUTED_PROVIDER")"
    fi
  fi

  if [[ -n "$ROUTED_KEY_VAR" ]] && [[ -n "${!ROUTED_KEY_VAR:-}" ]]; then
    ROUTED_KEY_STATE="present"
  else
    ROUTED_KEY_STATE="missing"
  fi
}

record_routing_metadata() {
  local family="$1"
  local task_name="$2"
  local start_at="$3"
  local routing_file
  routing_file="$(family_run_dir "$family")/routing_metadata.csv"

  if [[ ! -f "$routing_file" ]]; then
    echo "task_name,start_at,requested_model,canonical_model,provider,provider_model,base_url,key_var,key_state" > "$routing_file"
  fi

  echo "$task_name,$start_at,$ROUTED_REQUESTED_MODEL,$ROUTED_CANONICAL_MODEL,$ROUTED_PROVIDER,$ROUTED_PROVIDER_MODEL,$ROUTED_BASE_URL,$ROUTED_KEY_VAR,$ROUTED_KEY_STATE" >> "$routing_file"
}

run_task() {
  local family="$1"
  local task_name="$2"
  local task_spec="$3"
  local model="$4"
  local max_connections="$5"

  local run_dir output_path log_dir runtime_home start_at end_at rc
  local smid_resume_env smid_resume_count smid_resume_total
  run_dir="$(family_run_dir "$family")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$LOG_BASE/$family"
  runtime_home="$run_dir/_runtime_home"
  mkdir -p "$run_dir" "$log_dir" "$runtime_home"
  configure_routed_model "$model"
  smid_resume_env=""
  smid_resume_count=0
  smid_resume_total=0

  if ! task_is_selected "$task_name"; then
    printf '[%s] SKIP family=%s task=%s reason=task_filter=%s\n' "$(now_iso)" "$family" "$task_name" "$TASK_FILTER" > "$output_path"
    return 0
  fi

  case "$task_name" in
    smid_moral_rating)
      smid_resume_env="SMID_MORAL_RESUME_COUNT"
      ;;
    smid_foundation_classification)
      smid_resume_env="SMID_FOUNDATION_RESUME_COUNT"
      ;;
  esac

  if [[ -n "$smid_resume_env" ]]; then
    if task_status_has_success "$family" "$task_name"; then
      smid_resume_count=0
      smid_resume_total=0
    elif [[ -n "${!smid_resume_env:-}" ]]; then
      smid_resume_count="${!smid_resume_env}"
      read -r _smid_logged_count smid_resume_total <<< "$(task_logged_sample_progress "$log_dir" "$task_name")"
      unset _smid_logged_count
    else
      read -r smid_resume_count smid_resume_total <<< "$(task_logged_sample_progress "$log_dir" "$task_name")"
    fi
  fi

  if [[ "$smid_resume_total" =~ ^[0-9]+$ ]] && (( smid_resume_total > 0 )) && [[ "$smid_resume_count" =~ ^[0-9]+$ ]] && (( smid_resume_count >= smid_resume_total )); then
    start_at="$(now_iso)"
    end_at="$start_at"
    printf '[%s] SKIP family=%s task=%s reason=logged_sample_coverage_complete covered=%s total=%s\n' "$start_at" "$family" "$task_name" "$smid_resume_count" "$smid_resume_total" > "$output_path"
    record_status "$family" "$task_name" "$start_at" "$end_at" 0 "$output_path"
    return 0
  fi

  start_at="$(now_iso)"
  record_routing_metadata "$family" "$task_name" "$start_at"
  if (
    set +e
    if [[ -n "$smid_resume_env" && "$smid_resume_count" =~ ^[0-9]+$ && "$smid_resume_count" -gt 0 ]]; then
      export "$smid_resume_env=$smid_resume_count"
    fi
    echo "[$start_at] START family=$family task=$task_name model=$model routed_model=$ROUTED_MODEL provider=$ROUTED_PROVIDER provider_model=$ROUTED_PROVIDER_MODEL base_url=$ROUTED_BASE_URL key_var=$ROUTED_KEY_VAR key_state=$ROUTED_KEY_STATE max_connections=$max_connections resume_count=${smid_resume_count:-0} resume_total=${smid_resume_total:-0}"
    if [[ "$ROUTED_KEY_STATE" != "present" ]]; then
      echo "[$(now_iso)] ROUTING_PRECHECK_FAILED family=$family task=$task_name provider=$ROUTED_PROVIDER key_var=$ROUTED_KEY_VAR reason=missing_provider_api_key"
      exit 86
    fi
    if [[ "$ROUTED_PROVIDER" == "minimax" ]] && [[ -z "${CEI_MIN_MAX_TOKENS:-}" ]]; then
      export CEI_MIN_MAX_TOKENS=2048
    fi
    "${RUN_PREFIX[@]}" "$RUNNER" \
      --tasks "$task_spec" \
      --model "$ROUTED_MODEL" \
      --model_base_url "$ROUTED_BASE_URL" \
      --home_dir "$runtime_home" \
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
  return "$rc"
}

run_family() {
  local family="$1"
  local run_dir overall_rc
  run_dir="$(family_run_dir "$family")"
  mkdir -p "$run_dir"
  rm -f "$run_dir/family_done.txt" "$run_dir/family_skipped.txt"
  overall_rc=0

  if ! family_has_selected_tasks "$family"; then
    printf '[%s] SKIP family=%s reason=no_tasks_selected task_filter=%s\n' "$(now_iso)" "$family" "$TASK_FILTER" > "$run_dir/family_skipped.txt"
    now_iso > "$run_dir/family_done.txt"
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
      # Keep smaller text benchmarks first so we land earlier completions
      # before the large ValuePrism sweeps.
      run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
      run_task "$family" "denevil_fulcra_proxy_generation" "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" "$MINIMAX_TEXT_MODEL" 2 || overall_rc=$?
      run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
      run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
      run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$MINIMAX_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
      ;;
    minimax_smid)
      require_dir SMID_DATA_DIR
      export SMID_DATA_DIR="$SMID_DATA_DIR"
      run_task "$family" "smid_moral_rating" "src/inspect/evals/smid.py::smid_moral_rating" "$MINIMAX_VISION_MODEL" "$VISION_MAX_CONNECTIONS" || overall_rc=$?
      run_task "$family" "smid_foundation_classification" "src/inspect/evals/smid.py::smid_foundation_classification" "$MINIMAX_VISION_MODEL" "$VISION_MAX_CONNECTIONS" || overall_rc=$?
      ;;
    *)
      echo "Unknown family: $family" >&2
      return 1
      ;;
  esac

  if (( overall_rc == 0 )) && family_status_is_successful "$family"; then
    now_iso > "$run_dir/family_done.txt"
    return 0
  fi

  rm -f "$run_dir/family_done.txt"
  return "$overall_rc"
}

launch_family() {
  local family="$1"
  local pidfile pid stdout_path existing_pid
  pidfile="$PID_DIR/$family.pid"
  stdout_path="$LAUNCHER_STDOUT_DIR/${family}.out"

  existing_pid="$(find_live_family_pid "$family" || true)"
  if [[ -n "$existing_pid" ]]; then
    echo "$family already running (pid $existing_pid)"
    return 0
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
    live_pid="$(find_live_family_pid "$family" || true)"
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
    if [[ -f "$run_dir/family_done.txt" ]] && family_status_is_successful "$family"; then
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
