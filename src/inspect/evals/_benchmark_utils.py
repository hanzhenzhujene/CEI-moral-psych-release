"""Shared helpers for the moral-psych Inspect AI tasks.

These utilities centralize env-var parsing, lightweight dataset loading,
prompt normalization, and common scorers so individual benchmark modules stay
small and focused on benchmark-specific logic.
"""

from __future__ import annotations

import ast
import json
import os
import random
import re
import shutil
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
from inspect_ai.scorer import Score, Target, accuracy, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate
from rouge_score import rouge_scorer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = PROJECT_ROOT / "results" / "cache"

MORAL_FOUNDATION_LABELS = ["Care", "Fairness", "Loyalty", "Authority", "Sanctity"]
CCD_CLUSTER_MAP = {
    1: "anglo",
    2: "eastern_europe",
    3: "latin-america",
    4: "latin_europe",
    5: "confucian_asia",
    6: "nordic_europe",
    7: "sub-saharan_africa",
    8: "southern-asia",
    9: "germanic_europe",
    10: "middle_east",
}


def env_str(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def env_int(name: str, default: int) -> int:
    value = env_str(name)
    return int(value) if value is not None else default


def env_float(name: str, default: float) -> float:
    value = env_str(name)
    return float(value) if value is not None else default


def env_bool(name: str, default: bool = False) -> bool:
    value = env_str(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def generation_plan(max_tokens: int = 256):
    min_max_tokens = env_int("CEI_MIN_MAX_TOKENS", max_tokens)
    effective_max_tokens = max(max_tokens, min_max_tokens)
    return [generate(max_tokens=effective_max_tokens, temperature=env_float("CEI_TEMPERATURE", 0.0))]


def normalize_whitespace(text: str) -> str:
    return " ".join(str(text).split())


def normalize_text(text: str) -> str:
    return normalize_whitespace(text).lower()


def apply_prompt_prefix(text: str) -> str:
    prefix = env_str("CEI_PROMPT_PREFIX")
    if prefix is None:
        return text
    prefix = str(prefix).strip()
    if not prefix:
        return text
    return f"{prefix}\n\n{text}"


def maybe_literal(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
    return value


def ensure_cache_dir() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def cached_download(url: str, cache_name: str | None = None) -> Path:
    cache_dir = ensure_cache_dir()
    filename = cache_name or Path(urllib.parse.urlparse(url).path).name or "downloaded_file"
    output_path = cache_dir / filename
    if output_path.exists():
        return output_path
    with urllib.request.urlopen(url) as response, output_path.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return output_path


def load_json_source(path_or_url: str | None, *, default_url: str | None = None, cache_name: str | None = None) -> Any:
    if path_or_url:
        source = Path(path_or_url).expanduser()
        if not source.exists():
            raise FileNotFoundError(f"Expected dataset file at {source}")
        return json.loads(source.read_text())
    if default_url is None:
        raise FileNotFoundError("No dataset path was provided and there is no default URL for this benchmark.")
    cached = cached_download(default_url, cache_name=cache_name)
    return json.loads(cached.read_text())


def build_vision_input(image_path: Path, prompt: str):
    return [
        ChatMessageUser(
            content=[
                ContentImage(image=str(image_path)),
                ContentText(text=prompt),
            ]
        )
    ]


def extract_first_int(text: str, *, minimum: int | None = None, maximum: int | None = None) -> int | None:
    for match in re.findall(r"\b\d+\b", text):
        value = int(match)
        if minimum is not None and value < minimum:
            continue
        if maximum is not None and value > maximum:
            continue
        return value
    return None


def canonicalize_label(text: str, patterns: Mapping[str, Sequence[str]]) -> str | None:
    lowered = normalize_text(text)
    for canonical, regexes in patterns.items():
        for regex in regexes:
            if re.search(regex, lowered):
                return canonical
    return None


def first_matching_key(row: Mapping[str, Any], *candidates: str) -> str | None:
    normalized = {key.lower().strip(): key for key in row.keys()}
    for candidate in candidates:
        match = normalized.get(candidate.lower().strip())
        if match is not None:
            return match
    return None


def fuzzy_matching_key(row: Mapping[str, Any], *substrings: str) -> str | None:
    lowered_keys = {key.lower().strip(): key for key in row.keys()}
    for substring in substrings:
        substring = substring.lower().strip()
        for lowered, original in lowered_keys.items():
            if substring in lowered:
                return original
    return None


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_possible_actions(raw_actions: Any) -> list[str]:
    actions = maybe_literal(raw_actions)
    if not isinstance(actions, list):
        return [str(actions)]
    if actions and all(isinstance(item, str) for item in actions):
        return [str(item) for item in actions]
    if len(actions) >= 2 and all(isinstance(item, (list, tuple)) for item in actions):
        return [str(item[0]) if item else "" for item in actions[:2]]
    if actions and isinstance(actions[0], (list, tuple)) and len(actions[0]) >= 2:
        return [str(actions[0][0]), str(actions[0][1])]
    normalized = []
    for item in actions:
        if isinstance(item, (list, tuple)) and item:
            normalized.append(str(item[0]))
        else:
            normalized.append(str(item))
    return normalized


def format_ab_choices(raw_actions: Any) -> str:
    actions = normalize_possible_actions(raw_actions)
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "; ".join(f"({labels[idx].lower()}) {action}" for idx, action in enumerate(actions))


def selected_action_text(raw_actions: Any, selected_action: Any) -> str:
    actions = normalize_possible_actions(raw_actions)
    labels = "abcdefghijklmnopqrstuvwxyz"
    if isinstance(selected_action, str) and selected_action.lower() in labels[: len(actions)]:
        index = labels.index(selected_action.lower())
    else:
        index = int(selected_action) - 1
    index = max(0, min(index, len(actions) - 1))
    return f"{labels[index]}: {actions[index]}"


def ensure_extracted_zip(zip_path: Path) -> Path:
    extract_dir = zip_path.with_suffix("")
    if extract_dir.exists():
        return extract_dir
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)
    return extract_dir


@scorer(metrics=[accuracy(), stderr()])
def label_membership_scorer(patterns: Mapping[str, Sequence[str]]):
    async def score(state: TaskState, target: Target) -> Score:
        answer = canonicalize_label(state.output.completion, patterns)
        is_correct = answer is not None and answer in target.target
        return Score(
            value=1 if is_correct else 0,
            answer=answer or "",
            explanation=state.output.completion,
        )

    return score


@scorer(metrics=[mean(), stderr()])
def valid_choice_scorer(minimum: int, maximum: int):
    async def score(state: TaskState, target: Target) -> Score:
        choice = extract_first_int(state.output.completion, minimum=minimum, maximum=maximum)
        return Score(
            value=1.0 if choice is not None else 0.0,
            answer="" if choice is None else str(choice),
            explanation=state.output.completion,
            metadata={"selected_option": choice},
        )

    return score


@scorer(metrics=[mean(), stderr()])
def response_present_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        answer = normalize_whitespace(state.output.completion)
        return Score(
            value=1.0 if answer else 0.0,
            answer=answer,
            explanation=state.output.completion,
        )

    return score


@scorer(metrics=[mean(), stderr()])
def rouge_l_max_scorer():
    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

    async def score(state: TaskState, target: Target) -> Score:
        prediction = normalize_whitespace(state.output.completion)
        references = [normalize_whitespace(reference) for reference in target.target if reference]
        if not prediction or not references:
            return Score(value=0.0, answer=prediction, explanation=state.output.completion)

        best_score = 0.0
        best_reference = ""
        for reference in references:
            score_value = rouge.score(reference, prediction)["rougeL"].fmeasure
            if score_value > best_score:
                best_score = score_value
                best_reference = reference

        return Score(
            value=best_score,
            answer=prediction,
            explanation=best_reference,
            metadata={"best_reference": best_reference},
        )

    return score


def generate_latin_square(size: int = 10, seed: int = 42) -> list[list[int]]:
    random.seed(seed)
    latin_square = []
    for row_index in range(size):
        row = [(column_index + row_index) % size + 1 for column_index in range(size)]
        latin_square.append(row)

    row_indices = list(range(1, size))
    random.shuffle(row_indices)
    reordered_rows = [latin_square[0]] + [latin_square[index] for index in row_indices]

    column_indices = list(range(size))
    random.shuffle(column_indices)
    return [[row[index] for index in column_indices] for row in reordered_rows]


def generate_stratified_latin_squares(domains: Sequence[str], seed: int = 42) -> dict[str, list[list[int]]]:
    return {domain: generate_latin_square(10, seed + offset * 100) for offset, domain in enumerate(domains)}
