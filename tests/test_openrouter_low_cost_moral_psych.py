"""Regression checks for the low-cost OpenRouter moral-psych pipeline."""

from __future__ import annotations

from pathlib import Path

from scripts import openrouter_low_cost_moral_psych as openrouter


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
    assert "--full --output-dir results/openrouter-low-cost-moral-psych-full" in content
    assert "--max-total-estimated-cost 60 --yes" in content
    assert "Do not treat the bounded pilot as the full benchmark" in content


def test_completion_audit_marks_full_plan_as_not_yet_run(tmp_path: Path) -> None:
    plan_rows = _minimal_plan_rows()

    openrouter.write_completion_audit(tmp_path, None, _minimal_model_rows(), plan_rows)

    content = (tmp_path / "completion_audit.md").read_text(encoding="utf-8")
    assert "Evidence level: `plan only`." in content
    assert "Full-objective status: Planned, not yet run." in content
    assert "| Output model/family/size/release/benchmark/score/cost/replication tables | `benchmark_map.csv`, `model_grid.csv`, and `run_plan.csv` are present; scored result tables are created only after live rows exist. | planned only |" in content
    assert "Run only after explicit approval for the full selected-grid OpenRouter spend." in content
    assert "--max-total-estimated-cost 60 --yes" in content
    assert "Do not treat this plan as completed benchmark evidence." in content
