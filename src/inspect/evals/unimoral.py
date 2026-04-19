"""Inspect AI tasks for the UniMoral benchmark family."""

from __future__ import annotations

import ast
import csv
from collections import defaultdict
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample

from evals._benchmark_utils import (
    format_ab_choices,
    generation_plan,
    label_membership_scorer,
    normalize_possible_actions,
    normalize_whitespace,
    selected_action_text,
    env_str,
    rouge_l_max_scorer,
)

PROMPTS_DIR = Path(__file__).parent / "data" / "unimoral"
LANGUAGE_CODES = {
    "Arabic": "ara",
    "Chinese": "chi",
    "English": "eng",
    "Hindi": "hin",
    "Russian": "rus",
    "Spanish": "spa",
}
ACTION_PATTERNS = {"a": [r"selected action is\s*a\b", r"\boption\s*a\b", r"\b\(?a\)?\b"], "b": [r"selected action is\s*b\b", r"\boption\s*b\b", r"\b\(?b\)?\b"]}
TYPOLOGY_PATTERNS = {
    "Deontological": [r"deontolog"],
    "Utilitarianism": [r"utilitarian"],
    "Rights-based": [r"rights?[- ]based", r"\bright\b"],
    "Virtuous": [r"virtu"],
}
FACTOR_PATTERNS = {
    "Emotions": [r"emotion"],
    "Moral": [r"\bmoral\b"],
    "Culture": [r"culture"],
    "Responsibilities": [r"responsibilit"],
    "Relationships": [r"relationship"],
    "Legality": [r"legal", r"law"],
    "Politeness": [r"polite"],
    "Sacred values": [r"sacred"],
}
MORAL_LABELS = ["Care", "Equality", "Proportionality", "Loyalty", "Authority", "Purity"]
CULTURE_LABELS = [
    "Power Distance",
    "Individualism",
    "Motivation",
    "Uncertainty Avoidance",
    "Long Term Orientation",
    "Indulgence",
]
TYPOLOGY_LABELS = ["Deontological", "Utilitarianism", "Rights-based", "Virtuous"]
FACTOR_LABELS = [
    "Emotions",
    "Moral",
    "Culture",
    "Responsibilities",
    "Relationships",
    "Legality",
    "Politeness",
    "Sacred values",
]


def _load_prompt_dict(filename: str) -> dict[str, str]:
    return ast.literal_eval((PROMPTS_DIR / filename).read_text())


def _unimoral_languages() -> list[str]:
    requested = env_str("UNIMORAL_LANGUAGE", "all")
    if requested is None or requested.lower() == "all":
        return list(LANGUAGE_CODES)
    if requested not in LANGUAGE_CODES:
        valid = ", ".join(["all", *LANGUAGE_CODES])
        raise ValueError(f"Unsupported UNIMORAL_LANGUAGE={requested!r}. Expected one of: {valid}.")
    return [requested]


def _unimoral_data_dir() -> Path:
    data_dir = env_str("UNIMORAL_DATA_DIR")
    if not data_dir:
        raise FileNotFoundError(
            "UniMoral is gated. Set UNIMORAL_DATA_DIR to the folder containing files such as "
            "English_long.csv and English_short.csv."
        )
    path = Path(data_dir).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"UNIMORAL_DATA_DIR does not exist: {path}")
    return path


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _language_files(language: str) -> tuple[Path, Path]:
    data_dir = _unimoral_data_dir()
    long_path = data_dir / f"{language}_long.csv"
    short_path = data_dir / f"{language}_short.csv"
    if not long_path.exists():
        raise FileNotFoundError(f"Missing UniMoral file: {long_path}")
    return long_path, short_path


def _vector_from_serialized(value: str) -> list[float]:
    parsed = ast.literal_eval(value)
    return [float(item) for item in parsed.values()]


def _top_label_order(vector: list[float], labels: list[str]) -> list[str]:
    ranking = sorted(range(len(vector)), key=lambda idx: vector[idx], reverse=True)
    return [labels[idx] for idx in ranking]


def _action_target(raw_value: str | int) -> str:
    normalized = str(raw_value).strip().lower()
    return "a" if normalized in {"1", "a"} else "b"


def _list_targets(serialized: str, labels: list[str]) -> list[str]:
    values = [int(item) for item in ast.literal_eval(serialized)]
    maximum = max(values)
    return [labels[index] for index, value in enumerate(values) if value == maximum]


def _fewshot_by_annotator(rows: list[dict[str, str]], count: int) -> dict[tuple[str, str], list[dict[str, str]]]:
    rows_by_annotator: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rows_by_annotator[row["Annotator_id"]].append(row)

    fewshot_map: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        peers = [peer for peer in rows_by_annotator[row["Annotator_id"]] if peer["Scenario_id"] != row["Scenario_id"]]
        if not peers:
            peers = rows_by_annotator[row["Annotator_id"]]
        peers = sorted(peers, key=lambda item: item["Scenario_id"])
        chosen = peers[:count]
        while len(chosen) < count and peers:
            chosen.append(peers[len(chosen) % len(peers)])
        fewshot_map[(row["Annotator_id"], row["Scenario_id"])] = chosen
    return fewshot_map


def _prompt_key(mode: str, language: str, rq: int) -> str:
    suffix = LANGUAGE_CODES[language]
    return f"prompt_{mode}_{suffix}_rq{rq}"


def _fill_prompt(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return normalize_whitespace(rendered)


def _common_replacements(row: dict[str, str]) -> dict[str, str]:
    moral_vector = _vector_from_serialized(row["Moral_values"])
    culture_vector = _vector_from_serialized(row["Cultural_values"])
    moral_order = _top_label_order(moral_vector, MORAL_LABELS)
    culture_order = _top_label_order(culture_vector, CULTURE_LABELS)
    replacements = {
        "[SCENARIO]": row["Scenario"],
        "[ACTIONS]": format_ab_choices(row["Possible_actions"]),
        "[DESC]": row.get("Annotator_self_description", ""),
        "[MORAL]": " ".join(str(value) for value in moral_vector),
        "[CULTURE]": " ".join(str(value) for value in culture_vector),
    }
    for index, label in enumerate(moral_order, start=1):
        replacements[f"[MORAL_VALUE_{index}]"] = label
    for index, label in enumerate(culture_order, start=1):
        replacements[f"[CULTURAL_VALUE_{index}]"] = label
    return replacements


def _make_action_prediction_samples(limit: int | None = None) -> list[Sample]:
    prompts = _load_prompt_dict("PROMPTS.txt")
    mode = env_str("UNIMORAL_MODE", "np")
    samples: list[Sample] = []
    for language in _unimoral_languages():
        long_path, short_path = _language_files(language)
        rows = _load_csv_rows(long_path)
        if short_path.exists():
            rows.extend(_load_csv_rows(short_path))
        fs_map = _fewshot_by_annotator(rows, 3)
        prompt_key = _prompt_key(mode, language, 1)
        if prompt_key not in prompts:
            raise KeyError(f"Prompt key {prompt_key!r} not found in PROMPTS.txt")
        selected_rows = rows[:limit] if limit is not None else rows
        for sample_index, row in enumerate(selected_rows):
            replacements = _common_replacements(row)
            for index, fs_row in enumerate(fs_map[(row["Annotator_id"], row["Scenario_id"])], start=1):
                replacements[f"[FS_SCENARIO_{index}]"] = fs_row["Scenario"]
                replacements[f"[FS_ACTIONS_{index}]"] = format_ab_choices(fs_row["Possible_actions"])
                replacements[f"[FS_GT_{index}]"] = _action_target(fs_row["Selected_action"])
            rendered = _fill_prompt(prompts[prompt_key], replacements)
            samples.append(
                Sample(
                    id=f"{language}-rq1-{row['Scenario_id']}-{row['Annotator_id']}-{sample_index}",
                    input=rendered,
                    target=_action_target(row["Selected_action"]),
                    metadata={"language": language, "scenario_id": row["Scenario_id"], "annotator_id": row["Annotator_id"], "sample_index": sample_index},
                )
            )
    return samples


def _make_typology_samples(limit: int | None = None) -> list[Sample]:
    prompts = _load_prompt_dict("PROMPTS2.txt")
    mode = env_str("UNIMORAL_MODE", "np")
    samples: list[Sample] = []
    for language in _unimoral_languages():
        long_path, _ = _language_files(language)
        rows = _load_csv_rows(long_path)
        fs_map = _fewshot_by_annotator(rows, 1)
        prompt_key = _prompt_key(mode, language, 2)
        if prompt_key not in prompts:
            raise KeyError(f"Prompt key {prompt_key!r} not found in PROMPTS2.txt")
        selected_rows = rows[:limit] if limit is not None else rows
        for sample_index, row in enumerate(selected_rows):
            replacements = _common_replacements(row)
            replacements["[SELECTED_ACTION]"] = _action_target(row["Selected_action"]) if mode != "fs" else selected_action_text(row["Possible_actions"], row["Selected_action"])
            fs_row = fs_map[(row["Annotator_id"], row["Scenario_id"])][0]
            replacements["[FS_SCENARIO]"] = fs_row["Scenario"]
            replacements["[FS_ACTION]"] = selected_action_text(fs_row["Possible_actions"], fs_row["Selected_action"])
            replacements["[FS_ACTION_TYPE]"] = ", ".join(_list_targets(fs_row["Action_criteria"], TYPOLOGY_LABELS))
            rendered = _fill_prompt(prompts[prompt_key], replacements)
            samples.append(
                Sample(
                    id=f"{language}-rq2-{row['Scenario_id']}-{row['Annotator_id']}-{sample_index}",
                    input=rendered,
                    target=_list_targets(row["Action_criteria"], TYPOLOGY_LABELS),
                    metadata={"language": language, "scenario_id": row["Scenario_id"], "annotator_id": row["Annotator_id"], "sample_index": sample_index},
                )
            )
    return samples


def _make_factor_samples(limit: int | None = None) -> list[Sample]:
    prompts = _load_prompt_dict("PROMPTS3.txt")
    mode = env_str("UNIMORAL_MODE", "np")
    samples: list[Sample] = []
    for language in _unimoral_languages():
        long_path, _ = _language_files(language)
        rows = _load_csv_rows(long_path)
        fs_map = _fewshot_by_annotator(rows, 1)
        prompt_key = _prompt_key(mode, language, 3)
        if prompt_key not in prompts:
            raise KeyError(f"Prompt key {prompt_key!r} not found in PROMPTS3.txt")
        selected_rows = rows[:limit] if limit is not None else rows
        for sample_index, row in enumerate(selected_rows):
            replacements = _common_replacements(row)
            replacements["[SELECTED_ACTION]"] = _action_target(row["Selected_action"]) if mode != "fs" else selected_action_text(row["Possible_actions"], row["Selected_action"])
            fs_row = fs_map[(row["Annotator_id"], row["Scenario_id"])][0]
            replacements["[FS_SCENARIO]"] = fs_row["Scenario"]
            replacements["[FS_ACTION]"] = selected_action_text(fs_row["Possible_actions"], fs_row["Selected_action"])
            replacements["[FS_CONTRIBUTING_FACTOR]"] = ", ".join(_list_targets(fs_row["Contributing_factors"], FACTOR_LABELS))
            rendered = _fill_prompt(prompts[prompt_key], replacements)
            samples.append(
                Sample(
                    id=f"{language}-rq3-{row['Scenario_id']}-{row['Annotator_id']}-{sample_index}",
                    input=rendered,
                    target=_list_targets(row["Contributing_factors"], FACTOR_LABELS),
                    metadata={"language": language, "scenario_id": row["Scenario_id"], "annotator_id": row["Annotator_id"], "sample_index": sample_index},
                )
            )
    return samples


def _make_consequence_samples(limit: int | None = None) -> list[Sample]:
    prompts = _load_prompt_dict("PROMPTS4.txt")
    samples: list[Sample] = []
    for language in _unimoral_languages():
        long_path, _ = _language_files(language)
        rows = _load_csv_rows(long_path)
        grouped: dict[tuple[str, str], dict[str, list[str] | str]] = {}
        for row in rows:
            scenario_key = (row["Scenario_id"], _action_target(row["Selected_action"]))
            consequences = grouped.setdefault(
                scenario_key,
                {"scenario": row["Scenario"], "action": selected_action_text(row["Possible_actions"], row["Selected_action"]), "consequences": []},
            )
            consequence = normalize_whitespace(str(row.get("Consequence", ""))).strip("[]")
            if consequence:
                consequences["consequences"].append(consequence)
        prompt_key = f"prompt_{LANGUAGE_CODES[language]}_rq4"
        if prompt_key not in prompts:
            raise KeyError(f"Prompt key {prompt_key!r} not found in PROMPTS4.txt")
        values = list(grouped.items())
        if limit is not None:
            values = values[:limit]
        for (scenario_id, action_label), payload in values:
            rendered = _fill_prompt(
                prompts[prompt_key],
                {
                    "[SCENARIO]": str(payload["scenario"]),
                    "[SELECTED_ACTION]": str(payload["action"]),
                },
            )
            samples.append(
                Sample(
                    id=f"{language}-rq4-{scenario_id}-{action_label}",
                    input=rendered,
                    target=list(payload["consequences"]),
                    metadata={"language": language, "scenario_id": scenario_id, "selected_action": action_label},
                )
            )
    return samples


@task
def unimoral_action_prediction(limit: int | None = None) -> Task:
    return Task(dataset=MemoryDataset(_make_action_prediction_samples(limit=limit)), plan=generation_plan(max_tokens=64), scorer=label_membership_scorer(ACTION_PATTERNS))


@task
def unimoral_moral_typology(limit: int | None = None) -> Task:
    return Task(dataset=MemoryDataset(_make_typology_samples(limit=limit)), plan=generation_plan(max_tokens=96), scorer=label_membership_scorer(TYPOLOGY_PATTERNS))


@task
def unimoral_factor_attribution(limit: int | None = None) -> Task:
    return Task(dataset=MemoryDataset(_make_factor_samples(limit=limit)), plan=generation_plan(max_tokens=96), scorer=label_membership_scorer(FACTOR_PATTERNS))


@task
def unimoral_consequence_generation(limit: int | None = None) -> Task:
    return Task(dataset=MemoryDataset(_make_consequence_samples(limit=limit)), plan=generation_plan(max_tokens=256), scorer=rouge_l_max_scorer())
