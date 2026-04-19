#!/usr/bin/env python3
"""Build curated release tables and SVG figures from the authoritative Option 1 summary."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "results" / "release" / "2026-04-19-option1"
DEFAULT_INPUT = DEFAULT_RELEASE_DIR / "source" / "authoritative-summary.csv"
DEFAULT_FIGURE_DIR = ROOT / "figures" / "release"

MODEL_ORDER = ["Qwen", "DeepSeek", "Gemma"]
BENCHMARK_ORDER = ["UniMoral", "SMID", "Value Kaleidoscope", "CCD-Bench", "Denevil"]
BENCHMARK_TASK_COUNTS = {
    "UniMoral": 1,
    "SMID": 2,
    "Value Kaleidoscope": 2,
    "CCD-Bench": 1,
    "Denevil": 1,
}
ACCURACY_SCOPE_ORDER = [
    ("UniMoral", "Option 1 action prediction", "UniMoral\naction"),
    ("SMID", "Moral rating", "SMID\nrating"),
    ("SMID", "Foundation classification", "SMID\nfoundation"),
    ("Value Kaleidoscope", "Relevance", "Value\nrelevance"),
    ("Value Kaleidoscope", "Valence", "Value\nvalence"),
]
SAMPLE_BAR_ORDER = ["Value Kaleidoscope", "Denevil", "UniMoral", "SMID", "CCD-Bench"]


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            parsed = dict(row)
            parsed["completed_samples"] = int(parsed["completed_samples"])
            parsed["total_samples"] = int(parsed["total_samples"])
            parsed["progress_pct"] = float(parsed["progress_pct"])
            parsed["accuracy"] = float(parsed["accuracy"]) if parsed["accuracy"] else None
            parsed["stderr"] = float(parsed["stderr"]) if parsed["stderr"] else None
            rows.append(parsed)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fmt_float(value: float | None, digits: int = 3) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def build_model_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for model in MODEL_ORDER:
        model_rows = [row for row in rows if row["model_family"] == model]
        scored_rows = [row for row in model_rows if row["benchmark_mode"] == "benchmark_faithful" and row["accuracy"] is not None]
        grouped[model] = {
            "model_family": model,
            "tasks": len(model_rows),
            "faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in model_rows),
            "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in model_rows),
            "samples": sum(row["total_samples"] for row in model_rows),
            "scored_tasks": len(scored_rows),
            "faithful_macro_accuracy": mean(row["accuracy"] for row in scored_rows) if scored_rows else None,
        }
    return [grouped[model] for model in MODEL_ORDER]


def build_benchmark_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for benchmark in BENCHMARK_ORDER:
        bench_rows = [row for row in rows if row["benchmark"] == benchmark]
        output.append(
            {
                "benchmark": benchmark,
                "tasks": len(bench_rows),
                "models_covered": len({row["model_family"] for row in bench_rows}),
                "samples": sum(row["total_samples"] for row in bench_rows),
                "modes": ", ".join(sorted({row["benchmark_mode"] for row in bench_rows})),
            }
        )
    return output


def build_faithful_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    faithful_rows = [row for row in rows if row["benchmark_mode"] == "benchmark_faithful"]
    output: list[dict[str, Any]] = []
    for row in faithful_rows:
        output.append(
            {
                "benchmark": row["benchmark"],
                "benchmark_scope": row["benchmark_scope"],
                "model_family": row["model_family"],
                "task": row["task"],
                "model": row["model"],
                "accuracy": fmt_float(row["accuracy"], 6),
                "stderr": fmt_float(row["stderr"], 6),
                "samples": row["total_samples"],
                "status": row["status"],
            }
        )
    return output


def build_coverage_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for model in MODEL_ORDER:
        model_rows = [row for row in rows if row["model_family"] == model]
        for benchmark in BENCHMARK_ORDER:
            cell_rows = [row for row in model_rows if row["benchmark"] == benchmark]
            if not cell_rows:
                output.append(
                    {
                        "model_family": model,
                        "benchmark": benchmark,
                        "status": "not_run",
                        "completed_tasks": 0,
                        "expected_tasks": BENCHMARK_TASK_COUNTS[benchmark],
                        "label": "-",
                    }
                )
                continue
            mode = cell_rows[0]["benchmark_mode"]
            status = "proxy" if mode == "proxy" else "faithful"
            completed_tasks = len(cell_rows)
            expected = BENCHMARK_TASK_COUNTS[benchmark]
            label = "proxy" if status == "proxy" else f"{completed_tasks}/{expected}"
            output.append(
                {
                    "model_family": model,
                    "benchmark": benchmark,
                    "status": status,
                    "completed_tasks": completed_tasks,
                    "expected_tasks": expected,
                    "label": label,
                }
            )
    return output


def escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)



def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in rgb)



def interpolate_color(start: str, end: str, weight: float) -> str:
    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)
    mixed = tuple(round(s + (e - s) * weight) for s, e in zip(start_rgb, end_rgb))
    return rgb_to_hex(mixed)



def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<defs>",
        "<style>",
        ".title { font: 700 26px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #12263a; }",
        ".subtitle { font: 400 14px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #5c6b7a; }",
        ".axis { font: 600 14px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #22313f; }",
        ".label { font: 500 13px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #22313f; }",
        ".celltext { font: 700 16px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #ffffff; }",
        ".cellsub { font: 500 11px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: rgba(255,255,255,0.88); }",
        ".body { font: 500 12px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #22313f; }",
        ".small { font: 500 11px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #5c6b7a; }",
        ".grid { fill: #ffffff; stroke: #d7dee6; stroke-width: 1.25; }",
        ".panel { fill: #f8fafc; stroke: #e2e8f0; stroke-width: 1.25; }",
        "</style>",
        "</defs>",
    ]


def render_coverage_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1180, 520
    left, top = 210, 120
    cell_w, cell_h = 170, 74
    colors = {"faithful": "#2f855a", "proxy": "#b7791f", "not_run": "#cbd5e1"}

    matrix = {(row["model_family"], row["benchmark"]): row for row in rows}
    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            '<text x="48" y="64" class="title">Option 1 Benchmark Coverage</text>',
            '<text x="48" y="88" class="subtitle">Green cells are benchmark-faithful. Amber cells are explicit proxy evaluations. Gray cells were not part of the closed release.</text>',
        ]
    )

    for index, benchmark in enumerate(BENCHMARK_ORDER):
        x = left + index * cell_w + cell_w / 2
        lines.append(f'<text x="{x}" y="112" text-anchor="middle" class="axis">{escape_xml(benchmark)}</text>')

    for row_index, model in enumerate(MODEL_ORDER):
        y = top + row_index * cell_h + cell_h / 2 + 6
        lines.append(f'<text x="{left - 24}" y="{y}" text-anchor="end" class="axis">{escape_xml(model)}</text>')
        for col_index, benchmark in enumerate(BENCHMARK_ORDER):
            x = left + col_index * cell_w
            y0 = top + row_index * cell_h
            cell = matrix[(model, benchmark)]
            color = colors[cell["status"]]
            lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="{color}"/>')
            label_x = x + (cell_w - 14) / 2
            lines.append(f'<text x="{label_x}" y="{y0 + 34}" text-anchor="middle" class="celltext">{escape_xml(cell["label"])}</text>')
            detail = "benchmark-faithful" if cell["status"] == "faithful" else ("proxy" if cell["status"] == "proxy" else "not in release")
            text_color = "rgba(255,255,255,0.88)" if cell["status"] != "not_run" else "#415466"
            lines.append(
                f'<text x="{label_x}" y="{y0 + 54}" text-anchor="middle" style="font: 500 11px IBM Plex Sans, Helvetica Neue, Arial, sans-serif; fill: {text_color};">{escape_xml(detail)}</text>'
            )

    legend_y = height - 58
    legend_items = [("#2f855a", "benchmark-faithful"), ("#b7791f", "proxy"), ("#cbd5e1", "not in release")]
    for index, (color, label) in enumerate(legend_items):
        x = 48 + index * 210
        lines.append(f'<rect x="{x}" y="{legend_y - 14}" width="18" height="18" rx="4" fill="{color}"/>')
        lines.append(f'<text x="{x + 28}" y="{legend_y}" class="label">{escape_xml(label)}</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def render_accuracy_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1180, 560
    left, top = 210, 132
    cell_w, cell_h = 170, 78
    scored = [row["accuracy"] for row in rows if row["accuracy"] is not None]
    min_acc = min(scored)
    max_acc = max(scored)
    lookup = {(row["model_family"], row["benchmark"], row["benchmark_scope"]): row for row in rows if row["accuracy"] is not None}

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            '<text x="48" y="64" class="title">Option 1 Accuracy Heatmap</text>',
            '<text x="48" y="88" class="subtitle">Only tasks with directly comparable accuracy metrics are shown. Missing cells indicate benchmarks not run in the current closed slice.</text>',
        ]
    )

    for index, (_, _, label) in enumerate(ACCURACY_SCOPE_ORDER):
        x = left + index * cell_w + cell_w / 2
        first, second = label.split("\n")
        lines.append(f'<text x="{x}" y="110" text-anchor="middle" class="axis">{escape_xml(first)}</text>')
        lines.append(f'<text x="{x}" y="128" text-anchor="middle" class="small">{escape_xml(second)}</text>')

    for row_index, model in enumerate(MODEL_ORDER):
        y = top + row_index * cell_h + cell_h / 2 + 6
        lines.append(f'<text x="{left - 24}" y="{y}" text-anchor="end" class="axis">{escape_xml(model)}</text>')
        for col_index, (benchmark, scope, _) in enumerate(ACCURACY_SCOPE_ORDER):
            x = left + col_index * cell_w
            y0 = top + row_index * cell_h
            item = lookup.get((model, benchmark, scope))
            if item is None:
                lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="#dbe4ee"/>')
                lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 40}" text-anchor="middle" class="label">n/a</text>')
                continue
            weight = 0.0 if math.isclose(max_acc, min_acc) else (item["accuracy"] - min_acc) / (max_acc - min_acc)
            color = interpolate_color("#f2e8cf", "#1f6f78", weight)
            lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="{color}"/>')
            lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 36}" text-anchor="middle" class="celltext">{item["accuracy"] * 100:.1f}%</text>')
            lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 58}" text-anchor="middle" class="cellsub">stderr {item["stderr"]:.3f}</text>')

    legend_x = 760
    legend_y = height - 76
    legend_w = 290
    for step in range(100):
        weight = step / 99
        color = interpolate_color("#f2e8cf", "#1f6f78", weight)
        x = legend_x + step * (legend_w / 100)
        lines.append(f'<rect x="{x:.2f}" y="{legend_y}" width="{legend_w / 100 + 0.8:.2f}" height="14" fill="{color}"/>')
    lines.append(f'<text x="{legend_x}" y="{legend_y - 10}" class="small">Lower accuracy</text>')
    lines.append(f'<text x="{legend_x + legend_w}" y="{legend_y - 10}" text-anchor="end" class="small">Higher accuracy</text>')
    lines.append(f'<text x="{legend_x}" y="{legend_y + 34}" class="small">{min_acc * 100:.1f}%</text>')
    lines.append(f'<text x="{legend_x + legend_w}" y="{legend_y + 34}" text-anchor="end" class="small">{max_acc * 100:.1f}%</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def render_sample_volume_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1140, 520
    left, top = 270, 112
    bar_w = 720
    bar_h = 34
    gap = 52

    benchmark_totals: dict[str, dict[str, int]] = {
        benchmark: {"faithful": 0, "proxy": 0} for benchmark in SAMPLE_BAR_ORDER
    }
    for row in rows:
        mode = "proxy" if row["benchmark_mode"] == "proxy" else "faithful"
        benchmark_totals[row["benchmark"]][mode] += row["total_samples"]

    max_total = max(sum(parts.values()) for parts in benchmark_totals.values())
    total_samples = sum(row["total_samples"] for row in rows)

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            '<text x="48" y="64" class="title">Sample Volume by Benchmark</text>',
            f'<text x="48" y="88" class="subtitle">The closed Option 1 release contains {total_samples:,} evaluated samples. Proxy volume is isolated to Denevil.</text>',
        ]
    )

    for index, benchmark in enumerate(SAMPLE_BAR_ORDER):
        y = top + index * gap
        faithful = benchmark_totals[benchmark]["faithful"]
        proxy = benchmark_totals[benchmark]["proxy"]
        total = faithful + proxy
        faithful_w = 0 if max_total == 0 else bar_w * faithful / max_total
        proxy_w = 0 if max_total == 0 else bar_w * proxy / max_total
        lines.append(f'<text x="{left - 18}" y="{y + 22}" text-anchor="end" class="axis">{escape_xml(benchmark)}</text>')
        lines.append(f'<rect x="{left}" y="{y}" width="{bar_w}" height="{bar_h}" rx="12" fill="#e2e8f0"/>')
        if faithful_w:
            lines.append(f'<rect x="{left}" y="{y}" width="{faithful_w:.2f}" height="{bar_h}" rx="12" fill="#2f855a"/>')
        if proxy_w:
            lines.append(f'<rect x="{left + faithful_w:.2f}" y="{y}" width="{proxy_w:.2f}" height="{bar_h}" rx="12" fill="#b7791f"/>')
        lines.append(f'<text x="{left + bar_w + 18}" y="{y + 22}" class="axis">{total:,}</text>')
        if faithful:
            lines.append(f'<text x="{left + 10}" y="{y + 22}" class="cellsub">faithful {faithful:,}</text>')
        if proxy:
            lines.append(f'<text x="{left + faithful_w + 10:.2f}" y="{y + 22}" class="cellsub">proxy {proxy:,}</text>')

    legend_y = height - 66
    lines.append(f'<rect x="48" y="{legend_y - 14}" width="18" height="18" rx="4" fill="#2f855a"/>')
    lines.append(f'<text x="76" y="{legend_y}" class="label">benchmark-faithful samples</text>')
    lines.append(f'<rect x="286" y="{legend_y - 14}" width="18" height="18" rx="4" fill="#b7791f"/>')
    lines.append(f'<text x="314" y="{legend_y}" class="label">proxy samples</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def build_topline_summary(rows: list[dict[str, Any]], model_summary: list[dict[str, Any]]) -> str:
    total_samples = sum(row["total_samples"] for row in rows)
    faithful_tasks = sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows)
    proxy_tasks = sum(row["benchmark_mode"] == "proxy" for row in rows)
    lines = [
        "# 2026-04-19 Option 1 Release Summary",
        "",
        f"- authoritative tasks: `{len(rows)}`",
        f"- benchmark-faithful tasks: `{faithful_tasks}`",
        f"- proxy tasks: `{proxy_tasks}`",
        f"- total evaluated samples: `{total_samples:,}`",
        "- closed model families in this release: `Qwen`, `DeepSeek`, `Gemma`",
        "- key methodological caveat: `Denevil` is represented by a `FULCRA`-backed proxy task rather than a benchmark-faithful `MoralPrompt` run",
        "",
        "## Model Summary",
        "",
        "| Model family | Faithful tasks | Proxy tasks | Samples | Faithful macro accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in model_summary:
        lines.append(
            f"| `{row['model_family']}` | {row['faithful_tasks']} | {row['proxy_tasks']} | {row['samples']:,} | {fmt_float(row['faithful_macro_accuracy']) or 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "Macro accuracy is computed over faithful tasks with a directly comparable accuracy metric. `CCD-Bench` and `Denevil` are excluded from that average.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_release_readme(model_summary: list[dict[str, Any]], benchmark_summary: list[dict[str, Any]]) -> str:
    lines = [
        "# Option 1 Release Artifacts",
        "",
        "This directory contains the tracked, publication-facing outputs for the closed `2026-04-19 Option 1` release.",
        "",
        "## Files",
        "",
        "- `source/authoritative-summary.csv`: tracked source snapshot used to regenerate this release package",
        "- `source/README.md`: provenance note for the tracked source snapshot",
        "- `topline-summary.md`: concise release narrative and topline counts",
        "- `topline-summary.json`: machine-readable counterpart of the topline narrative",
        "- `release-manifest.json`: machine-readable index of release files, counts, and interpretation guardrails",
        "- `model-summary.csv`: per-model task counts, sample counts, and macro accuracy",
        "- `benchmark-summary.csv`: per-benchmark coverage and sample volume",
        "- `faithful-metrics.csv`: task-level metrics for benchmark-faithful tasks",
        "- `coverage-matrix.csv`: matrix used to render the release coverage figure",
        "",
        "## Model Summary",
        "",
        "| Model family | Faithful tasks | Proxy tasks | Samples | Faithful macro accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in model_summary:
        lines.append(
            f"| `{row['model_family']}` | {row['faithful_tasks']} | {row['proxy_tasks']} | {row['samples']:,} | {fmt_float(row['faithful_macro_accuracy']) or 'n/a'} |"
        )
    lines.extend(["", "## Benchmark Summary", "", "| Benchmark | Tasks | Models covered | Samples | Modes |", "| --- | ---: | ---: | ---: | --- |"])
    for row in benchmark_summary:
        lines.append(
            f"| `{row['benchmark']}` | {row['tasks']} | {row['models_covered']} | {row['samples']:,} | {row['modes']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Treat `Denevil` as a proxy line in this release.",
            "- Treat the release outputs here as authoritative for the closed `Option 1` slice.",
            "- Use the raw `results/inspect/` tree only for local debugging or provenance checks.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_source_readme() -> str:
    return "\n".join(
        [
            "# Release Source Snapshot",
            "",
            "The public `Option 1` deliverable is regenerated from `authoritative-summary.csv` in this directory.",
            "",
            "- This CSV is intentionally tracked in git so `make release` does not depend on the large local `results/inspect/` tree.",
            "- Maintainers with the original raw full-run folders can refresh this snapshot with `make refresh-authoritative`.",
            "- The raw `results/inspect/` directories remain useful for local provenance and debugging, but they are not required for public release regeneration.",
        ]
    ) + "\n"


def build_release_manifest(
    rows: list[dict[str, Any]],
    model_summary: list[dict[str, Any]],
    benchmark_summary: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "release_id": "2026-04-19-option1",
        "title": "CEI Moral-Psych Benchmark Suite: Option 1 Release",
        "source_snapshot": "results/release/2026-04-19-option1/source/authoritative-summary.csv",
        "counts": {
            "authoritative_tasks": len(rows),
            "benchmark_faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows),
            "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in rows),
            "total_samples": sum(row["total_samples"] for row in rows),
        },
        "model_families": MODEL_ORDER,
        "benchmarks": benchmark_summary,
        "model_summary": [
            {
                **row,
                "faithful_macro_accuracy": None if row["faithful_macro_accuracy"] is None else round(row["faithful_macro_accuracy"], 6),
            }
            for row in model_summary
        ],
        "tables": [
            "README.md",
            "topline-summary.md",
            "topline-summary.json",
            "release-manifest.json",
            "model-summary.csv",
            "benchmark-summary.csv",
            "faithful-metrics.csv",
            "coverage-matrix.csv",
        ],
        "figures": [
            "figures/release/option1_coverage_matrix.svg",
            "figures/release/option1_accuracy_heatmap.svg",
            "figures/release/option1_sample_volume.svg",
        ],
        "interpretation_guardrails": [
            "Denevil is represented only by the explicit FULCRA-backed proxy task in this release.",
            "DeepSeek has no SMID entries in the closed release slice because no vision route was included.",
            "Raw results/inspect artifacts are local provenance inputs, not required public dependencies for release regeneration.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release tables and figures from the authoritative Option 1 summary.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to authoritative-summary.csv")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output directory for release tables")
    parser.add_argument("--figure-dir", type=Path, default=DEFAULT_FIGURE_DIR, help="Output directory for SVG figures")
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Missing authoritative summary at {args.input}. "
            "Restore the tracked release source snapshot or run `make refresh-authoritative` if local raw full-run tables are available."
        )

    rows = read_rows(args.input)
    args.release_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)

    model_summary = build_model_summary(rows)
    benchmark_summary = build_benchmark_summary(rows)
    faithful_metrics = build_faithful_metrics(rows)
    coverage_matrix = build_coverage_matrix(rows)

    write_csv(
        args.release_dir / "model-summary.csv",
        [
            {
                **row,
                "faithful_macro_accuracy": fmt_float(row["faithful_macro_accuracy"], 6),
            }
            for row in model_summary
        ],
        ["model_family", "tasks", "faithful_tasks", "proxy_tasks", "samples", "scored_tasks", "faithful_macro_accuracy"],
    )
    write_csv(args.release_dir / "benchmark-summary.csv", benchmark_summary, ["benchmark", "tasks", "models_covered", "samples", "modes"])
    write_csv(
        args.release_dir / "faithful-metrics.csv",
        faithful_metrics,
        ["benchmark", "benchmark_scope", "model_family", "task", "model", "accuracy", "stderr", "samples", "status"],
    )
    write_csv(
        args.release_dir / "coverage-matrix.csv",
        coverage_matrix,
        ["model_family", "benchmark", "status", "completed_tasks", "expected_tasks", "label"],
    )

    topline_md = build_topline_summary(rows, model_summary)
    write_text(args.release_dir / "topline-summary.md", topline_md)
    write_text(
        args.release_dir / "README.md",
        build_release_readme(model_summary, benchmark_summary),
    )
    write_text(args.release_dir / "source" / "README.md", build_source_readme())
    write_text(
        args.release_dir / "topline-summary.json",
        json.dumps(
            {
                "authoritative_tasks": len(rows),
                "benchmark_faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows),
                "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in rows),
                "total_samples": sum(row["total_samples"] for row in rows),
                "model_summary": [
                    {
                        **row,
                        "faithful_macro_accuracy": None if row["faithful_macro_accuracy"] is None else round(row["faithful_macro_accuracy"], 6),
                    }
                    for row in model_summary
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        args.release_dir / "release-manifest.json",
        json.dumps(build_release_manifest(rows, model_summary, benchmark_summary), indent=2) + "\n",
    )

    render_coverage_svg(coverage_matrix, args.figure_dir / "option1_coverage_matrix.svg")
    render_accuracy_svg(rows, args.figure_dir / "option1_accuracy_heatmap.svg")
    render_sample_volume_svg(rows, args.figure_dir / "option1_sample_volume.svg")

    print(json.dumps({
        "release_dir": str(args.release_dir),
        "figure_dir": str(args.figure_dir),
        "tables": [
            "model-summary.csv",
            "benchmark-summary.csv",
            "faithful-metrics.csv",
            "coverage-matrix.csv",
            "topline-summary.md",
            "topline-summary.json",
            "release-manifest.json",
            "README.md",
        ],
        "figures": [
            "option1_coverage_matrix.svg",
            "option1_accuracy_heatmap.svg",
            "option1_sample_volume.svg",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
