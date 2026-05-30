"""Sample model outputs from Inspect AI logs for human spot-check review.

For each model×task cell, randomly samples N outputs and formats them as a
markdown file for manual plausibility review (response is coherent, not
garbled/truncated/off-topic).

Usage:
    python scripts/spot_check_sampler.py [--log-dir DIR] [--samples N] [--output-dir DIR]
    python scripts/spot_check_sampler.py --log-dir results/inspect/logs --samples 10
"""

from __future__ import annotations

import argparse
import json
import random
import zipfile
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample Inspect AI outputs for spot-check review")
    parser.add_argument(
        "--log-dir",
        default="results/inspect/logs",
        help="Root directory containing .eval archives (searched recursively)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=10,
        help="Number of samples per cell (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        default="results/spot_checks",
        help="Directory for output markdown files",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    return parser.parse_args()


def extract_eval_metadata(zf: zipfile.ZipFile) -> dict | None:
    """Read header.json and return eval metadata."""
    try:
        header = json.loads(zf.read("header.json").decode("utf-8"))
    except (KeyError, json.JSONDecodeError):
        return None

    eval_info = header.get("eval", {})
    return {
        "task": eval_info.get("task", "unknown"),
        "model": eval_info.get("model", "unknown"),
        "status": header.get("status", "unknown"),
        "dataset_samples": eval_info.get("dataset", {}).get("samples", 0),
    }


def extract_samples(zf: zipfile.ZipFile) -> list[dict]:
    """Extract sample data from .eval archive."""
    samples = []
    for name in zf.namelist():
        if not (name.startswith("samples/") and name.endswith(".json")):
            continue
        try:
            sample = json.loads(zf.read(name).decode("utf-8"))
            samples.append(sample)
        except (json.JSONDecodeError, KeyError):
            continue
    return samples


def format_sample_for_review(sample: dict, idx: int) -> str:
    """Format a single sample as markdown for human review."""
    lines = [f"### Sample {idx}"]
    lines.append(f"**ID:** `{sample.get('id', 'unknown')}`")

    # Input (truncated)
    input_text = ""
    if isinstance(sample.get("input"), str):
        input_text = sample["input"]
    elif isinstance(sample.get("input"), list):
        for msg in sample["input"]:
            if isinstance(msg, dict) and msg.get("role") == "user":
                input_text = msg.get("content", "")
                break
    if len(input_text) > 500:
        input_text = input_text[:500] + "..."
    lines.append(f"\n**Input:**\n```\n{input_text}\n```")

    # Output completion
    output = sample.get("output", {})
    completion = ""
    if isinstance(output, dict):
        completion = output.get("completion", "")
    elif isinstance(output, str):
        completion = output

    if not completion:
        lines.append("\n**Output:** *(empty)*")
    else:
        # Truncate very long outputs
        display = completion if len(completion) <= 2000 else completion[:2000] + "\n\n... (truncated)"
        lines.append(f"\n**Output:**\n```\n{display}\n```")

    # Score
    scores = sample.get("scores", {})
    if scores:
        score_parts = []
        for scorer_name, score_data in scores.items():
            if isinstance(score_data, dict):
                val = score_data.get("value", "N/A")
                expl = score_data.get("explanation", "")
                score_parts.append(f"{scorer_name}: {val}")
                if expl:
                    score_parts.append(f"  explanation: {expl[:200]}")
        lines.append(f"\n**Scores:**\n```\n" + "\n".join(score_parts) + "\n```")

    # Review checklist
    lines.append("\n**Review:** [ ] Coherent  [ ] On-topic  [ ] Not truncated  [ ] Plausible score")
    lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args()
    random.seed(args.seed)

    log_dir = Path(args.log_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not log_dir.exists():
        print(f"Log directory not found: {log_dir}")
        return

    # Find all .eval files
    eval_files = sorted(log_dir.rglob("*.eval"))
    if not eval_files:
        print(f"No .eval files found in {log_dir}")
        return

    print(f"Found {len(eval_files)} .eval files")

    # Group by model×task
    cells: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for eval_path in eval_files:
        try:
            with zipfile.ZipFile(eval_path) as zf:
                meta = extract_eval_metadata(zf)
                if meta and meta["status"] == "success":
                    key = f"{meta['model']}__{meta['task']}"
                    cells[key].append((eval_path, meta))
        except (zipfile.BadZipFile, OSError):
            continue

    print(f"Found {len(cells)} unique model×task cells with successful runs")

    # For each cell, sample from the most recent run
    total_files = 0
    for cell_key in sorted(cells.keys()):
        runs = cells[cell_key]
        # Use the most recent file (last by sort order = most recent timestamp)
        eval_path, meta = runs[-1]

        try:
            with zipfile.ZipFile(eval_path) as zf:
                all_samples = extract_samples(zf)
        except (zipfile.BadZipFile, OSError):
            continue

        if not all_samples:
            continue

        # Random sample
        n = min(args.samples, len(all_samples))
        selected = random.sample(all_samples, n)

        # Generate markdown
        model_name = meta["model"].replace("/", "_")
        task_name = meta["task"]
        filename = f"{model_name}__{task_name}.md"

        try:
            source_display = eval_path.resolve().relative_to(Path.cwd())
        except ValueError:
            source_display = eval_path

        lines = [
            f"# Spot-Check: {meta['model']} / {task_name}",
            f"\n**Source:** `{source_display}`",
            f"**Total samples:** {len(all_samples)}",
            f"**Reviewed:** {n}",
            f"**Reviewer:** _______________",
            f"**Date:** _______________",
            "",
            "---",
            "",
        ]

        for i, sample in enumerate(selected, 1):
            lines.append(format_sample_for_review(sample, i))
            lines.append("---\n")

        lines.append("## Summary")
        lines.append("- [ ] All samples are coherent and on-topic")
        lines.append("- [ ] No systematic truncation or garbled output")
        lines.append("- [ ] Scores are plausible given the responses")
        lines.append(f"- **Issues found:** _______________")
        lines.append(f"- **Recommendation:** [ ] T3 valid  [ ] Needs investigation")

        out_path = output_dir / filename
        out_path.write_text("\n".join(lines), encoding="utf-8")
        total_files += 1

    print(f"\nGenerated {total_files} spot-check files in {output_dir}/")
    print("Each file contains randomly sampled outputs for manual review.")


if __name__ == "__main__":
    main()
