from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path

from scripts import verify_unimoral_completion as verifier


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _set_tiny_verifier_constants(monkeypatch) -> None:
    tasks = {
        "unimoral_action_prediction": {"rq": "RQ1", "expected": 3, "metric": "accuracy"},
        "unimoral_moral_typology": {"rq": "RQ2", "expected": 2, "metric": "official_weighted_f1"},
    }
    monkeypatch.setattr(verifier, "MODEL_LINES", ["Line-A"])
    monkeypatch.setattr(verifier, "TASKS", tasks)
    monkeypatch.setattr(verifier, "PREDICTION_TASKS", {"unimoral_moral_typology": tasks["unimoral_moral_typology"]})
    monkeypatch.setattr(verifier, "EXPECTED_SAMPLE_PREDICTION_ROWS", 2)


def _write_success_eval(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("header.json", json.dumps({"status": "success"}) + "\n")


def _write_overview_metadata(release: Path, *, documented_incomplete: bool = False) -> None:
    total_samples = len(verifier.MODEL_LINES) * sum(task["expected"] for task in verifier.TASKS.values())
    families = list(
        dict.fromkeys(
            "GPT4 only" if line == "GPT4 only" else line.split("-", 1)[0]
            for line in verifier.MODEL_LINES
        )
    )
    mode = "benchmark_faithful; documented_incomplete" if documented_incomplete else "benchmark_faithful"
    _write_csv(
        release / "benchmark-summary.csv",
        [
            {
                "benchmark": "UniMoral",
                "task_types": len(verifier.TASKS),
                "evaluated_lines": len(verifier.MODEL_LINES) * len(verifier.TASKS),
                "models_covered": len(families),
                "samples": total_samples,
                "modes": mode,
            }
        ],
        ["benchmark", "task_types", "evaluated_lines", "models_covered", "samples", "modes"],
    )
    interpretation = (
        "Action prediction remains the original comparable UniMoral scalar; incomplete or parse-limited model-line cells are tracked in unimoral-failure-checklist.csv."
        if documented_incomplete
        else "Action prediction remains the original comparable UniMoral scalar; RQ2/RQ3/RQ4 expose the full model-line matrix."
    )
    _write_csv(
        release / "benchmark-catalog.csv",
        [
            {
                "benchmark": "UniMoral",
                "models_in_release": "; ".join(families),
                "samples_in_release": total_samples,
                "current_release_mode": mode,
                "repo_readout": "The release implements all four UniMoral task definitions.",
                "release_interpretation": interpretation,
            }
        ],
        ["benchmark", "models_in_release", "samples_in_release", "current_release_mode", "repo_readout", "release_interpretation"],
    )
    manifest_path = release / "release-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["benchmarks"] = [
            {
                "benchmark": "UniMoral",
                "task_types": len(verifier.TASKS),
                "evaluated_lines": len(verifier.MODEL_LINES) * len(verifier.TASKS),
                "models_covered": len(families),
                "samples": total_samples,
                "modes": mode,
            }
        ]
        manifest["counts"] = {
            "authoritative_tasks": len(verifier.MODEL_LINES) * len(verifier.TASKS),
            "benchmark_faithful_tasks": len(verifier.MODEL_LINES) * len(verifier.TASKS),
            "proxy_tasks": 0,
            "total_samples": total_samples,
        }
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")


def _write_minimal_complete_artifacts(root: Path) -> tuple[Path, Path]:
    release = root / "release"
    figures = root / "figures"
    release.mkdir(parents=True)
    figures.mkdir(parents=True)
    _write_overview_metadata(release)
    root.joinpath("README.md").write_text("The release now scores all four UniMoral tasks.\n", encoding="utf-8")
    release.joinpath("README.md").write_text("The release now scores all four UniMoral tasks.\n", encoding="utf-8")
    release.joinpath("jenny-group-report.md").write_text("The release now scores all four UniMoral tasks.\n", encoding="utf-8")
    release.joinpath("unimoral-minimax-resume-plan.md").write_text(
        "No MiniMax blockers are listed in the fixture failure checklist.\n",
        encoding="utf-8",
    )
    release.joinpath("unimoral-completion-audit.md").write_text(
        "# UniMoral Completion Audit\n\n"
        "Status: **achieved**.\n\n"
        "## Prompt-to-Artifact Checklist\n\n"
        "Strict completion is achieved in this fixture.\n\n"
        "| MiniMax is not run without explicit authorization | "
        "`make unimoral-missing-plan` | `make unimoral-missing-plan` is "
        "dry-run only; non-dry-run MiniMax lines require "
        "`UNIMORAL_ALLOW_MINIMAX=1`. | guarded |\n\n"
        "| Clean committed branch | `git status --short --branch`, "
        "`git rev-list --left-right --count HEAD...@{upstream}` | "
        "Post-generation check required: the final operator report must cite "
        "clean status and 0/0 ahead-behind after the last push. | external final check |\n\n"
        "No MiniMax provider calls are made by generating this audit.\n",
        encoding="utf-8",
    )

    for name in [
        "option1_unimoral_task_heatmap.svg",
        "option1_unimoral_task_rankings.svg",
        "option1_unimoral_task_spread.svg",
    ]:
        figures.joinpath(name).write_text("<svg></svg>\n", encoding="utf-8")

    _write_success_eval(root / "results" / "inspect" / "logs" / "example.eval")
    full_rows = []
    for line in verifier.MODEL_LINES:
        for task_name, task in verifier.TASKS.items():
            row = {
                "line_label": line,
                "family": line.split("-")[0],
                "size_slot": "",
                "task_name": task_name,
                "rq": task["rq"],
                "task_label": task_name,
                "primary_metric": task["metric"],
                "expected_samples": task["expected"],
                "completed_samples": task["expected"],
                "status": "complete",
                "accuracy": "0.5" if task_name != "unimoral_consequence_generation" else "",
                "official_weighted_f1": "0.5" if task["metric"] == "official_weighted_f1" else "",
                "bleu": "",
                "meteor": "0.1" if task["metric"] == "meteor" else "",
                "bert_score_f1": "",
                "rouge_l": "",
                "parsed_count": task["expected"],
                "log_path": "" if task_name == "unimoral_action_prediction" else "results/inspect/logs/example.eval",
            }
            full_rows.append(row)
    _write_csv(release / "unimoral-full-benchmark.csv", full_rows, list(full_rows[0]))

    coverage_rows = [
        {
            "rq": task["rq"],
            "task_name": task_name,
            "task_label": task_name,
            "status": "complete",
            "complete_model_lines": len(verifier.MODEL_LINES),
            "reported_model_lines": len(verifier.MODEL_LINES),
            "expected_model_lines": len(verifier.MODEL_LINES),
            "expected_samples_per_model": task["expected"],
        }
        for task_name, task in verifier.TASKS.items()
    ]
    _write_csv(release / "unimoral-coverage.csv", coverage_rows, list(coverage_rows[0]))
    spread_rows = [
        {
            "task_name": "unimoral_moral_typology",
            "task_label": "Moral typology",
            "model_lines": "1",
            "mean": "0.5",
            "min": "0.5",
            "max": "0.5",
            "range": "0.0",
            "diagnostic_read": "saturated",
        }
    ]
    _write_csv(release / "unimoral-task-spread.csv", spread_rows, list(spread_rows[0]))
    ranking_rows = [
        {
            "task_name": "unimoral_moral_typology",
            "task_label": "Moral typology",
            "rank": "1",
            "line_label": "Line-A",
            "metric": "official_weighted_f1",
            "value": "0.5",
        }
    ]
    _write_csv(release / "unimoral-model-rankings.csv", ranking_rows, list(ranking_rows[0]))
    _write_csv(
        release / "unimoral-sample-predictions.csv",
        [
            {
                "line_label": "Line-A",
                "family": "Line",
                "size_slot": "",
                "task_name": "unimoral_moral_typology",
                "rq": "RQ2",
                "sample_id": f"sample-{idx}",
                "language": "English",
                "scenario_id": str(idx),
                "target_json": '["answer"]',
                "prediction": "answer",
                "score_value": "1",
                "bert_score_f1": "",
                "answer_source": "visible",
                "source_log_dir": "results/inspect/logs",
                "source_log_count": "1",
            }
            for idx in range(verifier.PREDICTION_TASKS["unimoral_moral_typology"]["expected"])
        ],
        [
            "line_label",
            "family",
            "size_slot",
            "task_name",
            "rq",
            "sample_id",
            "language",
            "scenario_id",
            "target_json",
            "prediction",
            "score_value",
            "bert_score_f1",
            "answer_source",
            "source_log_dir",
            "source_log_count",
        ],
    )
    _write_csv(
        release / "unimoral-failure-checklist.csv",
        [],
        [
            "line_label",
            "task_name",
            "status",
            "completed_samples",
            "expected_samples",
            "parsed_count",
            "category",
            "reason",
            "next_action",
            "log_path",
        ],
    )
    release.joinpath("release-manifest.json").write_text(
        json.dumps(
            {
                "benchmarks": [
                    {
                        "benchmark": "UniMoral",
                        "task_types": len(verifier.TASKS),
                        "evaluated_lines": len(verifier.MODEL_LINES) * len(verifier.TASKS),
                        "models_covered": 1,
                        "samples": len(verifier.MODEL_LINES) * sum(task["expected"] for task in verifier.TASKS.values()),
                        "modes": "benchmark_faithful",
                    }
                ],
                "counts": {
                    "authoritative_tasks": len(verifier.MODEL_LINES) * len(verifier.TASKS),
                    "benchmark_faithful_tasks": len(verifier.MODEL_LINES) * len(verifier.TASKS),
                    "proxy_tasks": 0,
                    "total_samples": len(verifier.MODEL_LINES) * sum(task["expected"] for task in verifier.TASKS.values())
                },
                "entry_points": {
                    "unimoral_full_benchmark": "results/release/unimoral-full-benchmark.csv",
                    "unimoral_coverage": "results/release/unimoral-coverage.csv",
                    "unimoral_task_spread": "results/release/unimoral-task-spread.csv",
                    "unimoral_model_rankings": "results/release/unimoral-model-rankings.csv",
                    "unimoral_sample_predictions": "results/release/unimoral-sample-predictions.csv",
                    "unimoral_failure_checklist": "results/release/unimoral-failure-checklist.csv",
                    "unimoral_completion_audit": "results/release/unimoral-completion-audit.md",
                    "unimoral_minimax_resume_plan": "results/release/unimoral-minimax-resume-plan.md",
                    "unimoral_task_heatmap_figure": "figures/release/option1_unimoral_task_heatmap.svg",
                    "unimoral_task_rankings_figure": "figures/release/option1_unimoral_task_rankings.svg",
                    "unimoral_task_spread_figure": "figures/release/option1_unimoral_task_spread.svg",
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return release, figures


def test_unimoral_completion_verifier_passes_complete_artifacts(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    assert verifier.verify_release(release, figures, allow_incomplete=False) == []


def test_unimoral_completion_verifier_checks_branch_audit_contract(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    audit_path = release / "unimoral-completion-audit.md"
    audit_path.write_text(
        "# UniMoral Completion Audit\n\n"
        "Status: **achieved**.\n\n"
        "## Prompt-to-Artifact Checklist\n\n"
        "Strict completion is achieved in this fixture.\n\n"
        "No MiniMax provider calls are made by generating this audit.\n",
        encoding="utf-8",
    )

    errors = verifier.verify_release(release, figures, allow_incomplete=False)

    assert any("Clean committed branch" in error for error in errors)


def test_unimoral_completion_verifier_fails_incomplete_status(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    rows = list(csv.DictReader((release / "unimoral-full-benchmark.csv").open(newline="", encoding="utf-8")))
    rows[0]["status"] = "partial"
    rows[0]["completed_samples"] = "1"
    _write_csv(release / "unimoral-full-benchmark.csv", rows, list(rows[0]))

    errors = verifier.verify_release(release, figures, allow_incomplete=False)

    assert any("status=partial expected complete" in error for error in errors)
    assert any("completed_samples=1" in error for error in errors)


def test_unimoral_completion_verifier_allow_incomplete_skips_absent_raw_logs(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    for path in tmp_path.glob("results/inspect/logs/*.eval"):
        path.unlink()

    assert verifier.verify_release(release, figures, allow_incomplete=True) == []

    errors = verifier.verify_release(release, figures, allow_incomplete=False)

    assert any("status=unreadable expected success" in error for error in errors)


def test_unimoral_completion_verifier_allow_incomplete_keeps_structural_checks(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    _write_overview_metadata(release, documented_incomplete=True)

    rows = list(csv.DictReader((release / "unimoral-full-benchmark.csv").open(newline="", encoding="utf-8")))
    for row in rows:
        if row["task_name"] == "unimoral_moral_typology":
            row["status"] = "partial"
            row["completed_samples"] = "1"
            row["parsed_count"] = "1"
            row["accuracy"] = ""
    _write_csv(release / "unimoral-full-benchmark.csv", rows, list(rows[0]))
    coverage_rows = list(csv.DictReader((release / "unimoral-coverage.csv").open(newline="", encoding="utf-8")))
    for row in coverage_rows:
        if row["task_name"] == "unimoral_moral_typology":
            row["status"] = "incomplete"
            row["complete_model_lines"] = "0"
            row["reported_model_lines"] = "0"
    _write_csv(release / "unimoral-coverage.csv", coverage_rows, list(coverage_rows[0]))
    prediction_rows = list(csv.DictReader((release / "unimoral-sample-predictions.csv").open(newline="", encoding="utf-8")))
    _write_csv(release / "unimoral-sample-predictions.csv", prediction_rows[:1], list(prediction_rows[0]))
    _write_csv(
        release / "unimoral-failure-checklist.csv",
        [
            {
                "line_label": "Line-A",
                "task_name": "unimoral_moral_typology",
                "status": "partial",
                "completed_samples": "1",
                "expected_samples": "2",
                "parsed_count": "1",
                "category": "runtime",
                "reason": "fixture incomplete",
                "next_action": "rerun fixture",
                "log_path": "results/inspect/logs/example.eval",
            }
        ],
        [
            "line_label",
            "task_name",
            "status",
            "completed_samples",
            "expected_samples",
            "parsed_count",
            "category",
            "reason",
            "next_action",
            "log_path",
        ],
    )
    tmp_path.joinpath("README.md").write_text("current model-line matrix is not yet fully complete\n", encoding="utf-8")
    release.joinpath("unimoral-completion-audit.md").write_text(
        "# UniMoral Completion Audit\n\n"
        "Status: **not achieved**.\n\n"
        "## Prompt-to-Artifact Checklist\n\n"
        "Strict completion is blocked in this fixture.\n\n"
        "| MiniMax is not run without explicit authorization | "
        "`make unimoral-missing-plan` | `make unimoral-missing-plan` is "
        "dry-run only; non-dry-run MiniMax lines require "
        "`UNIMORAL_ALLOW_MINIMAX=1`. | guarded |\n\n"
        "| Clean committed branch | `git status --short --branch`, "
        "`git rev-list --left-right --count HEAD...@{upstream}` | "
        "Post-generation check required: the final operator report must cite "
        "clean status and 0/0 ahead-behind after the last push. | external final check |\n\n"
        "No MiniMax provider calls are made by generating this audit.\n",
        encoding="utf-8",
    )

    assert verifier.verify_release(release, figures, allow_incomplete=True) == []

    rows[0]["rq"] = "WRONG"
    _write_csv(release / "unimoral-full-benchmark.csv", rows, list(rows[0]))

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("has rq=WRONG" in error for error in errors)


def test_unimoral_completion_verifier_allow_incomplete_fails_duplicate_predictions(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    rows = list(csv.DictReader((release / "unimoral-sample-predictions.csv").open(newline="", encoding="utf-8")))
    rows.append(dict(rows[0]))
    _write_csv(release / "unimoral-sample-predictions.csv", rows, list(rows[0]))

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("contains duplicate line/task/sample rows" in error for error in errors)


def test_unimoral_completion_verifier_allow_incomplete_requires_failure_checklist_row(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    _write_overview_metadata(release, documented_incomplete=True)

    rows = list(csv.DictReader((release / "unimoral-full-benchmark.csv").open(newline="", encoding="utf-8")))
    for row in rows:
        if row["task_name"] == "unimoral_moral_typology":
            row["status"] = "partial"
            row["completed_samples"] = "1"
    _write_csv(release / "unimoral-full-benchmark.csv", rows, list(rows[0]))

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("incomplete model-task rows missing from failure checklist" in error for error in errors)


def test_unimoral_completion_verifier_validates_failure_checklist_detail(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    _write_overview_metadata(release, documented_incomplete=True)

    rows = list(csv.DictReader((release / "unimoral-full-benchmark.csv").open(newline="", encoding="utf-8")))
    for row in rows:
        if row["task_name"] == "unimoral_moral_typology":
            row["status"] = "partial"
            row["completed_samples"] = "1"
    _write_csv(release / "unimoral-full-benchmark.csv", rows, list(rows[0]))
    failure_rows = [
        {
            "line_label": "Line-A",
            "task_name": "unimoral_moral_typology",
            "status": "partial",
            "completed_samples": "2",
            "expected_samples": "2",
            "parsed_count": "2",
            "category": "unknown",
            "reason": "",
            "next_action": "rerun fixture",
            "log_path": "results/inspect/logs/example.eval",
        }
    ]
    _write_csv(release / "unimoral-failure-checklist.csv", failure_rows, list(failure_rows[0]))

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("failure checklist completed_samples='2' does not match benchmark row '1'" in error for error in errors)
    assert any("failure checklist category='unknown' is not recognized" in error for error in errors)
    assert any("failure checklist missing reason" in error for error in errors)


def test_unimoral_completion_verifier_requires_minimax_safety_wording(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    monkeypatch.setattr(verifier, "MODEL_LINES", ["MiniMax-S"])
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    _write_overview_metadata(release, documented_incomplete=True)

    rows = list(csv.DictReader((release / "unimoral-full-benchmark.csv").open(newline="", encoding="utf-8")))
    for row in rows:
        if row["task_name"] == "unimoral_moral_typology":
            row["status"] = "partial"
            row["completed_samples"] = "1"
            row["parsed_count"] = "1"
    _write_csv(release / "unimoral-full-benchmark.csv", rows, list(rows[0]))
    failure_rows = [
        {
            "line_label": "MiniMax-S",
            "task_name": "unimoral_moral_typology",
            "status": "partial",
            "completed_samples": "1",
            "expected_samples": "2",
            "parsed_count": "1",
            "category": "runtime",
            "reason": "fixture incomplete",
            "next_action": "rerun fixture",
            "log_path": "results/inspect/logs/example.eval",
        }
    ]
    _write_csv(release / "unimoral-failure-checklist.csv", failure_rows, list(failure_rows[0]))

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("next_action missing MiniMax safety phrase: 'make unimoral-missing-plan'" in error for error in errors)
    assert any("next_action missing MiniMax safety phrase: 'MiniMax explicitly allowed'" in error for error in errors)
    assert any("next_action missing MiniMax safety phrase: 'UNIMORAL_ALLOW_MINIMAX=1'" in error for error in errors)
    assert any("next_action missing MiniMax safety phrase: 'OPENROUTER_API_KEY'" in error for error in errors)


def test_unimoral_completion_verifier_checks_manifest_paths(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    manifest = json.loads((release / "release-manifest.json").read_text(encoding="utf-8"))
    manifest["entry_points"]["unimoral_task_heatmap_figure"] = "figures/release/missing.svg"
    (release / "release-manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("unimoral_task_heatmap_figure points to missing artifact" in error for error in errors)


def test_unimoral_completion_verifier_requires_minimax_resume_plan_manifest_entry(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    manifest = json.loads((release / "release-manifest.json").read_text(encoding="utf-8"))
    del manifest["entry_points"]["unimoral_minimax_resume_plan"]
    (release / "release-manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("release-manifest.json missing entry_points.unimoral_minimax_resume_plan" in error for error in errors)


def test_unimoral_completion_verifier_checks_minimax_resume_plan_content(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    (release / "unimoral-minimax-resume-plan.md").write_text(
        "# UniMoral MiniMax Resume Plan\n\nMiniMax reruns are pending.\n",
        encoding="utf-8",
    )

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("unimoral-minimax-resume-plan.md missing required phrase" in error for error in errors)
    assert any("without granting permission to run MiniMax" in error for error in errors)


def test_unimoral_completion_verifier_checks_required_csv_columns(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    rows = list(csv.DictReader((release / "unimoral-failure-checklist.csv").open(newline="", encoding="utf-8")))
    _write_csv(release / "unimoral-failure-checklist.csv", rows, ["line_label", "task_name"])

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("unimoral-failure-checklist.csv missing required columns" in error for error in errors)


def test_unimoral_completion_verifier_checks_overview_metadata(tmp_path, monkeypatch):
    _set_tiny_verifier_constants(monkeypatch)
    release, figures = _write_minimal_complete_artifacts(tmp_path)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)

    summary_rows = list(csv.DictReader((release / "benchmark-summary.csv").open(newline="", encoding="utf-8")))
    summary_rows[0]["samples"] = "10"
    _write_csv(release / "benchmark-summary.csv", summary_rows, list(summary_rows[0]))
    catalog_rows = list(csv.DictReader((release / "benchmark-catalog.csv").open(newline="", encoding="utf-8")))
    catalog_rows[0]["models_in_release"] = "Stale"
    catalog_rows[0]["current_release_mode"] = "stale"
    catalog_rows[0]["repo_readout"] = "old"
    _write_csv(release / "benchmark-catalog.csv", catalog_rows, list(catalog_rows[0]))
    manifest = json.loads((release / "release-manifest.json").read_text(encoding="utf-8"))
    manifest["benchmarks"][0]["task_types"] = 1
    manifest["benchmarks"][0]["samples"] = 10
    manifest["counts"]["authoritative_tasks"] = 1
    manifest["counts"]["total_samples"] = 10
    (release / "release-manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    errors = verifier.verify_release(release, figures, allow_incomplete=True)

    assert any("benchmark-summary.csv UniMoral samples='10'" in error for error in errors)
    assert any("benchmark-catalog.csv UniMoral models_in_release='Stale'" in error for error in errors)
    assert any("benchmark-catalog.csv UniMoral current_release_mode='stale'" in error for error in errors)
    assert any("repo_readout does not mention all four task definitions" in error for error in errors)
    assert any("release-manifest.json UniMoral task_types=1" in error for error in errors)
    assert any("release-manifest.json UniMoral samples=10" in error for error in errors)
    assert any("release-manifest.json counts.authoritative_tasks=1" in error for error in errors)
