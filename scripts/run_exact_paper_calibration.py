#!/usr/bin/env python3
"""Plan, run, and summarize exact same-model paper calibration rows.

This runner is intentionally narrow: it runs CCD-Bench only for exact
paper-model OpenRouter routes that are missing checked cluster distributions.
It writes small manifest/summary CSVs and leaves raw Inspect logs local.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
TASK_PATH = "src/inspect/evals/ccd_bench.py::ccd_bench_selection"
TASK_NAME = "ccd_bench_selection"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "paper-calibration-exact-20260705"
DEFAULT_ENV_FILES = [
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / ".env.local",
    PROJECT_ROOT.parent / "CEI" / ".env",
]
DEFAULT_EXTRA_BODY_JSON = json.dumps(
    {
        "reasoning": {"effort": "none", "exclude": True},
        "chat_template_kwargs": {"enable_thinking": False},
    }
)


@dataclass(frozen=True)
class CalibrationRun:
    paper_model: str
    model_id: str
    paper_anchor: str
    required_reason: str
    include_by_default: bool = True


RUN_CANDIDATES: list[CalibrationRun] = [
    CalibrationRun(
        "DeepSeek-chat-v3-0324",
        "deepseek/deepseek-chat-v3-0324",
        "Nordic Europe 22.9%; Germanic Europe 11.9%; plural rationales 96.8%; Cramer's V 0.161",
        "Current full-grid row has valid-choice coverage only; exact CCD cluster distribution is missing.",
    ),
    CalibrationRun(
        "Qwen2.5-72B-Instruct",
        "qwen/qwen-2.5-72b-instruct",
        "Nordic Europe 17.7%; Germanic Europe 9.4%; plural rationales 91.4%; Cramer's V 0.102",
        "Exact CCD paper model is available on OpenRouter but has no checked current distribution row.",
    ),
    CalibrationRun(
        "OpenAI GPT-4.1",
        "openai/gpt-4.1",
        "Nordic Europe 21.5%; Germanic Europe 7.6%; plural rationales 94.7%; Cramer's V 0.096",
        "Exact CCD paper model is available on OpenRouter; existing GPT-4.1-mini reference is not exact.",
    ),
    CalibrationRun(
        "Command-R 08-2024",
        "cohere/command-r-08-2024",
        "Nordic Europe 16.1%; Germanic Europe 10.2%; plural rationales 78.5%; Cramer's V 0.142",
        "Exact CCD paper model is available on OpenRouter but has no checked current distribution row.",
    ),
    CalibrationRun(
        "Microsoft Phi-4",
        "microsoft/phi-4",
        "Nordic Europe 18.9%; Germanic Europe 7.8%; plural rationales 82.7%; Cramer's V 0.152",
        "Exact CCD paper model is available on OpenRouter but has no checked current distribution row.",
    ),
    CalibrationRun(
        "WizardLM-2-8x22B",
        "microsoft/wizardlm-2-8x22b",
        "Nordic Europe 22.0%; Germanic Europe 16.4%; plural rationales 88.8%; Cramer's V 0.111",
        "Exact CCD paper model is available on OpenRouter but has no checked current distribution row.",
    ),
    CalibrationRun(
        "Perplexity Sonar",
        "perplexity/sonar",
        "Nordic Europe 21.8%; Germanic Europe 12.5%; plural rationales 92.9%; Cramer's V 0.127",
        "Exact CCD paper model is available on OpenRouter but has no checked current distribution row.",
    ),
    CalibrationRun(
        "Claude 4 Sonnet",
        "anthropic/claude-sonnet-4",
        "Nordic Europe 30.6%; Germanic Europe 15.9%; plural rationales 98.6%; Cramer's V 0.054",
        "Exact CCD paper model is available on OpenRouter but has no checked current distribution row.",
    ),
    CalibrationRun(
        "Mistral Nemo",
        "mistralai/mistral-nemo",
        "Nordic Europe 19.0%; Germanic Europe 13.1%; plural rationales 82.0%; Cramer's V 0.130",
        "Already has saved/prior exact CCD evidence; excluded by default to avoid duplicate spend.",
        include_by_default=False,
    ),
    CalibrationRun(
        "Llama-3.3-70B-Instruct",
        "meta-llama/llama-3.3-70b-instruct",
        "Nordic Europe 19.7%; Germanic Europe 15.3%; plural rationales 85.3%; Cramer's V 0.203",
        "Already has current exact CCD release evidence; excluded by default to avoid duplicate spend.",
        include_by_default=False,
    ),
]

SUMMARY_FIELDNAMES = [
    "paper_model",
    "openrouter_model_id",
    "run_stage",
    "run_status",
    "log_path",
    "paper_anchor",
    "total_ccd_samples",
    "valid_selection_count",
    "valid_selection_rate",
    "invalid_selection_count",
    "dominant_option",
    "dominant_option_share",
    "effective_cluster_count",
    "distribution_status",
    "actual_input_tokens",
    "actual_output_tokens",
    "actual_reasoning_tokens",
    "actual_cost_usd",
    "completed_at",
]

MANIFEST_FIELDNAMES = [
    "paper_model",
    "openrouter_model_id",
    "include_by_default",
    "paper_anchor",
    "required_reason",
    "openrouter_available",
    "context_length",
    "input_price_per_m",
    "output_price_per_m",
    "estimated_input_tokens",
    "estimated_output_tokens",
    "estimated_cost_usd",
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
        if not key or key in os.environ:
            continue
        if value and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


def load_env(paths: list[Path]) -> None:
    for path in paths:
        load_env_file(path)
    if os.environ.get("OPENROUTER_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    os.environ.setdefault("OPENAI_BASE_URL", OPENROUTER_BASE_URL)
    os.environ.setdefault("CCD_BENCH_DATA_FILE", str(PROJECT_ROOT / "results" / "cache" / "ccd_bench.json"))


def fetch_openrouter_models() -> tuple[dict[str, dict[str, Any]], str]:
    with urllib.request.urlopen(OPENROUTER_MODELS_URL, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    models = payload.get("data", payload if isinstance(payload, list) else [])
    return {model["id"]: model for model in models if "id" in model}, datetime.now(timezone.utc).isoformat()


def token_counter():
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("o200k_base")
        return lambda text: len(encoding.encode(str(text)))
    except Exception:
        return lambda text: max(1, round(len(str(text)) / 4))


def estimate_ccd_input_tokens() -> tuple[int, int]:
    inspect_src = PROJECT_ROOT / "src" / "inspect"
    if str(inspect_src) not in sys.path:
        sys.path.insert(0, str(inspect_src))
    from evals.ccd_bench import _make_ccd_samples

    count = token_counter()
    samples = _make_ccd_samples()
    return sum(count(sample.input) for sample in samples), len(samples)


def model_prices(model: dict[str, Any] | None) -> tuple[float, float]:
    if model is None:
        return 0.0, 0.0
    pricing = model.get("pricing") or {}
    return float(pricing.get("prompt") or 0.0) * 1_000_000, float(pricing.get("completion") or 0.0) * 1_000_000


def selected_candidates(args: argparse.Namespace) -> list[CalibrationRun]:
    rows = RUN_CANDIDATES if args.include_existing else [row for row in RUN_CANDIDATES if row.include_by_default]
    if args.model:
        wanted = set(args.model)
        rows = [row for row in rows if row.model_id in wanted or row.paper_model in wanted]
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plan_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str]:
    models, fetched_at = fetch_openrouter_models()
    estimated_input_tokens, sample_count = estimate_ccd_input_tokens()
    estimated_output_tokens = sample_count * 80
    rows: list[dict[str, Any]] = []
    for candidate in selected_candidates(args):
        model = models.get(candidate.model_id)
        input_price_per_m, output_price_per_m = model_prices(model)
        estimated_cost = (
            (estimated_input_tokens * input_price_per_m / 1_000_000)
            + (estimated_output_tokens * output_price_per_m / 1_000_000)
        )
        rows.append(
            {
                "paper_model": candidate.paper_model,
                "openrouter_model_id": candidate.model_id,
                "include_by_default": str(candidate.include_by_default).lower(),
                "paper_anchor": candidate.paper_anchor,
                "required_reason": candidate.required_reason,
                "openrouter_available": "yes" if model is not None else "no",
                "context_length": "" if model is None else model.get("context_length", ""),
                "input_price_per_m": f"{input_price_per_m:.6f}",
                "output_price_per_m": f"{output_price_per_m:.6f}",
                "estimated_input_tokens": estimated_input_tokens,
                "estimated_output_tokens": estimated_output_tokens,
                "estimated_cost_usd": f"{estimated_cost:.6f}",
            }
        )
    return rows, fetched_at


def write_plan(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows, fetched_at = plan_rows(args)
    write_csv(args.output_dir / "run-manifest.csv", rows, MANIFEST_FIELDNAMES)
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "openrouter_models_fetched_at": fetched_at,
        "task": TASK_NAME,
        "task_path": TASK_PATH,
        "max_estimated_cost_usd": args.max_estimated_cost,
        "selected_models": [row["openrouter_model_id"] for row in rows],
        "total_estimated_cost_usd": round(sum(float(row["estimated_cost_usd"]) for row in rows), 6),
    }
    (args.output_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return rows


def safe_model_id(model_id: str) -> str:
    return model_id.replace("/", "__").replace(":", "_")


def latest_eval(log_dir: Path) -> Path | None:
    evals = sorted(log_dir.glob("*.eval"), key=lambda path: path.stat().st_mtime)
    return evals[-1] if evals else None


def eval_status(eval_path: Path) -> str:
    from zipfile import BadZipFile, ZipFile

    try:
        with ZipFile(eval_path) as zf:
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, FileNotFoundError, KeyError, json.JSONDecodeError):
        return "unreadable"
    return str(header.get("status", "unknown"))


def run_one(args: argparse.Namespace, candidate: CalibrationRun, *, stage: str, limit: int | None) -> Path | None:
    model_safe = safe_model_id(candidate.model_id)
    log_dir = args.output_dir / "logs" / model_safe / stage
    home_dir = log_dir / "_home"
    stdout_path = log_dir / "stdout_stderr.log"
    log_dir.mkdir(parents=True, exist_ok=True)

    existing = latest_eval(log_dir)
    if existing is not None and eval_status(existing) == "success" and not args.force:
        print(f"[skip] {candidate.model_id} {stage}: existing successful log {existing}")
        return existing

    env = os.environ.copy()
    env["OPENAI_API_KEY"] = env["OPENROUTER_API_KEY"]
    env["OPENAI_BASE_URL"] = OPENROUTER_BASE_URL
    env["CCD_BENCH_DATA_FILE"] = env.get("CCD_BENCH_DATA_FILE") or str(PROJECT_ROOT / "results" / "cache" / "ccd_bench.json")
    env.setdefault("CEI_TEMPERATURE", "0")
    if candidate.model_id.startswith(("qwen/", "deepseek/")):
        env["CEI_PROMPT_PREFIX"] = args.reasoning_prompt_prefix

    cmd = [
        sys.executable,
        "src/inspect/run.py",
        "--tasks",
        TASK_PATH,
        "--model",
        f"openrouter/{candidate.model_id}",
        "--model_base_url",
        OPENROUTER_BASE_URL,
        "--temperature",
        "0",
        "--max_connections",
        str(args.max_connections),
        "--max_tasks",
        "1",
        "--no_sandbox",
        "--home_dir",
        str(home_dir),
        "--log_dir",
        str(log_dir),
        "--extra_body_json",
        args.extra_body_json,
    ]
    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    print(f"[run] {candidate.paper_model} ({candidate.model_id}) stage={stage} limit={limit or 'full'}")
    with stdout_path.open("a", encoding="utf-8") as stdout:
        stdout.write(f"\n\n=== {datetime.now(timezone.utc).isoformat()} {' '.join(cmd)} ===\n")
        stdout.flush()
        process = subprocess.Popen(cmd, cwd=PROJECT_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            stdout.write(line)
            stdout.flush()
        return_code = process.wait()
        stdout.write(f"\n=== exit {return_code} ===\n")
    if return_code != 0:
        print(f"[warn] {candidate.model_id} {stage} exited {return_code}", file=sys.stderr)
    return latest_eval(log_dir)


def parse_usage(eval_path: Path | None) -> tuple[str, str, str]:
    if eval_path is None:
        return "", "", ""
    from zipfile import BadZipFile, ZipFile

    try:
        with ZipFile(eval_path) as zf:
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, FileNotFoundError, KeyError, json.JSONDecodeError):
        return "", "", ""
    usage = header.get("stats", {}).get("model_usage", {})
    if not isinstance(usage, dict) or not usage:
        return "", "", ""
    first = next(iter(usage.values()))
    if not isinstance(first, dict):
        return "", "", ""
    return (
        str(first.get("input_tokens", "")),
        str(first.get("output_tokens", "")),
        str(first.get("reasoning_tokens", "")),
    )


def summarize(args: argparse.Namespace) -> list[dict[str, Any]]:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.build_release_artifacts import inspect_ccd_choice_distribution

    manifest = read_csv(args.output_dir / "run-manifest.csv")
    by_model = {row["openrouter_model_id"]: row for row in manifest}
    existing_rows = {
        (row.get("openrouter_model_id", ""), row.get("run_stage", "")): row
        for row in read_csv(args.output_dir / "calibration-summary.csv")
    }
    rows: list[dict[str, Any]] = []
    for candidate in selected_candidates(args):
        for stage in ("smoke", "full"):
            log_dir = args.output_dir / "logs" / safe_model_id(candidate.model_id) / stage
            eval_path = latest_eval(log_dir)
            if eval_path is None:
                existing_row = existing_rows.get((candidate.model_id, stage))
                if existing_row and existing_row.get("run_status") not in {"", "not_started"}:
                    rows.append(dict(existing_row))
                    continue
            status = "" if eval_path is None else eval_status(eval_path)
            distribution = inspect_ccd_choice_distribution(eval_path) if eval_path is not None and status == "success" else None
            input_tokens, output_tokens, reasoning_tokens = parse_usage(eval_path)
            actual_cost = ""
            manifest_row = by_model.get(candidate.model_id)
            if manifest_row and input_tokens:
                input_price = float(manifest_row["input_price_per_m"]) / 1_000_000
                output_price = float(manifest_row["output_price_per_m"]) / 1_000_000
                actual_cost = f"{(float(input_tokens or 0) * input_price + (float(output_tokens or 0) + float(reasoning_tokens or 0)) * output_price):.6f}"
            row: dict[str, Any] = {
                "paper_model": candidate.paper_model,
                "openrouter_model_id": candidate.model_id,
                "run_stage": stage,
                "run_status": status or "not_started",
                "log_path": "" if eval_path is None else str(eval_path.relative_to(PROJECT_ROOT)),
                "paper_anchor": candidate.paper_anchor,
                "actual_input_tokens": input_tokens,
                "actual_output_tokens": output_tokens,
                "actual_reasoning_tokens": reasoning_tokens,
                "actual_cost_usd": actual_cost,
                "completed_at": datetime.fromtimestamp(eval_path.stat().st_mtime, tz=timezone.utc).isoformat() if eval_path else "",
            }
            if distribution is not None:
                row.update(
                    {
                        "total_ccd_samples": distribution["total"],
                        "valid_selection_count": distribution["valid_selection_count"],
                        "valid_selection_rate": f"{distribution['valid_selection_rate']:.6f}" if distribution["valid_selection_rate"] is not None else "",
                        "invalid_selection_count": distribution["invalid_selection_count"],
                        "dominant_option": distribution["dominant_option_label"],
                        "dominant_option_share": f"{distribution['dominant_option_share']:.6f}" if distribution["dominant_option_share"] is not None else "",
                        "effective_cluster_count": f"{distribution['effective_cluster_count']:.6f}" if distribution["effective_cluster_count"] is not None else "",
                        "distribution_status": distribution["distribution_status"],
                    }
                )
            rows.append(row)
    write_csv(args.output_dir / "calibration-summary.csv", rows, SUMMARY_FIELDNAMES)
    return rows


def command_run(args: argparse.Namespace) -> None:
    if not args.yes:
        raise SystemExit("Live runs require --yes after reviewing run-manifest.csv.")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is required; value was not printed.")
    rows = write_plan(args)
    selected = selected_candidates(args)
    selected_cost = sum(float(row["estimated_cost_usd"]) for row in rows)
    if selected_cost > args.max_estimated_cost:
        raise SystemExit(f"Estimated cost ${selected_cost:.2f} exceeds cap ${args.max_estimated_cost:.2f}.")
    unavailable = [row["openrouter_model_id"] for row in rows if row["openrouter_available"] != "yes"]
    if unavailable:
        raise SystemExit(f"OpenRouter route(s) unavailable: {', '.join(unavailable)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    for candidate in selected:
        if args.smoke_first:
            smoke_log = run_one(args, candidate, stage="smoke", limit=1)
            if smoke_log is None or eval_status(smoke_log) != "success":
                summarize(args)
                if args.continue_on_error:
                    continue
                raise SystemExit(f"Smoke failed for {candidate.model_id}")
            if args.smoke_only:
                summarize(args)
                continue
        run_one(args, candidate, stage="full", limit=None)
        summarize(args)
        if args.stop_after_hours and (time.monotonic() - started) / 3600 >= args.stop_after_hours:
            print(f"[stop] reached stop-after-hours={args.stop_after_hours}")
            break
    summarize(args)


def run_candidate_sequence(args: argparse.Namespace, candidate: CalibrationRun, started: float) -> tuple[str, str]:
    if args.smoke_first:
        smoke_log = run_one(args, candidate, stage="smoke", limit=1)
        if smoke_log is None or eval_status(smoke_log) != "success":
            message = f"Smoke failed for {candidate.model_id}"
            if args.continue_on_error:
                return candidate.model_id, message
            raise RuntimeError(message)
        if args.smoke_only:
            return candidate.model_id, "smoke_complete"

    if args.stop_after_hours and (time.monotonic() - started) / 3600 >= args.stop_after_hours:
        return candidate.model_id, f"skipped_stop_after_hours={args.stop_after_hours}"
    full_log = run_one(args, candidate, stage="full", limit=None)
    if full_log is None:
        return candidate.model_id, "no_eval_log"
    return candidate.model_id, eval_status(full_log)


def command_run_parallel(args: argparse.Namespace) -> None:
    if not args.yes:
        raise SystemExit("Live runs require --yes after reviewing run-manifest.csv.")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is required; value was not printed.")
    rows = write_plan(args)
    selected = selected_candidates(args)
    selected_cost = sum(float(row["estimated_cost_usd"]) for row in rows)
    if selected_cost > args.max_estimated_cost:
        raise SystemExit(f"Estimated cost ${selected_cost:.2f} exceeds cap ${args.max_estimated_cost:.2f}.")
    unavailable = [row["openrouter_model_id"] for row in rows if row["openrouter_available"] != "yes"]
    if unavailable:
        raise SystemExit(f"OpenRouter route(s) unavailable: {', '.join(unavailable)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    worker_count = max(1, min(args.route_workers, len(selected)))
    print(f"[parallel] selected_routes={len(selected)} route_workers={worker_count}")
    results: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(run_candidate_sequence, args, candidate, started): candidate for candidate in selected}
        for future in as_completed(futures):
            candidate = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = (candidate.model_id, f"error: {exc}")
                if not args.continue_on_error:
                    raise
            results.append(result)
            print(f"[parallel-result] {result[0]} {result[1]}")
    summarize(args)
    print(json.dumps({"parallel_results": results}, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "run", "run-parallel", "summarize"], nargs="?", default="plan")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", action="append", type=Path, default=[])
    parser.add_argument("--model", action="append", help="Restrict to a model id or paper model label; repeatable.")
    parser.add_argument("--include-existing", action="store_true", help="Also plan/run rows that already have exact evidence.")
    parser.add_argument("--max-estimated-cost", type=float, default=50.0)
    parser.add_argument("--max-connections", type=int, default=1)
    parser.add_argument("--smoke-first", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--continue-on-error", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--stop-after-hours", type=float, default=0.0)
    parser.add_argument("--route-workers", type=int, default=8)
    parser.add_argument("--reasoning-prompt-prefix", default="/no_think")
    parser.add_argument("--extra-body-json", default=DEFAULT_EXTRA_BODY_JSON)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir = args.output_dir.resolve()
    load_env([*DEFAULT_ENV_FILES, *args.env_file])
    if args.command == "plan":
        write_plan(args)
    elif args.command == "run":
        command_run(args)
    elif args.command == "run-parallel":
        command_run_parallel(args)
    else:
        rows = summarize(args)
        print(json.dumps({"summary_rows": len(rows), "output": str(args.output_dir / "calibration-summary.csv")}, indent=2))


if __name__ == "__main__":
    main()
