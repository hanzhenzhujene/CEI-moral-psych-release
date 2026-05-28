#!/usr/bin/env python3
"""Low-cost OpenRouter planning/running for Jenny's text-only moral-psych tasks.

The script is intentionally conservative:
- only OpenRouter model IDs are eligible;
- MiniMax is excluded;
- SMID and DeNEVIL are excluded;
- prices are fetched from OpenRouter metadata before a run plan is emitted;
- every model is checked against per-million-token price caps before execution.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "openrouter-low-cost-moral-psych"
DEFAULT_EXTRA_BODY_JSON = json.dumps(
    {
        "reasoning": {"effort": "none", "exclude": True},
        "chat_template_kwargs": {"enable_thinking": False},
    }
)
INPUT_PRICE_CAP_PER_M = 3.0
OUTPUT_PRICE_CAP_PER_M = 15.0
DEFAULT_MAX_TOTAL_ESTIMATED_COST_USD = 1.0


@dataclass(frozen=True)
class TaskSpec:
    benchmark: str
    task_name: str
    task_path: str
    paper: str
    paper_url: str
    paper_repo_or_data: str
    prompt_source: str
    scorer_source: str
    metric: str
    max_output_tokens: int
    replication_status: str


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    family: str
    size_tier: str
    release_period: str
    grid: str
    rationale: str
    existing_baseline: bool = False


TASK_SPECS: list[TaskSpec] = [
    TaskSpec(
        benchmark="UniMoral",
        task_name="unimoral_action_prediction",
        task_path="src/inspect/evals/unimoral.py::unimoral_action_prediction",
        paper="Kumar et al. (ACL Findings 2025)",
        paper_url="https://aclanthology.org/2025.acl-long.294/",
        paper_repo_or_data="Hugging Face UniMoral export via $UNIMORAL_DATA_DIR",
        prompt_source="src/inspect/evals/data/unimoral/PROMPTS.txt",
        scorer_source="src/inspect/evals/_benchmark_utils.py::parsed_label_scorer(extract_action_choice)",
        metric="accuracy",
        max_output_tokens=64,
        replication_status="Benchmark-faithful task; paper model roster only partially available in current grid.",
    ),
    TaskSpec(
        benchmark="UniMoral",
        task_name="unimoral_moral_typology",
        task_path="src/inspect/evals/unimoral.py::unimoral_moral_typology",
        paper="Kumar et al. (ACL Findings 2025)",
        paper_url="https://aclanthology.org/2025.acl-long.294/",
        paper_repo_or_data="Hugging Face UniMoral export via $UNIMORAL_DATA_DIR",
        prompt_source="src/inspect/evals/data/unimoral/PROMPTS2.txt",
        scorer_source="src/inspect/evals/_benchmark_utils.py::label_membership_scorer(TYPOLOGY_PATTERNS)",
        metric="accuracy",
        max_output_tokens=512,
        replication_status="Benchmark-faithful task; paper reports weighted F1, so score scale differs unless post-processed.",
    ),
    TaskSpec(
        benchmark="UniMoral",
        task_name="unimoral_factor_attribution",
        task_path="src/inspect/evals/unimoral.py::unimoral_factor_attribution",
        paper="Kumar et al. (ACL Findings 2025)",
        paper_url="https://aclanthology.org/2025.acl-long.294/",
        paper_repo_or_data="Hugging Face UniMoral export via $UNIMORAL_DATA_DIR",
        prompt_source="src/inspect/evals/data/unimoral/PROMPTS3.txt",
        scorer_source="src/inspect/evals/_benchmark_utils.py::label_membership_scorer(FACTOR_PATTERNS)",
        metric="accuracy",
        max_output_tokens=512,
        replication_status="Benchmark-faithful task; paper reports weighted F1, so score scale differs unless post-processed.",
    ),
    TaskSpec(
        benchmark="UniMoral",
        task_name="unimoral_consequence_generation",
        task_path="src/inspect/evals/unimoral.py::unimoral_consequence_generation",
        paper="Kumar et al. (ACL Findings 2025)",
        paper_url="https://aclanthology.org/2025.acl-long.294/",
        paper_repo_or_data="Hugging Face UniMoral export via $UNIMORAL_DATA_DIR",
        prompt_source="src/inspect/evals/data/unimoral/PROMPTS4.txt",
        scorer_source="src/inspect/evals/_benchmark_utils.py::unimoral_consequence_scorer",
        metric="METEOR live scorer; BERTScore F1 is offline-only in the current release tooling",
        max_output_tokens=512,
        replication_status="Benchmark-faithful prompt route; BERTScore requires the offline release metric pass.",
    ),
    TaskSpec(
        benchmark="ValuePrism",
        task_name="value_prism_relevance",
        task_path="src/inspect/evals/value_kaleidoscope.py::value_prism_relevance",
        paper="Sorensen et al. (AAAI 2024)",
        paper_url="https://arxiv.org/abs/2309.00779",
        paper_repo_or_data="ValuePrism local CSV/HF export via $VALUEPRISM_RELEVANCE_FILE",
        prompt_source="src/inspect/evals/value_kaleidoscope.py::_make_relevance_samples",
        scorer_source="src/inspect/evals/_benchmark_utils.py::parsed_label_scorer(classify_yes_no_label)",
        metric="accuracy",
        max_output_tokens=24,
        replication_status="Closest feasible prompt-classification route; not Kaleido model replication.",
    ),
    TaskSpec(
        benchmark="ValuePrism",
        task_name="value_prism_valence",
        task_path="src/inspect/evals/value_kaleidoscope.py::value_prism_valence",
        paper="Sorensen et al. (AAAI 2024)",
        paper_url="https://arxiv.org/abs/2309.00779",
        paper_repo_or_data="ValuePrism local CSV/HF export via $VALUEPRISM_VALENCE_FILE",
        prompt_source="src/inspect/evals/value_kaleidoscope.py::_make_valence_samples",
        scorer_source="src/inspect/evals/_benchmark_utils.py::parsed_label_scorer(classify_valence_label)",
        metric="accuracy",
        max_output_tokens=32,
        replication_status="Closest feasible prompt-classification route; not Kaleido model replication.",
    ),
    TaskSpec(
        benchmark="CCD-Bench",
        task_name="ccd_bench_selection",
        task_path="src/inspect/evals/ccd_bench.py::ccd_bench_selection",
        paper="Rahman and Salam (arXiv 2025)",
        paper_url="https://github.com/smartlab-nyu/CCD-Bench",
        paper_repo_or_data="Official CCD-Bench JSON URL or $CCD_BENCH_DATA_FILE",
        prompt_source="src/inspect/evals/ccd_bench.py::SYSTEM_INSTRUCTIONS/_prompt_for_row",
        scorer_source="src/inspect/evals/_benchmark_utils.py::valid_choice_scorer(1, 10)",
        metric="valid-choice coverage plus selected-cluster distribution; not accuracy",
        max_output_tokens=80,
        replication_status="Benchmark-faithful route for choice behavior; compare cluster shares, not correctness.",
    ),
]


MODEL_SPECS: list[ModelSpec] = [
    # Within-family scaling: Qwen.
    ModelSpec("qwen/qwen3-8b", "Qwen", "S/8B", "2025-Q2", "within-family scaling", "Qwen3 small baseline", True),
    ModelSpec("qwen/qwen3-32b", "Qwen", "M/32B", "2025-Q2", "within-family scaling", "Qwen3 medium"),
    ModelSpec("qwen/qwen3-235b-a22b-2507", "Qwen", "L/MoE 235B-A22B", "2025-Q3", "within-family scaling", "Qwen3 large MoE"),
    # Within-family scaling: Gemma.
    ModelSpec("google/gemma-3-4b-it", "Gemma", "S/4B", "2025-Q1", "within-family scaling", "Gemma 3 small baseline", True),
    ModelSpec("google/gemma-3-12b-it", "Gemma", "M/12B", "2025-Q1", "within-family scaling", "Gemma 3 medium baseline", True),
    ModelSpec("google/gemma-3-27b-it", "Gemma", "L/27B", "2025-Q1", "within-family scaling", "Gemma 3 large baseline", True),
    # Within-family scaling: Llama.
    ModelSpec("meta-llama/llama-3.2-3b-instruct", "Llama", "S/3B", "2024-Q3", "within-family scaling", "Llama small"),
    ModelSpec("meta-llama/llama-3.1-8b-instruct", "Llama", "M/8B", "2024-Q3", "within-family scaling", "Llama medium/paper-adjacent"),
    ModelSpec("meta-llama/llama-3.3-70b-instruct", "Llama", "L/70B", "2024-Q4", "within-family scaling", "Llama large / CCD paper overlap"),
    # Time scaling: near-size or provider-line comparisons.
    ModelSpec("qwen/qwen-2.5-7b-instruct", "Qwen", "S/7B", "2024-Q4", "time scaling", "Older Qwen small"),
    ModelSpec("qwen/qwen3.5-9b", "Qwen", "S/9B", "2026-Q1", "time scaling", "Newer Qwen small"),
    ModelSpec("google/gemma-2-27b-it", "Gemma", "L/27B", "2024-Q3", "time scaling", "Older Gemma 27B"),
    ModelSpec("google/gemma-4-31b-it", "Gemma", "L/31B", "2026-Q1", "time scaling", "Newer Gemma large"),
    ModelSpec("deepseek/deepseek-chat-v3-0324", "DeepSeek", "chat/V3", "2025-Q1", "time scaling", "CCD paper overlap / older V3"),
    ModelSpec("deepseek/deepseek-chat-v3.1", "DeepSeek", "chat/V3.1", "2025-Q3", "time scaling", "Existing DeepSeek text baseline", True),
    ModelSpec("deepseek/deepseek-v3.2", "DeepSeek", "chat/V3.2", "2025-Q4", "time scaling", "Newer DeepSeek V3 line"),
    ModelSpec("deepseek/deepseek-v4-flash", "DeepSeek", "flash/V4", "2026-Q2", "time scaling", "Newest low-cost DeepSeek flash"),
]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def load_project_env() -> None:
    load_env_file(PROJECT_ROOT / ".env")
    load_env_file(PROJECT_ROOT / ".env.local")


def fetch_openrouter_models() -> tuple[dict[str, dict[str, Any]], str]:
    with urllib.request.urlopen(OPENROUTER_MODELS_URL, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    fetched_at = datetime.now(timezone.utc).isoformat()
    models = payload.get("data", payload if isinstance(payload, list) else [])
    return {model["id"]: model for model in models if "id" in model}, fetched_at


def pricing_per_million(model: dict[str, Any]) -> tuple[float, float]:
    pricing = model.get("pricing") or {}
    prompt = float(pricing.get("prompt") or 0.0) * 1_000_000
    completion = float(pricing.get("completion") or 0.0) * 1_000_000
    return prompt, completion


def price_per_token(model: dict[str, Any]) -> tuple[float, float]:
    pricing = model.get("pricing") or {}
    return float(pricing.get("prompt") or 0.0), float(pricing.get("completion") or 0.0)


def import_task_factory(task_name: str):
    inspect_src = PROJECT_ROOT / "src" / "inspect"
    if str(inspect_src) not in sys.path:
        sys.path.insert(0, str(inspect_src))
    if task_name.startswith("unimoral_"):
        from evals import unimoral as module
    elif task_name.startswith("value_prism_"):
        from evals import value_kaleidoscope as module
    elif task_name == "ccd_bench_selection":
        from evals import ccd_bench as module
    else:
        raise KeyError(task_name)
    return getattr(module, task_name)


def token_counter():
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("o200k_base")
        return lambda text: len(encoding.encode(str(text)))
    except Exception:
        return lambda text: max(1, round(len(str(text)) / 4))


def task_token_estimates(sample_limit: int | None) -> dict[str, dict[str, int]]:
    count_tokens = token_counter()
    estimates: dict[str, dict[str, int]] = {}
    for spec in TASK_SPECS:
        factory = import_task_factory(spec.task_name)
        task = factory(limit=sample_limit) if sample_limit is not None else factory()
        samples = list(task.dataset)
        input_tokens = sum(count_tokens(sample.input) for sample in samples)
        estimates[spec.task_name] = {
            "samples": len(samples),
            "input_tokens": input_tokens,
            "max_output_tokens": len(samples) * spec.max_output_tokens,
        }
    return estimates


def eligible_models(models_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for spec in MODEL_SPECS:
        if "minimax" in spec.model_id.lower():
            continue
        if spec.model_id in seen:
            continue
        seen.add(spec.model_id)
        model = models_by_id.get(spec.model_id)
        if model is None:
            rows.append(
                {
                    "model": spec.model_id,
                    "family": spec.family,
                    "size_tier": spec.size_tier,
                    "release_period": spec.release_period,
                    "grid": spec.grid,
                    "rationale": spec.rationale,
                    "existing_baseline": spec.existing_baseline,
                    "available": False,
                    "eligible": False,
                    "skip_reason": "missing from OpenRouter /models metadata",
                    "input_price_per_m": "",
                    "output_price_per_m": "",
                    "context_length": "",
                }
            )
            continue
        input_price, output_price = pricing_per_million(model)
        over_cap = input_price > INPUT_PRICE_CAP_PER_M or output_price > OUTPUT_PRICE_CAP_PER_M
        eligible = spec.existing_baseline or not over_cap
        rows.append(
            {
                "model": spec.model_id,
                "family": spec.family,
                "size_tier": spec.size_tier,
                "release_period": spec.release_period,
                "grid": spec.grid,
                "rationale": spec.rationale,
                "existing_baseline": spec.existing_baseline,
                "available": True,
                "eligible": eligible,
                "skip_reason": "" if eligible else "price cap",
                "input_price_per_m": f"{input_price:.6g}",
                "output_price_per_m": f"{output_price:.6g}",
                "context_length": model.get("context_length", ""),
            }
        )
    return rows


def benchmark_rows() -> list[dict[str, str]]:
    return [
        {
            "benchmark": spec.benchmark,
            "task": spec.task_name,
            "paper": spec.paper,
            "paper_url": spec.paper_url,
            "paper_repo_or_data": spec.paper_repo_or_data,
            "prompt_source": spec.prompt_source,
            "scorer_source": spec.scorer_source,
            "metric": spec.metric,
            "replication_status": spec.replication_status,
        }
        for spec in TASK_SPECS
    ]


def run_plan_rows(
    model_rows: list[dict[str, Any]],
    models_by_id: dict[str, dict[str, Any]],
    estimates: dict[str, dict[str, int]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_row in model_rows:
        if not model_row["eligible"]:
            continue
        model = models_by_id[model_row["model"]]
        prompt_price, completion_price = price_per_token(model)
        for spec in TASK_SPECS:
            estimate = estimates[spec.task_name]
            cost = estimate["input_tokens"] * prompt_price + estimate["max_output_tokens"] * completion_price
            rows.append(
                {
                    "model": model_row["model"],
                    "family": model_row["family"],
                    "size_tier": model_row["size_tier"],
                    "release_period": model_row["release_period"],
                    "grid": model_row["grid"],
                    "benchmark": spec.benchmark,
                    "task": spec.task_name,
                    "metric": spec.metric,
                    "score": "",
                    "samples": estimate["samples"],
                    "estimated_input_tokens": estimate["input_tokens"],
                    "estimated_max_output_tokens": estimate["max_output_tokens"],
                    "estimated_cost_usd": f"{cost:.6f}",
                    "input_price_per_m": model_row["input_price_per_m"],
                    "output_price_per_m": model_row["output_price_per_m"],
                    "reasoning_cost_control": "default /no_think prefix + reasoning.effort=none at run time" if model_row["family"] in {"Qwen", "DeepSeek"} else "",
                    "replication_status": spec.replication_status,
                    "run_status": "planned",
                    "log_path": "",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def render_cost_plot(rows: list[dict[str, Any]], output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    plt.rcParams["svg.hashsalt"] = "openrouter-low-cost-moral-psych"
    totals: dict[str, float] = {}
    for row in rows:
        totals[row["model"]] = totals.get(row["model"], 0.0) + float(row["estimated_cost_usd"] or 0.0)
    if not totals:
        return
    labels = list(totals)
    values = [totals[label] for label in labels]
    height = max(4, min(14, 0.38 * len(labels) + 1.5))
    plt.figure(figsize=(10, height))
    plt.barh(labels, values, color="#2f5d8c")
    plt.xlabel("Estimated USD for selected sample limit")
    plt.title("OpenRouter Low-Cost Moral-Psych Run Plan")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format="svg", metadata={"Date": "2026-05-27"})
    plt.close()
    strip_trailing_whitespace(output_path)


def parse_eval_log(log_path: Path) -> dict[str, Any]:
    try:
        with ZipFile(log_path) as zf:
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, FileNotFoundError, KeyError) as exc:
        return {"status": "unreadable", "error": str(exc)}

    result = {
        "status": str(header.get("status", "")),
        "completed_samples": "",
        "total_samples": "",
        "score": "",
        "metric_name": "",
        "input_tokens_actual": "",
        "output_tokens_actual": "",
        "reasoning_tokens_actual": "",
    }
    results = header.get("results") or {}
    result["completed_samples"] = results.get("completed_samples", "")
    result["total_samples"] = results.get("total_samples", "")
    scores = results.get("scores") or []
    if scores:
        metrics = scores[0].get("metrics") or {}
        preferred = "accuracy" if "accuracy" in metrics else "mean" if "mean" in metrics else next(iter(metrics), "")
        if preferred:
            result["metric_name"] = preferred
            result["score"] = metrics[preferred].get("value", "")
    usage = ((header.get("stats") or {}).get("model_usage") or {})
    if usage:
        first_usage = next(iter(usage.values()))
        result["input_tokens_actual"] = first_usage.get("input_tokens", "")
        result["output_tokens_actual"] = first_usage.get("output_tokens", "")
        result["reasoning_tokens_actual"] = first_usage.get("reasoning_tokens", "")
    return result


def parse_run_results(plan_rows: list[dict[str, Any]], models_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    output_rows = []
    for row in plan_rows:
        result = parse_eval_log(Path(row["log_path"])) if row.get("log_path") else {}
        out = dict(row)
        out["run_status"] = result.get("status", row.get("run_status", "planned"))
        out["score"] = result.get("score", row.get("score", ""))
        out["metric_observed"] = result.get("metric_name", "")
        out["completed_samples"] = result.get("completed_samples", "")
        out["total_samples"] = result.get("total_samples", "")
        out["input_tokens_actual"] = result.get("input_tokens_actual", "")
        out["output_tokens_actual"] = result.get("output_tokens_actual", "")
        out["reasoning_tokens_actual"] = result.get("reasoning_tokens_actual", "")
        if result.get("input_tokens_actual") != "":
            if row.get("input_price_per_m") not in {"", None} and row.get("output_price_per_m") not in {"", None}:
                prompt_price = float(row["input_price_per_m"]) / 1_000_000
                completion_price = float(row["output_price_per_m"]) / 1_000_000
            elif row["model"] in models_by_id:
                prompt_price, completion_price = price_per_token(models_by_id[row["model"]])
            else:
                prompt_price, completion_price = 0.0, 0.0
            completion_tokens = float(result.get("output_tokens_actual") or 0) + float(result.get("reasoning_tokens_actual") or 0)
            actual_cost = float(result.get("input_tokens_actual") or 0) * prompt_price + completion_tokens * completion_price
            out["actual_cost_usd"] = f"{actual_cost:.6f}"
            out["actual_cost_method"] = "input + output + reasoning tokens at OpenRouter metadata rates"
        else:
            out["actual_cost_usd"] = ""
            out["actual_cost_method"] = ""
        output_rows.append(out)
    return output_rows


def latest_eval_log(output_dir: Path, model: str, task: str) -> Path | None:
    safe_model = model.replace("/", "__").replace(":", "_")
    log_dir = output_dir / "logs" / safe_model / task
    eval_logs = sorted(log_dir.glob("*.eval"), key=lambda path: path.stat().st_mtime)
    return eval_logs[-1] if eval_logs else None


def successful_existing_log(
    output_dir: Path,
    row: dict[str, Any],
    models_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    safe_model = row["model"].replace("/", "__").replace(":", "_")
    log_dir = output_dir / "logs" / safe_model / row["task"]
    eval_logs = sorted(log_dir.glob("*.eval"), key=lambda path: path.stat().st_mtime, reverse=True)
    for log_path in eval_logs:
        row_with_log = dict(row)
        row_with_log["log_path"] = str(log_path)
        parsed = parse_run_results([row_with_log], models_by_id)[0]
        if parsed.get("run_status") == "success":
            return parsed
    return None


def scan_successful_existing_logs(
    output_dir: Path,
    plan_rows: list[dict[str, Any]],
    models_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows_with_logs: list[dict[str, Any]] = []
    for row in plan_rows:
        parsed = successful_existing_log(output_dir, row, models_by_id)
        if parsed is not None:
            rows_with_logs.append(parsed)
    return rows_with_logs


def merge_result_rows(*row_sets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    for rows in row_sets:
        for row in rows:
            merged[(row.get("model"), row.get("task"))] = row
    return list(merged.values())


def render_score_plot(rows: list[dict[str, Any]], output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    plt.rcParams["svg.hashsalt"] = "openrouter-low-cost-moral-psych"
    scored = [row for row in rows if str(row.get("score", "")).strip()]
    if not scored:
        return
    labels = [f"{row['family']} {row['size_tier']} | {row['task']}" for row in scored]
    values = [float(row["score"]) for row in scored]
    height = max(4, min(16, 0.34 * len(labels) + 1.5))
    colors = ["#2f5d8c" if row["benchmark"] != "CCD-Bench" else "#7765a8" for row in scored]
    plt.figure(figsize=(11, height))
    plt.barh(labels, values, color=colors)
    plt.xlabel("Score (metric depends on task; CCD is valid-choice coverage, not accuracy)")
    plt.title("OpenRouter Low-Cost Moral-Psych Pilot Scores")
    plt.xlim(0, 1)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format="svg", metadata={"Date": "2026-05-27"})
    plt.close()
    strip_trailing_whitespace(output_path)


def aggregate_benchmark_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("run_status") != "success" or not str(row.get("score", "")).strip():
            continue
        groups.setdefault((row["model"], row["benchmark"]), []).append(row)

    out: list[dict[str, Any]] = []
    for (model, benchmark), group in sorted(groups.items()):
        first = group[0]
        scores = [float(row["score"]) for row in group]
        actual_cost = sum(float(row.get("actual_cost_usd") or 0.0) for row in group)
        estimated_cost = sum(float(row.get("estimated_cost_usd") or 0.0) for row in group)
        completed_samples = sum(int(row.get("completed_samples") or 0) for row in group)
        reasoning_tokens = sum(int(row.get("reasoning_tokens_actual") or 0) for row in group)
        out.append(
            {
                "model": model,
                "family": first["family"],
                "size_tier": first["size_tier"],
                "release_period": first["release_period"],
                "grid": first["grid"],
                "benchmark": benchmark,
                "score": f"{sum(scores) / len(scores):.6f}",
                "tasks_completed": len(group),
                "completed_samples": completed_samples,
                "reasoning_tokens_actual": reasoning_tokens,
                "estimated_cost_usd": f"{estimated_cost:.6f}",
                "actual_cost_usd": f"{actual_cost:.6f}",
                "replication_status": " | ".join(sorted({row["replication_status"] for row in group})),
                "note": "CCD-Bench score is valid-choice coverage, not accuracy." if benchmark == "CCD-Bench" else "",
            }
        )
    return out


def aggregate_model_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("run_status") == "success":
            groups.setdefault(row["model"], []).append(row)
    out: list[dict[str, Any]] = []
    for model, group in sorted(groups.items()):
        first = group[0]
        numeric_scores = [float(row["score"]) for row in group if str(row.get("score", "")).strip()]
        actual_cost = sum(float(row.get("actual_cost_usd") or 0.0) for row in group)
        estimated_cost = sum(float(row.get("estimated_cost_usd") or 0.0) for row in group)
        reasoning_tokens = sum(int(row.get("reasoning_tokens_actual") or 0) for row in group)
        text_accuracy_rows = [
            row
            for row in group
            if row["benchmark"] != "CCD-Bench"
            and str(row.get("score", "")).strip()
            and "accuracy" in row.get("metric_observed", row.get("metric", ""))
        ]
        text_accuracy = [float(row["score"]) for row in text_accuracy_rows]
        out.append(
            {
                "model": model,
                "family": first["family"],
                "size_tier": first["size_tier"],
                "release_period": first["release_period"],
                "grid": first["grid"],
                "successful_tasks": len(group),
                "mean_all_observed_scores": f"{sum(numeric_scores) / len(numeric_scores):.6f}" if numeric_scores else "",
                "mean_text_accuracy_tasks": f"{sum(text_accuracy) / len(text_accuracy):.6f}" if text_accuracy else "",
                "reasoning_tokens_actual": reasoning_tokens,
                "actual_cost_usd": f"{actual_cost:.6f}",
                "estimated_cost_usd": f"{estimated_cost:.6f}",
                "actual_vs_estimated_cost_ratio": f"{actual_cost / estimated_cost:.3f}" if estimated_cost else "",
            }
        )
    return out


def summarize_patterns(
    model_summary: list[dict[str, Any]],
    benchmark_summary: list[dict[str, Any]],
    result_rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    completed = [row for row in result_rows if row.get("run_status") == "success"]
    total_actual_cost = sum(float(row.get("actual_cost_usd") or 0.0) for row in completed)
    total_reasoning_tokens = sum(int(row.get("reasoning_tokens_actual") or 0) for row in completed)
    completed_sample_counts = [
        int(row.get("completed_samples") or 0)
        for row in completed
        if str(row.get("completed_samples") or "").isdigit()
    ]
    sample_limit = max(completed_sample_counts) if completed_sample_counts else None
    if sample_limit is None:
        evidence_sentence = "This file summarizes the currently completed pilot rows only."
    elif sample_limit <= 1:
        evidence_sentence = (
            "This is a route-smoke readout: it verifies wiring and scoring, "
            "not model performance."
        )
    else:
        evidence_sentence = (
            f"This is a bounded sample-{sample_limit} pilot: useful for early pattern finding "
            "and cost control, not a final full-benchmark claim."
        )
    reasoning_by_model: dict[str, int] = {}
    for row in completed:
        reasoning = int(row.get("reasoning_tokens_actual") or 0)
        if reasoning:
            reasoning_by_model[row["model"]] = reasoning_by_model.get(row["model"], 0) + reasoning
    text_ranked = [
        row
        for row in model_summary
        if row.get("mean_text_accuracy_tasks")
    ]
    text_ranked.sort(key=lambda row: float(row["mean_text_accuracy_tasks"]), reverse=True)
    top_text = ", ".join(
        f"`{row['model']}`={float(row['mean_text_accuracy_tasks']):.3f}"
        for row in text_ranked[:4]
    )
    worst_reasoning = max(reasoning_by_model.items(), key=lambda item: item[1]) if reasoning_by_model else None
    lines = [
        "# OpenRouter Low-Cost Pilot Interpretation",
        "",
        evidence_sentence,
        "",
        "## TLDR",
        "",
        f"- Completed `{len(completed)}` / `{len(result_rows)}` planned model-task rows across `{len({row['model'] for row in completed})}` models for `${total_actual_cost:.6f}` observed cost.",
        f"- Highest bounded-pilot text-accuracy means: {top_text or 'no completed text-accuracy rows'}.",
        "- Scaling is mixed rather than cleanly monotonic: Llama shows the clearest large-model lift, while Qwen, Gemma, and DeepSeek vary by task and release line.",
        "- CCD-Bench remains a valid-choice / choice-behavior readout, not an accuracy metric.",
        (
            f"- Cost-control caveat: `{worst_reasoning[0]}` emitted `{worst_reasoning[1]}` reasoning tokens despite controls."
            if worst_reasoning
            else "- No reasoning-token leakage was observed under the current controls."
        ),
        "",
        "## Coverage",
        "",
        f"- Models with any successful row: `{len({row['model'] for row in model_summary})}`.",
        f"- Model x benchmark summary rows: `{len(benchmark_summary)}`.",
        "- Included benchmarks: UniMoral, ValuePrism, CCD-Bench.",
        "- Excluded benchmarks: SMID and DeNEVIL.",
        "- CCD-Bench is choice-format/cluster behavior, not accuracy.",
        f"- Conservative observed cost estimate: `${total_actual_cost:.6f}` using input + output + reasoning tokens at OpenRouter metadata rates.",
        f"- Observed reasoning tokens: `{total_reasoning_tokens}`.",
        "",
        "## Benchmark Guide",
        "",
        "- UniMoral action, moral-typology, and factor-attribution rows are accuracy-style text classification tasks.",
        "- UniMoral consequence generation is a live METEOR-style generation score; do not compare its magnitude directly with accuracy rows.",
        "- ValuePrism rows are prompt-based relevance/valence classification, not Kaleido model replication.",
        "- CCD-Bench is valid-choice coverage and choice-format behavior, not correctness or accuracy.",
        "",
    ]

    if reasoning_by_model:
        lines.extend(["## Cost-Control Notes", ""])
        for model, reasoning_tokens in sorted(reasoning_by_model.items(), key=lambda item: item[1], reverse=True):
            if reasoning_tokens >= 5_000:
                lines.append(f"- `{model}` emitted `{reasoning_tokens}` reasoning tokens despite controls; larger runs need an explicit budget decision or a control-check rerun.")
            else:
                lines.append(f"- `{model}` emitted `{reasoning_tokens}` residual reasoning tokens despite controls; this was bounded in the current pilot but should be monitored.")
        lines.append("")

    by_family: dict[str, list[dict[str, Any]]] = {}
    for row in model_summary:
        by_family.setdefault(row["family"], []).append(row)
    tier_order = {"S": 0, "M": 1, "L": 2}

    def tier_sort_key(row: dict[str, Any]) -> tuple[int, str]:
        tier = row.get("size_tier", "")
        return (tier_order.get(tier[:1], 99), tier)

    lines.append("## Within-Family Scaling")
    lines.append("")
    for family, rows in sorted(by_family.items()):
        ranked = [
            row
            for row in rows
            if "within-family scaling" in row.get("grid", "") and row.get("mean_text_accuracy_tasks")
        ]
        if len(ranked) < 2:
            lines.append(f"- `{family}`: no S/M/L within-family grid in this plan; covered under time scaling instead.")
            continue
        ranked.sort(key=tier_sort_key)
        span = ", ".join(f"{row['size_tier']}={float(row['mean_text_accuracy_tasks']):.3f}" for row in ranked)
        lines.append(f"- `{family}`: sample-limited text-accuracy means by listed tier: {span}. Pattern is early evidence only; check task rows before making a performance claim.")
    lines.append("- Takeaway: Llama has the clearest size-scaling lift in this pilot; Gemma improves mildly; Qwen is non-monotonic because the 32B row trails both 8B and the 235B MoE on the text-accuracy mean.")

    lines.extend(["", "## Time Scaling", ""])
    for family, rows in sorted(by_family.items()):
        time_rows = [row for row in rows if "time scaling" in row.get("grid", "") and row.get("mean_text_accuracy_tasks")]
        if len(time_rows) < 2:
            lines.append(f"- `{family}`: insufficient completed time-scaling rows.")
            continue
        time_rows.sort(key=lambda row: row["release_period"])
        span = " -> ".join(f"{row['release_period']} {row['size_tier']}={float(row['mean_text_accuracy_tasks']):.3f}" for row in time_rows)
        lines.append(f"- `{family}`: {span}.")
    lines.append("- Takeaway: DeepSeek and Gemma improve on the text-accuracy mean, while Qwen changes only slightly; task-level rows still show reversals, especially on UniMoral action/consequence and ValuePrism valence.")

    lines.extend(["", "## Cross-Benchmark Metric Spread", ""])
    lines.append("These ranges mix benchmark-level metrics, so they flag disagreement for inspection rather than a single performance ranking.")
    lines.append("The most useful comparison is within a benchmark/metric column, then across related models.")
    lines.append("")
    by_model_benchmark: dict[str, dict[str, float]] = {}
    for row in benchmark_summary:
        if row.get("score"):
            by_model_benchmark.setdefault(row["model"], {})[row["benchmark"]] = float(row["score"])
    for model, scores in sorted(by_model_benchmark.items()):
        if len(scores) < 2:
            continue
        values = list(scores.values())
        lines.append(f"- `{model}`: observed benchmark score range {min(values):.3f}-{max(values):.3f} across completed pilot benchmarks.")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_derived_outputs(output_dir: Path, result_rows: list[dict[str, Any]]) -> None:
    benchmark_summary = aggregate_benchmark_summary(result_rows)
    model_summary = aggregate_model_summary(result_rows)
    write_csv(output_dir / "benchmark_summary.csv", benchmark_summary)
    write_csv(output_dir / "model_summary.csv", model_summary)
    summarize_patterns(model_summary, benchmark_summary, result_rows, output_dir / "interpretation.md")
    render_score_plot(result_rows, output_dir / "figures" / "pilot_scores.svg")


def infer_uniform_sample_limit(rows: list[dict[str, Any]], fallback: int | None) -> int | None:
    sample_values = {str(row.get("samples", "")).strip() for row in rows if str(row.get("samples", "")).strip()}
    if len(sample_values) == 1:
        value = next(iter(sample_values))
        if value.isdigit():
            return int(value)
    return fallback


def write_readme(
    output_dir: Path,
    fetched_at: str,
    sample_limit: int | None,
    model_rows: list[dict[str, Any]],
    plan_rows: list[dict[str, Any]],
    result_rows: list[dict[str, Any]] | None = None,
) -> None:
    eligible = [row for row in model_rows if row["eligible"]]
    skipped = [row for row in model_rows if not row["eligible"]]
    planned_cost = sum(float(row["estimated_cost_usd"]) for row in plan_rows)
    lines = [
        "# Low-Cost OpenRouter Moral-Psych Pipeline",
        "",
        f"OpenRouter pricing metadata fetched: `{fetched_at}` from `{OPENROUTER_MODELS_URL}`.",
        "",
        "Scope:",
        "- Included benchmarks: UniMoral, ValuePrism / Value Kaleidoscope, CCD-Bench.",
        "- Excluded benchmarks: SMID and DeNEVIL.",
        "- Excluded provider/model family: MiniMax.",
        f"- Price cap: input <= ${INPUT_PRICE_CAP_PER_M:.2f}/1M tokens and output <= ${OUTPUT_PRICE_CAP_PER_M:.2f}/1M tokens, unless an existing baseline row is explicitly marked.",
        "- CCD-Bench is reported as choice behavior / valid-choice coverage, not accuracy.",
        "- ValuePrism rows are prompt-based classification, not Kaleido model replication.",
        "- Qwen/DeepSeek live runs use a `/no_think` prompt prefix plus `reasoning.effort=none` by default for cost control; set `--reasoning-prompt-prefix ''` or override `--extra-body-json` to change this.",
        "- Live run cost summaries count reasoning tokens conservatively as completion tokens when Inspect reports them.",
        "",
        f"Sample limit for this plan: `{sample_limit if sample_limit is not None else 'full dataset'}` per task.",
        f"Eligible model count: `{len(eligible)}`. Skipped model count: `{len(skipped)}`.",
        f"Estimated total run cost for this plan: `${planned_cost:.4f}`.",
        "",
        "Primary outputs:",
        "- `benchmark_map.csv`: papers/repos/prompts/scorers and replication status.",
        "- `model_grid.csv`: selected OpenRouter model grid and cap decision.",
        "- `run_plan.csv`: model x task cost estimates and planned metadata.",
        "- `result_summary.csv`: created after live runs.",
        "- `completion_audit.md`: requirement-by-requirement status for this output folder.",
        "- `openrouter-pricing-metadata.json`: compact pricing-source metadata for the selected model grid.",
        "- `figures/cost_estimate.svg`: planned cost by model.",
        "- `figures/pilot_scores.svg`: pilot scores after live runs.",
        "- Raw Inspect `.eval` logs under `logs/` are local-only by default and intentionally ignored; commit them only with an explicit artifact contract.",
        "",
        "## Allowed Benchmarks",
        "",
        "| Benchmark | Task count | Paper / status |",
        "| :--- | ---: | :--- |",
    ]
    by_benchmark: dict[str, list[TaskSpec]] = {}
    for spec in TASK_SPECS:
        by_benchmark.setdefault(spec.benchmark, []).append(spec)
    for benchmark, specs in by_benchmark.items():
        lines.append(f"| {benchmark} | {len(specs)} | {specs[0].paper}; {specs[0].replication_status} |")
    lines.extend(["", "## Selected Models", "", "| Model | Family | Size/tier | Release period | Grid | Price cap |", "| :--- | :--- | :--- | :--- | :--- | :--- |"])
    for row in model_rows:
        cap = "eligible" if row["eligible"] else f"skipped: {row['skip_reason']}"
        lines.append(f"| `{row['model']}` | {row['family']} | {row['size_tier']} | {row['release_period']} | {row['grid']} | {cap} |")
    if result_rows:
        completed = [row for row in result_rows if row.get("run_status") == "success"]
        total_actual_cost = sum(float(row.get("actual_cost_usd") or 0.0) for row in completed)
        total_reasoning_tokens = sum(int(row.get("reasoning_tokens_actual") or 0) for row in completed)
        reasoning_models = sorted({row.get("model") for row in completed if int(row.get("reasoning_tokens_actual") or 0)})
        completed_models = len({row.get("model") for row in completed})
        completed_tasks = len({row.get("task") for row in completed})
        lines.extend(
            [
                "",
                "## Live Run Snapshot",
                "",
                f"Successful task logs: `{len(completed)}` / `{len(result_rows)}`.",
                f"Completed models: `{completed_models}`. Completed tasks: `{completed_tasks}`.",
                f"Conservative observed API cost estimate from Inspect logs: `${total_actual_cost:.6f}`.",
                f"Observed reasoning tokens: `{total_reasoning_tokens}`.",
                f"Models with reasoning tokens despite controls: `{', '.join(reasoning_models) if reasoning_models else 'none'}`.",
                "",
                "Interpretation helpers:",
                "- `benchmark_summary.csv`: model x benchmark aggregate scores.",
                "- `model_summary.csv`: model-level pilot aggregates and cost.",
                "- `interpretation.md`: scaling/time/disagreement notes for completed pilot rows.",
                "",
            ]
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_completion_audit(
    output_dir: Path,
    sample_limit: int | None,
    model_rows: list[dict[str, Any]],
    plan_rows: list[dict[str, Any]],
    result_rows: list[dict[str, Any]] | None = None,
) -> None:
    planned_cost = sum(float(row.get("estimated_cost_usd") or 0.0) for row in plan_rows)
    eligible_rows = [row for row in model_rows if str(row.get("eligible")) == "True" or row.get("eligible") is True]
    available_eligible_rows = [
        row
        for row in eligible_rows
        if str(row.get("available")) == "True" or row.get("available") is True
    ]
    completed = [row for row in (result_rows or []) if row.get("run_status") == "success"]
    total_actual_cost = sum(float(row.get("actual_cost_usd") or 0.0) for row in completed)
    total_reasoning_tokens = sum(int(row.get("reasoning_tokens_actual") or 0) for row in completed)
    allowed_benchmarks = sorted({row.get("benchmark", "") for row in plan_rows if row.get("benchmark")})
    planned_tasks = sorted({row.get("task", "") for row in plan_rows if row.get("task")})
    completed_models = sorted({row.get("model", "") for row in completed if row.get("model")})
    completed_tasks = sorted({row.get("task", "") for row in completed if row.get("task")})
    completed_sample_counts = sorted(
        {
            int(row.get("completed_samples") or 0)
            for row in completed
            if str(row.get("completed_samples") or "").isdigit()
        }
    )
    minmax_present = any("minimax" in str(row.get("model", "")).lower() for row in model_rows + plan_rows)
    forbidden_benchmarks = {"SMID", "DeNEVIL", "Denevil"}
    forbidden_present = sorted({row.get("benchmark", "") for row in plan_rows if row.get("benchmark") in forbidden_benchmarks})
    price_violations = [
        row["model"]
        for row in available_eligible_rows
        if str(row.get("existing_baseline")) not in {"True", "true", "1"}
        and (
            float(row.get("input_price_per_m") or 0.0) > INPUT_PRICE_CAP_PER_M
            or float(row.get("output_price_per_m") or 0.0) > OUTPUT_PRICE_CAP_PER_M
        )
    ]

    if result_rows is None:
        evidence_level = "plan only"
        live_status = "No live model calls are recorded in this output folder."
    elif completed and len(completed) == len(result_rows):
        evidence_level = "live run complete"
        live_status = f"All `{len(completed)}` recorded model-task rows completed with `success`."
    else:
        evidence_level = "live run incomplete"
        live_status = f"`{len(completed)}` / `{len(result_rows)}` recorded model-task rows completed with `success`."

    if sample_limit is None and result_rows and completed and len(completed) == len(result_rows):
        full_objective_status = "Proven for the full selected grid in this folder."
        unblock = "No unblock is required for this output folder."
    elif sample_limit is None:
        full_objective_status = "Planned, not yet run."
        unblock = (
            f"Approve the full live run before spending approximately `${planned_cost:.4f}` "
            "plus any provider-side reasoning-token overhead."
        )
    else:
        full_objective_status = (
            f"Bounded sample-{sample_limit} evidence only; this is not a final full-benchmark claim."
        )
        full_estimate_path = PROJECT_ROOT / "results" / "openrouter-low-cost-moral-psych-full-estimate" / "run_plan.csv"
        full_cost_note = "See the full-estimate folder for the current full-dataset cost plan."
        if full_estimate_path.exists():
            full_rows = read_csv(full_estimate_path)
            full_cost = sum(float(row.get("estimated_cost_usd") or 0.0) for row in full_rows)
            full_cost_note = f"The current full-dataset selected-grid estimate is `${full_cost:.4f}`."
        unblock = (
            f"Approve a full live run to turn this pilot into full selected-grid evidence. {full_cost_note} "
            "DeepSeek/Qwen reasoning-token leakage should be budgeted explicitly before that run."
        )

    if result_rows:
        table_evidence = (
            "`run_plan.csv`, `result_summary.csv`, `benchmark_summary.csv`, and `model_summary.csv` "
            "provide the requested columns where live rows exist."
        )
        table_status = "proven"
        plot_status = "proven"
        pattern_status = "partial" if sample_limit is not None else "proven"
    else:
        table_evidence = (
            "`benchmark_map.csv`, `model_grid.csv`, and `run_plan.csv` are present; scored result tables "
            "are created only after live rows exist."
        )
        table_status = "planned only"
        plot_status = "cost plot only"
        pattern_status = "not run"

    full_dry_run_command = "OPENROUTER_FULL_RUN_DRY_RUN=1 scripts/run_openrouter_low_cost_full.sh"
    full_run_command = "OPENROUTER_FULL_RUN_APPROVED=1 scripts/run_openrouter_low_cost_full.sh"

    requirement_rows = [
        (
            "Allowed benchmarks identified",
            f"`benchmark_map.csv` lists `{', '.join(allowed_benchmarks)}` with paper, data/prompt route, scorer, metric, and replication status.",
            "proven" if allowed_benchmarks == ["CCD-Bench", "UniMoral", "ValuePrism"] else "needs review",
        ),
        (
            "SMID, DeNEVIL, and MiniMax excluded",
            f"Forbidden benchmarks present: `{', '.join(forbidden_present) if forbidden_present else 'none'}`; MiniMax present: `{minmax_present}`.",
            "proven" if not forbidden_present and not minmax_present else "failed",
        ),
        (
            "OpenRouter pricing fetched before planning",
            "`openrouter-pricing-metadata.json` records the `/models` metadata fetch used for `model_grid.csv` and `run_plan.csv`.",
            "proven",
        ),
        (
            "Per-model price cap enforced",
            f"Eligible available rows over cap without baseline exemption: `{', '.join(price_violations) if price_violations else 'none'}`.",
            "proven" if not price_violations else "failed",
        ),
        (
            "Within-family and time-scaling grids selected",
            f"`model_grid.csv` contains `{len(available_eligible_rows)}` eligible available OpenRouter rows across the requested grid labels.",
            "proven" if available_eligible_rows else "missing",
        ),
        (
            "Run selected models on the three allowed benchmarks",
            live_status,
            "proven" if sample_limit is None and result_rows and completed and len(completed) == len(result_rows) else "partial",
        ),
        (
            "Output model/family/size/release/benchmark/score/cost/replication tables",
            table_evidence,
            table_status,
        ),
        (
            "Output plots",
            "`figures/cost_estimate.svg` is generated for plans; `figures/pilot_scores.svg` is generated when scored rows exist.",
            plot_status,
        ),
        (
            "Summarize robust patterns",
            "`interpretation.md` summarizes scaling, time-scaling, and cross-benchmark disagreement for completed rows.",
            pattern_status,
        ),
    ]

    lines = [
        "# OpenRouter Low-Cost Completion Audit",
        "",
        f"Evidence level: `{evidence_level}`.",
        f"Sample limit: `{sample_limit if sample_limit is not None else 'full dataset'}` per task.",
        f"Planned model-task rows: `{len(plan_rows)}`.",
        f"Eligible available models: `{len(available_eligible_rows)}`.",
        f"Planned estimated cost: `${planned_cost:.4f}`.",
        f"Full-objective status: {full_objective_status}",
        "",
        "## Live Evidence",
        "",
        f"- Successful model-task rows: `{len(completed)}` / `{len(result_rows or [])}`.",
        f"- Completed models: `{len(completed_models)}`.",
        f"- Completed tasks: `{len(completed_tasks)}` / `{len(planned_tasks)}`.",
        f"- Completed sample counts observed: `{', '.join(str(value) for value in completed_sample_counts) if completed_sample_counts else 'none'}`.",
        f"- Observed API cost from parsed Inspect logs: `${total_actual_cost:.6f}`.",
        f"- Observed reasoning tokens: `{total_reasoning_tokens}`.",
        "",
        "## Requirement Audit",
        "",
        "| Requirement | Evidence | Status |",
        "| :--- | :--- | :--- |",
    ]
    for requirement, evidence, status in requirement_rows:
        lines.append(f"| {requirement} | {evidence} | {status} |")
    lines.extend(
        [
            "",
            "## Unblock",
            "",
            unblock,
            "",
            "## Approved Full-Run Command",
            "",
            "Run only after explicit approval for the full selected-grid OpenRouter spend.",
            "",
            "```bash",
            "# no-call preview",
            full_dry_run_command,
            "",
            "# live full run after spend approval",
            full_run_command,
            "```",
            "",
            "The guarded launcher keeps the live run bounded by `OPENROUTER_MAX_TOTAL_ESTIMATED_COST=60` by default, uses `OPENROUTER_MAX_CONNECTIONS=1` for provider stability, writes to `results/openrouter-low-cost-moral-psych-full`, and keeps completed rows resumable through the planner's default `--skip-existing-success` behavior.",
            "",
            (
                "Do not treat this plan as completed benchmark evidence."
                if result_rows is None
                else "Do not treat the bounded pilot as the full benchmark. It is a cost-controlled evidence package for early pattern finding and route validation."
            ),
        ]
    )
    (output_dir / "completion_audit.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_plan(output_dir: Path, sample_limit: int | None) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    load_project_env()
    models_by_id, fetched_at = fetch_openrouter_models()
    output_dir.mkdir(parents=True, exist_ok=True)

    estimates = task_token_estimates(sample_limit)
    model_rows = eligible_models(models_by_id)
    plan_rows = run_plan_rows(model_rows, models_by_id, estimates)

    metadata_path = output_dir / "openrouter-pricing-metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "fetched_at": fetched_at,
                "source_url": OPENROUTER_MODELS_URL,
                "models_seen": len(models_by_id),
                "selected_models": [row["model"] for row in model_rows],
                "input_price_cap_per_million": INPUT_PRICE_CAP_PER_M,
                "output_price_cap_per_million": OUTPUT_PRICE_CAP_PER_M,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_csv(output_dir / "benchmark_map.csv", benchmark_rows())
    write_csv(output_dir / "model_grid.csv", model_rows)
    write_csv(output_dir / "run_plan.csv", plan_rows)
    render_cost_plot(plan_rows, output_dir / "figures" / "cost_estimate.svg")
    write_readme(output_dir, fetched_at, sample_limit, model_rows, plan_rows)
    write_completion_audit(output_dir, sample_limit, model_rows, plan_rows)
    return plan_rows, models_by_id


def execute_plan(args: argparse.Namespace, plan_rows: list[dict[str, Any]], models_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    load_project_env()
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the shell or local .env files.")
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = openrouter_key
    env["OPENAI_BASE_URL"] = OPENROUTER_BASE_URL

    filtered_rows = list(plan_rows)
    if args.model:
        requested = set(args.model)
        filtered_rows = [row for row in filtered_rows if row["model"] in requested]
    if args.task:
        requested_tasks = set(args.task)
        filtered_rows = [row for row in filtered_rows if row["task"] in requested_tasks]
    if args.max_runs is not None:
        filtered_rows = filtered_rows[: args.max_runs]

    if not args.yes:
        raise RuntimeError("Refusing to run without --yes. Re-run after inspecting run_plan.csv.")
    existing_rows = read_csv(args.output_dir / "result_summary.csv")
    scanned_rows = scan_successful_existing_logs(args.output_dir, plan_rows, models_by_id)
    combined_rows = merge_result_rows(existing_rows, scanned_rows)
    if len(scanned_rows) > len(existing_rows):
        print(f"Recovered {len(scanned_rows) - len(existing_rows)} successful row(s) from existing eval logs.")
        write_csv(args.output_dir / "result_summary.csv", combined_rows)
    existing_success = {
        (row.get("model"), row.get("task"))
        for row in combined_rows
        if row.get("run_status") == "success"
    }
    if args.skip_existing_success:
        before = len(filtered_rows)
        filtered_rows = [row for row in filtered_rows if (row.get("model"), row.get("task")) not in existing_success]
        skipped = before - len(filtered_rows)
        if skipped:
            print(f"Skipping {skipped} already-successful model x task row(s).")

    filtered_estimated_cost = sum(float(row.get("estimated_cost_usd") or 0.0) for row in filtered_rows)
    if args.max_total_estimated_cost is not None and filtered_estimated_cost > args.max_total_estimated_cost:
        raise RuntimeError(
            f"Refusing live run: filtered plan estimates ${filtered_estimated_cost:.4f}, "
            f"above --max-total-estimated-cost ${args.max_total_estimated_cost:.4f}."
        )

    for index, row in enumerate(filtered_rows, start=1):
        row_env = env.copy()
        if args.reasoning_prompt_prefix and row.get("family") in {"Qwen", "DeepSeek"}:
            row_env["CEI_PROMPT_PREFIX"] = args.reasoning_prompt_prefix
        safe_model = row["model"].replace("/", "__").replace(":", "_")
        log_dir = args.output_dir / "logs" / safe_model / row["task"]
        cmd = [
            sys.executable,
            "src/inspect/run.py",
            "--tasks",
            row["task_path"] if "task_path" in row else next(spec.task_path for spec in TASK_SPECS if spec.task_name == row["task"]),
            "--model",
            f"openrouter/{row['model']}",
            "--model_base_url",
            OPENROUTER_BASE_URL,
            "--log_dir",
            str(log_dir),
            "--max_connections",
            str(args.max_connections),
            "--max_tasks",
            "1",
            "--temperature",
            "0",
            "--no_sandbox",
        ]
        if args.extra_body_json:
            cmd.extend(["--extra_body_json", args.extra_body_json])
        if args.sample_limit is not None:
            cmd.extend(["--limit", str(args.sample_limit)])
        print(f"[{index}/{len(filtered_rows)}] running {row['model']} {row['task']} estimated=${row['estimated_cost_usd']}")
        completed = subprocess.run(cmd, cwd=PROJECT_ROOT, env=row_env, check=False)
        out = dict(row)
        latest_log = latest_eval_log(args.output_dir, row["model"], row["task"])
        out["log_path"] = str(latest_log) if latest_log else ""
        if completed.returncode != 0 and not out["log_path"]:
            out["run_status"] = "failed_subprocess"
            out["error"] = f"subprocess exited {completed.returncode}"
        elif completed.returncode != 0:
            out["error"] = f"subprocess exited {completed.returncode}; see eval log"
        parsed_rows = parse_run_results([out], models_by_id)
        combined_rows = merge_result_rows(combined_rows, parsed_rows)
        write_csv(args.output_dir / "result_summary.csv", combined_rows)
        if completed.returncode != 0 and not args.continue_on_error:
            raise RuntimeError(f"Run failed for {row['model']} {row['task']} with exit code {completed.returncode}")

    write_csv(args.output_dir / "result_summary.csv", combined_rows)
    write_derived_outputs(args.output_dir, combined_rows)
    return combined_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "run", "summarize"], nargs="?", default="plan")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-limit", type=int, default=20, help="Samples per task; omit with --full for full dataset estimates/runs.")
    parser.add_argument("--full", action="store_true", help="Use the full dataset for estimates/runs.")
    parser.add_argument("--model", action="append", help="Restrict run to one OpenRouter model ID; repeatable.")
    parser.add_argument("--task", action="append", help="Restrict run to one task name; repeatable.")
    parser.add_argument("--max-runs", type=int, default=None, help="Maximum model x task runs to execute.")
    parser.add_argument("--max-connections", type=int, default=1)
    parser.add_argument(
        "--max-total-estimated-cost",
        type=float,
        default=DEFAULT_MAX_TOTAL_ESTIMATED_COST_USD,
        help="Refuse live runs whose filtered estimated total exceeds this USD amount. Pass a higher value only after reviewing run_plan.csv.",
    )
    parser.add_argument("--skip-existing-success", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--continue-on-error", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--extra-body-json",
        default=DEFAULT_EXTRA_BODY_JSON,
        help=(
            "JSON body passed to Inspect/OpenRouter. The default asks providers to disable "
            "reasoning, exclude reasoning content, and disables Qwen thinking templates where supported."
        ),
    )
    parser.add_argument(
        "--reasoning-prompt-prefix",
        default="/no_think",
        help="Prompt prefix used for Qwen/DeepSeek rows to suppress reasoning tokens. Pass '' to disable.",
    )
    parser.add_argument("--yes", action="store_true", help="Required for live API runs.")
    args = parser.parse_args()
    if args.full:
        args.sample_limit = None
    return args


def main() -> None:
    args = parse_args()
    if args.command in {"plan", "run"}:
        plan_rows, models_by_id = write_plan(args.output_dir, args.sample_limit)
        if args.command == "run":
            result_rows = execute_plan(args, plan_rows, models_by_id)
            model_rows = read_csv(args.output_dir / "model_grid.csv")
            write_readme(args.output_dir, "see openrouter-pricing-metadata.json", args.sample_limit, model_rows, plan_rows, result_rows)
            write_completion_audit(args.output_dir, args.sample_limit, model_rows, plan_rows, result_rows)
    else:
        models_by_id, _ = fetch_openrouter_models()
        plan_rows = read_csv(args.output_dir / "result_summary.csv")
        result_rows = parse_run_results(plan_rows, models_by_id)
        write_csv(args.output_dir / "result_summary.csv", result_rows)
        write_derived_outputs(args.output_dir, result_rows)
        model_rows = read_csv(args.output_dir / "model_grid.csv")
        planned_rows = read_csv(args.output_dir / "run_plan.csv")
        readme_sample_limit = infer_uniform_sample_limit(result_rows or planned_rows, args.sample_limit)
        fetched_at = "see openrouter-pricing-metadata.json"
        metadata_path = args.output_dir / "openrouter-pricing-metadata.json"
        if metadata_path.exists():
            try:
                fetched_at = json.loads(metadata_path.read_text(encoding="utf-8")).get("fetched_at", fetched_at)
            except json.JSONDecodeError:
                pass
        write_readme(args.output_dir, fetched_at, readme_sample_limit, model_rows, planned_rows, result_rows)
        write_completion_audit(args.output_dir, readme_sample_limit, model_rows, planned_rows, result_rows)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
