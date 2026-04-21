#!/usr/bin/env python3
"""Build curated release tables and SVG figures from the authoritative Option 1 summary."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "results" / "release" / "2026-04-19-option1"
DEFAULT_INPUT = DEFAULT_RELEASE_DIR / "source" / "authoritative-summary.csv"
DEFAULT_FIGURE_DIR = ROOT / "figures" / "release"
RELEASE_ID = "2026-04-19-option1"
RELEASE_TITLE = "CEI Moral-Psych Benchmark Suite: Jenny Zhu Option 1 Report"
REPORT_OWNER = "Jenny Zhu"
REPORT_DATE_LONG = "April 21, 2026"
REPORT_DATE_ISO = "2026-04-21"
SNAPSHOT_DATE_LONG = "April 19, 2026"
SNAPSHOT_DATE_ISO = "2026-04-19"
REPORT_PURPOSE = "Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan."
REPORT_PROVIDER = "OpenRouter"
REPORT_TEMPERATURE = "0"
REPORT_CURRENT_COST = "$35"
REPORT_STATUS_NOTE = (
    "Updated April 21, 2026. "
    "The frozen public snapshot remains Option 1 from April 19. "
    "Gemma-M and Gemma-L text are now complete locally, Qwen-M and Qwen-L text both have partial progress on disk, "
    "and no active local Inspect process was detected at this snapshot."
)
CI_WORKFLOW_URL = "https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml"
CI_RUN_URL = "https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927"
TEXT_EXPANSION_RUN_PATH = "results/inspect/full-runs/2026-04-19-family-size-text-expansion"
IMAGE_EXPANSION_RUN_PATH = "results/inspect/full-runs/2026-04-19-family-size-image-expansion"

MODEL_ORDER = ["Qwen", "DeepSeek", "Gemma"]
FULL_MODEL_FAMILY_ORDER = ["Qwen", "MiniMax", "DeepSeek", "Llama", "Gemma"]
BENCHMARK_ORDER = ["UniMoral", "SMID", "Value Kaleidoscope", "CCD-Bench", "Denevil"]
BENCHMARK_TASK_COUNTS = {
    "UniMoral": 1,
    "SMID": 2,
    "Value Kaleidoscope": 2,
    "CCD-Bench": 1,
    "Denevil": 1,
}
ACCURACY_SCOPE_ORDER = [
    ("UniMoral", "Option 1 action prediction", "UniMoral\naction"),
    ("SMID", "Moral rating", "SMID\nrating"),
    ("SMID", "Foundation classification", "SMID\nfoundation"),
    ("Value Kaleidoscope", "Relevance", "Value Kaleidoscope\nrelevance"),
    ("Value Kaleidoscope", "Valence", "Value Kaleidoscope\nvalence"),
]
SAMPLE_BAR_ORDER = ["Value Kaleidoscope", "Denevil", "UniMoral", "SMID", "CCD-Bench"]
COMPARABLE_RESULT_ORDER = ["Qwen-S", "DeepSeek-L", "Llama-S", "Gemma-S"]

BENCHMARK_METADATA = {
    "UniMoral": {
        "paper_title": "Are Rules Meant to be Broken? Understanding Multilingual Moral Reasoning as a Computational Pipeline with UniMoral",
        "citation": "Kumar et al. (ACL 2025 Findings)",
        "paper_url": "https://aclanthology.org/2025.acl-long.294/",
        "dataset_label": "Hugging Face dataset card",
        "dataset_url": "https://huggingface.co/datasets/shivaniku/UniMoral",
        "modality": "Text, multilingual moral reasoning",
        "repo_tasks": [
            "unimoral_action_prediction",
            "unimoral_moral_typology",
            "unimoral_factor_attribution",
            "unimoral_consequence_generation",
        ],
        "current_release_scope": "Action prediction only",
        "dataset_note": "This repo still expects a local export path via UNIMORAL_DATA_DIR.",
    },
    "SMID": {
        "paper_title": "The Socio-Moral Image Database (SMID): A Novel Stimulus Set for the Study of Social, Moral, and Affective Processes",
        "citation": "Crone et al. (PLOS ONE 2018)",
        "paper_url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190954",
        "dataset_label": "OSF project page",
        "dataset_url": "https://osf.io/ngzwx/",
        "modality": "Vision",
        "repo_tasks": [
            "smid_moral_rating",
            "smid_foundation_classification",
        ],
        "current_release_scope": "Moral rating + foundation classification",
        "dataset_note": "This repo expects local image assets plus the norms CSV under SMID_DATA_DIR.",
    },
    "Value Kaleidoscope": {
        "paper_title": "Value Kaleidoscope: Engaging AI with Pluralistic Human Values, Rights, and Duties",
        "citation": "Sorensen et al. (AAAI 2024 / arXiv 2023)",
        "paper_url": "https://arxiv.org/abs/2310.17681",
        "dataset_label": "Hugging Face dataset card",
        "dataset_url": "https://huggingface.co/datasets/allenai/ValuePrism",
        "modality": "Text value reasoning",
        "repo_tasks": [
            "value_prism_relevance",
            "value_prism_valence",
        ],
        "current_release_scope": "Relevance + valence",
        "dataset_note": "The harness can read local exports or gated Hugging Face access via allenai/ValuePrism.",
    },
    "CCD-Bench": {
        "paper_title": "CCD-Bench: Benchmarking Large Language Models for Cross-Cultural Response Generation",
        "citation": "Rahman et al. (arXiv 2025)",
        "paper_url": "https://arxiv.org/abs/2510.03553",
        "dataset_label": "GitHub repo",
        "dataset_url": "https://github.com/smartlab-nyu/CCD-Bench",
        "dataset_alt_url": "https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json",
        "modality": "Text response selection",
        "repo_tasks": [
            "ccd_bench_selection",
        ],
        "current_release_scope": "Selection",
        "dataset_note": "This repo can default to the official public JSON URL or a local cached copy.",
    },
    "Denevil": {
        "paper_title": "DeNEVIL: Navigating the Ethical Landscape of LLMs as Evaluators through Debate",
        "citation": "Duan et al. (ICLR 2024 submission / arXiv 2023)",
        "paper_url": "https://arxiv.org/abs/2310.11905",
        "dataset_label": "No public MoralPrompt export confirmed",
        "dataset_url": "",
        "modality": "Text generation",
        "repo_tasks": [
            "denevil_generation",
            "denevil_fulcra_proxy_generation",
        ],
        "current_release_scope": "Proxy generation only",
        "dataset_note": "A paper-faithful MoralPrompt export is still required for denevil_generation. The closed release uses a clearly labeled local proxy dataset instead.",
    },
}

MODEL_ROUTE_METADATA = {
    "openrouter/qwen/qwen3-8b": {
        "size_hint": "8B",
        "modality": "Text",
        "note": "Closed-slice text route for UniMoral, Value Kaleidoscope, CCD-Bench, and Denevil proxy.",
    },
    "openrouter/qwen/qwen3-vl-8b-instruct": {
        "size_hint": "8B VL",
        "modality": "Vision",
        "note": "Closed-slice vision route for SMID.",
    },
    "openrouter/deepseek/deepseek-chat-v3.1": {
        "size_hint": "Provider route",
        "modality": "Text",
        "note": "Closed-slice DeepSeek route. No separate SMID vision route is present in the release.",
    },
    "openrouter/google/gemma-3-4b-it": {
        "size_hint": "4B",
        "modality": "Text + Vision",
        "note": "Recovery route that superseded the earlier stalled Gemma namespace.",
    },
}

FUTURE_MODEL_PLAN = [
    {
        "family": "Qwen",
        "closed_release_status": "Included in Option 1",
        "current_route": "qwen3-8b + qwen3-vl-8b-instruct",
        "small_candidate": "Current 8B text + 8B vision routes complete in the release",
        "medium_candidate": "openrouter/qwen/qwen3-14b scheduled in the active non-image expansion run",
        "large_candidate": "text: openrouter/qwen/qwen3-32b; vision: openrouter/qwen/qwen2.5-vl-72b-instruct (SMID recovery complete)",
        "next_step": "Keep the completed Qwen-L SMID recovery as the large vision route, then run the queued qwen3-32b text line for UniMoral, Value Kaleidoscope, CCD-Bench, and Denevil proxy.",
    },
    {
        "family": "MiniMax",
        "closed_release_status": "Prepared only, not in Option 1",
        "current_route": "minimax-m2.1 + minimax-01 launcher present",
        "small_candidate": "Current small hybrid launcher exists, but the formal small line is still not closed",
        "medium_candidate": "openrouter/minimax/minimax-m2.5 scheduled in the non-image expansion run",
        "large_candidate": "openrouter/minimax/minimax-m2.7 scheduled last among the current text-only jobs",
        "next_step": "After the medium / large text jobs finish, decide whether to formalize the small hybrid line too.",
    },
    {
        "family": "DeepSeek",
        "closed_release_status": "Included in Option 1",
        "current_route": "deepseek-chat-v3.1",
        "small_candidate": "Closed release already uses a large-class DeepSeek route; a smaller baseline is still not frozen",
        "medium_candidate": "openrouter/deepseek/deepseek-r1-distill-qwen-32b scheduled for the non-image expansion run",
        "large_candidate": "openrouter/deepseek/deepseek-chat-v3.1 already complete in the closed release",
        "next_step": "If the group wants a stricter S/M/L ladder, add a smaller DeepSeek distill route after the current medium run.",
    },
    {
        "family": "Llama",
        "closed_release_status": "Completed locally, not promoted into Option 1",
        "current_route": "llama-3.2-11b-vision-instruct completed locally",
        "small_candidate": "Current 11B route complete across 5 papers / 7 tasks",
        "medium_candidate": "openrouter/meta-llama/llama-3.3-70b-instruct scheduled in the non-image expansion run",
        "large_candidate": "openrouter/meta-llama/llama-4-maverick scheduled after the 70B line in the same text-only queue",
        "next_step": "Let the 70B and Maverick text-only lines finish, then decide whether to promote Llama into the next authoritative snapshot.",
    },
    {
        "family": "Gemma",
        "closed_release_status": "Included in Option 1",
        "current_route": "gemma-3-4b-it",
        "small_candidate": "Current 4B route",
        "medium_candidate": "openrouter/google/gemma-3-12b-it scheduled in the active non-image expansion run",
        "large_candidate": "openrouter/google/gemma-3-27b-it scheduled first in the same text-only queue",
        "next_step": "Use the 12B and 27B text-only results to decide whether larger Gemma vision follow-up is needed.",
    },
]

IMAGE_EXPANSION_PLAN = [
    {
        "family": "Gemma",
        "size_slot": "Large",
        "model": "openrouter/google/gemma-3-27b-it",
        "benchmark": "SMID",
        "status": "Completed",
        "note": "Completed successfully in the family-size image queue.",
    },
    {
        "family": "Gemma",
        "size_slot": "Medium",
        "model": "openrouter/google/gemma-3-12b-it",
        "benchmark": "SMID",
        "status": "Completed",
        "note": "Completed successfully in the family-size image queue.",
    },
    {
        "family": "Qwen",
        "size_slot": "Large",
        "model": "openrouter/qwen/qwen2.5-vl-72b-instruct",
        "benchmark": "SMID",
        "status": "Completed",
        "note": "The original qwen3-vl-32b-instruct route hit provider-side image moderation after 59 / 2,941 samples on both SMID tasks, but the large Qwen line was recovered and completed via openrouter/qwen/qwen2.5-vl-72b-instruct with a non-Alibaba provider allowlist.",
    },
    {
        "family": "Llama",
        "size_slot": "Large",
        "model": "openrouter/meta-llama/llama-4-maverick",
        "benchmark": "SMID",
        "status": "Completed",
        "note": "Completed successfully in the family-size image queue.",
    },
]

IMAGE_EXPANSION_EXCLUSIONS = [
    "DeepSeek: no vision route in the current family-size plan.",
    "Qwen medium: no clean Qwen medium VL route was locked for this pass.",
    "Llama medium: the chosen 70B route is text-only.",
    "MiniMax image: the shared `minimax-01` route does not map cleanly onto separate medium / large size slots.",
]

SUPPLEMENTARY_MODEL_PROGRESS = [
    {
        "family": "Llama",
        "status_relative_to_closed_release": "Completed locally, outside the closed Option 1 counts",
        "exact_route": "openrouter/meta-llama/llama-3.2-11b-vision-instruct",
        "papers_covered": 5,
        "tasks_completed": 7,
        "benchmark_faithful_tasks": 6,
        "proxy_tasks": 1,
        "samples": 102886,
        "benchmark_faithful_macro_accuracy": 0.427602,
        "completed_benchmark_lines": "UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy",
        "missing_benchmark_lines": "Benchmark-faithful Denevil via MoralPrompt",
        "note": "Combines the original 2026-04-19-option1-llama32-11b-vision successes (UniMoral + SMID moral rating) with recovery-v3 completions for the remaining five tasks after a temporary OpenRouter key-limit stall.",
    },
    {
        "family": "MiniMax",
        "status_relative_to_closed_release": "Attempted locally, but current results are not usable",
        "exact_route": "minimax-m2.1 + minimax-01",
        "papers_covered": 0,
        "tasks_completed": 0,
        "benchmark_faithful_tasks": 0,
        "proxy_tasks": 0,
        "samples": 0,
        "benchmark_faithful_macro_accuracy": None,
        "completed_benchmark_lines": "None yet",
        "missing_benchmark_lines": "UniMoral; SMID; Value Kaleidoscope; CCD-Bench; Denevil proxy; Benchmark-faithful Denevil via MoralPrompt",
        "note": "A formal small-model run exists, but OpenRouter key-limit failures interrupted both the text and SMID legs, so the line still needs a clean rerun.",
    },
]

LOCAL_EXPANSION_CHECKPOINT = [
    {
        "line": "Qwen-L SMID recovery",
        "status": "done",
        "note": "Completed April 20, 2026 via openrouter/qwen/qwen2.5-vl-72b-instruct after the earlier qwen3-vl-32b moderation stop.",
    },
    {
        "line": "Gemma-L text batch",
        "status": "done",
        "note": "Completed April 21, 2026. UniMoral, Value Kaleidoscope, CCD-Bench, and the Denevil proxy task all finished successfully.",
    },
    {
        "line": "Gemma-M text batch",
        "status": "done",
        "note": "Completed April 21, 2026. The medium text route now has a full local line across all five benchmark papers.",
    },
    {
        "line": "Qwen-M text batch",
        "status": "partial",
        "note": "UniMoral and Value Kaleidoscope relevance completed successfully. Value Kaleidoscope valence started, but no active process is running now.",
    },
    {
        "line": "Qwen-L text batch",
        "status": "partial",
        "note": "UniMoral completed successfully. Value Kaleidoscope relevance started, but no active process is running now.",
    },
    {
        "line": "Llama-L SMID",
        "status": "done",
        "note": "The large Llama vision line is complete locally.",
    },
    {
        "line": "Next queued text lines",
        "status": "queue",
        "note": "Llama-M, Llama-L, MiniMax-M, DeepSeek-M, and MiniMax-L remain queued. Qwen-M and Qwen-L now have partial local progress rather than a clean queued state.",
    },
]

FAMILY_SIZE_PROGRESS = [
    {
        "family": "Qwen",
        "size_slot": "S",
        "line_label": "Qwen-S",
        "text_route": "openrouter/qwen/qwen3-8b",
        "vision_route": "openrouter/qwen/qwen3-vl-8b-instruct",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "done",
        "ccd_bench": "done",
        "denevil": "proxy",
        "summary_note": "Frozen Option 1 line.",
    },
    {
        "family": "Qwen",
        "size_slot": "M",
        "line_label": "Qwen-M",
        "text_route": "openrouter/qwen/qwen3-14b",
        "vision_route": "TBD",
        "unimoral": "done",
        "smid": "tbd",
        "value_kaleidoscope": "partial",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "UniMoral is done, Value Kaleidoscope started but did not finish, and no active medium Qwen text process is currently running.",
    },
    {
        "family": "Qwen",
        "size_slot": "L",
        "line_label": "Qwen-L",
        "text_route": "openrouter/qwen/qwen3-32b",
        "vision_route": "openrouter/qwen/qwen2.5-vl-72b-instruct (recovery complete)",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "partial",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "SMID and UniMoral are done, Value Kaleidoscope started but did not finish, and no active large Qwen text process is currently running.",
    },
    {
        "family": "MiniMax",
        "size_slot": "S",
        "line_label": "MiniMax-S",
        "text_route": "openrouter/minimax/minimax-m2.1",
        "vision_route": "openrouter/minimax/minimax-01",
        "unimoral": "error",
        "smid": "error",
        "value_kaleidoscope": "error",
        "ccd_bench": "error",
        "denevil": "error",
        "summary_note": "Attempted, but key-limit failures made the line unusable.",
    },
    {
        "family": "MiniMax",
        "size_slot": "M",
        "line_label": "MiniMax-M",
        "text_route": "openrouter/minimax/minimax-m2.5",
        "vision_route": "TBD",
        "unimoral": "queue",
        "smid": "tbd",
        "value_kaleidoscope": "queue",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "Text queued; no medium SMID route is fixed yet.",
    },
    {
        "family": "MiniMax",
        "size_slot": "L",
        "line_label": "MiniMax-L",
        "text_route": "openrouter/minimax/minimax-m2.7",
        "vision_route": "TBD",
        "unimoral": "queue",
        "smid": "tbd",
        "value_kaleidoscope": "queue",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "Text queued; no large SMID route is fixed yet.",
    },
    {
        "family": "DeepSeek",
        "size_slot": "S",
        "line_label": "DeepSeek-S",
        "text_route": "TBD",
        "vision_route": "-",
        "unimoral": "tbd",
        "smid": "-",
        "value_kaleidoscope": "tbd",
        "ccd_bench": "tbd",
        "denevil": "tbd",
        "summary_note": "Small baseline not frozen; no vision route is in scope.",
    },
    {
        "family": "DeepSeek",
        "size_slot": "M",
        "line_label": "DeepSeek-M",
        "text_route": "openrouter/deepseek/deepseek-r1-distill-qwen-32b",
        "vision_route": "-",
        "unimoral": "queue",
        "smid": "-",
        "value_kaleidoscope": "queue",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "Text queued; no vision route is in scope.",
    },
    {
        "family": "DeepSeek",
        "size_slot": "L",
        "line_label": "DeepSeek-L",
        "text_route": "openrouter/deepseek/deepseek-chat-v3.1",
        "vision_route": "-",
        "unimoral": "done",
        "smid": "-",
        "value_kaleidoscope": "done",
        "ccd_bench": "done",
        "denevil": "proxy",
        "summary_note": "Frozen large text line; no SMID route was included.",
    },
    {
        "family": "Llama",
        "size_slot": "S",
        "line_label": "Llama-S",
        "text_route": "openrouter/meta-llama/llama-3.2-11b-vision-instruct",
        "vision_route": "openrouter/meta-llama/llama-3.2-11b-vision-instruct",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "done",
        "ccd_bench": "done",
        "denevil": "proxy",
        "summary_note": "Complete locally across all five papers.",
    },
    {
        "family": "Llama",
        "size_slot": "M",
        "line_label": "Llama-M",
        "text_route": "openrouter/meta-llama/llama-3.3-70b-instruct",
        "vision_route": "-",
        "unimoral": "queue",
        "smid": "-",
        "value_kaleidoscope": "queue",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "Text queued; no SMID run is planned.",
    },
    {
        "family": "Llama",
        "size_slot": "L",
        "line_label": "Llama-L",
        "text_route": "openrouter/meta-llama/llama-4-maverick",
        "vision_route": "openrouter/meta-llama/llama-4-maverick",
        "unimoral": "queue",
        "smid": "done",
        "value_kaleidoscope": "queue",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "SMID done; text is still queued.",
    },
    {
        "family": "Gemma",
        "size_slot": "S",
        "line_label": "Gemma-S",
        "text_route": "openrouter/google/gemma-3-4b-it",
        "vision_route": "openrouter/google/gemma-3-4b-it",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "done",
        "ccd_bench": "done",
        "denevil": "proxy",
        "summary_note": "Frozen Option 1 recovery line.",
    },
    {
        "family": "Gemma",
        "size_slot": "M",
        "line_label": "Gemma-M",
        "text_route": "openrouter/google/gemma-3-12b-it",
        "vision_route": "openrouter/google/gemma-3-12b-it",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "done",
        "ccd_bench": "done",
        "denevil": "proxy",
        "summary_note": "Complete locally across all five papers, with Denevil covered through the same proxy route used elsewhere in this deliverable.",
    },
    {
        "family": "Gemma",
        "size_slot": "L",
        "line_label": "Gemma-L",
        "text_route": "openrouter/google/gemma-3-27b-it",
        "vision_route": "openrouter/google/gemma-3-27b-it",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "done",
        "ccd_bench": "done",
        "denevil": "proxy",
        "summary_note": "Complete locally across all five papers, with Denevil covered through the same proxy route used elsewhere in this deliverable.",
    },
]

CURRENT_RESULT_LINES = [
    {
        "line_label": "Qwen-S",
        "scope": "Frozen Option 1",
        "status": "done",
        "coverage": "5 benchmark lines complete (`Denevil` via proxy)",
        "note": "Primary small Qwen release line.",
    },
    {
        "line_label": "DeepSeek-L",
        "scope": "Frozen Option 1",
        "status": "done",
        "coverage": "4 benchmark lines plus `Denevil` proxy; no SMID route",
        "note": "Primary large DeepSeek release line.",
    },
    {
        "line_label": "Gemma-S",
        "scope": "Frozen Option 1",
        "status": "done",
        "coverage": "5 benchmark lines complete (`Denevil` via proxy)",
        "note": "Primary small Gemma release line.",
    },
    {
        "line_label": "Llama-S",
        "scope": "Complete local line",
        "status": "done",
        "coverage": "5 benchmark lines complete (`Denevil` via proxy)",
        "note": "Finished locally, outside the frozen Option 1 counts.",
    },
    {
        "line_label": "Gemma-M",
        "scope": "Complete local line",
        "status": "done",
        "coverage": "5 benchmark lines complete (`Denevil` via proxy)",
        "note": "Finished locally on April 21, 2026.",
    },
    {
        "line_label": "Gemma-L",
        "scope": "Complete local line",
        "status": "done",
        "coverage": "5 benchmark lines complete (`Denevil` via proxy)",
        "note": "Finished locally on April 21, 2026.",
    },
    {
        "line_label": "Qwen-M",
        "scope": "Partial local line",
        "status": "partial",
        "coverage": "UniMoral done; Value Kaleidoscope partially completed",
        "note": "No active process detected at this snapshot.",
    },
    {
        "line_label": "Qwen-L",
        "scope": "Partial local line",
        "status": "partial",
        "coverage": "SMID and UniMoral done; Value Kaleidoscope partially completed",
        "note": "No active process detected at this snapshot.",
    },
    {
        "line_label": "MiniMax-S",
        "scope": "Attempted local line",
        "status": "error",
        "coverage": "No usable benchmark line completed",
        "note": "OpenRouter key-limit failures interrupted both text and image paths.",
    },
]

AUTHORITATIVE_COMPARISON_LINES = {
    "Qwen": {
        "line_label": "Qwen-S",
        "family": "Qwen",
        "size_slot": "S",
        "route": "openrouter/qwen/qwen3-8b + openrouter/qwen/qwen3-vl-8b-instruct",
        "coverage_note": "Frozen Option 1 line.",
    },
    "DeepSeek": {
        "line_label": "DeepSeek-L",
        "family": "DeepSeek",
        "size_slot": "L",
        "route": "openrouter/deepseek/deepseek-chat-v3.1",
        "coverage_note": "Frozen large-class text line. No SMID vision route was included.",
    },
    "Gemma": {
        "line_label": "Gemma-S",
        "family": "Gemma",
        "size_slot": "S",
        "route": "openrouter/google/gemma-3-4b-it",
        "coverage_note": "Frozen Option 1 recovery line.",
    },
}

SUPPLEMENTARY_COMPARISON_LINES = [
    {
        "line_label": "Llama-S",
        "family": "Llama",
        "size_slot": "S",
        "route": "openrouter/meta-llama/llama-3.2-11b-vision-instruct",
        "unimoral_action_accuracy": 0.6479963570127505,
        "smid_average_accuracy": 0.21642298537912275,
        "value_average_accuracy": 0.5285828754578754,
        "coverage_note": "Complete locally across all five papers, but still outside the frozen Option 1 snapshot counts.",
    }
]

STATUS_DISPLAY = {
    "done": "Done",
    "proxy": "Proxy",
    "live": "Live",
    "partial": "Partial",
    "error": "Error",
    "queue": "Queue",
    "prep": "Prep",
    "tbd": "TBD",
    "-": "-",
}

STATUS_LEGEND = [
    ("Done", "Finished with a usable result."),
    ("Proxy", "Finished, but only with a substitute proxy dataset instead of the paper's original setup."),
    ("Live", "Currently running locally."),
    ("Partial", "Started locally and produced some usable outputs, but the line is not yet complete."),
    ("Error", "A formal attempt exists, but the current result is not usable."),
    ("Queue", "Approved and queued next."),
    ("TBD", "The family-size route is not frozen yet."),
    ("-", "No run is planned on that line right now."),
]


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            parsed = dict(row)
            parsed["completed_samples"] = int(parsed["completed_samples"])
            parsed["total_samples"] = int(parsed["total_samples"])
            parsed["progress_pct"] = float(parsed["progress_pct"])
            parsed["accuracy"] = float(parsed["accuracy"]) if parsed["accuracy"] else None
            parsed["stderr"] = float(parsed["stderr"]) if parsed["stderr"] else None
            rows.append(parsed)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fmt_float(value: float | None, digits: int = 3) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def serialize_model_summary_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_family": row["model_family"],
        "tasks": row["tasks"],
        "benchmark_faithful_tasks": row["faithful_tasks"],
        "proxy_tasks": row["proxy_tasks"],
        "samples": row["samples"],
        "scored_tasks": row["scored_tasks"],
        "benchmark_faithful_macro_accuracy": None if row["faithful_macro_accuracy"] is None else row["faithful_macro_accuracy"],
    }


def serialize_supplementary_progress_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": row["family"],
        "status_relative_to_closed_release": row["status_relative_to_closed_release"],
        "exact_route": row["exact_route"],
        "papers_covered": row["papers_covered"],
        "tasks_completed": row["tasks_completed"],
        "benchmark_faithful_tasks": row["benchmark_faithful_tasks"],
        "proxy_tasks": row["proxy_tasks"],
        "completed_benchmark_lines": row["completed_benchmark_lines"],
        "missing_benchmark_lines": row["missing_benchmark_lines"],
        "samples": row["samples"],
        "benchmark_faithful_macro_accuracy": None
        if row["benchmark_faithful_macro_accuracy"] is None
        else row["benchmark_faithful_macro_accuracy"],
        "note": row["note"],
    }


def markdown_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def csv_join(values: list[str]) -> str:
    return "; ".join(ordered_unique(values))


def build_model_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for model in MODEL_ORDER:
        model_rows = [row for row in rows if row["model_family"] == model]
        scored_rows = [row for row in model_rows if row["benchmark_mode"] == "benchmark_faithful" and row["accuracy"] is not None]
        grouped[model] = {
            "model_family": model,
            "tasks": len(model_rows),
            "faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in model_rows),
            "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in model_rows),
            "samples": sum(row["total_samples"] for row in model_rows),
            "scored_tasks": len(scored_rows),
            "faithful_macro_accuracy": mean(row["accuracy"] for row in scored_rows) if scored_rows else None,
        }
    return [grouped[model] for model in MODEL_ORDER]


def build_benchmark_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for benchmark in BENCHMARK_ORDER:
        bench_rows = [row for row in rows if row["benchmark"] == benchmark]
        output.append(
            {
                "benchmark": benchmark,
                "task_types": len({row["task"] for row in bench_rows}),
                "evaluated_lines": len(bench_rows),
                "models_covered": len({row["model_family"] for row in bench_rows}),
                "samples": sum(row["total_samples"] for row in bench_rows),
                "modes": ", ".join(sorted({row["benchmark_mode"] for row in bench_rows})),
            }
        )
    return output


def build_benchmark_catalog(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for benchmark in BENCHMARK_ORDER:
        metadata = BENCHMARK_METADATA[benchmark]
        bench_rows = [row for row in rows if row["benchmark"] == benchmark]
        model_families = [model for model in MODEL_ORDER if any(row["model_family"] == model for row in bench_rows)]
        output.append(
            {
                "benchmark": benchmark,
                "citation": metadata["citation"],
                "paper_title": metadata["paper_title"],
                "paper_url": metadata["paper_url"],
                "dataset_label": metadata["dataset_label"],
                "dataset_url": metadata.get("dataset_url", ""),
                "dataset_alt_url": metadata.get("dataset_alt_url", ""),
                "modality": metadata["modality"],
                "repo_tasks": csv_join(metadata["repo_tasks"]),
                "current_release_scope": metadata["current_release_scope"],
                "current_release_mode": ", ".join(sorted({row["benchmark_mode"] for row in bench_rows})) if bench_rows else "not_run",
                "models_in_release": csv_join(model_families),
                "samples_in_release": sum(row["total_samples"] for row in bench_rows),
                "dataset_note": metadata["dataset_note"],
            }
        )
    return output


def build_model_roster(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model_family"], row["model"])].append(row)

    output: list[dict[str, Any]] = []
    for model_family in MODEL_ORDER:
        family_keys = [key for key in grouped if key[0] == model_family]
        for _, model in sorted(family_keys, key=lambda item: item[1]):
            route_rows = grouped[(model_family, model)]
            metadata = MODEL_ROUTE_METADATA.get(model, {})
            output.append(
                {
                    "model_family": model_family,
                    "model": model,
                    "size_hint": metadata.get("size_hint", ""),
                    "modality": metadata.get("modality", ""),
                    "benchmarks": csv_join([row["benchmark"] for row in route_rows]),
                    "tasks": csv_join([row["task"] for row in route_rows]),
                    "release_modes": csv_join([row["benchmark_mode"] for row in route_rows]),
                    "samples": sum(row["total_samples"] for row in route_rows),
                    "note": metadata.get("note", ""),
                }
            )
    return output


def build_future_model_plan() -> list[dict[str, Any]]:
    return list(FUTURE_MODEL_PLAN)


def build_supplementary_model_progress() -> list[dict[str, Any]]:
    return list(SUPPLEMENTARY_MODEL_PROGRESS)


def build_family_size_progress() -> list[dict[str, Any]]:
    return list(FAMILY_SIZE_PROGRESS)


def append_local_expansion_checkpoint_table(lines: list[str]) -> None:
    lines.extend(
        [
            "| Line or batch | Status | Note |",
            "| --- | --- | --- |",
        ]
    )
    for row in LOCAL_EXPANSION_CHECKPOINT:
        lines.append(f"| `{row['line']}` | {STATUS_DISPLAY[row['status']]} | {row['note']} |")


def build_faithful_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    faithful_rows = [row for row in rows if row["benchmark_mode"] == "benchmark_faithful"]
    output: list[dict[str, Any]] = []
    for row in faithful_rows:
        output.append(
            {
                "benchmark": row["benchmark"],
                "benchmark_scope": row["benchmark_scope"],
                "model_family": row["model_family"],
                "task": row["task"],
                "model": row["model"],
                "accuracy": fmt_float(row["accuracy"], 6),
                "stderr": fmt_float(row["stderr"], 6),
                "samples": row["total_samples"],
                "status": row["status"],
            }
        )
    return output


def build_benchmark_comparison(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comparison_rows: list[dict[str, Any]] = []

    for model_family, metadata in AUTHORITATIVE_COMPARISON_LINES.items():
        model_rows = [row for row in rows if row["model_family"] == model_family]
        unimoral_row = next(row for row in model_rows if row["benchmark"] == "UniMoral")
        smid_rows = [row for row in model_rows if row["benchmark"] == "SMID" and row["accuracy"] is not None]
        value_rows = [row for row in model_rows if row["benchmark"] == "Value Kaleidoscope" and row["accuracy"] is not None]
        comparison_rows.append(
            {
                **metadata,
                "unimoral_action_accuracy": float(unimoral_row["accuracy"]) if unimoral_row["accuracy"] is not None else None,
                "smid_average_accuracy": mean(float(row["accuracy"]) for row in smid_rows) if smid_rows else None,
                "value_average_accuracy": mean(float(row["accuracy"]) for row in value_rows) if value_rows else None,
            }
        )

    comparison_rows.extend(SUPPLEMENTARY_COMPARISON_LINES)
    lookup = {row["line_label"]: row for row in comparison_rows}
    return [lookup[label] for label in COMPARABLE_RESULT_ORDER if label in lookup]


def build_coverage_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for model in MODEL_ORDER:
        model_rows = [row for row in rows if row["model_family"] == model]
        for benchmark in BENCHMARK_ORDER:
            cell_rows = [row for row in model_rows if row["benchmark"] == benchmark]
            if not cell_rows:
                output.append(
                    {
                        "model_family": model,
                        "benchmark": benchmark,
                        "status": "not_run",
                        "completed_tasks": 0,
                        "expected_tasks": BENCHMARK_TASK_COUNTS[benchmark],
                        "label": "-",
                    }
                )
                continue
            mode = cell_rows[0]["benchmark_mode"]
            status = "proxy" if mode == "proxy" else "benchmark_faithful"
            completed_tasks = len(cell_rows)
            expected = BENCHMARK_TASK_COUNTS[benchmark]
            label = "proxy" if status == "proxy" else f"{completed_tasks}/{expected}"
            output.append(
                {
                    "model_family": model,
                    "benchmark": benchmark,
                    "status": status,
                    "completed_tasks": completed_tasks,
                    "expected_tasks": expected,
                    "label": label,
                }
            )
    return output


def escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def relative_luminance(color: str) -> float:
    def linearize(channel: int) -> float:
        scaled = channel / 255
        if scaled <= 0.03928:
            return scaled / 12.92
        return ((scaled + 0.055) / 1.055) ** 2.4

    r, g, b = hex_to_rgb(color)
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def text_classes_for_fill(color: str) -> tuple[str, str]:
    return ("celltext", "cellsub") if relative_luminance(color) < 0.32 else ("celltext-dark", "cellsub-dark")



def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in rgb)



def interpolate_color(start: str, end: str, weight: float) -> str:
    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)
    mixed = tuple(round(s + (e - s) * weight) for s, e in zip(start_rgb, end_rgb))
    return rgb_to_hex(mixed)


def nice_tick_step(max_value: int, target_ticks: int = 4) -> int:
    if max_value <= 0:
        return 1

    raw_step = max_value / target_ticks
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude

    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 2.5:
        nice = 2.5
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10
    return int(nice * magnitude)


def build_axis_ticks(max_value: int, target_ticks: int = 4) -> tuple[list[int], int]:
    step = nice_tick_step(max_value, target_ticks=target_ticks)
    upper = int(math.ceil(max_value / step) * step)
    return [step * index for index in range(target_ticks + 1)], upper


def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<defs>",
        '<linearGradient id="panelGradient" x1="0" x2="0" y1="0" y2="1">',
        '<stop offset="0%" stop-color="#ffffff"/>',
        '<stop offset="100%" stop-color="#f8fafc"/>',
        "</linearGradient>",
        '<pattern id="diagonalHatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        '<line x1="0" y1="0" x2="0" y2="8" stroke="#cdd6e1" stroke-width="3"/>',
        "</pattern>",
        '<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">',
        '<feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#9fb0c2" flood-opacity="0.18"/>',
        "</filter>",
        "<style>",
        ".canvas { fill: #f3f6fa; }",
        ".title { font: 700 26px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #12263a; }",
        ".subtitle { font: 400 14px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #5c6b7a; }",
        ".axis { font: 600 14px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #22313f; }",
        ".label { font: 500 13px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #22313f; }",
        ".metric { font: 700 20px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #12263a; }",
        ".celltext { font: 700 16px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #ffffff; }",
        ".celltext-dark { font: 700 16px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #173042; }",
        ".cellsub { font: 500 11px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: rgba(255,255,255,0.88); }",
        ".cellsub-dark { font: 600 11px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #385062; }",
        ".body { font: 500 12px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #22313f; }",
        ".small { font: 500 11px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #5c6b7a; }",
        ".tiny { font: 600 10px 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; fill: #6b7c8f; letter-spacing: 0.04em; }",
        ".grid { fill: #ffffff; stroke: #d7dee6; stroke-width: 1.25; }",
        ".panel { fill: url(#panelGradient); stroke: #dbe4ee; stroke-width: 1.25; filter: url(#softShadow); }",
        ".subpanel { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1; }",
        ".legend-card { fill: #ffffff; stroke: #dbe4ee; stroke-width: 1; }",
        ".guide { stroke: #d7dee6; stroke-width: 1; stroke-dasharray: 4 6; }",
        ".baseline { stroke: #aab7c6; stroke-width: 1.1; }",
        ".muted-cell { fill: #eef2f7; stroke: #d7dee6; stroke-width: 1; }",
        ".muted-bar { fill: #ecf1f6; stroke: #d7dee6; stroke-width: 1; }",
        ".outline { stroke: rgba(255,255,255,0.9); stroke-width: 1; }",
        "</style>",
        "</defs>",
    ]


def render_coverage_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1220, 590
    left, top = 220, 156
    cell_w, cell_h = 176, 82
    colors = {"benchmark_faithful": "#2f855a", "proxy": "#b7791f", "not_run": "#cbd5e1"}

    matrix = {(row["model_family"], row["benchmark"]): row for row in rows}
    status_counts = {
        status: sum(row["status"] == status for row in rows)
        for status in ("benchmark_faithful", "proxy", "not_run")
    }
    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Option 1 benchmark coverage matrix</title>",
            "<desc>Coverage matrix for the frozen Option 1 release across Qwen, DeepSeek, and Gemma for the five benchmark lines.</desc>",
            '<text x="48" y="64" class="title">Option 1 Benchmark Coverage</text>',
            '<text x="48" y="88" class="subtitle">Green cells follow the paper setup. Amber cells are proxy-only. Hatched gray cells were not part of the frozen release.</text>',
        ]
    )

    for index, benchmark in enumerate(BENCHMARK_ORDER):
        x = left + index * cell_w + cell_w / 2
        lines.append(f'<text x="{x}" y="136" text-anchor="middle" class="axis">{escape_xml(benchmark)}</text>')

    for row_index, model in enumerate(MODEL_ORDER):
        y = top + row_index * cell_h + cell_h / 2 + 6
        lines.append(f'<text x="{left - 24}" y="{y}" text-anchor="end" class="axis">{escape_xml(model)}</text>')
        for col_index, benchmark in enumerate(BENCHMARK_ORDER):
            x = left + col_index * cell_w
            y0 = top + row_index * cell_h
            cell = matrix[(model, benchmark)]
            color = colors[cell["status"]]
            lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="18" fill="{color}" class="outline"/>')
            if cell["status"] == "not_run":
                lines.append(
                    f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="18" fill="url(#diagonalHatch)" opacity="0.7"/>'
                )
            label_x = x + (cell_w - 14) / 2
            main_class, sub_class = ("celltext-dark", "cellsub-dark") if cell["status"] == "not_run" else ("celltext", "cellsub")
            lines.append(f'<text x="{label_x}" y="{y0 + 36}" text-anchor="middle" class="{main_class}">{escape_xml(cell["label"])}</text>')
            detail = "paper setup" if cell["status"] == "benchmark_faithful" else ("proxy only" if cell["status"] == "proxy" else "not in release")
            lines.append(f'<text x="{label_x}" y="{y0 + 58}" text-anchor="middle" class="{sub_class}">{escape_xml(detail)}</text>')

    lines.append('<rect x="846" y="446" width="326" height="76" rx="16" class="legend-card"/>')
    lines.append('<text x="872" y="470" class="tiny">SLICE SUMMARY</text>')
    lines.append(f'<text x="872" y="491" class="body">Paper setup: {status_counts["benchmark_faithful"]} cells</text>')
    lines.append(f'<text x="872" y="509" class="body">Proxy only: {status_counts["proxy"]} cells</text>')
    lines.append(f'<text x="872" y="527" class="body">Not in release: {status_counts["not_run"]} cell</text>')

    legend_y = height - 64
    legend_items = [("#2f855a", "Paper setup"), ("#b7791f", "Proxy only"), ("#cbd5e1", "Not in release")]
    for index, (color, label) in enumerate(legend_items):
        x = 48 + index * 210
        lines.append(f'<rect x="{x}" y="{legend_y - 14}" width="18" height="18" rx="4" fill="{color}"/>')
        if label == "Not in release":
            lines.append(f'<rect x="{x}" y="{legend_y - 14}" width="18" height="18" rx="4" fill="url(#diagonalHatch)" opacity="0.7"/>')
        lines.append(f'<text x="{x + 28}" y="{legend_y}" class="label">{escape_xml(label)}</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def render_accuracy_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1220, 630
    left, top = 210, 148
    cell_w, cell_h = 170, 78
    scored = [row["accuracy"] for row in rows if row["accuracy"] is not None]
    min_acc = min(scored)
    max_acc = max(scored)
    lookup = {(row["model_family"], row["benchmark"], row["benchmark_scope"]): row for row in rows if row["accuracy"] is not None}

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Option 1 accuracy heatmap</title>",
            "<desc>Heatmap of comparable accuracy metrics across the frozen Option 1 model families and benchmark task scopes.</desc>",
            '<text x="48" y="64" class="title">Option 1 Accuracy Heatmap</text>',
            '<text x="48" y="88" class="subtitle">Only tasks with directly comparable accuracy metrics are shown. Hatched cells mark tasks that were not part of the frozen closed slice.</text>',
        ]
    )

    for index, (_, _, label) in enumerate(ACCURACY_SCOPE_ORDER):
        x = left + index * cell_w + cell_w / 2
        first, second = label.split("\n")
        lines.append(f'<text x="{x}" y="122" text-anchor="middle" class="axis">{escape_xml(first)}</text>')
        lines.append(f'<text x="{x}" y="140" text-anchor="middle" class="small">{escape_xml(second)}</text>')

    for row_index, model in enumerate(MODEL_ORDER):
        y = top + row_index * cell_h + cell_h / 2 + 6
        lines.append(f'<text x="{left - 24}" y="{y}" text-anchor="end" class="axis">{escape_xml(model)}</text>')
        for col_index, (benchmark, scope, _) in enumerate(ACCURACY_SCOPE_ORDER):
            x = left + col_index * cell_w
            y0 = top + row_index * cell_h
            item = lookup.get((model, benchmark, scope))
            if item is None:
                lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" class="muted-cell"/>')
                lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="url(#diagonalHatch)" opacity="0.8"/>')
                lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 36}" text-anchor="middle" class="label">n/a</text>')
                lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 58}" text-anchor="middle" class="small">not in slice</text>')
                continue
            weight = 0.0 if math.isclose(max_acc, min_acc) else (item["accuracy"] - min_acc) / (max_acc - min_acc)
            color = interpolate_color("#f2e8cf", "#1f6f78", weight)
            main_class, sub_class = text_classes_for_fill(color)
            lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="{color}" stroke="#ffffff" stroke-width="1"/>')
            lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 36}" text-anchor="middle" class="{main_class}">{item["accuracy"] * 100:.1f}%</text>')
            lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 58}" text-anchor="middle" class="{sub_class}">stderr {item["stderr"]:.3f}</text>')

    legend_x = 670
    legend_y = height - 92
    legend_w = 360
    legend_steps = 12
    lines.append(f'<rect x="{legend_x - 20}" y="{legend_y - 36}" width="446" height="86" rx="16" class="legend-card"/>')
    lines.append(f'<text x="{legend_x}" y="{legend_y - 18}" class="axis">Accuracy scale</text>')
    lines.append(f'<text x="{legend_x}" y="{legend_y - 2}" class="small">Lighter cells mean lower accuracy; darker cells mean higher accuracy.</text>')
    for step in range(legend_steps):
        weight = step / (legend_steps - 1)
        color = interpolate_color("#f2e8cf", "#1f6f78", weight)
        x = legend_x + step * (legend_w / legend_steps)
        lines.append(f'<rect x="{x:.2f}" y="{legend_y + 10}" width="{legend_w / legend_steps + 1:.2f}" height="16" fill="{color}" stroke="#ffffff" stroke-width="0.6"/>')
    lines.append(f'<text x="{legend_x}" y="{legend_y + 44}" class="small">{min_acc * 100:.1f}%</text>')
    lines.append(f'<text x="{legend_x + legend_w}" y="{legend_y + 44}" text-anchor="end" class="small">{max_acc * 100:.1f}%</text>')
    lines.append(f'<rect x="{legend_x + 382}" y="{legend_y + 6}" width="24" height="24" rx="6" class="muted-cell"/>')
    lines.append(f'<rect x="{legend_x + 382}" y="{legend_y + 6}" width="24" height="24" rx="6" fill="url(#diagonalHatch)" opacity="0.8"/>')
    lines.append(f'<text x="{legend_x + 416}" y="{legend_y + 24}" class="small">not in slice</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def render_sample_volume_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1220, 670
    left, top = 280, 184
    bar_w = 520
    bar_h = 26
    gap = 86
    breakdown_x = 888

    benchmark_totals: dict[str, dict[str, int]] = {
        benchmark: {"benchmark_faithful": 0, "proxy": 0} for benchmark in SAMPLE_BAR_ORDER
    }
    for row in rows:
        mode = "proxy" if row["benchmark_mode"] == "proxy" else "benchmark_faithful"
        benchmark_totals[row["benchmark"]][mode] += row["total_samples"]

    max_total = max(sum(parts.values()) for parts in benchmark_totals.values())
    total_samples = sum(row["total_samples"] for row in rows)
    ticks, axis_max = build_axis_ticks(max_total, target_ticks=4)

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Sample volume by benchmark</title>",
            "<desc>Sample counts in the frozen Option 1 release, with paper-setup and proxy samples separated by benchmark.</desc>",
            '<text x="48" y="64" class="title">Sample Volume by Benchmark</text>',
            f'<text x="48" y="88" class="subtitle">The closed Option 1 release contains {total_samples:,} evaluated samples. Bars show each benchmark share on a common scale, with the paper-setup and proxy split preserved.</text>',
            f'<text x="{left}" y="146" class="tiny">COMMON SAMPLE SCALE</text>',
            f'<text x="{breakdown_x}" y="146" class="tiny">BREAKDOWN</text>',
        ]
    )

    axis_top = top - 10
    axis_bottom = top + (len(SAMPLE_BAR_ORDER) - 1) * gap + bar_h + 8
    for tick in ticks:
        x = left + (bar_w * tick / axis_max if axis_max else 0)
        lines.append(f'<line x1="{x:.2f}" y1="{axis_top}" x2="{x:.2f}" y2="{axis_bottom}" class="guide"/>')
        lines.append(f'<text x="{x:.2f}" y="{axis_top - 10}" text-anchor="middle" class="small">{tick:,}</text>')

    for index, benchmark in enumerate(SAMPLE_BAR_ORDER):
        y = top + index * gap
        faithful = benchmark_totals[benchmark]["benchmark_faithful"]
        proxy = benchmark_totals[benchmark]["proxy"]
        total = faithful + proxy
        share_pct = 0 if total_samples == 0 else total / total_samples
        faithful_w = 0 if axis_max == 0 else bar_w * faithful / axis_max
        proxy_w = 0 if axis_max == 0 else bar_w * proxy / axis_max
        label_x = breakdown_x - 18
        lines.append(f'<text x="{left - 20}" y="{y + 18}" text-anchor="end" class="axis">{escape_xml(benchmark)}</text>')
        lines.append(f'<rect x="{left}" y="{y}" width="{bar_w}" height="{bar_h}" rx="10" fill="#e2e8f0"/>')
        if faithful_w:
            lines.append(f'<rect x="{left}" y="{y}" width="{faithful_w:.2f}" height="{bar_h}" rx="10" fill="#2f855a"/>')
        if proxy_w:
            lines.append(f'<rect x="{left + faithful_w:.2f}" y="{y}" width="{proxy_w:.2f}" height="{bar_h}" rx="10" fill="#b7791f"/>')
        lines.append(f'<text x="{label_x}" y="{y + 17}" text-anchor="end" class="metric">{total:,}</text>')
        lines.append(f'<text x="{label_x}" y="{y + 35}" text-anchor="end" class="small">{share_pct * 100:.1f}% of release</text>')
        lines.append(f'<rect x="{breakdown_x}" y="{y - 8}" width="250" height="52" rx="14" class="subpanel"/>')
        lines.append(f'<rect x="{breakdown_x + 16}" y="{y + 6}" width="10" height="10" rx="2.5" fill="#2f855a"/>')
        lines.append(f'<text x="{breakdown_x + 36}" y="{y + 15}" class="body">Paper setup: {faithful:,}</text>')
        lines.append(f'<rect x="{breakdown_x + 16}" y="{y + 27}" width="10" height="10" rx="2.5" fill="#b7791f"/>')
        lines.append(f'<text x="{breakdown_x + 36}" y="{y + 36}" class="body">Proxy: {proxy:,}</text>')

    legend_y = height - 78
    lines.append(f'<rect x="48" y="{legend_y - 14}" width="18" height="18" rx="4" fill="#2f855a"/>')
    lines.append(f'<text x="76" y="{legend_y}" class="label">paper-setup samples</text>')
    lines.append(f'<rect x="286" y="{legend_y - 14}" width="18" height="18" rx="4" fill="#b7791f"/>')
    lines.append(f'<text x="314" y="{legend_y}" class="label">proxy samples</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def render_benchmark_accuracy_bars_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1220, 960
    panel_left, panel_width = 280, 800
    bar_height, bar_gap = 28, 14
    panel_top, panel_gap = 192, 238
    tick_count = 5
    line_colors = {
        "Qwen-S": "#0f766e",
        "DeepSeek-L": "#2563eb",
        "Llama-S": "#c2410c",
        "Gemma-S": "#7c3aed",
    }
    metric_specs = [
        (
            "unimoral_action_accuracy",
            "UniMoral",
            "Action prediction accuracy",
        ),
        (
            "smid_average_accuracy",
            "SMID",
            "Average of moral rating and foundation classification",
        ),
        (
            "value_average_accuracy",
            "Value Kaleidoscope",
            "Average of relevance and valence accuracy",
        ),
    ]

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Comparable accuracy by benchmark</title>",
            "<desc>Horizontal bar panels comparing completed family-size lines on benchmarks with directly comparable accuracy metrics.</desc>",
            '<text x="48" y="64" class="title">Comparable Accuracy by Benchmark</text>',
            '<text x="48" y="88" class="subtitle">Each panel keeps the same completed lines in the same order. Hatched rows mark lines without a comparable run for that benchmark.</text>',
        ]
    )

    lines.append('<text x="48" y="122" class="axis">Comparable completed lines</text>')
    for index, line_label in enumerate(COMPARABLE_RESULT_ORDER):
        if line_label not in line_colors:
            continue
        x = 48 + index * 170
        lines.append(f'<rect x="{x}" y="138" width="18" height="18" rx="4" fill="{line_colors[line_label]}"/>')
        lines.append(f'<text x="{x + 28}" y="152" class="label">{escape_xml(line_label)}</text>')

    for panel_index, (field, benchmark_label, scope_label) in enumerate(metric_specs):
        panel_y = panel_top + panel_index * panel_gap
        lines.append(f'<rect x="42" y="{panel_y - 28}" width="{width - 84}" height="212" rx="18" class="subpanel"/>')
        lines.append(f'<text x="48" y="{panel_y}" class="axis">{escape_xml(benchmark_label)}</text>')
        lines.append(f'<text x="48" y="{panel_y + 20}" class="subtitle">{escape_xml(scope_label)}</text>')
        lines.append(f'<text x="{panel_left + panel_width}" y="{panel_y}" text-anchor="end" class="small">Accuracy</text>')

        tick_y = panel_y + 34
        for tick_index in range(tick_count):
            ratio = tick_index / (tick_count - 1)
            x = panel_left + ratio * panel_width
            lines.append(f'<line x1="{x:.2f}" y1="{tick_y}" x2="{x:.2f}" y2="{tick_y + 182}" class="guide"/>')
            lines.append(f'<text x="{x:.2f}" y="{tick_y - 8}" text-anchor="middle" class="small">{ratio * 100:.0f}%</text>')

        row_lookup = {row["line_label"]: row for row in rows}
        for row_index, line_label in enumerate(COMPARABLE_RESULT_ORDER):
            y = panel_y + 46 + row_index * (bar_height + bar_gap)
            row = row_lookup.get(line_label)
            value = None if row is None else row[field]
            lines.append(f'<text x="{panel_left - 16}" y="{y + 19}" text-anchor="end" class="label">{escape_xml(line_label)}</text>')
            lines.append(f'<rect x="{panel_left}" y="{y}" width="{panel_width}" height="{bar_height}" rx="10" fill="#e2e8f0"/>')
            if value is None:
                lines.append(f'<rect x="{panel_left}" y="{y}" width="{panel_width}" height="{bar_height}" rx="10" class="muted-bar"/>')
                lines.append(
                    f'<rect x="{panel_left}" y="{y}" width="{panel_width}" height="{bar_height}" rx="10" fill="url(#diagonalHatch)" opacity="0.7"/>'
                )
                lines.append(
                    f'<text x="{panel_left + panel_width - 10}" y="{y + 19}" text-anchor="end" class="small">not run for this benchmark</text>'
                )
                continue
            width_px = panel_width * value
            lines.append(
                f'<rect x="{panel_left}" y="{y}" width="{width_px:.2f}" height="{bar_height}" rx="10" fill="{line_colors.get(line_label, "#475569")}"/>'
            )
            label_x = min(panel_left + width_px + 10, panel_left + panel_width - 4)
            label_anchor = "start" if label_x < panel_left + panel_width - 4 else "end"
            lines.append(f'<text x="{label_x:.2f}" y="{y + 19}" text-anchor="{label_anchor}" class="label">{value * 100:.1f}%</text>')

    lines.append("</svg>")
    write_text(output_path, "\n".join(lines) + "\n")


def build_topline_summary(
    rows: list[dict[str, Any]],
    model_summary: list[dict[str, Any]],
    supplementary_model_progress: list[dict[str, Any]],
) -> str:
    total_samples = sum(row["total_samples"] for row in rows)
    faithful_tasks = sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows)
    proxy_tasks = sum(row["benchmark_mode"] == "proxy" for row in rows)
    llama_progress = next(row for row in supplementary_model_progress if row["family"] == "Llama")
    lines = [
        "# 2026-04-19 Option 1 Release Summary",
        "",
        f"- tasks in frozen snapshot: `{len(rows)}`",
        f"- paper-setup tasks: `{faithful_tasks}`",
        f"- proxy tasks: `{proxy_tasks}`",
        f"- total evaluated samples: `{total_samples:,}`",
        f"- current cost to date: `{REPORT_CURRENT_COST}`",
        "- closed model families in this release: `Qwen`, `DeepSeek`, `Gemma`",
        "- key methodological caveat: `Denevil` uses a clearly labeled local proxy dataset rather than the paper's original `MoralPrompt` setup",
        f"- extra local progress outside the frozen snapshot: `Llama` small is complete across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks and is intentionally excluded from the frozen `19 / 19` totals",
        "",
        "## Model Summary",
        "",
        "| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in model_summary:
        lines.append(
            f"| `{row['model_family']}` | {row['faithful_tasks']} | {row['proxy_tasks']} | {row['samples']:,} | {fmt_float(row['faithful_macro_accuracy']) or 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "Macro accuracy is computed over paper-setup tasks with a directly comparable accuracy metric. `CCD-Bench` and `Denevil` are excluded from that average.",
        ]
    )
    return "\n".join(lines) + "\n"


def append_family_size_progress_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| Line | UniMoral | SMID | Value Kaleidoscope | CCD-Bench | Denevil | Note |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['line_label']}` | {STATUS_DISPLAY[row['unimoral']]} | {STATUS_DISPLAY[row['smid']]} | "
            f"{STATUS_DISPLAY[row['value_kaleidoscope']]} | {STATUS_DISPLAY[row['ccd_bench']]} | "
            f"{STATUS_DISPLAY[row['denevil']]} | {row['summary_note']} |"
        )


def append_benchmark_comparison_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| Line | UniMoral action | SMID average | Value Kaleidoscope average | Coverage note |",
            "| :--- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['line_label']}` | {fmt_float(row['unimoral_action_accuracy']) or 'n/a'} | "
            f"{fmt_float(row['smid_average_accuracy']) or 'n/a'} | {fmt_float(row['value_average_accuracy']) or 'n/a'} | "
            f"{row['coverage_note']} |"
        )


def append_current_result_lines_table(lines: list[str]) -> None:
    lines.extend(
        [
            "| Line | Scope | Status | Coverage | Note |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in CURRENT_RESULT_LINES:
        lines.append(
            f"| `{row['line_label']}` | {row['scope']} | {STATUS_DISPLAY[row['status']]} | {row['coverage']} | {row['note']} |"
        )


def append_status_key(lines: list[str]) -> None:
    lines.extend(
        [
            "| Mark | Meaning |",
            "| --- | --- |",
        ]
    )
    for label, meaning in STATUS_LEGEND:
        lines.append(f"| `{label}` | {meaning} |")


def append_benchmark_catalog_table(lines: list[str], rows: list[dict[str, Any]], include_citation_column: bool) -> None:
    if include_citation_column:
        lines.extend(
            [
                "| Benchmark | Citation | Paper link | Dataset / access link | Modality | What this repo tests now |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
    else:
        lines.extend(
            [
                "| Benchmark | Paper | Dataset / access | Modality | What this repo tests now |",
                "| --- | --- | --- | --- | --- |",
            ]
        )

    for row in rows:
        dataset_cell = row["dataset_label"]
        if row["dataset_url"]:
            dataset_cell = markdown_link(row["dataset_label"], row["dataset_url"])
        if row["dataset_alt_url"]:
            dataset_cell = f"{dataset_cell}; {markdown_link('JSON', row['dataset_alt_url'])}"

        if include_citation_column:
            lines.append(
                f"| `{row['benchmark']}` | {row['citation']} | {markdown_link('paper', row['paper_url'])} | {dataset_cell} | {row['modality']} | {row['current_release_scope']} |"
            )
        else:
            lines.append(
                f"| `{row['benchmark']}` | {markdown_link(row['citation'], row['paper_url'])} | {dataset_cell} | {row['modality']} | {row['current_release_scope']} |"
            )


def append_family_route_summary_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| Family | Small route | Medium route | Large route |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(f"| `{row['family']}` | `{row['small_route']}` | `{row['medium_route']}` | `{row['large_route']}` |")


def format_family_size_route(row: dict[str, Any]) -> str:
    text_route = row["text_route"]
    vision_route = row["vision_route"]
    if vision_route in {"", "-", "TBD"}:
        return text_route
    if vision_route == text_route:
        return text_route
    return f"text: {text_route}; vision: {vision_route}"


def append_figure_gallery(lines: list[str], figure_prefix: str) -> None:
    lines.extend(
        [
            "## Supporting Figures",
            "",
            "| Figure | Why it matters | File |",
            "| --- | --- | --- |",
            f"| Figure 1 | Cross-model comparison for the benchmarks that share a directly comparable accuracy metric. | {markdown_link('option1_benchmark_accuracy_bars.svg', f'{figure_prefix}/option1_benchmark_accuracy_bars.svg')} |",
            f"| Figure 2 | Task-level heatmap for the frozen comparable metrics, including unavailable-task treatment. | {markdown_link('option1_accuracy_heatmap.svg', f'{figure_prefix}/option1_accuracy_heatmap.svg')} |",
            f"| Figure 3 | Coverage view of which benchmark lines are paper-setup, proxy-only, or not in the frozen release. | {markdown_link('option1_coverage_matrix.svg', f'{figure_prefix}/option1_coverage_matrix.svg')} |",
            f"| Figure 4 | Sample concentration by benchmark with paper-setup versus proxy volume separated. | {markdown_link('option1_sample_volume.svg', f'{figure_prefix}/option1_sample_volume.svg')} |",
            "",
            f"![Accuracy heatmap]({figure_prefix}/option1_accuracy_heatmap.svg)",
            "",
            "_Figure 2. Task-level accuracy heatmap for the frozen Option 1 slice, using a shared scale and a consistent unavailable-state treatment._",
            "",
            f"![Coverage matrix]({figure_prefix}/option1_coverage_matrix.svg)",
            "",
            "_Figure 3. Coverage matrix showing which benchmark lines are paper-setup, proxy-only, or absent from the frozen release._",
            "",
            f"![Sample volume by benchmark]({figure_prefix}/option1_sample_volume.svg)",
            "",
            "_Figure 4. Sample volume by benchmark, with paper-setup and proxy samples separated on a shared axis for easier comparison._",
            "",
        ]
    )


def build_family_route_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for family in FULL_MODEL_FAMILY_ORDER:
        family_rows = {row["size_slot"]: row for row in rows if row["family"] == family}
        summary.append(
            {
                "family": family,
                "small_route": format_family_size_route(family_rows["S"]),
                "medium_route": format_family_size_route(family_rows["M"]),
                "large_route": format_family_size_route(family_rows["L"]),
            }
        )
    return summary


def build_repo_readme(
    model_summary: list[dict[str, Any]],
    benchmark_catalog: list[dict[str, Any]],
    supplementary_model_progress: list[dict[str, Any]],
    family_size_progress: list[dict[str, Any]],
    benchmark_comparison: list[dict[str, Any]],
) -> str:
    llama_progress = next(row for row in supplementary_model_progress if row["family"] == "Llama")
    route_summary = build_family_route_summary(family_size_progress)
    lines = [
        "# CEI Moral-Psych Benchmark Suite",
        "",
        f"[![CI]({CI_WORKFLOW_URL}/badge.svg?branch=main)]({CI_WORKFLOW_URL})",
        "",
        "This repo is Jenny Zhu's CEI moral-psych benchmark deliverable for five assigned benchmark papers.",
        "",
        f"> Current cost to date: `{REPORT_CURRENT_COST}`",
        "",
        "It combines three things in one clean public surface:",
        "",
        "1. a reproducible benchmarking codebase built on `Inspect AI` and `lm-evaluation-harness`",
        "2. a frozen `Option 1` snapshot for the first formal public release",
        "3. a clearly labeled progress matrix for the larger `5 benchmarks x 5 model families x 3 size slots` plan",
        "",
        "## Results First",
        "",
        "This is the fastest way to understand the deliverable: which lines already have usable results, what is directly comparable now, and which family-size expansions are complete versus partial.",
        "",
    ]
    append_current_result_lines_table(lines)
    lines.extend(
        [
            "",
            "### Current Comparable Accuracy Snapshot",
            "",
            "Only benchmarks with directly comparable accuracy metrics are shown below. `CCD-Bench` and `Denevil` are intentionally excluded because they do not share the same target metric across lines.",
            "",
        ]
    )
    append_benchmark_comparison_table(lines, benchmark_comparison)
    lines.extend(
        [
            "",
            "![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)",
            "",
            "_Figure 1. Benchmark-level accuracy comparison across the currently completed comparable lines, with unavailable benchmark-line pairs shown explicitly._",
            "",
            "## Snapshot",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Report owner | `{REPORT_OWNER}` |",
            f"| Repo update date | `{REPORT_DATE_LONG}` |",
            f"| Frozen public snapshot | `Option 1`, `{SNAPSHOT_DATE_LONG}` |",
            f"| Current cost to date | `{REPORT_CURRENT_COST}` |",
            "| Intended use | Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan. |",
            "| Group plan target | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |",
            "| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |",
            "| Model families in scope | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |",
            "| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |",
            f"| Extra completed local line | `Llama-S`, complete locally across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks |",
            "| MiniMax small status | formal attempt exists, but the current line failed and is not counted as complete |",
            "| Run setting | `OpenRouter`, `temperature=0` |",
            f"| Current operations note | {REPORT_STATUS_NOTE} |",
            "",
            "## Start Here",
            "",
            "### Reports",
            "",
            "- [Jenny's group report](results/release/2026-04-19-option1/jenny-group-report.md)",
            "- [Release appendix](results/release/2026-04-19-option1/README.md)",
            "- [Frozen source snapshot](results/release/2026-04-19-option1/source/authoritative-summary.csv)",
            "- [How to read the results](docs/how-to-read-results.md)",
            "- [Reproducibility guide](docs/reproducibility.md)",
            "",
            "### Figures",
            "",
            "- [Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)",
            "- [Accuracy heatmap](figures/release/option1_accuracy_heatmap.svg)",
            "- [Coverage matrix](figures/release/option1_coverage_matrix.svg)",
            "- [Sample volume chart](figures/release/option1_sample_volume.svg)",
            "",
            "## Local Expansion Checkpoint",
            "",
            "This checkpoint summarizes the broader family-size expansion separately from the frozen Option 1 counts. It is a curated snapshot rather than a live dashboard.",
            "",
        ]
    )
    append_local_expansion_checkpoint_table(lines)
    lines.extend(
        [
            "",
            "## Status Key",
            "",
        ]
    )
    append_status_key(lines)
    lines.extend(
        [
            "",
            "## Family-Size Progress Matrix",
            "",
            "This is the main repo-level status table for the full group plan.",
            "",
        ]
    )
    append_family_size_progress_table(lines, family_size_progress)
    lines.extend(
        [
            "",
            "The same matrix is also saved as [family-size-progress.csv](results/release/2026-04-19-option1/family-size-progress.csv).",
            "",
            "## The Five Benchmark Papers",
            "",
        ]
    )
    append_benchmark_catalog_table(lines, benchmark_catalog, include_citation_column=False)
    lines.extend(
        [
            "",
            "## Model Families And Size Routes",
            "",
        ]
    )
    append_family_route_summary_table(lines, route_summary)
    lines.extend(
        [
            "",
        ]
    )
    append_figure_gallery(lines, "figures/release")
    lines.extend(
        [
            "## Reproducibility",
            "",
            "### 1. Setup",
            "",
            "```bash",
            "make setup",
            "cp .env.example .env",
            "```",
            "",
            "Populate `.env` with API keys such as `OPENROUTER_API_KEY` and local benchmark paths such as `UNIMORAL_DATA_DIR` and `SMID_DATA_DIR`.",
            "If `uv` is not on `PATH` but the repo `.venv` already exists, `make test`, `make release`, and `make audit` now fall back to `.venv/bin/python` automatically. `make setup` still requires `uv`. If neither runner is available, those targets fail early with a clear setup error; you can also override the fallback path with `VENV_PYTHON=/absolute/path/to/python`.",
            "",
            "### 2. Verify the repo",
            "",
            "```bash",
            "make test",
            "```",
            "",
            "### 3. Rebuild the public package",
            "",
            "```bash",
            "make release",
            "```",
            "",
            "This regenerates the tracked release package from the frozen source snapshot under `results/release/2026-04-19-option1/source/`.",
            "",
            "Expected high-level outputs:",
            "",
            "- `results/release/2026-04-19-option1/jenny-group-report.md`",
            "- `results/release/2026-04-19-option1/family-size-progress.csv`",
            "- `results/release/2026-04-19-option1/benchmark-comparison.csv`",
            "- `results/release/2026-04-19-option1/release-manifest.json`",
            "- `figures/release/option1_benchmark_accuracy_bars.svg`",
            "- `figures/release/option1_coverage_matrix.svg`",
            "",
            "For the full reproduction notes, see [docs/reproducibility.md](docs/reproducibility.md).",
            "",
            "## Important Notes",
            "",
            "- The full `5 x 5 x 3` matrix is the target plan, not a claim that all 75 cells are already complete.",
            "- `Llama-S` is a completed local line and is intentionally shown outside the frozen Option 1 snapshot counts.",
            "- `MiniMax-S` should currently be reported as a failed formal attempt, not as a completed comparison point.",
            "- `Denevil` is still proxy-only in the public release because the original paper-faithful `MoralPrompt` export is not available locally.",
            "- The detailed appendix lives in [results/release/2026-04-19-option1/](results/release/2026-04-19-option1/).",
        ]
    )
    return "\n".join(lines) + "\n"


def build_release_readme(
    model_summary: list[dict[str, Any]],
    benchmark_summary: list[dict[str, Any]],
    benchmark_catalog: list[dict[str, Any]],
    model_roster: list[dict[str, Any]],
    supplementary_model_progress: list[dict[str, Any]],
    family_size_progress: list[dict[str, Any]],
    benchmark_comparison: list[dict[str, Any]],
) -> str:
    llama_progress = next(row for row in supplementary_model_progress if row["family"] == "Llama")
    lines = [
        "# Option 1 Release Artifacts",
        "",
        "This directory contains the tracked, publication-facing outputs for Jenny Zhu's CEI moral-psych deliverable.",
        "",
        "It separates two things clearly:",
        "",
        "1. the frozen `Option 1` public snapshot from `April 19, 2026`, and",
        "2. the wider `5 benchmarks x 5 model families x 3 size slots` progress matrix that is still being filled in.",
        "",
        "## Results First",
        "",
        "This is the fastest way to read the deliverable: which lines already have usable results, what is directly comparable now, and where the current release snapshot stops.",
        "",
    ]
    append_current_result_lines_table(lines)
    lines.extend(
        [
            "",
            "### Current Comparable Accuracy Snapshot",
            "",
            "Only benchmarks with directly comparable accuracy metrics are shown here. `CCD-Bench` and `Denevil` are excluded because they do not share the same target metric across lines.",
            "",
        ]
    )
    append_benchmark_comparison_table(lines, benchmark_comparison)
    lines.extend(
        [
            "",
            "![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)",
            "",
            "_Figure 1. Benchmark-level accuracy comparison across the currently completed comparable lines, with unavailable benchmark-line pairs shown explicitly._",
            "",
            "## Snapshot",
            "",
        ]
    )
    lines.extend(
        [
            "| Field | Value |",
            "| --- | --- |",
            f"| Report owner | `{REPORT_OWNER}` |",
            f"| Repo update date | `{REPORT_DATE_LONG}` |",
            f"| Frozen public snapshot | `Option 1`, `{SNAPSHOT_DATE_LONG}` |",
            f"| Current cost to date | `{REPORT_CURRENT_COST}` |",
            f"| Intended use | {REPORT_PURPOSE} |",
            "| Agreed target matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |",
            "| Benchmarks in scope | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |",
            "| Agreed model families | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |",
            "| Frozen families already in Option 1 | `Qwen`, `DeepSeek`, `Gemma` |",
            f"| Extra completed local line outside release | `Llama` small via `llama-3.2-11b-vision-instruct`, complete across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks |",
            "| MiniMax small status | formal attempt exists, but the current run failed and is not counted as complete |",
            "| Provider / temperature | `OpenRouter`, `temperature=0` |",
            f"| Current operations note | {REPORT_STATUS_NOTE} |",
            f"| CI reference | {markdown_link('Workflow', CI_WORKFLOW_URL)}; last verified successful run: {markdown_link('run 24634450927', CI_RUN_URL)} |",
            "",
            "## Local Expansion Checkpoint",
            "",
            "This checkpoint summarizes the broader family-size expansion separately from the frozen Option 1 counts. It is a curated snapshot rather than a live dashboard.",
            "",
        ]
    )
    append_local_expansion_checkpoint_table(lines)
    lines.extend(
        [
            "",
            "## Start Here",
            "",
            "### Reports",
            "",
            "- `jenny-group-report.md`: mentor-facing report with the benchmark list, progress matrix, model roster, and current results",
            "- `topline-summary.md`: shortest narrative summary of the frozen Option 1 snapshot",
            "- `release-manifest.json`: machine-readable release index",
            f"- {markdown_link('how to read the results', '../../../docs/how-to-read-results.md')}: plain-language explanation of the report terms",
            "",
            "### Figures",
            "",
            f"- {markdown_link('grouped bar chart', '../../../figures/release/option1_benchmark_accuracy_bars.svg')}: current cross-model benchmark comparison",
            f"- {markdown_link('accuracy heatmap', '../../../figures/release/option1_accuracy_heatmap.svg')}: task-level view of comparable metrics",
            f"- {markdown_link('coverage matrix', '../../../figures/release/option1_coverage_matrix.svg')}: frozen Option 1 coverage only",
            f"- {markdown_link('sample volume chart', '../../../figures/release/option1_sample_volume.svg')}: where the evaluated samples are concentrated",
            "",
            "## Status Key",
            "",
        ]
    )
    append_status_key(lines)
    lines.extend(
        [
            "",
            "## Family-Size Progress Matrix",
            "",
            "This is the cleanest repo-level summary of where the full `5 x 5 x 3` plan stands today.",
            "",
        ]
    )
    append_family_size_progress_table(lines, family_size_progress)
    lines.extend(
        [
            "",
            "## Benchmark List",
            "",
        ]
    )
    append_benchmark_catalog_table(lines, benchmark_catalog, include_citation_column=False)
    lines.extend(
        [
            "",
        ]
    )
    append_figure_gallery(lines, "../../../figures/release")
    lines.extend(
        [
            "## Frozen Option 1 Model Summary",
            "",
            "| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |",
            "| :--- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in model_summary:
        lines.append(
            f"| `{row['model_family']}` | {row['faithful_tasks']} | {row['proxy_tasks']} | {row['samples']:,} | {fmt_float(row['faithful_macro_accuracy']) or 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            "- `source/authoritative-summary.csv`: tracked frozen source snapshot for the April 19 release",
            "- `jenny-group-report.md`: mentor-ready markdown report",
            "- `topline-summary.md`: concise release narrative",
            "- `release-manifest.json`: machine-readable index of counts, files, and caveats",
            "- `family-size-progress.csv`: 15-line matrix for the full five-family by three-size plan",
            "- `benchmark-comparison.csv`: current comparable accuracy table used for the grouped bar figure",
            "- `benchmark-catalog.csv`: benchmark registry with paper and dataset links",
            "- `model-roster.csv`: exact OpenRouter routes in the frozen Option 1 snapshot",
            "- `supplementary-model-progress.csv`: extra local lines outside the frozen snapshot counts",
            "",
            "## Regeneration",
            "",
            "From the repo root:",
            "",
            "```bash",
            "make release",
            "make audit",
            "```",
            "",
            "`make release` rebuilds this public package from the tracked source snapshot. `make audit` runs the public QA gate and rebuilds the package together.",
            "",
            "## Interpretation Notes",
            "",
            "- The full `5 x 5 x 3` plan is the target matrix, not a claim of completed coverage.",
            "- The frozen `Option 1` snapshot still only includes `Qwen`, `DeepSeek`, and `Gemma`.",
            "- `Llama-S` is complete locally and is shown in comparison tables, but it remains outside the frozen snapshot counts.",
            "- `MiniMax-S` has a formal attempt on disk, but it is still an error line rather than a finished comparison point.",
            "- `Denevil` is still proxy-only in the current public release because the paper-faithful `MoralPrompt` export is not available locally.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_jenny_group_report(
    rows: list[dict[str, Any]],
    model_summary: list[dict[str, Any]],
    benchmark_catalog: list[dict[str, Any]],
    supplementary_model_progress: list[dict[str, Any]],
    family_size_progress: list[dict[str, Any]],
    benchmark_comparison: list[dict[str, Any]],
) -> str:
    total_samples = sum(row["total_samples"] for row in rows)
    llama_progress = next(row for row in supplementary_model_progress if row["family"] == "Llama")
    route_summary = build_family_route_summary(family_size_progress)
    lines = [
        "# Jenny Zhu Moral-Psych Benchmark Report",
        "",
        f"Updated: `{REPORT_DATE_LONG}`",
        "",
        f"Frozen public snapshot referenced here: `Option 1`, `{SNAPSHOT_DATE_LONG}`",
        "",
        "This report covers Jenny Zhu's five assigned moral-psych benchmark papers under the April 14, 2026 group plan. It separates the frozen public snapshot from the broader family-size expansion work that is still being filled in.",
        "",
        "## Results First",
        "",
        "This section is the fastest summary for a mentor or collaborator: which lines already have usable results, what is directly comparable now, and which local expansions are complete versus partial.",
        "",
    ]
    append_current_result_lines_table(lines)
    lines.extend(
        [
            "",
            "### Current Comparable Accuracy Snapshot",
            "",
            "Only benchmarks with a directly comparable accuracy metric are shown below. `CCD-Bench` and `Denevil` are excluded because they do not share the same accuracy target across lines.",
            "",
        ]
    )
    append_benchmark_comparison_table(lines, benchmark_comparison)
    lines.extend(
        [
            "",
            "![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)",
            "",
            "_Figure 1. Benchmark-level accuracy comparison across the currently completed comparable lines, with unavailable benchmark-line pairs shown explicitly._",
            "",
            "## Report Snapshot",
            "",
        ]
    )
    lines.extend(
        [
            "| Field | Value |",
            "| --- | --- |",
            f"| Report owner | `{REPORT_OWNER}` |",
            f"| Repo update date | `{REPORT_DATE_LONG}` |",
            f"| Frozen public snapshot | `Option 1`, `{SNAPSHOT_DATE_LONG}` |",
            f"| Current cost to date | `{REPORT_CURRENT_COST}` |",
            f"| Purpose | {REPORT_PURPOSE} |",
            "| Full target matrix | `5 benchmarks x 5 model families x 3 size slots = 75 family-size-benchmark cells` |",
            "| Benchmarks being tracked | `UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil` |",
            "| Agreed model families | `Qwen`, `MiniMax`, `DeepSeek`, `Llama`, `Gemma` |",
            "| What the frozen snapshot actually covers | one closed `Option 1` slice across `Qwen`, `DeepSeek`, and `Gemma` |",
            f"| Extra completed local line outside release | `Llama` small complete via `llama-3.2-11b-vision-instruct` across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks |",
            "| MiniMax small status | formal attempt exists, but the current line failed and is not counted as complete |",
            "| Run provider / temperature | `OpenRouter`, `temperature=0` |",
            f"| Current operations note | {REPORT_STATUS_NOTE} |",
            f"| CI status reference | {markdown_link('CI workflow', CI_WORKFLOW_URL)}; latest verified passing run: {markdown_link('24634450927', CI_RUN_URL)} |",
            f"| Total evaluated samples in this release | `{total_samples:,}` |",
            "",
            "## Local Expansion Checkpoint",
            "",
            "This checkpoint summarizes the broader family-size expansion separately from the frozen Option 1 counts. It is a curated snapshot rather than a live dashboard.",
            "",
        ]
    )
    append_local_expansion_checkpoint_table(lines)
    lines.extend(
        [
            "",
            "Plain-language terms: [`docs/how-to-read-results.md`](../../../docs/how-to-read-results.md)",
            "",
            "## Status Key",
            "",
        ]
    )
    append_status_key(lines)
    lines.extend(
        [
            "",
            "## The Five Papers / Benchmarks Under Test",
            "",
        ]
    )
    append_benchmark_catalog_table(lines, benchmark_catalog, include_citation_column=True)
    lines.extend(
        [
            "",
            "## Model Families And Size Routes",
            "",
        ]
    )
    append_family_route_summary_table(lines, route_summary)
    lines.extend(
        [
            "",
            "## Full Family-Size Progress Matrix",
            "",
        ]
    )
    append_family_size_progress_table(lines, family_size_progress)
    lines.extend(
        [
            "",
        ]
    )
    append_figure_gallery(lines, "../../../figures/release")
    lines.extend(
        [
            "## Frozen Option 1 Summary",
            "",
            "| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |",
            "| :--- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in model_summary:
        lines.append(
            f"| `{row['model_family']}` | {row['faithful_tasks']} | {row['proxy_tasks']} | {row['samples']:,} | {fmt_float(row['faithful_macro_accuracy']) or 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- The `5 x 5 x 3` matrix is the target plan, not a claim that all 75 cells are already complete.",
            "- `Llama-S` is complete locally and should be reported as an extra completed local line outside the frozen Option 1 counts.",
            "- `MiniMax-S` should currently be reported as a failed formal attempt, not as a completed benchmark line.",
            "- `DeepSeek` does not yet have a frozen SMID vision route in this deliverable.",
            "- `Denevil` is still proxy-only in the public release because the original paper-faithful `MoralPrompt` export is not available locally.",
            "",
            "## Safe One-Sentence Framing",
            "",
            "> This repository contains Jenny Zhu's CEI moral-psych benchmark deliverable for five target papers, with a frozen Option 1 snapshot over Qwen, DeepSeek, and Gemma, an extra completed Llama small line outside the frozen counts, and a clearly labeled family-size progress matrix for the broader five-family plan.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_source_readme() -> str:
    return "\n".join(
        [
            "# Release Source Snapshot",
            "",
            "The public `Option 1` deliverable is regenerated from `authoritative-summary.csv` in this directory.",
            "",
            "From the repo root, the standard rebuild path is:",
            "",
            "```bash",
            "make release",
            "```",
            "",
            "- This CSV is intentionally tracked in git so `make release` does not depend on the large local `results/inspect/` tree.",
            "- Maintainers with the original raw full-run folders can refresh this snapshot with `make refresh-authoritative`.",
            "- The raw `results/inspect/` directories remain useful for local provenance and debugging, but they are not required for public release regeneration.",
        ]
    ) + "\n"


def build_release_manifest(
    rows: list[dict[str, Any]],
    model_summary: list[dict[str, Any]],
    benchmark_summary: list[dict[str, Any]],
    supplementary_model_progress: list[dict[str, Any]],
    family_size_progress: list[dict[str, Any]],
    benchmark_comparison: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "release_id": RELEASE_ID,
        "title": RELEASE_TITLE,
        "source_snapshot": "results/release/2026-04-19-option1/source/authoritative-summary.csv",
        "report_metadata": {
            "owner": REPORT_OWNER,
            "date": REPORT_DATE_ISO,
            "frozen_snapshot_date": SNAPSHOT_DATE_ISO,
            "current_cost": REPORT_CURRENT_COST,
            "purpose": REPORT_PURPOSE,
            "provider": REPORT_PROVIDER,
            "temperature": REPORT_TEMPERATURE,
            "operations_note": REPORT_STATUS_NOTE,
            "ci_workflow_url": CI_WORKFLOW_URL,
            "ci_last_verified_run_url": CI_RUN_URL,
        },
        "target_matrix": {
            "benchmarks": len(BENCHMARK_ORDER),
            "model_families": len(FULL_MODEL_FAMILY_ORDER),
            "size_slots": 3,
            "family_size_benchmark_cells": len(BENCHMARK_ORDER) * len(FULL_MODEL_FAMILY_ORDER) * 3,
        },
        "counts": {
            "authoritative_tasks": len(rows),
            "benchmark_faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows),
            "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in rows),
            "total_samples": sum(row["total_samples"] for row in rows),
        },
        "model_families": MODEL_ORDER,
        "benchmarks": benchmark_summary,
        "model_summary": [
            {
                **serialize_model_summary_row(row),
                "benchmark_faithful_macro_accuracy": None if row["faithful_macro_accuracy"] is None else round(row["faithful_macro_accuracy"], 6),
            }
            for row in model_summary
        ],
        "supplementary_model_progress": [
            {
                **serialize_supplementary_progress_row(row),
                "benchmark_faithful_macro_accuracy": None
                if row["benchmark_faithful_macro_accuracy"] is None
                else round(row["benchmark_faithful_macro_accuracy"], 6),
            }
            for row in supplementary_model_progress
        ],
        "entry_points": {
            "report": "results/release/2026-04-19-option1/jenny-group-report.md",
            "topline_summary": "results/release/2026-04-19-option1/topline-summary.md",
            "manifest": "results/release/2026-04-19-option1/release-manifest.json",
            "benchmark_catalog": "results/release/2026-04-19-option1/benchmark-catalog.csv",
            "supplementary_progress": "results/release/2026-04-19-option1/supplementary-model-progress.csv",
            "family_size_progress": "results/release/2026-04-19-option1/family-size-progress.csv",
            "benchmark_comparison": "results/release/2026-04-19-option1/benchmark-comparison.csv",
            "coverage_figure": "figures/release/option1_coverage_matrix.svg",
            "accuracy_figure": "figures/release/option1_accuracy_heatmap.svg",
            "benchmark_bar_figure": "figures/release/option1_benchmark_accuracy_bars.svg",
            "sample_volume_figure": "figures/release/option1_sample_volume.svg",
        },
        "tables": [
            "README.md",
            "jenny-group-report.md",
            "topline-summary.md",
            "topline-summary.json",
            "release-manifest.json",
            "benchmark-catalog.csv",
            "model-summary.csv",
            "model-roster.csv",
            "supplementary-model-progress.csv",
            "family-size-progress.csv",
            "benchmark-comparison.csv",
            "future-model-plan.csv",
            "benchmark-summary.csv",
            "faithful-metrics.csv",
            "coverage-matrix.csv",
        ],
        "figures": [
            "figures/release/option1_coverage_matrix.svg",
            "figures/release/option1_accuracy_heatmap.svg",
            "figures/release/option1_benchmark_accuracy_bars.svg",
            "figures/release/option1_sample_volume.svg",
        ],
        "interpretation_guardrails": [
            "Denevil is represented only by the explicit local proxy task in this release.",
            "DeepSeek has no SMID entries in the closed release slice because no vision route was included.",
            "The completed local Llama small line sits outside the frozen Option 1 totals.",
            "The MiniMax small line has a formal attempt on disk, but the current run failed and is not yet a usable comparison point.",
            "Raw results/inspect artifacts are local provenance inputs, not required public dependencies for release regeneration.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release tables and figures from the authoritative Option 1 summary.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to authoritative-summary.csv")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output directory for release tables")
    parser.add_argument("--figure-dir", type=Path, default=DEFAULT_FIGURE_DIR, help="Output directory for SVG figures")
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Missing authoritative summary at {args.input}. "
            "Restore the tracked release source snapshot or run `make refresh-authoritative` if local raw full-run tables are available."
        )

    rows = read_rows(args.input)
    args.release_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)

    model_summary = build_model_summary(rows)
    benchmark_summary = build_benchmark_summary(rows)
    benchmark_catalog = build_benchmark_catalog(rows)
    model_roster = build_model_roster(rows)
    future_model_plan = build_future_model_plan()
    supplementary_model_progress = build_supplementary_model_progress()
    family_size_progress = build_family_size_progress()
    benchmark_comparison = build_benchmark_comparison(rows)
    faithful_metrics = build_faithful_metrics(rows)
    coverage_matrix = build_coverage_matrix(rows)

    write_csv(
        args.release_dir / "model-summary.csv",
        [
            {
                **serialize_model_summary_row(row),
                "benchmark_faithful_macro_accuracy": fmt_float(row["faithful_macro_accuracy"], 6),
            }
            for row in model_summary
        ],
        ["model_family", "tasks", "benchmark_faithful_tasks", "proxy_tasks", "samples", "scored_tasks", "benchmark_faithful_macro_accuracy"],
    )
    write_csv(
        args.release_dir / "benchmark-summary.csv",
        benchmark_summary,
        ["benchmark", "task_types", "evaluated_lines", "models_covered", "samples", "modes"],
    )
    write_csv(
        args.release_dir / "benchmark-catalog.csv",
        benchmark_catalog,
        [
            "benchmark",
            "citation",
            "paper_title",
            "paper_url",
            "dataset_label",
            "dataset_url",
            "dataset_alt_url",
            "modality",
            "repo_tasks",
            "current_release_scope",
            "current_release_mode",
            "models_in_release",
            "samples_in_release",
            "dataset_note",
        ],
    )
    write_csv(
        args.release_dir / "model-roster.csv",
        model_roster,
        ["model_family", "model", "size_hint", "modality", "benchmarks", "tasks", "release_modes", "samples", "note"],
    )
    write_csv(
        args.release_dir / "supplementary-model-progress.csv",
        [
            {
                **serialize_supplementary_progress_row(row),
                "benchmark_faithful_macro_accuracy": fmt_float(row["benchmark_faithful_macro_accuracy"], 6),
            }
            for row in supplementary_model_progress
        ],
        [
            "family",
            "status_relative_to_closed_release",
            "exact_route",
            "completed_benchmark_lines",
            "missing_benchmark_lines",
            "papers_covered",
            "tasks_completed",
            "benchmark_faithful_tasks",
            "proxy_tasks",
            "samples",
            "benchmark_faithful_macro_accuracy",
            "note",
        ],
    )
    write_csv(
        args.release_dir / "future-model-plan.csv",
        future_model_plan,
        ["family", "closed_release_status", "current_route", "small_candidate", "medium_candidate", "large_candidate", "next_step"],
    )
    write_csv(
        args.release_dir / "family-size-progress.csv",
        family_size_progress,
        [
            "family",
            "size_slot",
            "line_label",
            "text_route",
            "vision_route",
            "unimoral",
            "smid",
            "value_kaleidoscope",
            "ccd_bench",
            "denevil",
            "summary_note",
        ],
    )
    write_csv(
        args.release_dir / "benchmark-comparison.csv",
        [
            {
                **row,
                "unimoral_action_accuracy": fmt_float(row["unimoral_action_accuracy"], 6),
                "smid_average_accuracy": fmt_float(row["smid_average_accuracy"], 6),
                "value_average_accuracy": fmt_float(row["value_average_accuracy"], 6),
            }
            for row in benchmark_comparison
        ],
        [
            "line_label",
            "family",
            "size_slot",
            "route",
            "unimoral_action_accuracy",
            "smid_average_accuracy",
            "value_average_accuracy",
            "coverage_note",
        ],
    )
    write_csv(
        args.release_dir / "faithful-metrics.csv",
        faithful_metrics,
        ["benchmark", "benchmark_scope", "model_family", "task", "model", "accuracy", "stderr", "samples", "status"],
    )
    write_csv(
        args.release_dir / "coverage-matrix.csv",
        coverage_matrix,
        ["model_family", "benchmark", "status", "completed_tasks", "expected_tasks", "label"],
    )

    topline_md = build_topline_summary(rows, model_summary, supplementary_model_progress)
    write_text(args.release_dir / "topline-summary.md", topline_md)
    write_text(
        args.release_dir / "README.md",
        build_release_readme(
            model_summary,
            benchmark_summary,
            benchmark_catalog,
            model_roster,
            supplementary_model_progress,
            family_size_progress,
            benchmark_comparison,
        ),
    )
    if args.release_dir.resolve() == DEFAULT_RELEASE_DIR.resolve() and args.figure_dir.resolve() == DEFAULT_FIGURE_DIR.resolve():
        write_text(
            ROOT / "README.md",
            build_repo_readme(
                model_summary,
                benchmark_catalog,
                supplementary_model_progress,
                family_size_progress,
                benchmark_comparison,
            ),
        )
    write_text(
        args.release_dir / "jenny-group-report.md",
        build_jenny_group_report(
            rows,
            model_summary,
            benchmark_catalog,
            supplementary_model_progress,
            family_size_progress,
            benchmark_comparison,
        ),
    )
    write_text(args.release_dir / "source" / "README.md", build_source_readme())
    write_text(
        args.release_dir / "topline-summary.json",
        json.dumps(
            {
                "authoritative_tasks": len(rows),
                "benchmark_faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows),
                "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in rows),
                "total_samples": sum(row["total_samples"] for row in rows),
                "model_summary": [
                    {
                        **serialize_model_summary_row(row),
                        "benchmark_faithful_macro_accuracy": None if row["faithful_macro_accuracy"] is None else round(row["faithful_macro_accuracy"], 6),
                    }
                    for row in model_summary
                ],
                "supplementary_model_progress": [
                    {
                        **serialize_supplementary_progress_row(row),
                        "benchmark_faithful_macro_accuracy": None
                        if row["benchmark_faithful_macro_accuracy"] is None
                        else round(row["benchmark_faithful_macro_accuracy"], 6),
                    }
                    for row in supplementary_model_progress
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        args.release_dir / "release-manifest.json",
        json.dumps(
            build_release_manifest(
                rows,
                model_summary,
                benchmark_summary,
                supplementary_model_progress,
                family_size_progress,
                benchmark_comparison,
            ),
            indent=2,
        )
        + "\n",
    )

    render_coverage_svg(coverage_matrix, args.figure_dir / "option1_coverage_matrix.svg")
    render_accuracy_svg(rows, args.figure_dir / "option1_accuracy_heatmap.svg")
    render_benchmark_accuracy_bars_svg(benchmark_comparison, args.figure_dir / "option1_benchmark_accuracy_bars.svg")
    render_sample_volume_svg(rows, args.figure_dir / "option1_sample_volume.svg")

    print(json.dumps({
        "release_dir": str(args.release_dir),
        "figure_dir": str(args.figure_dir),
        "tables": [
            "benchmark-catalog.csv",
            "model-summary.csv",
            "model-roster.csv",
            "supplementary-model-progress.csv",
            "family-size-progress.csv",
            "benchmark-comparison.csv",
            "future-model-plan.csv",
            "benchmark-summary.csv",
            "faithful-metrics.csv",
            "coverage-matrix.csv",
            "jenny-group-report.md",
            "topline-summary.md",
            "topline-summary.json",
            "release-manifest.json",
            "README.md",
        ],
        "figures": [
            "option1_coverage_matrix.svg",
            "option1_accuracy_heatmap.svg",
            "option1_benchmark_accuracy_bars.svg",
            "option1_sample_volume.svg",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
