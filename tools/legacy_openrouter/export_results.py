"""Export TrolleyBench results to clean, shareable formats.

Generates:
  - results/<run>/export/summary.csv          — one row per model, key metrics
  - results/<run>/export/all_responses.csv     — one row per scenario×model, with actions + frameworks
  - results/<run>/export/conversations.md      — full conversations, human-readable
  - results/<run>/eval_report.md               — evaluation report (from tools/legacy_openrouter/eval_trolleybench.py)

Usage:
    python tools/legacy_openrouter/export_results.py --results-dir results/trolleybench/20260421_072446
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from eval_trolleybench import extract_action, extract_framework


def export_summary_csv(results_dir: Path, export_dir: Path):
    """Export one-row-per-model summary CSV."""
    eval_summary = results_dir / "eval_summary.json"
    if not eval_summary.exists():
        print("  Skipping summary.csv — run tools/legacy_openrouter/eval_trolleybench.py first")
        return

    data = json.loads(eval_summary.read_text())
    rows = []
    for label, r in sorted(data.items()):
        rows.append({
            "model": label,
            "eci": r.get("eci", {}).get("eci"),
            "entropy_inconsistency": r.get("entropy_inconsistency", {}).get("mean_inconsistency"),
            "followup_reversal_rate": r.get("followup_impact", {}).get("reversal_rate"),
            "num_scenarios": r.get("num_scenarios"),
            "dominant_framework": max(r.get("framework_distribution", {}),
                                      key=r["framework_distribution"].get)
                                  if r.get("framework_distribution") else None,
        })

    out = export_dir / "summary.csv"
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {out} ({len(rows)} models)")


def export_all_responses_csv(results_dir: Path, export_dir: Path):
    """Export one-row-per-scenario-per-model with extracted actions and frameworks."""
    result_files = sorted(results_dir.glob("*_T*.json"))
    rows = []

    for f in result_files:
        if f.name in ("meta.json", "eval_summary.json"):
            continue
        label = f.stem
        data = json.loads(f.read_text())

        for scenario in data:
            row = {
                "model": label,
                "scenario_id": scenario["id"],
                "variant": scenario.get("variant", ""),
                "moral_dimension": scenario.get("metadata", {}).get("moral_dimension", ""),
                "mechanism": scenario.get("metadata", {}).get("mechanism", ""),
            }

            for i, resp in enumerate(scenario.get("responses", [])):
                turn = i + 1
                if "error" in resp:
                    row[f"t{turn}_action"] = "ERROR"
                    row[f"t{turn}_framework"] = "ERROR"
                    row[f"t{turn}_response_length"] = 0
                else:
                    text = resp.get("assistant", "")
                    row[f"t{turn}_action"] = extract_action(text) or "ambiguous"
                    row[f"t{turn}_framework"] = extract_framework(text)
                    row[f"t{turn}_response_length"] = len(text)

            rows.append(row)

    if not rows:
        print("  No results to export")
        return

    out = export_dir / "all_responses.csv"
    fieldnames = list(rows[0].keys())
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {out} ({len(rows)} rows)")


def export_conversations_md(results_dir: Path, export_dir: Path):
    """Export full conversations as readable markdown."""
    result_files = sorted(results_dir.glob("*_T*.json"))
    lines = ["# TrolleyBench — Full Conversations\n"]

    for f in result_files:
        if f.name in ("meta.json", "eval_summary.json"):
            continue
        label = f.stem
        data = json.loads(f.read_text())
        lines.append(f"\n---\n\n## {label}\n")

        for scenario in data:
            sid = scenario["id"]
            variant = scenario.get("variant", "")
            action_summary = []

            lines.append(f"\n### {sid} ({variant})\n")

            for resp in scenario.get("responses", []):
                turn = resp.get("turn", "?")
                user_msg = resp.get("user", "")
                lines.append(f"**Turn {turn} — User:**\n> {user_msg}\n")

                if "error" in resp:
                    lines.append(f"**Turn {turn} — Assistant:** ERROR: {resp['error']}\n")
                    action_summary.append("ERROR")
                else:
                    assistant_msg = resp.get("assistant", "")
                    action = extract_action(assistant_msg) or "ambiguous"
                    framework = extract_framework(assistant_msg)
                    action_summary.append(action)

                    # Truncate very long responses for readability
                    display = assistant_msg if len(assistant_msg) <= 2000 else assistant_msg[:2000] + "\n\n*[truncated]*"
                    lines.append(f"**Turn {turn} — Assistant** `[{action} | {framework}]`:\n{display}\n")

            lines.append(f"\n**Summary:** {' → '.join(action_summary)}\n")

    out = export_dir / "conversations.md"
    out.write_text("\n".join(lines))
    print(f"  {out} ({len(result_files)} models)")


def main():
    parser = argparse.ArgumentParser(description="Export TrolleyBench results")
    parser.add_argument("--results-dir", "-r", required=True, help="Path to results directory")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Results directory not found: {results_dir}")
        return

    export_dir = results_dir / "export"
    export_dir.mkdir(exist_ok=True)

    print(f"Exporting results from {results_dir}:\n")
    export_summary_csv(results_dir, export_dir)
    export_all_responses_csv(results_dir, export_dir)
    export_conversations_md(results_dir, export_dir)
    print(f"\nAll exports in {export_dir}/")


if __name__ == "__main__":
    main()
