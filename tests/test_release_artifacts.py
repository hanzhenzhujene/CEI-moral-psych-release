"""Regression checks for the tracked Option 1 release build."""

from __future__ import annotations

import csv
import json
import re
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
        "benchmark-difficulty-summary.csv",
        "benchmark-summary.csv",
        "coverage-matrix.csv",
        "family-scaling-summary.csv",
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
        "option1_benchmark_difficulty_profile.svg",
        "option1_coverage_matrix.svg",
        "option1_family_scaling_profile.svg",
        "option1_sample_volume.svg",
    }
    actual_figures = {path.name for path in figure_dir.glob("*.svg")}
    assert expected_figures == actual_figures

    manifest = json.loads((release_dir / "release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["authoritative_tasks"] == 19
    assert manifest["counts"]["proxy_tasks"] == 3
    assert any("Denevil" in item for item in manifest["interpretation_guardrails"])
    assert manifest["report_metadata"]["owner"] == "Jenny Zhu"
    assert manifest["report_metadata"]["current_cost_estimate"] == "$84.02"
    assert "later tracked reruns completed in this repo" in manifest["report_metadata"]["current_cost_scope"]
    assert manifest["report_metadata"]["ci_workflow_url"].endswith("/actions/workflows/ci.yml")
    assert manifest["target_matrix"]["family_size_benchmark_cells"] == 60
    assert manifest["target_matrix"]["model_families"] == 4
    assert manifest["model_families"] == ["Qwen", "DeepSeek", "Llama", "Gemma"]
    assert manifest["entry_points"]["report"].endswith("jenny-group-report.md")
    assert manifest["entry_points"]["supplementary_progress"].endswith("supplementary-model-progress.csv")
    assert manifest["entry_points"]["family_size_progress"].endswith("family-size-progress.csv")
    assert manifest["entry_points"]["benchmark_difficulty_summary"].endswith("benchmark-difficulty-summary.csv")
    assert manifest["entry_points"]["family_scaling_summary"].endswith("family-scaling-summary.csv")
    assert manifest["entry_points"]["benchmark_difficulty_figure"].endswith("option1_benchmark_difficulty_profile.svg")
    assert manifest["entry_points"]["family_scaling_figure"].endswith("option1_family_scaling_profile.svg")
    assert "benchmark-difficulty-summary.csv" in manifest["tables"]
    assert "family-scaling-summary.csv" in manifest["tables"]
    assert "figures/release/option1_benchmark_difficulty_profile.svg" in manifest["figures"]
    assert "figures/release/option1_family_scaling_profile.svg" in manifest["figures"]

    with (release_dir / "benchmark-catalog.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "paper_focus" in reader.fieldnames
        assert "repo_readout" in reader.fieldnames
        assert "release_interpretation" in reader.fieldnames
        benchmark_catalog_rows = list(reader)
    value_kaleidoscope = next(row for row in benchmark_catalog_rows if row["benchmark"] == "Value Kaleidoscope")
    assert value_kaleidoscope["paper_url"] == "https://arxiv.org/abs/2309.00779"
    assert "pluralism" in value_kaleidoscope["paper_focus"].lower()
    denevil = next(row for row in benchmark_catalog_rows if row["benchmark"] == "Denevil")
    assert denevil["paper_url"] == "https://arxiv.org/abs/2310.11053"
    assert "proxy line is a coverage and provenance signal" in denevil["release_interpretation"].lower()
    ccd_bench = next(row for row in benchmark_catalog_rows if row["benchmark"] == "CCD-Bench")
    assert ccd_bench["paper_title"] == "CCD-Bench: Probing Cultural Conflict in Large Language Model Decision-Making"

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
    assert llama_large["smid"] == "done"
    assert llama_large["unimoral"] in {"done", "queue"}
    assert llama_large["value_kaleidoscope"] in {"live", "partial", "done", "queue"}
    assert llama_large["ccd_bench"] in {"done", "partial", "queue"}
    assert llama_large["denevil"] in {"partial", "live", "queue", "proxy"}
    assert llama_large["summary_note"] in {
        "SMID complete; best saved Value Prism Relevance checkpoint still stands at 99.3%, and the current text rerun is active again.",
        "SMID complete; best saved Value Prism Relevance checkpoint still stands at 100.0%, and the current text rerun is active again.",
        "SMID complete; current text rerun active.",
        "SMID complete; local text rerun is now fully persisted through the Denevil proxy task (100.0%).",
        "SMID complete; text rerun is paused because OpenRouter credits are exhausted after a 99.3% Value Prism Relevance checkpoint.",
        "SMID done; text is still queued.",
    }
    deepseek_medium = row_for("DeepSeek-M")
    assert deepseek_medium["unimoral"] in {"done", "partial", "queue"}
    assert deepseek_medium["smid"] == "-"
    assert deepseek_medium["value_kaleidoscope"] in {"done", "live", "partial", "queue"}
    assert deepseek_medium["ccd_bench"] in {"done", "queue", "partial", "live"}
    assert deepseek_medium["denevil"] in {"queue", "partial", "live", "proxy"}
    allowed_deepseek_notes = {
        "No vision route; downstream attempt is currently stalled after partial text checkpoints.",
        "No vision route; queued behind the live Llama-M rerun.",
        "No vision route; downstream attempt is currently blocked because OpenRouter credits are exhausted.",
        "No vision route; downstream text run is active, but the current provider path is intermittently hitting NextBit upstream rate limits and provider errors.",
        "No vision route; launched after the Llama-M completion. The first UniMoral attempt was interrupted.",
        "Downstream text run is active again on the relaunched DeepInfra-backed distill route; detailed checkpoints are summarized in Snapshot.",
        "No vision route; downstream text run is active again on the relaunched DeepInfra-backed distill route.",
    }
    dynamic_deepseek_note_patterns = [
        r"Downstream text run is active again on the relaunched DeepInfra-backed distill route; the current Denevil proxy archive has already reached \d+\.\d%\.",
        r"No vision route; downstream text run is active again on the relaunched DeepInfra-backed distill route, and Denevil proxy has already reached \d+\.\d% persisted coverage\.",
        r"No SMID route; local text rerun finished successfully through the Denevil proxy task \(\d+\.\d%\)\.",
    ]
    assert deepseek_medium["summary_note"] in allowed_deepseek_notes or any(
        re.fullmatch(pattern, deepseek_medium["summary_note"])
        for pattern in dynamic_deepseek_note_patterns
    )

    with (release_dir / "benchmark-comparison.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert len(rows) == 10
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
        and row["unimoral_action_accuracy"] == "0.659836"
        and row["value_average_accuracy"] == "0.692319"
        for row in rows
    )
    assert any(
        row["line_label"] == "Qwen-M"
        and row["unimoral_action_accuracy"] == "0.664504"
        and row["smid_average_accuracy"] == ""
        and row["value_average_accuracy"] == "0.674714"
        for row in rows
    )
    assert any(
        row["line_label"] == "Qwen-L"
        and row["unimoral_action_accuracy"] == "0.665301"
        and row["smid_average_accuracy"] == "0.482829"
        and row["value_average_accuracy"] == "0.653159"
        for row in rows
    )
    assert any(
        row["line_label"] == "Llama-M"
        and row["unimoral_action_accuracy"] == "0.669854"
        and row["smid_average_accuracy"] == ""
        and row["value_average_accuracy"] == "0.723638"
        for row in rows
    )
    assert not any(row["line_label"] == "DeepSeek-M" for row in rows)

    with (release_dir / "benchmark-difficulty-summary.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        difficulty_rows = list(reader)
    assert [row["benchmark"] for row in difficulty_rows] == ["UniMoral", "SMID", "Value Kaleidoscope"]
    assert any(
        row["benchmark"] == "SMID"
        and row["mean_accuracy"] == "0.378030"
        and row["spread"] == "0.266406"
        and row["best_line"] == "Qwen-L"
        and row["weakest_line"] == "Llama-S"
        for row in difficulty_rows
    )
    assert any(
        row["benchmark"] == "Value Kaleidoscope"
        and row["mean_accuracy"] == "0.650180"
        and row["best_line"] == "Llama-M"
        and row["weakest_line"] == "Llama-S"
        for row in difficulty_rows
    )

    with (release_dir / "family-scaling-summary.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        scaling_rows = list(reader)
    assert [row["family"] for row in scaling_rows] == ["Qwen", "DeepSeek", "Llama", "Gemma"]
    assert any(
        row["family"] == "Qwen"
        and "Text benchmarks now have S/M/L comparable points" in row["evidence_scope"]
        and "UniMoral: S 0.647 -> M 0.665 -> L 0.665" in row["numeric_pattern"]
        and "SMID: S 0.368 -> L 0.483" in row["numeric_pattern"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "Llama"
        and "Text benchmarks now have S/M/L comparable points" in row["evidence_scope"]
        and "Value Kaleidoscope: S 0.529 -> M 0.724 -> L 0.692" in row["numeric_pattern"]
        and "medium text line still beats the large line" in row["interpretation"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "Gemma"
        and "Full S/M/L comparable sweep" in row["evidence_scope"]
        and "SMID: S 0.417 -> M 0.364 -> L 0.412" in row["numeric_pattern"]
        and "non-monotonic" in row["interpretation"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "DeepSeek"
        and "Only the large line remains accuracy-comparable" in row["evidence_scope"]
        and "cannot support a trustworthy accuracy size curve" in row["interpretation"]
        for row in scaling_rows
    )

    report_text = (release_dir / "jenny-group-report.md").read_text(encoding="utf-8")
    assert "## Results First" in report_text
    assert "## Interpretation" in report_text
    assert "### Interpretation At A Glance" in report_text
    assert "### Benchmark Reading Guide" in report_text
    assert "### Benchmark Difficulty Profile" in report_text
    assert "### Family Scaling Profile" in report_text
    assert "### Reporting Guardrails" in report_text
    assert "These benchmarks do not all ask for the same kind of moral competence" in report_text
    assert "### Latest Family-Size Progress Snapshot" in report_text
    assert "Strongest fully observed comparable line | `Qwen-L` averages 0.600" in report_text
    assert "Strongest text-only comparable line | `Llama-M` reaches UniMoral 0.670 and Value 0.724" in report_text
    assert "Keep `DeepSeek-M` out of the top-row comparable accuracy charts" in report_text
    assert "qwen2.5-vl-72b-instruct" in report_text
    assert "## Local Expansion Checkpoint" in report_text
    assert "| `Next queued text lines` | Done | No currently published line remains queued behind an active rerun. |" in report_text
    assert "curated snapshot rather than a live dashboard" in report_text
    assert "## Status Key" in report_text
    assert "## Supporting Figures" in report_text
    assert "option1_family_size_progress_overview.svg" in report_text
    assert "option1_benchmark_difficulty_profile.svg" in report_text
    assert "option1_family_scaling_profile.svg" in report_text
    assert "Partial" in report_text
    assert "Model families in scope" in report_text
    assert "## Safe One-Sentence Framing" in report_text
    assert "## Interpretation Notes" not in report_text
    assert "Current project cost estimate" in report_text
    assert "Cost scope" in report_text
    assert "Current cost to date" not in report_text
    assert "24634450927" not in report_text
    assert "`MiniMax`" not in report_text
    assert "| `MiniMax-S` |" not in report_text
    assert "| `MiniMax-M` |" not in report_text
    assert "| `MiniMax-L` |" not in report_text
    assert "![Coverage matrix]" in report_text
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | --- |" in report_text

    release_readme = (release_dir / "README.md").read_text(encoding="utf-8")
    assert "## Results First" in release_readme
    assert "## Interpretation" in release_readme
    assert "### Interpretation At A Glance" in release_readme
    assert "### Benchmark Reading Guide" in release_readme
    assert "### Benchmark Difficulty Profile" in release_readme
    assert "### Family Scaling Profile" in release_readme
    assert "### Reporting Guardrails" in release_readme
    assert "These benchmarks do not all ask for the same kind of moral competence" in release_readme
    assert "### Latest Family-Size Progress Snapshot" in release_readme
    assert "## Local Expansion Checkpoint" in release_readme
    assert "| `Next queued text lines` | Done | No currently published line remains queued behind an active rerun. |" in release_readme
    assert "sample volume chart" in release_readme
    assert "benchmark difficulty profile" in release_readme
    assert "family scaling profile" in release_readme
    assert "## Start Here" in release_readme
    assert "## Status Key" in release_readme
    assert "## Supporting Figures" in release_readme
    assert "option1_family_size_progress_overview.svg" in release_readme
    assert "option1_benchmark_difficulty_profile.svg" in release_readme
    assert "option1_family_scaling_profile.svg" in release_readme
    assert "Partial" in release_readme
    assert "Model families in scope" in release_readme
    assert "## Interpretation Notes" not in release_readme
    assert "Current project cost estimate" in release_readme
    assert "Cost scope" in release_readme
    assert "Current cost to date" not in release_readme
    assert "24634450927" not in release_readme
    assert "`MiniMax`" not in release_readme
    assert "| `MiniMax-S` |" not in release_readme
    assert "| `MiniMax-M` |" not in release_readme
    assert "| `MiniMax-L` |" not in release_readme
    assert "Done" in release_readme
    assert "Keep `DeepSeek-M` out of the top-row comparable accuracy charts" in release_readme

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

    benchmark_difficulty_svg = (figure_dir / "option1_benchmark_difficulty_profile.svg").read_text(encoding="utf-8")
    assert "Benchmark Difficulty And Spread" in benchmark_difficulty_svg
    assert "Hardest current comparable benchmark" in benchmark_difficulty_svg
    assert "Widest cross-line spread" in benchmark_difficulty_svg

    family_scaling_svg = (figure_dir / "option1_family_scaling_profile.svg").read_text(encoding="utf-8")
    assert "Family Scaling Profile" in family_scaling_svg
    assert 'preserveAspectRatio="xMidYMin meet"' in family_scaling_svg
    assert 'style="max-width:100%;height:auto"' in family_scaling_svg
    assert "Five benchmark panels: three scored accuracy panels plus two coverage-only benchmark panels." in family_scaling_svg
    assert "Top row: scored benchmarks only (`UniMoral`, `SMID`, `Value Kaleidoscope`)." in family_scaling_svg
    assert "Bottom row: CCD-Bench and Denevil coverage panels" in family_scaling_svg
    assert "CCD-Bench" in family_scaling_svg
    assert "Denevil" in family_scaling_svg
    assert "DeepSeek-M stays out of the top-row accuracy panels because" in family_scaling_svg
    assert (
        "its saved short-answer rerun is not trustworthy yet." in family_scaling_svg
        or "its saved short-answer rerun still shows 100.0% empty visible answers." in family_scaling_svg
    )
    assert "appears in the lower completion panels but not as a scored point in the upper accuracy panels." in family_scaling_svg
    assert "Takeaway: current evidence supports task-specific scaling statements" in family_scaling_svg
    assert "Qwen: Top-row text has S/M/L; SMID has S/L." in family_scaling_svg
    assert "Llama: Top-row text has S/M/L; SMID has S/L." in family_scaling_svg
    assert "DeepSeek: Top-row only L is scored; M is completion-only; S has no route." in family_scaling_svg
    assert "Only the small line is currently comparable." not in family_scaling_svg

    sample_volume_svg = (figure_dir / "option1_sample_volume.svg").read_text(encoding="utf-8")
    assert "Paper setup:" in sample_volume_svg
    assert "Proxy:" in sample_volume_svg
    assert "% of release" in sample_volume_svg
