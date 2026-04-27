"""Tests for lm-evaluation-harness run.py CLI wrapper."""

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

# Import from specific file path to avoid collision with src/inspect/run.py
_run_path = Path(__file__).parent.parent / "src" / "lm-evaluation-harness" / "run.py"
_spec = importlib.util.spec_from_file_location("lm_harness_run", _run_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
parse_args = _module.parse_args


def test_parse_args_defaults():
    with patch("sys.argv", ["run.py"]):
        args = parse_args()
    assert args.model == "hf"
    assert args.model_args == "pretrained=Qwen/Qwen3-0.6B"
    assert args.tasks == "cei_ethics"
    assert args.num_fewshot == 0
    assert args.limit is None
    assert args.log_samples is False
    # output_path should be absolute (not relative)
    assert Path(args.output_path).is_absolute()
    # task_dir should point to the tasks/ directory
    assert args.task_dir.endswith("tasks")


def test_parse_args_custom():
    with patch("sys.argv", [
        "run.py",
        "--model", "openai-chat-completions",
        "--model_args", "model=gpt-4o",
        "--tasks", "cei_ethics_cm",
        "--limit", "5",
    ]):
        args = parse_args()
    assert args.model == "openai-chat-completions"
    assert args.model_args == "model=gpt-4o"
    assert args.tasks == "cei_ethics_cm"
    assert args.limit == 5


def test_model_slug_generation():
    """Test that model_args produce valid filenames."""
    model_args = "pretrained=Qwen/Qwen3-0.6B"
    model_slug = model_args.replace("/", "_").replace("=", "-").replace(",", "_")
    assert model_slug == "pretrained-Qwen_Qwen3-0.6B"
    assert "/" not in model_slug
