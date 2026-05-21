#!/usr/bin/env bash
# Run the UniMoral RQ2/RQ3/RQ4 completion matrix for the released text model lines.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/src/inspect/run.py"
DATA_ROOT="${DATA_ROOT:-$(cd "$ROOT/.." && pwd)/data}"
RUN_ID="${RUN_ID:-2026-05-16-unimoral-full}"
LOG_BASE="$ROOT/results/inspect/logs/$RUN_ID"
RUN_BASE="$ROOT/results/inspect/full-runs/$RUN_ID"
VENV_PYTHON="${VENV_PYTHON:-$(command -v python)}"
MAX_CONNECTIONS_DEFAULT="${MAX_CONNECTIONS_DEFAULT:-8}"
UNIMORAL_DATA_DIR="${UNIMORAL_DATA_DIR:-$DATA_ROOT/unimoral}"
TASK_FILTER="${TASK_FILTER:-unimoral_moral_typology,unimoral_factor_attribution,unimoral_consequence_generation}"
MODEL_FILTER="${MODEL_FILTER:-}"
UNIMORAL_SKIP_MODEL_REGEX="${UNIMORAL_SKIP_MODEL_REGEX:-}"
FORCE_RERUN="${FORCE_RERUN:-0}"
UNIMORAL_ROUTE_MODE="${UNIMORAL_ROUTE_MODE:-auto}"
UNIMORAL_DRY_RUN="${UNIMORAL_DRY_RUN:-0}"
UNIMORAL_RERUN_UNPARSED="${UNIMORAL_RERUN_UNPARSED:-0}"
UNIMORAL_ALLOW_MINIMAX="${UNIMORAL_ALLOW_MINIMAX:-0}"

mkdir -p "$LOG_BASE" "$RUN_BASE"

load_env_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$path"
    set +a
  fi
}

load_env_file "$ROOT/.env"
load_env_file "$ROOT/.env.local"

if [[ -f "$ROOT/provider_config.sh" ]]; then
  # shellcheck source=/dev/null
  source "$ROOT/provider_config.sh"
fi

tasks=(
  "unimoral_moral_typology|src/inspect/evals/unimoral.py::unimoral_moral_typology|UNIMORAL_TYPOLOGY_RESUME_COUNT"
  "unimoral_factor_attribution|src/inspect/evals/unimoral.py::unimoral_factor_attribution|UNIMORAL_FACTOR_RESUME_COUNT"
  "unimoral_consequence_generation|src/inspect/evals/unimoral.py::unimoral_consequence_generation|UNIMORAL_CONSEQUENCE_RESUME_COUNT"
)

models=(
  "Qwen-S|qwen_s|openrouter/qwen/qwen3-8b|qwen"
  "Qwen-M|qwen_m|openrouter/qwen/qwen3-14b|qwen"
  "Qwen-L|qwen_l|openrouter/qwen/qwen3-32b|qwen"
  "MiniMax-S|minimax_s|openrouter/minimax/minimax-m2.1|minimax_reasoning"
  "MiniMax-M|minimax_m|openrouter/minimax/minimax-m2.5|minimax_reasoning"
  "MiniMax-L|minimax_l|openrouter/minimax/minimax-m2.5|minimax_reasoning"
  "DeepSeek-S|deepseek_s|openrouter/deepseek/deepseek-r1-distill-llama-70b|deepseek_distill_visible"
  "DeepSeek-M|deepseek_m|openrouter/deepseek/deepseek-chat-v3.1|plain"
  "DeepSeek-L|deepseek_l|openrouter/deepseek/deepseek-r1|deepseek_r1_mandatory_reasoning"
  "Llama-S|llama_s|openrouter/meta-llama/llama-3.2-11b-vision-instruct|plain"
  "Llama-M|llama_m|openrouter/meta-llama/llama-3.3-70b-instruct|plain"
  "Llama-L|llama_l|openrouter/meta-llama/llama-4-maverick|plain"
  "Gemma-S|gemma_s|openrouter/google/gemma-3-4b-it|plain"
  "Gemma-M|gemma_m|openrouter/google/gemma-3-12b-it|plain"
  "Gemma-L|gemma_l|openrouter/google/gemma-3-27b-it|plain"
  "GPT4 only|gpt4_only|openai/gpt-4o-mini|openai"
)

now_iso() {
  "$VENV_PYTHON" - <<'PY'
from datetime import datetime
print(datetime.now().astimezone().isoformat())
PY
}

selected() {
  local name="$1"
  local filter="$2"
  [[ -z "$filter" ]] && return 0
  "$VENV_PYTHON" - "$name" "$filter" <<'PY'
import sys
name = sys.argv[1]
requested = {part.strip() for part in sys.argv[2].split(",") if part.strip()}
raise SystemExit(0 if name in requested else 1)
PY
}

skip_model_line() {
  local line_label="$1"
  local slug="$2"
  local route="$3"
  local profile="$4"
  local haystack="$line_label|$slug|$route|$profile"
  [[ -n "$UNIMORAL_SKIP_MODEL_REGEX" && "$haystack" =~ $UNIMORAL_SKIP_MODEL_REGEX ]]
}

minimax_execution_allowed() {
  local profile="$1"
  [[ "$profile" != "minimax_reasoning" || "$UNIMORAL_ALLOW_MINIMAX" == "1" ]]
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

  if [[ "$requested_model" == openai/* && "$requested_model" != openrouter/* ]]; then
    ROUTED_PROVIDER="openai"
    ROUTED_PROVIDER_MODEL="$ROUTED_CANONICAL_MODEL"
    ROUTED_KEY_VAR="OPENAI_API_KEY"
    ROUTED_BASE_URL=""
    ROUTED_MODEL="$requested_model"
    unset OPENAI_BASE_URL || true
  else
    ROUTED_PROVIDER="openrouter"
    ROUTED_PROVIDER_MODEL="$ROUTED_CANONICAL_MODEL"
    ROUTED_KEY_VAR="OPENROUTER_API_KEY"
    ROUTED_BASE_URL="https://openrouter.ai/api/v1"
    ROUTED_MODEL="openai/$ROUTED_CANONICAL_MODEL"
    export OPENAI_API_KEY="${OPENROUTER_API_KEY:-}"
    export OPENAI_BASE_URL="$ROUTED_BASE_URL"

    if [[ "$UNIMORAL_ROUTE_MODE" != "openrouter" ]] && declare -F setup_model_provider >/dev/null 2>&1; then
      setup_model_provider "$ROUTED_CANONICAL_MODEL"
      ROUTED_MODEL="openai/$EFFECTIVE_MODEL"
      ROUTED_BASE_URL="${OPENAI_BASE_URL:-$ROUTED_BASE_URL}"
      if provider_entry=$(resolve_provider "$ROUTED_CANONICAL_MODEL" 2>/dev/null); then
        ROUTED_PROVIDER="${provider_entry%%|*}"
        ROUTED_PROVIDER_MODEL="${provider_entry#*|}"
        ROUTED_KEY_VAR="$(provider_key_var "$ROUTED_PROVIDER")"
      fi
    fi
  fi

  if [[ -n "$ROUTED_KEY_VAR" && -n "${!ROUTED_KEY_VAR:-}" ]]; then
    ROUTED_KEY_STATE="present"
  else
    ROUTED_KEY_STATE="missing"
  fi

  if [[ "$ROUTED_KEY_STATE" != "present" && "$UNIMORAL_ROUTE_MODE" == "auto" && "$ROUTED_PROVIDER" != "openai" && -n "${OPENROUTER_API_KEY:-}" ]]; then
    ROUTED_PROVIDER="openrouter"
    ROUTED_PROVIDER_MODEL="$ROUTED_CANONICAL_MODEL"
    ROUTED_KEY_VAR="OPENROUTER_API_KEY"
    ROUTED_BASE_URL="https://openrouter.ai/api/v1"
    ROUTED_MODEL="openai/$ROUTED_CANONICAL_MODEL"
    export OPENAI_API_KEY="$OPENROUTER_API_KEY"
    export OPENAI_BASE_URL="$ROUTED_BASE_URL"
    ROUTED_KEY_STATE="present"
  fi
}

record_routing_metadata() {
  local slug="$1"
  local task_name="$2"
  local start_at="$3"
  local routing_file="$RUN_BASE/$slug/routing_metadata.csv"

  if [[ ! -f "$routing_file" ]]; then
    echo "task_name,start_at,requested_model,canonical_model,provider,provider_model,base_url,key_var,key_state" > "$routing_file"
  fi

  echo "$task_name,$start_at,$ROUTED_REQUESTED_MODEL,$ROUTED_CANONICAL_MODEL,$ROUTED_PROVIDER,$ROUTED_PROVIDER_MODEL,$ROUTED_BASE_URL,$ROUTED_KEY_VAR,$ROUTED_KEY_STATE" >> "$routing_file"
}

eval_status_for_task() {
  local log_dir="$1"
  local task_name="$2"
  "$VENV_PYTHON" - "$log_dir" "$task_name" <<'PY'
import json
import os
import time
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

log_dir = Path(sys.argv[1])
task_name = sys.argv[2]
expected = {
    "unimoral_moral_typology": 3492,
    "unimoral_factor_attribution": 3492,
    "unimoral_consequence_generation": 1782,
}.get(task_name, 0)
success_ids = set()
best = ""
has_running = False
running_stale_seconds = int(os.getenv("UNIMORAL_RUNNING_STALE_SECONDS", "1800"))
for path in sorted(log_dir.glob("*.eval"), key=lambda p: p.stat().st_mtime, reverse=True):
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
            elif "_journal/start.json" in names and time.time() - path.stat().st_mtime < running_stale_seconds:
                start = json.loads(zf.read("_journal/start.json").decode("utf-8"))
                eval_meta = start.get("eval") if isinstance(start, dict) else {}
                if isinstance(eval_meta, dict) and eval_meta.get("task") == task_name:
                    has_running = True
                continue
            else:
                continue
            eval_meta = header.get("eval") if isinstance(header, dict) else {}
            if not isinstance(eval_meta, dict) or eval_meta.get("task") != task_name:
                continue
            status = str(header.get("status", ""))
            if status == "success":
                for name in names:
                    if not name.startswith("samples/") or not name.endswith(".json"):
                        continue
                    try:
                        sample = json.loads(zf.read(name).decode("utf-8"))
                    except (json.JSONDecodeError, KeyError):
                        continue
                    success_ids.add(str(sample.get("id") or sample.get("uuid") or name))
            best = status or "unknown"
    except (BadZipFile, json.JSONDecodeError, KeyError, ValueError):
        continue
if expected and len(success_ids) >= expected:
    print("success")
elif has_running:
    print("running")
elif success_ids:
    print("partial_success")
elif best:
    print(best)
PY
}

sample_progress_for_task() {
  local log_dir="$1"
  local task_name="$2"
  "$VENV_PYTHON" - "$log_dir" "$task_name" "$ROOT" "$UNIMORAL_DATA_DIR" <<'PY'
import json
import os
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

log_dir = Path(sys.argv[1])
task_name = sys.argv[2]
root = Path(sys.argv[3])
os.environ["UNIMORAL_DATA_DIR"] = sys.argv[4]
os.environ.setdefault("UNIMORAL_LANGUAGE", "all")
os.environ.setdefault("UNIMORAL_MODE", "np")
sys.path.insert(0, str(root / "src" / "inspect"))

from evals import unimoral  # noqa: E402

sample_builders = {
    "unimoral_moral_typology": unimoral._make_typology_samples,
    "unimoral_factor_attribution": unimoral._make_factor_samples,
    "unimoral_consequence_generation": unimoral._make_consequence_samples,
}

expected_ids = [str(sample.id) for sample in sample_builders[task_name]()]
logged_ids = set()
for path in sorted(log_dir.glob("*.eval"), key=lambda p: p.stat().st_mtime, reverse=True):
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
                eval_meta = header.get("eval") if isinstance(header, dict) else {}
                if not isinstance(eval_meta, dict) or eval_meta.get("task") != task_name:
                    continue
                for name in names:
                    if not name.startswith("samples/") or not name.endswith(".json"):
                        continue
                    sample = json.loads(zf.read(name).decode("utf-8"))
                    logged_ids.add(str(sample.get("id") or sample.get("uuid") or name))
                continue
            if "_journal/start.json" in names:
                start = json.loads(zf.read("_journal/start.json").decode("utf-8"))
                eval_meta = start.get("eval") if isinstance(start, dict) else {}
                if not isinstance(eval_meta, dict) or eval_meta.get("task") != task_name:
                    continue
                for name in names:
                    if not name.startswith("samples/") or not name.endswith(".json"):
                        continue
                    sample = json.loads(zf.read(name).decode("utf-8"))
                    logged_ids.add(str(sample.get("id") or sample.get("uuid") or name))
    except (BadZipFile, json.JSONDecodeError, KeyError, ValueError):
        continue

prefix = 0
while prefix < len(expected_ids) and expected_ids[prefix] in logged_ids:
    prefix += 1
print(prefix, len(expected_ids))
PY
}

sample_coverage_for_task() {
  local log_dir="$1"
  local task_name="$2"
  "$VENV_PYTHON" - "$log_dir" "$task_name" "$ROOT" "$UNIMORAL_DATA_DIR" <<'PY'
import json
import os
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

log_dir = Path(sys.argv[1])
task_name = sys.argv[2]
root = Path(sys.argv[3])
os.environ["UNIMORAL_DATA_DIR"] = sys.argv[4]
os.environ.setdefault("UNIMORAL_LANGUAGE", "all")
os.environ.setdefault("UNIMORAL_MODE", "np")
sys.path.insert(0, str(root / "src" / "inspect"))

from evals import unimoral  # noqa: E402
from evals._benchmark_utils import canonicalize_label_from_output, consequence_text_from_output  # noqa: E402

sample_builders = {
    "unimoral_moral_typology": unimoral._make_typology_samples,
    "unimoral_factor_attribution": unimoral._make_factor_samples,
    "unimoral_consequence_generation": unimoral._make_consequence_samples,
}

expected_ids = [str(sample.id) for sample in sample_builders[task_name]()]
logged_ids = set()
parseable_ids = set()
for path in sorted(log_dir.glob("*.eval"), key=lambda p: p.stat().st_mtime, reverse=True):
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            task_matches = False
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
                eval_meta = header.get("eval") if isinstance(header, dict) else {}
                task_matches = isinstance(eval_meta, dict) and eval_meta.get("task") == task_name
            elif "_journal/start.json" in names:
                start = json.loads(zf.read("_journal/start.json").decode("utf-8"))
                eval_meta = start.get("eval") if isinstance(start, dict) else {}
                task_matches = isinstance(eval_meta, dict) and eval_meta.get("task") == task_name
            if not task_matches:
                continue
            for name in names:
                if not name.startswith("samples/") or not name.endswith(".json"):
                    continue
                sample = json.loads(zf.read(name).decode("utf-8"))
                sample_id = str(sample.get("id") or sample.get("uuid") or name)
                logged_ids.add(sample_id)
                scores = sample.get("scores") if isinstance(sample.get("scores"), dict) else {}
                score_record = next((value for value in scores.values() if isinstance(value, dict)), {})
                answer = str(score_record.get("answer") or "").strip()
                output = sample.get("output") if isinstance(sample.get("output"), dict) else {}
                if task_name == "unimoral_moral_typology":
                    answer = answer if answer in unimoral.TYPOLOGY_PATTERNS else (canonicalize_label_from_output(output, unimoral.TYPOLOGY_PATTERNS)[0] or "")
                elif task_name == "unimoral_factor_attribution":
                    answer = answer if answer in unimoral.FACTOR_PATTERNS else (canonicalize_label_from_output(output, unimoral.FACTOR_PATTERNS)[0] or "")
                elif task_name == "unimoral_consequence_generation" and not answer:
                    answer = consequence_text_from_output(output)[0]
                if answer:
                    parseable_ids.add(sample_id)
    except (BadZipFile, json.JSONDecodeError, KeyError, ValueError):
        continue

prefix = 0
while prefix < len(expected_ids) and expected_ids[prefix] in logged_ids:
    prefix += 1
print(prefix, len(logged_ids), len(parseable_ids), len(expected_ids))
PY
}

sample_ranges_for_task() {
  local log_dir="$1"
  local task_name="$2"
  local force_rerun="$3"
  "$VENV_PYTHON" - "$log_dir" "$task_name" "$ROOT" "$UNIMORAL_DATA_DIR" "$force_rerun" <<'PY'
import json
import os
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

log_dir = Path(sys.argv[1])
task_name = sys.argv[2]
root = Path(sys.argv[3])
os.environ["UNIMORAL_DATA_DIR"] = sys.argv[4]
force_rerun = sys.argv[5] == "1"
rerun_unparsed = force_rerun and os.getenv("UNIMORAL_RERUN_UNPARSED", "0") == "1"
max_gap = int(os.getenv("UNIMORAL_RERUN_UNPARSED_MAX_GAP", "0")) if rerun_unparsed else 0
os.environ.setdefault("UNIMORAL_LANGUAGE", "all")
os.environ.setdefault("UNIMORAL_MODE", "np")
sys.path.insert(0, str(root / "src" / "inspect"))

from evals import unimoral  # noqa: E402
from evals._benchmark_utils import canonicalize_label_from_output, consequence_text_from_output  # noqa: E402

sample_builders = {
    "unimoral_moral_typology": unimoral._make_typology_samples,
    "unimoral_factor_attribution": unimoral._make_factor_samples,
    "unimoral_consequence_generation": unimoral._make_consequence_samples,
}

expected_ids = [str(sample.id) for sample in sample_builders[task_name]()]
if force_rerun and not rerun_unparsed:
    print(f"0 {len(expected_ids)}")
    raise SystemExit(0)

logged_ids = set()
parseable_ids = set()
for path in sorted(log_dir.glob("*.eval"), key=lambda p: p.stat().st_mtime, reverse=True):
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            task_matches = False
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
                eval_meta = header.get("eval") if isinstance(header, dict) else {}
                task_matches = isinstance(eval_meta, dict) and eval_meta.get("task") == task_name
            elif "_journal/start.json" in names:
                start = json.loads(zf.read("_journal/start.json").decode("utf-8"))
                eval_meta = start.get("eval") if isinstance(start, dict) else {}
                task_matches = isinstance(eval_meta, dict) and eval_meta.get("task") == task_name
            if not task_matches:
                continue
            for name in names:
                if not name.startswith("samples/") or not name.endswith(".json"):
                    continue
                sample = json.loads(zf.read(name).decode("utf-8"))
                sample_id = str(sample.get("id") or sample.get("uuid") or name)
                logged_ids.add(sample_id)
                scores = sample.get("scores") if isinstance(sample.get("scores"), dict) else {}
                score_record = next((value for value in scores.values() if isinstance(value, dict)), {})
                answer = str(score_record.get("answer") or "").strip()
                output = sample.get("output") if isinstance(sample.get("output"), dict) else {}
                if task_name == "unimoral_moral_typology":
                    answer = answer if answer in unimoral.TYPOLOGY_PATTERNS else (canonicalize_label_from_output(output, unimoral.TYPOLOGY_PATTERNS)[0] or "")
                elif task_name == "unimoral_factor_attribution":
                    answer = answer if answer in unimoral.FACTOR_PATTERNS else (canonicalize_label_from_output(output, unimoral.FACTOR_PATTERNS)[0] or "")
                elif task_name == "unimoral_consequence_generation" and not answer:
                    answer = consequence_text_from_output(output)[0]
                if answer:
                    parseable_ids.add(sample_id)
    except (BadZipFile, json.JSONDecodeError, KeyError, ValueError):
        continue

covered_ids = parseable_ids if rerun_unparsed else logged_ids
missing = [idx for idx, sample_id in enumerate(expected_ids) if sample_id not in covered_ids]
if not missing:
    raise SystemExit(0)

start = previous = missing[0]
for idx in missing[1:]:
    if idx <= previous + 1 + max_gap:
        previous = idx
        continue
    print(f"{start} {previous + 1}")
    start = previous = idx
print(f"{start} {previous + 1}")
PY
}

write_failure() {
  local line_label="$1"
  local task_name="$2"
  local reason="$3"
  local log_path="$4"
  local category="$5"
  local checklist="$RUN_BASE/unimoral-failure-checklist.csv"
  if [[ ! -f "$checklist" ]]; then
    echo "line_label,task_name,status,reason,log_path,category,timestamp" > "$checklist"
  fi
  printf '%s,%s,failed,%s,%s,%s,%s\n' "$line_label" "$task_name" "$reason" "$log_path" "$category" "$(now_iso)" >> "$checklist"
}

run_one() {
  local line_label="$1"
  local slug="$2"
  local route="$3"
  local profile="$4"
  local task_name="$5"
  local task_spec="$6"
  local resume_env="$7"
  local log_dir="$LOG_BASE/$slug"
  local stdout_dir="$RUN_BASE/$slug"
  local stdout_path="$stdout_dir/${task_name}.txt"
  local status
  local progress expected
  local attempts
  local rc
  local start_at
  local range_specs=()
  local range_spec
  local range_start range_end range_limit
  local range_ok

  mkdir -p "$log_dir" "$stdout_dir"

  status="$(eval_status_for_task "$log_dir" "$task_name" || true)"
  if [[ "$status" == "success" && "$FORCE_RERUN" != "1" ]]; then
    echo "[$(now_iso)] SKIP line=$line_label task=$task_name reason=already_success"
    return 0
  fi
  if [[ "$status" == "running" ]]; then
    echo "[$(now_iso)] SKIP line=$line_label task=$task_name reason=already_running"
    return 0
  fi

  configure_routed_model "$route"
  read -r progress expected <<< "$(sample_progress_for_task "$log_dir" "$task_name")"
  while IFS= read -r range_spec; do
    [[ -n "$range_spec" ]] && range_specs+=("$range_spec")
  done < <(sample_ranges_for_task "$log_dir" "$task_name" "$FORCE_RERUN")

  if [[ "$UNIMORAL_DRY_RUN" == "1" ]]; then
    local range_summary
    local prefix_progress logged_count parseable_count coverage_expected
    range_summary="none"
    if (( ${#range_specs[@]} > 0 )); then
      range_summary="$(printf '%s;' "${range_specs[@]}")"
    fi
    read -r prefix_progress logged_count parseable_count coverage_expected <<< "$(sample_coverage_for_task "$log_dir" "$task_name")"
    echo "[$(now_iso)] DRY_RUN line=$line_label task=$task_name route=$route routed_model=$ROUTED_MODEL provider=$ROUTED_PROVIDER key_var=$ROUTED_KEY_VAR key_state=$ROUTED_KEY_STATE prefix_progress=$prefix_progress logged=$logged_count parseable=$parseable_count expected=$coverage_expected ranges=${range_summary:-none}"
    return 0
  fi

  if ! minimax_execution_allowed "$profile"; then
    echo "[$(now_iso)] BLOCK line=$line_label task=$task_name reason=minimax_requires_UNIMORAL_ALLOW_MINIMAX"
    write_failure "$line_label" "$task_name" "minimax_requires_UNIMORAL_ALLOW_MINIMAX" "$stdout_path" "approval"
    return 1
  fi

  start_at="$(now_iso)"
  record_routing_metadata "$slug" "$task_name" "$start_at"

  if [[ "$ROUTED_KEY_STATE" != "present" ]]; then
    echo "[$(now_iso)] FAIL line=$line_label task=$task_name provider=$ROUTED_PROVIDER key_var=$ROUTED_KEY_VAR reason=missing_provider_api_key"
    write_failure "$line_label" "$task_name" "missing_provider_api_key:$ROUTED_KEY_VAR" "$stdout_path" "api"
    return 1
  fi
  if [[ "${#range_specs[@]}" == "0" ]]; then
    echo "[$(now_iso)] SKIP line=$line_label task=$task_name reason=no_missing_logged_samples prefix_progress=$progress expected=$expected"
    return 0
  fi

  for range_spec in "${range_specs[@]}"; do
    read -r range_start range_end <<< "$range_spec"
    range_limit=$((range_end - range_start))
    range_ok=0
    attempts=0
    while (( attempts < 2 )); do
      attempts=$((attempts + 1))
      (
        set +e
        export UNIMORAL_DATA_DIR
        export UNIMORAL_LANGUAGE=all
        export UNIMORAL_MODE=np
        export PYTHONUNBUFFERED=1
        export "$resume_env=$range_start"
        unset CEI_PROMPT_PREFIX CEI_MIN_MAX_TOKENS || true
        args=()
        route_args=(--model "$ROUTED_MODEL")
        if [[ -n "$ROUTED_BASE_URL" ]]; then
          route_args+=(--model_base_url "$ROUTED_BASE_URL")
        fi
        case "$profile" in
          minimax_reasoning)
            # MiniMax M2 endpoints currently require hidden reasoning on
            # OpenRouter. Cap hidden reasoning and keep enough output budget for
            # the visible final answer.
            export CEI_MIN_MAX_TOKENS="${UNIMORAL_REASONING_MIN_TOKENS:-2048}"
            if [[ "$ROUTED_PROVIDER" == "openrouter" ]]; then
              args+=(--extra_body_json "{\"reasoning\":{\"max_tokens\":${UNIMORAL_MINIMAX_REASONING_MAX_TOKENS:-512},\"exclude\":false},\"provider\":{\"sort\":\"throughput\"}}")
            fi
            ;;
          qwen)
            export CEI_PROMPT_PREFIX="/no_think"
            args+=(--reasoning_effort none --model_args "reasoning_enabled=False" --extra_body_json '{"chat_template_kwargs":{"enable_thinking":false}}')
            ;;
          deepseek_reasoning)
            export CEI_PROMPT_PREFIX="/no_think"
            args+=(--reasoning_effort none --model_args "reasoning_enabled=False" --extra_body_json '{"reasoning":{"effort":"minimal","exclude":true}}')
            ;;
          deepseek_distill_visible)
            export CEI_PROMPT_PREFIX="/no_think"
            export CEI_MIN_MAX_TOKENS="${UNIMORAL_REASONING_MIN_TOKENS:-2048}"
            if [[ "$ROUTED_PROVIDER" == "openrouter" ]]; then
              if [[ "${UNIMORAL_DEEPSEEK_DISTILL_REASONING_MAX_TOKENS:-256}" == "0" ]]; then
                args+=(--reasoning_effort none --extra_body_json '{"provider":{"sort":"throughput"}}')
              else
                args+=(--extra_body_json "{\"reasoning\":{\"max_tokens\":${UNIMORAL_DEEPSEEK_DISTILL_REASONING_MAX_TOKENS:-256},\"exclude\":false},\"provider\":{\"sort\":\"throughput\"}}")
              fi
            else
              args+=(--reasoning_effort none)
            fi
            ;;
          deepseek_r1_mandatory_reasoning)
            export CEI_PROMPT_PREFIX="/no_think"
            export CEI_MIN_MAX_TOKENS="${UNIMORAL_REASONING_MIN_TOKENS:-2048}"
            if [[ "$ROUTED_PROVIDER" == "openrouter" ]]; then
              args+=(--extra_body_json "{\"reasoning\":{\"max_tokens\":${UNIMORAL_DEEPSEEK_R1_REASONING_MAX_TOKENS:-512},\"exclude\":false},\"provider\":{\"sort\":\"throughput\"}}")
            fi
            ;;
          openai|plain)
            ;;
          *)
            echo "Unknown run profile: $profile" >&2
            exit 97
            ;;
        esac
        echo "[$(now_iso)] START line=$line_label task=$task_name route=$route routed_model=$ROUTED_MODEL provider=$ROUTED_PROVIDER provider_model=$ROUTED_PROVIDER_MODEL base_url=$ROUTED_BASE_URL key_var=$ROUTED_KEY_VAR attempt=$attempts range=${range_start}:${range_end} limit=$range_limit prefix_progress=$progress expected=$expected profile=$profile"
        "$VENV_PYTHON" "$RUNNER" \
          --tasks "$task_spec" \
          "${route_args[@]}" \
          --temperature 0 \
          --limit "$range_limit" \
          --no_sandbox \
          --max_connections "$MAX_CONNECTIONS_DEFAULT" \
          --log_dir "$log_dir" \
          ${args[@]+"${args[@]}"}
        rc=$?
        echo "[$(now_iso)] END line=$line_label task=$task_name route=$route attempt=$attempts range=${range_start}:${range_end} rc=$rc"
        exit "$rc"
      ) > "$stdout_path" 2>&1
      rc=$?
      if [[ "$rc" == "0" ]]; then
        range_ok=1
        break
      fi
    done
    if [[ "$range_ok" != "1" ]]; then
      write_failure "$line_label" "$task_name" "nonzero_after_retry_range_${range_start}_${range_end}" "$stdout_path" "runtime"
      return 1
    fi
    read -r progress expected <<< "$(sample_progress_for_task "$log_dir" "$task_name")"
  done

  status="$(eval_status_for_task "$log_dir" "$task_name" || true)"
  read -r progress expected <<< "$(sample_progress_for_task "$log_dir" "$task_name")"
  if [[ "$status" == "success" || "$FORCE_RERUN" == "1" || ( "$progress" =~ ^[0-9]+$ && "$expected" =~ ^[0-9]+$ && "$progress" -ge "$expected" ) ]]; then
    return 0
  fi

  write_failure "$line_label" "$task_name" "nonzero_or_non_success_after_retry" "$stdout_path" "runtime"
  return 1
}

if [[ "${UNIMORAL_SOURCE_ONLY:-0}" == "1" ]]; then
  return 0 2>/dev/null || exit 0
fi

overall_rc=0
for model_entry in "${models[@]}"; do
  IFS="|" read -r line_label slug route profile <<< "$model_entry"
  selected "$line_label" "$MODEL_FILTER" || continue
  if skip_model_line "$line_label" "$slug" "$route" "$profile"; then
    echo "[$(now_iso)] SKIP line=$line_label reason=matches_UNIMORAL_SKIP_MODEL_REGEX regex=$UNIMORAL_SKIP_MODEL_REGEX"
    continue
  fi
  for task_entry in "${tasks[@]}"; do
    IFS="|" read -r task_name task_spec resume_env <<< "$task_entry"
    selected "$task_name" "$TASK_FILTER" || continue
    run_one "$line_label" "$slug" "$route" "$profile" "$task_name" "$task_spec" "$resume_env" || overall_rc=1
  done
done

exit "$overall_rc"
