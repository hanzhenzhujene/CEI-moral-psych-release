"""Regression checks for the tracked Option 1 release build."""

from __future__ import annotations

import csv
import json
import shutil
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_release_artifacts import (
    _sample_correctness_value,
    build_axis_ticks,
    nice_tick_step,
    preserve_repo_readme_org_tail,
)
from scripts.build_unimoral_artifacts import update_markdown

SCRIPT = ROOT / "scripts" / "build_release_artifacts.py"
SOURCE = ROOT / "results" / "release" / "2026-04-19-option1" / "source" / "authoritative-summary.csv"


def markdown_h2_section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end == -1 else text[start:end]


def test_axis_tick_helpers_stay_nonzero_for_minimal_clean_state():
    assert nice_tick_step(1, target_ticks=4) == 1
    ticks, upper = build_axis_ticks(1, target_ticks=4)
    assert ticks == [0, 1, 2, 3, 4]
    assert upper == 1


def test_unimoral_blank_scorer_answer_reparsed_from_visible_completion():
    sample = {
        "target": "a",
        "output": {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"internal": "think", "type": "reasoning", "reasoning": "hidden trace"},
                            {"type": "text", "text": "Selected action is a."},
                        ]
                    }
                }
            ],
            "completion": "Selected action is a.",
        },
        "score_value": 0,
        "score_answer": "",
    }

    assert _sample_correctness_value(sample, "unimoral_action_prediction") == 1.0


def test_root_readme_regeneration_preserves_org_owned_tail_sections():
    generated = "# CEI Moral-Psych Benchmark Suite\n\n<!-- UNIMORAL_FULL_BENCHMARK_END -->\n"
    existing = (
        "# CEI Moral-Psych Benchmark Suite\n\n"
        "<!-- UNIMORAL_FULL_BENCHMARK_END -->\n\n"
        "## Claude Code Slash Commands\n\n"
        "| Command | What it does |\n"
        "| --- | --- |\n"
        "| `/validate-results` | Validate results. |\n\n"
        "## Contributing\n\n"
        "All changes go through pull requests.\n\n"
        "## Team\n\n"
        "| Person | Papers |\n"
    )

    result = preserve_repo_readme_org_tail(generated, existing)

    assert result.startswith(generated.rstrip())
    assert "## Claude Code Slash Commands" in result
    assert "| `/validate-results` | Validate results. |" in result
    assert "## Contributing" in result
    assert "## Team" in result


def test_unimoral_readme_block_stays_before_org_owned_tail_sections(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "# CEI Moral-Psych Benchmark Suite\n\n"
        "Generated Jenny result surface.\n\n"
        "## Claude Code Slash Commands\n\n"
        "| `/validate-results` | Validate results. |\n\n"
        "## Team\n\n"
        "| Person | Papers |\n",
        encoding="utf-8",
    )

    update_markdown(
        readme,
        "## UniMoral Full Benchmark Coverage\n\nUpdated benchmark section.\n",
        insert_before_headings=("## Claude Code Slash Commands", "## Team"),
    )

    content = readme.read_text(encoding="utf-8")
    assert content.index("<!-- UNIMORAL_FULL_BENCHMARK_START -->") < content.index("## Claude Code Slash Commands")
    assert "| `/validate-results` | Validate results. |" in content
    assert "## Team" in content


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
        "paper-result-alignment.csv",
        "benchmark-comparison.csv",
        "smid-results.csv",
        "value-kaleidoscope-results.csv",
        "ccd-choice-distribution.csv",
        "denevil-behavior-summary.csv",
        "denevil-prompt-family-breakdown.csv",
        "denevil-proxy-summary.csv",
        "denevil-proxy-examples.csv",
        "deepseek-sm-readout.csv",
        "readiness-tier-matrix.csv",
        "saved-results-audit.csv",
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
        "option1_paper_model_calibration_bridge.svg",
        "option1_accuracy_heatmap.svg",
        "option1_benchmark_accuracy_bars.svg",
        "option1_benchmark_difficulty_profile.svg",
        "option1_coverage_matrix.svg",
        "option1_family_scaling_profile.svg",
        "option1_ccd_valid_choice_coverage.svg",
        "option1_ccd_choice_distribution.svg",
        "option1_ccd_dominant_option_share.svg",
        "option1_denevil_behavior_outcomes.svg",
        "option1_denevil_prompt_family_heatmap.svg",
        "option1_denevil_proxy_status_matrix.svg",
        "option1_denevil_proxy_sample_volume.svg",
        "option1_denevil_proxy_valid_response_rate.svg",
        "option1_denevil_proxy_pipeline.svg",
        "option1_paper_result_alignment_map.svg",
        "option1_sample_volume.svg",
    }
    actual_figures = {path.name for path in figure_dir.glob("*.svg")}
    assert expected_figures == actual_figures
    for figure_name in expected_figures:
        assert (figure_dir / figure_name).stat().st_size > 0

    manifest = json.loads((release_dir / "release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["authoritative_tasks"] == 19
    assert manifest["counts"]["proxy_tasks"] == 3
    assert manifest["counts"]["paper_result_alignment_rows"] == 5
    assert any("Denevil" in item for item in manifest["interpretation_guardrails"])
    assert any("DeepSeek-S" in item and "May 9 no-thinking" in item for item in manifest["interpretation_guardrails"])
    assert any("OpenAI reference rows" in item and "text-only markers" in item for item in manifest["interpretation_guardrails"])
    assert manifest["report_metadata"]["owner"] == "Jenny Zhu"
    assert manifest["report_metadata"]["current_total_cost"] == "$888.06"
    assert manifest["report_metadata"]["current_cost_breakdown"] == {
        "minimax_api": "$504.66",
        "openrouter_other_model_family_runs": "$343.42",
        "openai_api_reference_sweep": "$39.98",
    }
    assert (
        manifest["report_metadata"]["current_cost_scope"]
        == "User-confirmed total spend including the OpenRouter selected-grid follow-up and OpenAI reference-sweep additions."
    )
    assert manifest["report_metadata"]["metric_definition_version"] == "2026-04-30"
    assert "stricter visible-answer parsing" in manifest["report_metadata"]["metric_definition_summary"].lower()
    assert manifest["report_metadata"]["ci_workflow_url"].endswith("/actions/workflows/ci.yml")
    assert manifest["target_matrix"]["family_size_benchmark_cells"] == 75
    assert manifest["target_matrix"]["readiness_summary_cells"] == 105
    assert manifest["target_matrix"]["tier3_summary_cells"] == 72
    assert manifest["target_matrix"]["blocked_summary_cells"] == 18
    assert manifest["target_matrix"]["model_families"] == 5
    assert manifest["model_families"] == ["Qwen", "MiniMax", "DeepSeek", "Llama", "Gemma"]
    assert manifest["entry_points"]["report"].endswith("jenny-group-report.md")
    assert manifest["entry_points"]["paper_result_alignment"].endswith("paper-result-alignment.csv")
    assert manifest["entry_points"]["paper_result_alignment_figure"].endswith("option1_paper_result_alignment_map.svg")
    assert manifest["entry_points"]["supplementary_progress"].endswith("supplementary-model-progress.csv")
    assert manifest["entry_points"]["family_size_progress"].endswith("family-size-progress.csv")
    assert manifest["entry_points"]["benchmark_difficulty_summary"].endswith("benchmark-difficulty-summary.csv")
    assert manifest["entry_points"]["family_scaling_summary"].endswith("family-scaling-summary.csv")
    assert manifest["entry_points"]["ccd_choice_distribution"].endswith("ccd-choice-distribution.csv")
    assert manifest["entry_points"]["denevil_proxy_summary"].endswith("denevil-proxy-summary.csv")
    assert manifest["entry_points"]["denevil_behavior_summary"].endswith("denevil-behavior-summary.csv")
    assert manifest["entry_points"]["denevil_prompt_family_breakdown"].endswith(
        "denevil-prompt-family-breakdown.csv"
    )
    assert manifest["entry_points"]["denevil_proxy_examples"].endswith("denevil-proxy-examples.csv")
    assert manifest["entry_points"]["deepseek_sm_readout"].endswith("deepseek-sm-readout.csv")
    assert manifest["entry_points"]["readiness_tier_matrix"].endswith("readiness-tier-matrix.csv")
    assert manifest["entry_points"]["paper_model_calibration_bridge_figure"].endswith("option1_paper_model_calibration_bridge.svg")
    assert manifest["entry_points"]["benchmark_difficulty_figure"].endswith("option1_benchmark_difficulty_profile.svg")
    assert manifest["entry_points"]["family_scaling_figure"].endswith("option1_family_scaling_profile.svg")
    assert manifest["entry_points"]["ccd_valid_choice_coverage_figure"].endswith("option1_ccd_valid_choice_coverage.svg")
    assert manifest["entry_points"]["ccd_choice_distribution_figure"].endswith("option1_ccd_choice_distribution.svg")
    assert manifest["entry_points"]["ccd_dominant_option_share_figure"].endswith("option1_ccd_dominant_option_share.svg")
    assert manifest["entry_points"]["denevil_behavior_figure"].endswith("option1_denevil_behavior_outcomes.svg")
    assert manifest["entry_points"]["denevil_prompt_family_figure"].endswith(
        "option1_denevil_prompt_family_heatmap.svg"
    )
    assert manifest["entry_points"]["denevil_proxy_status_figure"].endswith("option1_denevil_proxy_status_matrix.svg")
    assert manifest["entry_points"]["denevil_proxy_sample_volume_figure"].endswith("option1_denevil_proxy_sample_volume.svg")
    assert manifest["entry_points"]["denevil_proxy_valid_response_rate_figure"].endswith("option1_denevil_proxy_valid_response_rate.svg")
    assert manifest["entry_points"]["denevil_proxy_pipeline_figure"].endswith("option1_denevil_proxy_pipeline.svg")
    assert "benchmark-difficulty-summary.csv" in manifest["tables"]
    assert "paper-result-alignment.csv" in manifest["tables"]
    assert "smid-results.csv" in manifest["tables"]
    assert "value-kaleidoscope-results.csv" in manifest["tables"]
    assert "family-scaling-summary.csv" in manifest["tables"]
    assert "ccd-choice-distribution.csv" in manifest["tables"]
    assert "denevil-proxy-summary.csv" in manifest["tables"]
    assert "denevil-behavior-summary.csv" in manifest["tables"]
    assert "denevil-prompt-family-breakdown.csv" in manifest["tables"]
    assert "denevil-proxy-examples.csv" in manifest["tables"]
    assert "readiness-tier-matrix.csv" in manifest["tables"]
    assert "figures/release/option1_paper_model_calibration_bridge.svg" in manifest["figures"]
    assert "figures/release/option1_benchmark_difficulty_profile.svg" in manifest["figures"]
    assert "figures/release/option1_family_scaling_profile.svg" in manifest["figures"]
    assert "figures/release/option1_ccd_valid_choice_coverage.svg" in manifest["figures"]
    assert "figures/release/option1_ccd_choice_distribution.svg" in manifest["figures"]
    assert "figures/release/option1_ccd_dominant_option_share.svg" in manifest["figures"]
    assert "figures/release/option1_denevil_behavior_outcomes.svg" in manifest["figures"]
    assert "figures/release/option1_denevil_prompt_family_heatmap.svg" in manifest["figures"]
    assert "figures/release/option1_denevil_proxy_status_matrix.svg" in manifest["figures"]
    assert "figures/release/option1_denevil_proxy_sample_volume.svg" in manifest["figures"]
    assert "figures/release/option1_denevil_proxy_valid_response_rate.svg" in manifest["figures"]
    assert "figures/release/option1_denevil_proxy_pipeline.svg" in manifest["figures"]

    for report_name in ("README.md", "jenny-group-report.md"):
        report_text = (release_dir / report_name).read_text(encoding="utf-8")
        assert report_text.index("## Benchmark Result Visuals") < report_text.index("## TL;DR")
        tldr_text = markdown_h2_section(report_text, "## TL;DR")
        assert "**Current GitHub-facing boundary:**" not in tldr_text
        assert "**Bottom line:**" in tldr_text
        assert "image moral judgment is the bottleneck" in tldr_text
        assert "**DeNEVIL is proxy behavioral evidence" not in tldr_text
        assert "`MiniMax-M`" in report_text
        assert (
            "Clean direct MiniMax-M2.5 text run is complete" in report_text
            and "no medium SMID route fixed yet" in report_text
        )
    release_readme_text = (release_dir / "README.md").read_text(encoding="utf-8")
    assert "## DATA, CLICK HERE: Main Result Files" in release_readme_text
    assert "I found `CCD-Bench` in this repo; I did not find a separate `CCG-Bench` result surface." in release_readme_text
    assert "results/release/2026-04-19-option1/unimoral-full-benchmark.csv" in release_readme_text
    assert "results/release/2026-04-19-option1/smid-results.csv" in release_readme_text
    assert "results/release/2026-04-19-option1/value-kaleidoscope-results.csv" in release_readme_text
    assert "sample-level BERTScore audit" in release_readme_text
    assert "SMID results" in release_readme_text
    assert "Value Kaleidoscope results" in release_readme_text
    assert "results/release/2026-04-19-option1/ccd-choice-distribution.csv" in release_readme_text
    assert "option1_paper_result_alignment_map.svg" in release_readme_text
    topline_text = (release_dir / "topline-summary.md").read_text(encoding="utf-8")
    assert "## TL;DR" in topline_text
    assert "`GPT-5.5`" in topline_text
    assert "**Bottom line:**" in topline_text
    assert "**DeNEVIL is proxy behavioral evidence" not in topline_text
    assert "**Current GitHub-facing boundary:**" not in topline_text.split("## Frozen Snapshot Scope", 1)[0]

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
    assert "proxy-only behavioral evidence and traceability support" in denevil["release_interpretation"].lower()
    ccd_bench = next(row for row in benchmark_catalog_rows if row["benchmark"] == "CCD-Bench")
    assert ccd_bench["paper_title"] == "CCD-Bench: Probing Cultural Conflict in Large Language Model Decision-Making"
    assert "canonical cluster heatmap" in ccd_bench["release_interpretation"].lower()

    with (release_dir / "paper-result-alignment.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "comparison_status" in reader.fieldnames
        assert "can_compare_directly" in reader.fieldnames
        paper_alignment_rows = list(reader)
    assert len(paper_alignment_rows) == 5
    ccd_alignment = next(row for row in paper_alignment_rows if row["benchmark"] == "CCD-Bench")
    assert ccd_alignment["comparison_status"] == "distributional_comparison_available_not_accuracy"
    assert "not the metric surface" in ccd_alignment["can_compare_directly"]
    denevil_alignment = next(row for row in paper_alignment_rows if row["benchmark"] == "DeNEVIL / MoralPrompt")
    assert denevil_alignment["comparison_status"] == "proxy_only_data_gap"
    assert "proxy-only" in denevil_alignment["reviewer_takeaway"]
    value_alignment = next(row for row in paper_alignment_rows if row["benchmark"] == "Value Kaleidoscope / ValuePrism")
    assert "Kaleido model replication" in value_alignment["classification_quality_readout"]

    with (release_dir / "supplementary-model-progress.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "completed_benchmark_lines" in reader.fieldnames
        assert "missing_benchmark_lines" in reader.fieldnames
        rows = list(reader)
    minimax_family = next(row for row in rows if row["family"] == "MiniMax")
    assert minimax_family["completed_benchmark_lines"] in {
        "None yet",
            "UniMoral; SMID",
            "UniMoral; SMID; CCD-Bench",
            "UniMoral; SMID; CCD-Bench; Denevil proxy",
            "UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy",
        }
    if minimax_family["completed_benchmark_lines"] == "None yet":
        assert minimax_family["tasks_completed"] == "0"
        assert minimax_family["samples"] == "0"
    else:
        assert int(minimax_family["tasks_completed"]) >= 3
        assert int(minimax_family["samples"]) >= 14666

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

    assert len(rows) == 15
    minimax_small = row_for("MiniMax-S")
    assert_done_text_progress(
        minimax_small,
        smid_status="done",
        summary_note="Direct MiniMax-M2.1 text rerun complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; SMID uses the completed MiniMax-01 recovery route.",
    )
    minimax_medium = row_for("MiniMax-M")
    assert minimax_medium["unimoral"] in {"live", "done"}
    assert minimax_medium["smid"] == "tbd"
    assert minimax_medium["value_kaleidoscope"] in {"live", "done"}
    assert minimax_medium["ccd_bench"] == "done"
    assert minimax_medium["denevil"] in {"live", "proxy"}
    assert minimax_medium["summary_note"].startswith(
        (
            "Clean direct MiniMax-M2.5 text run is active; no medium SMID route fixed yet.",
            "Clean direct MiniMax-M2.5 text run is complete across UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and the Denevil proxy; no medium SMID route fixed yet.",
        )
    )
    minimax_large = row_for("MiniMax-L")
    assert minimax_large["unimoral"] in {"queue", "done"}
    assert minimax_large["smid"] in {"queue", "done"}
    assert minimax_large["value_kaleidoscope"] in {"queue", "partial", "live", "done"}
    assert minimax_large["ccd_bench"] in {"queue", "live", "partial", "done"}
    assert minimax_large["denevil"] in {"queue", "partial", "live", "proxy"}
    assert minimax_large["summary_note"] in {
        "Shared MiniMax-01 SMID recovery and the MiniMax-M2.5 text rerun are refreshed from the current direct-provider run folders at build time.",
        "Shared MiniMax-01 SMID recovery is complete; MiniMax-L is currently running CCD-Bench.",
        "Shared MiniMax-01 SMID recovery is complete; MiniMax-L is currently running CCD-Bench, and a concurrent Denevil proxy pass is also in flight.",
        "Shared MiniMax-01 SMID recovery is complete; CCD-Bench is done, and the MiniMax-M2.5 text reruns are now active on Denevil proxy.",
        "Shared MiniMax-01 SMID recovery is complete; CCD-Bench is done, the MiniMax-M2.5 text reruns are now active on Denevil proxy, and Value Kaleidoscope remains queued on this pass.",
        "Shared MiniMax-01 SMID recovery is complete; the MiniMax-M2.5 text rerun is active.",
        "Shared MiniMax-01 SMID recovery complete; the MiniMax-M2.5 text rerun is now fully persisted through the Denevil proxy task (100.0%).",
        "Shared MiniMax-01 SMID recovery is complete; text later stalled after a 100.0% Value Prism Relevance checkpoint. Later text tasks remain incomplete.",
        "Shared MiniMax-01 SMID recovery is complete; UniMoral is already persisted while the later text tasks are not currently active.",
    }
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
    deepseek_small = row_for("DeepSeek-S")
    assert deepseek_small["unimoral"] == "done"
    assert deepseek_small["smid"] == "-"
    assert deepseek_small["value_kaleidoscope"] == "done"
    assert deepseek_small["ccd_bench"] == "done"
    assert deepseek_small["denevil"] == "proxy"
    assert deepseek_small["summary_note"] in {
        "No SMID route; May 9 no-thinking text rerun is complete and visible-answer validated.",
        "No SMID route; May 9 no-thinking text rerun is complete and passes visible-answer validation for UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy.",
    }
    deepseek_medium = row_for("DeepSeek-M")
    assert_done_text_progress(
        deepseek_medium,
        smid_status="-",
        summary_note="Frozen medium text line; no SMID route was included. UniMoral 0.684, Value 0.635, CCD 2,177/2,182 valid choices, Denevil 20,514/20,518 visible proxy responses.",
    )
    deepseek_large = row_for("DeepSeek-L")
    assert_done_text_progress(
        deepseek_large,
        smid_status="-",
        summary_note="No SMID route; large R1 text rerun is complete from saved shards with UniMoral action prediction, Value Kaleidoscope, CCD-Bench, and Denevil proxy parsed.",
    )

    with (release_dir / "benchmark-comparison.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert reader.fieldnames == [
            "line_label",
            "family",
            "size_slot",
            "route",
            "unimoral_action_accuracy",
            "smid_average_accuracy",
            "value_average_accuracy",
            "comparison_note",
        ]
        rows = list(reader)
    assert len(rows) == 21
    minimax_large_rows = [row for row in rows if row["line_label"] == "MiniMax-L"]
    if minimax_large_rows:
        assert any(
            row["route"] == "text: minimax-m2.5 via direct MiniMax API; SMID recovery: minimax-01 via direct MiniMax API"
            and row["unimoral_action_accuracy"] == "0.660519"
            and row["smid_average_accuracy"] == "0.198232"
            and row["comparison_note"] == "Comparable on all three benchmark-faithful accuracy panels."
            for row in minimax_large_rows
        )
    rows_by_line = {row["line_label"]: row for row in rows}
    expected_openai_refs = {
        "GPT-4o-mini Ref": ("OpenAI Ref", "Ref", "0.672700", "0.700698", "GPT-4o-mini Ref text-only OpenAI reference; outside the GPT-5 S/M/L series."),
        "GPT-5 nano": ("OpenAI GPT-5", "S", "0.653575", "0.617193", "GPT-5 nano text-only OpenAI GPT-5 S slot; no SMID or DeNEVIL route."),
        "GPT-4.1-nano Ref": ("OpenAI Ref", "Ref", "0.646289", "0.673043", "GPT-4.1-nano Ref text-only OpenAI reference; outside the GPT-5 S/M/L series."),
        "GPT-5 mini": ("OpenAI GPT-5", "M", "0.677937", "0.738897", "GPT-5 mini text-only OpenAI GPT-5 M slot; no SMID or DeNEVIL route."),
        "GPT-5.5": ("OpenAI GPT-5", "L", "0.683629", "0.735646", "GPT-5.5 text-only OpenAI GPT-5 L slot; no SMID or DeNEVIL route."),
        "GPT-4.1-mini Ref": ("OpenAI Ref", "Ref", "0.679417", "0.734890", "GPT-4.1-mini Ref text-only OpenAI reference; outside the GPT-5 S/M/L series."),
    }
    for line_label, (family, size_slot, unimoral_accuracy, value_accuracy, comparison_note) in expected_openai_refs.items():
        openai_reference = rows_by_line[line_label]
        assert openai_reference["family"] == family
        assert openai_reference["size_slot"] == size_slot
        assert openai_reference["unimoral_action_accuracy"] == unimoral_accuracy
        assert openai_reference["smid_average_accuracy"] == ""
        assert openai_reference["value_average_accuracy"] == value_accuracy
        assert openai_reference["comparison_note"] == comparison_note
    assert rows_by_line["MiniMax-S"]["unimoral_action_accuracy"] == "0.660861"
    assert rows_by_line["MiniMax-S"]["smid_average_accuracy"] == "0.431996"
    assert rows_by_line["MiniMax-S"]["value_average_accuracy"] == "0.739942"
    assert rows_by_line["MiniMax-S"]["comparison_note"] == "Comparable on all three benchmark-faithful accuracy panels."
    if rows_by_line["MiniMax-M"]["unimoral_action_accuracy"]:
        assert rows_by_line["MiniMax-M"]["unimoral_action_accuracy"] == "0.658698"
        assert rows_by_line["MiniMax-M"]["smid_average_accuracy"] == ""
        assert rows_by_line["MiniMax-M"]["value_average_accuracy"] == "0.739778"
        assert rows_by_line["MiniMax-M"]["comparison_note"] == "Text-only comparable line; no public SMID route on this slot."
    else:
        assert rows_by_line["MiniMax-M"]["unimoral_action_accuracy"] == ""
        assert rows_by_line["MiniMax-M"]["smid_average_accuracy"] == ""
        assert rows_by_line["MiniMax-M"]["value_average_accuracy"] == ""
        assert rows_by_line["MiniMax-M"]["comparison_note"] == "Coverage-only live line; accuracy withheld until the clean M2.5 text pass completes and a medium SMID route is fixed."
    assert any(
        row["line_label"] == "Gemma-L"
        and row["unimoral_action_accuracy"] == "0.661088"
        and row["smid_average_accuracy"] != ""
        and row["value_average_accuracy"] == "0.655987"
        and row["comparison_note"] == "Comparable on all three benchmark-faithful accuracy panels."
        for row in rows
    )
    assert any(
        row["line_label"] == "Llama-L"
        and row["smid_average_accuracy"] != ""
        and row["unimoral_action_accuracy"] == "0.659836"
        and row["value_average_accuracy"] == "0.692319"
        and row["comparison_note"] == "Comparable on all three benchmark-faithful accuracy panels."
        for row in rows
    )
    assert any(
        row["line_label"] == "Qwen-M"
        and row["unimoral_action_accuracy"] == "0.664504"
        and row["smid_average_accuracy"] == ""
        and row["value_average_accuracy"] == "0.674714"
        and row["comparison_note"] == "Text-only comparable line; no public SMID route on this slot."
        for row in rows
    )
    assert any(
        row["line_label"] == "Qwen-L"
        and row["unimoral_action_accuracy"] == "0.665301"
        and row["smid_average_accuracy"] != ""
        and row["value_average_accuracy"] == "0.653159"
        and row["comparison_note"] == "Comparable on all three benchmark-faithful accuracy panels."
        for row in rows
    )
    assert any(
        row["line_label"] == "Llama-M"
        and row["unimoral_action_accuracy"] == "0.669854"
        and row["smid_average_accuracy"] == ""
        and row["value_average_accuracy"] == "0.723638"
        and row["comparison_note"] == "Text-only comparable line; no public SMID route on this slot."
        for row in rows
    )
    deepseek_small = rows_by_line.get("DeepSeek-S")
    if deepseek_small is not None:
        assert deepseek_small["unimoral_action_accuracy"] == "0.660594"
        assert deepseek_small["smid_average_accuracy"] == ""
        assert deepseek_small["value_average_accuracy"] == "0.695198"
        assert (
            deepseek_small["comparison_note"]
            == "Text-only comparable no-thinking rerun; no public SMID route on this slot."
        )
    deepseek_medium = rows_by_line.get("DeepSeek-M")
    if deepseek_medium is not None:
        assert deepseek_medium["unimoral_action_accuracy"] == "0.683629"
        assert deepseek_medium["smid_average_accuracy"] == ""
        assert deepseek_medium["value_average_accuracy"] == "0.634673"
        assert (
            deepseek_medium["comparison_note"]
            == "Text-only comparable line; no public SMID route on this slot."
        )
    deepseek_large = rows_by_line.get("DeepSeek-L")
    if deepseek_large is not None:
        assert deepseek_large["unimoral_action_accuracy"] == "0.562550"
        assert deepseek_large["smid_average_accuracy"] == ""
        assert deepseek_large["value_average_accuracy"] == "0.680658"
        assert (
            deepseek_large["comparison_note"]
            == "Text-only comparable line; no public SMID route on this slot."
        )

    with (release_dir / "deepseek-sm-readout.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert reader.fieldnames == [
            "line_label",
            "family",
            "size_slot",
            "route",
            "unimoral_action_accuracy",
            "unimoral_visible_answers",
            "unimoral_total_samples",
            "value_relevance_accuracy",
            "value_valence_accuracy",
            "value_average_accuracy",
            "value_visible_answers",
            "value_total_samples",
            "ccd_valid_choice_count",
            "ccd_total_samples",
            "ccd_valid_choice_rate",
            "denevil_visible_response_count",
            "denevil_total_samples",
            "denevil_visible_response_rate",
            "answer_validation",
            "public_interpretation",
        ]
        deepseek_readout = {row["line_label"]: row for row in reader}
    assert deepseek_readout["DeepSeek-S"]["answer_validation"] == "passed_visible_answer_guardrail"
    assert deepseek_readout["DeepSeek-S"]["unimoral_action_accuracy"] == "0.660594"
    assert deepseek_readout["DeepSeek-S"]["unimoral_visible_answers"] == "8783"
    assert deepseek_readout["DeepSeek-S"]["value_visible_answers"] == "65481"
    assert deepseek_readout["DeepSeek-S"]["ccd_valid_choice_count"] == "2180"
    assert deepseek_readout["DeepSeek-S"]["denevil_visible_response_count"] == "20474"
    assert "May 9 logs" in deepseek_readout["DeepSeek-S"]["public_interpretation"]
    assert deepseek_readout["DeepSeek-M"]["answer_validation"] == "passed_visible_answer_guardrail"
    assert deepseek_readout["DeepSeek-M"]["unimoral_action_accuracy"] == "0.683629"
    assert deepseek_readout["DeepSeek-M"]["value_average_accuracy"] == "0.634673"
    assert deepseek_readout["DeepSeek-M"]["ccd_valid_choice_count"] == "2177"
    assert deepseek_readout["DeepSeek-M"]["denevil_visible_response_count"] == "20514"
    assert deepseek_readout["DeepSeek-L"]["answer_validation"] == "passed_visible_answer_guardrail"
    assert deepseek_readout["DeepSeek-L"]["unimoral_action_accuracy"] == "0.562550"
    assert deepseek_readout["DeepSeek-L"]["unimoral_visible_answers"] == "8769"
    assert deepseek_readout["DeepSeek-L"]["value_relevance_accuracy"] == "0.681162"
    assert deepseek_readout["DeepSeek-L"]["value_valence_accuracy"] == "0.680154"
    assert deepseek_readout["DeepSeek-L"]["value_average_accuracy"] == "0.680658"
    assert deepseek_readout["DeepSeek-L"]["ccd_valid_choice_count"] == "2109"
    assert deepseek_readout["DeepSeek-L"]["denevil_visible_response_count"] == "20331"
    assert "large R1 rerun" in deepseek_readout["DeepSeek-L"]["public_interpretation"]

    with (release_dir / "ccd-choice-distribution.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "option_1_pct" in reader.fieldnames
        assert "option_10_pct" in reader.fieldnames
        assert "dominant_option" in reader.fieldnames
        assert "dominant_option_share" in reader.fieldnames
        assert "distribution_status" in reader.fieldnames
        ccd_distribution_rows = list(reader)
    assert len(ccd_distribution_rows) == 21
    for row in ccd_distribution_rows:
        valid_rate = row["valid_selection_rate"]
        if valid_rate == "n/a":
            continue
        if float(row["valid_selection_count"]) > 0:
            option_total = sum(float(row[f"option_{cluster_id}_pct"]) for cluster_id in range(1, 11))
            assert abs(option_total - 100.0) < 1e-5
        else:
            assert all(row[f"option_{cluster_id}_pct"] == "n/a" for cluster_id in range(1, 11))
            assert all(row[f"option_{cluster_id}_delta_pp"] == "n/a" for cluster_id in range(1, 11))
    ccd_rows_by_line = {row["line_label"]: row for row in ccd_distribution_rows}
    expected_openai_ccd = {
        "GPT-4o-mini Ref": ("OpenAI Ref", "Ref", "2182", "100.000000", "17.094409", "8.937721"),
        "GPT-5 nano": ("OpenAI GPT-5", "S", "2181", "99.954170", "27.785420", "6.793151"),
        "GPT-4.1-nano Ref": ("OpenAI Ref", "Ref", "2182", "100.000000", "21.494042", "8.397459"),
        "GPT-5 mini": ("OpenAI GPT-5", "M", "2182", "100.000000", "25.297892", "7.131573"),
        "GPT-5.5": ("OpenAI GPT-5", "L", "2182", "100.000000", "27.268561", "7.058620"),
        "GPT-4.1-mini Ref": ("OpenAI Ref", "Ref", "2182", "100.000000", "22.410632", "8.069893"),
    }
    for line_label, (family, size_slot, valid_count, valid_rate, option_6_pct, effective_clusters) in expected_openai_ccd.items():
        openai_ccd = ccd_rows_by_line[line_label]
        assert openai_ccd["family"] == family
        assert openai_ccd["size_slot"] == size_slot
        assert openai_ccd["valid_selection_count"] == valid_count
        assert openai_ccd["valid_selection_rate"] == valid_rate
        assert openai_ccd["option_6_pct"] == option_6_pct
        assert openai_ccd["dominant_option"] == "option_6 (Nordic Europe)"
        assert openai_ccd["effective_cluster_count"] == effective_clusters
    deepseek_small_ccd = ccd_rows_by_line["DeepSeek-S"]
    assert deepseek_small_ccd["distribution_status"] == "ok"
    assert deepseek_small_ccd["valid_selection_count"] == "2180"
    assert deepseek_small_ccd["valid_selection_rate"] == "99.908341"
    assert deepseek_small_ccd["dominant_option"] == "option_7 (Sub Saharan Africa)"
    assert deepseek_small_ccd["dominant_option_share"] == "13.761468"
    assert deepseek_small_ccd["effective_cluster_count"] == "9.567679"
    deepseek_medium_ccd = ccd_rows_by_line["DeepSeek-M"]
    if deepseek_medium_ccd["distribution_status"] == "ok":
        assert deepseek_medium_ccd["valid_selection_count"] == "2177"
        assert deepseek_medium_ccd["valid_selection_rate"] == "99.770852"
        assert deepseek_medium_ccd["dominant_option"] == "option_6 (Nordic Europe)"
        assert deepseek_medium_ccd["dominant_option_share"] == "22.553973"
    else:
        assert deepseek_medium_ccd["distribution_status"] == "missing_eval_samples"
        assert deepseek_medium_ccd["valid_selection_count"] == "n/a"
        assert deepseek_medium_ccd["valid_selection_rate"] == "n/a"
        assert deepseek_medium_ccd["dominant_option"] == "n/a"
        assert deepseek_medium_ccd["dominant_option_share"] == "n/a"
    deepseek_large_ccd = ccd_rows_by_line["DeepSeek-L"]
    assert deepseek_large_ccd["distribution_status"] == "ok"
    assert deepseek_large_ccd["valid_selection_count"] == "2109"
    assert deepseek_large_ccd["valid_selection_rate"] == "96.654445"
    assert deepseek_large_ccd["dominant_option"] == "option_6 (Nordic Europe)"
    assert deepseek_large_ccd["dominant_option_share"] == "20.720721"
    assert deepseek_large_ccd["effective_cluster_count"] == "8.682841"
    llama_large_ccd = ccd_rows_by_line["Llama-L"]
    if llama_large_ccd["distribution_status"] == "ok":
        assert llama_large_ccd["valid_selection_count"] == "2013"
        assert llama_large_ccd["valid_selection_rate"] == "92.254812"
        assert llama_large_ccd["option_6_pct"] == "23.546945"
        assert llama_large_ccd["dominant_option"] == "option_6 (Nordic Europe)"
        assert llama_large_ccd["dominant_option_share"] == "23.546945"
    else:
        assert llama_large_ccd["distribution_status"] == "missing_eval_samples"
        assert llama_large_ccd["valid_selection_count"] == "n/a"
        assert llama_large_ccd["valid_selection_rate"] == "n/a"
    qwen_small_ccd = ccd_rows_by_line["Qwen-S"]
    if qwen_small_ccd["distribution_status"] == "ok":
        assert qwen_small_ccd["valid_selection_count"] == "2182"
        assert qwen_small_ccd["valid_selection_rate"] == "100.000000"
        assert qwen_small_ccd["option_6_pct"] == "19.202566"
        assert qwen_small_ccd["dominant_option"] == "option_6 (Nordic Europe)"
    else:
        assert qwen_small_ccd["distribution_status"] == "missing_eval_samples"
        assert qwen_small_ccd["valid_selection_count"] == "n/a"
        assert qwen_small_ccd["valid_selection_rate"] == "n/a"

    with (release_dir / "denevil-proxy-summary.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert reader.fieldnames[:8] == [
            "model_line",
            "model_family",
            "size_slot",
            "proxy_status",
            "total_proxy_samples",
            "generated_response_count",
            "valid_response_rate",
            "persisted_checkpoint_pct",
        ]
        assert "route_model_name" in reader.fieldnames
        assert "latest_successful_eval_created_at" in reader.fieldnames
        assert "latest_proxy_artifact_updated_at" in reader.fieldnames
        assert "limitation_flag" in reader.fieldnames
        denevil_proxy_rows = list(reader)
    assert len(denevil_proxy_rows) == 15
    denevil_proxy_by_line = {row["model_line"]: row for row in denevil_proxy_rows}
    deepseek_small_proxy = denevil_proxy_by_line["DeepSeek-S"]
    assert deepseek_small_proxy["route_short_label"] == "deepseek-r1-distill-llama-70b"
    assert deepseek_small_proxy["proxy_status"] == "Proxy complete"
    if deepseek_small_proxy["total_proxy_samples"] == "20518":
        assert deepseek_small_proxy["generated_response_count"] == "20474"
        assert deepseek_small_proxy["valid_response_rate"] == "0.997856"
        assert deepseek_small_proxy["persisted_checkpoint_pct"] == "100.000000"
        assert deepseek_small_proxy["limitation_flag"] == "partial_visible_response_coverage"
        assert "near-complete visible proxy coverage" in deepseek_small_proxy["notes"].lower()
    else:
        assert deepseek_small_proxy["total_proxy_samples"] == "n/a"
        assert deepseek_small_proxy["generated_response_count"] == "n/a"
        assert deepseek_small_proxy["valid_response_rate"] == "n/a"
        assert deepseek_small_proxy["persisted_checkpoint_pct"] == "n/a"
        assert deepseek_small_proxy["limitation_flag"] == "missing_proxy_artifact"
    deepseek_medium_proxy = denevil_proxy_by_line["DeepSeek-M"]
    assert deepseek_medium_proxy["route_short_label"] == "deepseek-chat-v3.1"
    assert deepseek_medium_proxy["proxy_status"] == "Proxy complete"
    if deepseek_medium_proxy["total_proxy_samples"] == "20518":
        assert deepseek_medium_proxy["generated_response_count"] == "20514"
        assert deepseek_medium_proxy["valid_response_rate"] == "0.999805"
        assert deepseek_medium_proxy["persisted_checkpoint_pct"] == "100.000000"
        assert deepseek_medium_proxy["limitation_flag"] == "proxy_only_complete"
    else:
        assert deepseek_medium_proxy["total_proxy_samples"] == "n/a"
        assert deepseek_medium_proxy["generated_response_count"] == "n/a"
        assert deepseek_medium_proxy["valid_response_rate"] == "n/a"
        assert deepseek_medium_proxy["persisted_checkpoint_pct"] == "n/a"
        assert deepseek_medium_proxy["limitation_flag"] == "missing_proxy_artifact"
    deepseek_large_proxy = denevil_proxy_by_line["DeepSeek-L"]
    assert deepseek_large_proxy["proxy_status"] == "Proxy complete"
    assert deepseek_large_proxy["total_proxy_samples"] == "20518"
    assert deepseek_large_proxy["generated_response_count"] == "20331"
    assert deepseek_large_proxy["valid_response_rate"] == "0.990886"
    assert deepseek_large_proxy["persisted_checkpoint_pct"] == "100.000000"
    assert deepseek_large_proxy["route_short_label"] == "deepseek-r1"
    assert deepseek_large_proxy["limitation_flag"] == "partial_visible_response_coverage"
    assert "Visible proxy coverage reached 99.1%" in deepseek_large_proxy["notes"]
    qwen_small_proxy = denevil_proxy_by_line["Qwen-S"]
    if qwen_small_proxy["generated_response_count"] != "n/a":
        assert qwen_small_proxy["generated_response_count"] == "20515"
        assert qwen_small_proxy["valid_response_rate"] == "0.999854"
        assert qwen_small_proxy["persisted_checkpoint_pct"] == "100.000000"
    else:
        assert qwen_small_proxy["limitation_flag"] == "missing_proxy_artifact"

    with (release_dir / "readiness-tier-matrix.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "dashboard_unit",
            "cell_granularity",
            "line_label",
            "model_id",
            "provider_route",
            "family",
            "size_slot",
            "benchmark",
            "subtask_or_rq",
            "sample_set",
            "aggregation_rule",
            "readiness_tier",
            "metric_layer",
            "result_status",
            "blocker_status",
            "evidence_status",
            "primary_metric",
            "primary_metric_value",
            "source_file",
            "run_id_or_source_artifact",
            "lower_level_limitations",
            "interpretation",
        ]
        readiness_rows = list(reader)
    assert len(readiness_rows) == 105
    readiness_by_pair = {
        (row["line_label"], row["benchmark"]): row
        for row in readiness_rows
    }
    minimax_small_smid = readiness_by_pair[("MiniMax-S", "SMID")]
    assert minimax_small_smid["dashboard_unit"] == "public_summary_model_line_x_benchmark"
    assert minimax_small_smid["cell_granularity"] == "summary"
    assert "public model line" in minimax_small_smid["lower_level_limitations"]
    assert minimax_small_smid["readiness_tier"] == "Tier 3"
    assert minimax_small_smid["metric_layer"] == "M1 benchmark-faithful accuracy"
    assert minimax_small_smid["result_status"] == "interpretable_comparable"
    assert minimax_small_smid["blocker_status"] == ""
    assert minimax_small_smid["subtask_or_rq"] == "moral_rating + foundation_classification"
    assert minimax_small_smid["primary_metric_value"] == "0.431996"
    qwen_medium_smid = readiness_by_pair[("Qwen-M", "SMID")]
    assert qwen_medium_smid["readiness_tier"] == ""
    assert qwen_medium_smid["result_status"] == "blocked"
    assert qwen_medium_smid["blocker_status"] == "route_gap"
    assert qwen_medium_smid["evidence_status"] == "route_gap"
    assert qwen_medium_smid["primary_metric_value"] == ""
    gpt55_unimoral = readiness_by_pair[("GPT-5.5", "UniMoral")]
    assert gpt55_unimoral["readiness_tier"] == "Tier 3"
    assert gpt55_unimoral["metric_layer"] == "M1 benchmark-faithful accuracy"
    assert gpt55_unimoral["primary_metric_value"] == "0.683629"
    gpt55_smid = readiness_by_pair[("GPT-5.5", "SMID")]
    assert gpt55_smid["readiness_tier"] == ""
    assert gpt55_smid["result_status"] == "blocked"
    assert gpt55_smid["blocker_status"] == "route_gap"
    gpt5_mini_ccd = readiness_by_pair[("GPT-5 mini", "CCD-Bench")]
    assert gpt5_mini_ccd["readiness_tier"] == "Tier 3"
    assert gpt5_mini_ccd["metric_layer"] == "M2 choice-distribution behavior"
    assert gpt5_mini_ccd["subtask_or_rq"] == "cultural_choice"
    assert gpt5_mini_ccd["primary_metric"] == "choice_distribution"
    assert "dominant=option_" in gpt5_mini_ccd["primary_metric_value"]
    assert "effective_clusters=" in gpt5_mini_ccd["primary_metric_value"]
    gpt5_mini_denevil = readiness_by_pair[("GPT-5 mini", "Denevil")]
    assert gpt5_mini_denevil["readiness_tier"] == ""
    assert gpt5_mini_denevil["metric_layer"] == "M3 proxy behavior/provenance"
    assert gpt5_mini_denevil["result_status"] == "blocked"
    assert gpt5_mini_denevil["blocker_status"] == "not_run"
    assert gpt5_mini_denevil["evidence_status"] == "not_run"
    qwen_small_denevil = readiness_by_pair[("Qwen-S", "Denevil")]
    assert qwen_small_denevil["readiness_tier"] == ""
    assert qwen_small_denevil["result_status"] == "proxy_only_available"
    assert qwen_small_denevil["blocker_status"] == "proxy_only_not_paper_faithful"
    assert qwen_small_denevil["primary_metric"] == "proxy_behavior_mix"
    assert qwen_small_denevil["primary_metric_value"] == "see denevil-behavior-summary.csv"
    assert "No Tier 3 readiness tier is assigned" in qwen_small_denevil["interpretation"]

    with (release_dir / "denevil-behavior-summary.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert reader.fieldnames[:6] == [
            "model_line",
            "model_family",
            "size_slot",
            "total_proxy_samples",
            "protective_refusal_count",
            "protective_refusal_rate",
        ]
        assert "potentially_risky_continuation_rate" in reader.fieldnames
        assert "no_visible_answer_rate" in reader.fieldnames
        assert "protective_response_rate" in reader.fieldnames
        assert "dominant_behavior" in reader.fieldnames
        assert "behavior_status" in reader.fieldnames
        denevil_behavior_rows = list(reader)
    assert len(denevil_behavior_rows) == 15
    denevil_behavior_by_line = {row["model_line"]: row for row in denevil_behavior_rows}
    deepseek_small_behavior = denevil_behavior_by_line["DeepSeek-S"]
    if deepseek_small_behavior["behavior_status"] == "ok":
        assert deepseek_small_behavior["total_proxy_samples"] == "20518"
        assert deepseek_small_behavior["protective_response_rate"] == "98.191832"
        assert deepseek_small_behavior["no_visible_answer_rate"] == "0.214446"
        assert deepseek_small_behavior["potentially_risky_continuation_rate"] == "1.354908"
        assert deepseek_small_behavior["dominant_behavior"] == "Corrective / contextual response"
        assert (
            "no longer has the old empty-answer collapse"
            in deepseek_small_behavior["limitation_note"].lower()
        )
    else:
        assert deepseek_small_behavior["behavior_status"] == "missing_eval_samples"
        assert deepseek_small_behavior["total_proxy_samples"] == "n/a"
        assert deepseek_small_behavior["dominant_behavior"] == "n/a"
    deepseek_medium_behavior = denevil_behavior_by_line["DeepSeek-M"]
    if deepseek_medium_behavior["behavior_status"] == "ok":
        assert deepseek_medium_behavior["total_proxy_samples"] == "20518"
        assert deepseek_medium_behavior["protective_response_rate"] == "99.122722"
        assert deepseek_medium_behavior["no_visible_answer_rate"] == "0.019495"
        assert deepseek_medium_behavior["potentially_risky_continuation_rate"] == "0.229067"
        assert deepseek_medium_behavior["dominant_behavior"] == "Corrective / contextual response"
    else:
        assert deepseek_medium_behavior["behavior_status"] == "missing_eval_samples"
        assert deepseek_medium_behavior["total_proxy_samples"] == "n/a"
        assert deepseek_medium_behavior["dominant_behavior"] == "n/a"
    deepseek_large_behavior = denevil_behavior_by_line["DeepSeek-L"]
    assert deepseek_large_behavior["behavior_status"] == "ok"
    assert deepseek_large_behavior["total_proxy_samples"] == "20518"
    assert deepseek_large_behavior["protective_response_rate"] == "94.921532"
    assert deepseek_large_behavior["no_visible_answer_rate"] == "0.911395"
    assert deepseek_large_behavior["potentially_risky_continuation_rate"] == "0.657959"
    assert deepseek_large_behavior["dominant_behavior"] == "Corrective / contextual response"
    llama_large_behavior = denevil_behavior_by_line["Llama-L"]
    if llama_large_behavior["behavior_status"] == "ok":
        assert llama_large_behavior["protective_refusal_rate"] == "22.882347"
        assert llama_large_behavior["corrective_contextual_response_rate"] == "74.719758"
        assert llama_large_behavior["potentially_risky_continuation_rate"] == "0.199825"
        assert llama_large_behavior["dominant_behavior"] == "Corrective / contextual response"
    else:
        assert llama_large_behavior["behavior_status"] == "missing_eval_samples"
        assert llama_large_behavior["dominant_behavior"] == "n/a"

    with (release_dir / "denevil-prompt-family-breakdown.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert reader.fieldnames == [
            "model_line",
            "model_family",
            "size_slot",
            "prompt_family",
            "prompt_count",
            "protective_response_rate",
            "risky_continuation_rate",
            "empty_response_rate",
            "dominant_behavior",
        ]
        denevil_prompt_family_rows = list(reader)
    assert len(denevil_prompt_family_rows) == 90
    prompt_family_by_key = {
        (row["model_line"], row["prompt_family"]): row for row in denevil_prompt_family_rows
    }
    deepseek_large_sabotage = prompt_family_by_key[("DeepSeek-L", "Illicit access / sabotage")]
    assert deepseek_large_sabotage["prompt_count"] == "798"
    assert deepseek_large_sabotage["protective_response_rate"] == "90.225564"
    assert deepseek_large_sabotage["dominant_behavior"] == "Protective refusal"
    deepseek_small_prompt_family = prompt_family_by_key[
        ("DeepSeek-S", "Loaded social / political judgment")
    ]
    if deepseek_small_prompt_family["prompt_count"] == "n/a":
        assert deepseek_small_prompt_family["protective_response_rate"] == "n/a"
        assert deepseek_small_prompt_family["empty_response_rate"] == "n/a"
        assert deepseek_small_prompt_family["dominant_behavior"] == "n/a"
    else:
        assert deepseek_small_prompt_family["protective_response_rate"] == "10.000000"
        assert deepseek_small_prompt_family["empty_response_rate"] == "1.666667"
        assert deepseek_small_prompt_family["dominant_behavior"] == "Potentially risky continuation"
    deepseek_medium_prompt_family = prompt_family_by_key[
        ("DeepSeek-M", "Loaded social / political judgment")
    ]
    if deepseek_medium_prompt_family["prompt_count"] == "n/a":
        assert deepseek_medium_prompt_family["protective_response_rate"] == "n/a"
        assert deepseek_medium_prompt_family["empty_response_rate"] == "n/a"
        assert deepseek_medium_prompt_family["dominant_behavior"] == "n/a"
    else:
        assert deepseek_medium_prompt_family["protective_response_rate"] == "100.000000"
        assert deepseek_medium_prompt_family["empty_response_rate"] == "0.000000"
        assert deepseek_medium_prompt_family["dominant_behavior"] == "Corrective / contextual response"
    qwen_small_prompt_family = prompt_family_by_key[("Qwen-S", "Violence / physical harm")]
    if qwen_small_prompt_family["prompt_count"] == "n/a":
        assert qwen_small_prompt_family["protective_response_rate"] == "n/a"
        assert qwen_small_prompt_family["risky_continuation_rate"] == "n/a"
    else:
        assert qwen_small_prompt_family["protective_response_rate"] == "99.342105"
        assert qwen_small_prompt_family["risky_continuation_rate"] == "0.493421"

    with (release_dir / "denevil-proxy-examples.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "model_line",
            "proxy_prompt_type",
            "shortened_model_output_pattern",
            "interpretable_signal",
        ]
        denevil_example_rows = list(reader)
    assert len(denevil_example_rows) >= 0
    deepseek_small_examples = [
        row for row in denevil_example_rows if row["model_line"] == "DeepSeek-S"
    ]
    if deepseek_small_examples:
        assert any(
            row["shortened_model_output_pattern"] == "No visible answer"
            and "subset of traces that actually surface a visible public answer"
            in row["interpretable_signal"].lower()
            for row in deepseek_small_examples
        )

    with (release_dir / "benchmark-difficulty-summary.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        difficulty_rows = list(reader)
    assert [row["benchmark"] for row in difficulty_rows] == ["UniMoral", "SMID", "Value Kaleidoscope"]
    assert any(
        row["benchmark"] == "SMID"
        and row["mean_accuracy"] in {"0.364610", "0.378030", "0.363773", "0.364030", "0.364049", "0.364232"}
        and row["spread"] in {"0.279545", "0.266406", "0.286906", "0.284597"}
        and row["best_line"] == "Qwen-L"
        and row["weakest_line"] in {"MiniMax-L", "Llama-S"}
        for row in difficulty_rows
    )
    assert any(
        row["benchmark"] == "Value Kaleidoscope"
        and row["mean_accuracy"] in {"0.650180", "0.662989", "0.668485", "0.673238", "0.674954"}
        and row["best_line"] in {"Llama-M", "MiniMax-L"}
        and row["weakest_line"] == "Llama-S"
        for row in difficulty_rows
    )

    with (release_dir / "family-scaling-summary.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        scaling_rows = list(reader)
    assert tuple(row["family"] for row in scaling_rows) in {
        ("Qwen", "MiniMax", "DeepSeek", "Llama", "Gemma", "OpenAI GPT-5", "OpenAI Ref"),
        ("Qwen", "MiniMax", "DeepSeek", "Llama", "Gemma", "OpenAI Ref"),
        ("Qwen", "MiniMax", "DeepSeek", "Llama", "Gemma"),
        ("Qwen", "DeepSeek", "Llama", "Gemma"),
    }
    minimax_scaling_rows = [row for row in scaling_rows if row["family"] == "MiniMax"]
    if minimax_scaling_rows:
        assert any(
            row["evidence_scope"] == "3 comparable metric series available."
            and row["numeric_pattern"] in {
                "UniMoral: L 0.661; SMID: S 0.432 -> L 0.198; Value Kaleidoscope: L 0.741",
                "UniMoral: S 0.661 -> L 0.661; SMID: S 0.432 -> L 0.198; Value Kaleidoscope: S 0.740 -> L 0.741",
                "UniMoral: S 0.661 -> M 0.659 -> L 0.661; SMID: S 0.432 -> L 0.198; Value Kaleidoscope: S 0.740 -> M 0.740 -> L 0.741",
            }
            and "too sparse" in row["interpretation"]
            for row in minimax_scaling_rows
        )
    assert any(
        row["family"] == "Qwen"
        and "Text benchmarks now have S/M/L comparable points" in row["evidence_scope"]
        and "UniMoral: S 0.647 -> M 0.665 -> L 0.665" in row["numeric_pattern"]
        and "SMID: S 0.368 -> L 0.483" in row["numeric_pattern"]
        and "CCD-Bench" not in row["numeric_pattern"]
        and "Denevil" not in row["numeric_pattern"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "Llama"
        and "Text benchmarks now have S/M/L comparable points" in row["evidence_scope"]
        and "Value Kaleidoscope: S 0.529 -> M 0.724 -> L 0.692" in row["numeric_pattern"]
        and "CCD-Bench" not in row["numeric_pattern"]
        and "Denevil" not in row["numeric_pattern"]
        and "M still beats L on some text metrics" in row["interpretation"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "Gemma"
        and "Full S/M/L comparable sweep" in row["evidence_scope"]
        and "SMID: S 0.417 -> M 0.364 -> L 0.412" in row["numeric_pattern"]
        and "does not give a simple bigger-is-better story" in row["interpretation"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "DeepSeek"
        and "S/M/L text lines are now accuracy-comparable" in row["evidence_scope"]
        and "UniMoral: S 0.661 -> M 0.684 -> L 0.563" in row["numeric_pattern"]
        and "Value Kaleidoscope: S 0.695 -> M 0.635 -> L 0.681" in row["numeric_pattern"]
        and "CCD-Bench" not in row["numeric_pattern"]
        and "Denevil" not in row["numeric_pattern"]
        and "text-only curve" in row["interpretation"]
        and "image benchmark is absent" in row["interpretation"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "OpenAI GPT-5"
        and "Text-only GPT-5 S/M/L series" in row["evidence_scope"]
        and "UniMoral: S 0.654 -> M 0.678 -> L 0.684" in row["numeric_pattern"]
        and "Value Kaleidoscope: S 0.617 -> M 0.739 -> L 0.736" in row["numeric_pattern"]
        and "GPT-5.5 is L" in row["interpretation"]
        and "all-benchmark OpenAI coverage" in row["interpretation"]
        for row in scaling_rows
    )
    assert any(
        row["family"] == "OpenAI Ref"
        and "Three GPT-4o/GPT-4.1 text-only reference rows" in row["evidence_scope"]
        and "UniMoral: range 0.646-0.679" in row["numeric_pattern"]
        and "best GPT-4.1-mini Ref 0.679" in row["numeric_pattern"]
        and "Value Kaleidoscope: range 0.673-0.735" in row["numeric_pattern"]
        and "best GPT-4.1-mini Ref 0.735" in row["numeric_pattern"]
        and "should not be folded into the GPT-5 S/M/L curve" in row["interpretation"]
        for row in scaling_rows
    )

    report_text = (release_dir / "jenny-group-report.md").read_text(encoding="utf-8")
    release_readme = (release_dir / "README.md").read_text(encoding="utf-8")
    topline_summary = (release_dir / "topline-summary.md").read_text(encoding="utf-8")
    for text in (report_text, release_readme):
        assert "## TL;DR" in text
        assert "Key takeaways:" in text
        assert text.index("## Benchmark Result Visuals") < text.index("## TL;DR")
        tldr_text = markdown_h2_section(text, "## TL;DR")
        assert "Best comparable all-around line" in tldr_text
        assert "Bottom line" in tldr_text
        assert "text moral reasoning is usable; image moral judgment is the bottleneck" in tldr_text
        assert "Best text-only line" in tldr_text
        assert "Scaling read" in tldr_text
        assert "bigger is not reliably better" in tldr_text
        assert "UniMoral readout" in tldr_text
        assert "CCD-Bench read" in tldr_text
        assert "cultural-choice behavior, not accuracy" in tldr_text
        assert "**Current GitHub-facing boundary:**" not in tldr_text
        assert "OpenAI/GPT read" in tldr_text
        assert "`GPT-5 nano` = S, `GPT-5 mini` = M, `GPT-5.5` = L" in tldr_text
        assert "UniMoral tops out at `GPT-5.5`" in tldr_text
        assert "Completed GPT-5 RQ2-RQ4 follow-up" in tldr_text
        assert "RQ4 BERTScore F1 0.725" in tldr_text
        assert "semantic RQ4 still peaks at `Llama-M` 0.730" in tldr_text
        assert "GPT-4o/GPT-4.1 rows are separate text refs" in tldr_text
        assert "GPT-4o-mini reference line" not in text
        assert "76,486/76,486 parsed prompts" not in text
        assert "DeNEVIL boundary" in tldr_text
        assert "proxy behavior, not paper-faithful MoralPrompt scoring" in tldr_text
        assert "Small-model floor" in tldr_text
        assert "May 13 Mistral/Qwen/Llama follow-up shows a capability threshold" in tldr_text
        assert "Small-model capability floor | May 13 follow-up" in text
        assert "### Small-Model Follow-Up: Capability Floor" in text
        assert "`Mistral Nemo` | 12B | 0.648" in text
        assert "additional_model_sweep_unimoral_accuracy.svg" in text
        assert "additional_model_sweep_scaling.svg" in text
        assert "additional_model_sweep_ccd_dominant_share.svg" in text
        assert "The hardest benchmark is SMID" not in tldr_text
        assert "Bigger is not automatically more moral" not in tldr_text
        assert "DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring" not in tldr_text
        assert "## Results First" in text
        assert "## Benchmark Result Visuals" in text
        assert "Start here. These figures are the main result surface" in text
        assert "Visual readout in one sentence" in text
        assert "### 1. UniMoral RQ1-RQ4: family-size scaling and task readout" in text
        assert "### 2. SMID / Value Kaleidoscope: topline comparable accuracy" in text
        assert "### 3. SMID / Value Kaleidoscope: family-size scaling" in text
        assert "### 4. CCD-Bench: cultural-cluster choice behavior" in text
        assert "### 5. CCD-Bench: dominant-option concentration" in text
        assert "### 6. DeNEVIL: proxy behavioral outcomes" in text
        assert "### 7. CCD-Bench: dominant-option concentration" not in text
        assert "### 8. DeNEVIL: proxy behavioral outcomes" not in text
        assert "## Interpretation" in text
        assert "### Direct Read" in text
        assert "Overall comparable winner" in text
        assert "Text-only winner" in text
        assert "### Interpretation At A Glance" in text
        assert "### Benchmark Reading Guide" in text
        assert "| Benchmark readout | In plain language: what it asks | Why it matters for moral psychology | How to read this release |" in text
        assert "`UniMoral RQ1: action prediction`" in text
        assert "`UniMoral RQ2: moral typology`" in text
        assert "`UniMoral RQ3: factor attribution`" in text
        assert "`UniMoral RQ4: consequence generation`" in text
        assert "`SMID` | Look at real images and infer moral wrongness or the dominant moral foundation." in text
        assert "`CCD-Bench` | Choose among ten culturally grounded responses to a cross-cultural dilemma." in text
        assert "`DeNEVIL` | Probe how the model behaves when prompts try to surface unethical or value-violating content." in text
        assert "### Benchmark Difficulty Profile" in text
        assert "### Family Scaling Profile" in text
        assert "### CCD-Bench Choice Behavior" in text
        assert "### DeNEVIL Proxy Behavioral Evidence" in text
        assert "### Reporting Guardrails" in text
        assert "These benchmarks do not all ask for the same kind of moral competence" in text
        assert "Moral psychology cares about why people choose, not only what they choose." in text
        assert "### Latest Family-Size Progress Snapshot" not in text
        assert "Metric definition version: `2026-04-30`." in text
        assert "### DeepSeek S/M/L Log-Derived Readout" in text
        assert "Valid text-only no-thinking rerun from saved May 9 logs" in text
        assert "`DeepSeek-M` | UniMoral 0.684; Value 0.635" in text
        assert "`DeepSeek-L` | UniMoral 0.563; Value 0.681" in text
        assert "Strongest fully observed comparable line | `MiniMax-S` averages 0.611" in text
        assert "Strongest text-only comparable line | `GPT-5.5` reaches UniMoral 0.684 and Value 0.736" in text
        assert "Keep `DeepSeek-S` out of all-around winner claims because it has no SMID route" in text
        assert "CCD-Bench should not be flattened into a universal accuracy number." in text
        assert "The repo still lacks a stable local `MoralPrompt` export" in text
        assert "paper-aligned APV / EVR / MVP are `n/a`" in text
        assert "headline DeNEVIL behavioral-outcomes chart already appears above" in text
        assert "ccd-choice-distribution.csv" in text
        assert "option1_unimoral_task_heatmap.svg" in text
        assert "option1_unimoral_generation_quality.svg" in text
        assert "option1_unimoral_family_scaling.svg" in text
        assert "option1_ccd_choice_distribution.svg" in text
        assert "option1_ccd_dominant_option_share.svg" in text
        assert "option1_denevil_behavior_outcomes.svg" in text
        assert "option1_family_scaling_profile.svg" in text
        assert "option1_ccd_valid_choice_coverage.svg" not in text
        assert "option1_denevil_prompt_family_heatmap.svg" not in text
        assert "option1_denevil_proxy_status_matrix.svg" not in text
        assert "option1_denevil_proxy_sample_volume.svg" not in text
        assert "option1_denevil_proxy_valid_response_rate.svg" not in text
        assert "option1_denevil_proxy_pipeline.svg" not in text
        assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in text
        assert "Current project total cost" in text
        assert "Cost scope" in text
        assert "Current project cost estimate" not in text
        assert "Current cost to date" not in text
        assert "24634450927" not in text
        assert "| `MiniMax-L` |" in text
        assert "| `MiniMax-S` |" in text
        assert "headline family-scaling figure already appears above" in text
        assert "Read `CCD-Bench` in its dedicated choice-behavior figures" in text
        assert "Read `Denevil` only through the dedicated proxy evidence package." in text
        assert "Low-level DeNEVIL QA/provenance artifacts remain exported" in text
        assert "## Interpretation Notes" not in text
        assert text.count("![Comparable accuracy bars]") == 1
        assert text.count("![UniMoral family-size scaling by RQ]") == 1
        assert text.count("![Family scaling profile]") == 1
        assert text.count("![CCD choice distribution]") == 1
        assert text.count("![CCD dominant-option share]") == 1
        assert text.count("![DeNEVIL proxy behavioral outcomes]") == 1
        assert "without re-embedding the same chart" in text
        assert "without re-embedding low-level QA charts" in text

    assert "## Local Expansion Checkpoint" in report_text
    assert "| `Next queued text lines` |" in report_text
    assert re.search(
        r"^\| `Next queued text lines` \| [^|]+ \| .+\|$",
        report_text,
        flags=re.MULTILINE,
    )
    assert "| Current live reruns |" in report_text
    assert re.search(
        r"^\| Current live reruns \| .+\|$",
        report_text,
        flags=re.MULTILINE,
    )
    assert "curated snapshot rather than a live dashboard" in report_text
    assert "## Status Key" in report_text
    assert "option1_benchmark_difficulty_profile.svg" in report_text
    assert "option1_family_scaling_profile.svg" in report_text
    assert "Partial" in report_text
    assert "Model families in scope" in report_text
    assert "## Safe One-Sentence Framing" in report_text
    assert "## Supporting Figures" not in report_text
    assert "option1_family_size_progress_overview.svg" not in report_text
    assert "![Coverage matrix]" not in report_text
    assert "## Full Family-Size Progress Matrix" not in report_text
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | --- |" not in report_text

    assert "## Local Expansion Checkpoint" in release_readme
    assert "| `Next queued text lines` |" in release_readme
    assert re.search(
        r"^\| `Next queued text lines` \| [^|]+ \| .+\|$",
        release_readme,
        flags=re.MULTILINE,
    )
    assert "| Current live reruns |" in release_readme
    assert re.search(
        r"^\| Current live reruns \| .+\|$",
        release_readme,
        flags=re.MULTILINE,
    )
    assert "sample volume chart" not in release_readme
    assert "benchmark difficulty profile" in release_readme
    assert "family scaling profile" in release_readme
    assert "## Start Here" in release_readme
    assert "### DATA, CLICK HERE:" in release_readme
    assert "[unimoral-full-benchmark.csv](unimoral-full-benchmark.csv)" in release_readme
    assert "[smid-results.csv](smid-results.csv)" in release_readme
    assert "[value-kaleidoscope-results.csv](value-kaleidoscope-results.csv)" in release_readme
    assert "## Benchmark Result Visuals" in release_readme
    assert "## Status Key" in release_readme
    assert "option1_benchmark_difficulty_profile.svg" in release_readme
    assert "option1_family_scaling_profile.svg" in release_readme
    assert "## Supporting Figures" not in release_readme
    assert "option1_family_size_progress_overview.svg" not in release_readme
    assert "Partial" in release_readme
    assert "Model families in scope" in release_readme
    assert "Done" in release_readme
    assert "denevil-proxy-summary.csv" in release_readme
    assert "denevil-behavior-summary.csv" in release_readme
    assert "denevil-prompt-family-breakdown.csv" in release_readme
    assert "denevil-proxy-examples.csv" in release_readme
    assert "readiness-tier-matrix.csv" in release_readme
    assert "## Family-Size Progress Matrix" not in release_readme
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | --- |" not in release_readme

    assert "## TL;DR" in topline_summary
    assert "Key takeaways:" in topline_summary
    assert "Bottom line" in topline_summary
    assert "**Current GitHub-facing boundary:**" not in topline_summary.split("## Frozen Snapshot Scope", 1)[0]
    assert "OpenAI/GPT read" in topline_summary
    assert "`GPT-5 nano` = S, `GPT-5 mini` = M, `GPT-5.5` = L" in topline_summary
    assert "GPT-4o/GPT-4.1 rows are separate text refs" in topline_summary
    assert "Small-model floor" in topline_summary
    assert "Mistral Nemo" in topline_summary
    assert "GPT-4o-mini reference line" not in topline_summary
    assert "76,486/76,486 parsed prompts" not in topline_summary
    assert "## Frozen Snapshot Scope" in topline_summary
    assert "Best comparable all-around line" in topline_summary
    assert "CCD-Bench read" in topline_summary
    assert "GPT-5 nano" in topline_summary
    assert "DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring" not in topline_summary
    assert "For the full public package, move next to `README.md`" in topline_summary

    progress_overview_svg = (figure_dir / "option1_family_size_progress_overview.svg").read_text(encoding="utf-8")
    assert "Family-Size Progress Overview" in progress_overview_svg
    assert "usable now" in progress_overview_svg
    assert "Pending / TBD / not planned" in progress_overview_svg
    assert "family-size matrix" in progress_overview_svg
    assert "MiniMax-S" in progress_overview_svg

    heatmap_svg = (figure_dir / "option1_accuracy_heatmap.svg").read_text(encoding="utf-8")
    assert "Current Comparable Accuracy Heatmap" in heatmap_svg
    assert "Accuracy scale" in heatmap_svg
    assert "n/a / no route" in heatmap_svg
    assert "withdrawn from direct comparison" in heatmap_svg
    assert "Qwen-S" in heatmap_svg

    benchmark_bar_svg = (figure_dir / "option1_benchmark_accuracy_bars.svg").read_text(encoding="utf-8")
    assert "Hatched SMID rows for DeepSeek-S, DeepSeek-M, DeepSeek-L, Qwen-M, and Llama-M are no-route cells" in benchmark_bar_svg
    assert "no SMID vision route" not in benchmark_bar_svg
    assert "Gemma-L" in benchmark_bar_svg
    assert "GPT-4o-mini Ref" in benchmark_bar_svg
    assert "GPT-5.5" in benchmark_bar_svg

    benchmark_difficulty_svg = (figure_dir / "option1_benchmark_difficulty_profile.svg").read_text(encoding="utf-8")
    assert "Benchmark Difficulty And Spread" in benchmark_difficulty_svg
    assert "Hardest current comparable benchmark" in benchmark_difficulty_svg
    assert "Widest cross-line spread" in benchmark_difficulty_svg

    family_scaling_svg = (figure_dir / "option1_family_scaling_profile.svg").read_text(encoding="utf-8")
    assert "Family Scaling Profile" in family_scaling_svg
    assert 'preserveAspectRatio="xMidYMin meet"' in family_scaling_svg
    assert 'style="max-width:100%;height:auto"' in family_scaling_svg
    assert "UniMoral is grouped in Figure 1 above" in family_scaling_svg
    assert "Two comparable benchmark panels here: SMID and Value Kaleidoscope." in family_scaling_svg
    assert "This figure is reserved for benchmark-faithful comparable accuracy, not CCD coverage or Denevil proxy evidence." in family_scaling_svg
    assert "OpenAI GPT-5 black text-only points are S=GPT-5 nano, M=GPT-5 mini, and L=GPT-5.5." in family_scaling_svg
    assert "GPT-4o and GPT-4.1 text refs are gray dashed reference lines where a text metric exists." in family_scaling_svg
    assert "OpenAI refs 67.3%-73.5%" in family_scaling_svg
    assert "Best GPT-4.1-mini Ref 73.5%" in family_scaling_svg
    assert "OpenAI GPT-5" in family_scaling_svg
    assert 'stroke="#000000"' in family_scaling_svg
    assert 'fill="#000000"' in family_scaling_svg
    for old_openai_color in ("#be123c", "#e11d48", "#fb7185"):
        assert old_openai_color not in family_scaling_svg
    assert "GPT-4o-mini Ref: no SMID route" not in family_scaling_svg
    assert "#dc2626" in family_scaling_svg
    assert ">Ref<" not in family_scaling_svg
    assert "#4 CCD-Bench" not in family_scaling_svg
    assert "#5 Denevil" not in family_scaling_svg
    assert "100% coverage" not in family_scaling_svg
    assert "67% coverage" not in family_scaling_svg
    assert "33% coverage" not in family_scaling_svg
    assert "0% coverage" not in family_scaling_svg
    assert "Read CCD-Bench in the choice-distribution" in family_scaling_svg
    assert "and dominant-option concentration figures." in family_scaling_svg
    assert "Read Denevil in the behavioral-outcomes figure." in family_scaling_svg
    assert "Do not mix proxy evidence into accuracy scaling." in family_scaling_svg
    assert "Value S/M/L are parsed from saved logs" in family_scaling_svg
    assert "Qwen" in family_scaling_svg
    assert "Takeaway: scaling is benchmark-specific" in family_scaling_svg
    if "MiniMax" in family_scaling_svg:
        assert "Value S/M/L are scored; SMID S/L have routes" in family_scaling_svg
        assert "route." in family_scaling_svg
    assert "Value scored at S/M/L; SMID at S/L." in family_scaling_svg
    assert "Value S/M/L are parsed from saved logs; no DeepSeek SMID route exists." in family_scaling_svg
    assert "full S/M/L sweep on SMID and Value." in family_scaling_svg
    assert "Only the small line is currently comparable." not in family_scaling_svg

    ccd_coverage_svg = (figure_dir / "option1_ccd_valid_choice_coverage.svg").read_text(encoding="utf-8")
    assert "Appendix QA: CCD-Bench valid-choice coverage, not accuracy." in ccd_coverage_svg
    assert "Appendix QA only." in ccd_coverage_svg
    assert "parseable integer in 1-10" in ccd_coverage_svg
    assert "Hatched rows are missing (`n/a`) rather than zero." in ccd_coverage_svg
    assert "MiniMax-M" in ccd_coverage_svg
    if "valid 0 / 2,182" in ccd_coverage_svg:
        assert "valid 2,013 / 2,182" in ccd_coverage_svg
    assert "Coverage = (# saved visible answers with a parseable 1-10 CCD choice) / (# all CCD-Bench prompts)." in ccd_coverage_svg

    ccd_distribution_svg = (figure_dir / "option1_ccd_choice_distribution.svg").read_text(encoding="utf-8")
    assert "CCD-Bench cultural-cluster choice behavior, not accuracy" in ccd_distribution_svg
    assert "Rows are grouped by family and ordered S → M → L" in ccd_distribution_svg
    assert "FAMILY" in ccd_distribution_svg
    assert "SIZE" in ccd_distribution_svg
    assert "DeepSeek-S" in ccd_distribution_svg
    assert "10% uniform baseline" in ccd_distribution_svg
    assert "Coverage stays in the appendix QA figure." in ccd_distribution_svg
    assert "Rows with no valid visible CCD selection stay hatched as `n/a`" in ccd_distribution_svg
    assert "Top cluster share" in ccd_distribution_svg
    assert "Effective clusters" in ccd_distribution_svg
    assert "No explicit rationale tags are retained in the public archive" in ccd_distribution_svg
    assert "Nordic Europe" in ccd_distribution_svg
    assert "Germanic Europe" in ccd_distribution_svg
    assert "Middle East" in ccd_distribution_svg
    assert "line chart" not in ccd_distribution_svg.lower()

    ccd_dominant_share_svg = (figure_dir / "option1_ccd_dominant_option_share.svg").read_text(encoding="utf-8")
    assert "CCD-Bench choice-concentration summary, not accuracy" in ccd_dominant_share_svg
    assert "Rows are grouped by family and ordered S → M → L" in ccd_dominant_share_svg
    assert "DeepSeek-S" in ccd_dominant_share_svg
    assert "Higher bars mean more concentration on one cluster." in ccd_dominant_share_svg
    assert "MiniMax-M" in ccd_dominant_share_svg
    assert "effective clusters" in ccd_dominant_share_svg.lower()
    assert "line chart" not in ccd_dominant_share_svg.lower()

    denevil_behavior_svg = (figure_dir / "option1_denevil_behavior_outcomes.svg").read_text(encoding="utf-8")
    assert "DeNEVIL proxy behavioral outcomes, not accuracy" in denevil_behavior_svg
    assert "Rows are grouped by family and ordered S → M → L for direct size comparisons." in denevil_behavior_svg
    assert "DOMINANT / PROTECTIVE" in denevil_behavior_svg
    assert "Each bar distributes all released proxy prompts across auditable visible-behavior categories." in denevil_behavior_svg
    assert "Paper-aligned APV / EVR / MVP are `n/a`" in denevil_behavior_svg
    assert "Protective refusal" in denevil_behavior_svg
    assert "Protective redirect" in denevil_behavior_svg
    assert "Corrective / contextual response" in denevil_behavior_svg
    assert "Potentially risky continuation" in denevil_behavior_svg
    assert "No visible answer" in denevil_behavior_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_behavior_svg
    assert "line chart" not in denevil_behavior_svg.lower()

    denevil_prompt_family_svg = (figure_dir / "option1_denevil_prompt_family_heatmap.svg").read_text(
        encoding="utf-8"
    )
    assert "DeNEVIL proxy protective-response rate by prompt family, not accuracy" in denevil_prompt_family_svg
    assert "Rows are grouped by family and ordered S → M → L." in denevil_prompt_family_svg
    assert "FAMILY" in denevil_prompt_family_svg
    assert "SIZE" in denevil_prompt_family_svg
    assert "Loaded social /" in denevil_prompt_family_svg
    assert "Prompt families are heuristic labels" in denevil_prompt_family_svg
    assert "protective visible behaviors" in denevil_prompt_family_svg
    assert "not paper-faithful foundations" in denevil_prompt_family_svg
    assert "line chart" not in denevil_prompt_family_svg.lower()

    denevil_status_matrix_svg = (figure_dir / "option1_denevil_proxy_status_matrix.svg").read_text(encoding="utf-8")
    assert "Appendix QA: DeNEVIL proxy status matrix" in denevil_status_matrix_svg
    assert "Appendix QA / provenance only." in denevil_status_matrix_svg
    assert "Proxy complete" in denevil_status_matrix_svg
    assert "Active rerun" not in denevil_status_matrix_svg
    assert "SAMPLE COUNT" in denevil_status_matrix_svg
    assert "GENERATED RESPONSES" in denevil_status_matrix_svg
    assert "VALID RESPONSE RATE" in denevil_status_matrix_svg
    assert "ROUTE / MODEL" in denevil_status_matrix_svg
    assert "NOTES" in denevil_status_matrix_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_status_matrix_svg
    assert "DeepSeek-S now has 99.8% visible proxy coverage" in denevil_status_matrix_svg
    assert "May 9 no-thinking archive" in denevil_status_matrix_svg

    denevil_sample_volume_svg = (figure_dir / "option1_denevil_proxy_sample_volume.svg").read_text(encoding="utf-8")
    assert "Appendix QA: DeNEVIL proxy sample volume" in denevil_sample_volume_svg
    assert "Appendix QA / provenance only." in denevil_sample_volume_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_sample_volume_svg
    assert "visible 20,474 / 20,518" in denevil_sample_volume_svg
    assert "MiniMax-M" in denevil_sample_volume_svg

    denevil_valid_rate_svg = (figure_dir / "option1_denevil_proxy_valid_response_rate.svg").read_text(encoding="utf-8")
    assert "Appendix QA: DeNEVIL proxy visible-response coverage" in denevil_valid_rate_svg
    assert "Appendix QA / provenance only." in denevil_valid_rate_svg
    assert "High bars mean stronger public traceability coverage, not stronger benchmark-faithful ethical quality." in denevil_valid_rate_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_valid_rate_svg
    assert "MiniMax-M" in denevil_valid_rate_svg
    assert "DeepSeek-S is 99.8% visible in the May 9 no-thinking archive" in denevil_valid_rate_svg
    assert "clearest cross-line comparison for the proxy package" not in denevil_valid_rate_svg

    denevil_pipeline_svg = (figure_dir / "option1_denevil_proxy_pipeline.svg").read_text(encoding="utf-8")
    assert "Appendix explanation: DeNEVIL proxy pipeline" in denevil_pipeline_svg
    assert "Supporting appendix only." in denevil_pipeline_svg
    assert "Denevil paper goal" in denevil_pipeline_svg
    assert "Local limitation" in denevil_pipeline_svg
    assert "Implemented release path" in denevil_pipeline_svg
    assert "Observed public evidence" in denevil_pipeline_svg
    assert "PI-facing deliverable" in denevil_pipeline_svg
    assert (
        "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; "
        "not benchmark-faithful ethical-quality scoring."
    ) in denevil_pipeline_svg
    assert "coverage and provenance rather than ethical-quality accuracy" in denevil_pipeline_svg

    sample_volume_svg = (figure_dir / "option1_sample_volume.svg").read_text(encoding="utf-8")
    assert "Paper setup:" in sample_volume_svg
    assert "Proxy:" in sample_volume_svg
    assert "% of release" in sample_volume_svg

    paper_alignment_svg = (figure_dir / "option1_paper_result_alignment_map.svg").read_text(encoding="utf-8")
    assert "Paper-vs-current Replication Map" in paper_alignment_svg
    assert "Partial overlap" in paper_alignment_svg
    assert "Distributional comparison only; do not" in paper_alignment_svg
    assert "read CCD as accuracy." in paper_alignment_svg
    assert "Proxy-only evidence; no paper-faithful" in paper_alignment_svg
    assert "MoralPrompt comparison." in paper_alignment_svg
    assert " ".join(("low", "cost")) not in paper_alignment_svg.lower()


def test_default_release_builder_leaves_repo_readme_untouched(tmp_path):
    repo_copy = tmp_path / "repo"
    script_copy = repo_copy / "scripts" / "build_release_artifacts.py"
    source_copy = repo_copy / "results" / "release" / "2026-04-19-option1" / "source" / "authoritative-summary.csv"
    benchmark_utils_copy = repo_copy / "src" / "inspect" / "evals" / "_benchmark_utils.py"

    script_copy.parent.mkdir(parents=True, exist_ok=True)
    source_copy.parent.mkdir(parents=True, exist_ok=True)
    benchmark_utils_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT, script_copy)
    shutil.copy2(SOURCE, source_copy)
    shutil.copy2(ROOT / "src" / "inspect" / "evals" / "_benchmark_utils.py", benchmark_utils_copy)
    (benchmark_utils_copy.parent / "__init__.py").write_text("", encoding="utf-8")

    original_readme = "# Unified Repo README\n\nThis file should not be rewritten by `make release`.\n"
    (repo_copy / "README.md").write_text(original_readme, encoding="utf-8")

    subprocess.run([sys.executable, str(script_copy)], check=True, cwd=repo_copy)

    assert (repo_copy / "README.md").read_text(encoding="utf-8") == original_readme


def test_openai_gpt_rows_are_visible_in_unimoral_and_ccd_figures():
    figure_dir = ROOT / "figures" / "release"
    openai_rows = [
        "GPT-4o-mini Ref",
        "GPT-5 nano",
        "GPT-5 mini",
        "GPT-5.5",
        "GPT-4.1-nano Ref",
        "GPT-4.1-mini Ref",
    ]

    unimoral_heatmap = (figure_dir / "option1_unimoral_task_heatmap.svg").read_text(encoding="utf-8")
    for label in openai_rows:
        assert label in unimoral_heatmap
    assert "Rows include OpenAI GPT-5 S/M/L across RQ1-RQ3" in unimoral_heatmap
    assert "GPT-4o/GPT-4.1 text refs where those tasks exist." in unimoral_heatmap
    assert "OpenAI refs are one-off" not in unimoral_heatmap

    unimoral_scaling = (figure_dir / "option1_unimoral_family_scaling.svg").read_text(encoding="utf-8")
    for label in ("GPT-5 nano", "GPT-5 mini", "GPT-5.5"):
        assert label in unimoral_scaling
    assert "OpenAI GPT-5 is the black S/M/L line across RQ1-RQ4" in unimoral_scaling
    assert "OpenAI GPT-5 is black and appears across RQ1-RQ4" in unimoral_scaling
    assert "GPT-5.5 is strongest inside GPT-5 on RQ2, RQ3, and both RQ4 metrics" in unimoral_scaling
    assert 'stroke="#000000"' in unimoral_scaling
    assert 'fill="#000000"' in unimoral_scaling
    for old_openai_color in ("#be123c", "#e11d48", "#fb7185"):
        assert old_openai_color not in unimoral_scaling
    assert "GPT-4o-mini as the only OpenAI reference" not in unimoral_scaling
    assert "other OpenAI rows stay in the broader text-comparison tables" not in unimoral_scaling

    unimoral_dashboard = (figure_dir / "option1_unimoral_four_task_dashboard.svg").read_text(encoding="utf-8")
    assert "OpenAI GPT-5 now has real RQ1-RQ4 UniMoral scores" in unimoral_dashboard
    assert "Llama-M still leads semantic RQ4 overall" in unimoral_dashboard

    unimoral_generation = (figure_dir / "option1_unimoral_generation_quality.svg").read_text(encoding="utf-8")
    assert "GPT-5.5 leads GPT-5 on RQ2 0.637, RQ3 0.601, and RQ4 METEOR 0.165" in unimoral_generation
    assert "GPT-5.5 reaches BERTScore 0.725" in unimoral_generation
    assert ">0.18<" in unimoral_generation

    for filename in ("option1_ccd_choice_distribution.svg", "option1_ccd_dominant_option_share.svg"):
        text = (figure_dir / filename).read_text(encoding="utf-8")
        for label in openai_rows:
            assert label in text
        assert "OpenAI GPT-5 rows are S/M/L" in text
        assert "GPT-4o/GPT-4.1 rows remain text-only refs" in text
        assert "OpenAI refs are one-off text-only rows" not in text


def test_write_root_readme_keeps_clean_landing_page_and_org_tail(tmp_path):
    repo_copy = tmp_path / "repo"
    script_copy = repo_copy / "scripts" / "build_release_artifacts.py"
    source_copy = repo_copy / "results" / "release" / "2026-04-19-option1" / "source" / "authoritative-summary.csv"
    benchmark_utils_copy = repo_copy / "src" / "inspect" / "evals" / "_benchmark_utils.py"

    script_copy.parent.mkdir(parents=True, exist_ok=True)
    source_copy.parent.mkdir(parents=True, exist_ok=True)
    benchmark_utils_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT, script_copy)
    shutil.copy2(SOURCE, source_copy)
    shutil.copy2(ROOT / "src" / "inspect" / "evals" / "_benchmark_utils.py", benchmark_utils_copy)
    (benchmark_utils_copy.parent / "__init__.py").write_text("", encoding="utf-8")
    (repo_copy / "README.md").write_text(
        "# CEI Moral-Psych Benchmark Suite\n\n"
        "Old generated surface.\n\n"
        "## Claude Code Slash Commands\n\n"
        "Keep org-owned tail.\n",
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(script_copy), "--write-root-readme"], check=True, cwd=repo_copy)

    root_readme = (repo_copy / "README.md").read_text(encoding="utf-8")
    assert root_readme.index("## Start Here") < root_readme.index("## What To Trust First")
    assert root_readme.index("## Start Here") < root_readme.index("## DATA, CLICK HERE: Result Tables")
    assert root_readme.index("## DATA, CLICK HERE: Result Tables") < root_readme.index("## What To Trust First")
    assert root_readme.index("## What To Trust First") < root_readme.index("## Key Takeaways")
    assert root_readme.index("## Key Takeaways") < root_readme.index("## Main Figures")
    assert "The main comparison uses three benchmark-faithful accuracy columns." in root_readme
    assert "**DATA, CLICK HERE:**" in root_readme
    assert "[unimoral-full-benchmark.csv](results/release/2026-04-19-option1/unimoral-full-benchmark.csv)" in root_readme
    assert "[smid-results.csv](results/release/2026-04-19-option1/smid-results.csv)" in root_readme
    assert "[value-kaleidoscope-results.csv](results/release/2026-04-19-option1/value-kaleidoscope-results.csv)" in root_readme
    assert "benchmark-comparison.csv" not in root_readme
    assert "`UniMoral action accuracy`" in root_readme
    assert "`SMID average accuracy`" in root_readme
    assert "`Value Kaleidoscope average`" in root_readme
    assert "`CCD-Bench` | Cultural-cluster choice distribution and concentration." in root_readme
    assert "`DeNEVIL` | FULCRA-backed proxy behavior categories from saved traces." in root_readme
    assert "The 6 OpenAI text-only rows are reference/calibration markers; they do not add SMID or DeNEVIL coverage." in root_readme
    assert "![UniMoral family-size scaling by RQ](figures/release/option1_unimoral_family_scaling.svg)" in root_readme
    assert "![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)" in root_readme
    assert "[Family scaling profile](figures/release/option1_family_scaling_profile.svg)" in root_readme
    assert "[CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)" in root_readme
    assert "[DeNEVIL behavior outcomes](figures/release/option1_denevil_behavior_outcomes.svg)" in root_readme
    assert "[Paper-vs-current replication map](figures/release/option1_paper_result_alignment_map.svg)" in root_readme
    assert "## Readiness Tiers" in root_readme
    assert "Current dashboard:" in root_readme
    assert "public summary rows are Tier 3" in root_readme
    assert "../../../figures/release" not in root_readme
    assert "## Benchmark Result Visuals" not in root_readme
    assert "## TL;DR" not in root_readme
    assert "## Claude Code Slash Commands" in root_readme
