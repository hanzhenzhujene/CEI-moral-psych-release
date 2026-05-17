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
  python3 - <<'PY'
from datetime import datetime
print(datetime.now().astimezone().isoformat())
PY
}

selected() {
  local name="$1"
  local filter="$2"
  [[ -z "$filter" ]] && return 0
  python3 - "$name" "$filter" <<'PY'
import sys
name = sys.argv[1]
requested = {part.strip() for part in sys.argv[2].split(",") if part.strip()}
raise SystemExit(0 if name in requested else 1)
PY
}

eval_status_for_task() {
  local log_dir="$1"
  local task_name="$2"
  python3 - "$log_dir" "$task_name" <<'PY'
import json
import time
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

log_dir = Path(sys.argv[1])
task_name = sys.argv[2]
best = ""
for path in sorted(log_dir.glob("*.eval"), key=lambda p: p.stat().st_mtime, reverse=True):
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
            elif "_journal/start.json" in names and time.time() - path.stat().st_mtime < 6 * 60 * 60:
                start = json.loads(zf.read("_journal/start.json").decode("utf-8"))
                eval_meta = start.get("eval") if isinstance(start, dict) else {}
                if isinstance(eval_meta, dict) and eval_meta.get("task") == task_name:
                    print("running")
                    raise SystemExit(0)
                continue
            else:
                continue
    except (BadZipFile, json.JSONDecodeError, KeyError):
        continue
    eval_meta = header.get("eval") if isinstance(header, dict) else {}
    if not isinstance(eval_meta, dict) or eval_meta.get("task") != task_name:
        continue
    status = str(header.get("status", ""))
    if status == "success":
        print("success")
        raise SystemExit(0)
    best = status or "unknown"
if best:
    print(best)
PY
}

sample_progress_for_task() {
  local log_dir="$1"
  local task_name="$2"
  python3 - "$log_dir" "$task_name" <<'PY'
import json
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
best = 0
for path in sorted(log_dir.glob("*.eval"), key=lambda p: p.stat().st_mtime, reverse=True):
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if "header.json" in names:
                continue
            start = json.loads(zf.read("_journal/start.json").decode("utf-8")) if "_journal/start.json" in names else {}
            eval_meta = start.get("eval") if isinstance(start, dict) else {}
            if not isinstance(eval_meta, dict) or eval_meta.get("task") != task_name:
                continue
            count = sum(1 for name in names if name.startswith("samples/") and name.endswith(".json"))
            best = max(best, count)
    except (BadZipFile, json.JSONDecodeError, KeyError):
        continue
print(best, expected)
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

provider_key_ok() {
  local route="$1"
  if [[ "$route" == openrouter/* ]]; then
    [[ -n "${OPENROUTER_API_KEY:-}" ]]
  elif [[ "$route" == openai/* ]]; then
    [[ -n "${OPENAI_API_KEY:-}" ]]
  else
    return 1
  fi
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

  mkdir -p "$log_dir" "$stdout_dir"

  status="$(eval_status_for_task "$log_dir" "$task_name" || true)"
  if [[ "$status" == "success" ]]; then
    echo "[$(now_iso)] SKIP line=$line_label task=$task_name reason=already_success"
    return 0
  fi
  if [[ "$status" == "running" ]]; then
    echo "[$(now_iso)] SKIP line=$line_label task=$task_name reason=already_running"
    return 0
  fi

  if ! provider_key_ok "$route"; then
    echo "[$(now_iso)] FAIL line=$line_label task=$task_name reason=missing_provider_api_key"
    write_failure "$line_label" "$task_name" "missing_provider_api_key" "$stdout_path" "api"
    return 1
  fi

  read -r progress expected <<< "$(sample_progress_for_task "$log_dir" "$task_name")"
  attempts=0
  while (( attempts < 2 )); do
    attempts=$((attempts + 1))
    (
      set +e
      export UNIMORAL_DATA_DIR
      export UNIMORAL_LANGUAGE=all
      export UNIMORAL_MODE=np
      export PYTHONUNBUFFERED=1
      if [[ "$progress" =~ ^[0-9]+$ ]] && (( progress > 0 )) && (( progress < expected )); then
        export "$resume_env=$progress"
      fi
      unset CEI_PROMPT_PREFIX CEI_MIN_MAX_TOKENS || true
      args=()
      case "$profile" in
        minimax_reasoning)
          # MiniMax M2 endpoints currently require hidden reasoning on
          # OpenRouter. A larger budget is needed for the visible final answer.
          export CEI_MIN_MAX_TOKENS="${UNIMORAL_REASONING_MIN_TOKENS:-2048}"
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
          args+=(--reasoning_effort none --extra_body_json '{"reasoning":{"enabled":false,"exclude":true},"include_reasoning":false}')
          ;;
        deepseek_r1_mandatory_reasoning)
          export CEI_PROMPT_PREFIX="/no_think"
          export CEI_MIN_MAX_TOKENS="${UNIMORAL_REASONING_MIN_TOKENS:-2048}"
          args+=(--extra_body_json '{"reasoning":{"effort":"minimal","exclude":true}}')
          ;;
        openai|plain)
          ;;
        *)
          echo "Unknown run profile: $profile" >&2
          exit 97
          ;;
      esac
      echo "[$(now_iso)] START line=$line_label task=$task_name route=$route attempt=$attempts progress=$progress expected=$expected profile=$profile"
      "$VENV_PYTHON" "$RUNNER" \
        --tasks "$task_spec" \
        --model "$route" \
        --temperature 0 \
        --no_sandbox \
        --max_connections "$MAX_CONNECTIONS_DEFAULT" \
        --log_dir "$log_dir" \
        ${args[@]+"${args[@]}"}
      rc=$?
      echo "[$(now_iso)] END line=$line_label task=$task_name route=$route attempt=$attempts rc=$rc"
      exit "$rc"
    ) > "$stdout_path" 2>&1
    rc=$?
    status="$(eval_status_for_task "$log_dir" "$task_name" || true)"
    if [[ "$rc" == "0" && "$status" == "success" ]]; then
      return 0
    fi
    read -r progress expected <<< "$(sample_progress_for_task "$log_dir" "$task_name")"
  done

  write_failure "$line_label" "$task_name" "nonzero_or_non_success_after_retry" "$stdout_path" "runtime"
  return 1
}

overall_rc=0
for model_entry in "${models[@]}"; do
  IFS="|" read -r line_label slug route profile <<< "$model_entry"
  selected "$line_label" "$MODEL_FILTER" || continue
  for task_entry in "${tasks[@]}"; do
    IFS="|" read -r task_name task_spec resume_env <<< "$task_entry"
    selected "$task_name" "$TASK_FILTER" || continue
    run_one "$line_label" "$slug" "$route" "$profile" "$task_name" "$task_spec" "$resume_env" || overall_rc=1
  done
done

exit "$overall_rc"
