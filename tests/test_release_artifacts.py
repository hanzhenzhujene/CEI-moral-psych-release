"""Regression checks for the tracked Option 1 release build."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_release_artifacts import build_axis_ticks, nice_tick_step

SCRIPT = ROOT / "scripts" / "build_release_artifacts.py"
SOURCE = ROOT / "results" / "release" / "2026-04-19-option1" / "source" / "authoritative-summary.csv"


def test_axis_tick_helpers_stay_nonzero_for_minimal_clean_state():
    assert nice_tick_step(1, target_ticks=4) == 1
    ticks, upper = build_axis_ticks(1, target_ticks=4)
    assert ticks == [0, 1, 2, 3, 4]
    assert upper == 1


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
        "ccd-choice-distribution.csv",
        "denevil-behavior-summary.csv",
        "denevil-prompt-family-breakdown.csv",
        "denevil-proxy-summary.csv",
        "denevil-proxy-examples.csv",
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
        "option1_ccd_valid_choice_coverage.svg",
        "option1_ccd_choice_distribution.svg",
        "option1_ccd_dominant_option_share.svg",
        "option1_denevil_behavior_outcomes.svg",
        "option1_denevil_prompt_family_heatmap.svg",
        "option1_denevil_proxy_status_matrix.svg",
        "option1_denevil_proxy_sample_volume.svg",
        "option1_denevil_proxy_valid_response_rate.svg",
        "option1_denevil_proxy_pipeline.svg",
        "option1_sample_volume.svg",
    }
    actual_figures = {path.name for path in figure_dir.glob("*.svg")}
    assert expected_figures == actual_figures
    for figure_name in expected_figures:
        assert (figure_dir / figure_name).stat().st_size > 0

    manifest = json.loads((release_dir / "release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["authoritative_tasks"] == 19
    assert manifest["counts"]["proxy_tasks"] == 3
    assert any("Denevil" in item for item in manifest["interpretation_guardrails"])
    assert manifest["report_metadata"]["owner"] == "Jenny Zhu"
    assert manifest["report_metadata"]["current_cost_estimate"] == "$84.02"
    assert "later tracked reruns completed in this repo" in manifest["report_metadata"]["current_cost_scope"]
    assert manifest["report_metadata"]["metric_definition_version"] == "2026-04-30"
    assert "stricter visible-answer parsing" in manifest["report_metadata"]["metric_definition_summary"].lower()
    assert manifest["report_metadata"]["ci_workflow_url"].endswith("/actions/workflows/ci.yml")
    assert manifest["target_matrix"]["family_size_benchmark_cells"] == 60
    assert manifest["target_matrix"]["model_families"] == 4
    assert manifest["model_families"] == ["Qwen", "DeepSeek", "Llama", "Gemma"]
    assert manifest["entry_points"]["report"].endswith("jenny-group-report.md")
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
    assert "family-scaling-summary.csv" in manifest["tables"]
    assert "ccd-choice-distribution.csv" in manifest["tables"]
    assert "denevil-proxy-summary.csv" in manifest["tables"]
    assert "denevil-behavior-summary.csv" in manifest["tables"]
    assert "denevil-prompt-family-breakdown.csv" in manifest["tables"]
    assert "denevil-proxy-examples.csv" in manifest["tables"]
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
    assert len(rows) in {10, 11}
    assert not any(row["line_label"].startswith("MiniMax-") for row in rows)
    rows_by_line = {row["line_label"]: row for row in rows}
    assert any(
        row["line_label"] == "Gemma-L"
        and row["unimoral_action_accuracy"] == "0.661088"
        and row["smid_average_accuracy"] == "0.412275"
        and row["value_average_accuracy"] == "0.655987"
        and row["comparison_note"] == "Comparable on all three benchmark-faithful accuracy panels."
        for row in rows
    )
    assert any(
        row["line_label"] == "Llama-L"
        and row["smid_average_accuracy"] == "0.386093"
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
        and row["smid_average_accuracy"] == "0.482829"
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
    deepseek_medium = rows_by_line.get("DeepSeek-M")
    if deepseek_medium is not None:
        assert deepseek_medium["unimoral_action_accuracy"] == ""
        assert deepseek_medium["smid_average_accuracy"] == ""
        assert deepseek_medium["value_average_accuracy"] == ""
        assert (
            deepseek_medium["comparison_note"]
            == "Coverage-only line; accuracy withheld after visible-answer validation."
        )

    with (release_dir / "ccd-choice-distribution.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None
        assert "option_1_pct" in reader.fieldnames
        assert "option_10_pct" in reader.fieldnames
        assert "dominant_option" in reader.fieldnames
        assert "dominant_option_share" in reader.fieldnames
        assert "distribution_status" in reader.fieldnames
        ccd_distribution_rows = list(reader)
    assert len(ccd_distribution_rows) == 12
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
    assert any(
        row["line_label"] == "DeepSeek-S"
        and row["route"] == "No distinct small OpenRouter route exposed"
        and row["valid_selection_count"] == "n/a"
        and row["valid_selection_rate"] == "n/a"
        and row["dominant_option"] == "n/a"
        and row["distribution_status"] == "missing_route"
        for row in ccd_distribution_rows
    )
    ccd_rows_by_line = {row["line_label"]: row for row in ccd_distribution_rows}
    deepseek_medium_ccd = ccd_rows_by_line["DeepSeek-M"]
    assert deepseek_medium_ccd["dominant_option"] == "n/a"
    assert deepseek_medium_ccd["dominant_option_share"] == "n/a"
    assert deepseek_medium_ccd["effective_cluster_count"] == "n/a"
    if deepseek_medium_ccd["distribution_status"] == "no_valid_visible_choices":
        assert deepseek_medium_ccd["valid_selection_count"] == "0"
        assert deepseek_medium_ccd["valid_selection_rate"] == "0.000000"
    else:
        assert deepseek_medium_ccd["valid_selection_count"] == "n/a"
        assert deepseek_medium_ccd["valid_selection_rate"] == "n/a"
        assert deepseek_medium_ccd["distribution_status"] == "missing_eval_samples"
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
    assert len(denevil_proxy_rows) == 12
    denevil_proxy_by_line = {row["model_line"]: row for row in denevil_proxy_rows}
    assert any(
        row["model_line"] == "DeepSeek-S"
        and row["proxy_status"] == "No route"
        and row["total_proxy_samples"] == "n/a"
        and row["generated_response_count"] == "n/a"
        and row["valid_response_rate"] == "n/a"
        and row["persisted_checkpoint_pct"] == "n/a"
        and row["latest_successful_eval_created_at"] == "n/a"
        and row["latest_proxy_artifact_updated_at"] == "n/a"
        and row["route_short_label"] == "no-route"
        and row["limitation_flag"] == "missing_route"
        for row in denevil_proxy_rows
    )
    deepseek_medium_proxy = denevil_proxy_by_line["DeepSeek-M"]
    assert deepseek_medium_proxy["route_short_label"] == "deepseek-r1-distill-llama-70b"
    if deepseek_medium_proxy["proxy_status"] == "Proxy complete":
        assert deepseek_medium_proxy["total_proxy_samples"] == "20518"
        assert deepseek_medium_proxy["generated_response_count"] == "2863"
        assert deepseek_medium_proxy["valid_response_rate"] == "0.139536"
        assert deepseek_medium_proxy["persisted_checkpoint_pct"] == "100.000000"
        assert deepseek_medium_proxy["limitation_flag"] == "low_visible_response_rate"
        assert "saved-answer surfacing failure" in deepseek_medium_proxy["notes"].lower()
    else:
        assert deepseek_medium_proxy["proxy_status"] == "Queued"
        assert deepseek_medium_proxy["total_proxy_samples"] == "n/a"
        assert deepseek_medium_proxy["generated_response_count"] == "n/a"
        assert deepseek_medium_proxy["valid_response_rate"] == "n/a"
        assert deepseek_medium_proxy["persisted_checkpoint_pct"] == "n/a"
        assert deepseek_medium_proxy["limitation_flag"] == "missing_proxy_artifact"
    qwen_small_proxy = denevil_proxy_by_line["Qwen-S"]
    if qwen_small_proxy["generated_response_count"] != "n/a":
        assert qwen_small_proxy["generated_response_count"] == "20515"
        assert qwen_small_proxy["valid_response_rate"] == "0.999854"
        assert qwen_small_proxy["persisted_checkpoint_pct"] == "100.000000"
    else:
        assert qwen_small_proxy["limitation_flag"] == "missing_proxy_artifact"

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
    assert len(denevil_behavior_rows) == 12
    denevil_behavior_by_line = {row["model_line"]: row for row in denevil_behavior_rows}
    assert any(
        row["model_line"] == "DeepSeek-S"
        and row["behavior_status"] == "missing_route"
        and row["dominant_behavior"] == "n/a"
        and row["total_proxy_samples"] == "n/a"
        and row["protective_refusal_count"] == "n/a"
        and row["protective_refusal_rate"] == "n/a"
        for row in denevil_behavior_rows
    )
    deepseek_medium_behavior = denevil_behavior_by_line["DeepSeek-M"]
    if deepseek_medium_behavior["behavior_status"] == "ok":
        assert deepseek_medium_behavior["total_proxy_samples"] == "20518"
        assert deepseek_medium_behavior["protective_response_rate"] == "12.793645"
        assert deepseek_medium_behavior["no_visible_answer_rate"] == "86.046398"
        assert deepseek_medium_behavior["potentially_risky_continuation_rate"] == "0.024369"
        assert deepseek_medium_behavior["dominant_behavior"] == "No visible answer"
        assert (
            "incomplete surfacing rather than a low ethical-quality score"
            in deepseek_medium_behavior["limitation_note"].lower()
        )
    else:
        assert deepseek_medium_behavior["behavior_status"] == "missing_eval_samples"
        assert deepseek_medium_behavior["total_proxy_samples"] == "n/a"
        assert deepseek_medium_behavior["protective_response_rate"] == "n/a"
        assert deepseek_medium_behavior["dominant_behavior"] == "n/a"
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
    assert len(denevil_prompt_family_rows) == 72
    prompt_family_by_key = {
        (row["model_line"], row["prompt_family"]): row for row in denevil_prompt_family_rows
    }
    assert any(
        row["model_line"] == "DeepSeek-S"
        and row["prompt_family"] == "Illicit access / sabotage"
        and row["prompt_count"] == "n/a"
        and row["protective_response_rate"] == "n/a"
        and row["dominant_behavior"] == "n/a"
        for row in denevil_prompt_family_rows
    )
    deepseek_medium_prompt_family = prompt_family_by_key[
        ("DeepSeek-M", "Loaded social / political judgment")
    ]
    if deepseek_medium_prompt_family["prompt_count"] == "n/a":
        assert deepseek_medium_prompt_family["protective_response_rate"] == "n/a"
        assert deepseek_medium_prompt_family["empty_response_rate"] == "n/a"
        assert deepseek_medium_prompt_family["dominant_behavior"] == "n/a"
    else:
        assert deepseek_medium_prompt_family["protective_response_rate"] == "3.333333"
        assert deepseek_medium_prompt_family["empty_response_rate"] == "96.666667"
        assert deepseek_medium_prompt_family["dominant_behavior"] == "No visible answer"
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
    deepseek_medium_examples = [
        row for row in denevil_example_rows if row["model_line"] == "DeepSeek-M"
    ]
    if deepseek_medium_examples:
        assert any(
            row["shortened_model_output_pattern"] == "No visible answer"
            and "subset of traces that actually surface a visible public answer"
            in row["interpretable_signal"].lower()
            for row in deepseek_medium_examples
        )

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
        and "Only the large line remains accuracy-comparable on the family scaling view" in row["evidence_scope"]
        and "CCD-Bench" not in row["numeric_pattern"]
        and "Denevil" not in row["numeric_pattern"]
        and "cannot support a trustworthy accuracy size curve" in row["interpretation"]
        for row in scaling_rows
    )

    report_text = (release_dir / "jenny-group-report.md").read_text(encoding="utf-8")
    release_readme = (release_dir / "README.md").read_text(encoding="utf-8")
    topline_summary = (release_dir / "topline-summary.md").read_text(encoding="utf-8")
    for text in (report_text, release_readme):
        assert "## TL;DR" in text
        assert "Best like-for-like line" in text
        assert "Best text-only line" in text
        assert "The hardest benchmark is SMID" in text
        assert "There is no universal scaling law" in text
        if "CCD-Bench shows cultural choice style, not accuracy" in text:
            assert "`Gemma-L` at 17.6% to `Llama-S` at 23.9%" in text
        if "DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring" in text:
            assert "92.4% to 99.5% protective response rate" in text
            assert "86.0% of prompts surfaced no visible answer" in text
        assert "## Results First" in text
        assert "## Benchmark Result Visuals" in text
        assert "### 1. UniMoral / SMID / Value Kaleidoscope: topline comparable accuracy" in text
        assert "### 2. UniMoral / SMID / Value Kaleidoscope: family-size scaling" in text
        assert "### 3. CCD-Bench: cultural-cluster choice behavior" in text
        assert "### 4. CCD-Bench: dominant-option concentration" in text
        assert "### 5. DeNEVIL: proxy behavioral outcomes" in text
        assert "## Interpretation" in text
        assert "### Interpretation At A Glance" in text
        assert "### Benchmark Reading Guide" in text
        assert "### Benchmark Difficulty Profile" in text
        assert "### Family Scaling Profile" in text
        assert "### CCD-Bench Choice Behavior" in text
        assert "### DeNEVIL Proxy Behavioral Evidence" in text
        assert "### DeNEVIL Appendix QA / Provenance" in text
        assert "### Reporting Guardrails" in text
        assert "These benchmarks do not all ask for the same kind of moral competence" in text
        assert "### Latest Family-Size Progress Snapshot" in text
        assert "Metric definition version: `2026-04-30`." in text
        assert "Strongest fully observed comparable line | `Qwen-L` averages 0.600" in text
        assert "Strongest text-only comparable line | `Llama-M` reaches UniMoral 0.670 and Value 0.724" in text
        assert "Keep `DeepSeek-M` out of the top-row comparable accuracy charts" in text
        assert "CCD-Bench should not be flattened into a universal accuracy number." in text
        assert "The repo still lacks a stable local `MoralPrompt` export" in text
        assert "paper-aligned APV / EVR / MVP are `n/a`" in text
        assert "headline DeNEVIL behavioral-outcomes chart already appears above" in text
        assert "ccd-choice-distribution.csv" in text
        assert "option1_ccd_valid_choice_coverage.svg" in text
        assert "option1_ccd_choice_distribution.svg" in text
        assert "option1_ccd_dominant_option_share.svg" in text
        assert "option1_denevil_behavior_outcomes.svg" in text
        assert "option1_family_scaling_profile.svg" in text
        assert "option1_denevil_prompt_family_heatmap.svg" in text
        assert "option1_denevil_proxy_status_matrix.svg" in text
        assert "option1_denevil_proxy_sample_volume.svg" in text
        assert "option1_denevil_proxy_valid_response_rate.svg" in text
        assert "option1_denevil_proxy_pipeline.svg" in text
        assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in text
        assert "Current project cost estimate" in text
        assert "Cost scope" in text
        assert "Current cost to date" not in text
        assert "24634450927" not in text
        assert "`MiniMax`" not in text
        assert "| `MiniMax-S` |" not in text
        assert "| `MiniMax-M` |" not in text
        assert "| `MiniMax-L` |" not in text
        assert "headline family-scaling figure already appears above" in text
        assert "Read `CCD-Bench` in its dedicated choice-behavior figures" in text
        assert "Read `Denevil` only through the dedicated proxy evidence package." in text
        assert "## Interpretation Notes" not in text
        assert text.count("![Comparable accuracy bars]") == 1
        assert text.count("![Family scaling profile]") == 1
        assert text.count("![CCD choice distribution]") == 1
        assert text.count("![CCD dominant-option share]") == 1
        assert text.count("![DeNEVIL proxy behavioral outcomes]") == 1
        assert "without re-embedding the same chart" in text
        assert "without duplicating the same graphics" in text

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
    assert "![Coverage matrix]" in report_text
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | --- |" in report_text

    assert "## Local Expansion Checkpoint" in release_readme
    assert "| `Next queued text lines` | Done | No currently published line remains queued behind an active rerun. |" in release_readme
    assert "sample volume chart" in release_readme
    assert "benchmark difficulty profile" in release_readme
    assert "family scaling profile" in release_readme
    assert "## Start Here" in release_readme
    assert "## Benchmark Result Visuals" in release_readme
    assert "## Status Key" in release_readme
    assert "## Supporting Figures" in release_readme
    assert "option1_family_size_progress_overview.svg" in release_readme
    assert "option1_benchmark_difficulty_profile.svg" in release_readme
    assert "option1_family_scaling_profile.svg" in release_readme
    assert "Partial" in release_readme
    assert "Model families in scope" in release_readme
    assert "Done" in release_readme
    assert "denevil-proxy-summary.csv" in release_readme
    assert "denevil-behavior-summary.csv" in release_readme
    assert "denevil-prompt-family-breakdown.csv" in release_readme
    assert "denevil-proxy-examples.csv" in release_readme

    assert "## TL;DR" in topline_summary
    assert "## Frozen Snapshot Scope" in topline_summary
    assert "Best like-for-like line" in topline_summary
    if "CCD-Bench shows cultural choice style, not accuracy" in topline_summary:
        assert "Llama-S" in topline_summary
    if "DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring" in topline_summary:
        assert "DeepSeek-M" in topline_summary
    assert "For the full public package, move next to `README.md`" in topline_summary

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
    assert "Three comparable benchmark panels only: UniMoral, SMID, and Value Kaleidoscope." in family_scaling_svg
    assert "This figure is reserved for benchmark-faithful comparable accuracy, not CCD coverage or Denevil proxy evidence." in family_scaling_svg
    assert "#4 CCD-Bench" not in family_scaling_svg
    assert "#5 Denevil" not in family_scaling_svg
    assert "100% coverage" not in family_scaling_svg
    assert "67% coverage" not in family_scaling_svg
    assert "33% coverage" not in family_scaling_svg
    assert "0% coverage" not in family_scaling_svg
    assert "Read CCD-Bench in Figures 5-7." in family_scaling_svg
    assert "Read Denevil in Figures 8-11." in family_scaling_svg
    assert "Proxy-only coverage and traceability evidence;" in family_scaling_svg
    assert "MoralPrompt unavailable; not benchmark-faithful" in family_scaling_svg
    assert "DeepSeek-L" in family_scaling_svg
    assert "Takeaway: current evidence supports task-specific scaling statements" in family_scaling_svg
    assert "Qwen: text scored at S/M/L; SMID at S/L." in family_scaling_svg
    assert "Llama: text scored at S/M/L; SMID at S/L." in family_scaling_svg
    assert "DeepSeek: only L is scored up top; M is read in CCD / Denevil figures." in family_scaling_svg
    assert "Gemma: full S/M/L scored sweep." in family_scaling_svg
    assert "Only the small line is currently comparable." not in family_scaling_svg

    ccd_coverage_svg = (figure_dir / "option1_ccd_valid_choice_coverage.svg").read_text(encoding="utf-8")
    assert "Appendix QA: CCD-Bench valid-choice coverage, not accuracy." in ccd_coverage_svg
    assert "Appendix QA only." in ccd_coverage_svg
    assert "parseable integer in 1-10" in ccd_coverage_svg
    assert "Hatched rows are missing (`n/a`) rather than zero." in ccd_coverage_svg
    assert "n/a — no released CCD route" in ccd_coverage_svg
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
    assert "no valid visible CCD selections" in ccd_dominant_share_svg
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
    assert "No route" in denevil_status_matrix_svg
    assert "SAMPLE COUNT" in denevil_status_matrix_svg
    assert "GENERATED RESPONSES" in denevil_status_matrix_svg
    assert "VALID RESPONSE RATE" in denevil_status_matrix_svg
    assert "ROUTE / MODEL" in denevil_status_matrix_svg
    assert "NOTES" in denevil_status_matrix_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_status_matrix_svg
    assert "DeepSeek-M is the key cautionary row" in denevil_status_matrix_svg
    assert "traceability / surfacing gap" in denevil_status_matrix_svg

    denevil_sample_volume_svg = (figure_dir / "option1_denevil_proxy_sample_volume.svg").read_text(encoding="utf-8")
    assert "Appendix QA: DeNEVIL proxy sample volume" in denevil_sample_volume_svg
    assert "Appendix QA / provenance only." in denevil_sample_volume_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_sample_volume_svg
    if "visible 20,515 / 20,518" in denevil_sample_volume_svg:
        assert "visible 2,863 / 20,518" in denevil_sample_volume_svg
    assert "n/a — no released Denevil proxy route" in denevil_sample_volume_svg

    denevil_valid_rate_svg = (figure_dir / "option1_denevil_proxy_valid_response_rate.svg").read_text(encoding="utf-8")
    assert "Appendix QA: DeNEVIL proxy visible-response coverage" in denevil_valid_rate_svg
    assert "Appendix QA / provenance only." in denevil_valid_rate_svg
    assert "High bars mean stronger public traceability coverage, not stronger benchmark-faithful ethical quality." in denevil_valid_rate_svg
    assert "Proxy-only coverage and traceability evidence; MoralPrompt unavailable; not benchmark-faithful ethical-quality scoring." in denevil_valid_rate_svg
    assert "n/a — no released Denevil proxy route" in denevil_valid_rate_svg
    assert "DeepSeek-M stays low not because the public release proved low ethical quality" in denevil_valid_rate_svg
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
