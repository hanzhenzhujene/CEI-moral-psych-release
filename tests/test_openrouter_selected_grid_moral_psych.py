"""Regression checks for the selected-grid OpenRouter moral-psych pipeline."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from scripts import openrouter_selected_grid_moral_psych as openrouter

ROOT = Path(__file__).parent.parent


def _model_metadata(input_price_per_m: float, output_price_per_m: float) -> dict[str, object]:
    return {
        "pricing": {
            "prompt": str(input_price_per_m / 1_000_000),
            "completion": str(output_price_per_m / 1_000_000),
        },
        "context_length": 8192,
    }


def _minimal_model_rows() -> list[dict[str, object]]:
    return [
        {
            "model": "qwen/qwen3-8b",
            "family": "Qwen",
            "size_tier": "S/8B",
            "release_period": "2025-Q2",
            "grid": "within-family scaling",
            "eligible": True,
            "available": True,
            "existing_baseline": False,
            "input_price_per_m": "0.05",
            "output_price_per_m": "0.4",
        }
    ]


def _minimal_plan_rows() -> list[dict[str, object]]:
    return [
        {
            "model": "qwen/qwen3-8b",
            "benchmark": "UniMoral",
            "task": "unimoral_action_prediction",
            "estimated_cost_usd": "0.10",
        },
        {
            "model": "qwen/qwen3-8b",
            "benchmark": "ValuePrism",
            "task": "value_prism_relevance",
            "estimated_cost_usd": "0.05",
        },
        {
            "model": "qwen/qwen3-8b",
            "benchmark": "CCD-Bench",
            "task": "ccd_bench_selection",
            "estimated_cost_usd": "0.02",
        },
    ]


def test_openrouter_pipeline_scope_excludes_forbidden_benchmarks_and_minimax() -> None:
    assert {spec.benchmark for spec in openrouter.TASK_SPECS} == {"UniMoral", "ValuePrism", "CCD-Bench"}
    assert all("smid" not in spec.task_name.lower() for spec in openrouter.TASK_SPECS)
    assert all("denevil" not in spec.task_name.lower() for spec in openrouter.TASK_SPECS)
    assert all("minimax" not in spec.model_id.lower() for spec in openrouter.MODEL_SPECS)
    assert {"within-family scaling", "time scaling"}.issubset({spec.grid for spec in openrouter.MODEL_SPECS})


def test_openrouter_price_caps_skip_non_baseline_models_but_allow_existing_baselines() -> None:
    models_by_id = {
        spec.model_id: _model_metadata(0.1, 0.1)
        for spec in openrouter.MODEL_SPECS
    }
    models_by_id["qwen/qwen3-32b"] = _model_metadata(4.0, 0.1)
    models_by_id["qwen/qwen3-8b"] = _model_metadata(4.0, 16.0)

    rows = {row["model"]: row for row in openrouter.eligible_models(models_by_id)}

    assert rows["qwen/qwen3-32b"]["eligible"] is False
    assert rows["qwen/qwen3-32b"]["skip_reason"] == "price cap"
    assert rows["qwen/qwen3-8b"]["eligible"] is True
    assert rows["qwen/qwen3-8b"]["existing_baseline"] is True


def test_completion_audit_marks_sample_limited_live_run_as_partial(tmp_path: Path) -> None:
    plan_rows = _minimal_plan_rows()
    result_rows = [
        {
            **row,
            "run_status": "success",
            "actual_cost_usd": "0.01",
            "completed_samples": "100",
            "reasoning_tokens_actual": "0",
        }
        for row in plan_rows
    ]

    openrouter.write_completion_audit(tmp_path, 100, _minimal_model_rows(), plan_rows, result_rows)

    content = (tmp_path / "completion_audit.md").read_text(encoding="utf-8")
    assert "Evidence level: `live run complete`." in content
    assert "Full-objective status: Bounded sample-100 evidence only" in content
    assert "| Run selected models on the three allowed benchmarks | All `3` recorded model-task rows completed with `success`. | partial |" in content
    assert "## Approved Full-Run Command" in content
    assert "OPENROUTER_FULL_RUN_DRY_RUN=1 scripts/run_openrouter_selected_grid_full.sh" in content
    assert "OPENROUTER_FULL_RUN_APPROVED=1 scripts/run_openrouter_selected_grid_full.sh" in content
    assert "Do not treat the bounded pilot as the full benchmark" in content


def test_completion_audit_marks_full_plan_as_not_yet_run(tmp_path: Path) -> None:
    plan_rows = _minimal_plan_rows()

    openrouter.write_completion_audit(tmp_path, None, _minimal_model_rows(), plan_rows)

    content = (tmp_path / "completion_audit.md").read_text(encoding="utf-8")
    assert "Evidence level: `plan only`." in content
    assert "Full-objective status: Planned, not yet run." in content
    assert "| Output model/family/size/release/benchmark/score/cost/replication tables | `benchmark_map.csv`, `model_grid.csv`, and `run_plan.csv` are present; scored result tables are created only after live rows exist. | planned only |" in content
    assert "Run only after explicit approval for the full selected-grid OpenRouter spend." in content
    assert "OPENROUTER_FULL_RUN_APPROVED=1 scripts/run_openrouter_selected_grid_full.sh" in content
    assert "Do not treat this plan as completed benchmark evidence." in content


def test_completion_audit_marks_full_attempt_with_blocked_cells(tmp_path: Path) -> None:
    plan_rows = _minimal_plan_rows()
    result_rows = [
        {
            **plan_rows[0],
            "run_status": "success",
            "actual_cost_usd": "0.01",
            "completed_samples": "8784",
            "reasoning_tokens_actual": "0",
        },
        {
            **plan_rows[1],
            "run_status": "error",
            "actual_cost_usd": "0.02",
            "completed_samples": "",
            "reasoning_tokens_actual": "10",
            "error": "provider route blocked",
        },
        {
            **plan_rows[2],
            "run_status": "cancelled",
            "actual_cost_usd": "0.03",
            "completed_samples": "",
            "reasoning_tokens_actual": "20",
            "error": "stale route",
        },
    ]

    openrouter.write_completion_audit(tmp_path, None, _minimal_model_rows(), plan_rows, result_rows)

    content = (tmp_path / "completion_audit.md").read_text(encoding="utf-8")
    assert "Evidence level: `full selected-grid attempted with blocked cells`." in content
    assert "All `3` planned rows were attempted; `1` produced scored success rows and `2` are documented" in content
    assert "All recorded API cost from parsed Inspect logs, including blocked partial rows: `$0.060000`." in content
    assert "| `qwen/qwen3-8b` | `value_prism_relevance` | `error` | provider route blocked |" in content
    assert "## Approved Full-Run Command" not in content
    assert "## Optional Targeted Retry" in content


def test_selected_grid_readme_surfaces_first_figures(tmp_path: Path) -> None:
    plan_rows = _minimal_plan_rows()
    result_rows = [
        {
            **row,
            "run_status": "success",
            "actual_cost_usd": "0.01",
            "completed_samples": "100",
            "reasoning_tokens_actual": "0",
        }
        for row in plan_rows
    ]

    openrouter.write_readme(tmp_path, "test-fetch", 100, _minimal_model_rows(), plan_rows, result_rows)

    content = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "## Figures To Open First" in content
    assert "![Within-family scaling](figures/within_family_scaling.svg)" in content
    assert "![Time scaling](figures/time_scaling.svg)" in content
    assert "![Benchmark comparison matrix](figures/benchmark_score_matrix.svg)" in content
    assert "text-only follow-up figures, not replacements for the frozen release figures" in content
    assert "CCD-Bench is valid-choice behavior, not correctness or accuracy" in content


def test_existing_log_scan_recovers_success_even_when_newer_partial_exists(tmp_path: Path, monkeypatch) -> None:
    row = {
        "model": "qwen/qwen3-8b",
        "task": "unimoral_action_prediction",
        "benchmark": "UniMoral",
    }
    log_dir = tmp_path / "logs" / "qwen__qwen3-8b" / "unimoral_action_prediction"
    log_dir.mkdir(parents=True)
    success_log = log_dir / "older-success.eval"
    partial_log = log_dir / "newer-partial.eval"
    success_log.write_text("success", encoding="utf-8")
    partial_log.write_text("partial", encoding="utf-8")

    def fake_parse(rows, _models_by_id):
        parsed = dict(rows[0])
        parsed["run_status"] = "success" if rows[0]["log_path"].endswith("older-success.eval") else "unreadable"
        return [parsed]

    monkeypatch.setattr(openrouter, "parse_run_results", fake_parse)

    recovered = openrouter.scan_successful_existing_logs(tmp_path, [row], {})

    assert len(recovered) == 1
    assert recovered[0]["log_path"].endswith("older-success.eval")


def test_guarded_full_run_launcher_refuses_without_approval() -> None:
    env = os.environ.copy()
    env.pop("OPENROUTER_FULL_RUN_APPROVED", None)
    env.pop("OPENROUTER_FULL_RUN_DRY_RUN", None)

    result = subprocess.run(
        ["bash", "scripts/run_openrouter_selected_grid_full.sh"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "Refusing to start cost-bearing OpenRouter calls." in result.stderr
    assert "No provider calls were made." in result.stderr


def test_guarded_full_run_launcher_dry_run_prints_command_without_approval() -> None:
    env = os.environ.copy()
    env.pop("OPENROUTER_FULL_RUN_APPROVED", None)
    env["OPENROUTER_FULL_RUN_DRY_RUN"] = "1"
    env["OPENROUTER_PYTHON"] = "fake-python"

    result = subprocess.run(
        ["bash", "scripts/run_openrouter_selected_grid_full.sh"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Dry run only; no provider calls were made." in result.stdout
    assert "--max-total-estimated-cost 60 --yes" in result.stdout
    assert "scripts/openrouter_selected_grid_moral_psych.py run --full" in result.stdout
