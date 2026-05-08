"""Regression checks for benchmark answer parsers and scorer-facing helpers."""

from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "inspect"))

from evals._benchmark_utils import (  # noqa: E402
    build_vision_input,
    classify_valence_label,
    classify_yes_no_label,
    extract_structured_label,
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


def test_extract_structured_rating_accepts_ratio_style():
    assert extract_structured_rating_int("I would rate this 4 out of 5.", minimum=1, maximum=7) == 4


def test_extract_structured_rating_accepts_fraction_style():
    assert extract_structured_rating_int("4/7", minimum=1, maximum=7) == 4


def test_extract_structured_rating_accepts_labeled_integer():
    assert extract_structured_rating_int("Rating: 4", minimum=1, maximum=7) == 4


def test_extract_structured_rating_accepts_rate_as_phrase():
    text = "Based on the scene, I would rate the situation as a 5 on the moral scale."
    assert extract_structured_rating_int(text, minimum=1, maximum=7) == 5


def test_extract_structured_rating_prefers_explicit_final_answer_over_scale_description():
    text = "Scale: 1 is moral and 5 is immoral. Therefore, my answer is: 5"
    assert extract_structured_rating_int(text, minimum=1, maximum=7) == 5


def test_extract_structured_rating_accepts_exact_integer():
    assert extract_structured_rating_int("4", minimum=1, maximum=7) == 4


def test_extract_structured_rating_rejects_out_of_range():
    assert extract_structured_rating_int("9", minimum=1, maximum=7) is None


def test_extract_action_choice_does_not_confuse_article_with_answer():
    assert extract_action_choice("A friend should tell the truth.") is None


def test_extract_action_choice_recovers_explicit_choice():
    assert extract_action_choice("Selected action: b") == "b"


def test_classify_yes_no_label_handles_not_relevant_before_relevant():
    assert classify_yes_no_label("This candidate is not relevant.") == "No"


def test_classify_yes_no_label_returns_yes_for_relevant():
    assert classify_yes_no_label("Yes, this is relevant.") == "Yes"


def test_classify_yes_no_label_standalone_no():
    assert classify_yes_no_label("No") == "No"


def test_classify_yes_no_label_yes_before_no():
    """When both 'yes' and 'no' appear, 'yes/relevant' wins."""
    assert classify_yes_no_label("It's not a no, it's yes and relevant.") == "Yes"


def test_classify_yes_no_label_prefers_explicit_final_answer_over_earlier_relevant_word():
    text = "The value may sound relevant in the abstract, but final answer: No"
    assert classify_yes_no_label(text) == "No"


def test_classify_yes_no_label_prefers_line_leading_no_over_later_relevant_word():
    text = "No, even if the concept seems relevant in the abstract."
    assert classify_yes_no_label(text) == "No"


def test_classify_valence_label_supports_before_either():
    """Definitive stance should win over hedged/mixed qualifier."""
    assert classify_valence_label("Supports, either way could work.") == "Supports"


def test_classify_valence_label_opposes():
    assert classify_valence_label("Opposes the value.") == "Opposes"


def test_classify_valence_label_prefers_explicit_final_answer_over_earlier_support_mention():
    text = "It may support one reading, but final answer: Opposes"
    assert classify_valence_label(text) == "Opposes"


def test_classify_valence_label_either_standalone():
    assert classify_valence_label("Either way / mixed.") == "Either"


def test_classify_valence_label_neutral():
    assert classify_valence_label("Neutral on this topic.") == "Either"


def test_extract_structured_label_prefers_explicit_answer_over_earlier_label_mentions():
    patterns = {
        "Care": [r"\bcare\b", r"\bharm\b"],
        "Fairness": [r"\bfairness\b", r"\bfair\b"],
        "Loyalty": [r"\bloyalty\b", r"\bloyal\b"],
    }
    text = (
        "Options include Care, Fairness, and Loyalty.\n"
        "The answer is: Loyalty"
    )
    assert extract_structured_label(text, patterns) == "Loyalty"


def test_build_vision_input_uses_standard_image_block_off_minimax(tmp_path, monkeypatch):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake-image-bytes")

    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    messages = build_vision_input(image_path, "Rate this image.")

    assert len(messages) == 1
    assert messages[0].content[0].type == "image"
    assert messages[0].content[0].image == str(image_path)
    assert messages[0].content[1].type == "text"
    assert messages[0].content[1].text == "Rate this image."


def test_build_vision_input_uses_image_block_with_data_uri_for_direct_minimax(tmp_path, monkeypatch):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake-image-bytes")

    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.minimax.io/v1")

    messages = build_vision_input(image_path, "Rate this image.")

    assert len(messages) == 1
    assert len(messages[0].content) == 2
    assert messages[0].content[0].type == "image"
    assert messages[0].content[0].image.startswith("data:image/png;base64,")
    assert "ZmFrZS1pbWFnZS1ieXRlcw==" in messages[0].content[0].image
    assert messages[0].content[1].type == "text"
    assert messages[0].content[1].text == "Rate this image."
