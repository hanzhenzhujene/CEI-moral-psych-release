#!/usr/bin/env python3
"""Summarize raw Inspect `.eval` artifacts into CSV, Markdown, and JSON views."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


@dataclass
class EvalProgress:
    family: str
    task: str
    model: str
    created_at: str
    status: str
    total_samples: int
    completed_samples: int
    progress_pct: float
    artifact_mb: float
    eval_path: str
    note: str = ""
    accuracy: str = ""
    stderr: str = ""
    error_message: str = ""


def _read_json(zf: ZipFile, member: str) -> dict[str, Any] | list[Any] | None:
    try:
        return json.loads(zf.read(member).decode("utf-8"))
    except KeyError:
        return None


def _iso_from_epoch(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).astimezone().isoformat()


def _parse_eval(eval_path: Path, log_root: Path) -> EvalProgress:
    family = eval_path.relative_to(log_root).parts[0]
    artifact_mb = eval_path.stat().st_size / (1024 * 1024)
    created_at = _iso_from_epoch(eval_path.stat().st_mtime)

    try:
        with ZipFile(eval_path) as zf:
            header = _read_json(zf, "header.json")
            start = _read_json(zf, "_journal/start.json")
            members = zf.namelist()
    except BadZipFile:
        return EvalProgress(
            family=family,
            task=eval_path.stem,
            model="",
            created_at=created_at,
            status="unreadable",
            total_samples=0,
            completed_samples=0,
            progress_pct=0.0,
            artifact_mb=artifact_mb,
            eval_path=str(eval_path),
            note="zip still being written",
        )

    base = header or start or {}
    eval_meta = base.get("eval", {}) if isinstance(base, dict) else {}
    task = str(eval_meta.get("task", eval_path.stem))
    model = str(eval_meta.get("model", ""))
    created_at = str(eval_meta.get("created", created_at))
    total_samples = int(eval_meta.get("dataset", {}).get("samples", 0) or 0)
    sample_members = [name for name in members if name.startswith("samples/") and name.endswith(".json")]
    completed_samples = len(sample_members)
    progress_pct = (completed_samples / total_samples * 100.0) if total_samples else 0.0

    status = "running"
    accuracy = ""
    stderr = ""
    note = ""
    error_message = ""

    if isinstance(header, dict):
        status = str(header.get("status", "success"))
        error = header.get("error")
        if isinstance(error, dict):
            error_message = str(error.get("message", ""))
        results = header.get("results", {})
        if isinstance(results, dict):
            completed_samples = int(results.get("completed_samples", completed_samples) or completed_samples)
            total_samples = int(results.get("total_samples", total_samples) or total_samples)
            progress_pct = (completed_samples / total_samples * 100.0) if total_samples else 0.0
            scores = results.get("scores", [])
            if scores:
                metrics = scores[0].get("metrics", {})
                accuracy_value = metrics.get("accuracy", {}).get("value")
                stderr_value = metrics.get("stderr", {}).get("value")
                if accuracy_value is not None:
                    accuracy = str(accuracy_value)
                if stderr_value is not None:
                    stderr = str(stderr_value)

    if isinstance(start, dict) and not header:
        note = "start.json present, run still active or incomplete"
    elif header and status != "success":
        note = "header.json present with non-success status"

    # Some long-running generation jobs can finish writing all sample payloads
    # even if header.json was never finalized. Treat a fully populated archive
    # as complete so downstream status packages reflect the true run state.
    if not header and total_samples and completed_samples >= total_samples:
        status = "success"
        note = "all sample files present; header.json missing"

    return EvalProgress(
        family=family,
        task=task,
        model=model,
        created_at=created_at,
        status=status,
        total_samples=total_samples,
        completed_samples=completed_samples,
        progress_pct=progress_pct,
        artifact_mb=artifact_mb,
        eval_path=str(eval_path),
        note=note,
        accuracy=accuracy,
        stderr=stderr,
        error_message=error_message,
    )


def _scan(log_root: Path) -> list[EvalProgress]:
    eval_paths = sorted(log_root.rglob("*.eval"))
    return [_parse_eval(path, log_root) for path in eval_paths]


def _write_csv(rows: list[EvalProgress], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family",
                "task",
                "model",
                "created_at",
                "status",
                "completed_samples",
                "total_samples",
                "progress_pct",
                "artifact_mb",
                "accuracy",
                "stderr",
                "error_message",
                "note",
                "eval_path",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "family": row.family,
                    "task": row.task,
                    "model": row.model,
                    "created_at": row.created_at,
                    "status": row.status,
                    "completed_samples": row.completed_samples,
                    "total_samples": row.total_samples,
                    "progress_pct": f"{row.progress_pct:.2f}",
                    "artifact_mb": f"{row.artifact_mb:.2f}",
                    "accuracy": row.accuracy,
                    "stderr": row.stderr,
                    "error_message": row.error_message,
                    "note": row.note,
                    "eval_path": row.eval_path,
                }
            )


def _write_markdown(rows: list[EvalProgress], output_path: Path, log_root: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Inspect Eval Progress Summary",
        "",
        f"Generated from `{log_root}`.",
        "",
        "| Family | Task | Status | Samples | Progress | Artifact | Model | Notes |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        samples = f"{row.completed_samples}/{row.total_samples}" if row.total_samples else str(row.completed_samples)
        lines.append(
            "| "
            + " | ".join(
                [
                    row.family,
                    row.task,
                    row.status,
                    samples,
                    f"{row.progress_pct:.1f}%",
                    f"{row.artifact_mb:.2f} MB",
                    row.model or "-",
                    row.error_message or row.note or "-",
                ]
            )
            + " |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize progress of Inspect .eval artifacts.")
    parser.add_argument("--log-root", required=True, type=Path, help="Directory containing Inspect .eval files.")
    parser.add_argument("--csv-out", type=Path, help="Optional CSV output path.")
    parser.add_argument("--md-out", type=Path, help="Optional Markdown output path.")
    args = parser.parse_args()

    rows = _scan(args.log_root)

    if args.csv_out:
        _write_csv(rows, args.csv_out)
    if args.md_out:
        _write_markdown(rows, args.md_out, args.log_root)

    print(
        json.dumps(
            [
                {
                    "family": row.family,
                    "task": row.task,
                    "status": row.status,
                    "completed_samples": row.completed_samples,
                    "total_samples": row.total_samples,
                    "progress_pct": round(row.progress_pct, 2),
                    "artifact_mb": round(row.artifact_mb, 2),
                    "model": row.model,
                    "error_message": row.error_message,
                    "note": row.note,
                }
                for row in rows
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
