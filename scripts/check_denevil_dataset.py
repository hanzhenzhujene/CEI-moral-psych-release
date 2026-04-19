#!/usr/bin/env python3
"""Check whether a local Denevil export matches the harness schema expectations."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PROMPT_KEYS = ("prompt", "instruction", "question", "text")


def load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"Expected a top-level list in JSON file: {path}")
        return data
    if suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    raise ValueError(f"Unsupported file type: {path}")


def detect_schema(row: dict[str, Any]) -> tuple[str, str]:
    for key in PROMPT_KEYS:
        if key in row:
            return "moralprompt_compatible", f"Found prompt-like column `{key}`."
    if "dialogue" in row and ("value_items" in row or "value_types" in row):
        return (
            "fulcra_dialogue",
            "Detected FULCRA-style rows with `dialogue` and value annotations, not a MoralPrompt prompt column.",
        )
    return "unknown", "No prompt-like column detected."


def build_report(path: Path, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return (
            f"Denevil dataset check\n"
            f"- file: {path}\n"
            f"- rows: 0\n"
            f"- status: unusable\n"
            f"- note: file is empty\n"
        )

    first_row = rows[0]
    schema, note = detect_schema(first_row)
    status = "ready_for_harness" if schema == "moralprompt_compatible" else "blocked_for_benchmark_faithful_run"
    keys = ", ".join(sorted(first_row))

    next_step = {
        "moralprompt_compatible": "Set DENEVIL_DATA_FILE to this file and launch `denevil_generation` when ready.",
        "fulcra_dialogue": "Do not treat this as the benchmark-ready Denevil dataset. Obtain the MoralPrompt export for `denevil_generation`, or use `denevil_fulcra_proxy_generation` as a clearly non-faithful proxy run.",
        "unknown": "Inspect the schema manually and map a prompt-like column before launching the harness.",
    }[schema]

    return (
        f"Denevil dataset check\n"
        f"- file: {path}\n"
        f"- rows: {len(rows)}\n"
        f"- status: {status}\n"
        f"- detected_schema: {schema}\n"
        f"- keys: {keys}\n"
        f"- note: {note}\n"
        f"- next_step: {next_step}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate whether a local Denevil file matches the MoralPrompt-style schema expected by the harness.")
    parser.add_argument("data_file", help="Path to a candidate CSV, JSON, or JSONL file.")
    parser.add_argument("--report-out", help="Optional path for saving the text report.")
    args = parser.parse_args()

    path = Path(args.data_file).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    rows = load_rows(path)
    report = build_report(path, rows)
    print(report, end="")

    if args.report_out:
        out_path = Path(args.report_out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
