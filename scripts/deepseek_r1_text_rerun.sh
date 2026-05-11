#!/usr/bin/env bash
# DeepSeek-R1 text rerun launcher with on-disk resume.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
RUNNER="$ROOT/src/inspect/run.py"
PROVIDER_CONFIG="$ROOT/provider_config.sh"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"
UV_BIN="${UV_BIN:-$(command -v uv 2>/dev/null || true)}"
DEFAULT_VENV_PYTHON=""
if [[ -z "${VENV_PYTHON:-}" ]]; then
  for candidate in \
    "$ROOT/.venv/bin/python" \
    "$ROOT/../moral-psych-harness/CEI/.venv/bin/python"
  do
    if [[ -x "$candidate" ]]; then
      DEFAULT_VENV_PYTHON="$candidate"
      break
    fi
  done
fi
VENV_PYTHON="${VENV_PYTHON:-$DEFAULT_VENV_PYTHON}"

cd "$ROOT"

export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"

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
  echo "Could not resolve a runnable Python via uv or VENV_PYTHON." >&2
  exit 1
fi

RUN_ID="${RUN_ID:-2026-05-07-deepseek-r1-text-rerun}"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
PID_DIR="$RUN_BASE/pids"
LAUNCHER_STDOUT_DIR="$RUN_BASE/launcher"

TEXT_MAX_CONNECTIONS="${TEXT_MAX_CONNECTIONS:-8}"
DEEPSEEK_TEXT_MODEL="${DEEPSEEK_TEXT_MODEL:-deepseek/deepseek-r1}"
DEEPSEEK_ROUTE_MODE="${DEEPSEEK_ROUTE_MODE:-auto}"
DEEPSEEK_REASONING_EFFORT="${DEEPSEEK_REASONING_EFFORT:-none}"
DEEPSEEK_MODEL_ARGS="${DEEPSEEK_MODEL_ARGS:-reasoning_enabled=False}"
DEEPSEEK_EXTRA_BODY_JSON="${DEEPSEEK_EXTRA_BODY_JSON:-{\"chat_template_kwargs\":{\"enable_thinking\":false}}}"
DEEPSEEK_PROMPT_PREFIX="${DEEPSEEK_PROMPT_PREFIX:-/no_think}"
DEEPSEEK_OPENROUTER_MAX_CONNECTIONS="${DEEPSEEK_OPENROUTER_MAX_CONNECTIONS:-2}"
DEEPSEEK_OPENROUTER_REASONING_EFFORT="${DEEPSEEK_OPENROUTER_REASONING_EFFORT-}"
DEEPSEEK_OPENROUTER_MODEL_ARGS="${DEEPSEEK_OPENROUTER_MODEL_ARGS-}"
DEEPSEEK_OPENROUTER_EXTRA_BODY_JSON="${DEEPSEEK_OPENROUTER_EXTRA_BODY_JSON:-{\"reasoning\":{\"effort\":\"minimal\",\"exclude\":true}}}"
DEEPSEEK_OPENROUTER_PROMPT_PREFIX="${DEEPSEEK_OPENROUTER_PROMPT_PREFIX:-/no_think}"
DEEPSEEK_CEI_MIN_MAX_TOKENS="${DEEPSEEK_CEI_MIN_MAX_TOKENS-}"
TASK_FILTER="${TASK_FILTER:-ccd_bench_selection,unimoral_action_prediction,denevil_fulcra_proxy_generation,value_prism_valence,value_prism_relevance}"

UNIMORAL_DATA_DIR="${UNIMORAL_DATA_DIR:-$DATA_ROOT/unimoral}"
DENEVIL_DATA_FILE="${DENEVIL_DATA_FILE:-$DATA_ROOT/denevil/data_hybrid.jsonl}"
CCD_BENCH_DATA_FILE="${CCD_BENCH_DATA_FILE:-$DATA_ROOT/ccd-bench/CCD-Bench.json}"
VALUEPRISM_RELEVANCE_FILE="${VALUEPRISM_RELEVANCE_FILE:-$DATA_ROOT/valueprism/relevance/relevance_test.csv}"
VALUEPRISM_VALENCE_FILE="${VALUEPRISM_VALENCE_FILE:-$DATA_ROOT/valueprism/valence/valence_test.csv}"

families=(
  deepseek_r1_text
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

with open(sys.argv[1], newline="") as handle:
    for row in csv.DictReader(handle):
        if row.get("task_name") == sys.argv[2] and row.get("returncode") == "0":
            raise SystemExit(0)

raise SystemExit(1)
PY
}

task_logged_sample_progress() {
  local task_name="$1"
  local root="$2"

  python3 - "$task_name" "$root" "${UNIMORAL_DATA_DIR:-}" <<'PY'
from __future__ import annotations

import csv
import json
import os
import re
import sys
import zipfile
from pathlib import Path

task_name = sys.argv[1]
root = Path(sys.argv[2])
unimoral_data_dir = Path(sys.argv[3]).expanduser() if len(sys.argv) > 3 and sys.argv[3] else None
sample_ids: set[str] = set()
sample_ordinals: set[int] = set()
total = 0
stable_ordinal_tasks = {
    "ccd_bench_selection",
    "denevil_fulcra_proxy_generation",
    "value_prism_relevance",
    "value_prism_valence",
}

if root.exists():
    for path in root.glob("*.eval"):
        try:
            with zipfile.ZipFile(path) as zf:
                meta = json.loads(zf.read("_journal/start.json"))
                if meta.get("eval", {}).get("task") != task_name:
                    continue
                total = max(total, int(meta.get("eval", {}).get("dataset", {}).get("samples", 0) or 0))
                for name in zf.namelist():
                    if not (name.startswith("samples/") and name.endswith(".json")):
                        continue
                    sample_id = name.split("/")[-1].rsplit("_epoch_", 1)[0]
                    sample_ids.add(sample_id)
                    if task_name in stable_ordinal_tasks:
                        match = re.search(r"-(\d+)$", sample_id)
                        if match:
                            sample_ordinals.add(int(match.group(1)))
        except Exception:
            continue

count = len(sample_ids)
prefix = 0
if task_name == "unimoral_action_prediction" and unimoral_data_dir is not None and unimoral_data_dir.exists():
    languages = ["Arabic", "Chinese", "English", "Hindi", "Russian", "Spanish"]
    ordered_ids: list[str] = []
    for language in languages:
        rows: list[dict[str, str]] = []
        for kind in ("long", "short"):
            path = unimoral_data_dir / f"{language}_{kind}.csv"
            if not path.exists():
                continue
            with path.open(newline="", encoding="utf-8") as handle:
                rows.extend(csv.DictReader(handle))
        for index, row in enumerate(rows):
            ordered_ids.append(f"{language}-rq1-{row['Scenario_id']}-{row['Annotator_id']}-{index}")
    if ordered_ids:
        total = max(total, len(ordered_ids))
        while prefix < len(ordered_ids) and ordered_ids[prefix] in sample_ids:
            prefix += 1
        print(f"{count} {prefix} {total}")
        raise SystemExit(0)

if sample_ordinals:
    while prefix + 1 in sample_ordinals:
        prefix += 1
else:
    prefix = count

print(f"{count} {prefix} {total}")
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

  if [[ "$DEEPSEEK_ROUTE_MODE" != "openrouter" ]] && declare -F setup_model_provider >/dev/null 2>&1; then
    setup_model_provider "$ROUTED_CANONICAL_MODEL"
    ROUTED_MODEL="openai/$EFFECTIVE_MODEL"
    ROUTED_BASE_URL="${OPENAI_BASE_URL:-$ROUTED_BASE_URL}"
    if provider_entry=$(resolve_provider "$ROUTED_CANONICAL_MODEL" 2>/dev/null); then
      ROUTED_PROVIDER="${provider_entry%%|*}"
      ROUTED_PROVIDER_MODEL="${provider_entry#*|}"
      ROUTED_KEY_VAR="$(provider_key_var "$ROUTED_PROVIDER")"
    fi
  fi

  if [[ -n "$ROUTED_KEY_VAR" && -n "${!ROUTED_KEY_VAR:-}" ]]; then
    ROUTED_KEY_STATE="present"
  else
    ROUTED_KEY_STATE="missing"
  fi

  # Fall back to OpenRouter when the direct DeepSeek key is absent but an
  # OpenRouter key is available. This keeps DeepSeek-R1 runnable in the same
  # non-conflicting provider lane the user expects.
  if [[ "$ROUTED_KEY_STATE" != "present" && "$DEEPSEEK_ROUTE_MODE" == "auto" && -n "${OPENROUTER_API_KEY:-}" ]]; then
    ROUTED_PROVIDER="openrouter"
    ROUTED_PROVIDER_MODEL="$ROUTED_CANONICAL_MODEL"
    ROUTED_KEY_VAR="OPENROUTER_API_KEY"
    ROUTED_BASE_URL="https://openrouter.ai/api/v1"
    ROUTED_MODEL="openai/$ROUTED_CANONICAL_MODEL"
    ROUTED_KEY_STATE="present"
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

  local run_dir output_path log_dir runtime_home start_at end_at rc reasoning_effort model_args extra_body_json prompt_prefix
  local task_resume_env task_resume_count task_resume_prefix task_resume_total task_logged_count
  run_dir="$(family_run_dir "$family")"
  output_path="$run_dir/${task_name}.txt"
  log_dir="$(family_log_dir "$family")"
  runtime_home="$run_dir/_runtime_home"
  mkdir -p "$run_dir" "$log_dir" "$runtime_home"
  configure_routed_model "$model"
  reasoning_effort="$DEEPSEEK_REASONING_EFFORT"
  model_args="$DEEPSEEK_MODEL_ARGS"
  extra_body_json="$DEEPSEEK_EXTRA_BODY_JSON"
  prompt_prefix="$DEEPSEEK_PROMPT_PREFIX"
  if [[ "$ROUTED_PROVIDER" == "openrouter" ]]; then
    max_connections="$DEEPSEEK_OPENROUTER_MAX_CONNECTIONS"
    reasoning_effort="$DEEPSEEK_OPENROUTER_REASONING_EFFORT"
    model_args="$DEEPSEEK_OPENROUTER_MODEL_ARGS"
    extra_body_json="$DEEPSEEK_OPENROUTER_EXTRA_BODY_JSON"
    prompt_prefix="$DEEPSEEK_OPENROUTER_PROMPT_PREFIX"
  fi

  if ! task_is_selected "$task_name"; then
    printf '[%s] SKIP family=%s task=%s reason=task_filter=%s\n' "$(now_iso)" "$family" "$task_name" "$TASK_FILTER" > "$output_path"
    return 0
  fi

  if task_status_has_success "$family" "$task_name"; then
    start_at="$(now_iso)"
    printf '[%s] SKIP family=%s task=%s reason=task_status_success\n' "$start_at" "$family" "$task_name" > "$output_path"
    return 0
  fi

  case "$task_name" in
    ccd_bench_selection) task_resume_env="CCD_BENCH_RESUME_COUNT" ;;
    denevil_fulcra_proxy_generation) task_resume_env="DENEVIL_FULCRA_RESUME_COUNT" ;;
    unimoral_action_prediction) task_resume_env="UNIMORAL_ACTION_RESUME_COUNT" ;;
    value_prism_valence) task_resume_env="VALUEPRISM_VALENCE_RESUME_COUNT" ;;
    value_prism_relevance) task_resume_env="VALUEPRISM_RELEVANCE_RESUME_COUNT" ;;
    *) task_resume_env="" ;;
  esac

  task_resume_count=0
  task_resume_prefix=0
  task_resume_total=0
  task_logged_count=0
  if [[ -n "$task_resume_env" ]]; then
    read -r task_logged_count task_resume_prefix task_resume_total <<< "$(task_logged_sample_progress "$task_name" "$log_dir")"
    task_resume_count="$task_resume_prefix"
  fi

  if [[ "$task_resume_total" =~ ^[0-9]+$ ]] && (( task_resume_total > 0 )) && [[ "$task_resume_prefix" =~ ^[0-9]+$ ]] && (( task_resume_prefix >= task_resume_total )); then
    start_at="$(now_iso)"
    printf '[%s] SKIP family=%s task=%s reason=logged_sample_coverage_complete covered=%s total=%s\n' "$start_at" "$family" "$task_name" "$task_resume_prefix" "$task_resume_total" > "$output_path"
    record_status "$family" "$task_name" "$start_at" "$start_at" 0 "$output_path"
    return 0
  fi

  start_at="$(now_iso)"
  record_routing_metadata "$family" "$task_name" "$start_at"
  if (
    set +e
    if [[ -n "$task_resume_env" && "$task_resume_count" =~ ^[0-9]+$ && "$task_resume_count" -gt 0 ]]; then
      export "$task_resume_env=$task_resume_count"
    fi
    export PYTHONUNBUFFERED=1
    if [[ -n "$prompt_prefix" ]]; then
      export CEI_PROMPT_PREFIX="$prompt_prefix"
    else
      unset CEI_PROMPT_PREFIX || true
    fi
    if [[ -n "$DEEPSEEK_CEI_MIN_MAX_TOKENS" ]]; then
      export CEI_MIN_MAX_TOKENS="$DEEPSEEK_CEI_MIN_MAX_TOKENS"
    else
      unset CEI_MIN_MAX_TOKENS || true
    fi
    echo "[$start_at] START family=$family task=$task_name model=$model routed_model=$ROUTED_MODEL provider=$ROUTED_PROVIDER provider_model=$ROUTED_PROVIDER_MODEL base_url=$ROUTED_BASE_URL key_var=$ROUTED_KEY_VAR key_state=$ROUTED_KEY_STATE max_connections=$max_connections reasoning_effort=${reasoning_effort:-default} model_args=${model_args:-default} extra_body_json=${extra_body_json:-default} prompt_prefix=${prompt_prefix:-default} resume_count=${task_resume_count:-0} resume_prefix=${task_resume_prefix:-0} logged_count=${task_logged_count:-0} resume_total=${task_resume_total:-0}"
    if [[ "$ROUTED_KEY_STATE" != "present" ]]; then
      echo "[$(now_iso)] ROUTING_PRECHECK_FAILED family=$family task=$task_name provider=$ROUTED_PROVIDER key_var=$ROUTED_KEY_VAR reason=missing_provider_api_key"
      exit 86
    fi
    if [[ "$ROUTED_PROVIDER" == "openrouter" ]]; then
      export OPENAI_API_KEY="$OPENROUTER_API_KEY"
      export OPENAI_BASE_URL="$ROUTED_BASE_URL"
    fi
    "${RUN_PREFIX[@]}" "$RUNNER" \
      --tasks "$task_spec" \
      --model "$ROUTED_MODEL" \
      --model_base_url "$ROUTED_BASE_URL" \
      --home_dir "$runtime_home" \
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
  return "$rc"
}

run_family() {
  local family="$1"
  local run_dir overall_rc
  run_dir="$(family_run_dir "$family")"
  mkdir -p "$run_dir"
  rm -f "$run_dir/family_done.txt"
  overall_rc=0

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

  run_task "$family" "ccd_bench_selection" "src/inspect/evals/ccd_bench.py::ccd_bench_selection" "$DEEPSEEK_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
  run_task "$family" "unimoral_action_prediction" "src/inspect/evals/unimoral.py::unimoral_action_prediction" "$DEEPSEEK_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
  run_task "$family" "denevil_fulcra_proxy_generation" "src/inspect/evals/denevil.py::denevil_fulcra_proxy_generation" "$DEEPSEEK_TEXT_MODEL" 4 || overall_rc=$?
  run_task "$family" "value_prism_valence" "src/inspect/evals/value_kaleidoscope.py::value_prism_valence" "$DEEPSEEK_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?
  run_task "$family" "value_prism_relevance" "src/inspect/evals/value_kaleidoscope.py::value_prism_relevance" "$DEEPSEEK_TEXT_MODEL" "$TEXT_MAX_CONNECTIONS" || overall_rc=$?

  if (( overall_rc == 0 )); then
    now_iso > "$run_dir/family_done.txt"
  else
    rm -f "$run_dir/family_done.txt"
  fi
  return "$overall_rc"
}

launch_family() {
  local family="$1"
  local pidfile stdout_path existing_pid
  pidfile="$PID_DIR/$family.pid"
  stdout_path="$LAUNCHER_STDOUT_DIR/${family}.out"

  if [[ -f "$pidfile" ]]; then
    existing_pid="$(cat "$pidfile" 2>/dev/null || true)"
    if [[ -n "$existing_pid" ]] && is_running_pid "$existing_pid"; then
      echo "$family already running (pid $existing_pid)"
      return 0
    fi
  fi

  nohup /bin/bash "$SCRIPT_PATH" run "$family" > "$stdout_path" 2>&1 &
  echo "$!" > "$pidfile"
  echo "$family launched (pid $!)"
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
