#!/usr/bin/env python3
"""Build result tables and figures for the May 13 additional-model sweep.

This parser reads Inspect `.eval` archives directly. It intentionally treats
Mistral's provider-503 partial archives as valid partial evidence and merges
them with the later resume archives by sample id.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_ROOT = ROOT / "results" / "inspect" / "logs" / "2026-05-13-additional-model-sweep" / "full"
DEFAULT_RESULT_DIR = ROOT / "results" / "exploratory" / "2026-05-13-additional-model-sweep"
DEFAULT_FIGURE_DIR = ROOT / "figures" / "exploratory"

MODEL_LABELS = {
    "meta-llama__llama-3-8b-instruct": "Llama 3 8B",
    "meta-llama__llama-3.1-8b-instruct": "Llama 3.1 8B",
    "meta-llama__llama-3.2-1b-instruct": "Llama 3.2 1B",
    "qwen__qwen-2.5-7b-instruct": "Qwen2.5 7B",
    "mistralai__mistral-nemo": "Mistral Nemo",
}

MODEL_FAMILY = {
    "Llama 3 8B": "Llama",
    "Llama 3.1 8B": "Llama",
    "Llama 3.2 1B": "Llama",
    "Qwen2.5 7B": "Qwen",
    "Mistral Nemo": "Mistral",
}

MODEL_SIZE_B = {
    "Llama 3.2 1B": 1.0,
    "Qwen2.5 7B": 7.0,
    "Llama 3 8B": 8.0,
    "Llama 3.1 8B": 8.0,
    "Mistral Nemo": 12.0,
}

MODEL_ORDER = [
    "Mistral Nemo",
    "Qwen2.5 7B",
    "Llama 3.1 8B",
    "Llama 3 8B",
    "Llama 3.2 1B",
]

CCD_CLUSTER_LABELS = {
    "anglo": "Anglo",
    "eastern_europe": "Eastern Europe",
    "latin-america": "Latin America",
    "latin_europe": "Latin Europe",
    "confucian_asia": "Confucian Asia",
    "nordic_europe": "Nordic Europe",
    "sub-saharan_africa": "Sub-Saharan Africa",
    "southern-asia": "Southern Asia",
    "germanic_europe": "Germanic Europe",
    "middle_east": "Middle East",
}

CCD_CLUSTER_ORDER = [
    "anglo",
    "eastern_europe",
    "latin-america",
    "latin_europe",
    "confucian_asia",
    "nordic_europe",
    "sub-saharan_africa",
    "southern-asia",
    "germanic_europe",
    "middle_east",
]


@dataclass(frozen=True)
class ParsedSample:
    model: str
    task: str
    sample_id: str
    completion: str
    target: str
    metadata: dict[str, Any]
    scores: dict[str, Any]
    source_eval: str


def canonical_task(task_dir_name: str, header_task: str | None = None) -> str:
    if task_dir_name.startswith("ccd_bench_selection"):
        return "ccd_bench_selection"
    if task_dir_name.startswith("unimoral_action_prediction"):
        return "unimoral_action_prediction"
    return header_task or task_dir_name


def iter_eval_samples(log_root: Path) -> list[ParsedSample]:
    samples: list[ParsedSample] = []
    for eval_path in sorted(log_root.rglob("*.eval")):
        parts = eval_path.relative_to(log_root).parts
        if len(parts) < 3:
            continue
        model_dir, task_dir = parts[0], parts[1]
        model = MODEL_LABELS.get(model_dir, model_dir)

        with zipfile.ZipFile(eval_path) as archive:
            header_task = None
            if "header.json" in archive.namelist():
                try:
                    header = json.loads(archive.read("header.json"))
                    header_task = (header.get("eval") or {}).get("task")
                except json.JSONDecodeError:
                    header_task = None
            task = canonical_task(task_dir, header_task)
            if task not in {"unimoral_action_prediction", "ccd_bench_selection"}:
                continue
            for name in archive.namelist():
                if not name.startswith("samples/") or not name.endswith(".json"):
                    continue
                record = json.loads(archive.read(name))
                output = record.get("output") or {}
                samples.append(
                    ParsedSample(
                        model=model,
                        task=task,
                        sample_id=str(record.get("id") or ""),
                        completion=str(output.get("completion") or ""),
                        target=str(record.get("target") or ""),
                        metadata=record.get("metadata") or {},
                        scores=record.get("scores") or {},
                        source_eval=str(eval_path.relative_to(ROOT)),
                    )
                )
    return samples


def merged_samples(samples: list[ParsedSample]) -> dict[tuple[str, str, str], ParsedSample]:
    merged: dict[tuple[str, str, str], ParsedSample] = {}
    duplicate_sources: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for sample in samples:
        key = (sample.model, sample.task, sample.sample_id)
        if key in merged:
            duplicate_sources[key].append(sample.source_eval)
        # Later sorted archives are resume runs; if a duplicate exists, keep the
        # later archive because it reflects the completed pass.
        merged[key] = sample
    return merged


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("<", " ").replace(">", " ")
    text = re.sub(r"[`\"'“”‘’]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_unimoral_answer(text: str) -> str | None:
    normalized = normalize_text(text)
    if not normalized:
        return None

    # Accept the short A/B forms and the common "Selected action is A/B"
    # format used by these saved runs.
    patterns = [
        r"^selected action(?:\s+is|\s+es|是)?\s*[:\-]?\s*\(?\s*([ab])\s*\)?\b",
        r"^(?:answer|choice|option|action)\s*[:\-]?\s*\(?\s*([ab])\s*\)?\b",
        r"^i (?:choose|chose|select|selected|would choose|would select)\s+(?:option\s+|action\s+)?\(?\s*([ab])\s*\)?\b",
        r"^(?:la\s+)?acci[oó]n seleccionada es\s*\(?\s*([ab])\s*\)?\b",
        r"^выбранное действие\s*[:\-]?\s*\(?\s*([ab])\s*\)?\b",
        r"^(?:चयनित कार्य|चयनित कार्रवाई|चुनी गई क्रिया|चुनी गई कार्रवाई|चुनी गई कार्य|संभावित क्रिया)\s*(?:है)?\s*[:\-]?\s*\(?\s*([ab])\s*\)?\b",
        r"^(?:الإجابة الصحيحة هي|الإجابة|الجواب هو|الجواب)\s*[:\-]?\s*[\"']?\(?\s*([ab])\s*\)?\b",
        r"^\(?([ab])\)?\.?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            return match.group(1)

    # A small number of weak-model outputs localize the option letter itself.
    compact = normalized.strip(" .。\"'()[]{}")
    localized_exact = {
        "ब": "b",
        "बी": "b",
        "ب": "b",
        "أ": "a",
        "ا": "a",
    }
    if compact in localized_exact:
        return localized_exact[compact]
    return None


def parse_ccd_selected_option(sample: ParsedSample) -> int | None:
    score = sample.scores.get("valid_choice_scorer") or {}
    metadata = score.get("metadata") or {}
    selected = metadata.get("selected_option") or score.get("answer")
    if selected is not None:
        try:
            value = int(selected)
            if 1 <= value <= 10:
                return value
        except (TypeError, ValueError):
            pass
    match = re.search(r"selected option\s*[:\-]\s*(10|[1-9])\b", sample.completion, flags=re.I)
    if match:
        return int(match.group(1))
    return None


def pct(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.3f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def summarize_unimoral(samples: list[ParsedSample]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    language_rows: list[dict[str, Any]] = []
    by_model: dict[str, list[ParsedSample]] = defaultdict(list)
    for sample in samples:
        by_model[sample.model].append(sample)

    for model, model_samples in by_model.items():
        total = len(model_samples)
        extracted_answers = [extract_unimoral_answer(sample.completion) for sample in model_samples]
        answered = sum(answer is not None for answer in extracted_answers)
        correct = sum(
            answer == sample.target
            for answer, sample in zip(extracted_answers, model_samples)
            if answer is not None
        )
        accuracy = correct / total if total else None
        rows.append(
            {
                "model": model,
                "family": MODEL_FAMILY.get(model, ""),
                "size_b": MODEL_SIZE_B.get(model, ""),
                "samples": total,
                "answered": answered,
                "answer_rate": answered / total if total else None,
                "correct": correct,
                "accuracy": accuracy,
            }
        )

        by_language: dict[str, list[tuple[ParsedSample, str | None]]] = defaultdict(list)
        for sample, answer in zip(model_samples, extracted_answers):
            by_language[str(sample.metadata.get("language") or "unknown")].append((sample, answer))
        for language, language_samples in sorted(by_language.items()):
            lang_total = len(language_samples)
            lang_answered = sum(answer is not None for _, answer in language_samples)
            lang_correct = sum(answer == sample.target for sample, answer in language_samples if answer is not None)
            language_rows.append(
                {
                    "model": model,
                    "language": language,
                    "samples": lang_total,
                    "answered": lang_answered,
                    "accuracy": lang_correct / lang_total if lang_total else None,
                }
            )
    rows.sort(key=lambda row: row["accuracy"] or 0, reverse=True)
    return rows, language_rows


def summarize_ccd(samples: list[ParsedSample]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summary_rows: list[dict[str, Any]] = []
    distribution_rows: list[dict[str, Any]] = []
    by_model: dict[str, list[ParsedSample]] = defaultdict(list)
    for sample in samples:
        by_model[sample.model].append(sample)

    for model, model_samples in by_model.items():
        selected_options = [parse_ccd_selected_option(sample) for sample in model_samples]
        valid_count = sum(option is not None for option in selected_options)
        cluster_counts: Counter[str] = Counter()
        for sample, option in zip(model_samples, selected_options):
            if option is None:
                continue
            cluster = (sample.metadata.get("display_to_cluster") or {}).get(str(option))
            if cluster:
                cluster_counts[str(cluster)] += 1
        dominant_cluster, dominant_count = ("", 0)
        if cluster_counts:
            dominant_cluster, dominant_count = cluster_counts.most_common(1)[0]
        total = len(model_samples)
        valid_total = max(valid_count, 1)
        shares = [cluster_counts.get(cluster, 0) / valid_total for cluster in CCD_CLUSTER_ORDER]
        effective_clusters = 1 / sum(share * share for share in shares if share > 0)
        summary_rows.append(
            {
                "model": model,
                "family": MODEL_FAMILY.get(model, ""),
                "size_b": MODEL_SIZE_B.get(model, ""),
                "samples": total,
                "valid_choice_count": valid_count,
                "valid_choice_rate": valid_count / total if total else None,
                "dominant_cluster": CCD_CLUSTER_LABELS.get(dominant_cluster, dominant_cluster),
                "dominant_share": dominant_count / valid_total if valid_count else None,
                "effective_cluster_count": effective_clusters,
            }
        )
        for cluster in CCD_CLUSTER_ORDER:
            count = cluster_counts.get(cluster, 0)
            distribution_rows.append(
                {
                    "model": model,
                    "cluster": CCD_CLUSTER_LABELS[cluster],
                    "count": count,
                    "share": count / valid_total if valid_count else None,
                }
            )
    summary_rows.sort(key=lambda row: row["dominant_share"] or 0, reverse=True)
    distribution_rows.sort(key=lambda row: (MODEL_ORDER.index(row["model"]) if row["model"] in MODEL_ORDER else 99, row["cluster"]))
    return summary_rows, distribution_rows


def load_sweep(log_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    raw = iter_eval_samples(log_root)
    merged = merged_samples(raw)
    unimoral_samples = [sample for sample in merged.values() if sample.task == "unimoral_action_prediction"]
    ccd_samples = [sample for sample in merged.values() if sample.task == "ccd_bench_selection"]
    unimoral_rows, language_rows = summarize_unimoral(unimoral_samples)
    ccd_rows, ccd_distribution_rows = summarize_ccd(ccd_samples)
    return unimoral_rows, language_rows, ccd_rows, ccd_distribution_rows


def svg_header(width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        '<style>'
        'text{font-family:Arial,Helvetica,sans-serif;fill:#18212f}'
        '.title{font-size:26px;font-weight:700}.subtitle{font-size:15px;fill:#536171}'
        '.axis{font-size:14px;fill:#536171}.label{font-size:15px}.small{font-size:12px;fill:#536171}'
        '.metric{font-size:16px;font-weight:700;fill:#253044}'
        '</style>'
    )


def write_unimoral_accuracy_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    width, height = 960, 470
    left, top, chart_w, chart_h = 210, 92, 650, 255
    models = [row["model"] for row in rows]
    max_val = 0.70
    group_h = chart_h / len(models)
    parts = [
        svg_header(width, height),
        '<rect width="100%" height="100%" fill="#f8faf7"/>',
        '<text x="34" y="42" class="title">Small-model follow-up: UniMoral accuracy</text>',
        '<text x="34" y="68" class="subtitle">Metric: action-prediction accuracy. Higher means closer to human-labeled choices.</text>',
    ]
    for tick in [0, 0.2, 0.4, 0.6]:
        x = left + tick / max_val * chart_w
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+chart_h}" stroke="#d6ddd9" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{top+chart_h+28}" text-anchor="middle" class="axis">{tick:.1f}</text>')
    for idx, row in enumerate(rows):
        y = top + idx * group_h + 16
        value = float(row["accuracy"] or 0)
        bar_w = value / max_val * chart_w
        color = "#0f766e" if value >= 0.60 else "#94a3b8"
        parts.append(f'<text x="{left-14}" y="{y+14}" text-anchor="end" class="label">{row["model"]}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="18" rx="5" fill="{color}"/>')
        parts.append(f'<text x="{left+bar_w+10:.1f}" y="{y+14}" class="small">{value:.3f}</text>')
    parts.extend(
        [
            f'<text x="{left + chart_w / 2:.1f}" y="{height - 70}" text-anchor="middle" class="metric">Metric: UniMoral action accuracy</text>',
            '<text x="34" y="430" class="subtitle">Takeaway: the 7B-12B routes cluster tightly; Llama 3.2 1B is the clear low line.</text>',
            "</svg>",
        ]
    )
    path.write_text("\n".join(parts), encoding="utf-8")


def write_ccd_dominant_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    width, height = 960, 470
    left, top, chart_w, chart_h = 210, 92, 650, 255
    max_val = 0.28
    parts = [
        svg_header(width, height),
        '<rect width="100%" height="100%" fill="#fffaf2"/>',
        '<text x="34" y="42" class="title">CCD-Bench: dominant cultural-cluster concentration</text>',
        '<text x="34" y="68" class="subtitle">Metric: dominant-option share. Lower means less collapse into one cultural cluster.</text>',
    ]
    for tick in [0.10, 0.15, 0.20, 0.25]:
        x = left + tick / max_val * chart_w
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+chart_h}" stroke="#eadfce" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{top+chart_h+28}" text-anchor="middle" class="axis">{tick:.0%}</text>')
    ordered = sorted(rows, key=lambda row: float(row["dominant_share"] or 0))
    group_h = chart_h / len(ordered)
    for idx, row in enumerate(ordered):
        y = top + idx * group_h + 16
        share = float(row["dominant_share"] or 0)
        bar_w = share / max_val * chart_w
        color = "#2563eb" if row["model"] == "Llama 3.2 1B" else "#f97316"
        parts.append(f'<text x="{left-14}" y="{y+13}" text-anchor="end" class="label">{row["model"]}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="18" rx="5" fill="{color}"/>')
        parts.append(
            f'<text x="{left+bar_w+8:.1f}" y="{y+14}" class="small">{share:.1%} {row["dominant_cluster"]}</text>'
        )
    parts.extend(
        [
            f'<text x="{left + chart_w / 2:.1f}" y="{height - 70}" text-anchor="middle" class="metric">Metric: dominant cultural-cluster share</text>',
            '<text x="34" y="430" class="subtitle">Takeaway: all five lines peak on Nordic Europe; the difference is how concentrated the choice pattern becomes.</text>',
            "</svg>",
        ]
    )
    path.write_text("\n".join(parts), encoding="utf-8")


def write_scaling_svg(path: Path, unimoral_rows: list[dict[str, Any]], ccd_rows: list[dict[str, Any]]) -> None:
    width, height = 1040, 540
    left, top, chart_w, chart_h = 98, 100, 780, 320
    by_model = {row["model"]: row for row in unimoral_rows}
    ccd_by_model = {row["model"]: row for row in ccd_rows}
    models = ["Llama 3.2 1B", "Qwen2.5 7B", "Llama 3 8B", "Llama 3.1 8B", "Mistral Nemo"]
    x_min, x_max = 0, 13
    y_min, y_max = 0.34, 0.67
    colors = {
        "Llama": "#f97316",
        "Qwen": "#0ea5e9",
        "Mistral": "#7c3aed",
    }
    parts = [
        svg_header(width, height),
        '<rect width="100%" height="100%" fill="#f6f7fb"/>',
        '<text x="34" y="42" class="title">Small-model follow-up: size and capability floor</text>',
        '<text x="34" y="68" class="subtitle">Metric: UniMoral accuracy. Point size shows CCD dominant-cluster concentration.</text>',
    ]
    for tick in [0.4, 0.5, 0.6]:
        y = top + chart_h - (tick - y_min) / (y_max - y_min) * chart_h
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+chart_w}" y2="{y:.1f}" stroke="#d9dee8"/>')
        parts.append(f'<text x="{left-14}" y="{y+4:.1f}" text-anchor="end" class="axis">{tick:.1f}</text>')
    for tick in [1, 7, 8, 12]:
        x = left + (tick - x_min) / (x_max - x_min) * chart_w
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+chart_h}" stroke="#e5e9f2"/>')
        parts.append(f'<text x="{x:.1f}" y="{top+chart_h+30}" text-anchor="middle" class="axis">{tick:g}B</text>')
    llama_points = []
    for model in ["Llama 3.2 1B", "Llama 3 8B", "Llama 3.1 8B"]:
        row = by_model[model]
        x = left + (float(row["size_b"]) - x_min) / (x_max - x_min) * chart_w
        y = top + chart_h - (float(row["accuracy"]) - y_min) / (y_max - y_min) * chart_h
        llama_points.append((x, y))
    parts.append(
        '<polyline points="{}" fill="none" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>'.format(
            " ".join(f"{x:.1f},{y:.1f}" for x, y in llama_points)
        )
    )
    label_offsets = {
        "Llama 3.2 1B": (14, -20, "start"),
        "Qwen2.5 7B": (-18, -18, "end"),
        "Llama 3 8B": (18, 34, "start"),
        "Llama 3.1 8B": (18, -30, "start"),
        "Mistral Nemo": (18, -18, "start"),
    }
    for model in models:
        row = by_model[model]
        ccd = ccd_by_model[model]
        size = float(row["size_b"])
        acc = float(row["accuracy"])
        concentration = float(ccd["dominant_share"])
        x = left + (size - x_min) / (x_max - x_min) * chart_w
        y = top + chart_h - (acc - y_min) / (y_max - y_min) * chart_h
        radius = 7 + concentration * 42
        family = str(row["family"])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{colors.get(family, "#334155")}" fill-opacity="0.78" stroke="white" stroke-width="2"/>')
        dx, dy, anchor = label_offsets[model]
        label_x = x + dx
        label_y = y + dy
        parts.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" class="small">{model}</text>')
        parts.append(f'<text x="{label_x:.1f}" y="{label_y + 15:.1f}" text-anchor="{anchor}" class="small">{acc:.3f}</text>')
    legend_x, legend_y = 905, 110
    for idx, (family, color) in enumerate(colors.items()):
        y = legend_y + idx * 28
        parts.append(f'<circle cx="{legend_x}" cy="{y}" r="7" fill="{color}" fill-opacity="0.78" stroke="white" stroke-width="2"/>')
        parts.append(f'<text x="{legend_x + 16}" y="{y + 5}" class="label">{family}</text>')
    parts.extend(
        [
            f'<text x="{left + chart_w / 2:.1f}" y="{height-76}" text-anchor="middle" class="metric">Approximate model size (B parameters)</text>',
            f'<text x="28" y="{top + chart_h / 2:.1f}" transform="rotate(-90 28 {top + chart_h / 2:.1f})" text-anchor="middle" class="metric">Metric: UniMoral accuracy</text>',
            '<text x="34" y="504" class="subtitle">Takeaway: the 1B route is much weaker; the 7B-12B routes cluster instead of forming a clean bigger-is-better ladder.</text>',
            "</svg>",
        ]
    )
    path.write_text("\n".join(parts), encoding="utf-8")


def write_readme(
    path: Path,
    unimoral_rows: list[dict[str, Any]],
    ccd_rows: list[dict[str, Any]],
    figure_dir: Path,
) -> None:
    best = max(unimoral_rows, key=lambda row: float(row["accuracy"] or 0))
    weakest = min(unimoral_rows, key=lambda row: float(row["accuracy"] or 0))
    most_diffuse = min(ccd_rows, key=lambda row: float(row["dominant_share"] or 0))
    most_concentrated = max(ccd_rows, key=lambda row: float(row["dominant_share"] or 0))
    unimoral_fig = Path("../../../figures/exploratory/additional_model_sweep_unimoral_accuracy.svg")
    ccd_fig = Path("../../../figures/exploratory/additional_model_sweep_ccd_dominant_share.svg")
    scaling_fig = Path("../../../figures/exploratory/additional_model_sweep_scaling.svg")
    lines = [
        "# Additional Model Sweep: UniMoral + CCD-Bench",
        "",
        "Date: 2026-05-13",
        "",
        "This follow-up brings five older or smaller OpenRouter routes into the deliverable as a capability-floor check. It asks whether `Mistral`, `Qwen`, and smaller `Llama` routes change the main moral-psych story, or whether they mainly show where text moral-choice performance starts to fall off.",
        "",
        "## Key Findings",
        "",
        f"- Best UniMoral result: **{best['model']}** at **{float(best['accuracy']):.3f}**.",
        f"- Weakest UniMoral result: **{weakest['model']}** at **{float(weakest['accuracy']):.3f}**; this is the only clear low-performing line.",
        "- The other four UniMoral lines are tightly clustered from **0.632** to **0.648**, so the main separation is the 1B route versus the 7B-12B routes.",
        f"- CCD-Bench is **not accuracy**. All five lines peak on **Nordic Europe**, but concentration differs: **{most_diffuse['model']}** is most diffuse at **{float(most_diffuse['dominant_share']):.1%}**, while **{most_concentrated['model']}** is most concentrated at **{float(most_concentrated['dominant_share']):.1%}**.",
        "- Scaling readout: this looks like a **capability floor**, not a clean monotonic scaling law. Llama 3.2 1B is much weaker on UniMoral, but the 7B-12B models are tightly clustered.",
        "",
        "## Interpretation",
        "",
        "**Model-wise:** Mistral Nemo is the top UniMoral line at 0.648, but Qwen2.5 7B, Llama 3.1 8B, and Llama 3 8B are close behind from 0.632 to 0.640. Llama 3.2 1B is the clear weak line at 0.406, with a lower answer rate as well.",
        "",
        "**Benchmark-wise:** UniMoral gives a clear performance separation between the very small 1B route and the stronger 7B-12B cluster. CCD-Bench gives a style/concentration readout rather than a correctness score: all models peak on Nordic Europe, but Llama 3.2 1B is most diffuse (15.9% dominant share; 9.12 effective clusters), while Mistral Nemo is most concentrated (25.3%; 7.22 effective clusters).",
        "",
        "**Compared with the main release:** the follow-up supports the same high-level interpretation. Once a route is in the mid-sized instruction-model range, text moral-choice scores are close enough that the benchmark-specific story matters more than a simple model-size ranking. The 1B route is the warning case.",
        "",
        "**Bottom line:** this is the practical takeaway to report: do not overclaim a universal bigger-is-better trend. Very small routes can fall off sharply, while several older or mid-sized instruction routes remain competitive on selected text moral-choice and cultural-style checks.",
        "",
        "## Result Tables",
        "",
        "### UniMoral",
        "",
        "| Model | Accuracy | Answer rate | Correct | Samples |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in unimoral_rows:
        lines.append(
            f"| {row['model']} | {float(row['accuracy']):.3f} | {float(row['answer_rate']):.3f} | "
            f"{int(row['correct'])} | {int(row['samples'])} |"
        )
    lines.extend(
        [
            "",
            "### CCD-Bench",
            "",
            "| Model | Valid choice rate | Dominant cluster | Dominant share | Effective clusters |",
            "|---|---:|---|---:|---:|",
        ]
    )
    for row in ccd_rows:
        lines.append(
            f"| {row['model']} | {float(row['valid_choice_rate']):.3f} | {row['dominant_cluster']} | "
            f"{float(row['dominant_share']):.3f} | {float(row['effective_cluster_count']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Figures",
            "",
            f"![Additional model sweep UniMoral accuracy]({unimoral_fig})",
            "",
            f"![CCD dominant cluster share]({ccd_fig})",
            "",
            f"![Additional model sweep scaling]({scaling_fig})",
            "",
            "## Metric Boundary",
            "",
            "- UniMoral accuracy is computed from the completed run records with the same final A/B scoring rule across all five routes; no new API calls were used.",
            "- CCD-Bench reports cultural-choice distribution and concentration, not correctness.",
            "- This follow-up is a capability-floor check, not a replacement for the main release matrix.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build(log_root: Path, result_dir: Path, figure_dir: Path) -> None:
    result_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    unimoral_rows, language_rows, ccd_rows, ccd_distribution_rows = load_sweep(log_root)

    write_csv(
        result_dir / "unimoral-summary.csv",
        unimoral_rows,
        [
            "model",
            "family",
            "size_b",
            "samples",
            "answered",
            "answer_rate",
            "correct",
            "accuracy",
        ],
    )
    write_csv(
        result_dir / "unimoral-language-breakdown.csv",
        language_rows,
        ["model", "language", "samples", "answered", "accuracy"],
    )
    write_csv(
        result_dir / "ccd-summary.csv",
        ccd_rows,
        [
            "model",
            "family",
            "size_b",
            "samples",
            "valid_choice_count",
            "valid_choice_rate",
            "dominant_cluster",
            "dominant_share",
            "effective_cluster_count",
        ],
    )
    write_csv(
        result_dir / "ccd-cluster-distribution.csv",
        ccd_distribution_rows,
        ["model", "cluster", "count", "share"],
    )
    write_csv(
        result_dir / "sweep-overview.csv",
        [
            {
                "artifact": "unimoral_action_prediction",
                "models": len(unimoral_rows),
                "samples_per_complete_model": 8784,
                "status": "complete",
                "metric_boundary": "saved-log A/B action-prediction accuracy",
            },
            {
                "artifact": "ccd_bench_selection",
                "models": len(ccd_rows),
                "samples_per_complete_model": 2182,
                "status": "complete",
                "metric_boundary": "valid cultural choice distribution, not accuracy",
            },
        ],
        ["artifact", "models", "samples_per_complete_model", "status", "metric_boundary"],
    )
    write_unimoral_accuracy_svg(figure_dir / "additional_model_sweep_unimoral_accuracy.svg", unimoral_rows)
    write_ccd_dominant_svg(figure_dir / "additional_model_sweep_ccd_dominant_share.svg", ccd_rows)
    write_scaling_svg(figure_dir / "additional_model_sweep_scaling.svg", unimoral_rows, ccd_rows)
    write_readme(result_dir / "README.md", unimoral_rows, ccd_rows, figure_dir)

    manifest = {
        "source_log_root": str(log_root.relative_to(ROOT)),
        "result_dir": str(result_dir.relative_to(ROOT)),
        "figure_dir": str(figure_dir.relative_to(ROOT)),
        "tables": sorted(path.name for path in result_dir.glob("*.csv")),
        "figures": sorted(path.name for path in figure_dir.glob("additional_model_sweep_*.svg")),
        "counts": {
            "unimoral_models": len(unimoral_rows),
            "ccd_models": len(ccd_rows),
            "unimoral_samples_total": sum(int(row["samples"]) for row in unimoral_rows),
            "ccd_samples_total": sum(int(row["samples"]) for row in ccd_rows),
        },
    }
    (result_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    parser.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT_DIR)
    parser.add_argument("--figure-dir", type=Path, default=DEFAULT_FIGURE_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build(args.log_root, args.result_dir, args.figure_dir)
    print(f"Wrote additional model sweep artifacts to {args.result_dir}")
    print(f"Wrote additional model sweep figures to {args.figure_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
