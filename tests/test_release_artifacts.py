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
        "option1_family_size_progress_overview.svg",
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
    assert manifest["report_metadata"]["current_cost"] == "$40.73"
    assert manifest["target_matrix"]["family_size_benchmark_cells"] == 60
    assert manifest["target_matrix"]["model_families"] == 4
    assert manifest["model_families"] == ["Qwen", "DeepSeek", "Llama", "Gemma"]
    assert manifest["entry_points"]["report"].endswith("jenny-group-report.md")
    assert manifest["entry_points"]["supplementary_progress"].endswith("supplementary-model-progress.csv")
    assert manifest["entry_points"]["family_size_progress"].endswith("family-size-progress.csv")

    with (release_dir / "supplementary-model-progress.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "completed_benchmark_lines" in reader.fieldnames
        assert "missing_benchmark_lines" in reader.fieldnames
        rows = list(reader)
    assert not any(row["family"] == "MiniMax" for row in rows)

    with (release_dir / "family-size-progress.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    def row_for(line_label: str) -> dict[str, str]:
        return next(row for row in rows if row["line_label"] == line_label)

    def assert_partial_text_progress(row: dict[str, str], *, smid_status: str, summary_note: str) -> None:
        assert row["unimoral"] == "done"
        assert row["smid"] == smid_status
        assert row["value_kaleidoscope"] == "done"
        assert row["ccd_bench"] == "done"
        assert row["denevil"] == "partial"
        assert row["summary_note"] == summary_note

    def assert_live_text_progress(row: dict[str, str], *, smid_status: str) -> None:
        assert row["unimoral"] == "done"
        assert row["smid"] == smid_status
        assert row["value_kaleidoscope"] in {"live", "done"}
        assert row["ccd_bench"] in {"queue", "live", "done"}
        assert row["denevil"] in {"queue", "live", "proxy"}
        if row["denevil"] in {"live", "proxy"}:
            assert row["value_kaleidoscope"] == "done"
            assert row["ccd_bench"] == "done"
        elif row["ccd_bench"] in {"live", "done"}:
            assert row["value_kaleidoscope"] == "done"

    def assert_live_downstream_progress(
        row: dict[str, str], *, smid_status: str, summary_note: str
    ) -> None:
        assert row["unimoral"] == "done"
        assert row["smid"] == smid_status
        assert row["value_kaleidoscope"] == "done"
        assert row["ccd_bench"] in {"partial", "live", "done"}
        assert row["denevil"] in {"queue", "live", "proxy"}
        if row["denevil"] in {"live", "proxy"}:
            assert row["ccd_bench"] == "done"
        assert row["summary_note"] == summary_note

    def assert_done_text_progress(row: dict[str, str], *, smid_status: str, summary_note: str) -> None:
        assert row["unimoral"] == "done"
        assert row["smid"] == smid_status
        assert row["value_kaleidoscope"] == "done"
        assert row["ccd_bench"] == "done"
        assert row["denevil"] == "proxy"
        assert row["summary_note"] == summary_note

    assert len(rows) == 12
    assert not any(row["line_label"].startswith("MiniMax-") for row in rows)
    assert any(
        row["line_label"] == "Gemma-L"
        and row["smid"] == "done"
        and row["value_kaleidoscope"] == "done"
        and row["ccd_bench"] == "done"
        and row["denevil"] == "proxy"
        for row in rows
    )
    assert any(
        row["line_label"] == "Gemma-M"
        and row["unimoral"] == "done"
        and row["smid"] == "done"
        and row["value_kaleidoscope"] == "done"
        and row["ccd_bench"] == "done"
        and row["denevil"] == "proxy"
        for row in rows
    )
    assert any(row["line_label"] == "Llama-L" and row["smid"] == "done" for row in rows)
    qwen_large = row_for("Qwen-L")
    if qwen_large["denevil"] == "proxy":
        assert_done_text_progress(
            qwen_large,
            smid_status="done",
            summary_note="SMID recovery complete; clean text rerun finished locally.",
        )
    elif qwen_large["value_kaleidoscope"] == "live":
        assert_live_text_progress(qwen_large, smid_status="done")
        assert qwen_large["summary_note"] == "SMID recovery complete; clean text rerun active."
    elif qwen_large["ccd_bench"] in {"partial", "live"} or qwen_large["denevil"] in {"queue", "live"}:
        assert_live_downstream_progress(
            qwen_large,
            smid_status="done",
            summary_note="SMID recovery complete; clean text rerun active.",
        )
    else:
        assert_partial_text_progress(
            qwen_large,
            smid_status="done",
            summary_note="SMID recovery complete; clean text rerun reached Denevil, then stopped on OpenRouter monthly key-limit 403.",
        )
    qwen_medium = row_for("Qwen-M")
    if qwen_medium["denevil"] == "proxy":
        assert_done_text_progress(
            qwen_medium,
            smid_status="tbd",
            summary_note="Clean text rerun finished locally after the withdrawn short-answer artifacts.",
        )
    elif qwen_medium["denevil"] == "partial":
        assert_partial_text_progress(
            qwen_medium,
            smid_status="tbd",
            summary_note="Clean text rerun reached Denevil, then stopped on OpenRouter monthly key-limit 403.",
        )
    else:
        assert_live_text_progress(qwen_medium, smid_status="tbd")
        assert qwen_medium["summary_note"] == "Clean text rerun active after withdrawn short-answer artifacts."
    llama_medium = row_for("Llama-M")
    if llama_medium["denevil"] == "proxy":
        assert_done_text_progress(
            llama_medium,
            smid_status="-",
            summary_note="No SMID route; medium text line completed locally on April 22, 2026.",
        )
    else:
        assert_live_text_progress(llama_medium, smid_status="-")
    llama_large = row_for("Llama-L")
    assert llama_large["unimoral"] == "done"
    assert llama_large["smid"] == "done"
    assert llama_large["value_kaleidoscope"] in {"live", "partial", "done"}
    assert llama_large["ccd_bench"] in {"done", "partial", "queue"}
    assert llama_large["denevil"] in {"partial", "live", "queue", "proxy"}
    assert "SMID complete" in llama_large["summary_note"]
    deepseek_medium = row_for("DeepSeek-M")
    assert deepseek_medium["unimoral"] in {"partial", "queue"}
    assert deepseek_medium["smid"] == "-"
    assert deepseek_medium["value_kaleidoscope"] in {"partial", "queue"}
    assert deepseek_medium["ccd_bench"] in {"queue", "partial"}
    assert deepseek_medium["denevil"] in {"queue", "partial"}
    assert deepseek_medium["summary_note"] in {
        "No vision route; downstream attempt is currently stalled after partial text checkpoints.",
        "No vision route; queued behind the live Llama-M rerun.",
        "No vision route; downstream attempt is currently blocked because OpenRouter credits are exhausted.",
    }

    with (release_dir / "benchmark-comparison.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert len(rows) == 7
    assert not any(row["line_label"].startswith("MiniMax-") for row in rows)
    assert any(
        row["line_label"] == "Gemma-L"
        and row["unimoral_action_accuracy"] == "0.661088"
        and row["smid_average_accuracy"] == "0.412275"
        and row["value_average_accuracy"] == "0.655987"
        for row in rows
    )
    assert any(
        row["line_label"] == "Llama-L"
        and row["smid_average_accuracy"] == "0.386093"
        and row["unimoral_action_accuracy"] == ""
        for row in rows
    )
    assert not any(row["line_label"] in {"Qwen-M", "Qwen-L"} for row in rows)

    report_text = (release_dir / "jenny-group-report.md").read_text(encoding="utf-8")
    assert "## Results First" in report_text
    assert "### Latest Family-Size Progress Snapshot" in report_text
    assert "qwen2.5-vl-72b-instruct" in report_text
    assert "## Local Expansion Checkpoint" in report_text
    assert "curated snapshot rather than a live dashboard" in report_text
    assert "## Status Key" in report_text
    assert "## Supporting Figures" in report_text
    assert "option1_family_size_progress_overview.svg" in report_text
    assert "Partial" in report_text
    assert "Model families in scope" in report_text
    assert "`MiniMax`" not in report_text
    assert "| `MiniMax-S` |" not in report_text
    assert "| `MiniMax-M` |" not in report_text
    assert "| `MiniMax-L` |" not in report_text
    assert "![Coverage matrix]" in report_text
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | --- |" in report_text

    release_readme = (release_dir / "README.md").read_text(encoding="utf-8")
    assert "## Results First" in release_readme
    assert "### Latest Family-Size Progress Snapshot" in release_readme
    assert "## Local Expansion Checkpoint" in release_readme
    assert "sample volume chart" in release_readme
    assert "## Start Here" in release_readme
    assert "## Status Key" in release_readme
    assert "## Supporting Figures" in release_readme
    assert "option1_family_size_progress_overview.svg" in release_readme
    assert "Partial" in release_readme
    assert "Model families in scope" in release_readme
    assert "`MiniMax`" not in release_readme
    assert "| `MiniMax-S` |" not in release_readme
    assert "| `MiniMax-M` |" not in release_readme
    assert "| `MiniMax-L` |" not in release_readme
    assert "Done" in release_readme

    progress_overview_svg = (figure_dir / "option1_family_size_progress_overview.svg").read_text(encoding="utf-8")
    assert "Family-Size Progress Overview" in progress_overview_svg
    assert "usable now" in progress_overview_svg
    assert "Pending / TBD / not planned" in progress_overview_svg
    assert "four-family matrix" in progress_overview_svg
    assert "MiniMax-S" not in progress_overview_svg

    heatmap_svg = (figure_dir / "option1_accuracy_heatmap.svg").read_text(encoding="utf-8")
    assert "Current Comparable Accuracy Heatmap" in heatmap_svg
    assert "Accuracy scale" in heatmap_svg
    assert "no current result" in heatmap_svg
    assert "withdrawn from direct comparison" in heatmap_svg
    assert "MiniMax-S" not in heatmap_svg

    benchmark_bar_svg = (figure_dir / "option1_benchmark_accuracy_bars.svg").read_text(encoding="utf-8")
    assert "no current result for this benchmark" in benchmark_bar_svg
    assert "Gemma-L" in benchmark_bar_svg
    assert "withdrawn from direct comparison" in benchmark_bar_svg

    sample_volume_svg = (figure_dir / "option1_sample_volume.svg").read_text(encoding="utf-8")
    assert "Paper setup:" in sample_volume_svg
    assert "Proxy:" in sample_volume_svg
    assert "% of release" in sample_volume_svg
