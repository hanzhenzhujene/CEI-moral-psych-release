"""Regression checks for benchmark answer parsers and scorer-facing helpers."""

from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "inspect"))

from evals._benchmark_utils import (  # noqa: E402
    classify_valence_label,
    classify_yes_no_label,
    extract_action_choice,
    extract_structured_choice_int,
    extract_structured_rating_int,
)


def test_extract_structured_choice_prefers_tagged_choice():
    text = "SELECTED OPTION: 4\nRATIONALE: Options 1 and 2 are weaker."
    assert extract_structured_choice_int(text, minimum=1, maximum=10) == 4


def test_extract_structured_choice_rejects_ambiguous_multi_number_freeform_text():
    text = "There are 10 options here and I like 4 for the final answer."
    assert extract_structured_choice_int(text, minimum=1, maximum=10) is None


def test_extract_structured_choice_accepts_single_exact_integer():
    assert extract_structured_choice_int("7", minimum=1, maximum=10) == 7


def test_extract_structured_rating_rejects_ratio_style_output():
    assert extract_structured_rating_int("I would rate this 4 out of 5.", minimum=1, maximum=7) is None


def test_extract_structured_rating_accepts_labeled_integer():
    assert extract_structured_rating_int("Rating: 4", minimum=1, maximum=7) == 4


def test_extract_action_choice_does_not_confuse_article_with_answer():
    assert extract_action_choice("A friend should tell the truth.") is None


def test_extract_action_choice_recovers_explicit_choice():
    assert extract_action_choice("Selected action: b") == "b"


def test_classify_yes_no_label_handles_not_relevant_before_relevant():
    assert classify_yes_no_label("This candidate is not relevant.") == "No"


def test_classify_valence_label_prefers_either_before_support_or_oppose():
    assert classify_valence_label("Either way / mixed depending on context.") == "Either"
