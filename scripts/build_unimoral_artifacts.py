"""Build UniMoral full-benchmark result tables and SVG figures from Inspect logs."""

from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from pathlib import Path
from statistics import mean
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "inspect"))

from evals._benchmark_utils import (  # noqa: E402
    canonicalize_label_from_output,
    consequence_text_from_output,
    meteor_score,
    normalize_whitespace,
    sentence_bleu_score,
    text_from_sample_output,
)
from evals.unimoral import FACTOR_PATTERNS, TYPOLOGY_PATTERNS  # noqa: E402
from rouge_score import rouge_scorer  # noqa: E402

MODEL_LINES = [
    ("Qwen-S", "Qwen", "S", "qwen_s"),
    ("Qwen-M", "Qwen", "M", "qwen_m"),
    ("Qwen-L", "Qwen", "L", "qwen_l"),
    ("MiniMax-S", "MiniMax", "S", "minimax_s"),
    ("MiniMax-M", "MiniMax", "M", "minimax_m"),
    ("MiniMax-L", "MiniMax", "L", "minimax_l"),
    ("DeepSeek-S", "DeepSeek", "S", "deepseek_s"),
    ("DeepSeek-M", "DeepSeek", "M", "deepseek_m"),
    ("DeepSeek-L", "DeepSeek", "L", "deepseek_l"),
    ("Llama-S", "Llama", "S", "llama_s"),
    ("Llama-M", "Llama", "M", "llama_m"),
    ("Llama-L", "Llama", "L", "llama_l"),
    ("Gemma-S", "Gemma", "S", "gemma_s"),
    ("Gemma-M", "Gemma", "M", "gemma_m"),
    ("Gemma-L", "Gemma", "L", "gemma_l"),
    ("GPT4 only", "GPT4 only", "Ref", "gpt4_only"),
]

TASKS = {
    "unimoral_action_prediction": {
        "rq": "RQ1",
        "label": "Action prediction",
        "metric": "accuracy",
        "expected": 8784,
    },
    "unimoral_moral_typology": {
        "rq": "RQ2",
        "label": "Moral typology",
        "metric": "accuracy",
        "expected": 3492,
    },
    "unimoral_factor_attribution": {
        "rq": "RQ3",
        "label": "Factor attribution",
        "metric": "accuracy",
        "expected": 3492,
    },
    "unimoral_consequence_generation": {
        "rq": "RQ4",
        "label": "Consequence generation",
        "metric": "bert_score_f1",
        "expected": 1782,
    },
}

CLASSIFICATION_TASK_NAMES = [
    "unimoral_action_prediction",
    "unimoral_moral_typology",
    "unimoral_factor_attribution",
]
GENERATION_TASK_NAME = "unimoral_consequence_generation"

MINIMAX_RESUME_PLAN = {
    ("MiniMax-S", "unimoral_moral_typology"): {
        "evidence": "3492/3492 logged; 3383/3492 parseable",
        "range_summary": "54 parse-gap ranges covering 109 samples",
        "recommended_env": "",
        "range_detail": "Use the dry-run command above to print the full 54-range list.",
    },
    ("MiniMax-S", "unimoral_factor_attribution"): {
        "evidence": "3492/3492 logged; 719/3492 parseable",
        "range_summary": "511 unmerged ranges covering 2773 samples; max_gap=3 gives 14 ranges covering 3436 samples",
        "recommended_env": "UNIMORAL_RERUN_UNPARSED_MAX_GAP=3 ",
        "range_detail": "0 304;308 387;393 604;608 619;623 626;630 834;838 857;861 1026;1031 1238;1242 2369;2373 2651;2656 3077;3081 3472;3476 3492",
    },
    ("MiniMax-S", "unimoral_consequence_generation"): {
        "evidence": "1782/1782 logged; 1781/1782 parseable",
        "range_summary": "1 parse-gap range covering 1 sample",
        "recommended_env": "",
        "range_detail": "1120 1121",
    },
    ("MiniMax-M", "unimoral_factor_attribution"): {
        "evidence": "3492/3492 logged; 3491/3492 parseable",
        "range_summary": "1 parse-gap range covering 1 sample",
        "recommended_env": "",
        "range_detail": "1981 1982",
    },
    ("MiniMax-M", "unimoral_consequence_generation"): {
        "evidence": "1782/1782 logged; 1770/1782 parseable",
        "range_summary": "5 parse-gap ranges covering 12 samples",
        "recommended_env": "",
        "range_detail": "1111 1112;1172 1173;1334 1335;1465 1466;1468 1476",
    },
    ("MiniMax-L", "unimoral_factor_attribution"): {
        "evidence": "1800/3492 logged; 1784/3492 parseable",
        "range_summary": "8 missing/parse-gap ranges covering 1708 samples",
        "recommended_env": "",
        "range_detail": "379 380;715 717;721 722;725 1750;2774 2775;2811 2812;2814 2817;2818 3492",
    },
    ("MiniMax-L", "unimoral_consequence_generation"): {
        "evidence": "0/1782 logged; 0/1782 parseable",
        "range_summary": "1 full-task range covering 1782 samples",
        "recommended_env": "",
        "range_detail": "0 1782",
    },
}

MINIMAX_PARSER_AUDIT = [
    ("MiniMax-S", "unimoral_moral_typology", "109 unparseable saved samples; all reasoning-only completions"),
    ("MiniMax-S", "unimoral_factor_attribution", "2773 unparseable saved samples; all reasoning-only completions"),
    ("MiniMax-S", "unimoral_consequence_generation", "1 unparseable saved sample; reasoning-only completion"),
    ("MiniMax-M", "unimoral_factor_attribution", "1 unparseable saved sample; reasoning-only completion"),
    ("MiniMax-M", "unimoral_consequence_generation", "12 unparseable saved samples; 3 reasoning-only and 9 provider/error-text records"),
    ("MiniMax-L", "unimoral_factor_attribution", "1692 missing samples plus 16 unparseable saved samples; remaining saved gaps are provider/error-text records or one incomplete visible fragment"),
    ("MiniMax-L", "unimoral_consequence_generation", "1782 missing samples; no usable saved samples to recover"),
]

MINIMAX_LOCAL_SAMPLEBUFFER_AUDIT = [
    (
        "MiniMax-S",
        "unimoral_moral_typology",
        "3 DBs; 31 buffered samples; 11 scored samples",
        "All scored rows already appear in `unimoral-sample-predictions.csv`",
    ),
    (
        "MiniMax-M",
        "unimoral_moral_typology",
        "1 DB; 10 buffered samples; 9 scored samples",
        "Non-blocking cell; no missing release rows",
    ),
    (
        "MiniMax-M",
        "unimoral_factor_attribution",
        "1 DB; 15 buffered samples; 7 scored samples",
        "Non-blocking cell; no missing release rows",
    ),
    (
        "MiniMax-L",
        "unimoral_moral_typology",
        "3 DBs; 17 buffered samples; 3 scored samples",
        "Non-blocking cell; no missing release rows",
    ),
    (
        "MiniMax-L",
        "unimoral_factor_attribution",
        "no matching factor-attribution samplebuffer DBs",
        "Cannot recover the 1692 missing samples",
    ),
    (
        "MiniMax-L",
        "unimoral_consequence_generation",
        "no samplebuffer DB for `2026-05-17T03-30-30-00-00_unimoral-consequence-generation_Ax9iEsGjvHYpAKRrpnqexK.eval`",
        "Cannot recover the 1782 missing samples",
    ),
]

MINIMAX_COMPACT_DRY_RUN_RANGES = [
    (
        "MiniMax-S",
        "unimoral_moral_typology",
        "2613 2614;3298 3300;3304 3395;3399 3423;3431 3481;3485 3492",
    ),
    (
        "MiniMax-M",
        "unimoral_consequence_generation",
        "1111 1112;1172 1173;1334 1335;1465 1476",
    ),
    (
        "MiniMax-L",
        "unimoral_factor_attribution",
        "379 380;715 717;721 1750;2774 2775;2811 3492",
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def eval_header(path: Path) -> dict | None:
    try:
        with ZipFile(path) as zf:
            if "header.json" not in zf.namelist():
                return None
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, KeyError, json.JSONDecodeError):
        return None
    return header if isinstance(header, dict) else None


def successful_eval(log_dir: Path, task_name: str) -> Path | None:
    candidates = []
    for path in log_dir.glob("*.eval"):
        header = eval_header(path)
        if header is None or header.get("status") != "success":
            continue
        eval_meta = header.get("eval") if isinstance(header.get("eval"), dict) else {}
        if eval_meta.get("task") == task_name:
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


def eval_task_name(path: Path) -> str | None:
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
                eval_meta = header.get("eval") if isinstance(header.get("eval"), dict) else {}
                return eval_meta.get("task")
            if "_journal/start.json" in names:
                start = json.loads(zf.read("_journal/start.json").decode("utf-8"))
                eval_meta = start.get("eval") if isinstance(start.get("eval"), dict) else {}
                return eval_meta.get("task")
    except (BadZipFile, KeyError, json.JSONDecodeError):
        return None
    return None


def eval_status(path: Path) -> str:
    try:
        with ZipFile(path) as zf:
            names = zf.namelist()
            if "header.json" in names:
                header = json.loads(zf.read("header.json").decode("utf-8"))
                return str(header.get("status") or "unknown")
            if "_journal/start.json" in names:
                return "interrupted"
    except (BadZipFile, KeyError, json.JSONDecodeError):
        return "unreadable"
    return "unknown"


def eval_paths_for_task(log_dir: Path, task_name: str) -> list[Path]:
    paths = [
        path
        for path in log_dir.glob("*.eval")
        if eval_task_name(path) == task_name
    ]
    return sorted(paths, key=lambda path: path.stat().st_mtime)


def resolve_display_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def eval_error_message(path: Path) -> str:
    try:
        with ZipFile(path) as zf:
            if "header.json" not in zf.namelist():
                return ""
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, KeyError, json.JSONDecodeError):
        return ""
    error = header.get("error") if isinstance(header, dict) else None
    if not isinstance(error, dict):
        return ""
    return str(error.get("message") or "")


def iter_samples(eval_path: Path) -> list[dict]:
    samples = []
    try:
        with ZipFile(eval_path) as zf:
            for name in sorted(zf.namelist()):
                if not name.startswith("samples/") or not name.endswith(".json"):
                    continue
                sample = json.loads(zf.read(name).decode("utf-8"))
                if isinstance(sample, dict):
                    samples.append(sample)
    except (BadZipFile, KeyError, json.JSONDecodeError):
        return []
    return samples


def parsed_answer_for_task(task_name: str, sample: dict) -> tuple[str, str]:
    cache = sample.get("_artifact_parsed_answers")
    if not isinstance(cache, dict):
        cache = {}
        sample["_artifact_parsed_answers"] = cache
    if task_name in cache:
        cached_answer, cached_source = cache[task_name]
        return str(cached_answer), str(cached_source)

    record = score_record(sample)
    answer = str(record.get("answer") or "").strip()
    score_metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    score_source = str(score_metadata.get("answer_source") or "")
    if task_name == "unimoral_moral_typology":
        if answer in TYPOLOGY_PATTERNS:
            result = (answer, score_source or "score")
            cache[task_name] = result
            return result
        parsed_answer, _, answer_source = canonicalize_label_from_output(sample_output(sample), TYPOLOGY_PATTERNS)
        result = (parsed_answer or answer, answer_source)
        cache[task_name] = result
        return result
    if task_name == "unimoral_factor_attribution":
        if answer in FACTOR_PATTERNS:
            result = (answer, score_source or "score")
            cache[task_name] = result
            return result
        parsed_answer, _, answer_source = canonicalize_label_from_output(sample_output(sample), FACTOR_PATTERNS)
        result = (parsed_answer or answer, answer_source)
        cache[task_name] = result
        return result
    if task_name == "unimoral_consequence_generation":
        if answer:
            result = (answer, score_source or "score")
            cache[task_name] = result
            return result
        parsed_answer, _, answer_source = consequence_text_from_output(sample_output(sample))
        result = (parsed_answer, answer_source)
        cache[task_name] = result
        return result
    result = (answer, score_source)
    cache[task_name] = result
    return result


def prefer_sample_for_task(task_name: str, existing: dict, candidate: dict) -> dict:
    """Prefer parseable duplicates; otherwise keep the newer candidate."""
    existing_answer, _ = parsed_answer_for_task(task_name, existing)
    candidate_answer, _ = parsed_answer_for_task(task_name, candidate)
    if existing_answer and not candidate_answer:
        return existing
    return candidate


def parsed_sample_count(task_name: str, samples: list[dict]) -> int:
    return sum(1 for sample in samples if parsed_answer_for_task(task_name, sample)[0])


def combined_samples(eval_paths: list[Path], task_name: str | None = None) -> list[dict]:
    samples_by_id: dict[str, dict] = {}
    for eval_path in eval_paths:
        for sample in iter_samples(eval_path):
            sample_id = str(sample.get("id") or sample.get("uuid") or "")
            if not sample_id:
                sample_id = f"{eval_path.name}:{len(samples_by_id)}"
            if task_name is None or sample_id not in samples_by_id:
                samples_by_id[sample_id] = sample
            else:
                samples_by_id[sample_id] = prefer_sample_for_task(task_name, samples_by_id[sample_id], sample)
    return [samples_by_id[key] for key in sorted(samples_by_id)]


def score_record(sample: dict) -> dict:
    scores = sample.get("scores")
    if not isinstance(scores, dict):
        return {}
    for value in scores.values():
        if isinstance(value, dict):
            return value
    return {}


def sample_output(sample: dict) -> dict:
    return sample.get("output") if isinstance(sample.get("output"), dict) else {}


def answer_text(sample: dict, *, include_reasoning: bool = True) -> str:
    return text_from_sample_output(sample_output(sample), include_reasoning=include_reasoning)


def target_list(sample: dict) -> list[str]:
    target = sample.get("target")
    if isinstance(target, list):
        return [str(item) for item in target if item not in {None, ""}]
    if target in {None, ""}:
        return []
    return [str(target)]


def load_bertscore_lookup(path: Path | None) -> dict[tuple[str, str, str], float]:
    if path is None or not path.exists():
        return {}
    lookup: dict[tuple[str, str, str], float] = {}
    for row in read_csv(path):
        value = row.get("bert_score_f1")
        if value in {None, ""}:
            continue
        key = (str(row.get("line_label") or ""), str(row.get("task_name") or ""), str(row.get("sample_id") or ""))
        if not all(key):
            continue
        lookup[key] = float(value)
    return lookup


def sample_bertscore_average(
    *,
    line_label: str,
    task_name: str,
    samples: list[dict],
    lookup: dict[tuple[str, str, str], float],
) -> float | None:
    if not samples or not lookup:
        return None
    values = []
    for sample in samples:
        sample_id = str(sample.get("id") or sample.get("uuid") or "")
        key = (line_label, task_name, sample_id)
        if key not in lookup:
            return None
        values.append(lookup[key])
    return mean(values) if values else None


def classification_summary(samples: list[dict], patterns: dict[str, list[str]]) -> dict[str, object]:
    labels = list(patterns)
    per_class = {label: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for label in labels}
    correct = 0
    parsed = 0
    for sample in samples:
        targets = set(target_list(sample))
        answer = str(score_record(sample).get("answer") or "").strip()
        prediction = answer if answer in labels else canonicalize_label_from_output(sample_output(sample), patterns)[0]
        if prediction:
            parsed += 1
        if prediction in targets:
            correct += 1
        for label in labels:
            if label in targets:
                per_class[label]["support"] += 1
            if prediction == label and label in targets:
                per_class[label]["tp"] += 1
            elif prediction == label and label not in targets:
                per_class[label]["fp"] += 1
            elif prediction != label and label in targets:
                per_class[label]["fn"] += 1
    total_support = sum(values["support"] for values in per_class.values())
    weighted_f1 = 0.0
    for values in per_class.values():
        tp = values["tp"]
        precision = tp / (tp + values["fp"]) if tp + values["fp"] else 0.0
        recall = tp / (tp + values["fn"]) if tp + values["fn"] else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        weighted_f1 += f1 * values["support"]
    return {
        "samples": len(samples),
        "parsed": parsed,
        "accuracy": correct / len(samples) if samples else None,
        "official_weighted_f1": weighted_f1 / total_support if total_support else None,
    }


def consequence_summary(samples: list[dict]) -> dict[str, object]:
    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    bleu_values = []
    meteor_values = []
    rouge_values = []
    parsed = 0
    for sample in samples:
        scored_answer = str(score_record(sample).get("answer") or "").strip()
        raw_prediction = scored_answer or consequence_text_from_output(sample_output(sample))[0]
        prediction = normalize_whitespace(raw_prediction.lower())
        refs = [normalize_whitespace(reference).lower() for reference in target_list(sample)]
        if prediction:
            parsed += 1
        if not prediction or not refs:
            bleu_values.append(0.0)
            meteor_values.append(0.0)
            rouge_values.append(0.0)
            continue
        bleu_values.append(max(sentence_bleu_score(ref, prediction) for ref in refs))
        meteor_values.append(max(meteor_score(ref, prediction) for ref in refs))
        rouge_values.append(max(rouge.score(ref, prediction)["rougeL"].fmeasure for ref in refs))
    return {
        "samples": len(samples),
        "parsed": parsed,
        "bleu": mean(bleu_values) if bleu_values else None,
        "meteor": mean(meteor_values) if meteor_values else None,
        "rouge_l": mean(rouge_values) if rouge_values else None,
        "bert_score_f1": None,
    }


def fallback_sample_score(task_name: str, answer: str, targets: list[str]) -> float | str:
    if not targets:
        return ""
    if task_name in {"unimoral_moral_typology", "unimoral_factor_attribution"}:
        return 1.0 if answer in set(targets) else 0.0
    if task_name == "unimoral_consequence_generation":
        prediction = normalize_whitespace(answer.lower())
        refs = [normalize_whitespace(reference).lower() for reference in targets]
        return max(meteor_score(ref, prediction) for ref in refs) if refs and prediction else 0.0
    return ""


def action_lookup(release_dir: Path) -> dict[str, float]:
    lookup: dict[str, float] = {}
    for row in read_csv(release_dir / "benchmark-comparison.csv"):
        value = row.get("unimoral_action_accuracy")
        if value:
            lookup[row["line_label"]] = float(value)
    return lookup


def build_rows(
    log_root: Path,
    release_dir: Path,
    *,
    bertscore_lookup: dict[tuple[str, str, str], float] | None = None,
) -> list[dict[str, object]]:
    action = action_lookup(release_dir)
    bertscore_lookup = bertscore_lookup or {}
    rows: list[dict[str, object]] = []
    for line_label, family, size_slot, slug in MODEL_LINES:
        for task_name, task in TASKS.items():
            base = {
                "line_label": line_label,
                "family": family,
                "size_slot": size_slot,
                "task_name": task_name,
                "rq": task["rq"],
                "task_label": task["label"],
                "primary_metric": task["metric"],
                "expected_samples": task["expected"],
                "completed_samples": 0,
                "status": "missing",
                "log_path": "",
                "accuracy": "",
                "official_weighted_f1": "",
                "bleu": "",
                "meteor": "",
                "bert_score_f1": "",
                "rouge_l": "",
                "parsed_count": "",
            }
            if task_name == "unimoral_action_prediction":
                value = action.get(line_label)
                base.update(
                    {
                        "completed_samples": task["expected"] if value is not None else 0,
                        "status": "complete" if value is not None else "missing",
                        "accuracy": "" if value is None else round(value, 6),
                        "parsed_count": task["expected"] if value is not None else "",
                    }
                )
                rows.append(base)
                continue
            eval_paths = eval_paths_for_task(log_root / slug, task_name)
            if not eval_paths:
                rows.append(base)
                continue
            success_paths = [path for path in eval_paths if eval_status(path) == "success"]
            success_samples = combined_samples(success_paths, task_name)
            if len(success_samples) == task["expected"]:
                all_samples = combined_samples(eval_paths, task_name)
                success_parsed = parsed_sample_count(task_name, success_samples)
                all_parsed = parsed_sample_count(task_name, all_samples)
                if success_parsed < int(0.95 * task["expected"]) and all_parsed > success_parsed:
                    samples = all_samples
                    scoring_paths = eval_paths
                    has_success_full_coverage = False
                else:
                    samples = success_samples
                    scoring_paths = success_paths
                    has_success_full_coverage = True
            else:
                samples = combined_samples(eval_paths, task_name)
                scoring_paths = eval_paths
                has_success_full_coverage = False
            if task_name == "unimoral_moral_typology":
                summary = classification_summary(samples, TYPOLOGY_PATTERNS)
            elif task_name == "unimoral_factor_attribution":
                summary = classification_summary(samples, FACTOR_PATTERNS)
            else:
                summary = consequence_summary(samples)
            complete = summary["samples"] == task["expected"]
            parse_rate = (int(summary["parsed"]) / int(summary["samples"])) if summary["samples"] else 0.0
            if not complete:
                status = "partial"
            elif parse_rate < 0.95:
                status = "complete_parse_gap"
            elif not has_success_full_coverage:
                status = "complete_recovered_logs"
            else:
                status = "complete"
            base.update(
                {
                    "completed_samples": summary["samples"],
                    "status": status,
                    "log_path": ";".join(display_path(path) for path in scoring_paths),
                    "parsed_count": summary["parsed"],
                }
            )
            for key in ("accuracy", "official_weighted_f1", "bleu", "meteor", "bert_score_f1", "rouge_l"):
                value = summary.get(key)
                base[key] = "" if value is None else round(float(value), 6)
            if task_name == "unimoral_consequence_generation" and bertscore_lookup:
                bert_average = sample_bertscore_average(
                    line_label=line_label,
                    task_name=task_name,
                    samples=samples,
                    lookup=bertscore_lookup,
                )
                if bert_average is not None:
                    base["bert_score_f1"] = round(bert_average, 6)
            rows.append(base)
    return rows


def sample_prediction_rows(
    log_root: Path,
    *,
    bertscore_lookup: dict[tuple[str, str, str], float] | None = None,
) -> list[dict[str, object]]:
    bertscore_lookup = bertscore_lookup or {}
    rows: list[dict[str, object]] = []
    for line_label, family, size_slot, slug in MODEL_LINES:
        for task_name, task in TASKS.items():
            if task_name == "unimoral_action_prediction":
                continue
            eval_paths = eval_paths_for_task(log_root / slug, task_name)
            if not eval_paths:
                continue
            success_paths = [path for path in eval_paths if eval_status(path) == "success"]
            success_samples = combined_samples(success_paths, task_name)
            if len(success_samples) == task["expected"]:
                all_samples = combined_samples(eval_paths, task_name)
                success_parsed = parsed_sample_count(task_name, success_samples)
                all_parsed = parsed_sample_count(task_name, all_samples)
                if success_parsed < int(0.95 * task["expected"]) and all_parsed > success_parsed:
                    samples = all_samples
                    source_paths = eval_paths
                else:
                    samples = success_samples
                    source_paths = success_paths
            else:
                samples = combined_samples(eval_paths, task_name)
                source_paths = eval_paths

            for sample in samples:
                record = score_record(sample)
                answer, answer_source = parsed_answer_for_task(task_name, sample)
                metadata = sample.get("metadata") if isinstance(sample.get("metadata"), dict) else {}
                if task_name in {"unimoral_moral_typology", "unimoral_factor_attribution"}:
                    score_value = fallback_sample_score(task_name, answer, target_list(sample))
                else:
                    score_value = record.get("value", "")
                    if score_value in {None, ""}:
                        score_value = fallback_sample_score(task_name, answer, target_list(sample))
                rows.append(
                    {
                        "line_label": line_label,
                        "family": family,
                        "size_slot": size_slot,
                        "task_name": task_name,
                        "rq": task["rq"],
                        "sample_id": sample.get("id") or sample.get("uuid") or "",
                        "language": metadata.get("language", ""),
                        "scenario_id": metadata.get("scenario_id", ""),
                        "target_json": json.dumps(target_list(sample), ensure_ascii=False),
                        "prediction": answer,
                        "score_value": score_value,
                        "bert_score_f1": (
                            bertscore_lookup.get((line_label, task_name, str(sample.get("id") or sample.get("uuid") or "")), "")
                            if task_name == "unimoral_consequence_generation"
                            else ""
                        ),
                        "answer_source": answer_source,
                        "source_log_dir": display_path(log_root / slug),
                        "source_log_count": len(source_paths),
                    }
                )
    return rows


def metric_value(row: dict[str, object]) -> float | None:
    key = str(row["primary_metric"])
    value = row.get(key)
    if value in {None, ""}:
        return None
    return float(value)


def field_value(row: dict[str, object] | None, field: str) -> float | None:
    if not row:
        return None
    value = row.get(field)
    if value in {None, ""}:
        return None
    return float(value)


def coverage_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for task_name, task in TASKS.items():
        task_rows = [row for row in rows if row["task_name"] == task_name]
        complete = sum(1 for row in task_rows if row["status"] == "complete")
        reported = sum(1 for row in task_rows if str(row["status"]).startswith("complete"))
        output.append(
            {
                "rq": task["rq"],
                "task_name": task_name,
                "task_label": task["label"],
                "status": "complete" if complete == len(MODEL_LINES) else "incomplete",
                "complete_model_lines": complete,
                "reported_model_lines": reported,
                "expected_model_lines": len(MODEL_LINES),
                "expected_samples_per_model": task["expected"],
            }
        )
    return output


def failure_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        if row["status"] == "complete":
            continue
        expected = int(row["expected_samples"] or 0)
        completed = int(row["completed_samples"] or 0)
        parsed = int(row["parsed_count"] or 0) if row["parsed_count"] != "" else 0
        if completed == 0:
            category = "runtime"
            reason = "no usable eval log completed"
        elif completed < expected:
            category = "api/runtime"
            reason = f"provider run stalled or was interrupted after saving {completed}/{expected} samples"
            error_messages = [
                eval_error_message(resolve_display_path(path_text))
                for path_text in str(row["log_path"]).split(";")
                if path_text
            ]
            if any("Insufficient credits" in message or "Error code: 402" in message for message in error_messages):
                category = "api"
                reason = f"OpenRouter 402 insufficient credits after saving {completed}/{expected} samples"
        elif parsed < int(0.95 * expected):
            category = "format/parsing"
            reason = f"only {parsed}/{expected} samples had a parseable scored answer"
        else:
            category = "runtime"
            reason = "some scored samples were recovered from interrupted or error logs"
        task_filter = row["task_name"]
        model_filter = row["line_label"]
        is_minimax = str(model_filter).lower().startswith("minimax")
        route_prefix = "UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter " if is_minimax else ""
        provider_clause = "with MiniMax explicitly allowed and OPENROUTER_API_KEY available, " if is_minimax else ""
        preflight_clause = "Refresh planned ranges first with `make unimoral-missing-plan`, then " if is_minimax else ""
        if category == "format/parsing":
            next_action = (
                f"{preflight_clause}rerun parse gaps only {provider_clause}with "
                f"{route_prefix}FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='{model_filter}' TASK_FILTER='{task_filter}' "
                "scripts/run_unimoral_missing_tasks.sh."
            )
        elif completed == 0:
            next_action = (
                f"{preflight_clause}run the full missing task {provider_clause}with "
                f"{route_prefix}MODEL_FILTER='{model_filter}' TASK_FILTER='{task_filter}' scripts/run_unimoral_missing_tasks.sh."
            )
        elif completed < expected:
            next_action = (
                f"{preflight_clause}resume missing and parse-limited sample ranges after provider/API issue is resolved {provider_clause}with "
                f"{route_prefix}FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='{model_filter}' TASK_FILTER='{task_filter}' "
                "scripts/run_unimoral_missing_tasks.sh."
            )
        else:
            next_action = (
                f"{preflight_clause}rerun non-success or unparseable saved samples {provider_clause}to replace interrupted/error logs with "
                f"{route_prefix}FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='{model_filter}' TASK_FILTER='{task_filter}' "
                "scripts/run_unimoral_missing_tasks.sh."
            )
        output.append(
            {
                "line_label": row["line_label"],
                "task_name": row["task_name"],
                "status": row["status"],
                "completed_samples": completed,
                "expected_samples": expected,
                "parsed_count": parsed,
                "category": category,
                "reason": reason,
                "next_action": next_action,
                "log_path": row["log_path"],
            }
        )
    return output


def spread_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for task_name, task in TASKS.items():
        values = [metric_value(row) for row in rows if row["task_name"] == task_name and row["status"] == "complete"]
        values = [value for value in values if value is not None]
        if not values:
            output.append({"task_name": task_name, "task_label": task["label"], "model_lines": 0, "mean": "", "min": "", "max": "", "range": "", "diagnostic_read": "missing"})
            continue
        spread = max(values) - min(values)
        if spread < 0.05:
            diagnostic = "saturated"
        elif spread < 0.10:
            diagnostic = "moderately diagnostic"
        else:
            diagnostic = "diagnostic"
        output.append(
            {
                "task_name": task_name,
                "task_label": task["label"],
                "model_lines": len(values),
                "mean": round(mean(values), 6),
                "min": round(min(values), 6),
                "max": round(max(values), 6),
                "range": round(spread, 6),
                "diagnostic_read": diagnostic,
            }
        )
    return output


def ranking_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for task_name, task in TASKS.items():
        task_rows = [(row, metric_value(row)) for row in rows if row["task_name"] == task_name and row["status"] == "complete"]
        task_rows = [(row, value) for row, value in task_rows if value is not None]
        task_rows.sort(key=lambda item: item[1], reverse=True)
        for rank, (row, value) in enumerate(task_rows, start=1):
            output.append(
                {
                    "task_name": task_name,
                    "task_label": task["label"],
                    "rank": rank,
                    "line_label": row["line_label"],
                    "metric": task["metric"],
                    "value": round(value, 6),
                }
            )
    return output


FAMILY_COLORS = {
    "Qwen": "#2f6f9f",
    "MiniMax": "#8a5a44",
    "DeepSeek": "#4f7d45",
    "Llama": "#b56a33",
    "Gemma": "#7b62a3",
    "GPT4 only": "#6b7280",
}


def family_for_line(line_label: str) -> str:
    for label, family, _, _ in MODEL_LINES:
        if label == line_label:
            return family
    return ""


def color(value: float | None, low: float = 0.0, high: float = 1.0) -> str:
    if value is None:
        return "#f2f2f2"
    if high <= low:
        value = 0.72
    else:
        value = (value - low) / (high - low)
    value = max(0.0, min(1.0, value))
    red = int(241 - 205 * value)
    green = int(248 - 103 * value)
    blue = int(248 - 101 * value)
    return f"#{red:02x}{green:02x}{blue:02x}"


def task_metric_ranges(rows: list[dict[str, object]]) -> dict[str, tuple[float, float]]:
    ranges: dict[str, tuple[float, float]] = {}
    for task_name in TASKS:
        values = [
            value
            for value in (metric_value(row) for row in rows if row["task_name"] == task_name)
            if value is not None
        ]
        ranges[task_name] = (min(values), max(values)) if values else (0.0, 1.0)
    return ranges


def complete_values(rows: list[dict[str, object]], task_name: str, field: str) -> list[float]:
    values = []
    for row in rows:
        if row.get("task_name") != task_name or row.get("status") != "complete":
            continue
        value = row.get(field)
        if value in {None, ""}:
            continue
        values.append(float(value))
    return values


def value_range_text(rows: list[dict[str, object]], task_name: str, field: str) -> str:
    values = complete_values(rows, task_name, field)
    if not values:
        return "n/a"
    return f"{min(values):.3f}-{max(values):.3f}"


def card_metric_label(rows: list[dict[str, object]], task_name: str, metric: object) -> str:
    if task_name in {"unimoral_moral_typology", "unimoral_factor_attribution"}:
        return "exact-match accuracy"
    if task_name == "unimoral_consequence_generation":
        return f"BERTScore; METEOR {value_range_text(rows, task_name, 'meteor')}"
    return str(metric)


def score_scale_note(rows: list[dict[str, object]]) -> str:
    rq2_accuracy = value_range_text(rows, "unimoral_moral_typology", "accuracy")
    rq3_accuracy = value_range_text(rows, "unimoral_factor_attribution", "accuracy")
    rq4_bertscore = value_range_text(rows, "unimoral_consequence_generation", "bert_score_f1")
    rq4_meteor = value_range_text(rows, "unimoral_consequence_generation", "meteor")
    return (
        "Metric sanity check: UniMoral has four RQs. Because the frozen RQ1 source exposes only aggregate action accuracy, "
        "the main RQ1-RQ3 comparison uses one shared exact-match accuracy metric. "
        f"In the current strict-complete cells, exact-match accuracy spans RQ2 {rq2_accuracy} and RQ3 {rq3_accuracy}. "
        f"RQ4 is a generation task, so it is separated and read with semantic similarity instead of accuracy: BERTScore F1 spans {rq4_bertscore}, with METEOR {rq4_meteor} as a lexical side metric."
    )


def line_meta_for(label: str) -> tuple[str, str]:
    for line_label, family, size_slot, _ in MODEL_LINES:
        if line_label == label:
            return family, size_slot
    return "", ""


def family_group_spans() -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    current_family: str | None = None
    start_index = 0
    for index, (_, family, _, _) in enumerate(MODEL_LINES):
        if current_family is None:
            current_family = family
            start_index = index
            continue
        if family != current_family:
            spans.append((current_family, start_index, index - 1))
            current_family = family
            start_index = index
    if current_family is not None:
        spans.append((current_family, start_index, len(MODEL_LINES) - 1))
    return spans


def svg_four_task_dashboard(
    rows: list[dict[str, object]],
    coverage: list[dict[str, object]],
    spreads: list[dict[str, object]],
    rankings: list[dict[str, object]],
    path: Path,
) -> None:
    width, height = 1800, 1080
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append(
        "<style>"
        "text{font-family:Arial,sans-serif;font-size:14px;fill:#17202a}"
        ".title{font-size:28px;font-weight:700}"
        ".subtitle{font-size:15px;fill:#4b5563}"
        ".axis{font-weight:700}"
        ".small{font-size:12px;fill:#4b5563}"
        ".card{fill:#fbfcfd;stroke:#d8dee4;rx:8}"
        ".panel{fill:white;stroke:#d8dee4;rx:8}"
        "</style>"
    )
    parts.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    parts.append('<text x="36" y="44" class="title">UniMoral RQ1-RQ4 dashboard</text>')
    parts.append(
        '<text x="36" y="70" class="subtitle">Updated UniMoral view: action prediction is only RQ1; RQ2 typology, RQ3 attribution, and RQ4 consequence generation are shown separately.</text>'
    )
    parts.append(
        '<text x="36" y="92" class="subtitle">There are four RQs. RQ1-RQ3 use one shared accuracy readout; RQ4 generation quality is kept separate so readers do not compare mixed metrics in one chart.</text>'
    )

    coverage_by_task = {row["task_name"]: row for row in coverage}
    spread_by_task = {row["task_name"]: row for row in spreads}
    top_by_task = {row["task_name"]: row for row in rankings if str(row["rank"]) == "1"}
    card_w, card_h, gap = 410, 132, 20
    for idx, (task_name, task) in enumerate(TASKS.items()):
        x = 36 + idx * (card_w + gap)
        y = 122
        coverage_row = coverage_by_task.get(task_name, {})
        spread = spread_by_task.get(task_name, {})
        top = top_by_task.get(task_name, {})
        parts.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" class="card"/>')
        parts.append(f'<text x="{x + 18}" y="{y + 30}" class="axis">{task["rq"]}: {html.escape(task["label"])}</text>')
        parts.append(f'<text x="{x + 18}" y="{y + 56}" class="small">Metric: {html.escape(card_metric_label(rows, task_name, task["metric"]))}</text>')
        parts.append(
            f'<text x="{x + 18}" y="{y + 78}" class="small">Strict complete: {coverage_row.get("complete_model_lines", "")}/{coverage_row.get("expected_model_lines", "")}; reported: {coverage_row.get("reported_model_lines", "")}/{coverage_row.get("expected_model_lines", "")}</text>'
        )
        top_text = f'{top.get("line_label", "")} ({format_value(top.get("value", ""))})' if top else ""
        parts.append(f'<text x="{x + 18}" y="{y + 100}" class="small">Mean/range: {format_value(spread.get("mean", ""))} / {format_value(spread.get("range", ""))}</text>')
        parts.append(f'<text x="{x + 18}" y="{y + 122}" class="small">Top line: {html.escape(top_text)}</text>')

    panel_y = 286
    parts.append(f'<rect x="36" y="{panel_y}" width="840" height="382" class="panel"/>')
    parts.append(f'<text x="60" y="{panel_y + 34}" class="axis">Metric guide</text>')
    metric_lines = [
        "RQ1 has only aggregate action accuracy in the frozen release source.",
        "RQ2/RQ3 use the same accuracy readout in the main comparison.",
        "RQ1-RQ3 can be read horizontally because they share the same metric.",
        "RQ4 is generation, so it is not an exact-match accuracy task; read it separately.",
    ]
    for index, line in enumerate(metric_lines):
        parts.append(f'<text x="72" y="{panel_y + 74 + index * 34}" class="subtitle">{html.escape(line)}</text>')
    parts.append(f'<rect x="916" y="{panel_y}" width="848" height="382" class="panel"/>')
    parts.append(f'<text x="940" y="{panel_y + 34}" class="axis">Figure guide</text>')
    figure_lines = [
        "1. This dashboard: four RQs, coverage, and metric boundary.",
        "2. Main UniMoral figure: RQ1-RQ3 exact-match accuracy only.",
        "3. Generation figure: RQ4 BERTScore F1 and METEOR, separate from accuracy.",
        "4. Classification rankings/spread use the same RQ1-RQ3 accuracy metric.",
        "All public/reference model lines remain listed: Qwen, MiniMax, DeepSeek, Llama, Gemma S/M/L plus GPT4 Ref.",
    ]
    for index, line in enumerate(figure_lines):
        parts.append(f'<text x="952" y="{panel_y + 74 + index * 34}" class="subtitle">{html.escape(line)}</text>')

    y0 = 720
    parts.append(f'<rect x="36" y="{y0}" width="1728" height="292" fill="#fbfcfd" stroke="#d8dee4" rx="8"/>')
    parts.append(f'<text x="60" y="{y0 + 34}" class="axis">Coverage readout</text>')
    parts.append(
        f'<text x="60" y="{y0 + 62}" class="subtitle">Complete four-task lines outside MiniMax: Qwen-S/M/L, DeepSeek-S/M/L, Llama-S/M/L, Gemma-S/M/L, and GPT4 only (13/13 lines).</text>'
    )
    parts.append(
        f'<text x="60" y="{y0 + 88}" class="subtitle">MiniMax is included where scored, but strict completion is still blocked by documented parse/recovery gaps in RQ2/RQ3/RQ4.</text>'
    )
    chip_y = y0 + 124
    chips = [
        ("Qwen", "S/M/L: 4 tasks complete"),
        ("DeepSeek", "S/M/L: 4 tasks complete"),
        ("Llama", "S/M/L: 4 tasks complete"),
        ("Gemma", "S/M/L: 4 tasks complete"),
        ("GPT4 only", "reference: 4 tasks complete"),
        ("MiniMax", "caveats: see failure checklist"),
    ]
    chip_w = 260
    for idx, (family, label) in enumerate(chips):
        x = 60 + idx * 280
        fill = FAMILY_COLORS.get(family, "#6b7280")
        parts.append(f'<rect x="{x}" y="{chip_y}" width="{chip_w}" height="54" fill="white" stroke="{fill}" stroke-width="2" rx="8"/>')
        parts.append(f'<circle cx="{x + 22}" cy="{chip_y + 27}" r="7" fill="{fill}"/>')
        parts.append(f'<text x="{x + 40}" y="{chip_y + 22}" class="axis">{html.escape(family)}</text>')
        parts.append(f'<text x="{x + 40}" y="{chip_y + 42}" class="small">{html.escape(label)}</text>')
    parts.append(f'<text x="60" y="{y0 + 214}" class="small">All run lines are shown in the full score heatmap and all-line ranking below: Qwen/MiniMax/DeepSeek/Llama/Gemma S-M-L plus GPT4 Ref.</text>')
    parts.append(f'<text x="60" y="{y0 + 238}" class="small">MiniMax remaining gaps are documented in unimoral-failure-checklist.csv; the main figures avoid special cell markers.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_heatmap(rows: list[dict[str, object]], path: Path) -> None:
    task_names = CLASSIFICATION_TASK_NAMES
    lines = [line for line, _, _, _ in MODEL_LINES]
    row_lookup = {(row["line_label"], row["task_name"]): row for row in rows}
    ranges: dict[str, tuple[float, float]] = {}
    for task_name in task_names:
        values = [
            value
            for value in (
                field_value(row, "accuracy")
                for row in rows
                if row["task_name"] == task_name and row.get("status") == "complete"
            )
            if value is not None
        ]
        ranges[task_name] = (min(values), max(values)) if values else (0.0, 1.0)
    cell_w, cell_h = 220, 42
    family_x, family_w = 24, 108
    size_x, size_w = 150, 58
    line_x = 228
    left, top = 392, 204
    width = left + cell_w * len(task_names) + 52
    height = top + cell_h * len(lines) + 128
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append("<style>text{font-family:Arial,sans-serif;font-size:15px;fill:#17202a}.title{font-size:28px;font-weight:700}.subtitle{font-size:16px;fill:#334155}.axis{font-weight:700}.small{font-size:13px;fill:#334155}.tiny{font-size:12px;fill:#475569;font-weight:700}</style>")
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="28" y="42" class="title">UniMoral RQ1-RQ3 exact-match accuracy</text>')
    parts.append('<text x="28" y="74" class="subtitle">One shared metric for the three classification-style RQs, so values can be compared horizontally. Higher is better.</text>')
    parts.append('<text x="28" y="100" class="subtitle">Rows list every public/reference line that has been run; RQ4 generation is shown in a separate BERTScore/METEOR figure.</text>')
    parts.append(f'<text x="{family_x + family_w / 2}" y="{top - 52}" text-anchor="middle" class="tiny">FAMILY</text>')
    parts.append(f'<text x="{size_x + size_w / 2}" y="{top - 52}" text-anchor="middle" class="tiny">SIZE</text>')
    parts.append(f'<text x="{line_x}" y="{top - 52}" class="tiny">MODEL LINE</text>')
    for col, task_name in enumerate(task_names):
        x = left + col * cell_w
        task = TASKS[task_name]
        parts.append(f'<text x="{x + 6}" y="{top - 48}" class="axis">{task["rq"]}</text>')
        parts.append(f'<text x="{x + 6}" y="{top - 30}" class="axis">{html.escape(task["label"])}</text>')
        parts.append(f'<text x="{x + 6}" y="{top - 12}" class="small">exact-match accuracy</text>')
    for family, start_index, end_index in family_group_spans():
        y = top + start_index * cell_h - 4
        h = (end_index - start_index + 1) * cell_h - 6
        fill = FAMILY_COLORS.get(family, "#6b7280")
        parts.append(f'<rect x="{family_x}" y="{y}" width="{family_w}" height="{h}" fill="{fill}" opacity="0.12" stroke="{fill}" rx="8"/>')
        parts.append(f'<text x="{family_x + family_w / 2}" y="{y + h / 2 + 4:.1f}" text-anchor="middle" class="axis">{html.escape(family)}</text>')
        if start_index > 0:
            divider_y = y - 4
            parts.append(f'<line x1="{family_x}" y1="{divider_y}" x2="{width - 30}" y2="{divider_y}" stroke="#d8dee4"/>')
    for row_index, line in enumerate(lines):
        y = top + row_index * cell_h
        family, size_slot = line_meta_for(line)
        fill = FAMILY_COLORS.get(family, "#6b7280")
        parts.append(f'<rect x="{size_x}" y="{y + 5}" width="{size_w}" height="26" fill="{fill}" rx="13"/>')
        parts.append(f'<text x="{size_x + size_w / 2}" y="{y + 24}" text-anchor="middle" fill="#ffffff" font-weight="700">{html.escape(size_slot)}</text>')
        parts.append(f'<text x="{line_x}" y="{y + 25}" class="axis">{html.escape(line)}</text>')
        for col, task_name in enumerate(task_names):
            x = left + col * cell_w
            row = row_lookup.get((line, task_name))
            value = field_value(row, "accuracy") if row and row.get("status") == "complete" else None
            low, high = ranges[task_name]
            label = "n/a" if value is None else f"{value:.3f}"
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 8}" height="{cell_h - 8}" fill="{color(value, low, high)}" stroke="#c9cdd1" stroke-width="1.2" rx="4"/>')
            parts.append(f'<text x="{x + 14}" y="{y + 26}" class="axis">{label}</text>')
    parts.append(f'<text x="28" y="{height - 52}" class="small">Rows include all public model lines plus the GPT4 reference. S/M/L are planning slots for within-family scaling, not a universal vendor taxonomy.</text>')
    parts.append(f'<text x="28" y="{height - 28}" class="small">This main figure uses strict-complete exact-match accuracy cells only; parse gaps remain in the audit tables.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_generation_quality(rows: list[dict[str, object]], path: Path) -> None:
    task_name = GENERATION_TASK_NAME
    task_rows = [
        row
        for row in rows
        if row["task_name"] == task_name
        and field_value(row, "bert_score_f1") is not None
        and field_value(row, "meteor") is not None
    ]
    task_rows.sort(key=lambda row: field_value(row, "bert_score_f1") or -1.0, reverse=True)
    width = 1220
    top = 190
    row_h = 44
    row_gap = 10
    height = top + len(task_rows) * (row_h + row_gap) + 126
    label_x = 42
    size_x = 186
    bert_x = 268
    bert_w = 420
    meteor_x = 804
    meteor_w = 270
    bert_min, bert_max = 0.60, 0.75
    meteor_min, meteor_max = 0.07, 0.16

    def scaled_width(value: float | None, low: float, high: float, width_value: int) -> float:
        if value is None or high <= low:
            return 0.0
        position = max(0.0, min(1.0, (value - low) / (high - low)))
        return width_value * position

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append("<style>text{font-family:Arial,sans-serif;font-size:15px;fill:#17202a}.title{font-size:30px;font-weight:700}.metric{font-size:18px;font-weight:700;fill:#17202a}.subtitle{font-size:16px;fill:#334155}.axis{font-weight:700}.small{font-size:13px;fill:#334155}.tiny{font-size:12px;fill:#475569;font-weight:700}</style>")
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="36" y="42" class="title">UniMoral RQ4 generation quality</text>')
    parts.append('<text x="36" y="74" class="subtitle">RQ4 asks models to generate consequences, so it is not mixed with the RQ1-RQ3 accuracy chart.</text>')
    parts.append('<text x="36" y="100" class="subtitle">Both metrics are higher-better. BERTScore F1 reads semantic similarity; METEOR reads lexical overlap.</text>')
    parts.append('<text x="36" y="124" class="subtitle">Each metric panel uses its own axis so within-metric differences are visible.</text>')
    parts.append(f'<text x="{bert_x}" y="{top - 44}" class="metric">BERTScore F1</text>')
    parts.append(f'<text x="{meteor_x}" y="{top - 44}" class="metric">METEOR</text>')
    for tick in (0.60, 0.65, 0.70, 0.75):
        x = bert_x + bert_w * ((tick - bert_min) / (bert_max - bert_min))
        parts.append(f'<line x1="{x:.2f}" y1="{top - 12}" x2="{x:.2f}" y2="{height - 76}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{x:.2f}" y="{top - 20}" text-anchor="middle" class="small">{tick:.2f}</text>')
    for tick in (0.07, 0.10, 0.13, 0.16):
        x = meteor_x + meteor_w * ((tick - meteor_min) / (meteor_max - meteor_min))
        parts.append(f'<line x1="{x:.2f}" y1="{top - 12}" x2="{x:.2f}" y2="{height - 76}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{x:.2f}" y="{top - 20}" text-anchor="middle" class="small">{tick:.2f}</text>')
    for index, row in enumerate(task_rows):
        y = top + index * (row_h + row_gap)
        family, size_slot = line_meta_for(str(row["line_label"]))
        fill = FAMILY_COLORS.get(family, "#6b7280")
        bert_value = field_value(row, "bert_score_f1")
        meteor = field_value(row, "meteor")
        parts.append(f'<text x="{label_x}" y="{y + 27}" class="axis">{html.escape(str(row["line_label"]))}</text>')
        parts.append(f'<rect x="{size_x}" y="{y + 8}" width="46" height="24" fill="{fill}" rx="12"/>')
        parts.append(f'<text x="{size_x + 23}" y="{y + 26}" text-anchor="middle" fill="#ffffff" font-weight="700">{html.escape(size_slot)}</text>')
        parts.append(f'<rect x="{bert_x}" y="{y + 5}" width="{bert_w}" height="{row_h - 10}" fill="#eef2f7" rx="8"/>')
        bert_bar_w = scaled_width(bert_value, bert_min, bert_max, bert_w)
        parts.append(f'<rect x="{bert_x}" y="{y + 5}" width="{bert_bar_w:.1f}" height="{row_h - 10}" fill="{fill}" rx="8"/>')
        parts.append(f'<text x="{bert_x + bert_w + 12}" y="{y + 28}" class="axis">{bert_value:.3f}</text>')
        parts.append(f'<rect x="{meteor_x}" y="{y + 5}" width="{meteor_w}" height="{row_h - 10}" fill="#eef2f7" rx="8"/>')
        meteor_bar_w = scaled_width(meteor, meteor_min, meteor_max, meteor_w)
        parts.append(f'<rect x="{meteor_x}" y="{y + 5}" width="{meteor_bar_w:.1f}" height="{row_h - 10}" fill="{fill}" opacity="0.72" rx="8"/>')
        parts.append(f'<text x="{meteor_x + meteor_w + 12}" y="{y + 28}" class="axis">{meteor:.3f}</text>')
    parts.append(f'<text x="36" y="{height - 52}" class="small">Rows require usable BERTScore F1 and METEOR values. This figure is intentionally separate from the RQ1-RQ3 accuracy figure.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_rankings(rows: list[dict[str, object]], path: Path) -> None:
    width = 1240
    row_h = 24
    task_rows_by_name: dict[str, list[dict[str, object]]] = {}
    for task_name in CLASSIFICATION_TASK_NAMES:
        task_rows = [
            row
            for row in rows
            if row.get("task_name") == task_name and row.get("status") == "complete" and field_value(row, "accuracy") is not None
        ]
        task_rows.sort(key=lambda row: float(row["accuracy"]), reverse=True)
        task_rows_by_name[task_name] = task_rows
    panel_heights = {
        task_name: 54 + max(1, len(task_rows)) * row_h + 24
        for task_name, task_rows in task_rows_by_name.items()
    }
    height = 58 + sum(panel_heights.values())
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append("<style>text{font-family:Arial,sans-serif;font-size:12px;fill:#17202a}.title{font-size:20px;font-weight:700}.subtitle{fill:#4b5563}.axis{font-weight:700}.small{font-size:11px;fill:#4b5563}</style>")
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="24" y="32" class="title">UniMoral per-task model rankings: exact-match accuracy (RQ1-RQ3)</text>')
    parts.append('<text x="24" y="52" class="subtitle">Same metric in every panel: exact-match accuracy. RQ4 generation is intentionally not mixed into this ranking.</text>')
    y_cursor = 74
    for task_name in CLASSIFICATION_TASK_NAMES:
        task = TASKS[task_name]
        panel_h = panel_heights[task_name]
        y0 = y_cursor
        task_rows = task_rows_by_name[task_name]
        parts.append(f'<rect x="20" y="{y0 - 22}" width="{width - 40}" height="{panel_h - 10}" fill="#fbfcfd" stroke="#d8dee4" rx="8"/>')
        parts.append(f'<text x="36" y="{y0}" class="axis">{task["rq"]}: {html.escape(task["label"])} (exact-match accuracy)</text>')
        max_value = max((float(row["accuracy"]) for row in task_rows), default=1.0)
        for idx, row in enumerate(task_rows):
            y = y0 + 26 + idx * row_h
            value = float(row["accuracy"])
            bar_w = 760 * value / max_value if max_value else 0
            family, size_slot = line_meta_for(str(row["line_label"]))
            fill = FAMILY_COLORS.get(family, "#6b7280")
            parts.append(f'<text x="44" y="{y + 14}">{idx + 1}. {html.escape(str(row["line_label"]))}</text>')
            parts.append(f'<rect x="178" y="{y + 1}" width="38" height="18" fill="{fill}" rx="9"/>')
            parts.append(f'<text x="197" y="{y + 14}" text-anchor="middle" fill="#ffffff" font-weight="700">{html.escape(size_slot)}</text>')
            parts.append(f'<rect x="246" y="{y}" width="{bar_w:.1f}" height="18" fill="{fill}" rx="3"/>')
            parts.append(f'<text x="{256 + bar_w:.1f}" y="{y + 14}">{value:.3f}</text>')
        y_cursor += panel_h
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_spread(rows: list[dict[str, object]], path: Path) -> None:
    width, height = 980, 330
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append("<style>text{font-family:Arial,sans-serif;font-size:12px;fill:#17202a}.title{font-size:20px;font-weight:700}.subtitle{font-size:12px;fill:#4b5563}.axis{font-weight:700}</style>")
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="24" y="34" class="title">UniMoral task spread and saturation: exact-match accuracy</text>')
    parts.append('<text x="24" y="58" class="subtitle">Same metric for RQ1-RQ3. Longer bars mean more cross-line separation; short bars indicate near-saturation.</text>')
    spread_rows = []
    for task_name in CLASSIFICATION_TASK_NAMES:
        values = [
            value
            for value in (field_value(row, "accuracy") for row in rows if row["task_name"] == task_name and row["status"] == "complete")
            if value is not None
        ]
        if values:
            spread_rows.append((TASKS[task_name]["label"], max(values) - min(values)))
    max_range = max((spread for _, spread in spread_rows), default=1.0)
    for idx, (label, spread) in enumerate(spread_rows):
        y = 92 + idx * 50
        bar_w = 460 * spread / max_range if max_range else 0
        parts.append(f'<text x="36" y="{y + 15}" class="axis">{html.escape(str(label))}</text>')
        parts.append(f'<rect x="250" y="{y}" width="{bar_w:.1f}" height="22" fill="#3c78d8" rx="3"/>')
        parts.append(f'<text x="732" y="{y + 16}">accuracy range {spread:.3f}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def update_manifest(release_dir: Path) -> None:
    manifest_path = release_dir / "release-manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    task_count = len(TASKS)
    model_line_count = len(MODEL_LINES)
    family_labels = list(dict.fromkeys(family for _, family, _, _ in MODEL_LINES))
    total_samples = sum(int(task["expected"]) for task in TASKS.values()) * model_line_count
    coverage_path = release_dir / "unimoral-coverage.csv"
    coverage_rows_for_status = read_csv(coverage_path) if coverage_path.exists() else []
    all_complete = bool(coverage_rows_for_status) and all(row.get("status") == "complete" for row in coverage_rows_for_status)
    mode = "benchmark_faithful" if all_complete else "benchmark_faithful; documented_incomplete"

    benchmarks = manifest.setdefault("benchmarks", [])
    unimoral_row = next((row for row in benchmarks if row.get("benchmark") == "UniMoral"), None)
    if unimoral_row is None:
        unimoral_row = {"benchmark": "UniMoral"}
        benchmarks.append(unimoral_row)
    unimoral_row.update(
        {
            "evaluated_lines": task_count * model_line_count,
            "models_covered": len(family_labels),
            "modes": mode,
            "samples": total_samples,
            "task_types": task_count,
        }
    )
    counts = manifest.setdefault("counts", {})
    try:
        counts["authoritative_tasks"] = sum(int(row.get("evaluated_lines") or 0) for row in benchmarks)
        counts["benchmark_faithful_tasks"] = sum(
            int(row.get("evaluated_lines") or 0)
            for row in benchmarks
            if "benchmark_faithful" in str(row.get("modes") or "")
        )
        counts["proxy_tasks"] = sum(
            int(row.get("evaluated_lines") or 0)
            for row in benchmarks
            if str(row.get("modes") or "") == "proxy"
        )
        counts["total_samples"] = sum(int(row.get("samples") or 0) for row in benchmarks)
    except (TypeError, ValueError):
        counts["total_samples"] = total_samples

    entry_points = manifest.setdefault("entry_points", {})
    entry_points.update(
        {
            "unimoral_full_benchmark": "results/release/2026-04-19-option1/unimoral-full-benchmark.csv",
            "unimoral_coverage": "results/release/2026-04-19-option1/unimoral-coverage.csv",
            "unimoral_task_spread": "results/release/2026-04-19-option1/unimoral-task-spread.csv",
            "unimoral_model_rankings": "results/release/2026-04-19-option1/unimoral-model-rankings.csv",
            "unimoral_sample_predictions": "results/release/2026-04-19-option1/unimoral-sample-predictions.csv",
            "unimoral_failure_checklist": "results/release/2026-04-19-option1/unimoral-failure-checklist.csv",
            "unimoral_completion_audit": "results/release/2026-04-19-option1/unimoral-completion-audit.md",
            "unimoral_four_task_dashboard_figure": "figures/release/option1_unimoral_four_task_dashboard.svg",
            "unimoral_task_heatmap_figure": "figures/release/option1_unimoral_task_heatmap.svg",
            "unimoral_generation_quality_figure": "figures/release/option1_unimoral_generation_quality.svg",
            "unimoral_task_rankings_figure": "figures/release/option1_unimoral_task_rankings.svg",
            "unimoral_task_spread_figure": "figures/release/option1_unimoral_task_spread.svg",
        }
    )
    bertscore_path = release_dir / "unimoral-rq4-bertscore.csv"
    if bertscore_path.exists() and bertscore_path.stat().st_size > 0:
        entry_points["unimoral_rq4_bertscore"] = "results/release/2026-04-19-option1/unimoral-rq4-bertscore.csv"
    entry_points["unimoral_minimax_resume_plan"] = "results/release/2026-04-19-option1/unimoral-minimax-resume-plan.md"
    for key, values in {
        "tables": [
            "unimoral-full-benchmark.csv",
            "unimoral-coverage.csv",
            "unimoral-task-spread.csv",
            "unimoral-model-rankings.csv",
            "unimoral-sample-predictions.csv",
            "unimoral-failure-checklist.csv",
            "unimoral-completion-audit.md",
            "unimoral-minimax-resume-plan.md",
            *(["unimoral-rq4-bertscore.csv"] if bertscore_path.exists() and bertscore_path.stat().st_size > 0 else []),
        ],
        "figures": [
            "figures/release/option1_unimoral_four_task_dashboard.svg",
            "figures/release/option1_unimoral_task_heatmap.svg",
            "figures/release/option1_unimoral_generation_quality.svg",
            "figures/release/option1_unimoral_task_rankings.svg",
            "figures/release/option1_unimoral_task_spread.svg",
        ],
    }.items():
        existing = manifest.setdefault(key, [])
        for value in values:
            if value not in existing:
                existing.append(value)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_minimax_resume_plan(release_dir: Path, failures: list[dict[str, object]]) -> None:
    path = release_dir / "unimoral-minimax-resume-plan.md"
    failure_by_key = {
        (str(row.get("line_label", "")), str(row.get("task_name", ""))): row
        for row in failures
        if str(row.get("line_label", "")).startswith("MiniMax") and str(row.get("status", "")) != "complete"
    }
    planned_keys = list(MINIMAX_RESUME_PLAN) if failure_by_key else []
    lines = [
        "# UniMoral MiniMax Resume Plan",
        "",
        "This file is a provider-free handoff for the remaining UniMoral RQ2/RQ3/RQ4 blockers. It documents the current MiniMax gaps without granting permission to run MiniMax.",
        "",
        "Run these only after MiniMax runs are explicitly allowed, `UNIMORAL_ALLOW_MINIMAX=1` is set, and a valid `OPENROUTER_API_KEY` or direct MiniMax route is available.",
        "",
        "## Current State",
        "",
    ]
    if not planned_keys:
        lines.extend(
            [
                "No MiniMax blockers are listed in `unimoral-failure-checklist.csv`.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "| Line | Task | Failure status | Saved coverage | Dry-run range plan |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for key in planned_keys:
            row = failure_by_key.get(key, {"line_label": key[0], "task_name": key[1], "status": "parse_gap_dry_run"})
            plan = MINIMAX_RESUME_PLAN.get(key, {})
            completed = row.get("completed_samples", "")
            expected = row.get("expected_samples", "")
            parsed = row.get("parsed_count", "")
            coverage = (
                f"{completed}/{expected} logged; {parsed}/{expected} parseable"
                if key in failure_by_key
                else plan.get("evidence") or f"{completed}/{expected} logged; {parsed}/{expected} parseable"
            )
            range_summary = plan.get("range_summary", "Run the dry-run command below to print current ranges.")
            lines.append(
                f"| `{row.get('line_label', '')}` | `{row.get('task_name', '')}` | `{row.get('status', '')}` | {coverage} | {range_summary} |"
            )
        lines.extend(
            [
                "",
                "Rows marked `parse_gap_dry_run` were not severe enough to appear in `unimoral-failure-checklist.csv`, but the provider-free launcher dry-run still found parse-limited samples worth replacing during the MiniMax cleanup pass.",
                "",
                "## Parser Recovery Audit",
                "",
                "A provider-free scan of the remaining MiniMax gaps found no safe scorer-only recovery path. Do not infer labels from hidden reasoning, prompt context, model IDs, or incomplete visible fragments.",
                "",
                "| Line | Task | Unrecoverable saved-state evidence |",
                "| --- | --- | --- |",
            ]
        )
        for line_label, task_name, evidence in MINIMAX_PARSER_AUDIT:
            lines.append(f"| `{line_label}` | `{task_name}` | {evidence} |")
        lines.extend(
            [
                "",
                "## Local Samplebuffer Audit",
                "",
                "Inspect's local samplebuffer cache was also checked under `~/Library/Application Support/inspect_ai/samplebuffer/`. This found small interrupted-shard buffers, but no provider-free path to close the remaining MiniMax blockers.",
                "",
                "| Line | Task | Buffered state | Release impact |",
                "| --- | --- | --- | --- |",
            ]
        )
        for line_label, task_name, buffered_state, release_impact in MINIMAX_LOCAL_SAMPLEBUFFER_AUDIT:
            lines.append(f"| `{line_label}` | `{task_name}` | {buffered_state} | {release_impact} |")
        lines.extend(
            [
                "",
                "The MiniMax trace files for the failed consequence-generation run contained request telemetry only. The eval config had `log_samples=true` but `log_model_api=false`, and no response-body fields such as `choices`, `messages`, `content`, `prompt`, `completion`, or `sample_id` were present in the MiniMax trace files.",
                "",
                "The broader Inspect application-support trace directory was checked as well. Those global traces had no matching `MiniMax`, failed RQ4 eval ID, or response-body fields, so they do not provide an alternate recovery source.",
                "",
                "Redacted shell-history and older-checkout breadcrumbs were checked too. The history points to UniMoral dataset setup under `~/Desktop/moral-psych-data/unimoral` and an older `~/Desktop/moral-psychology-benchmark` checkout, but not to completed RQ2/RQ3/RQ4 MiniMax result artifacts. The older checkout contains UniMoral RQ2/RQ3/RQ4 task-builder code and prompts, while its saved Inspect UniMoral logs are action-prediction runs only.",
                "",
                'The sibling `~/Desktop/cei-jenny-main-sync` checkout was also inspected. Its release catalog reports UniMoral as "Action prediction only", and the checkout contains RQ2/RQ3/RQ4 task-builder code/prompts but no saved MiniMax RQ2/RQ3/RQ4 release artifacts or Inspect logs.',
                "",
                "Local Time Machine snapshots were listed for May 17, 2026, but no browsable backup content was mounted under `/Volumes/.timemachine`. Do not attempt a snapshot restore or mount operation without explicit user approval.",
                "",
                "The `results/inspect/full-runs/2026-05-16-unimoral-full/minimax_l/` transcripts were checked after a Spotlight index search. They contain run starts and one old `args[@]: unbound variable` shell failure for MiniMax-L factor attribution, but no model predictions. The current launcher keeps the empty-args expansion guarded under `set -u`, with a regression test in `tests/test_provider_config.py`.",
                "",
                "Git LFS and ignored local payloads were checked. There are no Git LFS files or local LFS objects. The ignored MiniMax-L full-run `.eval` files match the release tables exactly: `unimoral_factor_attribution` has 1800 unique logged samples locally and 1800 release prediction rows, while `unimoral_consequence_generation` has 0 local samples and 0 release prediction rows. No ignored success shard was omitted from `unimoral-sample-predictions.csv`.",
                "",
                "The MiniMax smoke/probe logs under `results/inspect/logs/2026-05-16-unimoral-smoke/` and `results/inspect/logs/2026-05-17-unimoral-smoke/` were checked. They contain 22 tiny MiniMax eval archives, map only to MiniMax-S/M model routes, and do not add any same-line sample IDs missing from the release tables. They should not be used to fill the MiniMax-L blockers.",
                "",
                "A follow-up provider-free filesystem search across the local Desktop and Inspect application-support paths found the current full-run logs, those tiny smoke/probe logs, older UniMoral action-prediction logs, and unrelated MiniMax benchmark logs, but no additional full MiniMax RQ2/RQ3/RQ4 archives that close the remaining blockers.",
                "",
                "Spotlight metadata search found only the current repo artifacts/caches plus an older `~/Desktop/moral-psych-harness/CEI-openai-update` checkout. That checkout contains UniMoral action-prediction exploratory summaries and prompts, but no UniMoral RQ2/RQ3/RQ4 eval archives or release prediction CSVs.",
                "",
                "Local Git branches, remote refs, stashes, and reflog-retained artifact commits were checked. Every retained `unimoral-sample-predictions.csv` snapshot still has 136782 rows, 1800 MiniMax-L factor-attribution rows, and 0 MiniMax-L consequence-generation rows; no historical release artifact closes the remaining MiniMax blockers.",
                "",
                "An exact home-directory search for duplicate UniMoral release CSVs and likely UniMoral/CEI release archives found only the current repo's release/full-run files and no alternate CSV set or compressed bundle to recover from.",
                "",
                "GitHub remote-side recovery was checked too: the release repo currently has zero Actions artifacts, code search found no separate `unimoral-sample-predictions` artifact, and merged PR #1 has no comments or attachment links with recoverable UniMoral RQ2/RQ3/RQ4 outputs.",
                "",
                'Google Drive was searched for exported or shared UniMoral artifacts using exact and broad terms including `unimoral sample predictions`, `unimoral full benchmark`, `unimoral-rq4-bertscore`, `unimoral_factor_attribution`, `unimoral_consequence_generation`, `MiniMax-L factor attribution`, `MiniMax-L consequence generation`, `CEI moral psych release`, and the failed MiniMax-L consequence-generation eval ID. The only relevant hits were the May 2026 working doc/deck materials, which state the extra UniMoral tasks were still "not yet scored" or action items to check; no Drive result contained saved MiniMax RQ2/RQ3/RQ4 predictions or release CSV artifacts.',
                "",
                "## Dry-Run Check",
                "",
                "Use this provider-free wrapper before any provider call to refresh the planned ranges:",
                "",
                "```bash",
                "make unimoral-missing-plan",
                "```",
                "",
                "Equivalent raw command:",
                "",
                "```bash",
                "UNIMORAL_DRY_RUN=1 FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 UNIMORAL_ROUTE_MODE=openrouter MODEL_FILTER='MiniMax-S,MiniMax-M,MiniMax-L' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh",
                "```",
                "",
                "For `MiniMax-S` factor attribution, the unmerged plan has 511 tiny ranges. The best practical dry-run setting observed on May 17, 2026 was:",
                "",
                "```bash",
                "UNIMORAL_DRY_RUN=1 FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 UNIMORAL_RERUN_UNPARSED_MAX_GAP=3 UNIMORAL_ROUTE_MODE=openrouter MODEL_FILTER='MiniMax-S' TASK_FILTER='unimoral_factor_attribution' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh",
                "```",
                "",
                "A full MiniMax provider-free refresh with `UNIMORAL_RERUN_UNPARSED_MAX_GAP=3` on May 17, 2026 kept the same missing cells but merged nearby gaps for other cells too. Notable compact ranges were:",
                "",
                "| Line | Task | `max_gap=3` dry-run ranges |",
                "| --- | --- | --- |",
            ]
        )
        for line_label, task_name, ranges in MINIMAX_COMPACT_DRY_RUN_RANGES:
            lines.append(f"| `{line_label}` | `{task_name}` | `{ranges}` |")
        lines.extend(
            [
                "",
                "Use these compact ranges only when you intentionally want to rerun a few already-parseable samples between close gaps to reduce process startup overhead.",
                "",
                "A fresh provider-free preflight on May 17, 2026 at 15:05 America/New_York confirmed the same compact ranges and reported `key_state=missing` for the OpenRouter MiniMax route. No provider calls were made during that preflight.",
                "",
                "## Recommended Execution",
                "",
                "Run cells separately so a MiniMax failure does not hide which cell advanced:",
                "",
            ]
        )
        for key in planned_keys:
            plan = MINIMAX_RESUME_PLAN.get(key, {})
            recommended_env = str(plan.get("recommended_env", ""))
            lines.extend(
                [
                    f"### {key[0]} / {key[1]}",
                    "",
                    "```bash",
                    f"{recommended_env}UNIMORAL_ALLOW_MINIMAX=1 UNIMORAL_ROUTE_MODE=openrouter FORCE_RERUN=1 UNIMORAL_RERUN_UNPARSED=1 MODEL_FILTER='{key[0]}' TASK_FILTER='{key[1]}' VENV_PYTHON=/opt/anaconda3/bin/python scripts/run_unimoral_missing_tasks.sh",
                    "```",
                    "",
                    f"Range detail: `{plan.get('range_detail', 'refresh with UNIMORAL_DRY_RUN=1 before executing')}`",
                    "",
                ]
            )
        lines.extend(
            [
                "## After Reruns",
                "",
                "Rebuild and verify the release artifacts:",
                "",
                "```bash",
                "/opt/anaconda3/bin/python scripts/build_unimoral_artifacts.py",
                "/opt/anaconda3/bin/python scripts/verify_unimoral_completion.py",
                "make audit VENV_PYTHON=/opt/anaconda3/bin/python",
                "```",
                "",
                "Strict completion requires `unimoral-failure-checklist.csv` to be empty and RQ1-RQ4 coverage to show 16/16 strict-complete model lines.",
                "",
            ]
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_completion_audit(
    release_dir: Path,
    coverage: list[dict[str, object]],
    failures: list[dict[str, object]],
) -> None:
    path = release_dir / "unimoral-completion-audit.md"
    sample_predictions = release_dir / "unimoral-sample-predictions.csv"
    sample_rows = max(0, sum(1 for _ in sample_predictions.open(encoding="utf-8")) - 1) if sample_predictions.exists() else 0
    expected_prediction_rows = sum(
        int(task["expected"])
        for task_name, task in TASKS.items()
        if task_name != "unimoral_action_prediction"
    ) * len(MODEL_LINES)
    coverage_complete = bool(coverage) and all(row.get("status") == "complete" for row in coverage)
    coverage_summary = ", ".join(
        f"{row.get('task_name')} {row.get('complete_model_lines')}/{row.get('expected_model_lines')} {row.get('status')}"
        for row in coverage
    )
    failure_summary = "; ".join(
        f"{row.get('line_label')} {row.get('task_name')} {row.get('status')} {row.get('completed_samples')}/{row.get('expected_samples')} parsed={row.get('parsed_count')}"
        for row in failures
    ) or "none"
    full_rows = read_csv(release_dir / "unimoral-full-benchmark.csv") if (release_dir / "unimoral-full-benchmark.csv").exists() else []
    prediction_rows = read_csv(sample_predictions) if sample_predictions.exists() else []
    full_by_pair = {
        (str(row.get("line_label", "")), str(row.get("task_name", ""))): row
        for row in full_rows
    }
    expected_pairs = {(line_label, task_name) for line_label, _, _, _ in MODEL_LINES for task_name in TASKS}
    actual_pairs = set(full_by_pair)
    prediction_counts: dict[tuple[str, str], int] = {}
    prediction_keys: list[tuple[str, str, str]] = []
    for row in prediction_rows:
        key = (str(row.get("line_label", "")), str(row.get("task_name", "")))
        prediction_counts[key] = prediction_counts.get(key, 0) + 1
        prediction_keys.append((*key, str(row.get("sample_id", ""))))

    total_prediction_gap = 0
    strict_blocker_lines: list[str] = []
    missing_pairs = sorted(expected_pairs - actual_pairs)
    extra_pairs = sorted(actual_pairs - expected_pairs)
    duplicate_model_task_count = len(full_rows) - len(actual_pairs)
    if missing_pairs:
        strict_blocker_lines.append(
            f"- `unimoral-full-benchmark.csv`: {len(missing_pairs)} expected model-task rows missing."
        )
    if extra_pairs:
        strict_blocker_lines.append(
            f"- `unimoral-full-benchmark.csv`: {len(extra_pairs)} unexpected model-task rows present."
        )
    if duplicate_model_task_count:
        strict_blocker_lines.append(
            f"- `unimoral-full-benchmark.csv`: {duplicate_model_task_count} duplicate model-task rows prevent strict completion."
        )
    duplicate_prediction_count = len(prediction_keys) - len(set(prediction_keys))
    if duplicate_prediction_count:
        strict_blocker_lines.append(
            f"- `unimoral-sample-predictions.csv`: {duplicate_prediction_count} duplicate "
            "line/task/sample prediction rows prevent strict completion."
        )
    for line_label, _, _, _ in MODEL_LINES:
        for task_name, task in TASKS.items():
            if task_name == "unimoral_action_prediction":
                continue
            expected = int(task["expected"])
            prediction_count = prediction_counts.get((line_label, task_name), 0)
            row = full_by_pair.get((line_label, task_name))
            status_value = str(row.get("status", "missing_row")) if row else "missing_row"
            gap = max(0, expected - prediction_count)
            if gap:
                total_prediction_gap += gap
                strict_blocker_lines.append(
                    f"- `{line_label}` `{task_name}`: {gap} sample predictions missing "
                    f"({prediction_count}/{expected}); status `{status_value}`."
                )
            elif status_value != "complete":
                strict_blocker_lines.append(
                    f"- `{line_label}` `{task_name}`: no sample-count gap "
                    f"({prediction_count}/{expected}) but status `{status_value}` prevents strict completion."
                )
    sample_predictions_complete = sample_rows == expected_prediction_rows and duplicate_prediction_count == 0
    failures_clear = not failures
    strict_complete = coverage_complete and sample_predictions_complete and failures_clear and not strict_blocker_lines
    status = "achieved" if strict_complete else "not achieved"
    figures_evidence = (
        "Structural release gate can run without documented incomplete-cell caveats once artifacts are regenerated."
        if strict_complete
        else "Structural release gate allows documented incomplete cells until MiniMax blockers are resolved."
    )
    gate_sentence = (
        "Strict completion is achieved by `scripts/verify_unimoral_completion.py`; `unimoral-failure-checklist.csv` is empty and `unimoral-coverage.csv` has complete RQ2/RQ3/RQ4 rows."
        if strict_complete
        else "Strict completion is blocked by saved-artifact gaps or consistency failures. Do not mark the objective complete while `scripts/verify_unimoral_completion.py` fails, `unimoral-failure-checklist.csv` is nonempty, or `unimoral-coverage.csv` has incomplete RQ2/RQ3/RQ4 rows."
    )
    lines = [
        "# UniMoral Completion Audit",
        "",
        f"Status: **{status}**.",
        "",
        "Objective: complete UniMoral RQ2/RQ3/RQ4 for the existing release model set, update code/results/figures/docs, validate consistency, and commit/push a clean branch.",
        "",
        "## Prompt-to-Artifact Checklist",
        "",
        "| Requirement | Evidence artifact or command | Current evidence | Status |",
        "| --- | --- | --- | --- |",
        "| RQ2/RQ3/RQ4 task definitions exist | `src/inspect/evals/unimoral.py`, `src/inspect/evals/moral_psych.py`, `scripts/verify_unimoral_task_builders.py` | Provider-free task-builder verification covers RQ1-RQ4 registry entries. | structurally covered |",
        "| Results cover existing model set | `unimoral-coverage.csv`, `unimoral-full-benchmark.csv`, strict `scripts/verify_unimoral_completion.py` | "
        + coverage_summary
        + f" | {'achieved' if coverage_complete else 'incomplete'} |",
        "| Sample-level predictions are complete for RQ2/RQ3/RQ4 | `unimoral-sample-predictions.csv` | "
        + f"{sample_rows} rows present; strict expected count is {expected_prediction_rows}. | {'achieved' if sample_predictions_complete else 'incomplete'} |",
        "| Known failures are empty | `unimoral-failure-checklist.csv` | "
        + f"{len(failures)} rows: {failure_summary}. | {'achieved' if failures_clear else 'incomplete'} |",
        f"| Figures and release docs rebuild from tracked artifacts | `scripts/build_unimoral_artifacts.py`, `make audit` | {figures_evidence} | {'covered' if strict_complete else 'covered with caveat'} |",
        "| MiniMax is not run without explicit authorization | `make unimoral-missing-plan`, `scripts/run_unimoral_missing_tasks.sh`, `tests/test_provider_config.py` | `make unimoral-missing-plan` is dry-run only; non-dry-run MiniMax lines require `UNIMORAL_ALLOW_MINIMAX=1` and explicit authorization. | guarded |",
        "| Secrets or credentials are not introduced | Branch diff credential-pattern scan against `origin/main...HEAD` | No literal provider keys or tokens were found; provider key references are environment-variable names only. | covered |",
        "| Clean committed branch | `git status --short --branch`, `git rev-list --left-right --count HEAD...@{upstream}` | Post-generation check required: this generated artifact cannot prove the final commit/push state; the final operator report must cite clean status and 0/0 ahead-behind after the last push. | external final check |",
        "",
        "## CSV-Level Strict Blockers",
        "",
        f"Total strict sample prediction gap: **{total_prediction_gap}** rows.",
        "",
        *(strict_blocker_lines or ["No CSV-level strict blockers remain; `scripts/verify_unimoral_completion.py` remains the source of truth."]),
        "",
        "## Completion Gate",
        "",
        gate_sentence,
        "",
        "No MiniMax provider calls are made by generating this audit.",
    ]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def log_root_has_evals(log_root: Path) -> bool:
    return any(log_root.glob("*.eval")) or any(log_root.glob("*/*.eval"))


def existing_release_tables_available(release_dir: Path) -> bool:
    required = [
        "unimoral-full-benchmark.csv",
        "unimoral-coverage.csv",
        "unimoral-task-spread.csv",
        "unimoral-model-rankings.csv",
        "unimoral-sample-predictions.csv",
        "unimoral-failure-checklist.csv",
    ]
    return all((release_dir / filename).exists() and (release_dir / filename).stat().st_size > 0 for filename in required)


def update_release_overview_tables(release_dir: Path, coverage: list[dict[str, object]]) -> None:
    all_complete = all(row["status"] == "complete" for row in coverage)
    task_count = len(TASKS)
    model_line_count = len(MODEL_LINES)
    family_labels = list(dict.fromkeys(family for _, family, _, _ in MODEL_LINES))
    total_samples = sum(int(task["expected"]) for task in TASKS.values()) * model_line_count
    per_line_unimoral_samples = sum(int(task["expected"]) for task in TASKS.values())
    added_unimoral_samples = per_line_unimoral_samples - int(TASKS["unimoral_action_prediction"]["expected"])
    task_names = list(TASKS)

    coverage_path = release_dir / "coverage-matrix.csv"
    if all_complete and coverage_path.exists():
        rows = read_csv(coverage_path)
        for row in rows:
            if row.get("benchmark") != "UniMoral" or row.get("status") == "not_run":
                continue
            row["status"] = "benchmark_faithful"
            row["completed_tasks"] = str(task_count)
            row["expected_tasks"] = str(task_count)
            row["label"] = f"{task_count}/{task_count}"
        write_csv(coverage_path, rows, list(rows[0]) if rows else [])

    summary_path = release_dir / "benchmark-summary.csv"
    if summary_path.exists():
        rows = read_csv(summary_path)
        for row in rows:
            if row.get("benchmark") != "UniMoral":
                continue
            row["task_types"] = str(task_count)
            row["evaluated_lines"] = str(task_count * model_line_count)
            row["models_covered"] = str(len(family_labels))
            row["samples"] = str(total_samples)
            row["modes"] = "benchmark_faithful" if all_complete else "benchmark_faithful; documented_incomplete"
        write_csv(summary_path, rows, list(rows[0]) if rows else [])

    catalog_path = release_dir / "benchmark-catalog.csv"
    if catalog_path.exists():
        rows = read_csv(catalog_path)
        for row in rows:
            if row.get("benchmark") != "UniMoral":
                continue
            row["models_in_release"] = "; ".join(family_labels)
            row["samples_in_release"] = str(total_samples)
            if "current_release_mode" in row:
                row["current_release_mode"] = "benchmark_faithful" if all_complete else "benchmark_faithful; documented_incomplete"
            row["repo_readout"] = "The release implements all four UniMoral task definitions: action prediction, moral typology classification, factor attribution, and consequence generation."
            if all_complete:
                row["release_interpretation"] = "Action prediction remains the original comparable UniMoral scalar and is near-saturated; RQ2/RQ3/RQ4 expose typology, attribution, and generation behavior separately across the full model-line matrix."
            else:
                row["release_interpretation"] = "Action prediction remains the original comparable UniMoral scalar and is near-saturated; RQ2/RQ3/RQ4 expose typology, attribution, and generation behavior separately, with incomplete or parse-limited model-line cells tracked in unimoral-failure-checklist.csv."
        write_csv(catalog_path, rows, list(rows[0]) if rows else [])

    roster_path = release_dir / "model-roster.csv"
    if all_complete and roster_path.exists():
        rows = read_csv(roster_path)
        for row in rows:
            benchmarks = {item.strip() for item in str(row.get("benchmarks", "")).split(";") if item.strip()}
            if "UniMoral" not in benchmarks:
                continue
            existing_tasks = [item.strip() for item in str(row.get("tasks", "")).split(";") if item.strip()]
            task_list = list(dict.fromkeys([*existing_tasks, *task_names]))
            row["tasks"] = "; ".join(task_list)
            try:
                current_samples = int(row.get("samples") or 0)
            except ValueError:
                current_samples = 0
            if added_unimoral_samples and not all(task in existing_tasks for task in task_names):
                row["samples"] = str(current_samples + added_unimoral_samples)
        write_csv(roster_path, rows, list(rows[0]) if rows else [])


def format_value(value: object) -> str:
    if value in {None, ""}:
        return ""
    return f"{float(value):.3f}"


def build_markdown_section(
    rows: list[dict[str, object]],
    coverage: list[dict[str, object]],
    spreads: list[dict[str, object]],
    rankings: list[dict[str, object]],
    *,
    figure_prefix: str,
    resume_plan_link: str,
    completion_audit_link: str,
) -> str:
    spread_by_task = {row["task_name"]: row for row in spreads}
    top_by_task = {row["task_name"]: row for row in rankings if str(row["rank"]) == "1"}
    all_complete = all(row["status"] == "complete" for row in coverage)
    if all_complete:
        summary = "The release has clean scored coverage for all four UniMoral tasks: action prediction, moral typology classification, factor attribution, and consequence generation. Action prediction remains the legacy comparable scalar and is retained as RQ1; the added RQ2/RQ3/RQ4 artifacts expose the more diagnostic typology, attribution, and generation surfaces."
    else:
        summary = "The release now implements all four UniMoral task definitions and exports scored artifacts where model runs completed, but the current model-line matrix is not yet fully complete. Incomplete or parse-limited cells are listed in `unimoral-failure-checklist.csv`; action prediction remains the legacy comparable scalar and is retained as RQ1."
    score_note = score_scale_note(rows)
    lines = [
        "## UniMoral Full Benchmark Coverage",
        "",
        summary,
        "",
        score_note,
        "",
        "| RQ | Task | Status | Strict complete | Reported cells | Primary metric | Mean | Range | Top line | Diagnostic read |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for item in coverage:
        task_name = str(item["task_name"])
        task = TASKS[task_name]
        spread = spread_by_task[task_name]
        top = top_by_task.get(task_name, {})
        top_cell = ""
        if top:
            top_cell = f"{top['line_label']} ({format_value(top['value'])})"
        lines.append(
            "| {rq} | {task_label} | {status} | {complete}/{expected} | {reported}/{expected} | {metric} | {mean} | {range_} | {top} | {diagnostic} |".format(
                rq=item["rq"],
                task_label=item["task_label"],
                status=item["status"],
                complete=item["complete_model_lines"],
                reported=item["reported_model_lines"],
                expected=item["expected_model_lines"],
                metric=task["metric"],
                mean=format_value(spread["mean"]),
                range_=format_value(spread["range"]),
                top=top_cell,
                diagnostic=spread["diagnostic_read"],
            )
        )
    lines.extend(
        [
            "",
            "Sample-level predictions for RQ2/RQ3/RQ4 are exported in `unimoral-sample-predictions.csv`; full Inspect `.eval` logs remain under the ignored `results/inspect/logs/2026-05-16-unimoral-full/` run directory.",
            f"The provider-free MiniMax handoff is tracked in [`unimoral-minimax-resume-plan.md`]({resume_plan_link}).",
            f"The prompt-to-artifact completion audit, including the verifier-checked CSV-level strict blocker inventory, is tracked in [`unimoral-completion-audit.md`]({completion_audit_link}).",
            "",
            "| Task | What it measures | Scoring note |",
            "| --- | --- | --- |",
            "| RQ1 action prediction | Selects the crowd-endorsed action from a two-action dilemma. | Main figure uses exact-match accuracy because the frozen release source exposes only aggregate action accuracy. |",
            "| RQ2 moral typology | Classifies the selected action as deontological, utilitarian, rights-based, or virtuous using `Action_criteria`. | Main figure uses exact-match accuracy for horizontal comparison with RQ1/RQ3. |",
            "| RQ3 factor attribution | Classifies the main contributor to the annotator decision using `Contributing_factors`. | Main figure uses exact-match accuracy for horizontal comparison with RQ1/RQ2. |",
            "| RQ4 consequence generation | Generates likely consequences for the selected action using `Consequence` references. | BERTScore F1 is the semantic-similarity metric; METEOR, BLEU, and ROUGE-L are lexical side metrics. RQ4 is kept separate from classification accuracy charts. |",
            "",
            f"![UniMoral classification accuracy heatmap]({figure_prefix}option1_unimoral_task_heatmap.svg)",
            "",
            f"![UniMoral RQ4 generation quality]({figure_prefix}option1_unimoral_generation_quality.svg)",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def update_markdown(path: Path, section: str) -> None:
    if not path.exists():
        return
    start = "<!-- UNIMORAL_FULL_BENCHMARK_START -->"
    end = "<!-- UNIMORAL_FULL_BENCHMARK_END -->"
    block = f"{start}\n{section}{end}\n"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = text.rstrip() + "\n\n" + block
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def update_markdown_reports(
    release_dir: Path,
    rows: list[dict[str, object]],
    coverage: list[dict[str, object]],
    spreads: list[dict[str, object]],
    rankings: list[dict[str, object]],
) -> None:
    root_section = build_markdown_section(
        rows,
        coverage,
        spreads,
        rankings,
        figure_prefix="figures/release/",
        resume_plan_link="results/release/2026-04-19-option1/unimoral-minimax-resume-plan.md",
        completion_audit_link="results/release/2026-04-19-option1/unimoral-completion-audit.md",
    )
    release_section = build_markdown_section(
        rows,
        coverage,
        spreads,
        rankings,
        figure_prefix="../../../figures/release/",
        resume_plan_link="unimoral-minimax-resume-plan.md",
        completion_audit_link="unimoral-completion-audit.md",
    )
    update_markdown(ROOT / "README.md", root_section)
    update_markdown(release_dir / "README.md", release_section)
    update_markdown(release_dir / "jenny-group-report.md", release_section)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-root", default=ROOT / "results" / "inspect" / "logs" / "2026-05-16-unimoral-full", type=Path)
    parser.add_argument("--release-dir", default=ROOT / "results" / "release" / "2026-04-19-option1", type=Path)
    parser.add_argument("--figure-dir", default=ROOT / "figures" / "release", type=Path)
    parser.add_argument(
        "--bertscore-file",
        default=None,
        type=Path,
        help="Optional per-sample RQ4 BERTScore CSV to merge into UniMoral artifacts.",
    )
    args = parser.parse_args()

    if not log_root_has_evals(args.log_root) and existing_release_tables_available(args.release_dir):
        rows = read_csv(args.release_dir / "unimoral-full-benchmark.csv")
        coverage = read_csv(args.release_dir / "unimoral-coverage.csv")
        spreads = read_csv(args.release_dir / "unimoral-task-spread.csv")
        rankings = read_csv(args.release_dir / "unimoral-model-rankings.csv")
        failures = read_csv(args.release_dir / "unimoral-failure-checklist.csv")
        args.figure_dir.mkdir(parents=True, exist_ok=True)
        svg_four_task_dashboard(rows, coverage, spreads, rankings, args.figure_dir / "option1_unimoral_four_task_dashboard.svg")
        svg_heatmap(rows, args.figure_dir / "option1_unimoral_task_heatmap.svg")
        svg_generation_quality(rows, args.figure_dir / "option1_unimoral_generation_quality.svg")
        svg_rankings(rows, args.figure_dir / "option1_unimoral_task_rankings.svg")
        svg_spread(rows, args.figure_dir / "option1_unimoral_task_spread.svg")
        write_minimax_resume_plan(args.release_dir, failures)
        write_completion_audit(args.release_dir, coverage, failures)
        update_manifest(args.release_dir)
        update_release_overview_tables(args.release_dir, coverage)
        update_markdown_reports(args.release_dir, rows, coverage, spreads, rankings)
        print(f"No Inspect .eval logs found under {args.log_root}; reused existing tracked UniMoral CSV artifacts.")
        return

    bertscore_file = args.bertscore_file or args.release_dir / "unimoral-rq4-bertscore.csv"
    bertscore_lookup = load_bertscore_lookup(bertscore_file)
    rows = build_rows(args.log_root, args.release_dir, bertscore_lookup=bertscore_lookup)
    predictions = sample_prediction_rows(args.log_root, bertscore_lookup=bertscore_lookup)
    coverage = coverage_rows(rows)
    spreads = spread_rows(rows)
    rankings = ranking_rows(rows)
    failures = failure_rows(rows)

    result_fields = [
        "line_label",
        "family",
        "size_slot",
        "task_name",
        "rq",
        "task_label",
        "primary_metric",
        "expected_samples",
        "completed_samples",
        "status",
        "accuracy",
        "official_weighted_f1",
        "bleu",
        "meteor",
        "bert_score_f1",
        "rouge_l",
        "parsed_count",
        "log_path",
    ]
    write_csv(args.release_dir / "unimoral-full-benchmark.csv", rows, result_fields)
    write_csv(args.release_dir / "unimoral-coverage.csv", coverage, list(coverage[0]))
    write_csv(args.release_dir / "unimoral-task-spread.csv", spreads, list(spreads[0]))
    write_csv(args.release_dir / "unimoral-model-rankings.csv", rankings, list(rankings[0]) if rankings else ["task_name", "task_label", "rank", "line_label", "metric", "value"])
    write_csv(
        args.release_dir / "unimoral-sample-predictions.csv",
        predictions,
        [
            "line_label",
            "family",
            "size_slot",
            "task_name",
            "rq",
            "sample_id",
            "language",
            "scenario_id",
            "target_json",
            "prediction",
            "score_value",
            "bert_score_f1",
            "answer_source",
            "source_log_dir",
            "source_log_count",
        ],
    )
    write_csv(
        args.release_dir / "unimoral-failure-checklist.csv",
        failures,
        [
            "line_label",
            "task_name",
            "status",
            "completed_samples",
            "expected_samples",
            "parsed_count",
            "category",
            "reason",
            "next_action",
            "log_path",
        ],
    )

    args.figure_dir.mkdir(parents=True, exist_ok=True)
    svg_four_task_dashboard(rows, coverage, spreads, rankings, args.figure_dir / "option1_unimoral_four_task_dashboard.svg")
    svg_heatmap(rows, args.figure_dir / "option1_unimoral_task_heatmap.svg")
    svg_generation_quality(rows, args.figure_dir / "option1_unimoral_generation_quality.svg")
    svg_rankings(rows, args.figure_dir / "option1_unimoral_task_rankings.svg")
    svg_spread(rows, args.figure_dir / "option1_unimoral_task_spread.svg")
    write_minimax_resume_plan(args.release_dir, failures)
    write_completion_audit(args.release_dir, coverage, failures)
    update_manifest(args.release_dir)
    update_release_overview_tables(args.release_dir, coverage)
    update_markdown_reports(args.release_dir, rows, coverage, spreads, rankings)


if __name__ == "__main__":
    main()
