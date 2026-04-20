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
        "benchmark-summary.csv",
        "coverage-matrix.csv",
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
    assert manifest["entry_points"]["report"].endswith("jenny-group-report.md")
    assert manifest["entry_points"]["supplementary_progress"].endswith("supplementary-model-progress.csv")

    with (release_dir / "supplementary-model-progress.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "completed_benchmark_lines" in reader.fieldnames
        assert "missing_benchmark_lines" in reader.fieldnames
