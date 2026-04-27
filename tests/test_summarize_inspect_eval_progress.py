from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "scripts" / "summarize_inspect_eval_progress.py"
SPEC = importlib.util.spec_from_file_location("summarize_inspect_eval_progress", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
_parse_eval = MODULE._parse_eval


def write_eval(path: Path, *, task: str, model: str, total_samples: int, completed_samples: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "_journal/start.json",
            json.dumps(
                {
                    "eval": {
                        "task": task,
                        "model": model,
                        "dataset": {"samples": total_samples},
                    }
                }
            ),
        )
        for idx in range(1, completed_samples + 1):
            zf.writestr(f"samples/{idx}_epoch_1.json", json.dumps({"id": idx}))


def test_parse_eval_uses_job_directory_as_family_when_log_root_is_parent(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    eval_path = log_root / "gemma_27b_large" / "run.eval"
    write_eval(
        eval_path,
        task="value_prism_relevance",
        model="openrouter/google/gemma-3-27b-it",
        total_samples=100,
        completed_samples=30,
    )

    row = _parse_eval(eval_path, log_root)

    assert row.family == "gemma_27b_large"
    assert row.task == "value_prism_relevance"
    assert row.completed_samples == 30
    assert row.total_samples == 100
    assert row.progress_pct == 30.0


def test_parse_eval_uses_parent_directory_as_family_when_log_root_is_job_dir(tmp_path: Path) -> None:
    job_root = tmp_path / "logs" / "gemma_27b_large"
    eval_path = job_root / "run.eval"
    write_eval(
        eval_path,
        task="value_prism_relevance",
        model="openrouter/google/gemma-3-27b-it",
        total_samples=50,
        completed_samples=20,
    )

    row = _parse_eval(eval_path, job_root)

    assert row.family == "gemma_27b_large"
    assert row.completed_samples == 20
    assert row.total_samples == 50
