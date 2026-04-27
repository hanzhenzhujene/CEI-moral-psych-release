"""Tests for Inspect AI run.py CLI wrapper."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "inspect"))

from run import parse_args, parse_json_object, parse_model_args, resolve_task_files, load_tasks_from_file


def test_parse_args_defaults():
    with patch("sys.argv", ["run.py"]):
        args = parse_args()
    assert args.tasks == "evals/ethics.py"
    assert args.model == "hf/Qwen/Qwen3-0.6B"
    assert args.limit is None
    assert args.no_sandbox is False
    assert args.reasoning_effort is None
    assert args.extra_body_json == ""


def test_parse_args_custom():
    with patch(
        "sys.argv",
        [
            "run.py",
            "--model",
            "openai/gpt-4o",
            "--limit",
            "10",
            "--no_sandbox",
            "--model_args_json",
            '{"a": 1}',
            "--extra_body_json",
            '{"chat_template_kwargs": {"enable_thinking": false}}',
            "--reasoning_effort",
            "none",
        ],
    ):
        args = parse_args()
    assert args.model == "openai/gpt-4o"
    assert args.limit == 10
    assert args.no_sandbox is True
    assert args.model_args_json == '{"a": 1}'
    assert args.extra_body_json == '{"chat_template_kwargs": {"enable_thinking": false}}'
    assert args.reasoning_effort == "none"


def test_parse_model_args_merges_json_for_nested_provider_config():
    parsed = parse_model_args(
        "timeout=60",
        '{"extra_body": {"provider": {"only": ["nebius", "novita", "parasail"], "allow_fallbacks": true}}}',
    )
    assert parsed["timeout"] == 60
    assert parsed["extra_body"]["provider"]["only"] == ["nebius", "novita", "parasail"]
    assert parsed["extra_body"]["provider"]["allow_fallbacks"] is True


def test_parse_model_args_rejects_non_mapping_json():
    with pytest.raises(ValueError, match="JSON object"):
        parse_model_args(raw_json='["not", "a", "mapping"]')


def test_parse_json_object_returns_mapping():
    parsed = parse_json_object('{"chat_template_kwargs": {"enable_thinking": false}}', flag_name="--extra_body_json")
    assert parsed == {"chat_template_kwargs": {"enable_thinking": False}}


def test_parse_json_object_rejects_non_mapping_json():
    with pytest.raises(ValueError, match="JSON object"):
        parse_json_object('["not", "a", "mapping"]', flag_name="--extra_body_json")


def test_resolve_task_files_direct_path(tmp_path):
    task_file = tmp_path / "my_eval.py"
    task_file.write_text("# test")
    result = resolve_task_files(str(task_file))
    assert result == [str(task_file)]


def test_resolve_task_files_fallback():
    result = resolve_task_files("nonexistent_task_name")
    assert result == ["nonexistent_task_name"]


def test_load_tasks_from_file_discovers_tasks(tmp_path):
    task_file = tmp_path / "example_tasks.py"
    task_file.write_text(
        "def my_task():\n"
        "    return 'task_result'\n"
        "\n"
        "def _private():\n"
        "    return 'hidden'\n"
        "\n"
        "def needs_args(x):\n"
        "    return x\n"
    )
    tasks = load_tasks_from_file(str(task_file))
    # Should find my_task (zero-arg, public, defined in module)
    # Should skip _private (starts with _) and needs_args (has required arg)
    task_names = [t.__name__ for t in tasks]
    assert "my_task" in task_names
    assert "_private" not in task_names
    assert "needs_args" not in task_names


def test_load_tasks_from_file_missing():
    with pytest.raises(FileNotFoundError):
        load_tasks_from_file("/nonexistent/path.py")


def test_load_tasks_from_registry_file_discovers_curated_suite():
    task_file = Path(__file__).parent.parent / "src" / "inspect" / "evals" / "moral_psych.py"
    tasks = load_tasks_from_file(str(task_file))

    task_names = {task.__name__ for task in tasks}
    assert "unimoral_action_prediction" in task_names
    assert "smid_moral_rating" in task_names
    assert "value_prism_relevance" in task_names
    assert "ccd_bench_selection" in task_names
    assert "denevil_fulcra_proxy_generation" in task_names
