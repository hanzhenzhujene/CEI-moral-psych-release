"""Regression checks for the tracked Option 1 release build."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "build_release_artifacts.py"
SOURCE = ROOT / "results" / "release" / "2026-04-19-option1" / "source" / "authoritative-summary.csv"


def test_release_builder_emits_expected_files(tmp_path):
    release_dir = tmp_path / "release"
    figure_dir = tmp_path / "figures"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(SOURCE),
            "--release-dir",
            str(release_dir),
            "--figure-dir",
            str(figure_dir),
        ],
        check=True,
        cwd=ROOT,
    )

    expected_release_files = {
        "README.md",
        "benchmark-catalog.csv",
        "benchmark-comparison.csv",
        "benchmark-summary.csv",
        "coverage-matrix.csv",
        "family-size-progress.csv",
        "faithful-metrics.csv",
        "future-model-plan.csv",
        "jenny-group-report.md",
        "model-summary.csv",
        "model-roster.csv",
        "release-manifest.json",
        "supplementary-model-progress.csv",
        "topline-summary.json",
        "topline-summary.md",
        "source/README.md",
    }
    actual_release_files = {
        str(path.relative_to(release_dir))
        for path in release_dir.rglob("*")
        if path.is_file()
    }
    assert expected_release_files.issubset(actual_release_files)

    expected_figures = {
        "option1_accuracy_heatmap.svg",
        "option1_benchmark_accuracy_bars.svg",
        "option1_coverage_matrix.svg",
        "option1_sample_volume.svg",
    }
    actual_figures = {path.name for path in figure_dir.glob("*.svg")}
    assert expected_figures == actual_figures

    manifest = json.loads((release_dir / "release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["authoritative_tasks"] == 19
    assert manifest["counts"]["proxy_tasks"] == 3
    assert any("Denevil" in item for item in manifest["interpretation_guardrails"])
    assert manifest["report_metadata"]["owner"] == "Jenny Zhu"
    assert manifest["report_metadata"]["current_cost"] == "$35"
    assert manifest["target_matrix"]["family_size_benchmark_cells"] == 75
    assert manifest["entry_points"]["report"].endswith("jenny-group-report.md")
    assert manifest["entry_points"]["supplementary_progress"].endswith("supplementary-model-progress.csv")
    assert manifest["entry_points"]["family_size_progress"].endswith("family-size-progress.csv")

    with (release_dir / "supplementary-model-progress.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "completed_benchmark_lines" in reader.fieldnames
        assert "missing_benchmark_lines" in reader.fieldnames
        rows = list(reader)
    assert any(
        row["family"] == "MiniMax"
        and row["status_relative_to_closed_release"] == "Attempted locally, but current results are not usable"
        for row in rows
    )

    with (release_dir / "family-size-progress.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert len(rows) == 15
    assert any(
        row["line_label"] == "Gemma-L"
        and row["smid"] == "done"
        and row["value_kaleidoscope"] == "done"
        and row["ccd_bench"] == "done"
        and row["denevil"] == "live"
        for row in rows
    )
    assert any(row["line_label"] == "Gemma-M" and row["smid"] == "done" for row in rows)
    assert any(row["line_label"] == "Llama-L" and row["smid"] == "done" for row in rows)
    assert any(row["line_label"] == "Qwen-L" and row["smid"] == "error" for row in rows)

    report_text = (release_dir / "jenny-group-report.md").read_text(encoding="utf-8")
    assert "qwen2.5-vl-72b-instruct" in report_text
    assert "non-Alibaba provider allowlist" in report_text
    assert "## Figure Gallery" in report_text
    assert "![Coverage matrix]" in report_text
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | --- |" in report_text

    release_readme = (release_dir / "README.md").read_text(encoding="utf-8")
    assert "sample volume chart" in release_readme
    assert "## Figure Gallery" in release_readme
    assert "Done" in release_readme

    heatmap_svg = (figure_dir / "option1_accuracy_heatmap.svg").read_text(encoding="utf-8")
    assert "celltext-dark" in heatmap_svg
    assert "Accuracy scale" in heatmap_svg

    sample_volume_svg = (figure_dir / "option1_sample_volume.svg").read_text(encoding="utf-8")
    assert "Paper setup:" in sample_volume_svg
    assert "Proxy:" in sample_volume_svg
