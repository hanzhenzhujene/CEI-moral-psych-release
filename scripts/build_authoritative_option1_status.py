"""Reconcile local Option 1 run namespaces into a single authoritative status table.

This script is maintainer-facing: it depends on the raw local full-run folders
under `results/inspect/` and is used to refresh the tracked public release
snapshot when provenance needs to be rebuilt from source logs.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = ROOT / "results" / "inspect" / "full-runs"
OUTPUT_ROOT = RESULTS_ROOT / "2026-04-19-option1-authoritative-status"
TRACE_ROOT = Path.home() / "Library" / "Application Support" / "inspect_ai" / "traces"

RUN_SUMMARIES = {
    "main_funded": RESULTS_ROOT / "2026-04-17-option1-full-funded" / "progress-summary.csv",
    "gemma_paid_v2": RESULTS_ROOT / "2026-04-17-option1-full-funded-gemma-paid-v2" / "progress-summary.csv",
    "qwen_recovery_v1": RESULTS_ROOT / "2026-04-18-option1-full-funded-qwen-recovery-v1" / "progress-summary.csv",
    "denevil_formal_v3": RESULTS_ROOT / "2026-04-18-denevil-fulcra-proxy-formal-v3" / "progress-summary.csv",
    "denevil_recovery_v1": RESULTS_ROOT / "2026-04-18-denevil-fulcra-proxy-recovery-v1" / "progress-summary.csv",
}

RECENT_ERROR_PATTERN = re.compile(r"HTTP/1\.1 (402|429|403|500)")


@dataclass(frozen=True)
class AuthoritativeTask:
    benchmark: str
    benchmark_scope: str
    model_family: str
    family: str
    task: str
    source_run: str
    benchmark_mode: str
    authoritative_reason: str
    note: str = ""


AUTHORITATIVE_TASKS: list[AuthoritativeTask] = [
    AuthoritativeTask(
        benchmark="UniMoral",
        benchmark_scope="Option 1 action prediction",
        model_family="Qwen",
        family="qwen_text",
        task="unimoral_action_prediction",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
    ),
    AuthoritativeTask(
        benchmark="UniMoral",
        benchmark_scope="Option 1 action prediction",
        model_family="DeepSeek",
        family="deepseek_text",
        task="unimoral_action_prediction",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
    ),
    AuthoritativeTask(
        benchmark="UniMoral",
        benchmark_scope="Option 1 action prediction",
        model_family="Gemma",
        family="gemma_text",
        task="unimoral_action_prediction",
        source_run="gemma_paid_v2",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Paid Gemma recovery supersedes the stalled free-tier namespace.",
    ),
    AuthoritativeTask(
        benchmark="SMID",
        benchmark_scope="Moral rating",
        model_family="Qwen",
        family="qwen_smid",
        task="smid_moral_rating",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
        note="Vision-capable route.",
    ),
    AuthoritativeTask(
        benchmark="SMID",
        benchmark_scope="Foundation classification",
        model_family="Qwen",
        family="qwen_smid",
        task="smid_foundation_classification",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
        note="Vision-capable route.",
    ),
    AuthoritativeTask(
        benchmark="SMID",
        benchmark_scope="Moral rating",
        model_family="Gemma",
        family="gemma_smid",
        task="smid_moral_rating",
        source_run="gemma_paid_v2",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Paid Gemma recovery supersedes the stalled free-tier namespace.",
        note="Vision-capable route.",
    ),
    AuthoritativeTask(
        benchmark="SMID",
        benchmark_scope="Foundation classification",
        model_family="Gemma",
        family="gemma_smid",
        task="smid_foundation_classification",
        source_run="gemma_paid_v2",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Paid Gemma recovery supersedes the stalled free-tier namespace.",
        note="Vision-capable route.",
    ),
    AuthoritativeTask(
        benchmark="Value Kaleidoscope",
        benchmark_scope="Relevance",
        model_family="Qwen",
        family="qwen_text",
        task="value_prism_relevance",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
    ),
    AuthoritativeTask(
        benchmark="Value Kaleidoscope",
        benchmark_scope="Valence",
        model_family="Qwen",
        family="qwen_text",
        task="value_prism_valence",
        source_run="qwen_recovery_v1",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Qwen recovery namespace supersedes the earlier 402-stopped main-funded attempt.",
    ),
    AuthoritativeTask(
        benchmark="Value Kaleidoscope",
        benchmark_scope="Relevance",
        model_family="DeepSeek",
        family="deepseek_text",
        task="value_prism_relevance",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
    ),
    AuthoritativeTask(
        benchmark="Value Kaleidoscope",
        benchmark_scope="Valence",
        model_family="DeepSeek",
        family="deepseek_text",
        task="value_prism_valence",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
    ),
    AuthoritativeTask(
        benchmark="Value Kaleidoscope",
        benchmark_scope="Relevance",
        model_family="Gemma",
        family="gemma_text",
        task="value_prism_relevance",
        source_run="gemma_paid_v2",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Paid Gemma recovery supersedes the stalled free-tier namespace.",
    ),
    AuthoritativeTask(
        benchmark="Value Kaleidoscope",
        benchmark_scope="Valence",
        model_family="Gemma",
        family="gemma_text",
        task="value_prism_valence",
        source_run="gemma_paid_v2",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Paid Gemma recovery supersedes the stalled free-tier namespace.",
    ),
    AuthoritativeTask(
        benchmark="CCD-Bench",
        benchmark_scope="Selection",
        model_family="Qwen",
        family="qwen_text",
        task="ccd_bench_selection",
        source_run="qwen_recovery_v1",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Qwen recovery namespace supersedes the earlier 402-stopped main-funded attempt.",
    ),
    AuthoritativeTask(
        benchmark="CCD-Bench",
        benchmark_scope="Selection",
        model_family="DeepSeek",
        family="deepseek_text",
        task="ccd_bench_selection",
        source_run="main_funded",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Main funded namespace completed this task cleanly.",
    ),
    AuthoritativeTask(
        benchmark="CCD-Bench",
        benchmark_scope="Selection",
        model_family="Gemma",
        family="gemma_text",
        task="ccd_bench_selection",
        source_run="gemma_paid_v2",
        benchmark_mode="benchmark_faithful",
        authoritative_reason="Paid Gemma recovery supersedes the stalled free-tier namespace.",
    ),
    AuthoritativeTask(
        benchmark="Denevil",
        benchmark_scope="FULCRA-backed proxy generation",
        model_family="Qwen",
        family="qwen_proxy",
        task="denevil_fulcra_proxy_generation",
        source_run="denevil_recovery_v1",
        benchmark_mode="proxy",
        authoritative_reason="Recovery namespace supersedes the earlier 402-stopped formal-v3 attempt.",
        note="Proxy only; not benchmark-faithful MoralPrompt.",
    ),
    AuthoritativeTask(
        benchmark="Denevil",
        benchmark_scope="FULCRA-backed proxy generation",
        model_family="DeepSeek",
        family="deepseek_proxy",
        task="denevil_fulcra_proxy_generation",
        source_run="denevil_recovery_v1",
        benchmark_mode="proxy",
        authoritative_reason="Recovery namespace supersedes the earlier 402-stopped formal-v3 attempt.",
        note="Proxy only; not benchmark-faithful MoralPrompt.",
    ),
    AuthoritativeTask(
        benchmark="Denevil",
        benchmark_scope="FULCRA-backed proxy generation",
        model_family="Gemma",
        family="gemma_proxy",
        task="denevil_fulcra_proxy_generation",
        source_run="denevil_formal_v3",
        benchmark_mode="proxy",
        authoritative_reason="Formal-v3 namespace completed successfully on paid Gemma.",
        note="Proxy only; not benchmark-faithful MoralPrompt.",
    ),
]


def load_run_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return {(row["family"], row["task"]): row for row in reader}


def format_percent(value: str) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return value


def to_int(value: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def normalize_repo_path(path_text: str) -> str:
    path = Path(path_text)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path_text


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else (ROOT / path)


def build_rows() -> list[dict[str, str]]:
    run_data = {name: load_run_rows(path) for name, path in RUN_SUMMARIES.items()}
    rows: list[dict[str, str]] = []

    for item in AUTHORITATIVE_TASKS:
        source_rows = run_data[item.source_run]
        key = (item.family, item.task)
        if key not in source_rows:
            raise KeyError(f"Missing authoritative row for {item.source_run}: {key}")

        source_row = source_rows[key]
        rows.append(
            {
                "benchmark": item.benchmark,
                "benchmark_scope": item.benchmark_scope,
                "benchmark_mode": item.benchmark_mode,
                "model_family": item.model_family,
                "family": item.family,
                "task": item.task,
                "model": source_row["model"],
                "status": source_row["status"],
                "completed_samples": source_row["completed_samples"],
                "total_samples": source_row["total_samples"],
                "progress_pct": source_row["progress_pct"],
                "accuracy": source_row.get("accuracy", ""),
                "stderr": source_row.get("stderr", ""),
                "source_run": item.source_run,
                "source_created_at": source_row["created_at"],
                "source_eval_path": normalize_repo_path(source_row["eval_path"]),
                "authoritative_reason": item.authoritative_reason,
                "note": item.note,
            }
        )

    rows.sort(key=lambda row: (row["benchmark"], row["model_family"], row["benchmark_scope"]))
    return rows


def run_command(args: list[str]) -> str:
    result = subprocess.run(args, check=True, capture_output=True)
    return result.stdout.decode("utf-8", errors="replace")


def find_active_pid(log_dir: Path) -> int | None:
    output = run_command(["ps", "-Ao", "pid=,comm=,command="])
    candidates = {str(log_dir)}
    try:
        candidates.add(str(log_dir.relative_to(ROOT)))
    except ValueError:
        pass

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or "src/inspect/run.py" not in stripped:
            continue
        match = re.match(r"^(\d+)\s+(\S+)\s+(.*)$", stripped)
        if not match:
            continue

        pid_text, comm, command = match.groups()
        comm_lower = comm.lower()
        if "zsh" in comm_lower or "tee" in comm_lower:
            continue
        if not any(candidate in command for candidate in candidates):
            continue
        try:
            return int(pid_text)
        except ValueError:
            continue
    return None


def find_trace_path(pid: int) -> Path | None:
    try:
        output = run_command(["lsof", "-Fn", "-p", str(pid)])
    except subprocess.CalledProcessError:
        return None

    for line in output.splitlines():
        if not line.startswith("n"):
            continue
        candidate = Path(line[1:])
        if candidate.parent == TRACE_ROOT and candidate.name.startswith("trace-") and candidate.suffix == ".log":
            return candidate
    return None


def parse_trace_timestamp(line: str) -> datetime | None:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None

    timestamp = payload.get("timestamp")
    if not timestamp:
        return None

    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        return None


def summarize_trace(trace_path: Path) -> dict[str, str]:
    content = trace_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    http_200_count = content.count('HTTP/1.1 200 OK')

    last_timestamp: datetime | None = None
    for line in reversed(lines):
        last_timestamp = parse_trace_timestamp(line)
        if last_timestamp is not None:
            break

    recent_window = lines[-400:]
    recent_errors: list[str] = []
    for line in recent_window:
        match = RECENT_ERROR_PATTERN.search(line)
        if match:
            recent_errors.append(match.group(1))

    recent_error_codes = ",".join(sorted(set(recent_errors)))
    now = datetime.now(ZoneInfo("America/New_York"))
    if last_timestamp is not None:
        last_timestamp_local = last_timestamp.astimezone(ZoneInfo("America/New_York"))
        last_timestamp_text = last_timestamp_local.isoformat()
        minutes_since_last_event = (now - last_timestamp_local).total_seconds() / 60
        age_text = f"{minutes_since_last_event:.2f}"
    else:
        last_timestamp_text = ""
        age_text = ""

    return {
        "trace_path": str(trace_path),
        "trace_http_200_count": str(http_200_count),
        "trace_last_timestamp": last_timestamp_text,
        "trace_age_minutes": age_text,
        "recent_error_count": str(len(recent_errors)),
        "recent_error_codes": recent_error_codes,
    }


def build_live_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    live_rows: list[dict[str, str]] = []

    for row in rows:
        if row["status"] != "running":
            continue

        log_dir = resolve_repo_path(row["source_eval_path"]).parent
        pid = find_active_pid(log_dir)
        live_row = {
            "benchmark": row["benchmark"],
            "task": row["task"],
            "model_family": row["model_family"],
            "family": row["family"],
            "source_run": row["source_run"],
            "status": row["status"],
            "official_completed_samples": row["completed_samples"],
            "official_total_samples": row["total_samples"],
            "official_progress_pct": row["progress_pct"],
            "pid": str(pid or ""),
            "process_alive": "yes" if pid else "no",
            "trace_path": "",
            "trace_http_200_count": "",
            "trace_last_timestamp": "",
            "trace_age_minutes": "",
            "recent_error_count": "",
            "recent_error_codes": "",
            "heartbeat_status": "not_running",
        }

        if pid is None:
            live_rows.append(live_row)
            continue

        trace_path = find_trace_path(pid)
        if trace_path is None or not trace_path.exists():
            live_row["heartbeat_status"] = "running_no_trace_found"
            live_rows.append(live_row)
            continue

        live_row.update(summarize_trace(trace_path))

        try:
            age_minutes = float(live_row["trace_age_minutes"])
        except ValueError:
            age_minutes = 10_000.0

        if age_minutes <= 10 and live_row["recent_error_count"] == "0":
            heartbeat_status = "healthy"
        elif age_minutes <= 10:
            heartbeat_status = "active_with_recent_errors"
        else:
            heartbeat_status = "process_alive_but_quiet"

        live_row["heartbeat_status"] = heartbeat_status
        live_rows.append(live_row)

    live_rows.sort(key=lambda row: (row["model_family"], row["task"]))
    return live_rows


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_live_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "benchmark",
        "task",
        "model_family",
        "family",
        "source_run",
        "status",
        "official_completed_samples",
        "official_total_samples",
        "official_progress_pct",
        "pid",
        "process_alive",
        "trace_path",
        "trace_http_200_count",
        "trace_last_timestamp",
        "trace_age_minutes",
        "recent_error_count",
        "recent_error_codes",
        "heartbeat_status",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_model_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["model_family"], []).append(row)

    summary_rows: list[dict[str, str]] = []
    for model_family, model_rows in sorted(grouped.items()):
        complete = sum(1 for row in model_rows if row["status"] == "success")
        running = sum(1 for row in model_rows if row["status"] == "running")
        errored = sum(1 for row in model_rows if row["status"] == "error")
        summary_rows.append(
            {
                "model_family": model_family,
                "task_count": str(len(model_rows)),
                "success_count": str(complete),
                "running_count": str(running),
                "error_count": str(errored),
                "benchmark_modes": ", ".join(sorted({row["benchmark_mode"] for row in model_rows})),
            }
        )
    return summary_rows


def render_markdown(rows: list[dict[str, str]], live_rows: list[dict[str, str]], output_path: Path) -> None:
    snapshot = datetime.now(ZoneInfo("America/New_York")).strftime("%B %d, %Y, %H:%M %Z")
    total_rows = len(rows)
    success_rows = sum(1 for row in rows if row["status"] == "success")
    running_rows = sum(1 for row in rows if row["status"] == "running")
    error_rows = sum(1 for row in rows if row["status"] == "error")
    model_summary = build_model_summary(rows)

    lines: list[str] = []
    lines.append("# Option 1 Authoritative Status")
    lines.append("")
    lines.append(f"Snapshot time: {snapshot}")
    lines.append("")
    lines.append("## What This File Is")
    lines.append("")
    lines.append("This is the authoritative cross-namespace status table for the moral-psych `Option 1` slice that Jenny has been running in CEI.")
    lines.append("")
    lines.append("It resolves stale or superseded namespaces by choosing the current source of truth for each task.")
    lines.append("")
    lines.append("## High-Level Status")
    lines.append("")
    lines.append(f"- Authoritative tasks tracked: `{total_rows}`")
    lines.append(f"- Successful tasks: `{success_rows}`")
    lines.append(f"- Running tasks: `{running_rows}`")
    lines.append(f"- Error tasks: `{error_rows}`")
    lines.append("")
    lines.append("## Scope Notes")
    lines.append("")
    lines.append("- This is the `Option 1` task slice, not yet the full meeting-notes sweep over every model family and three size tiers.")
    lines.append("- `Denevil` is currently represented by a `FULCRA`-backed proxy task, because a benchmark-faithful public `MoralPrompt` export is still unavailable locally.")
    lines.append("- Free-tier Gemma artifacts in the original funded namespace are audit history only. Paid Gemma recovery is the authoritative Gemma source.")
    lines.append("")
    lines.append("## Model Summary")
    lines.append("")
    lines.append("| Model Family | Tasks | Success | Running | Error | Modes |")
    lines.append("| --- | ---: | ---: | ---: | ---: | --- |")
    for row in model_summary:
        lines.append(
            f"| {row['model_family']} | {row['task_count']} | {row['success_count']} | {row['running_count']} | {row['error_count']} | {row['benchmark_modes']} |"
        )
    lines.append("")
    lines.append("## Authoritative Task Table")
    lines.append("")
    lines.append("| Benchmark | Scope | Model Family | Status | Progress | Source Run | Mode | Notes |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        progress = f"{row['completed_samples']} / {row['total_samples']} ({format_percent(row['progress_pct'])})"
        notes = row["note"] or row["authoritative_reason"]
        lines.append(
            f"| {row['benchmark']} | `{row['task']}` | {row['model_family']} | {row['status']} | {progress} | `{row['source_run']}` | {row['benchmark_mode']} | {notes} |"
        )
    lines.append("")
    lines.append("## Current Remaining Work")
    lines.append("")
    remaining = [row for row in rows if row["status"] != "success"]
    if not remaining:
        lines.append("- All authoritative tasks are complete.")
    else:
        for row in remaining:
            progress = f"{row['completed_samples']} / {row['total_samples']} ({format_percent(row['progress_pct'])})"
            lines.append(
                f"- `{row['model_family']}` `{row['task']}` is `{row['status']}` at {progress} in `{row['source_run']}`."
            )
    lines.append("")
    if live_rows:
        lines.append("## Live Heartbeat For Running Tasks")
        lines.append("")
        lines.append("These are live trace-health signals for currently running tasks.")
        lines.append("")
        lines.append("They are useful for monitoring, but they do not replace the authoritative flushed sample counts above.")
        lines.append("")
        lines.append("| Model Family | Task | PID | Official Progress | Trace HTTP 200s | Last Trace Event | Trace Age (min) | Recent Error Codes | Heartbeat |")
        lines.append("| --- | --- | ---: | --- | ---: | --- | ---: | --- | --- |")
        for row in live_rows:
            progress = (
                f"{row['official_completed_samples']} / {row['official_total_samples']} "
                f"({format_percent(row['official_progress_pct'])})"
            )
            last_event = row["trace_last_timestamp"] or "n/a"
            error_codes = row["recent_error_codes"] or "none"
            lines.append(
                f"| {row['model_family']} | `{row['task']}` | {row['pid'] or 'n/a'} | {progress} | "
                f"{row['trace_http_200_count'] or 'n/a'} | {last_event} | {row['trace_age_minutes'] or 'n/a'} | "
                f"{error_codes} | {row['heartbeat_status']} |"
            )
        lines.append("")
    lines.append("## Authoritative Namespace Mapping")
    lines.append("")
    lines.append("- `main_funded`: DeepSeek text, Qwen text early tasks, Qwen SMID")
    lines.append("- `gemma_paid_v2`: all authoritative Gemma text and Gemma SMID tasks")
    lines.append("- `qwen_recovery_v1`: Qwen `value_prism_valence` and `ccd_bench_selection`")
    lines.append("- `denevil_formal_v3`: Gemma `Denevil` proxy success")
    lines.append("- `denevil_recovery_v1`: authoritative completed Qwen and DeepSeek `Denevil` proxy recovery runs")
    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_live_markdown(live_rows: list[dict[str, str]], output_path: Path) -> None:
    snapshot = datetime.now(ZoneInfo("America/New_York")).strftime("%B %d, %Y, %H:%M %Z")
    lines: list[str] = []
    lines.append("# Option 1 Live Heartbeat")
    lines.append("")
    lines.append(f"Snapshot time: {snapshot}")
    lines.append("")
    lines.append("## What This File Is")
    lines.append("")
    lines.append("This is a live-monitoring companion to the authoritative Option 1 status package.")
    lines.append("")
    lines.append("It reports process and trace health for currently running tasks, especially when `.eval` archives have not yet flushed new sample files.")
    lines.append("")
    if not live_rows:
        lines.append("## Current State")
        lines.append("")
        lines.append("- No authoritative tasks are currently marked as running.")
    else:
        lines.append("## Current State")
        lines.append("")
        lines.append("| Model Family | Task | PID | Process Alive | Official Progress | Trace HTTP 200s | Last Trace Event | Trace Age (min) | Recent Error Codes | Heartbeat |")
        lines.append("| --- | --- | ---: | --- | --- | ---: | --- | ---: | --- | --- |")
        for row in live_rows:
            progress = (
                f"{row['official_completed_samples']} / {row['official_total_samples']} "
                f"({format_percent(row['official_progress_pct'])})"
            )
            lines.append(
                f"| {row['model_family']} | `{row['task']}` | {row['pid'] or 'n/a'} | {row['process_alive']} | "
                f"{progress} | {row['trace_http_200_count'] or 'n/a'} | {row['trace_last_timestamp'] or 'n/a'} | "
                f"{row['trace_age_minutes'] or 'n/a'} | {row['recent_error_codes'] or 'none'} | {row['heartbeat_status']} |"
            )
        lines.append("")
        lines.append("## Interpretation")
        lines.append("")
        lines.append("- `Official Progress` comes from flushed sample files in the authoritative `.eval` archive.")
        lines.append("- `Trace HTTP 200s` is a live transport-health signal from the active Inspect trace and can move ahead of the flushed archive.")
        lines.append("- A `healthy` heartbeat means the process is alive, the trace is fresh, and no recent `402`, `429`, `403`, or `500` HTTP responses were seen in the recent trace window.")
    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    live_rows = build_live_rows(rows)
    csv_path = OUTPUT_ROOT / "authoritative-summary.csv"
    md_path = OUTPUT_ROOT / "authoritative-summary.md"
    live_csv_path = OUTPUT_ROOT / "live-heartbeat.csv"
    live_md_path = OUTPUT_ROOT / "live-heartbeat.md"
    write_csv(rows, csv_path)
    write_live_csv(live_rows, live_csv_path)
    render_markdown(rows, live_rows, md_path)
    render_live_markdown(live_rows, live_md_path)
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {live_csv_path}")
    print(f"Wrote {live_md_path}")


if __name__ == "__main__":
    main()
