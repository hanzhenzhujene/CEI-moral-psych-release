"""Tests for custom lm-eval YAML task configs and utils."""

import sys
from pathlib import Path

import pytest
import yaml

TASKS_DIR = Path(__file__).parent.parent / "src" / "lm-evaluation-harness" / "tasks"


class _LmEvalLoader(yaml.SafeLoader):
    """YAML loader that handles lm-eval's !function tag."""
    pass

_LmEvalLoader.add_constructor(
    "!function",
    lambda loader, node: f"!function {loader.construct_scalar(node)}",
)


def _load_task_yaml(path):
    with open(path) as f:
        return yaml.load(f, Loader=_LmEvalLoader)

sys.path.insert(0, str(TASKS_DIR))

from utils import _preproc_doc, doc_to_text, doc_to_target, process_virtue_docs


# ---------------------------------------------------------------------------
# YAML config validation
# ---------------------------------------------------------------------------

TASK_YAMLS = [
    "cei_ethics_cm.yaml",
    "cei_ethics_deontology.yaml",
    "cei_ethics_justice.yaml",
    "cei_ethics_utilitarianism.yaml",
    "cei_ethics_virtue.yaml",
]


@pytest.mark.parametrize("yaml_file", TASK_YAMLS)
def test_yaml_has_required_fields(yaml_file):
    path = TASKS_DIR / yaml_file
    config = _load_task_yaml(path)

    assert "task" in config, f"{yaml_file}: missing 'task'"
    assert "dataset_path" in config, f"{yaml_file}: missing 'dataset_path'"
    assert config["dataset_path"] == "csv"
    assert "dataset_kwargs" in config, f"{yaml_file}: missing 'dataset_kwargs'"
    assert "data_files" in config["dataset_kwargs"]
    assert "test" in config["dataset_kwargs"]["data_files"]
    assert "output_type" in config
    assert "metric_list" in config


def test_group_yaml():
    path = TASKS_DIR / "_cei_ethics.yaml"
    config = _load_task_yaml(path)

    assert config["group"] == "cei_ethics"
    assert len(config["task"]) == 5


# ---------------------------------------------------------------------------
# Utilitarianism utils
# ---------------------------------------------------------------------------

def test_preproc_doc_deterministic():
    doc = {"baseline": "Good scenario", "less_pleasant": "Bad scenario"}
    result1 = _preproc_doc(doc)
    result2 = _preproc_doc(doc)
    # Same input should produce same output (seeded random)
    assert result1 == result2


def test_preproc_doc_contains_both_scenarios():
    doc = {"baseline": "Good scenario", "less_pleasant": "Bad scenario"}
    result = _preproc_doc(doc)
    assert "Good scenario" in result["scenarios"]
    assert "Bad scenario" in result["scenarios"]
    assert result["label"] in (0, 1)


def test_doc_to_text_format():
    doc = {"baseline": "Good scenario", "less_pleasant": "Bad scenario"}
    text = doc_to_text(doc)
    assert "Scenario 1:" in text
    assert "Scenario 2:" in text
    assert "Is Scenario 1 preferable?" in text


def test_doc_to_target_returns_int():
    doc = {"baseline": "Good scenario", "less_pleasant": "Bad scenario"}
    target = doc_to_target(doc)
    assert target in (0, 1)


# ---------------------------------------------------------------------------
# Virtue utils
# ---------------------------------------------------------------------------

def test_process_virtue_docs_splits_sep():
    """Test that process_virtue_docs correctly splits [SEP] delimiter."""
    from datasets import Dataset

    ds = Dataset.from_dict({
        "label": [1, 0],
        "scenario": [
            "She helped the old lady. [SEP] kind",
            "He stole the wallet. [SEP] honest",
        ],
    })

    result = process_virtue_docs(ds)
    assert "trait" in result.column_names
    assert result[0]["scenario"] == "She helped the old lady."
    assert result[0]["trait"] == "kind"
    assert result[1]["scenario"] == "He stole the wallet."
    assert result[1]["trait"] == "honest"
