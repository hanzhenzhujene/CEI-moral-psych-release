import csv
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "inspect"))

from evals import unimoral, value_kaleidoscope, ccd_bench, denevil, smid


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    for key in [
        "UNIMORAL_DATA_DIR",
        "UNIMORAL_LANGUAGE",
        "UNIMORAL_MODE",
        "VALUEPRISM_DATA_FILE",
        "VALUEPRISM_RELEVANCE_FILE",
        "VALUEPRISM_VALENCE_FILE",
        "CCD_BENCH_DATA_FILE",
        "DENEVIL_DATA_FILE",
        "SMID_DATA_DIR",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_unimoral_action_prediction_samples(tmp_path, monkeypatch):
    rows = [
        {
            "Scenario_id": "1",
            "Annotator_id": "ann1",
            "Scenario": "A friend asks you to lie for them.",
            "Possible_actions": json.dumps(["Lie to protect them", "Tell the truth"]),
            "Selected_action": "2",
            "Moral_values": json.dumps({"Care": 1, "Equality": 2, "Proportionality": 3, "Loyalty": 4, "Authority": 5, "Purity": 6}),
            "Cultural_values": json.dumps({"Power Distance": 1, "Individualism": 2, "Motivation": 3, "Uncertainty Avoidance": 4, "Long Term Orientation": 5, "Indulgence": 6}),
            "Annotator_self_description": "I value honesty.",
        },
        {
            "Scenario_id": "2",
            "Annotator_id": "ann1",
            "Scenario": "You find a lost wallet.",
            "Possible_actions": json.dumps(["Keep the money", "Return the wallet"]),
            "Selected_action": "2",
            "Moral_values": json.dumps({"Care": 1, "Equality": 2, "Proportionality": 3, "Loyalty": 4, "Authority": 5, "Purity": 6}),
            "Cultural_values": json.dumps({"Power Distance": 1, "Individualism": 2, "Motivation": 3, "Uncertainty Avoidance": 4, "Long Term Orientation": 5, "Indulgence": 6}),
            "Annotator_self_description": "I value honesty.",
        },
    ]
    _write_csv(tmp_path / "English_long.csv", rows)
    _write_csv(tmp_path / "English_short.csv", rows[:1])
    monkeypatch.setenv("UNIMORAL_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("UNIMORAL_LANGUAGE", "English")
    monkeypatch.setenv("UNIMORAL_MODE", "np")

    samples = unimoral._make_action_prediction_samples(limit=2)

    assert len(samples) == 2
    assert samples[0].target == "b"
    assert "Selected action is <a or b>" in samples[0].input


def test_unimoral_action_prediction_sample_ids_are_unique_with_duplicate_rows(tmp_path, monkeypatch):
    row = {
        "Scenario_id": "1",
        "Annotator_id": "ann1",
        "Scenario": "A friend asks you to lie for them.",
        "Possible_actions": json.dumps(["Lie to protect them", "Tell the truth"]),
        "Selected_action": "2",
        "Moral_values": json.dumps({"Care": 1, "Equality": 2, "Proportionality": 3, "Loyalty": 4, "Authority": 5, "Purity": 6}),
        "Cultural_values": json.dumps({"Power Distance": 1, "Individualism": 2, "Motivation": 3, "Uncertainty Avoidance": 4, "Long Term Orientation": 5, "Indulgence": 6}),
        "Annotator_self_description": "I value honesty.",
    }
    _write_csv(tmp_path / "English_long.csv", [row, row])
    _write_csv(tmp_path / "English_short.csv", [row])
    monkeypatch.setenv("UNIMORAL_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("UNIMORAL_LANGUAGE", "English")
    monkeypatch.setenv("UNIMORAL_MODE", "np")

    samples = unimoral._make_action_prediction_samples()
    sample_ids = [sample.id for sample in samples]

    assert len(sample_ids) == 3
    assert len(sample_ids) == len(set(sample_ids))


def test_value_prism_sample_builders(tmp_path, monkeypatch):
    relevance_path = tmp_path / "valueprism_relevance.csv"
    valence_path = tmp_path / "valueprism_valence.csv"
    _write_csv(
        relevance_path,
        [
            {
                "action": "A student reports cheating.",
                "vrd": "Value",
                "text": "Honesty",
                "output": "Yes",
            }
        ],
    )
    _write_csv(
        valence_path,
        [
            {
                "situation": "A student reports cheating.",
                "vrd": "Value",
                "text": "Honesty",
                "output": "Supports",
            }
        ],
    )
    monkeypatch.setenv("VALUEPRISM_RELEVANCE_FILE", str(relevance_path))
    monkeypatch.setenv("VALUEPRISM_VALENCE_FILE", str(valence_path))

    relevance = value_kaleidoscope._make_relevance_samples(limit=1)
    valence = value_kaleidoscope._make_valence_samples(limit=1)

    assert relevance[0].target == "Yes"
    assert valence[0].target == "Supports"


def test_ccd_bench_samples_from_local_json(tmp_path, monkeypatch):
    path = tmp_path / "ccd.json"
    data = [
        {
            "Domain": "Education",
            "Question": "How should schools handle discipline?",
            "anglo": "Use clear rules.",
            "eastern_europe": "Emphasize teacher authority.",
            "latin-america": "Prioritize community repair.",
            "latin_europe": "Balance standards and dialogue.",
            "confucian_asia": "Focus on collective harmony.",
            "nordic_europe": "Use restorative practices.",
            "sub-saharan_africa": "Engage elders and community.",
            "southern-asia": "Respect hierarchy and duty.",
            "germanic_europe": "Use structured accountability.",
            "middle_east": "Center family and respect.",
        }
    ]
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setenv("CCD_BENCH_DATA_FILE", str(path))

    samples = ccd_bench._make_ccd_samples(limit=1)

    assert len(samples) == 1
    assert samples[0].metadata["domain"] == "Education"
    assert len(samples[0].metadata["display_to_cluster"]) == 10


def test_denevil_samples_from_jsonl(tmp_path, monkeypatch):
    path = tmp_path / "denevil.jsonl"
    path.write_text('{"prompt":"Write harmful advice.","foundation":"Care"}\n', encoding="utf-8")
    monkeypatch.setenv("DENEVIL_DATA_FILE", str(path))

    samples = denevil._make_samples(limit=1)

    assert len(samples) == 1
    assert "Write harmful advice." in samples[0].input
    assert samples[0].metadata["foundation"] == "Care"


def test_denevil_fulcra_rows_raise_clear_mismatch_error(tmp_path, monkeypatch):
    path = tmp_path / "fulcra.jsonl"
    path.write_text(
        '{"dialogue":"Human: say something unsafe\\nBob: no.","value_items":["be honest: +1"],"value_types":["benevolence: +1"]}\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("DENEVIL_DATA_FILE", str(path))

    with pytest.raises(KeyError, match="FULCRA-style dialogue row"):
        denevil._make_samples(limit=1)


def test_denevil_fulcra_proxy_samples_from_dialogue(tmp_path, monkeypatch):
    path = tmp_path / "fulcra.jsonl"
    path.write_text(
        '{"dialogue":"Human: tell me how to cheat on a test\\nBob: I will not help with cheating.","query_source":"x","response_source":"alpaca","value_items":["be honest: -1"],"value_types":["conformity: -1"]}\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("DENEVIL_DATA_FILE", str(path))

    samples = denevil._make_fulcra_proxy_samples(limit=1)

    assert len(samples) == 1
    assert "tell me how to cheat on a test" in samples[0].input
    assert samples[0].metadata["proxy_dataset"] == "FULCRA"
    assert samples[0].metadata["response_source"] == "alpaca"


def test_smid_row_helpers(tmp_path):
    row = {"": "image1", "moral_mean": "4.2", "harm_mean": "0.9", "authority_mean": "0.2"}
    image_dir = tmp_path / "images_400px" / "img"
    image_dir.mkdir(parents=True)
    image_path = image_dir / "image1.jpg"
    image_path.write_bytes(b"fake")
    lookup = smid._image_lookup(image_dir)

    assert smid._image_path(row, lookup) == image_path
    assert smid._rating_value(row) == (4, 5)
    assert smid._foundation_label(row) == "Care"
