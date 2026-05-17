#!/usr/bin/env python3
"""Strict consistency checks for the full UniMoral release artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "results" / "release" / "2026-04-19-option1"
DEFAULT_FIGURE_DIR = ROOT / "figures" / "release"

MODEL_LINES = [
    "Qwen-S",
    "Qwen-M",
    "Qwen-L",
    "MiniMax-S",
    "MiniMax-M",
    "MiniMax-L",
    "DeepSeek-S",
    "DeepSeek-M",
    "DeepSeek-L",
    "Llama-S",
    "Llama-M",
    "Llama-L",
    "Gemma-S",
    "Gemma-M",
    "Gemma-L",
    "GPT4 only",
]

TASKS = {
    "unimoral_action_prediction": {"rq": "RQ1", "expected": 8784, "metric": "accuracy"},
    "unimoral_moral_typology": {"rq": "RQ2", "expected": 3492, "metric": "official_weighted_f1"},
    "unimoral_factor_attribution": {"rq": "RQ3", "expected": 3492, "metric": "official_weighted_f1"},
    "unimoral_consequence_generation": {"rq": "RQ4", "expected": 1782, "metric": "meteor"},
}

EXPECTED_SAMPLE_PREDICTION_ROWS = len(MODEL_LINES) * sum(
    task["expected"]
    for name, task in TASKS.items()
    if name != "unimoral_action_prediction"
)
PREDICTION_TASKS = {
    name: task
    for name, task in TASKS.items()
    if name != "unimoral_action_prediction"
}
FAILURE_CATEGORIES = {"api", "data", "format/parsing", "parsing", "runtime"}

REQUIRED_CSV_COLUMNS = {
    "unimoral-full-benchmark.csv": {
        "line_label",
        "family",
        "size_slot",
        "task_name",
        "rq",
        "task_label",
        "primary_metric",
        "expected_samples",
        "completed_samples",
        "status",
        "accuracy",
        "official_weighted_f1",
        "bleu",
        "meteor",
        "bert_score_f1",
        "rouge_l",
        "parsed_count",
        "log_path",
    },
    "unimoral-coverage.csv": {
        "rq",
        "task_name",
        "task_label",
        "status",
        "complete_model_lines",
        "reported_model_lines",
        "expected_model_lines",
        "expected_samples_per_model",
    },
    "unimoral-task-spread.csv": {
        "task_name",
        "task_label",
        "model_lines",
        "mean",
        "min",
        "max",
        "range",
        "diagnostic_read",
    },
    "unimoral-model-rankings.csv": {
        "task_name",
        "task_label",
        "rank",
        "line_label",
        "metric",
        "value",
    },
    "unimoral-sample-predictions.csv": {
        "line_label",
        "family",
        "size_slot",
        "task_name",
        "rq",
        "sample_id",
        "language",
        "scenario_id",
        "target_json",
        "prediction",
        "score_value",
        "bert_score_f1",
        "answer_source",
        "source_log_dir",
        "source_log_count",
    },
    "unimoral-failure-checklist.csv": {
        "line_label",
        "task_name",
        "status",
        "completed_samples",
        "expected_samples",
        "parsed_count",
        "category",
        "reason",
        "next_action",
        "log_path",
    },
    "unimoral-rq4-bertscore.csv": {
        "line_label",
        "task_name",
        "sample_id",
        "language",
        "bert_score_f1",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def csv_fieldnames(path: Path) -> set[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return set(csv.DictReader(handle).fieldnames or [])


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_file(path: Path, errors: list[str]) -> bool:
    if not path.exists():
        fail(errors, f"missing file: {path}")
        return False
    if path.stat().st_size == 0:
        fail(errors, f"empty file: {path}")
        return False
    return True


def _resolve_release_path(path_text: str, release_dir: Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    candidate = ROOT / path
    if candidate.exists():
        return candidate
    return release_dir / path


def _eval_status(path: Path) -> str:
    try:
        with ZipFile(path) as zf:
            if "header.json" not in zf.namelist():
                return "missing_header"
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, KeyError, json.JSONDecodeError, FileNotFoundError):
        return "unreadable"
    return str(header.get("status") or "unknown")


def _resolve_manifest_path(path_text: str, release_dir: Path, figure_dir: Path) -> Path | None:
    path = Path(path_text)
    if path.is_absolute():
        return path if path.exists() else None
    candidates = [
        ROOT / path,
        release_dir / path,
        figure_dir / path,
        release_dir / path.name,
        figure_dir / path.name,
    ]
    return next((candidate for candidate in candidates if candidate.exists()), None)


def _manifest_path_exists(path_text: str, release_dir: Path, figure_dir: Path) -> bool:
    return _resolve_manifest_path(path_text, release_dir, figure_dir) is not None


def _any_referenced_log_exists(full_rows: list[dict[str, str]], release_dir: Path) -> bool:
    for row in full_rows:
        if row.get("task_name") not in PREDICTION_TASKS:
            continue
        for path_text in str(row.get("log_path") or "").split(";"):
            if path_text and _resolve_release_path(path_text, release_dir).exists():
                return True
    return False


def _message_pair(message: str) -> tuple[str, str] | None:
    parts = message.split(maxsplit=2)
    if len(parts) < 2:
        return None
    line_label, task_name = parts[0], parts[1]
    if line_label in MODEL_LINES and task_name in PREDICTION_TASKS:
        return line_label, task_name
    return None


def _is_allowed_incomplete_error(
    message: str,
    *,
    incomplete_pairs: set[tuple[str, str]],
    incomplete_tasks: set[str],
    has_failure_rows: bool,
) -> bool:
    if " failure checklist " in message:
        return False
    pair = _message_pair(message)
    if pair in incomplete_pairs:
        return any(
            marker in message
            for marker in (
                "completed_samples=",
                "status=",
                "missing primary metric value",
                " log ",
                "sample predictions=",
                "empty sample score values",
            )
        )
    if message.startswith("unimoral-sample-predictions.csv has "):
        return bool(incomplete_pairs)
    if message.startswith("unimoral-failure-checklist.csv is not empty"):
        return has_failure_rows
    if " still contains incomplete-status phrase: " in message:
        return bool(incomplete_pairs)
    for task_name in incomplete_tasks:
        if message.startswith(f"{task_name} coverage ") and (
            "complete_model_lines=" in message
            or "reported_model_lines=" in message
            or "status=" in message
        ):
            return True
    return False


def verify_release(
    release_dir: Path,
    figure_dir: Path,
    *,
    allow_incomplete: bool,
) -> list[str]:
    errors: list[str] = []
    expected_task_count = len(TASKS)
    expected_model_task_rows = len(MODEL_LINES) * expected_task_count
    expected_total_samples = len(MODEL_LINES) * sum(task["expected"] for task in TASKS.values())
    expected_families = list(
        dict.fromkeys("GPT4 only" if line == "GPT4 only" else line.split("-", 1)[0] for line in MODEL_LINES)
    )
    required_files = [
        "unimoral-full-benchmark.csv",
        "unimoral-coverage.csv",
        "unimoral-task-spread.csv",
        "unimoral-model-rankings.csv",
        "unimoral-sample-predictions.csv",
        "unimoral-failure-checklist.csv",
        "benchmark-summary.csv",
        "benchmark-catalog.csv",
        "release-manifest.json",
        "README.md",
        "jenny-group-report.md",
    ]
    if "unimoral_consequence_generation" in TASKS:
        required_files.append("unimoral-rq4-bertscore.csv")
    for filename in required_files:
        require_file(release_dir / filename, errors)

    for filename in [
        "option1_unimoral_task_heatmap.svg",
        "option1_unimoral_task_rankings.svg",
        "option1_unimoral_task_spread.svg",
    ]:
        require_file(figure_dir / filename, errors)

    if errors:
        return errors

    for filename, required_columns in REQUIRED_CSV_COLUMNS.items():
        if filename == "unimoral-rq4-bertscore.csv" and "unimoral_consequence_generation" not in TASKS:
            continue
        actual_columns = csv_fieldnames(release_dir / filename)
        missing_columns = sorted(required_columns - actual_columns)
        if missing_columns:
            fail(errors, f"{filename} missing required columns: {missing_columns}")

    if errors:
        return errors

    full_rows = read_csv(release_dir / "unimoral-full-benchmark.csv")
    coverage_rows = read_csv(release_dir / "unimoral-coverage.csv")
    prediction_rows = read_csv(release_dir / "unimoral-sample-predictions.csv")
    failure_rows = read_csv(release_dir / "unimoral-failure-checklist.csv")
    benchmark_summary_rows = read_csv(release_dir / "benchmark-summary.csv")
    benchmark_catalog_rows = read_csv(release_dir / "benchmark-catalog.csv")
    incomplete_pairs = {
        (row.get("line_label", ""), row.get("task_name", ""))
        for row in full_rows
        if row.get("task_name") in PREDICTION_TASKS and row.get("status") != "complete"
    }
    documented_incomplete_pairs = {
        (row.get("line_label", ""), row.get("task_name", ""))
        for row in failure_rows
        if row.get("task_name") in PREDICTION_TASKS
    }
    incomplete_tasks = {
        str(row.get("task_name", ""))
        for row in coverage_rows
        if row.get("task_name") in PREDICTION_TASKS and row.get("status") != "complete"
    }
    full_by_pair = {(row["line_label"], row["task_name"]): row for row in full_rows}
    referenced_logs_available = _any_referenced_log_exists(full_rows, release_dir)

    expected_pairs = {(line, task) for line in MODEL_LINES for task in TASKS}
    actual_pairs = {(row["line_label"], row["task_name"]) for row in full_rows}
    missing_pairs = sorted(expected_pairs - actual_pairs)
    extra_pairs = sorted(actual_pairs - expected_pairs)
    if missing_pairs:
        fail(errors, f"missing model-task rows: {missing_pairs[:10]}")
    if extra_pairs:
        fail(errors, f"unexpected model-task rows: {extra_pairs[:10]}")
    if len(full_rows) != len(expected_pairs):
        fail(errors, f"unimoral-full-benchmark.csv has {len(full_rows)} rows, expected {len(expected_pairs)}")
    if len(actual_pairs) != len(full_rows):
        fail(errors, "unimoral-full-benchmark.csv contains duplicate model-task rows")

    for row in full_rows:
        task_name = row.get("task_name", "")
        task = TASKS.get(task_name)
        if task is None:
            continue
        if row.get("rq") != task["rq"]:
            fail(errors, f"{row['line_label']} {task_name} has rq={row.get('rq')} expected {task['rq']}")
        if row.get("primary_metric") != task["metric"]:
            fail(errors, f"{row['line_label']} {task_name} has primary_metric={row.get('primary_metric')} expected {task['metric']}")
        if row.get("expected_samples") != str(task["expected"]):
            fail(errors, f"{row['line_label']} {task_name} expected_samples={row.get('expected_samples')} expected {task['expected']}")
        if row.get("completed_samples") != str(task["expected"]):
            fail(errors, f"{row['line_label']} {task_name} completed_samples={row.get('completed_samples')} expected {task['expected']}")
        if row.get("status") != "complete":
            fail(errors, f"{row['line_label']} {task_name} status={row.get('status')} expected complete")
        metric_value = row.get(str(row.get("primary_metric", "")), "")
        if metric_value == "":
            fail(errors, f"{row['line_label']} {task_name} missing primary metric value")
        if task_name in PREDICTION_TASKS:
            log_paths = [path for path in str(row.get("log_path") or "").split(";") if path]
            if not log_paths:
                fail(errors, f"{row['line_label']} {task_name} missing Inspect log_path")
            if allow_incomplete and not referenced_logs_available:
                continue
            for path_text in log_paths:
                path = _resolve_release_path(path_text, release_dir)
                status = _eval_status(path)
                if status != "success":
                    fail(errors, f"{row['line_label']} {task_name} log {path_text} status={status} expected success")

    coverage_by_task = {row["task_name"]: row for row in coverage_rows}
    for task_name, task in TASKS.items():
        row = coverage_by_task.get(task_name)
        if row is None:
            fail(errors, f"missing coverage row for {task_name}")
            continue
        if row.get("rq") != task["rq"]:
            fail(errors, f"{task_name} coverage rq={row.get('rq')} expected {task['rq']}")
        for field in ("complete_model_lines", "reported_model_lines", "expected_model_lines"):
            if row.get(field) != str(len(MODEL_LINES)):
                fail(errors, f"{task_name} coverage {field}={row.get(field)} expected {len(MODEL_LINES)}")
        if row.get("status") != "complete":
            fail(errors, f"{task_name} coverage status={row.get('status')} expected complete")

    prediction_keys = [
        (row["line_label"], row["task_name"], row["sample_id"])
        for row in prediction_rows
    ]
    duplicate_prediction_count = len(prediction_keys) - len(set(prediction_keys))
    if len(prediction_rows) != EXPECTED_SAMPLE_PREDICTION_ROWS:
        fail(
            errors,
            f"unimoral-sample-predictions.csv has {len(prediction_rows)} rows, expected {EXPECTED_SAMPLE_PREDICTION_ROWS}",
        )
    if duplicate_prediction_count:
        fail(errors, "unimoral-sample-predictions.csv contains duplicate line/task/sample rows")
    predictions_by_pair: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in prediction_rows:
        predictions_by_pair.setdefault((row["line_label"], row["task_name"]), []).append(row)
    strict_prediction_gap = 0
    completion_audit_blocker_phrases: list[str] = []
    if missing_pairs:
        completion_audit_blocker_phrases.append(
            f"`unimoral-full-benchmark.csv`: {len(missing_pairs)} expected model-task rows missing"
        )
    if extra_pairs:
        completion_audit_blocker_phrases.append(
            f"`unimoral-full-benchmark.csv`: {len(extra_pairs)} unexpected model-task rows present"
        )
    duplicate_model_task_count = len(full_rows) - len(actual_pairs)
    if duplicate_model_task_count:
        completion_audit_blocker_phrases.append(
            f"`unimoral-full-benchmark.csv`: {duplicate_model_task_count} duplicate model-task rows prevent strict completion"
        )
    if duplicate_prediction_count:
        completion_audit_blocker_phrases.append(
            f"`unimoral-sample-predictions.csv`: {duplicate_prediction_count} duplicate "
            "line/task/sample prediction rows prevent strict completion"
        )
    for line in MODEL_LINES:
        for task_name, task in PREDICTION_TASKS.items():
            rows_for_pair = predictions_by_pair.get((line, task_name), [])
            if len(rows_for_pair) != task["expected"]:
                fail(errors, f"{line} {task_name} sample predictions={len(rows_for_pair)} expected {task['expected']}")
            empty_scores = sum(1 for row in rows_for_pair if row.get("score_value") in {None, ""})
            if empty_scores:
                fail(errors, f"{line} {task_name} has {empty_scores} empty sample score values")
            full_row = full_by_pair.get((line, task_name), {})
            status_value = str(full_row.get("status", "missing_row"))
            prediction_gap = max(0, int(task["expected"]) - len(rows_for_pair))
            if prediction_gap:
                strict_prediction_gap += prediction_gap
                completion_audit_blocker_phrases.append(
                    f"`{line}` `{task_name}`: {prediction_gap} sample predictions missing"
                )
            elif status_value != "complete":
                completion_audit_blocker_phrases.append(
                    f"`{line}` `{task_name}`: no sample-count gap "
                    f"({len(rows_for_pair)}/{task['expected']}) but status `{status_value}` prevents strict completion"
                )
    all_tasks_complete = all(row.get("status") == "complete" for row in coverage_rows)
    if all_tasks_complete:
        rq4_rows = [row for row in full_rows if row.get("task_name") == "unimoral_consequence_generation"]
        for row in rq4_rows:
            if row.get("bert_score_f1") in {None, ""}:
                fail(errors, f"{row['line_label']} unimoral_consequence_generation missing official BERTScore value")
        for line in MODEL_LINES:
            rows_for_pair = predictions_by_pair.get((line, "unimoral_consequence_generation"), [])
            missing_bert = sum(1 for row in rows_for_pair if row.get("bert_score_f1") in {None, ""})
            if missing_bert:
                fail(errors, f"{line} unimoral_consequence_generation has {missing_bert} missing per-sample BERTScore values")
    if failure_rows:
        fail(errors, f"unimoral-failure-checklist.csv is not empty ({len(failure_rows)} rows)")
    if allow_incomplete:
        undocumented_pairs = sorted(incomplete_pairs - documented_incomplete_pairs)
        stale_failure_pairs = sorted(documented_incomplete_pairs - incomplete_pairs)
        if undocumented_pairs:
            fail(errors, f"incomplete model-task rows missing from failure checklist: {undocumented_pairs[:10]}")
        if stale_failure_pairs:
            fail(errors, f"failure checklist contains rows that are now complete or missing: {stale_failure_pairs[:10]}")
        for row in failure_rows:
            pair = (row.get("line_label", ""), row.get("task_name", ""))
            task_name = pair[1]
            if task_name not in PREDICTION_TASKS:
                fail(errors, f"failure checklist contains unexpected task row: {pair}")
                continue
            full_row = full_by_pair.get(pair)
            if full_row is None:
                continue
            for field in ("status", "completed_samples", "expected_samples", "parsed_count"):
                if row.get(field) != full_row.get(field):
                    fail(
                        errors,
                        f"{pair[0]} {task_name} failure checklist {field}={row.get(field)!r} "
                        f"does not match benchmark row {full_row.get(field)!r}",
                    )
            if row.get("expected_samples") != str(PREDICTION_TASKS[task_name]["expected"]):
                fail(
                    errors,
                    f"{pair[0]} {task_name} failure checklist expected_samples={row.get('expected_samples')} "
                    f"expected {PREDICTION_TASKS[task_name]['expected']}",
                )
            if row.get("category") not in FAILURE_CATEGORIES:
                fail(errors, f"{pair[0]} {task_name} failure checklist category={row.get('category')!r} is not recognized")
            for field in ("reason", "next_action", "log_path"):
                if not str(row.get(field) or "").strip():
                    fail(errors, f"{pair[0]} {task_name} failure checklist missing {field}")
            next_action = str(row.get("next_action") or "")
            if pair[0].startswith("MiniMax-"):
                for phrase in (
                    "make unimoral-missing-plan",
                    "MiniMax explicitly allowed",
                    "UNIMORAL_ALLOW_MINIMAX=1",
                    "OPENROUTER_API_KEY",
                ):
                    if phrase not in next_action:
                        fail(
                            errors,
                            f"{pair[0]} {task_name} failure checklist next_action missing MiniMax safety phrase: {phrase!r}",
                        )

    summary_row = next((row for row in benchmark_summary_rows if row.get("benchmark") == "UniMoral"), None)
    if summary_row is None:
        fail(errors, "benchmark-summary.csv missing UniMoral row")
    else:
        expected_summary = {
            "task_types": str(expected_task_count),
            "evaluated_lines": str(expected_model_task_rows),
            "models_covered": str(len(expected_families)),
            "samples": str(expected_total_samples),
        }
        for field, expected in expected_summary.items():
            if summary_row.get(field) != expected:
                fail(errors, f"benchmark-summary.csv UniMoral {field}={summary_row.get(field)!r} expected {expected!r}")
        expected_mode = "benchmark_faithful; documented_incomplete" if incomplete_pairs else "benchmark_faithful"
        if summary_row.get("modes") != expected_mode:
            fail(errors, f"benchmark-summary.csv UniMoral modes={summary_row.get('modes')!r} expected {expected_mode!r}")

    catalog_row = next((row for row in benchmark_catalog_rows if row.get("benchmark") == "UniMoral"), None)
    if catalog_row is None:
        fail(errors, "benchmark-catalog.csv missing UniMoral row")
    else:
        expected_family_text = "; ".join(expected_families)
        if catalog_row.get("models_in_release") != expected_family_text:
            fail(errors, f"benchmark-catalog.csv UniMoral models_in_release={catalog_row.get('models_in_release')!r} expected {expected_family_text!r}")
        if catalog_row.get("samples_in_release") != str(expected_total_samples):
            fail(errors, f"benchmark-catalog.csv UniMoral samples_in_release={catalog_row.get('samples_in_release')!r} expected {expected_total_samples!r}")
        expected_mode = "benchmark_faithful; documented_incomplete" if incomplete_pairs else "benchmark_faithful"
        if "current_release_mode" in catalog_row and catalog_row.get("current_release_mode") != expected_mode:
            fail(errors, f"benchmark-catalog.csv UniMoral current_release_mode={catalog_row.get('current_release_mode')!r} expected {expected_mode!r}")
        if "all four UniMoral task definitions" not in str(catalog_row.get("repo_readout") or ""):
            fail(errors, "benchmark-catalog.csv UniMoral repo_readout does not mention all four task definitions")
        interpretation = str(catalog_row.get("release_interpretation") or "")
        if incomplete_pairs:
            if "unimoral-failure-checklist.csv" not in interpretation:
                fail(errors, "benchmark-catalog.csv UniMoral release_interpretation does not point to unimoral-failure-checklist.csv")
        elif "incomplete" in interpretation.lower() or "parse-limited" in interpretation.lower():
            fail(errors, "benchmark-catalog.csv UniMoral release_interpretation still describes incomplete coverage")

    manifest = json.loads((release_dir / "release-manifest.json").read_text(encoding="utf-8"))
    manifest_benchmarks = manifest.get("benchmarks", [])
    manifest_unimoral = next((row for row in manifest_benchmarks if row.get("benchmark") == "UniMoral"), None)
    if manifest_unimoral is None:
        fail(errors, "release-manifest.json missing UniMoral benchmark row")
    else:
        expected_manifest = {
            "task_types": expected_task_count,
            "evaluated_lines": expected_model_task_rows,
            "models_covered": len(expected_families),
            "samples": expected_total_samples,
            "modes": "benchmark_faithful; documented_incomplete" if incomplete_pairs else "benchmark_faithful",
        }
        for field, expected in expected_manifest.items():
            if str(manifest_unimoral.get(field)) != str(expected):
                fail(
                    errors,
                    f"release-manifest.json UniMoral {field}={manifest_unimoral.get(field)!r} expected {expected!r}",
                )
    try:
        manifest_sample_total = sum(int(row.get("samples") or 0) for row in manifest_benchmarks)
        manifest_evaluated_total = sum(int(row.get("evaluated_lines") or 0) for row in manifest_benchmarks)
        manifest_benchmark_faithful_total = sum(
            int(row.get("evaluated_lines") or 0)
            for row in manifest_benchmarks
            if "benchmark_faithful" in str(row.get("modes") or "")
        )
        manifest_proxy_total = sum(
            int(row.get("evaluated_lines") or 0)
            for row in manifest_benchmarks
            if str(row.get("modes") or "") == "proxy"
        )
    except (TypeError, ValueError):
        manifest_sample_total = None
        manifest_evaluated_total = None
        manifest_benchmark_faithful_total = None
        manifest_proxy_total = None
    manifest_counts = manifest.get("counts", {})
    if manifest_sample_total is not None:
        counts_total = manifest_counts.get("total_samples")
        if str(counts_total) != str(manifest_sample_total):
            fail(
                errors,
                f"release-manifest.json counts.total_samples={counts_total!r} expected benchmark sample sum {manifest_sample_total!r}",
            )
    if manifest_evaluated_total is not None:
        expected_counts = {
            "authoritative_tasks": manifest_evaluated_total,
            "benchmark_faithful_tasks": manifest_benchmark_faithful_total,
            "proxy_tasks": manifest_proxy_total,
        }
        for field, expected in expected_counts.items():
            value = manifest_counts.get(field)
            if str(value) != str(expected):
                fail(errors, f"release-manifest.json counts.{field}={value!r} expected benchmark evaluated-line sum {expected!r}")

    entry_points = manifest.get("entry_points", {})
    for key in [
        "unimoral_full_benchmark",
        "unimoral_coverage",
        "unimoral_task_spread",
        "unimoral_model_rankings",
        "unimoral_sample_predictions",
        "unimoral_failure_checklist",
        "unimoral_completion_audit",
        "unimoral_minimax_resume_plan",
        "unimoral_rq4_bertscore",
        "unimoral_task_heatmap_figure",
        "unimoral_task_rankings_figure",
        "unimoral_task_spread_figure",
    ]:
        if key == "unimoral_rq4_bertscore" and "unimoral_consequence_generation" not in TASKS:
            continue
        if key not in entry_points:
            fail(errors, f"release-manifest.json missing entry_points.{key}")
            continue
        if not _manifest_path_exists(str(entry_points[key]), release_dir, figure_dir):
            fail(errors, f"release-manifest.json entry_points.{key} points to missing artifact: {entry_points[key]}")

    resume_plan_entry = entry_points.get("unimoral_minimax_resume_plan")
    if resume_plan_entry:
        resume_plan_path = _resolve_manifest_path(str(resume_plan_entry), release_dir, figure_dir)
        if resume_plan_path is not None:
            resume_plan_text = resume_plan_path.read_text(encoding="utf-8")
            if "No MiniMax blockers are listed" not in resume_plan_text:
                required_phrases = [
                    "without granting permission to run MiniMax",
                    "make unimoral-missing-plan",
                    "UNIMORAL_DRY_RUN=1",
                    "Do not infer labels from hidden reasoning",
                    "Local Samplebuffer Audit",
                    "Google Drive was searched",
                    "UNIMORAL_ALLOW_MINIMAX=1",
                    "UNIMORAL_RERUN_UNPARSED_MAX_GAP=3` on May 17, 2026",
                    "key_state=missing",
                    "MiniMax-L` | `unimoral_consequence_generation",
                ]
                for phrase in required_phrases:
                    if phrase not in resume_plan_text:
                        fail(errors, f"unimoral-minimax-resume-plan.md missing required phrase: {phrase!r}")

    completion_audit_entry = entry_points.get("unimoral_completion_audit")
    if completion_audit_entry:
        completion_audit_path = _resolve_manifest_path(str(completion_audit_entry), release_dir, figure_dir)
        if completion_audit_path is not None:
            completion_audit_text = completion_audit_path.read_text(encoding="utf-8")
            required_phrases = [
                "Prompt-to-Artifact Checklist",
                "Strict completion is",
                "No MiniMax provider calls are made by generating this audit.",
                "make unimoral-missing-plan",
                "dry-run only",
                "UNIMORAL_ALLOW_MINIMAX=1",
                "Clean committed branch",
                "`git status --short --branch`",
                "`git rev-list --left-right --count HEAD...@{upstream}`",
                "0/0 ahead-behind",
                "final operator report",
                "external final check",
                "CSV-Level Strict Blockers",
                "Total strict sample prediction gap",
            ]
            for phrase in required_phrases:
                if phrase not in completion_audit_text:
                    fail(errors, f"unimoral-completion-audit.md missing required phrase: {phrase!r}")
            strict_complete = not failure_rows and not incomplete_tasks
            if strict_complete and "Status: **achieved**." not in completion_audit_text:
                fail(errors, "unimoral-completion-audit.md does not mark strict-complete artifacts as achieved")
            if not strict_complete and "Status: **not achieved**." not in completion_audit_text:
                fail(errors, "unimoral-completion-audit.md does not mark incomplete artifacts as not achieved")
            sample_count_phrase = (
                f"{len(prediction_rows)} rows present; strict expected count is {EXPECTED_SAMPLE_PREDICTION_ROWS}."
            )
            if sample_count_phrase not in completion_audit_text:
                fail(errors, f"unimoral-completion-audit.md missing current sample prediction count: {sample_count_phrase!r}")
            gap_phrase = f"Total strict sample prediction gap: **{strict_prediction_gap}** rows."
            if gap_phrase not in completion_audit_text:
                fail(errors, f"unimoral-completion-audit.md missing current strict prediction gap: {gap_phrase!r}")
            if completion_audit_blocker_phrases:
                for phrase in completion_audit_blocker_phrases:
                    if phrase not in completion_audit_text:
                        fail(errors, f"unimoral-completion-audit.md missing CSV blocker phrase: {phrase!r}")
            elif "No CSV-level strict blockers remain" not in completion_audit_text:
                fail(errors, "unimoral-completion-audit.md does not say CSV-level strict blockers are clear")
            stale_audit_phrases = [
                "current user instruction",
                "forbids MiniMax runs",
            ]
            for phrase in stale_audit_phrases:
                if phrase in completion_audit_text:
                    fail(errors, f"unimoral-completion-audit.md contains stale operator-context phrase: {phrase!r}")

    stale_phrases = [
        "current model-line matrix is not yet fully complete",
        "Incomplete or parse-limited cells",
        "coverage caveats",
        "provider cells remain incomplete",
        "remain incomplete",
    ]
    for path in [ROOT / "README.md", release_dir / "README.md", release_dir / "jenny-group-report.md"]:
        text = path.read_text(encoding="utf-8")
        for phrase in stale_phrases:
            if phrase in text:
                fail(errors, f"{path} still contains incomplete-status phrase: {phrase!r}")

    if allow_incomplete:
        allowed_pairs = documented_incomplete_pairs if documented_incomplete_pairs else incomplete_pairs
        return [
            error
            for error in errors
            if not _is_allowed_incomplete_error(
                error,
                incomplete_pairs=allowed_pairs,
                incomplete_tasks=incomplete_tasks,
                has_failure_rows=bool(failure_rows),
            )
        ]
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-dir", default=DEFAULT_RELEASE_DIR, type=Path)
    parser.add_argument("--figure-dir", default=DEFAULT_FIGURE_DIR, type=Path)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow known incomplete model-task cells while still checking artifact structure and naming.",
    )
    args = parser.parse_args()

    errors = verify_release(args.release_dir, args.figure_dir, allow_incomplete=args.allow_incomplete)
    if errors:
        print("UniMoral completion verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("UniMoral completion verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
