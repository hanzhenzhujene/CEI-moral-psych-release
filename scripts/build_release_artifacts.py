#!/usr/bin/env python3
"""Build curated release tables and SVG figures from the authoritative Option 1 summary."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import subprocess
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any
from zipfile import BadZipFile, ZipFile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "results" / "release" / "2026-04-19-option1"
DEFAULT_INPUT = DEFAULT_RELEASE_DIR / "source" / "authoritative-summary.csv"
DEFAULT_FIGURE_DIR = ROOT / "figures" / "release"
REPORT_TIMEZONE = ZoneInfo("America/New_York")
REPORT_GENERATED_AT = datetime.now(tz=REPORT_TIMEZONE)
RELEASE_ID = "2026-04-19-option1"
RELEASE_TITLE = "CEI Moral-Psych Benchmark Suite: Jenny Zhu Option 1 Report"
REPORT_OWNER = "Jenny Zhu"
REPORT_DATE_LONG = f"{REPORT_GENERATED_AT.strftime('%B')} {REPORT_GENERATED_AT.day}, {REPORT_GENERATED_AT.year}"
REPORT_DATE_ISO = REPORT_GENERATED_AT.date().isoformat()
SNAPSHOT_DATE_LONG = "April 19, 2026"
SNAPSHOT_DATE_ISO = "2026-04-19"
REPORT_PURPOSE = "Jenny Zhu's group-facing progress report for the April 14, 2026 five-benchmark moral-psych plan."
REPORT_PROVIDER = "OpenRouter"
REPORT_TEMPERATURE = "0"
REPORT_CURRENT_COST = "$40.73"
REPORT_STATUS_NOTE = (
    f"Updated {REPORT_DATE_LONG}. "
    "The frozen public snapshot remains Option 1 from April 19. "
    "Gemma-M and Gemma-L text remain complete locally. "
    "The earlier Qwen-M and Qwen-L text checkpoints were withdrawn from the public comparable snapshot after a "
    "verification pass showed that Qwen-3 reasoning tokens were exhausting the visible output budget on short-answer "
    "tasks. When the local rerun artifacts are available, this operations note is refreshed from the latest on-disk "
    "checkpoints, trace logs, and watcher logs at build time."
)
REPORT_LIVE_RERUNS_SUMMARY = "Pending refresh from the on-disk rerun monitor."
REPORT_NEXT_ACTION_SUMMARY = "Pending refresh from the on-disk rerun monitor."
REPORT_RELEASE_GUARDRAIL_SUMMARY = (
    "Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only."
)
REPORT_STATUS_HIGHLIGHTS = [
    "Live rerun, stalled-line, and queued-line highlights are refreshed from the latest on-disk watcher and checkpoint state at build time.",
    "Only persisted checkpoints are summarized in the public package; in-memory work that has not flushed to disk is intentionally excluded.",
    "The frozen public slice is still `Option 1`; this repo also surfaces extra local lines and queued expansion work separately.",
]
MINIMAX_SMALL_STATUS_SUMMARY = (
    "formal attempt exists, but the current line failed and is not counted as complete"
)
MINIMAX_SMALL_INTERPRETATION_NOTE = (
    "`MiniMax-S` should currently be reported as a failed formal attempt, not as a completed five-benchmark line."
)
MINIMAX_SMALL_GUARDRAIL = (
    "The MiniMax small line has a formal attempt on disk, but the current run failed and is not yet a usable comparison point."
)
PUBLIC_WITHHELD_FAMILIES = {"MiniMax"}
PUBLIC_WITHHELD_LINES = {"MiniMax-S", "MiniMax-M", "MiniMax-L"}
PUBLIC_WITHHELD_FAMILY_STATUS = ""
PUBLIC_WITHHELD_FAMILY_NOTE = ""
PUBLIC_NEXT_QUEUED_NOTE = "Pending refresh from the on-disk rerun monitor."
CI_WORKFLOW_URL = "https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml"
CI_RUN_URL = "https://github.com/hanzhenzhujene/CEI-moral-psych-release/actions/runs/24634450927"
TEXT_EXPANSION_RUN_PATH = "results/inspect/full-runs/2026-04-19-family-size-text-expansion"
IMAGE_EXPANSION_RUN_PATH = "results/inspect/full-runs/2026-04-19-family-size-image-expansion"

MODEL_ORDER = ["Qwen", "DeepSeek", "Gemma"]
FULL_MODEL_FAMILY_ORDER = ["Qwen", "MiniMax", "DeepSeek", "Llama", "Gemma"]
BENCHMARK_ORDER = ["UniMoral", "SMID", "Value Kaleidoscope", "CCD-Bench", "Denevil"]
FAMILY_SIZE_STATUS_COLUMNS = ["unimoral", "smid", "value_kaleidoscope", "ccd_bench", "denevil"]
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
MODEL_SIZE_PATTERN = re.compile(r"(?<!\d)(\d+(?:\.\d+)?)b\b", re.IGNORECASE)
TRACE_RETRY_PATTERN = re.compile(r"retry(?:ing)? in ([0-9,]+) seconds", re.IGNORECASE)

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
        "small_candidate": "No distinct small DeepSeek route is currently exposed on OpenRouter; keep the S slot unassigned for now",
        "medium_candidate": "openrouter/deepseek/deepseek-r1-distill-qwen-32b scheduled for the non-image expansion run",
        "large_candidate": "openrouter/deepseek/deepseek-chat-v3.1 already complete in the closed release",
        "next_step": "Run the queued medium DeepSeek line next; only add a separate small line if a distinct smaller provider route becomes available.",
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

LIVE_MONITOR_RERUNS = {
    "Qwen-M": {
        "eval_dir": ROOT / "results" / "inspect" / "logs" / "2026-04-21-qwen-medium-text-rerun-v1" / "qwen_14b_medium",
        "trace_dir": ROOT
        / "results"
        / "inspect"
        / "logs"
        / "2026-04-21-qwen-medium-text-rerun-v1"
        / "qwen_14b_medium"
        / "_inspect_traces",
    },
    "Qwen-L": {
        "eval_dir": ROOT / "results" / "inspect" / "logs" / "2026-04-23-qwen-large-text-rerun-v2" / "qwen_32b_large",
        "trace_dir": ROOT
        / "results"
        / "inspect"
        / "logs"
        / "2026-04-23-qwen-large-text-rerun-v2"
        / "qwen_32b_large"
        / "_inspect_traces",
    },
    "Llama-M": {
        "eval_dir": ROOT / "results" / "inspect" / "logs" / "2026-04-21-llama-medium-text-v1" / "llama_70b_medium",
        "trace_dir": ROOT
        / "results"
        / "inspect"
        / "logs"
        / "2026-04-21-llama-medium-text-v1"
        / "llama_70b_medium"
        / "_inspect_traces",
    },
}

WATCHER_LOG_PATHS = [
    ROOT / "results" / "inspect" / "full-runs" / "2026-04-21-next-text-launch-watch" / "watcher.log",
    ROOT / "results" / "inspect" / "full-runs" / "2026-04-21-deepseek-medium-launch-watch" / "watcher.log",
    ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-qwen-large-text-rerun-v2" / "keepalive.log",
]
QWEN_MEDIUM_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-21-qwen-medium-text-rerun-v1"
QWEN_LARGE_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-qwen-large-text-rerun-v2"
LLAMA_MEDIUM_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-21-llama-medium-text-v1"
LLAMA_LARGE_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-llama-large-text-rerun-v3"
LLAMA_LARGE_EVAL_DIR = (
    ROOT
    / "results"
    / "inspect"
    / "logs"
    / "2026-04-23-llama-large-text-rerun-v3"
    / "llama_4_maverick_large"
)
LLAMA_LARGE_TRACE_DIR = LLAMA_LARGE_EVAL_DIR / "_inspect_traces"
DEEPSEEK_MEDIUM_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-deepseek-medium-text-rerun-v3"
DEEPSEEK_MEDIUM_EVAL_DIR = (
    ROOT
    / "results"
    / "inspect"
    / "logs"
    / "2026-04-23-deepseek-medium-text-rerun-v3"
    / "deepseek_r1_qwen_32b_medium"
)
DEEPSEEK_MEDIUM_TRACE_DIR = DEEPSEEK_MEDIUM_EVAL_DIR / "_inspect_traces"
MINIMAX_SMALL_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-22-minimax-small-rerun-debug"
MINIMAX_SMALL_TEXT_FULL_RUN_DIR = (
    ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-minimax-small-text-rerun-v3"
)
MINIMAX_MEDIUM_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-minimax-medium-text-v2"
MINIMAX_LARGE_FULL_RUN_DIR = ROOT / "results" / "inspect" / "full-runs" / "2026-04-23-minimax-large-text-v2"
MINIMAX_MEDIUM_EVAL_DIR = (
    ROOT
    / "results"
    / "inspect"
    / "logs"
    / "2026-04-23-minimax-medium-text-v2"
    / "minimax_m2_5_medium"
)
MINIMAX_MEDIUM_TRACE_DIR = MINIMAX_MEDIUM_EVAL_DIR / "_inspect_traces"
MINIMAX_LARGE_EVAL_DIR = (
    ROOT
    / "results"
    / "inspect"
    / "logs"
    / "2026-04-23-minimax-large-text-v2"
    / "minimax_m2_7_large"
)
MINIMAX_LARGE_TRACE_DIR = MINIMAX_LARGE_EVAL_DIR / "_inspect_traces"
MINIMAX_SMALL_TEXT_EVAL_DIR = (
    ROOT
    / "results"
    / "inspect"
    / "logs"
    / "2026-04-23-minimax-small-text-rerun-v3"
    / "minimax_text"
)
MINIMAX_SMALL_SMID_EVAL_DIR = (
    ROOT
    / "results"
    / "inspect"
    / "logs"
    / "2026-04-22-minimax-small-rerun-debug"
    / "minimax_smid"
)

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
        "note": "Recovered via qwen2.5-vl-72b-instruct after the earlier moderation stop.",
    },
    {
        "line": "Gemma-L text batch",
        "status": "done",
        "note": "Completed April 21 with a full local large text line.",
    },
    {
        "line": "Gemma-M text batch",
        "status": "done",
        "note": "Completed April 21 with a full local medium text line.",
    },
    {
        "line": "Qwen-M text batch",
        "status": "live",
        "note": "Clean text rerun active; detailed checkpoints are summarized in Snapshot.",
    },
    {
        "line": "Qwen-L text batch",
        "status": "live",
        "note": "SMID recovery complete; clean text rerun active.",
    },
    {
        "line": "Llama-M text batch",
        "status": "live",
        "note": "Medium text rerun active; detailed checkpoints are summarized in Snapshot.",
    },
    {
        "line": "DeepSeek-M text batch",
        "status": "prep",
        "note": "Still queued behind the live Llama-M rerun.",
    },
    {
        "line": "Llama-L SMID",
        "status": "done",
        "note": "The large Llama vision line is complete locally.",
    },
    {
        "line": "Next queued text lines",
        "status": "queue",
        "note": "Llama-L, MiniMax-M, and MiniMax-L are waiting on the live reruns.",
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
        "value_kaleidoscope": "live",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "Clean text rerun active after withdrawn short-answer artifacts.",
    },
    {
        "family": "Qwen",
        "size_slot": "L",
        "line_label": "Qwen-L",
        "text_route": "openrouter/qwen/qwen3-32b",
        "vision_route": "openrouter/qwen/qwen2.5-vl-72b-instruct (recovery complete)",
        "unimoral": "done",
        "smid": "done",
        "value_kaleidoscope": "live",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "SMID recovery complete; clean text rerun active.",
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
        "summary_note": "Text queued; no medium SMID route fixed yet.",
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
        "summary_note": "Text queued; no large SMID route fixed yet.",
    },
    {
        "family": "DeepSeek",
        "size_slot": "S",
        "line_label": "DeepSeek-S",
        "text_route": "No distinct small OpenRouter route exposed",
        "vision_route": "-",
        "unimoral": "tbd",
        "smid": "-",
        "value_kaleidoscope": "tbd",
        "ccd_bench": "tbd",
        "denevil": "tbd",
        "summary_note": "No distinct small DeepSeek route is fixed yet.",
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
        "summary_note": "No vision route; queued behind the live Llama-M rerun.",
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
        "unimoral": "done",
        "smid": "-",
        "value_kaleidoscope": "live",
        "ccd_bench": "queue",
        "denevil": "queue",
        "summary_note": "No SMID run is planned. UniMoral is complete. The live rerun checkpoint text is refreshed from the local artifacts at build time when those files are available.",
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
        "summary_note": "Complete local line across all five papers.",
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
        "summary_note": "Complete local line across all five papers.",
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
        "scope": "Live local rerun",
        "status": "live",
        "coverage": "Earlier text checkpoints withdrawn; UniMoral done; live rerun checkpoint refreshes at build time",
        "note": "Clean text rerun active; detailed checkpoints are summarized in Snapshot.",
    },
    {
        "line_label": "Qwen-L",
        "scope": "Live local rerun",
        "status": "live",
        "coverage": "SMID recovery stands; UniMoral done; live rerun checkpoint refreshes at build time",
        "note": "SMID recovery complete; clean text rerun active.",
    },
    {
        "line_label": "Llama-M",
        "scope": "Live local rerun",
        "status": "live",
        "coverage": "UniMoral done; live rerun checkpoint refreshes at build time",
        "note": "Medium text rerun active; detailed checkpoints are summarized in Snapshot.",
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

LOCAL_COMPARISON_LINE_SOURCES = [
    {
        "line_label": "MiniMax-S",
        "family": "MiniMax",
        "size_slot": "S",
        "route": "text: openrouter/minimax/minimax-m2.1; vision: openrouter/minimax/minimax-01",
        "coverage_note": "Fresh small rerun: SMID is complete locally; the text rerun is still partial after key-limit failures.",
        "task_sources": {
            "unimoral_action_prediction": MINIMAX_SMALL_TEXT_EVAL_DIR,
            "smid_moral_rating": MINIMAX_SMALL_SMID_EVAL_DIR,
            "smid_foundation_classification": MINIMAX_SMALL_SMID_EVAL_DIR,
            "value_prism_relevance": MINIMAX_SMALL_TEXT_EVAL_DIR,
            "value_prism_valence": MINIMAX_SMALL_TEXT_EVAL_DIR,
        },
    },
    {
        "line_label": "Llama-S",
        "family": "Llama",
        "size_slot": "S",
        "route": "openrouter/meta-llama/llama-3.2-11b-vision-instruct",
        "coverage_note": "Complete locally across all five papers, but still outside the frozen Option 1 snapshot counts.",
        "unimoral_action_accuracy": 0.6479963570127505,
        "smid_average_accuracy": 0.21642298537912275,
        "value_average_accuracy": 0.5285828754578754,
        "task_sources": {
            "unimoral_action_prediction": [
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision" / "llama_text",
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision-recovery-v3" / "llama_text",
            ],
            "value_prism_relevance": [
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision" / "llama_text",
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision-recovery-v3" / "llama_text",
            ],
            "value_prism_valence": [
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision" / "llama_text",
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision-recovery-v3" / "llama_text",
            ],
            "smid_moral_rating": [
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision" / "llama_smid",
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision-recovery-v3" / "llama_smid",
            ],
            "smid_foundation_classification": [
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision" / "llama_smid",
                ROOT / "results" / "inspect" / "logs" / "2026-04-19-option1-llama32-11b-vision-recovery-v3" / "llama_smid",
            ],
        },
    },
    {
        "line_label": "Llama-L",
        "family": "Llama",
        "size_slot": "L",
        "route": "vision: openrouter/meta-llama/llama-4-maverick",
        "coverage_note": "Latest large vision line. SMID is complete, while the matching text tasks are still queued.",
        "unimoral_action_accuracy": None,
        "smid_average_accuracy": 0.3860931655899354,
        "value_average_accuracy": None,
        "task_sources": {
            "smid_moral_rating": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-image-expansion" / "llama_4_maverick_large_smid",
            "smid_foundation_classification": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-image-expansion" / "llama_4_maverick_large_smid",
        },
    },
    {
        "line_label": "Gemma-M",
        "family": "Gemma",
        "size_slot": "M",
        "route": "text: openrouter/google/gemma-3-12b-it; vision: openrouter/google/gemma-3-12b-it",
        "coverage_note": "Complete local medium line with both text and SMID image results finished.",
        "unimoral_action_accuracy": 0.662568306010929,
        "smid_average_accuracy": 0.36365181910914654,
        "value_average_accuracy": 0.6636561355311355,
        "task_sources": {
            "unimoral_action_prediction": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-text-expansion" / "gemma_12b_medium",
            "value_prism_relevance": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-text-expansion" / "gemma_12b_medium",
            "value_prism_valence": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-text-expansion" / "gemma_12b_medium",
            "smid_moral_rating": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-image-expansion" / "gemma_12b_medium_smid",
            "smid_foundation_classification": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-image-expansion" / "gemma_12b_medium_smid",
        },
    },
    {
        "line_label": "Gemma-L",
        "family": "Gemma",
        "size_slot": "L",
        "route": "text: openrouter/google/gemma-3-27b-it; vision: openrouter/google/gemma-3-27b-it",
        "coverage_note": "Complete local large line with both text and SMID image results finished.",
        "unimoral_action_accuracy": 0.6610883424408015,
        "smid_average_accuracy": 0.4122747364841891,
        "value_average_accuracy": 0.6559867216117216,
        "task_sources": {
            "unimoral_action_prediction": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-text-expansion" / "gemma_27b_large",
            "value_prism_relevance": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-text-expansion" / "gemma_27b_large",
            "value_prism_valence": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-text-expansion" / "gemma_27b_large",
            "smid_moral_rating": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-image-expansion" / "gemma_27b_large_smid",
            "smid_foundation_classification": ROOT / "results" / "inspect" / "logs" / "2026-04-19-family-size-image-expansion" / "gemma_27b_large_smid",
        },
    },
]

FAMILY_COLOR_SCALES = {
    "Qwen": {"S": "#0f766e", "M": "#0d9488", "L": "#2dd4bf"},
    "DeepSeek": {"S": "#1d4ed8", "M": "#2563eb", "L": "#60a5fa"},
    "Llama": {"S": "#c2410c", "M": "#ea580c", "L": "#fb923c"},
    "Gemma": {"S": "#6d28d9", "M": "#8b5cf6", "L": "#c4b5fd"},
    "MiniMax": {"S": "#b45309", "M": "#d97706", "L": "#fbbf24"},
}

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


def _read_json_member(zf: ZipFile, member: str) -> dict[str, Any] | list[Any] | None:
    try:
        return json.loads(zf.read(member).decode("utf-8"))
    except KeyError:
        return None


def _format_samples(value: int) -> str:
    return f"{value:,}"


def _format_monitor_time(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=REPORT_TIMEZONE)
    return f"{dt.strftime('%I:%M %p').lstrip('0')} ET"


def _format_monitor_date(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=REPORT_TIMEZONE)
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def _format_monitor_time_on_date(timestamp: float) -> str:
    return f"{_format_monitor_time(timestamp)} on {_format_monitor_date(timestamp)}"


def _latest_existing_mtime(paths: list[Path]) -> float | None:
    mtimes = [path.stat().st_mtime for path in paths if path.exists()]
    return max(mtimes) if mtimes else None


def _latest_trace_mtime(trace_dir: Path) -> float | None:
    if not trace_dir.exists():
        return None
    mtimes = [path.stat().st_mtime for path in trace_dir.glob("trace-*.log*") if path.is_file()]
    return max(mtimes) if mtimes else None


def _has_recent_trace_activity(trace_dir: Path, max_age_seconds: int = 15 * 60) -> bool:
    trace_mtime = _latest_trace_mtime(trace_dir)
    if trace_mtime is None:
        return False
    return (datetime.now(tz=REPORT_TIMEZONE).timestamp() - trace_mtime) <= max_age_seconds


def _latest_trace_tail(trace_dir: Path, max_lines: int = 40) -> list[str]:
    if not trace_dir.exists():
        return []

    trace_files = [path for path in trace_dir.glob("trace-*.log*") if path.is_file()]
    if not trace_files:
        return []

    latest = max(trace_files, key=lambda path: path.stat().st_mtime)
    opener = gzip.open if latest.suffix == ".gz" else open
    try:
        with opener(latest, "rt", encoding="utf-8", errors="ignore") as handle:
            return list(deque(handle, maxlen=max_lines))
    except OSError:
        return []


def _latest_trace_contains_success(trace_dir: Path) -> bool:
    tail = _latest_trace_tail(trace_dir, max_lines=40)
    return any("200 OK" in line for line in tail)


def _latest_trace_retry_seconds(trace_dir: Path) -> int | None:
    for line in reversed(_latest_trace_tail(trace_dir, max_lines=80)):
        match = TRACE_RETRY_PATTERN.search(line)
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def _format_backoff_duration(seconds: int) -> str:
    minutes, remainder = divmod(seconds, 60)
    if remainder == 0 and minutes:
        hours, extra_minutes = divmod(minutes, 60)
        if hours and extra_minutes:
            return f"{hours} hour{'s' if hours != 1 else ''} {extra_minutes} minute{'s' if extra_minutes != 1 else ''}"
        if hours:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{seconds:,} seconds"


def _trace_monitor_sentence(label: str, trace_dir: Path) -> str:
    trace_mtime = _latest_trace_mtime(trace_dir)
    if trace_mtime is None:
        return f"{label} had no fresh local Inspect trace evidence in this pass"

    trace_phrase = _format_monitor_time_on_date(trace_mtime)
    if _latest_trace_contains_success(trace_dir):
        return f"{label} still showed live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}"

    retry_seconds = _latest_trace_retry_seconds(trace_dir)
    if retry_seconds is not None:
        return (
            f"{label} still showed Inspect trace writes through about {trace_phrase}, but the latest tail was in "
            f"connection-error retry backoff ({_format_backoff_duration(retry_seconds)}) rather than a fresh `200 OK`"
        )

    return f"{label} still showed Inspect trace writes through about {trace_phrase}"


def _iter_eval_checkpoints(eval_dir: Path, task_name: str | None = None) -> Iterable[dict[str, Any]]:
    if not eval_dir.exists():
        return

    for eval_path in sorted(eval_dir.glob("*.eval")):
        try:
            with ZipFile(eval_path) as zf:
                names = zf.namelist()
                header = _read_json_member(zf, "header.json") or {}
                start = _read_json_member(zf, "_journal/start.json") or {}
                base = header or start
                meta = (base.get("eval") if isinstance(base, dict) else {}) or {}
                task = str(meta.get("task", ""))
                if task_name is not None and task != task_name:
                    continue
                total = int((((meta.get("dataset") or {}).get("samples")) or 0))
                completed = sum(1 for name in names if name.startswith("samples/") and name.endswith(".json"))
                if header.get("results"):
                    completed = int(header["results"].get("completed_samples", completed) or completed)
                    total = int(header["results"].get("total_samples", total) or total)
                status = str(header.get("status", "running")) if header else "running"
                error = header.get("error")
                if isinstance(error, dict):
                    error_message = str(error.get("message", ""))
                elif error is None:
                    error_message = ""
                else:
                    error_message = str(error)
        except BadZipFile:
            continue

        yield {
            "path": eval_path,
            "task": task,
            "status": status,
            "error_message": error_message,
            "completed": completed,
            "total": total,
            "progress_pct": (completed / total * 100.0) if total else 0.0,
            "mtime": eval_path.stat().st_mtime,
            "size_bytes": eval_path.stat().st_size,
        }


def _best_eval_checkpoint(eval_dir: Path, task_name: str | None = None) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for checkpoint in _iter_eval_checkpoints(eval_dir, task_name=task_name):
        if best is None or (
            checkpoint["completed"],
            checkpoint["mtime"],
            checkpoint["size_bytes"],
        ) > (
            best["completed"],
            best["mtime"],
            best["size_bytes"],
        ):
            best = checkpoint
    return best


def _latest_eval_checkpoint(eval_dir: Path, task_name: str | None = None) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    for checkpoint in _iter_eval_checkpoints(eval_dir, task_name=task_name):
        if latest is None or (
            checkpoint["mtime"],
            checkpoint["size_bytes"],
            checkpoint["completed"],
        ) > (
            latest["mtime"],
            latest["size_bytes"],
            latest["completed"],
        ):
            latest = checkpoint
    return latest


def _task_display_name(task_name: str) -> str:
    display = {
        "unimoral_action_prediction": "UniMoral action prediction",
        "value_prism_relevance": "Value Prism Relevance",
        "value_prism_valence": "Value Prism Valence",
        "ccd_bench_selection": "CCD-Bench",
        "denevil_fulcra_proxy_generation": "Denevil proxy",
    }.get(task_name)
    if display is not None:
        return display
    return task_name.replace("_", " ").strip().title()


def _checkpoint_task_phrase(checkpoint: dict[str, Any]) -> str:
    task_label = _task_display_name(str(checkpoint.get("task", ""))).strip()
    return (
        f"{_format_samples(checkpoint['completed'])} / {_format_samples(checkpoint['total'])} "
        f"{task_label} samples ({checkpoint['progress_pct']:.1f}%) at "
        f"{_format_monitor_time_on_date(checkpoint['mtime'])}"
    )


def _checkpoint_summary(label: str, checkpoint: dict[str, Any]) -> str:
    return (
        f"{_format_samples(checkpoint['completed'])} / {_format_samples(checkpoint['total'])} samples "
        f"({checkpoint['progress_pct']:.1f}%) for {label} at {_format_monitor_time_on_date(checkpoint['mtime'])}"
    )


def _checkpoint_has_key_limit_error(checkpoint: dict[str, Any] | None) -> bool:
    if checkpoint is None:
        return False
    error_text = str(checkpoint.get("error_message", "") or "")
    return "Key limit exceeded" in error_text or "monthly limit" in error_text


def _find_row(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    for row in rows:
        if row.get(key) == value:
            return row
    raise KeyError(f"Could not find row where {key} == {value!r}")


def _read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _live_worker_pid(path: Path, command_fragment: str) -> int | None:
    text = _read_text_if_exists(path)
    if not text:
        return None

    try:
        pid = int(text)
    except ValueError:
        return None

    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return None

    command = result.stdout.strip()
    if not command or command_fragment not in command:
        return None

    return pid


def _read_task_status_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            parsed = dict(row)
            try:
                parsed["returncode"] = int(str(parsed.get("returncode", "")).strip())
            except ValueError:
                parsed["returncode"] = None
            rows.append(parsed)
    return rows


def _latest_task_status_row(path: Path, task_name: str | None = None) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    for row in _read_task_status_rows(path):
        if task_name is not None and row.get("task_name") != task_name:
            continue
        latest = row
    return latest


def _task_row_output_text(row: dict[str, Any] | None) -> str:
    if row is None:
        return ""
    output_path = row.get("output_path")
    if not output_path:
        return ""
    return (_read_text_if_exists(Path(str(output_path))) or "").strip()


def _task_row_has_credit_exhaustion(row: dict[str, Any] | None) -> bool:
    text = _task_row_output_text(row)
    return "Insufficient credits" in text and "402" in text


def _upsert_current_result_line(row: dict[str, Any], before_label: str | None = None) -> dict[str, Any]:
    for existing in CURRENT_RESULT_LINES:
        if existing.get("line_label") == row.get("line_label"):
            existing.update(row)
            return existing

    insert_at = len(CURRENT_RESULT_LINES)
    if before_label is not None:
        for index, existing in enumerate(CURRENT_RESULT_LINES):
            if existing.get("line_label") == before_label:
                insert_at = index
                break
    CURRENT_RESULT_LINES.insert(insert_at, row)
    return CURRENT_RESULT_LINES[insert_at]


def _join_optional_note_sentences(*notes: str) -> str:
    sentences: list[str] = []
    for note in notes:
        stripped = note.strip()
        if not stripped:
            continue
        if stripped[-1] not in ".!?":
            stripped += "."
        sentences.append(stripped)

    if not sentences:
        return ""
    return " " + " ".join(sentences)


def _apply_live_monitor_snapshot() -> None:
    global MINIMAX_SMALL_GUARDRAIL
    global MINIMAX_SMALL_INTERPRETATION_NOTE
    global MINIMAX_SMALL_STATUS_SUMMARY
    global REPORT_LIVE_RERUNS_SUMMARY
    global REPORT_NEXT_ACTION_SUMMARY
    global REPORT_RELEASE_GUARDRAIL_SUMMARY
    global REPORT_STATUS_HIGHLIGHTS
    global REPORT_STATUS_NOTE

    checkpoints: dict[str, dict[str, Any]] = {}
    for label, spec in LIVE_MONITOR_RERUNS.items():
        checkpoint = _best_eval_checkpoint(spec["eval_dir"])
        if checkpoint is None:
            return
        checkpoints[label] = checkpoint

    trace_mtime = max(
        (mtime for mtime in (_latest_trace_mtime(spec["trace_dir"]) for spec in LIVE_MONITOR_RERUNS.values()) if mtime is not None),
        default=None,
    )
    watcher_mtime = _latest_existing_mtime(WATCHER_LOG_PATHS)
    if trace_mtime is None or watcher_mtime is None:
        return

    trace_phrase = _format_monitor_time_on_date(trace_mtime)
    watcher_phrase = _format_monitor_time_on_date(watcher_mtime)
    qwen_medium = checkpoints["Qwen-M"]
    qwen_large = checkpoints["Qwen-L"]
    llama_medium = checkpoints["Llama-M"]
    qwen_medium_job_dir = QWEN_MEDIUM_FULL_RUN_DIR / "qwen_14b_medium"
    qwen_medium_job_done = (qwen_medium_job_dir / "job_done.txt").exists()
    qwen_medium_active_rerun = (
        _live_worker_pid(
            qwen_medium_job_dir / "worker.pid",
            "family_size_text_expansion.sh run qwen_14b_medium",
        )
        is not None
        or _has_recent_trace_activity(LIVE_MONITOR_RERUNS["Qwen-M"]["trace_dir"])
    )
    qwen_medium_final_task = _latest_task_status_row(qwen_medium_job_dir / "task_status.csv")
    qwen_large_job_dir = QWEN_LARGE_FULL_RUN_DIR / "qwen_32b_large"
    qwen_large_job_done = (qwen_large_job_dir / "job_done.txt").exists()
    qwen_large_active_rerun = (
        _live_worker_pid(
            qwen_large_job_dir / "worker.pid",
            "family_size_text_expansion.sh run qwen_32b_large",
        )
        is not None
        or _has_recent_trace_activity(LIVE_MONITOR_RERUNS["Qwen-L"]["trace_dir"])
    )
    qwen_large_final_task = _latest_task_status_row(qwen_large_job_dir / "task_status.csv")
    qwen_medium_valence = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Qwen-M"]["eval_dir"],
        task_name="value_prism_valence",
    )
    qwen_medium_latest = _latest_eval_checkpoint(LIVE_MONITOR_RERUNS["Qwen-M"]["eval_dir"])
    qwen_medium_ccd = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Qwen-M"]["eval_dir"],
        task_name="ccd_bench_selection",
    )
    qwen_medium_denevil = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Qwen-M"]["eval_dir"],
        task_name="denevil_fulcra_proxy_generation",
    )
    qwen_medium_completed_clean = bool(
        qwen_medium_job_done
        and qwen_medium_final_task is not None
        and qwen_medium_final_task.get("task_name") == "denevil_fulcra_proxy_generation"
        and qwen_medium_final_task.get("returncode") == 0
        and qwen_medium_denevil is not None
        and qwen_medium_denevil["status"] == "success"
        and qwen_medium_denevil["completed"] == qwen_medium_denevil["total"]
    )
    qwen_medium_stopped_partial = (
        qwen_medium_job_done and not qwen_medium_completed_clean and not qwen_medium_active_rerun
    )
    llama_valence = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Llama-M"]["eval_dir"],
        task_name="value_prism_valence",
    )
    llama_denevil = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Llama-M"]["eval_dir"],
        task_name="denevil_fulcra_proxy_generation",
    )
    llama_latest = _latest_eval_checkpoint(LIVE_MONITOR_RERUNS["Llama-M"]["eval_dir"])
    llama_ccd = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Llama-M"]["eval_dir"],
        task_name="ccd_bench_selection",
    )
    llama_master_status_path = LLAMA_MEDIUM_FULL_RUN_DIR / "master_status.txt"
    llama_master_status = _read_text_if_exists(llama_master_status_path) or ""
    llama_completed = llama_master_status.startswith("completed:")
    llama_completion_phrase = (
        _format_monitor_time_on_date(llama_master_status_path.stat().st_mtime)
        if llama_completed
        else None
    )
    deepseek_master_status_path = DEEPSEEK_MEDIUM_FULL_RUN_DIR / "master_status.txt"
    deepseek_master_status = _read_text_if_exists(deepseek_master_status_path) or ""
    deepseek_current_job = _read_text_if_exists(DEEPSEEK_MEDIUM_FULL_RUN_DIR / "current_job.txt") or ""
    deepseek_job_dir = DEEPSEEK_MEDIUM_FULL_RUN_DIR / "deepseek_r1_qwen_32b_medium"
    deepseek_job_failed = (deepseek_job_dir / "job_failed.txt").exists()
    deepseek_latest_task = _latest_task_status_row(deepseek_job_dir / "task_status.csv")
    deepseek_credit_exhausted = _task_row_has_credit_exhaustion(deepseek_latest_task)
    deepseek_launched = (
        deepseek_master_status.startswith("running:")
        or deepseek_master_status.startswith("completed:")
        or bool(deepseek_current_job)
    )
    deepseek_completed = deepseek_master_status.startswith("completed:")
    deepseek_launch_phrase = (
        _format_monitor_time_on_date(deepseek_master_status_path.stat().st_mtime)
        if deepseek_master_status_path.exists()
        else None
    )
    deepseek_trace_sentence = _trace_monitor_sentence("DeepSeek-M", DEEPSEEK_MEDIUM_TRACE_DIR)
    deepseek_latest = _latest_eval_checkpoint(DEEPSEEK_MEDIUM_EVAL_DIR)
    deepseek_unimoral = _best_eval_checkpoint(
        DEEPSEEK_MEDIUM_EVAL_DIR,
        task_name="unimoral_action_prediction",
    )
    deepseek_value_relevance = _best_eval_checkpoint(
        DEEPSEEK_MEDIUM_EVAL_DIR,
        task_name="value_prism_relevance",
    )
    deepseek_value_valence = _best_eval_checkpoint(
        DEEPSEEK_MEDIUM_EVAL_DIR,
        task_name="value_prism_valence",
    )
    deepseek_ccd = _best_eval_checkpoint(
        DEEPSEEK_MEDIUM_EVAL_DIR,
        task_name="ccd_bench_selection",
    )
    deepseek_denevil = _best_eval_checkpoint(
        DEEPSEEK_MEDIUM_EVAL_DIR,
        task_name="denevil_fulcra_proxy_generation",
    )
    deepseek_live_rerun = (
        _live_worker_pid(
            deepseek_job_dir / "worker.pid",
            "family_size_text_expansion.sh run deepseek_r1_qwen_32b_medium",
        )
        is not None
        or _has_recent_trace_activity(DEEPSEEK_MEDIUM_TRACE_DIR)
    )
    llama_large_job_dir = LLAMA_LARGE_FULL_RUN_DIR / "llama_4_maverick_large"
    llama_large_latest_task = _latest_task_status_row(llama_large_job_dir / "task_status.csv")
    llama_large_credit_exhausted = _task_row_has_credit_exhaustion(llama_large_latest_task)
    llama_large_active_rerun = (
        _live_worker_pid(
            llama_large_job_dir / "worker.pid",
            "family_size_text_expansion.sh run llama_4_maverick_large",
        )
        is not None
        or _has_recent_trace_activity(LLAMA_LARGE_TRACE_DIR)
    )
    llama_large_latest = _latest_eval_checkpoint(LLAMA_LARGE_EVAL_DIR)
    llama_large_unimoral = _best_eval_checkpoint(
        LLAMA_LARGE_EVAL_DIR,
        task_name="unimoral_action_prediction",
    )
    llama_large_value_relevance = _best_eval_checkpoint(
        LLAMA_LARGE_EVAL_DIR,
        task_name="value_prism_relevance",
    )
    llama_large_value_valence = _best_eval_checkpoint(
        LLAMA_LARGE_EVAL_DIR,
        task_name="value_prism_valence",
    )
    llama_large_ccd = _best_eval_checkpoint(
        LLAMA_LARGE_EVAL_DIR,
        task_name="ccd_bench_selection",
    )
    llama_large_denevil = _best_eval_checkpoint(
        LLAMA_LARGE_EVAL_DIR,
        task_name="denevil_fulcra_proxy_generation",
    )
    minimax_medium_job_dir = MINIMAX_MEDIUM_FULL_RUN_DIR / "minimax_m2_5_medium"
    minimax_medium_active_rerun = (
        _live_worker_pid(
            minimax_medium_job_dir / "worker.pid",
            "family_size_text_expansion.sh run minimax_m2_5_medium",
        )
        is not None
        or _has_recent_trace_activity(MINIMAX_MEDIUM_TRACE_DIR)
    )
    minimax_medium_latest = _latest_eval_checkpoint(MINIMAX_MEDIUM_EVAL_DIR)
    minimax_medium_unimoral = _best_eval_checkpoint(
        MINIMAX_MEDIUM_EVAL_DIR,
        task_name="unimoral_action_prediction",
    )
    minimax_large_job_dir = MINIMAX_LARGE_FULL_RUN_DIR / "minimax_m2_7_large"
    minimax_large_active_rerun = (
        _live_worker_pid(
            minimax_large_job_dir / "worker.pid",
            "family_size_text_expansion.sh run minimax_m2_7_large",
        )
        is not None
        or _has_recent_trace_activity(MINIMAX_LARGE_TRACE_DIR)
    )
    minimax_large_latest = _latest_eval_checkpoint(MINIMAX_LARGE_EVAL_DIR)
    minimax_large_unimoral = _best_eval_checkpoint(
        MINIMAX_LARGE_EVAL_DIR,
        task_name="unimoral_action_prediction",
    )
    minimax_large_value_relevance = _best_eval_checkpoint(
        MINIMAX_LARGE_EVAL_DIR,
        task_name="value_prism_relevance",
    )
    minimax_text_done = (MINIMAX_SMALL_FULL_RUN_DIR / "minimax_text" / "family_done.txt").exists()
    minimax_smid_done = (MINIMAX_SMALL_FULL_RUN_DIR / "minimax_smid" / "family_done.txt").exists()
    minimax_has_rerun = minimax_text_done or minimax_smid_done
    minimax_unimoral = _best_eval_checkpoint(
        MINIMAX_SMALL_TEXT_EVAL_DIR,
        task_name="unimoral_action_prediction",
    )
    minimax_value_relevance = _best_eval_checkpoint(
        MINIMAX_SMALL_TEXT_EVAL_DIR,
        task_name="value_prism_relevance",
    )
    minimax_value_valence = _best_eval_checkpoint(
        MINIMAX_SMALL_TEXT_EVAL_DIR,
        task_name="value_prism_valence",
    )
    minimax_ccd = _best_eval_checkpoint(
        MINIMAX_SMALL_TEXT_EVAL_DIR,
        task_name="ccd_bench_selection",
    )
    minimax_denevil = _best_eval_checkpoint(
        MINIMAX_SMALL_TEXT_EVAL_DIR,
        task_name="denevil_fulcra_proxy_generation",
    )
    minimax_smid_moral = latest_successful_eval(MINIMAX_SMALL_SMID_EVAL_DIR, "smid_moral_rating")
    minimax_smid_foundation = latest_successful_eval(
        MINIMAX_SMALL_SMID_EVAL_DIR,
        "smid_foundation_classification",
    )
    minimax_smid_complete = minimax_smid_moral is not None and minimax_smid_foundation is not None
    minimax_small_latest_task = _latest_task_status_row(
        MINIMAX_SMALL_TEXT_FULL_RUN_DIR / "minimax_text" / "task_status.csv"
    )
    minimax_small_active_rerun = (
        _live_worker_pid(
            MINIMAX_SMALL_TEXT_FULL_RUN_DIR / "pids" / "minimax_text.pid",
            "full_option1_runs_minimax_small.sh run minimax_text",
        )
        is not None
    )
    minimax_small_reasoning_blocked = False
    if minimax_small_latest_task is not None and minimax_small_latest_task.get("returncode") not in {None, 0, "0"}:
        latest_output_path = minimax_small_latest_task.get("output_path")
        latest_output_text = (
            _read_text_if_exists(Path(str(latest_output_path))) if latest_output_path else None
        ) or ""
        minimax_small_reasoning_blocked = (
            "Reasoning is mandatory" in latest_output_text
            and "cannot be disabled" in latest_output_text
        )
    minimax_unimoral_guardrail = (
        inspect_empty_answer_rate(minimax_unimoral["path"]) if minimax_unimoral is not None else None
    )
    minimax_unimoral_invalid = bool(
        minimax_unimoral_guardrail is not None
        and minimax_unimoral_guardrail["empty_answer_rate"] >= 0.95
    )
    trace_evidence_sentences: list[str] = []
    if qwen_medium_active_rerun:
        trace_evidence_sentences.append(_trace_monitor_sentence("Qwen-M", LIVE_MONITOR_RERUNS["Qwen-M"]["trace_dir"]))
    if qwen_large_active_rerun:
        trace_evidence_sentences.append(_trace_monitor_sentence("Qwen-L", LIVE_MONITOR_RERUNS["Qwen-L"]["trace_dir"]))
    if llama_large_active_rerun:
        trace_evidence_sentences.append(_trace_monitor_sentence("Llama-L", LLAMA_LARGE_TRACE_DIR))
    if minimax_medium_active_rerun:
        trace_evidence_sentences.append(_trace_monitor_sentence("MiniMax-M", MINIMAX_MEDIUM_TRACE_DIR))
    if deepseek_live_rerun:
        trace_evidence_sentences.append(deepseek_trace_sentence)
    elif not llama_completed:
        trace_evidence_sentences.append(_trace_monitor_sentence("Llama-M", LIVE_MONITOR_RERUNS["Llama-M"]["trace_dir"]))
    trace_evidence_phrase = "; ".join(trace_evidence_sentences)
    qwen_medium_current_scope = "Live local rerun"
    qwen_medium_current_status = "live"
    qwen_medium_current_note = "Clean text rerun active; detailed checkpoints are summarized in Snapshot."
    qwen_medium_progress_summary = "Clean text rerun active after withdrawn short-answer artifacts."
    qwen_medium_local_checkpoint_status = "live"
    qwen_medium_local_checkpoint_note = "Clean text rerun active; detailed checkpoints are summarized in Snapshot."
    if qwen_medium_stopped_partial:
        qwen_medium_current_scope = "Attempted local rerun"
        qwen_medium_current_status = "partial"
        qwen_medium_current_note = "Clean text rerun reached Denevil, then stopped on OpenRouter monthly key-limit 403."
        qwen_medium_progress_summary = qwen_medium_current_note
        qwen_medium_local_checkpoint_status = "partial"
        qwen_medium_local_checkpoint_note = qwen_medium_current_note
    elif qwen_medium_completed_clean:
        qwen_medium_current_scope = "Complete local line"
        qwen_medium_current_status = "done"
        qwen_medium_current_note = "Clean text rerun finished locally after the withdrawn short-answer artifacts."
        qwen_medium_progress_summary = qwen_medium_current_note
        qwen_medium_local_checkpoint_status = "done"
        qwen_medium_local_checkpoint_note = qwen_medium_current_note

    llama_stage_note = ""
    qwen_medium_stage_note = ""
    qwen_large_stage_note = ""
    deepseek_stage_note = ""
    minimax_stage_note = ""
    qwen_medium_current_coverage = (
        f"Earlier text checkpoints withdrawn; UniMoral done; live rerun holds a "
        f"{qwen_medium['progress_pct']:.1f}% persisted Value Prism Relevance checkpoint"
    )
    qwen_medium_line_suffix = (
        f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}, and the rerun is "
        f"active again with live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
    )
    qwen_medium_matrix_summary = (
        f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}. The Value "
        f"Kaleidoscope rerun is active again, with live Inspect trace writes and recent `200 OK` OpenRouter calls "
        f"through about {trace_phrase}."
    )
    qwen_large_valence = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Qwen-L"]["eval_dir"],
        task_name="value_prism_valence",
    )
    qwen_large_latest = _latest_eval_checkpoint(LIVE_MONITOR_RERUNS["Qwen-L"]["eval_dir"])
    qwen_large_ccd = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Qwen-L"]["eval_dir"],
        task_name="ccd_bench_selection",
    )
    qwen_large_denevil = _best_eval_checkpoint(
        LIVE_MONITOR_RERUNS["Qwen-L"]["eval_dir"],
        task_name="denevil_fulcra_proxy_generation",
    )
    qwen_large_completed_clean = bool(
        qwen_large_job_done
        and qwen_large_final_task is not None
        and qwen_large_final_task.get("task_name") == "denevil_fulcra_proxy_generation"
        and qwen_large_final_task.get("returncode") == 0
        and qwen_large_denevil is not None
        and qwen_large_denevil["status"] == "success"
        and qwen_large_denevil["completed"] == qwen_large_denevil["total"]
    )
    qwen_large_stopped_partial = (
        qwen_large_job_done and not qwen_large_completed_clean and not qwen_large_active_rerun
    )
    qwen_large_current_scope = "Live local rerun"
    qwen_large_current_status = "live"
    qwen_large_current_note = "SMID recovery complete; clean text rerun active."
    qwen_large_progress_summary = "SMID recovery complete; clean text rerun active."
    qwen_large_local_checkpoint_status = "live"
    qwen_large_local_checkpoint_note = "SMID recovery complete; clean text rerun active."
    if qwen_large_stopped_partial:
        qwen_large_current_scope = "Attempted local rerun"
        qwen_large_current_status = "partial"
        qwen_large_current_note = "SMID recovery complete; clean text rerun reached Denevil, then stopped on OpenRouter monthly key-limit 403."
        qwen_large_progress_summary = qwen_large_current_note
        qwen_large_local_checkpoint_status = "partial"
        qwen_large_local_checkpoint_note = qwen_large_current_note
    elif qwen_large_completed_clean:
        qwen_large_current_scope = "Complete local line"
        qwen_large_current_status = "done"
        qwen_large_current_note = "SMID recovery complete; clean text rerun finished locally."
        qwen_large_progress_summary = qwen_large_current_note
        qwen_large_local_checkpoint_status = "done"
        qwen_large_local_checkpoint_note = qwen_large_current_note
    qwen_large_current_coverage = (
        "SMID recovery stands; UniMoral done; live rerun holds a "
        f"{qwen_large['progress_pct']:.1f}% persisted Value Prism Relevance checkpoint"
    )
    qwen_large_line_suffix = (
        "The SMID recovery still stands, and the best clean rerun checkpoint on disk still reaches "
        f"{_checkpoint_task_phrase(qwen_large)}, and the rerun is active again with live Inspect trace writes and "
        f"recent `200 OK` OpenRouter calls through about {trace_phrase}."
    )
    qwen_large_matrix_summary = (
        "The SMID recovery remains complete. UniMoral also remains complete, and the best clean rerun checkpoint on "
        f"disk still reaches {_checkpoint_task_phrase(qwen_large)}. The Value Kaleidoscope rerun is active again, with "
        f"live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
    )
    if qwen_medium_valence is not None and qwen_medium_valence["completed"] > 0:
        qwen_medium_stage_note = (
            " Qwen-M has already moved into Value Prism Valence, and the current saved archive has reached "
            f"{_checkpoint_task_phrase(qwen_medium_valence)}."
        )
        qwen_medium_current_coverage = (
            "Earlier text checkpoints withdrawn; UniMoral done; Value Prism Relevance is fully persisted; "
            f"Value Prism Valence holds a {qwen_medium_valence['progress_pct']:.1f}% persisted checkpoint"
        )
        qwen_medium_line_suffix = (
            f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}. The current "
            f"Value Prism Valence archive has also reached {_checkpoint_task_phrase(qwen_medium_valence)}, and the rerun "
            f"is active again with live Inspect trace writes and recent `200 OK` OpenRouter calls through about "
            f"{trace_phrase}."
        )
        qwen_medium_matrix_summary = (
            f"{_checkpoint_task_phrase(qwen_medium)}. The current Value Prism Valence archive has also reached "
            f"{_checkpoint_task_phrase(qwen_medium_valence)}. The Value Kaleidoscope rerun is active again, with live "
            f"Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
        )
    if (
        qwen_medium_ccd is not None
        and qwen_medium_ccd["completed"] > 0
        and qwen_medium_latest is not None
        and qwen_medium_latest["task"] == "ccd_bench_selection"
    ):
        qwen_medium_stage_note = (
            " Qwen-M has now fully persisted Value Prism Valence, and it has already moved into CCD-Bench; "
            f"the current saved archive there has reached {_checkpoint_task_phrase(qwen_medium_ccd)}."
        )
        qwen_medium_current_coverage = (
            "Earlier text checkpoints withdrawn; UniMoral done; Value Kaleidoscope is fully persisted; "
            f"CCD-Bench holds a {qwen_medium_ccd['progress_pct']:.1f}% persisted checkpoint"
        )
        if qwen_medium_valence is not None and qwen_medium_valence["completed"] > 0:
            qwen_medium_line_suffix = (
                f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}. "
                f"Value Prism Valence is now fully persisted at {_checkpoint_task_phrase(qwen_medium_valence)}. "
                f"The current CCD-Bench archive has also reached {_checkpoint_task_phrase(qwen_medium_ccd)}, and the "
                f"rerun is active again with live Inspect trace writes and recent `200 OK` OpenRouter calls through "
                f"about {trace_phrase}."
            )
            qwen_medium_matrix_summary = (
                f"{_checkpoint_task_phrase(qwen_medium)}. Value Prism Valence is now fully persisted at "
                f"{_checkpoint_task_phrase(qwen_medium_valence)}. The current CCD-Bench archive has also reached "
                f"{_checkpoint_task_phrase(qwen_medium_ccd)}, and the rerun is active again with live Inspect trace "
                f"writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
            )
        else:
            qwen_medium_line_suffix = (
                f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}. "
                f"The current CCD-Bench archive has also reached {_checkpoint_task_phrase(qwen_medium_ccd)}, and the "
                f"rerun is active again with live Inspect trace writes and recent `200 OK` OpenRouter calls through "
                f"about {trace_phrase}."
            )
            qwen_medium_matrix_summary = (
                f"{_checkpoint_task_phrase(qwen_medium)}. The current CCD-Bench archive has also reached "
                f"{_checkpoint_task_phrase(qwen_medium_ccd)}, and the rerun is active again with live Inspect trace "
                f"writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
            )
    if qwen_medium_latest is not None and qwen_medium_latest["task"] == "denevil_fulcra_proxy_generation":
        qwen_medium_stage_note = (
            " Qwen-M has now fully persisted CCD-Bench, and it has already moved into the Denevil proxy task"
        )
        qwen_medium_current_coverage = (
            "Earlier text checkpoints withdrawn; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; "
            "Denevil proxy has started"
        )
        if qwen_medium_denevil is not None and qwen_medium_denevil["completed"] > 0:
            qwen_medium_stage_note = (
                f"{qwen_medium_stage_note}; the current saved archive there has reached "
                f"{_checkpoint_task_phrase(qwen_medium_denevil)}."
            )
            qwen_medium_current_coverage = (
                "Earlier text checkpoints withdrawn; UniMoral done; Value Kaleidoscope and CCD-Bench are fully "
                f"persisted; Denevil proxy holds a {qwen_medium_denevil['progress_pct']:.1f}% persisted checkpoint"
            )
            if qwen_medium_valence is not None and qwen_medium_ccd is not None:
                qwen_medium_line_suffix = (
                    f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}. "
                    f"Value Prism Valence is now fully persisted at {_checkpoint_task_phrase(qwen_medium_valence)}. "
                    f"CCD-Bench is now fully persisted at {_checkpoint_task_phrase(qwen_medium_ccd)}. The current "
                    f"Denevil proxy archive has also reached {_checkpoint_task_phrase(qwen_medium_denevil)}, and the "
                    f"rerun is active again with live Inspect trace writes and recent `200 OK` OpenRouter calls "
                    f"through about {trace_phrase}."
                )
                qwen_medium_matrix_summary = (
                    f"{_checkpoint_task_phrase(qwen_medium)}. Value Prism Valence is now fully persisted at "
                    f"{_checkpoint_task_phrase(qwen_medium_valence)}. CCD-Bench is now fully persisted at "
                    f"{_checkpoint_task_phrase(qwen_medium_ccd)}. The current Denevil proxy archive has also reached "
                    f"{_checkpoint_task_phrase(qwen_medium_denevil)}, and the rerun is active again with live Inspect "
                    f"trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
                )
    if _checkpoint_has_key_limit_error(qwen_medium_denevil):
        qwen_medium_stage_note = (
            f"{qwen_medium_stage_note} The saved Denevil proxy archive then hit an OpenRouter monthly key-limit 403."
        ).strip()
    if qwen_medium_stopped_partial:
        qwen_medium_current_coverage = (
            "Earlier text checkpoints withdrawn; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; "
            "Denevil proxy remains partial after the latest non-success exit"
        )
        qwen_medium_line_suffix = (
            f"The best clean rerun checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_medium)}. "
            "The Denevil proxy rerun preserved partial output on disk, but the latest attempt is currently stopped after "
            "a non-success exit."
        )
        qwen_medium_matrix_summary = (
            f"{_checkpoint_task_phrase(qwen_medium)}. The Denevil proxy rerun preserved partial output on disk, but the "
            "latest attempt is currently stopped after a non-success exit."
        )
    if qwen_large_valence is not None and qwen_large_valence["completed"] > 0:
        qwen_large_stage_note = (
            " Qwen-L has already moved into Value Prism Valence, and the current saved archive has reached "
            f"{_checkpoint_task_phrase(qwen_large_valence)}."
        )
        if qwen_large["completed"] == qwen_large["total"]:
            qwen_large_current_coverage = (
                "SMID recovery stands; UniMoral done; Value Prism Relevance is fully persisted; "
                f"Value Prism Valence holds a {qwen_large_valence['progress_pct']:.1f}% persisted checkpoint"
            )
        else:
            qwen_large_current_coverage = (
                "SMID recovery stands; UniMoral done; the best Value Prism Relevance rerun checkpoint still tops out at "
                f"{qwen_large['progress_pct']:.1f}%; Value Prism Valence holds a "
                f"{qwen_large_valence['progress_pct']:.1f}% persisted checkpoint"
            )
        qwen_large_line_suffix = (
            "The SMID recovery still stands, and the best clean rerun checkpoint on disk still reaches "
            f"{_checkpoint_task_phrase(qwen_large)}. The current Value Prism Valence archive has also reached "
            f"{_checkpoint_task_phrase(qwen_large_valence)}, and the rerun is active again with live Inspect trace "
            f"writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
        )
        qwen_large_matrix_summary = (
            "The SMID recovery remains complete. UniMoral also remains complete, and the best clean rerun checkpoint on "
            f"disk still reaches {_checkpoint_task_phrase(qwen_large)}. The current Value Prism Valence archive has "
            f"also reached {_checkpoint_task_phrase(qwen_large_valence)}. The Value Kaleidoscope rerun is active "
            f"again, with live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
        )
    if (
        qwen_large_ccd is not None
        and qwen_large_ccd["completed"] > 0
        and qwen_large_latest is not None
        and qwen_large_latest["task"] == "ccd_bench_selection"
    ):
        qwen_large_stage_note = (
            " Qwen-L has now fully persisted Value Prism Valence, and it has already moved into CCD-Bench; "
            f"the current saved archive there has reached {_checkpoint_task_phrase(qwen_large_ccd)}."
        )
        qwen_large_current_coverage = (
            "SMID recovery stands; UniMoral done; Value Kaleidoscope is fully persisted; "
            f"CCD-Bench holds a {qwen_large_ccd['progress_pct']:.1f}% persisted checkpoint"
        )
        if qwen_large_valence is not None and qwen_large_valence["completed"] > 0:
            qwen_large_line_suffix = (
                "The SMID recovery still stands, and the best clean rerun checkpoint on disk still reaches "
                f"{_checkpoint_task_phrase(qwen_large)}. Value Prism Valence is now fully persisted at "
                f"{_checkpoint_task_phrase(qwen_large_valence)}. The current CCD-Bench archive has also reached "
                f"{_checkpoint_task_phrase(qwen_large_ccd)}, and the rerun is active again with live Inspect trace "
                f"writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
            )
            qwen_large_matrix_summary = (
                "The SMID recovery remains complete. UniMoral also remains complete, and the best clean rerun "
                f"checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_large)}. Value Prism Valence is now "
                f"fully persisted at {_checkpoint_task_phrase(qwen_large_valence)}. The current CCD-Bench archive has "
                f"also reached {_checkpoint_task_phrase(qwen_large_ccd)}, and the rerun is active again with live "
                f"Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
            )
    if qwen_large_latest is not None and qwen_large_latest["task"] == "denevil_fulcra_proxy_generation":
        qwen_large_stage_note = (
            " Qwen-L has now fully persisted CCD-Bench, and it has already moved into the Denevil proxy task"
        )
        qwen_large_current_coverage = (
            "SMID recovery stands; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; "
            "Denevil proxy has started"
        )
        if qwen_large_denevil is not None and qwen_large_denevil["completed"] > 0:
            qwen_large_stage_note = (
                f"{qwen_large_stage_note}; the current saved archive there has reached "
                f"{_checkpoint_task_phrase(qwen_large_denevil)}."
            )
            qwen_large_current_coverage = (
                "SMID recovery stands; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; "
                f"Denevil proxy holds a {qwen_large_denevil['progress_pct']:.1f}% persisted checkpoint"
            )
            if qwen_large_valence is not None and qwen_large_ccd is not None:
                qwen_large_line_suffix = (
                    "The SMID recovery still stands, and the best clean rerun checkpoint on disk still reaches "
                    f"{_checkpoint_task_phrase(qwen_large)}. Value Prism Valence is now fully persisted at "
                    f"{_checkpoint_task_phrase(qwen_large_valence)}. CCD-Bench is now fully persisted at "
                    f"{_checkpoint_task_phrase(qwen_large_ccd)}. The current Denevil proxy archive has also reached "
                    f"{_checkpoint_task_phrase(qwen_large_denevil)}, and the rerun is active again with live Inspect "
                    f"trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
                )
                qwen_large_matrix_summary = (
                    "The SMID recovery remains complete. UniMoral also remains complete, and the best clean rerun "
                    f"checkpoint on disk still reaches {_checkpoint_task_phrase(qwen_large)}. Value Prism Valence is "
                    f"now fully persisted at {_checkpoint_task_phrase(qwen_large_valence)}. CCD-Bench is now fully "
                    f"persisted at {_checkpoint_task_phrase(qwen_large_ccd)}. The current Denevil proxy archive has "
                    f"also reached {_checkpoint_task_phrase(qwen_large_denevil)}, and the rerun is active again with "
                    f"live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
                )
    if _checkpoint_has_key_limit_error(qwen_large_denevil):
        qwen_large_stage_note = (
            f"{qwen_large_stage_note} The saved Denevil proxy archive then hit an OpenRouter monthly key-limit 403."
        ).strip()
    if qwen_large_stopped_partial:
        qwen_large_current_coverage = (
            "SMID recovery stands; UniMoral done; Value Kaleidoscope and CCD-Bench are fully persisted; Denevil proxy "
            "remains partial after the latest non-success exit"
        )
        qwen_large_line_suffix = (
            "The SMID recovery still stands, and the best clean rerun checkpoint on disk still reaches "
            f"{_checkpoint_task_phrase(qwen_large)}. The Denevil proxy rerun preserved partial output on disk, but the "
            "latest attempt is currently stopped after a non-success exit."
        )
        qwen_large_matrix_summary = (
            "The SMID recovery remains complete. UniMoral also remains complete, and the best clean rerun checkpoint on "
            f"disk still reaches {_checkpoint_task_phrase(qwen_large)}. The Denevil proxy rerun preserved partial "
            "output on disk, but the latest attempt is currently stopped after a non-success exit."
        )
    llama_current_coverage = (
        f"UniMoral done; live rerun holds a {llama_medium['progress_pct']:.1f}% persisted Value Prism Relevance checkpoint"
    )
    llama_line_suffix = (
        f"{_checkpoint_task_phrase(llama_medium).replace(' Value Prism Relevance', '')}, and the rerun is active again "
        f"with live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
    )
    if llama_valence is not None and llama_valence["completed"] > 0:
        llama_stage_note = (
            f" Llama-M has already moved into Value Prism Valence, and the current saved archive has reached "
            f"{_checkpoint_task_phrase(llama_valence)}."
        )
        llama_current_coverage = (
            "UniMoral done; Value Prism Relevance is fully persisted; "
            f"Value Prism Valence holds a {llama_valence['progress_pct']:.1f}% persisted checkpoint"
        )
        llama_line_suffix = (
            f"{_checkpoint_task_phrase(llama_medium).replace(' Value Prism Relevance', '')}. The current Value Prism "
            f"Valence archive has also reached {_checkpoint_task_phrase(llama_valence)}, and the rerun is active again "
            f"with live Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
        )
    if (
        llama_ccd is not None
        and llama_ccd["completed"] > 0
        and llama_latest is not None
        and llama_latest["task"] == "ccd_bench_selection"
    ):
        llama_stage_note = (
            " Llama-M has now fully persisted Value Prism Valence, and it has already moved into CCD-Bench; "
            f"the current saved archive there has reached {_checkpoint_task_phrase(llama_ccd)}."
        )
        llama_current_coverage = (
            "UniMoral done; Value Prism is fully persisted; "
            f"CCD-Bench holds a {llama_ccd['progress_pct']:.1f}% persisted checkpoint"
        )
        if llama_valence is not None and llama_valence["completed"] > 0:
            llama_line_suffix = (
                f"{_checkpoint_task_phrase(llama_medium).replace(' Value Prism Relevance', '')}. Value Prism Valence is "
                f"now fully persisted at {_checkpoint_task_phrase(llama_valence)}. The current CCD-Bench archive has "
                f"also reached {_checkpoint_task_phrase(llama_ccd)}, and the rerun is active again with live Inspect "
                f"trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
            )
        else:
            llama_line_suffix = (
                f"{_checkpoint_task_phrase(llama_medium).replace(' Value Prism Relevance', '')}. The current CCD-Bench "
                f"archive has also reached {_checkpoint_task_phrase(llama_ccd)}, and the rerun is active again with live "
                f"Inspect trace writes and recent `200 OK` OpenRouter calls through about {trace_phrase}."
            )
    if llama_latest is not None and llama_latest["task"] == "denevil_fulcra_proxy_generation":
        llama_stage_note = " Llama-M has now fully persisted CCD-Bench, and it has already moved into the Denevil proxy task"
        llama_current_coverage = "UniMoral done; Value Prism and CCD-Bench are fully persisted; Denevil proxy has started"
        if llama_denevil is not None and llama_denevil["completed"] > 0:
            llama_stage_note = (
                f"{llama_stage_note}; the current saved archive there has reached "
                f"{_checkpoint_task_phrase(llama_denevil)}."
            )
            llama_current_coverage = (
                "UniMoral done; Value Prism and CCD-Bench are fully persisted; "
                f"Denevil proxy holds a {llama_denevil['progress_pct']:.1f}% persisted checkpoint"
            )
            if llama_valence is not None and llama_valence["completed"] > 0 and llama_ccd is not None:
                llama_line_suffix = (
                    f"{_checkpoint_task_phrase(llama_medium).replace(' Value Prism Relevance', '')}. "
                    f"Value Prism Valence is now fully persisted at {_checkpoint_task_phrase(llama_valence)}. "
                    f"CCD-Bench is now fully persisted at {_checkpoint_task_phrase(llama_ccd)}. The current "
                    f"Denevil proxy archive has also reached {_checkpoint_task_phrase(llama_denevil)}, and the rerun "
                    f"is active again with live Inspect trace writes and recent `200 OK` OpenRouter calls through about "
                    f"{trace_phrase}."
                )
        else:
            if llama_denevil is not None:
                llama_stage_note = (
                    f"{llama_stage_note}, which started at "
                    f"{_format_monitor_time_on_date(llama_denevil['mtime'])} but has not written a persisted sample "
                    "checkpoint yet."
                )
            else:
                llama_stage_note = f"{llama_stage_note}, but no persisted sample checkpoint is on disk yet."
            if llama_valence is not None and llama_valence["completed"] > 0 and llama_ccd is not None:
                llama_line_suffix = (
                    f"{_checkpoint_task_phrase(llama_medium).replace(' Value Prism Relevance', '')}. "
                    f"Value Prism Valence is now fully persisted at {_checkpoint_task_phrase(llama_valence)}. "
                    f"CCD-Bench is now fully persisted at {_checkpoint_task_phrase(llama_ccd)}. The Denevil proxy "
                    "task has started, but no persisted sample checkpoint is on disk yet, and the rerun is active "
                    f"again with live Inspect trace writes and recent `200 OK` OpenRouter calls through about "
                    f"{trace_phrase}."
                )

    llama_current_scope = "Live local rerun"
    llama_current_status = "live"
    llama_current_note = "Medium text rerun active; detailed checkpoints are summarized in Snapshot."
    llama_progress_summary = "No SMID run planned; medium text rerun active."
    llama_local_checkpoint_status = "live"
    llama_local_checkpoint_note = "Medium text rerun active; detailed checkpoints are summarized in Snapshot."
    if llama_completed:
        llama_current_scope = "Complete local line"
        llama_current_status = "done"
        llama_current_note = "Completed locally on April 22, 2026."
        llama_current_coverage = "4 benchmark lines plus `Denevil` proxy; no SMID route"
        llama_progress_summary = "No SMID route; medium text line completed locally on April 22, 2026."
        llama_local_checkpoint_status = "done"
        llama_local_checkpoint_note = "Completed April 22 with a full medium text line."

    deepseek_current_coverage = "No vision route; queued behind the live Llama-M rerun."
    deepseek_current_note = "Still queued behind the live Llama-M rerun."
    deepseek_progress_summary = "No vision route; queued behind the live Llama-M rerun."
    deepseek_current_scope = "Live local rerun"
    deepseek_current_status = "live"
    deepseek_local_checkpoint_status = "live"
    if deepseek_launched:
        deepseek_current_note = "Downstream text run active; detailed checkpoints are summarized in Snapshot."
        deepseek_progress_summary = "No vision route; launched after the Llama-M completion."
        deepseek_current_coverage = "No vision route; downstream text run launched after the Llama-M completion"
        if deepseek_unimoral is not None and deepseek_unimoral["status"] != "success":
            deepseek_stage_note = (
                " DeepSeek-M already launched; the first UniMoral attempt ended with "
                f"{_checkpoint_task_phrase(deepseek_unimoral)} and non-success status `{deepseek_unimoral['status']}`."
            )
            deepseek_current_coverage = (
                "No vision route; launched after the Llama-M completion; UniMoral logged a partial interrupted attempt"
            )
            deepseek_progress_summary = (
                "No vision route; launched after the Llama-M completion. The first UniMoral attempt was interrupted."
            )
        if deepseek_latest is not None and deepseek_latest["task"] == "value_prism_relevance":
            if deepseek_value_relevance is not None and deepseek_value_relevance["completed"] > 0:
                deepseek_current_coverage = (
                    "No vision route; launched after the Llama-M completion; Value Prism Relevance holds a "
                    f"{deepseek_value_relevance['progress_pct']:.1f}% persisted checkpoint"
                )
                deepseek_stage_note = (
                    f"{deepseek_stage_note} DeepSeek-M has already moved into Value Prism Relevance, where the current "
                    f"saved archive has reached {_checkpoint_task_phrase(deepseek_value_relevance)}."
                ).strip()
            else:
                deepseek_current_coverage = (
                    f"{deepseek_current_coverage}; Value Prism Relevance is now live"
                )
                deepseek_stage_note = (
                    f"{deepseek_stage_note} DeepSeek-M has already moved into Value Prism Relevance, but no persisted "
                    "sample checkpoint is on disk there yet."
                ).strip()
        if deepseek_job_failed:
            deepseek_current_scope = "Attempted local line"
            deepseek_current_status = "partial"
            deepseek_local_checkpoint_status = "partial"
            if deepseek_credit_exhausted:
                deepseek_current_note = "Downstream attempt is currently blocked because OpenRouter credits are exhausted."
                deepseek_progress_summary = (
                    "No vision route; downstream attempt is currently blocked because OpenRouter credits are exhausted."
                )
                deepseek_current_coverage = (
                    "No vision route; downstream attempt preserved earlier partial checkpoints, but the latest retry stopped immediately on OpenRouter credit exhaustion"
                )
                if deepseek_value_relevance is not None and deepseek_value_relevance["completed"] > 0:
                    deepseek_stage_note = (
                        f"DeepSeek-M preserved {_checkpoint_task_phrase(deepseek_unimoral)} and "
                        f"{_checkpoint_task_phrase(deepseek_value_relevance)} earlier, but the latest retry then stopped immediately with provider `402` because OpenRouter credits are exhausted."
                    )
                else:
                    deepseek_stage_note = (
                        "DeepSeek-M preserved earlier partial checkpoints, but the latest retry then stopped immediately with provider `402` because OpenRouter credits are exhausted."
                    )
            else:
                deepseek_current_note = "Downstream attempt stopped on OpenRouter key-limit failures; partial checkpoints are summarized in Snapshot."
                deepseek_progress_summary = (
                    "No vision route; downstream attempt started after the Llama-M completion but stopped on OpenRouter key-limit failures."
                )
                deepseek_current_coverage = (
                    "No vision route; downstream attempt logged partial UniMoral and Value Prism Relevance checkpoints before OpenRouter key-limit failures"
                )
                if deepseek_value_relevance is not None and deepseek_value_relevance["completed"] > 0:
                    deepseek_stage_note = (
                        f"DeepSeek-M's first downstream attempt wrote {_checkpoint_task_phrase(deepseek_unimoral)} with "
                        f"non-success status `{deepseek_unimoral['status']}` and then reached "
                        f"{_checkpoint_task_phrase(deepseek_value_relevance)} before later tasks hit an OpenRouter monthly key-limit 403."
                    )
                else:
                    deepseek_stage_note = (
                        f"DeepSeek-M's first downstream attempt wrote {_checkpoint_task_phrase(deepseek_unimoral)} with "
                        f"non-success status `{deepseek_unimoral['status']}` and then hit an OpenRouter monthly key-limit 403."
                    )
        elif deepseek_completed:
            deepseek_current_scope = "Complete local line"
            deepseek_current_status = "done"
            deepseek_local_checkpoint_status = "done"
            deepseek_current_coverage = "4 benchmark lines plus `Denevil` proxy; no SMID route"
            deepseek_current_note = "Completed locally on April 22, 2026."
            deepseek_progress_summary = "No SMID route; medium text line completed locally on April 22, 2026."
        elif not deepseek_live_rerun:
            deepseek_current_scope = "Attempted local line"
            deepseek_current_status = "partial"
            deepseek_local_checkpoint_status = "partial"
            deepseek_current_note = (
                "Downstream attempt is currently stalled; partial checkpoints are summarized in Snapshot."
            )
            deepseek_progress_summary = (
                "No vision route; downstream attempt is currently stalled after partial text checkpoints."
            )
            deepseek_current_coverage = (
                "No vision route; downstream attempt preserved partial UniMoral and Value checkpoints, "
                "but no live worker remains"
            )

    minimax_current_scope = "Attempted local line"
    minimax_current_status = "error"
    minimax_current_coverage = "No usable benchmark line completed"
    minimax_current_note = "OpenRouter key-limit failures interrupted both text and image paths."
    minimax_progress_summary = "Attempted, but key-limit failures made the line unusable."
    if minimax_has_rerun and minimax_smid_complete:
        minimax_current_status = "partial"
        if minimax_value_relevance is not None and minimax_value_relevance["completed"] > 0:
            minimax_current_coverage = (
                "SMID is fully persisted; UniMoral is done; Value Prism Relevance holds a "
                f"{minimax_value_relevance['progress_pct']:.1f}% persisted checkpoint"
            )
            minimax_stage_note = (
                "A current MiniMax-S text rerun keeps both SMID tasks complete from the earlier debug pass, "
                f"finishes {_checkpoint_task_phrase(minimax_unimoral)} and has now reached "
                f"{_checkpoint_task_phrase(minimax_value_relevance)}."
            )
            MINIMAX_SMALL_STATUS_SUMMARY = (
                "SMID rerun is now complete locally, and the current text rerun has reached a "
                f"{minimax_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint"
            )
            MINIMAX_SMALL_INTERPRETATION_NOTE = (
                "`MiniMax-S` now has a usable SMID rerun plus a live Value Prism Relevance checkpoint, "
                "but it is still not a complete five-benchmark line."
            )
            MINIMAX_SMALL_GUARDRAIL = (
                "The MiniMax small line now has a usable SMID rerun plus a live Value Prism Relevance checkpoint, "
                "but it is still not a complete five-benchmark line."
            )
        elif minimax_unimoral is not None and minimax_unimoral["completed"] > 0:
            minimax_current_coverage = (
                "SMID is fully persisted; UniMoral holds a "
                f"{minimax_unimoral['progress_pct']:.1f}% persisted checkpoint; later text tasks hit OpenRouter monthly key-limit 403"
            )
            minimax_stage_note = (
                "A separate MiniMax-S rerun debug pass completed both SMID tasks successfully, and its text leg preserved "
                f"{_checkpoint_task_phrase(minimax_unimoral)} before later tasks hit an OpenRouter monthly key-limit 403."
            )
        else:
            minimax_current_coverage = (
                "SMID is fully persisted; later text tasks hit OpenRouter monthly key-limit 403"
            )
            minimax_stage_note = (
                "A separate MiniMax-S rerun debug pass completed both SMID tasks successfully, but its text leg later hit an OpenRouter monthly key-limit 403."
            )
        minimax_current_note = "Fresh rerun produced usable SMID metrics, but the text line is still partial."
        minimax_progress_summary = (
            "SMID rerun complete locally; the text rerun remains partial after UniMoral and later key-limit failures."
        )
        if minimax_value_relevance is None or minimax_value_relevance["completed"] <= 0:
            MINIMAX_SMALL_STATUS_SUMMARY = (
                "SMID rerun is now complete locally, but the text line is still partial after UniMoral and later key-limit failures"
            )
            MINIMAX_SMALL_INTERPRETATION_NOTE = (
                "`MiniMax-S` now has a usable SMID rerun and a partial UniMoral text checkpoint, "
                "but it is still not a complete five-benchmark line."
            )
            MINIMAX_SMALL_GUARDRAIL = (
                "The MiniMax small line now has a usable SMID rerun plus a partial UniMoral text checkpoint, "
                "but it is still not a complete five-benchmark line."
            )

        if minimax_unimoral_invalid:
            empty_pct = minimax_unimoral_guardrail["empty_answer_rate"] * 100
            minimax_current_coverage = (
                "SMID is fully persisted, but the current short-answer text rerun is not yet a clean comparable line: "
                f"{empty_pct:.1f}% of UniMoral scored answers were empty."
            )
            minimax_current_note = (
                "Fresh rerun produced usable SMID metrics, but the short-answer text outputs still need a clean no-thinking retry."
            )
            minimax_progress_summary = (
                "SMID rerun complete locally; the short-answer text rerun still needs a clean no-thinking retry for direct comparison."
            )
            minimax_stage_note = (
                "A current MiniMax-S text rerun keeps both SMID tasks complete from the earlier debug pass and writes "
                f"{_checkpoint_task_phrase(minimax_unimoral)} on disk, but {empty_pct:.1f}% of UniMoral scored answers were empty after the visible answer budget was exhausted."
            )
            MINIMAX_SMALL_STATUS_SUMMARY = (
                "SMID rerun is complete locally, but the current short-answer text rerun still needs a clean no-thinking retry"
            )
            MINIMAX_SMALL_INTERPRETATION_NOTE = (
                "`MiniMax-S` has a usable SMID rerun, but its short-answer text checkpoints are not yet cleanly comparable because most visible answers came back empty."
            )
            MINIMAX_SMALL_GUARDRAIL = (
                "Treat the current MiniMax small text checkpoints as incomplete for direct comparison until a clean no-thinking retry restores visible short answers."
            )
            if minimax_small_reasoning_blocked:
                minimax_current_coverage = (
                    "SMID is fully persisted; the withdrawn short-answer text checkpoints remain excluded, and the "
                    "latest no-thinking retry now fails immediately because the current `minimax-m2.1` endpoint "
                    "requires reasoning."
                )
                minimax_current_note = (
                    "A follow-up no-thinking rerun now fails immediately on the provider because this MiniMax-S endpoint cannot disable reasoning."
                )
                minimax_progress_summary = (
                    "SMID rerun complete locally; clean no-thinking MiniMax-S retry is blocked because the `minimax-m2.1` endpoint requires reasoning."
                )
                minimax_stage_note = (
                    "The earlier MiniMax-S short-answer checkpoint is still withdrawn because "
                    f"{empty_pct:.1f}% of UniMoral scored answers were empty after the visible answer budget was exhausted. "
                    "A follow-up no-thinking rerun on April 26, 2026 then failed immediately across all text tasks with "
                    "provider `400` because the current `minimax-m2.1` endpoint requires reasoning and cannot disable it."
                )
                MINIMAX_SMALL_STATUS_SUMMARY = (
                    "SMID rerun is complete locally, but a clean MiniMax-S text retry is currently blocked because the `minimax-m2.1` endpoint requires reasoning"
                )
                MINIMAX_SMALL_INTERPRETATION_NOTE = (
                    "`MiniMax-S` still relies on the earlier SMID rerun, and the current OpenRouter `minimax-m2.1` route now rejects no-thinking retries before any text samples can run."
                )
                MINIMAX_SMALL_GUARDRAIL = (
                    "Keep the earlier MiniMax small text checkpoints out of direct comparison; a clean retry now needs a different MiniMax-S route or provider path that allows visible short answers without mandatory reasoning."
                )
            if minimax_small_active_rerun:
                minimax_current_scope = "Live local rerun"
                minimax_current_status = "live"
                minimax_current_coverage = (
                    "SMID is fully persisted, and a clean no-thinking text rerun is now active while the earlier "
                    f"withdrawn UniMoral checkpoint remains excluded after {empty_pct:.1f}% empty visible answers."
                )
                minimax_current_note = (
                    "A clean no-thinking text rerun is now live to replace the withdrawn short-answer checkpoints."
                )
                minimax_progress_summary = (
                    "SMID rerun complete locally; clean no-thinking MiniMax-S text rerun is now active."
                )
                minimax_stage_note = (
                    "The earlier MiniMax-S short-answer checkpoint is still withdrawn because "
                    f"{empty_pct:.1f}% of UniMoral scored answers were empty after the visible answer budget was exhausted. "
                    "A fresh no-thinking text rerun is now live in the same MiniMax-S text log directory."
                )
                MINIMAX_SMALL_STATUS_SUMMARY = (
                    "SMID rerun is complete locally, and a clean no-thinking text rerun is now active"
                )
                MINIMAX_SMALL_INTERPRETATION_NOTE = (
                    "`MiniMax-S` still relies on the earlier SMID rerun, and a fresh no-thinking text rerun is now live to replace the withdrawn short-answer checkpoints."
                )
                MINIMAX_SMALL_GUARDRAIL = (
                    "Keep the earlier MiniMax small text checkpoints out of direct comparison until the live no-thinking rerun lands clean visible answers."
                )

    qwen_live_labels: list[str] = []
    if qwen_medium_active_rerun:
        qwen_live_labels.append("Qwen-M")
    if qwen_large_active_rerun:
        qwen_live_labels.append("Qwen-L")
    if len(qwen_live_labels) == 2:
        qwen_live_label_phrase = "Qwen-M and Qwen-L"
    elif qwen_live_labels:
        qwen_live_label_phrase = qwen_live_labels[0]
    else:
        qwen_live_label_phrase = "the Qwen reruns"

    if llama_completed and deepseek_job_failed:
        if qwen_medium_stopped_partial and qwen_large_stopped_partial:
            REPORT_STATUS_NOTE = (
                f"Updated {REPORT_DATE_LONG}. "
                "The frozen public snapshot remains Option 1 from April 19. "
                "Gemma-M and Gemma-L text remain complete locally. "
                "The earlier Qwen-M and Qwen-L text checkpoints were withdrawn from the public comparable snapshot after a "
                "verification pass showed that Qwen-3 reasoning tokens were exhausting the visible output budget on short-answer "
                f"tasks. Llama-M then finished cleanly at {llama_completion_phrase}. The repaired DeepSeek-M handoff watcher "
                f"launched the downstream run at {deepseek_launch_phrase or watcher_phrase}, but that first downstream attempt "
                "stopped on the same OpenRouter monthly key-limit 403. Qwen-M and Qwen-L are no longer live reruns: "
                "both run directories wrote `job_done.txt`, and their final Denevil proxy tasks exited non-success after "
                "preserving partial checkpoints on disk. The best persisted Value Prism "
                f"Relevance checkpoints currently on disk stand at {_checkpoint_summary('Qwen-M', qwen_medium)}, "
                f"{_checkpoint_summary('Qwen-L', qwen_large)}, and {_checkpoint_summary('Llama-M', llama_medium)}."
                f"{_join_optional_note_sentences(qwen_medium_stage_note, qwen_large_stage_note, llama_stage_note, deepseek_stage_note, minimax_stage_note)} "
                "No new downstream line was started in this pass because the OpenRouter monthly key limit is still exhausted."
            )
        else:
            REPORT_STATUS_NOTE = (
                f"Updated {REPORT_DATE_LONG}. "
                "The frozen public snapshot remains Option 1 from April 19. "
                "Gemma-M and Gemma-L text remain complete locally. "
                "The earlier Qwen-M and Qwen-L text checkpoints were withdrawn from the public comparable snapshot after a "
                "verification pass showed that Qwen-3 reasoning tokens were exhausting the visible output budget on short-answer "
                f"tasks. Llama-M then finished cleanly at {llama_completion_phrase}. The repaired DeepSeek-M handoff watcher "
                f"launched the downstream run at {deepseek_launch_phrase or watcher_phrase}, but that first downstream attempt "
                "still stands as failed. The latest live retry evidence now comes from the active open-source reruns: "
                f"{trace_evidence_phrase}. The best persisted Value Prism "
                f"Relevance checkpoints currently on disk stand at {_checkpoint_summary('Qwen-M', qwen_medium)}, "
                f"{_checkpoint_summary('Qwen-L', qwen_large)}, and {_checkpoint_summary('Llama-M', llama_medium)}."
                f"{_join_optional_note_sentences(qwen_medium_stage_note, qwen_large_stage_note, llama_stage_note, deepseek_stage_note, minimax_stage_note)} "
                "Qwen-M was restarted cleanly in the earlier recovery pass, and the remaining downstream queue stays "
                "unchanged while the revived Denevil rerun continues to prove stable."
            )
    elif llama_completed and deepseek_launched:
        REPORT_STATUS_NOTE = (
            f"Updated {REPORT_DATE_LONG}. "
            "The frozen public snapshot remains Option 1 from April 19. "
            "Gemma-M and Gemma-L text remain complete locally. "
            "The earlier Qwen-M and Qwen-L text checkpoints were withdrawn from the public comparable snapshot after a "
            "verification pass showed that Qwen-3 reasoning tokens were exhausting the visible output budget on short-answer "
            f"tasks. Llama-M then finished cleanly at {llama_completion_phrase}. The repaired DeepSeek-M handoff watcher "
            f"launched the downstream run at {deepseek_launch_phrase or watcher_phrase}. The latest live rerun evidence now "
            f"comes from the active open-source reruns: {trace_evidence_phrase}. The best persisted Value Prism Relevance "
            f"checkpoints currently on disk stand at {_checkpoint_summary('Qwen-M', qwen_medium)}, "
            f"{_checkpoint_summary('Qwen-L', qwen_large)}, and {_checkpoint_summary('Llama-M', llama_medium)}."
            f"{_join_optional_note_sentences(qwen_medium_stage_note, qwen_large_stage_note, llama_stage_note, deepseek_stage_note, minimax_stage_note)}"
        )
    else:
        REPORT_STATUS_NOTE = (
            f"Updated {REPORT_DATE_LONG}. "
            "The frozen public snapshot remains Option 1 from April 19. "
            "Gemma-M and Gemma-L text remain complete locally. "
            "The earlier Qwen-M and Qwen-L text checkpoints were withdrawn from the public comparable snapshot after a "
            "verification pass showed that Qwen-3 reasoning tokens were exhausting the visible output budget on short-answer "
            "tasks. The saved master / worker PID markers are still stale, while the repaired DeepSeek-M handoff watcher "
            f"log was still polling through about {watcher_phrase}. The latest live rerun evidence now comes from the active open-source reruns: "
            f"{trace_evidence_phrase}. The best persisted Value Prism Relevance checkpoints currently on disk stand at "
            f"{_checkpoint_summary('Qwen-M', qwen_medium)}, {_checkpoint_summary('Qwen-L', qwen_large)}, and "
            f"{_checkpoint_summary('Llama-M', llama_medium)}."
            f"{_join_optional_note_sentences(qwen_medium_stage_note, qwen_large_stage_note, llama_stage_note, minimax_stage_note)} "
            "No new downstream launch was started in this pass because "
            "Llama-M has not written a clean completion marker yet; DeepSeek-M remains queued behind the Llama-M text batch."
        )

    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Qwen-M text batch")["status"] = qwen_medium_local_checkpoint_status
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Qwen-M text batch")["note"] = (
        qwen_medium_local_checkpoint_note
    )
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Qwen-L text batch")["status"] = qwen_large_local_checkpoint_status
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Qwen-L text batch")["note"] = (
        qwen_large_local_checkpoint_note
    )
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Llama-M text batch")["status"] = llama_local_checkpoint_status
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Llama-M text batch")["note"] = (
        llama_local_checkpoint_note
    )
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "DeepSeek-M text batch")["status"] = (
        deepseek_local_checkpoint_status if deepseek_launched else "prep"
    )
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "DeepSeek-M text batch")["note"] = (
        deepseek_current_note
    )
    active_text_labels: list[str] = []
    if qwen_large_active_rerun:
        active_text_labels.append("Qwen-L")
    if llama_large_active_rerun:
        active_text_labels.append("Llama-L")
    if minimax_medium_active_rerun:
        active_text_labels.append("MiniMax-M")
    if deepseek_live_rerun:
        active_text_labels.append("DeepSeek-M")
    if len(active_text_labels) > 1:
        active_text_phrase = ", ".join(active_text_labels[:-1]) + ", and " + active_text_labels[-1]
    elif active_text_labels:
        active_text_phrase = active_text_labels[0]
    else:
        active_text_phrase = ""
    if active_text_labels and (llama_large_active_rerun or minimax_medium_active_rerun):
        next_queued_note = (
            f"MiniMax-L remains queued next while {active_text_phrase} are currently in flight."
            if len(active_text_labels) > 1
            else f"MiniMax-L remains queued next while {active_text_phrase} is currently in flight."
        )
        if deepseek_launched and not deepseek_live_rerun:
            next_queued_note += " DeepSeek-M still has a stale running marker but no live worker."
        if minimax_large_value_relevance is not None and not minimax_large_active_rerun:
            next_queued_note += (
                " MiniMax-L is the next restart candidate; its last partial checkpoint reached "
                f"{minimax_large_value_relevance['progress_pct']:.1f}% of Value Prism Relevance."
            )
    elif deepseek_job_failed:
        next_queued_note = (
            "Llama-L, MiniMax-M, and MiniMax-L remain queued while Qwen-M is back in flight; "
            "Qwen-L, DeepSeek-M, and MiniMax-S still need fresh retries."
            if qwen_medium_active_rerun
            else "Llama-L, MiniMax-M, and MiniMax-L remain queued while DeepSeek-M, Qwen-M, Qwen-L, and "
            "MiniMax-S all need fresh retries after the OpenRouter limit resets."
        )
    elif deepseek_launched:
        next_queued_note = "Llama-L, MiniMax-M, and MiniMax-L are waiting on the active Qwen and DeepSeek reruns."
    else:
        next_queued_note = "Llama-L, MiniMax-M, and MiniMax-L are waiting on the live reruns."
    _find_row(LOCAL_EXPANSION_CHECKPOINT, "line", "Next queued text lines")["note"] = (
        next_queued_note
    )

    qwen_medium_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "Qwen-M")
    if qwen_medium_valence is not None and qwen_medium_valence["status"] == "success":
        qwen_medium_progress["value_kaleidoscope"] = "done"
    if qwen_medium_ccd is not None and qwen_medium_ccd["completed"] > 0:
        qwen_medium_progress["ccd_bench"] = "done" if qwen_medium_ccd["status"] == "success" else "partial"
    if qwen_medium_latest is not None and qwen_medium_latest["task"] == "denevil_fulcra_proxy_generation":
        if qwen_medium_denevil and qwen_medium_denevil["status"] == "success":
            qwen_medium_progress["denevil"] = "proxy"
        elif qwen_medium_stopped_partial:
            qwen_medium_progress["denevil"] = "partial"
        else:
            qwen_medium_progress["denevil"] = "live"
    qwen_medium_progress["summary_note"] = qwen_medium_progress_summary
    qwen_large_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "Qwen-L")
    if qwen_large_valence is not None and qwen_large_valence["status"] == "success":
        qwen_large_progress["value_kaleidoscope"] = "done"
    if qwen_large_ccd is not None and qwen_large_ccd["completed"] > 0:
        qwen_large_progress["ccd_bench"] = "done" if qwen_large_ccd["status"] == "success" else "partial"
    if qwen_large_latest is not None and qwen_large_latest["task"] == "denevil_fulcra_proxy_generation":
        if qwen_large_denevil and qwen_large_denevil["status"] == "success":
            qwen_large_progress["denevil"] = "proxy"
        elif qwen_large_stopped_partial:
            qwen_large_progress["denevil"] = "partial"
        else:
            qwen_large_progress["denevil"] = "live"
    qwen_large_progress["summary_note"] = qwen_large_progress_summary
    llama_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "Llama-M")
    if llama_valence is not None and llama_valence["status"] == "success":
        llama_progress["value_kaleidoscope"] = "done"
    if llama_ccd is not None and llama_ccd["completed"] > 0:
        llama_progress["ccd_bench"] = "done" if llama_ccd["status"] == "success" else "live"
    if llama_latest is not None and llama_latest["task"] == "denevil_fulcra_proxy_generation":
        llama_progress["denevil"] = "proxy" if (llama_denevil and llama_denevil["status"] == "success") else "live"
    llama_progress["summary_note"] = llama_progress_summary
    deepseek_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "DeepSeek-M")
    if deepseek_launched:
        if deepseek_completed:
            if deepseek_unimoral is not None:
                deepseek_progress["unimoral"] = "done"
            if deepseek_value_relevance is not None or deepseek_value_valence is not None:
                deepseek_progress["value_kaleidoscope"] = "done"
            if deepseek_ccd is not None and deepseek_ccd["completed"] > 0:
                deepseek_progress["ccd_bench"] = "done"
            if deepseek_denevil is not None and deepseek_denevil["completed"] > 0:
                deepseek_progress["denevil"] = "proxy" if deepseek_denevil["status"] == "success" else "partial"
        elif deepseek_job_failed or not deepseek_live_rerun:
            if deepseek_unimoral is not None:
                if deepseek_unimoral["status"] == "success" and deepseek_unimoral["completed"] == deepseek_unimoral["total"]:
                    deepseek_progress["unimoral"] = "done"
                else:
                    deepseek_progress["unimoral"] = "partial" if deepseek_unimoral["completed"] > 0 else "error"
            if deepseek_value_relevance is not None or deepseek_value_valence is not None:
                deepseek_value_completed = 0
                if deepseek_value_relevance is not None:
                    deepseek_value_completed = max(deepseek_value_completed, int(deepseek_value_relevance["completed"]))
                if deepseek_value_valence is not None:
                    deepseek_value_completed = max(deepseek_value_completed, int(deepseek_value_valence["completed"]))
                deepseek_progress["value_kaleidoscope"] = "partial" if deepseek_value_completed > 0 else "error"
            if deepseek_ccd is not None:
                deepseek_progress["ccd_bench"] = "partial" if deepseek_ccd["completed"] > 0 else "error"
            if deepseek_denevil is not None:
                deepseek_progress["denevil"] = "proxy" if deepseek_denevil["status"] == "success" else (
                    "partial" if deepseek_denevil["completed"] > 0 else "error"
                )
        else:
            if deepseek_unimoral is not None:
                if deepseek_unimoral["status"] == "success" and deepseek_unimoral["completed"] == deepseek_unimoral["total"]:
                    deepseek_progress["unimoral"] = "done"
                elif deepseek_unimoral["status"] == "error":
                    deepseek_progress["unimoral"] = "partial" if deepseek_unimoral["completed"] > 0 else "error"
                else:
                    deepseek_progress["unimoral"] = "live"
            if deepseek_value_valence is not None and deepseek_value_valence["status"] == "success":
                deepseek_progress["value_kaleidoscope"] = "done"
            elif deepseek_value_relevance is not None or (
                deepseek_latest is not None and deepseek_latest["task"] in {"value_prism_relevance", "value_prism_valence"}
            ):
                deepseek_progress["value_kaleidoscope"] = "live"
            if deepseek_ccd is not None and deepseek_ccd["completed"] > 0:
                deepseek_progress["ccd_bench"] = "done" if deepseek_ccd["status"] == "success" else "live"
            if deepseek_latest is not None and deepseek_latest["task"] == "denevil_fulcra_proxy_generation":
                deepseek_progress["denevil"] = "proxy" if (deepseek_denevil and deepseek_denevil["status"] == "success") else "live"
    deepseek_progress["summary_note"] = deepseek_progress_summary

    llama_large_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "Llama-L")
    if llama_large_unimoral is not None:
        llama_large_progress["unimoral"] = (
            "done"
            if llama_large_unimoral["status"] == "success" and llama_large_unimoral["completed"] == llama_large_unimoral["total"]
            else "partial"
            if llama_large_unimoral["completed"] > 0
            else "error"
        )
    if llama_large_active_rerun and llama_large_latest is not None and llama_large_latest["task"] in {"value_prism_relevance", "value_prism_valence"}:
        llama_large_progress["value_kaleidoscope"] = "live"
    elif llama_large_value_valence is not None and llama_large_value_valence["status"] == "success":
        llama_large_progress["value_kaleidoscope"] = "done"
    elif llama_large_value_relevance is not None or llama_large_value_valence is not None:
        llama_large_value_completed = max(
            int(llama_large_value_relevance["completed"]) if llama_large_value_relevance is not None else 0,
            int(llama_large_value_valence["completed"]) if llama_large_value_valence is not None else 0,
        )
        llama_large_progress["value_kaleidoscope"] = "partial" if llama_large_value_completed > 0 else "error"
    if llama_large_ccd is not None and llama_large_ccd["completed"] > 0:
        llama_large_progress["ccd_bench"] = "done" if llama_large_ccd["status"] == "success" else "partial"
    if llama_large_denevil is not None and llama_large_denevil["completed"] > 0:
        llama_large_progress["denevil"] = "proxy" if llama_large_denevil["status"] == "success" else "partial"
    if llama_large_active_rerun and llama_large_value_relevance is not None and llama_large_value_relevance["completed"] > 0:
        llama_large_progress["summary_note"] = (
            "SMID complete; current text rerun active with a "
            f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
        )
    elif llama_large_active_rerun:
        llama_large_progress["summary_note"] = "SMID complete; current text rerun active."
    elif llama_large_credit_exhausted and llama_large_value_relevance is not None and llama_large_value_relevance["completed"] > 0:
        llama_large_progress["summary_note"] = (
            "SMID complete; text rerun is paused because OpenRouter credits are exhausted after a "
            f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
        )
    elif llama_large_denevil is not None and llama_large_denevil["completed"] > 0:
        llama_large_progress["summary_note"] = "SMID complete; earlier text attempt reached the Denevil proxy task."
    elif llama_large_ccd is not None and llama_large_ccd["completed"] > 0:
        llama_large_progress["summary_note"] = "SMID complete; earlier text attempt reached CCD-Bench."
    elif llama_large_unimoral is not None and llama_large_unimoral["completed"] > 0:
        llama_large_progress["summary_note"] = "SMID complete; UniMoral is already persisted locally."

    minimax_medium_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "MiniMax-M")
    if minimax_medium_active_rerun and minimax_medium_latest is not None and minimax_medium_latest["task"] == "unimoral_action_prediction":
        minimax_medium_progress["unimoral"] = "live"
    elif minimax_medium_unimoral is not None:
        minimax_medium_progress["unimoral"] = (
            "done"
            if minimax_medium_unimoral["status"] == "success" and minimax_medium_unimoral["completed"] == minimax_medium_unimoral["total"]
            else "partial"
            if minimax_medium_unimoral["completed"] > 0
            else "error"
        )
    if minimax_medium_active_rerun:
        minimax_medium_progress["summary_note"] = "Text rerun active; no medium SMID route fixed yet."
    elif minimax_medium_unimoral is not None and minimax_medium_unimoral["completed"] > 0:
        minimax_medium_progress["summary_note"] = (
            "Partial text checkpoint exists locally; no medium SMID route fixed yet."
        )

    minimax_large_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "MiniMax-L")
    if minimax_large_unimoral is not None:
        minimax_large_progress["unimoral"] = (
            "done"
            if minimax_large_unimoral["status"] == "success" and minimax_large_unimoral["completed"] == minimax_large_unimoral["total"]
            else "partial"
            if minimax_large_unimoral["completed"] > 0
            else "error"
        )
    if minimax_large_active_rerun and minimax_large_latest is not None and minimax_large_latest["task"] == "value_prism_relevance":
        minimax_large_progress["value_kaleidoscope"] = "live"
    elif minimax_large_value_relevance is not None:
        minimax_large_progress["value_kaleidoscope"] = (
            "done"
            if minimax_large_value_relevance["status"] == "success"
            and minimax_large_value_relevance["completed"] == minimax_large_value_relevance["total"]
            else "partial"
            if minimax_large_value_relevance["completed"] > 0
            else "error"
        )
    if minimax_large_active_rerun:
        minimax_large_progress["summary_note"] = "Large text rerun active; no large SMID route fixed yet."
    elif minimax_large_value_relevance is not None and minimax_large_value_relevance["completed"] > 0:
        minimax_large_progress["summary_note"] = (
            "UniMoral done locally; stalled after a "
            f"{minimax_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint. "
            "No large SMID route fixed yet."
        )
    elif minimax_large_unimoral is not None and minimax_large_unimoral["completed"] > 0:
        minimax_large_progress["summary_note"] = (
            "UniMoral is complete locally, but the large text rerun is not currently active."
        )

    minimax_progress = _find_row(FAMILY_SIZE_PROGRESS, "line_label", "MiniMax-S")
    if minimax_smid_complete:
        minimax_progress["smid"] = "done"
    if minimax_unimoral is not None:
        minimax_progress["unimoral"] = (
            "done"
            if minimax_unimoral["status"] == "success" and minimax_unimoral["completed"] == minimax_unimoral["total"]
            else "partial"
            if minimax_unimoral["completed"] > 0
            else "error"
        )
    if minimax_value_relevance is not None or minimax_value_valence is not None:
        minimax_value_completed = max(
            int(minimax_value_relevance["completed"]) if minimax_value_relevance is not None else 0,
            int(minimax_value_valence["completed"]) if minimax_value_valence is not None else 0,
        )
        minimax_progress["value_kaleidoscope"] = "partial" if minimax_value_completed > 0 else "error"
    if minimax_ccd is not None:
        minimax_progress["ccd_bench"] = "partial" if minimax_ccd["completed"] > 0 else "error"
    if minimax_denevil is not None:
        minimax_progress["denevil"] = "partial" if minimax_denevil["completed"] > 0 else "error"
    minimax_progress["summary_note"] = minimax_progress_summary

    qwen_medium_current = _find_row(CURRENT_RESULT_LINES, "line_label", "Qwen-M")
    qwen_medium_current["scope"] = qwen_medium_current_scope
    qwen_medium_current["status"] = qwen_medium_current_status
    qwen_medium_current["coverage"] = qwen_medium_current_coverage
    qwen_medium_current["note"] = qwen_medium_current_note

    qwen_large_current = _find_row(CURRENT_RESULT_LINES, "line_label", "Qwen-L")
    qwen_large_current["scope"] = qwen_large_current_scope
    qwen_large_current["status"] = qwen_large_current_status
    qwen_large_current["coverage"] = qwen_large_current_coverage
    qwen_large_current["note"] = qwen_large_current_note

    llama_medium_current = _find_row(CURRENT_RESULT_LINES, "line_label", "Llama-M")
    llama_medium_current["scope"] = llama_current_scope
    llama_medium_current["status"] = llama_current_status
    llama_medium_current["coverage"] = llama_current_coverage
    llama_medium_current["note"] = llama_current_note

    llama_large_note = "SMID complete; current text rerun active."
    llama_large_coverage = "SMID complete; text rerun active."
    if llama_large_unimoral is not None and llama_large_unimoral["status"] == "success":
        llama_large_coverage = "SMID complete; UniMoral done; text rerun active."
    if llama_large_active_rerun and llama_large_value_relevance is not None and llama_large_value_relevance["completed"] > 0:
        llama_large_note = (
            "SMID complete; current text rerun active with a "
            f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
        )
        llama_large_coverage = (
            "SMID complete; UniMoral done; Value Prism Relevance holds a "
            f"{llama_large_value_relevance['progress_pct']:.1f}% persisted checkpoint."
        )
    elif llama_large_value_relevance is not None and llama_large_value_relevance["completed"] > 0:
        if llama_large_credit_exhausted:
            llama_large_note = (
                "SMID complete; text rerun is paused because OpenRouter credits are exhausted after a "
                f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
            )
        else:
            llama_large_note = (
                "SMID complete; earlier text attempt stalled after a "
                f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
            )
        llama_large_coverage = (
            "SMID complete; UniMoral done; Value Prism Relevance preserved a "
            f"{llama_large_value_relevance['progress_pct']:.1f}% checkpoint before the run stalled."
        )
    elif llama_large_denevil is not None and llama_large_denevil["completed"] > 0:
        llama_large_note = "SMID complete; earlier text attempt reached the Denevil proxy task."
        llama_large_coverage = (
            "SMID complete; earlier text attempt reached a "
            f"{llama_large_denevil['progress_pct']:.1f}% Denevil proxy checkpoint."
        )
    elif llama_large_unimoral is not None and llama_large_unimoral["completed"] > 0:
        llama_large_note = "SMID complete; UniMoral is already persisted, but later text tasks are still incomplete."
        llama_large_coverage = "SMID complete; UniMoral done; later text tasks remain incomplete."
    if llama_large_active_rerun or llama_large_unimoral is not None or llama_large_denevil is not None:
        _upsert_current_result_line(
            {
                "line_label": "Llama-L",
                "scope": "Live local rerun" if llama_large_active_rerun else "Attempted local line",
                "status": "live" if llama_large_active_rerun else "partial",
                "coverage": llama_large_coverage,
                "note": llama_large_note,
            },
            before_label="MiniMax-S",
        )

    if minimax_medium_active_rerun or minimax_medium_unimoral is not None:
        minimax_medium_coverage = "No medium SMID route fixed yet; text rerun active on UniMoral."
        minimax_medium_note = "Text rerun active; the first UniMoral chunk has not flushed yet."
        if minimax_medium_unimoral is not None and minimax_medium_unimoral["completed"] > 0:
            minimax_medium_coverage = (
                "No medium SMID route fixed yet; UniMoral holds a "
                f"{minimax_medium_unimoral['progress_pct']:.1f}% persisted checkpoint."
            )
            minimax_medium_note = (
                "Text rerun active; UniMoral has already persisted a "
                f"{minimax_medium_unimoral['progress_pct']:.1f}% checkpoint."
            )
        _upsert_current_result_line(
            {
                "line_label": "MiniMax-M",
                "scope": "Live local rerun" if minimax_medium_active_rerun else "Attempted local line",
                "status": "live" if minimax_medium_active_rerun else "partial",
                "coverage": minimax_medium_coverage,
                "note": minimax_medium_note,
            },
            before_label="MiniMax-S",
        )

    if deepseek_launched:
        _upsert_current_result_line(
            {
                "line_label": "DeepSeek-M",
                "scope": deepseek_current_scope,
                "status": deepseek_current_status,
                "coverage": deepseek_current_coverage,
                "note": deepseek_current_note,
            },
            before_label="MiniMax-S",
        )

    for comparison_row in LOCAL_COMPARISON_LINE_SOURCES:
        if comparison_row.get("line_label") != "Llama-L":
            continue
        if llama_large_active_rerun and llama_large_value_relevance is not None and llama_large_value_relevance["completed"] > 0:
            comparison_row["coverage_note"] = (
                "SMID is complete locally, and the restarted text rerun now holds a "
                f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
            )
        elif llama_large_active_rerun:
            comparison_row["coverage_note"] = (
                "SMID is complete locally, and the matching text rerun is back in flight."
            )
        elif llama_large_denevil is not None and llama_large_denevil["completed"] > 0:
            comparison_row["coverage_note"] = (
                "SMID is complete locally, and the latest text attempt later reached a "
                f"{llama_large_denevil['progress_pct']:.1f}% Denevil proxy checkpoint before stalling."
            )
        elif llama_large_value_relevance is not None and llama_large_value_relevance["completed"] > 0:
            if llama_large_credit_exhausted:
                comparison_row["coverage_note"] = (
                    "SMID is complete locally, but the latest text retry is paused because OpenRouter credits are exhausted after a "
                    f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
                )
            else:
                comparison_row["coverage_note"] = (
                    "SMID is complete locally, and the latest text attempt stalled after a "
                    f"{llama_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
                )
        elif llama_large_unimoral is not None and llama_large_unimoral["completed"] > 0:
            comparison_row["coverage_note"] = (
                "SMID is complete locally, and UniMoral is already persisted while the later text tasks remain incomplete."
            )
        break

    for comparison_row in LOCAL_COMPARISON_LINE_SOURCES:
        if comparison_row.get("line_label") != "MiniMax-S":
            continue
        if minimax_small_reasoning_blocked:
            comparison_row["coverage_note"] = (
                f"{comparison_row['coverage_note']} A follow-up no-thinking retry on April 26, 2026 failed immediately because the current `minimax-m2.1` endpoint requires reasoning and cannot disable it."
            )
        elif minimax_small_active_rerun:
            comparison_row["coverage_note"] = (
                f"{comparison_row['coverage_note']} A clean no-thinking text rerun is now active."
            )
        break

    minimax_current = _find_row(CURRENT_RESULT_LINES, "line_label", "MiniMax-S")
    minimax_current["scope"] = minimax_current_scope
    minimax_current["status"] = minimax_current_status
    minimax_current["coverage"] = minimax_current_coverage
    minimax_current["note"] = minimax_current_note

    def live_checkpoint_highlight(label: str, checkpoint: dict[str, Any] | None) -> str:
        if checkpoint is None:
            return f"`{label}` with live rerun traces but no persisted checkpoint yet"
        task_label = _task_display_name(str(checkpoint.get("task", ""))).strip()
        return (
            f"`{label}` on {task_label} "
            f"{_format_samples(checkpoint['completed'])} / {_format_samples(checkpoint['total'])} "
            f"({checkpoint['progress_pct']:.1f}%)"
        )

    REPORT_LIVE_RERUNS_SUMMARY = (
        _human_join([f"`{label}`" for label in active_text_labels])
        if active_text_labels
        else "No tracked open-source rerun was live at build time."
    )
    if minimax_large_value_relevance is not None and not minimax_large_active_rerun:
        REPORT_NEXT_ACTION_SUMMARY = (
            "Restart `MiniMax-L` next from its "
            f"{minimax_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint."
        )
    elif deepseek_launched and not deepseek_live_rerun:
        REPORT_NEXT_ACTION_SUMMARY = "Revisit stalled `DeepSeek-M` text work after the active reruns free a slot."
    elif active_text_labels:
        REPORT_NEXT_ACTION_SUMMARY = "Keep the active reruns healthy, then relaunch the next queued incomplete line."
    else:
        REPORT_NEXT_ACTION_SUMMARY = "Relaunch the next incomplete queued open-source line."
    REPORT_RELEASE_GUARDRAIL_SUMMARY = (
        "Qwen and MiniMax short-answer checkpoints stay out of the comparable snapshot until clean no-thinking reruns are verified, and `Denevil` remains proxy-only in public tables."
    )

    active_progress_items: list[str] = []
    if qwen_large_active_rerun:
        active_progress_items.append(live_checkpoint_highlight("Qwen-L", qwen_large_denevil or qwen_large_latest))
    if llama_large_active_rerun:
        active_progress_items.append(
            live_checkpoint_highlight("Llama-L", llama_large_value_relevance or llama_large_latest)
        )
    if minimax_medium_active_rerun:
        active_progress_items.append(
            live_checkpoint_highlight("MiniMax-M", minimax_medium_unimoral or minimax_medium_latest)
        )
    if deepseek_live_rerun:
        active_progress_items.append(live_checkpoint_highlight("DeepSeek-M", deepseek_latest))

    stalled_items: list[str] = []
    if deepseek_launched and not deepseek_live_rerun:
        stalled_items.append("`DeepSeek-M` preserved partial UniMoral and Value checkpoints but no live worker remains")
    if minimax_large_value_relevance is not None and not minimax_large_active_rerun:
        stalled_items.append(
            "`MiniMax-L` is the next restart candidate after a "
            f"{minimax_large_value_relevance['progress_pct']:.1f}% Value Prism Relevance checkpoint"
        )

    completed_local_labels = [
        f"`{row['line_label']}`"
        for row in CURRENT_RESULT_LINES
        if row["scope"] == "Complete local line"
    ]
    completed_local_summary = (
        _human_join(completed_local_labels)
        if completed_local_labels
        else "No extra local line is complete outside the frozen release."
    )

    REPORT_STATUS_HIGHLIGHTS = [
        (
            f"Active open-source reruns: {_human_join(active_progress_items)}."
            if active_progress_items
            else "Active open-source reruns: none were live at build time."
        ),
        (
            f"Stalled or queued follow-up work: {'; '.join(stalled_items)}."
            if stalled_items
            else f"Queued follow-up work: {REPORT_NEXT_ACTION_SUMMARY}"
        ),
        f"Complete local lines beyond the frozen `Option 1` slice: {completed_local_summary}.",
        f"Release guardrails: {REPORT_RELEASE_GUARDRAIL_SUMMARY}",
    ]

    minimax_supplementary = next(
        row for row in SUPPLEMENTARY_MODEL_PROGRESS if row["family"] == "MiniMax"
    )
    if minimax_smid_complete:
        minimax_supplementary.update(
            {
                "status_relative_to_closed_release": "Partial local rerun with SMID complete and text still interrupted",
                "papers_covered": 1,
                "tasks_completed": 2,
                "benchmark_faithful_tasks": 2,
                "proxy_tasks": 0,
                "samples": 5882,
                "benchmark_faithful_macro_accuracy": mean(
                    [
                        float(minimax_smid_moral["accuracy"]),
                        float(minimax_smid_foundation["accuracy"]),
                    ]
                ),
                "completed_benchmark_lines": "SMID",
                "missing_benchmark_lines": "UniMoral; Value Kaleidoscope; CCD-Bench; Denevil proxy; Benchmark-faithful Denevil via MoralPrompt",
                "note": "Fresh small rerun completed both SMID tasks successfully and preserved a partial UniMoral checkpoint before later text tasks hit OpenRouter key-limit 403.",
            }
        )


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


def filter_public_family_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("family") not in PUBLIC_WITHHELD_FAMILIES]


def filter_public_line_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("line_label") not in PUBLIC_WITHHELD_LINES]


def public_current_result_lines() -> list[dict[str, Any]]:
    return filter_public_line_rows(CURRENT_RESULT_LINES)


def public_local_expansion_checkpoint_rows() -> list[dict[str, Any]]:
    rows = [dict(row) for row in LOCAL_EXPANSION_CHECKPOINT]
    for row in rows:
        if row.get("line") == "Next queued text lines":
            row["note"] = PUBLIC_NEXT_QUEUED_NOTE
    return rows


def ordered_present_families(rows: list[dict[str, Any]]) -> list[str]:
    present = {row["family"] for row in rows}
    return [family for family in FULL_MODEL_FAMILY_ORDER if family in present]


def public_family_summary(rows: list[dict[str, Any]]) -> tuple[list[str], str, int]:
    families = ordered_present_families(rows)
    quoted = ", ".join(f"`{family}`" for family in families)
    return families, quoted, len(families)


def _public_line_summary(label: str, note: str) -> str:
    return f"`{label}` ({note.rstrip('.')})"


def _refresh_public_release_summaries() -> None:
    global MINIMAX_SMALL_GUARDRAIL
    global MINIMAX_SMALL_INTERPRETATION_NOTE
    global MINIMAX_SMALL_STATUS_SUMMARY
    global PUBLIC_NEXT_QUEUED_NOTE
    global REPORT_LIVE_RERUNS_SUMMARY
    global REPORT_NEXT_ACTION_SUMMARY
    global REPORT_RELEASE_GUARDRAIL_SUMMARY
    global REPORT_STATUS_HIGHLIGHTS
    global REPORT_STATUS_NOTE

    public_current = public_current_result_lines()
    live_rows = [row for row in public_current if row["status"] == "live"]
    partial_rows = [row for row in public_current if row["status"] == "partial"]
    credit_blocked_rows = [row for row in partial_rows if "credits are exhausted" in row["note"].lower()]
    completed_local_labels = [
        f"`{row['line_label']}`" for row in public_current if row["scope"] == "Complete local line"
    ]
    live_summary_items = [_public_line_summary(row["line_label"], row["note"]) for row in live_rows]
    partial_summary_items = [_public_line_summary(row["line_label"], row["note"]) for row in partial_rows]

    if live_summary_items:
        REPORT_LIVE_RERUNS_SUMMARY = _human_join([f"`{row['line_label']}`" for row in live_rows])
        active_highlight = f"Active open-source reruns: {_human_join(live_summary_items)}."
    else:
        REPORT_LIVE_RERUNS_SUMMARY = "No currently published line is still running locally."
        active_highlight = "Active open-source reruns: none are currently shown in the published matrix."

    if partial_summary_items:
        stalled_highlight = f"Stalled or queued follow-up work: {_human_join(partial_summary_items)}."
        first_partial = partial_rows[0]["line_label"]
        if credit_blocked_rows:
            blocked_label = credit_blocked_rows[0]["line_label"]
            REPORT_NEXT_ACTION_SUMMARY = f"Add OpenRouter credits, then relaunch `{blocked_label}`."
        else:
            REPORT_NEXT_ACTION_SUMMARY = (
                f"Keep the active published reruns healthy, then revisit `{first_partial}`."
                if live_rows
                else f"Revisit `{first_partial}` next."
            )
    else:
        stalled_highlight = "Stalled or queued follow-up work: no published partial line is waiting right now."
        REPORT_NEXT_ACTION_SUMMARY = (
            "Keep the active published reruns healthy."
            if live_rows
            else "No published rerun is active right now."
        )

    REPORT_RELEASE_GUARDRAIL_SUMMARY = (
        "Public tables only show lines with trustworthy comparable outputs, and `Denevil` remains proxy-only in public tables."
    )
    REPORT_STATUS_HIGHLIGHTS = [
        active_highlight,
        stalled_highlight,
        (
            f"Complete local lines beyond the frozen `Option 1` slice: {_human_join(completed_local_labels)}."
            if completed_local_labels
            else "Complete local lines beyond the frozen `Option 1` slice: none are currently published."
        ),
        f"Release guardrails: {REPORT_RELEASE_GUARDRAIL_SUMMARY}",
    ]
    next_public_label = partial_rows[0]["line_label"] if partial_rows else "DeepSeek-M"
    PUBLIC_NEXT_QUEUED_NOTE = (
        f"Keep the current published reruns healthy while `{next_public_label}` remains the next visible follow-up."
        if live_rows
        else f"`{next_public_label}` remains the next visible follow-up."
    )
    MINIMAX_SMALL_STATUS_SUMMARY = ""
    MINIMAX_SMALL_INTERPRETATION_NOTE = ""
    MINIMAX_SMALL_GUARDRAIL = ""
    REPORT_STATUS_NOTE = (
        f"Updated {REPORT_DATE_LONG}. "
        "The frozen public snapshot remains Option 1 from April 19. "
        "Qwen-M, Qwen-L, Gemma-M, Gemma-L, and Llama-M are complete locally beyond the frozen slice, "
        "Llama-L and DeepSeek-M remain the two incomplete published follow-up lines."
    )


def summarize_family_size_progress(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        counts = {
            "done": 0,
            "proxy": 0,
            "partial": 0,
            "live": 0,
            "error": 0,
            "pending": 0,
        }
        for column in FAMILY_SIZE_STATUS_COLUMNS:
            status = row[column]
            if status == "done":
                counts["done"] += 1
            elif status == "proxy":
                counts["proxy"] += 1
            elif status == "partial":
                counts["partial"] += 1
            elif status == "live":
                counts["live"] += 1
            elif status == "error":
                counts["error"] += 1
            else:
                counts["pending"] += 1

        output.append(
            {
                "family": row["family"],
                "line_label": row["line_label"],
                **counts,
                "usable_now": counts["done"] + counts["proxy"],
            }
        )
    return output


def append_local_expansion_checkpoint_table(lines: list[str]) -> None:
    lines.extend(
        [
            "| Line or batch | Status | Note |",
            "| --- | --- | --- |",
        ]
    )
    for row in public_local_expansion_checkpoint_rows():
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


def mean_if_all_present(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if len(present) != len(values):
        return None
    return mean(present) if present else None


def parse_eval_artifact(eval_path: Path) -> dict[str, Any] | None:
    try:
        with ZipFile(eval_path) as zf:
            members = zf.namelist()
            if "header.json" not in members:
                return None
            header = json.loads(zf.read("header.json").decode("utf-8"))
            start = json.loads(zf.read("_journal/start.json").decode("utf-8")) if "_journal/start.json" in members else {}
    except (BadZipFile, json.JSONDecodeError, KeyError):
        return None

    if not isinstance(header, dict) or header.get("status") != "success":
        return None

    base = header or start
    eval_meta = base.get("eval", {}) if isinstance(base, dict) else {}
    results = header.get("results", {}) if isinstance(header, dict) else {}
    scores = results.get("scores", []) if isinstance(results, dict) else []
    metrics = scores[0].get("metrics", {}) if scores else {}
    accuracy_metric = metrics.get("accuracy", {}) if isinstance(metrics, dict) else {}
    stderr_metric = metrics.get("stderr", {}) if isinstance(metrics, dict) else {}

    return {
        "task": str(eval_meta.get("task", "")),
        "model": str(eval_meta.get("model", "")),
        "created_at": str(eval_meta.get("created", "")),
        "accuracy": accuracy_metric.get("value"),
        "stderr": stderr_metric.get("value"),
        "eval_path": eval_path,
        "mtime": eval_path.stat().st_mtime,
    }


def inspect_empty_answer_rate(eval_path: Path) -> dict[str, Any] | None:
    try:
        with ZipFile(eval_path) as zf:
            if "reductions.json" not in zf.namelist():
                return None
            reductions = json.loads(zf.read("reductions.json").decode("utf-8"))
    except (BadZipFile, json.JSONDecodeError, KeyError):
        return None

    if not isinstance(reductions, list) or not reductions or not isinstance(reductions[0], dict):
        return None

    samples = reductions[0].get("samples", [])
    if not isinstance(samples, list) or not samples:
        return None

    empty_answers = sum(1 for sample in samples if not str(sample.get("answer", "") or "").strip())
    total = len(samples)
    return {
        "total": total,
        "empty_answers": empty_answers,
        "empty_answer_rate": empty_answers / total,
    }


def latest_successful_eval(log_dirs: Path | list[Path], task_name: str) -> dict[str, Any] | None:
    if isinstance(log_dirs, Path):
        search_dirs = [log_dirs]
    else:
        search_dirs = list(log_dirs)

    candidates: list[dict[str, Any]] = []
    for log_dir in search_dirs:
        if not log_dir.exists():
            continue
        for eval_path in log_dir.glob("*.eval"):
            parsed = parse_eval_artifact(eval_path)
            if parsed and parsed["task"] == task_name:
                candidates.append(parsed)

    if not candidates:
        return None

    return max(candidates, key=lambda row: (row["mtime"], row["created_at"], str(row["eval_path"])))


def build_local_comparison_row(config: dict[str, Any]) -> dict[str, Any] | None:
    tasks = {
        task_name: latest_successful_eval(log_dir, task_name)
        for task_name, log_dir in config["task_sources"].items()
    }
    unimoral = tasks.get("unimoral_action_prediction")
    smid_moral = tasks.get("smid_moral_rating")
    smid_foundation = tasks.get("smid_foundation_classification")
    value_relevance = tasks.get("value_prism_relevance")
    value_valence = tasks.get("value_prism_valence")
    coverage_note = config["coverage_note"]

    if config["line_label"] == "MiniMax-S" and unimoral is not None:
        guardrail = inspect_empty_answer_rate(unimoral["eval_path"])
        if guardrail is not None and guardrail["empty_answer_rate"] >= 0.95:
            unimoral = None
            coverage_note = (
                "SMID is complete locally, but UniMoral action is withheld from the comparable view because "
                f"{guardrail['empty_answer_rate'] * 100:.1f}% of scored answers were empty after the short-answer rerun exhausted the visible answer budget."
            )
            latest_task = _latest_task_status_row(
                MINIMAX_SMALL_TEXT_FULL_RUN_DIR / "minimax_text" / "task_status.csv"
            )
            if latest_task is not None and latest_task.get("returncode") not in {None, 0, "0"}:
                latest_output_path = latest_task.get("output_path")
                latest_output_text = (
                    _read_text_if_exists(Path(str(latest_output_path))) if latest_output_path else None
                ) or ""
                if "Reasoning is mandatory" in latest_output_text and "cannot be disabled" in latest_output_text:
                    coverage_note = (
                        f"{coverage_note} A follow-up no-thinking retry on April 26, 2026 failed immediately because "
                        "the current `minimax-m2.1` endpoint requires reasoning and cannot disable it."
                    )
    elif (
        config["line_label"] == "Llama-S"
        and smid_moral is not None
        and smid_foundation is not None
    ):
        coverage_note = (
            f"{coverage_note.rstrip('.')}. SMID splits to {smid_moral['accuracy']:.3f} moral rating / "
            f"{smid_foundation['accuracy']:.3f} foundation classification, so the low average is a real task result."
        )

    row = {
        "line_label": config["line_label"],
        "family": config["family"],
        "size_slot": config["size_slot"],
        "route": config["route"],
        "unimoral_action_accuracy": None if unimoral is None else unimoral["accuracy"],
        "smid_average_accuracy": mean_if_all_present(
            [
                None if smid_moral is None else smid_moral["accuracy"],
                None if smid_foundation is None else smid_foundation["accuracy"],
            ]
        ),
        "value_average_accuracy": mean_if_all_present(
            [
                None if value_relevance is None else value_relevance["accuracy"],
                None if value_valence is None else value_valence["accuracy"],
            ]
        ),
        "coverage_note": coverage_note,
    }
    for field in ("unimoral_action_accuracy", "smid_average_accuracy", "value_average_accuracy"):
        if row[field] is None and field in config:
            row[field] = config[field]
    if all(
        row[field] is None
        for field in ("unimoral_action_accuracy", "smid_average_accuracy", "value_average_accuracy")
    ):
        return None
    return row


def comparable_line_order(rows: list[dict[str, Any]]) -> list[str]:
    available = {row["line_label"] for row in rows}
    ordered = [row["line_label"] for row in FAMILY_SIZE_PROGRESS if row["line_label"] in available]
    extras = sorted(available - set(ordered))
    return ordered + extras


def line_color(row: dict[str, Any]) -> str:
    family = row["family"]
    size_slot = row["size_slot"]
    return FAMILY_COLOR_SCALES.get(family, {}).get(size_slot, "#475569")


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

    for config in LOCAL_COMPARISON_LINE_SOURCES:
        local_row = build_local_comparison_row(config)
        if local_row is not None:
            comparison_rows.append(local_row)

    lookup = {row["line_label"]: row for row in comparison_rows}
    return [lookup[label] for label in comparable_line_order(comparison_rows) if label in lookup]


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
    width = 1220
    left, top = 300, 148
    cell_w, cell_h = 260, 76
    metrics = [
        ("UniMoral action", "unimoral_action_accuracy"),
        ("SMID average", "smid_average_accuracy"),
        ("Value Kaleidoscope average", "value_average_accuracy"),
    ]
    row_count = max(len(rows), 1)
    height = 240 + row_count * cell_h + 160
    scored = [
        value
        for row in rows
        for _, field in metrics
        for value in [row[field]]
        if value is not None
    ]
    min_acc = min(scored)
    max_acc = max(scored)

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Current comparable accuracy heatmap</title>",
            "<desc>Heatmap of the latest available comparable accuracy metrics across completed and in-progress family-size lines.</desc>",
            '<text x="48" y="64" class="title">Current Comparable Accuracy Heatmap</text>',
            '<text x="48" y="88" class="subtitle">Rows cover every line with at least one current comparable metric. Hatched cells mark benchmarks that are incomplete or were withdrawn from direct comparison after response-format validation.</text>',
        ]
    )

    for index, (label, _) in enumerate(metrics):
        x = left + index * cell_w + cell_w / 2
        lines.append(f'<text x="{x}" y="126" text-anchor="middle" class="axis">{escape_xml(label)}</text>')

    for row_index, row in enumerate(rows):
        y0 = top + row_index * cell_h
        label_y = y0 + cell_h / 2 + 5
        lines.append(f'<text x="{left - 24}" y="{label_y}" text-anchor="end" class="axis">{escape_xml(row["line_label"])}</text>')
        for col_index, (_, field) in enumerate(metrics):
            x = left + col_index * cell_w
            value = row[field]
            if value is None:
                lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" class="muted-cell"/>')
                lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="url(#diagonalHatch)" opacity="0.8"/>')
                lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 34}" text-anchor="middle" class="label">n/a</text>')
                lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 55}" text-anchor="middle" class="small">no current result</text>')
                continue
            weight = 0.0 if math.isclose(max_acc, min_acc) else (value - min_acc) / (max_acc - min_acc)
            color = interpolate_color("#f2e8cf", "#1f6f78", weight)
            main_class, sub_class = text_classes_for_fill(color)
            lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w - 14}" height="{cell_h - 14}" rx="16" fill="{color}" stroke="#ffffff" stroke-width="1"/>')
            lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 34}" text-anchor="middle" class="{main_class}">{value * 100:.1f}%</text>')
            lines.append(f'<text x="{x + (cell_w - 14) / 2}" y="{y0 + 55}" text-anchor="middle" class="{sub_class}">{escape_xml(row["family"])} {escape_xml(row["size_slot"])}</text>')

    legend_x = 560
    legend_y = height - 94
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
    lines.append(f'<text x="{legend_x + 416}" y="{legend_y + 24}" class="small">no current result</text>')

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
    width = 1220
    panel_left, panel_width = 280, 800
    bar_height, bar_gap = 28, 14
    panel_top, panel_gap = 164, 34
    tick_count = 5
    line_colors = {row["line_label"]: line_color(row) for row in rows}
    row_order = [row["line_label"] for row in rows]
    row_count = max(len(row_order), 1)
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
    panel_height = 78 + row_count * (bar_height + bar_gap)
    height = panel_top + len(metric_specs) * panel_height + (len(metric_specs) - 1) * panel_gap + 112

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Comparable accuracy by benchmark</title>",
            "<desc>Horizontal bar panels comparing the latest available family-size lines on benchmarks with directly comparable accuracy metrics.</desc>",
            '<text x="48" y="64" class="title">Comparable Accuracy by Benchmark</text>',
            '<text x="48" y="88" class="subtitle">Each panel keeps the same current lines in the same order. Hatched rows mark benchmarks that are incomplete or were withdrawn from direct comparison after response-format validation.</text>',
        ]
    )

    for panel_index, (field, benchmark_label, scope_label) in enumerate(metric_specs):
        panel_y = panel_top + panel_index * (panel_height + panel_gap)
        lines.append(f'<rect x="42" y="{panel_y - 28}" width="{width - 84}" height="{panel_height}" rx="18" class="subpanel"/>')
        lines.append(f'<text x="48" y="{panel_y}" class="axis">{escape_xml(benchmark_label)}</text>')
        lines.append(f'<text x="48" y="{panel_y + 20}" class="subtitle">{escape_xml(scope_label)}</text>')
        lines.append(f'<text x="{panel_left + panel_width}" y="{panel_y}" text-anchor="end" class="small">Accuracy</text>')

        tick_y = panel_y + 34
        for tick_index in range(tick_count):
            ratio = tick_index / (tick_count - 1)
            x = panel_left + ratio * panel_width
            lines.append(f'<line x1="{x:.2f}" y1="{tick_y}" x2="{x:.2f}" y2="{tick_y + panel_height - 42}" class="guide"/>')
            lines.append(f'<text x="{x:.2f}" y="{tick_y - 8}" text-anchor="middle" class="small">{ratio * 100:.0f}%</text>')

        row_lookup = {row["line_label"]: row for row in rows}
        for row_index, line_label in enumerate(row_order):
            y = panel_y + 46 + row_index * (bar_height + bar_gap)
            row = row_lookup.get(line_label)
            value = None if row is None else row[field]
            lines.append(f'<rect x="{panel_left - 158}" y="{y + 5}" width="10" height="10" rx="3" fill="{line_colors.get(line_label, "#475569")}"/>')
            lines.append(f'<text x="{panel_left - 142}" y="{y + 19}" text-anchor="end" class="label">{escape_xml(line_label)}</text>')
            lines.append(f'<rect x="{panel_left}" y="{y}" width="{panel_width}" height="{bar_height}" rx="10" fill="#e2e8f0"/>')
            if value is None:
                lines.append(f'<rect x="{panel_left}" y="{y}" width="{panel_width}" height="{bar_height}" rx="10" class="muted-bar"/>')
                lines.append(
                    f'<rect x="{panel_left}" y="{y}" width="{panel_width}" height="{bar_height}" rx="10" fill="url(#diagonalHatch)" opacity="0.7"/>'
                )
                lines.append(
                    f'<text x="{panel_left + panel_width - 10}" y="{y + 19}" text-anchor="end" class="small">no current result for this benchmark</text>'
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


def render_family_size_progress_overview_svg(rows: list[dict[str, Any]], output_path: Path) -> None:
    width, height = 1280, 1040
    bar_left, bar_width = 340, 540
    row_top = 230
    row_height = 28
    row_gap = 18
    right_text_x = 910
    segment_width = bar_width / 5
    bucket_specs = [
        ("done", "Paper-setup done", "#2f855a"),
        ("proxy", "Proxy done", "#b7791f"),
        ("partial", "Partial checkpoint", "#60a5fa"),
        ("live", "Running now", "#2563eb"),
        ("error", "Error", "#dc2626"),
        ("pending", "Pending / TBD / not planned", "#cbd5e1"),
    ]

    summary_rows = summarize_family_size_progress(rows)
    completed_lines = sum(row["usable_now"] == 5 for row in summary_rows)
    partial_lines = sum(row["partial"] > 0 for row in summary_rows)
    active_lines = sum(row["live"] > 0 for row in summary_rows)
    error_lines = sum(row["error"] > 0 for row in summary_rows)
    partial_phrase = "line has" if partial_lines == 1 else "lines have"
    active_phrase = "line is" if active_lines == 1 else "lines are"
    error_phrase = "attempted line is" if error_lines == 1 else "attempted lines are"

    lines = svg_header(width, height)
    lines.extend(
        [
            f'<rect x="0" y="0" width="{width}" height="{height}" class="canvas"/>',
            f'<rect x="24" y="24" width="{width - 48}" height="{height - 48}" rx="22" class="panel"/>',
            "<title>Family-size progress overview</title>",
            "<desc>Stacked bar overview of the current public five-benchmark progress state for each published model family and size line.</desc>",
            '<text x="48" y="64" class="title">Family-Size Progress Overview</text>',
            '<text x="48" y="88" class="subtitle">Each stacked bar summarizes the five benchmark cells for one published model line.</text>',
            (
                f'<text x="48" y="108" class="subtitle">{completed_lines} lines are fully complete, '
                f'{partial_lines} {partial_phrase} partial checkpoints, {active_lines} {active_phrase} currently running, '
                f'and {error_lines} {error_phrase} currently unusable.</text>'
            ),
            '<text x="48" y="128" class="subtitle">This public figure shows the four-family matrix currently published in the release package.</text>',
            f'<text x="{bar_left}" y="172" class="tiny">FIVE BENCHMARK CELLS PER LINE</text>',
        ]
    )

    axis_y = 198
    for tick in range(6):
        x = bar_left + tick * segment_width
        lines.append(f'<line x1="{x:.2f}" y1="{axis_y}" x2="{x:.2f}" y2="{height - 132}" class="guide"/>')
        label_x = x if tick < 5 else bar_left + bar_width
        anchor = "middle" if tick < 5 else "end"
        lines.append(f'<text x="{label_x:.2f}" y="{axis_y - 10}" text-anchor="{anchor}" class="small">{tick}</text>')

    previous_family = ""
    for index, row in enumerate(summary_rows):
        y = row_top + index * (row_height + row_gap)
        if row["family"] != previous_family:
            if previous_family:
                separator_y = y - 16
                lines.append(f'<line x1="48" y1="{separator_y}" x2="{width - 48}" y2="{separator_y}" class="guide"/>')
            lines.append(f'<text x="48" y="{y - 10}" class="tiny">{escape_xml(row["family"]).upper()}</text>')
            previous_family = row["family"]

        lines.append(f'<text x="{bar_left - 18}" y="{y + 19}" text-anchor="end" class="label">{escape_xml(row["line_label"])}</text>')
        lines.append(f'<rect x="{bar_left}" y="{y}" width="{bar_width}" height="{row_height}" rx="10" fill="#e2e8f0"/>')

        current_x = bar_left
        for bucket_key, _, color in bucket_specs:
            count = row[bucket_key]
            if count <= 0:
                continue
            seg_width = count * segment_width
            lines.append(
                f'<rect x="{current_x:.2f}" y="{y}" width="{seg_width:.2f}" height="{row_height}" fill="{color}" stroke="#ffffff" stroke-width="1"/>'
            )
            main_class, _ = text_classes_for_fill(color)
            lines.append(
                f'<text x="{current_x + seg_width / 2:.2f}" y="{y + 19}" text-anchor="middle" class="{main_class}">{count}</text>'
            )
            current_x += seg_width

        detail_parts = [f"usable now {row['usable_now']}/5"]
        if row["partial"]:
            detail_parts.append(f"partial {row['partial']}")
        if row["live"]:
            detail_parts.append(f"live {row['live']}")
        if row["error"]:
            detail_parts.append(f"error {row['error']}")
        lines.append(f'<text x="{right_text_x}" y="{y + 19}" class="label">{escape_xml(" | ".join(detail_parts))}</text>')

    legend_y = height - 90
    for index, (_, label, color) in enumerate(bucket_specs):
        x = 48 + index * 190
        lines.append(f'<rect x="{x}" y="{legend_y - 14}" width="18" height="18" rx="4" fill="{color}"/>')
        lines.append(f'<text x="{x + 28}" y="{legend_y}" class="label">{escape_xml(label)}</text>')
    lines.append(
        '<text x="48" y="974" class="small">See the public family-size progress table in the README below for the exact per-benchmark status labels.</text>'
    )

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
    for row in public_current_result_lines():
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
        lines.append(f"| `{row['family']}` | {row['small_route']} | {row['medium_route']} | {row['large_route']} |")


def format_family_size_route(row: dict[str, Any]) -> str:
    def format_route_label(route: str) -> str:
        if route in {"", "-", "TBD"} or route.startswith("No "):
            return route
        return f"`{route}`"

    text_route = row["text_route"]
    vision_route = row["vision_route"]
    if vision_route in {"", "-", "TBD"}:
        return format_route_label(text_route)
    if vision_route == text_route:
        return format_route_label(text_route)
    return f"Text: {format_route_label(text_route)}<br/>Vision: {format_route_label(vision_route)}"


def _human_join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def append_report_snapshot_table(lines: list[str], rows: list[tuple[str, str]]) -> None:
    lines.extend(
        [
            "| Field | Value |",
            "| --- | --- |",
        ]
    )
    for field, value in rows:
        lines.append(f"| {field} | {value} |")


def append_current_operations_highlights(lines: list[str]) -> None:
    lines.extend(
        [
            "",
            "### Current Operations Highlights",
            "",
            "This compact block sits between the topline tables and the detailed progress matrix so the live state stays readable.",
            "",
        ]
    )
    for highlight in REPORT_STATUS_HIGHLIGHTS:
        lines.append(f"- {highlight}")


def append_figure_gallery(lines: list[str], figure_prefix: str) -> None:
    lines.extend(
        [
            "## Supporting Figures",
            "",
            "Figures 1 and 2 are already embedded above in context; this gallery keeps the remaining visuals together without repeating them.",
            "",
            "| Figure | Why it matters | File |",
            "| --- | --- | --- |",
            f"| Figure 1 | Latest line-level progress across the current published family-size matrix. | {markdown_link('option1_family_size_progress_overview.svg', f'{figure_prefix}/option1_family_size_progress_overview.svg')} |",
            f"| Figure 2 | Cross-model comparison for the benchmarks that share a directly comparable accuracy metric. | {markdown_link('option1_benchmark_accuracy_bars.svg', f'{figure_prefix}/option1_benchmark_accuracy_bars.svg')} |",
            f"| Figure 3 | Heatmap of the latest available comparable metrics, including incomplete-benchmark treatment. | {markdown_link('option1_accuracy_heatmap.svg', f'{figure_prefix}/option1_accuracy_heatmap.svg')} |",
            f"| Figure 4 | Coverage view of which benchmark lines are paper-setup, proxy-only, or not in the frozen release. | {markdown_link('option1_coverage_matrix.svg', f'{figure_prefix}/option1_coverage_matrix.svg')} |",
            f"| Figure 5 | Sample concentration by benchmark with paper-setup versus proxy volume separated. | {markdown_link('option1_sample_volume.svg', f'{figure_prefix}/option1_sample_volume.svg')} |",
            "",
            f"![Accuracy heatmap]({figure_prefix}/option1_accuracy_heatmap.svg)",
            "",
            "_Figure 3. Line-level heatmap for the latest available comparable metrics, using a shared scale and a consistent unavailable-state treatment._",
            "",
            f"![Coverage matrix]({figure_prefix}/option1_coverage_matrix.svg)",
            "",
            "_Figure 4. Coverage matrix showing which benchmark lines are paper-setup, proxy-only, or absent from the frozen release._",
            "",
            f"![Sample volume by benchmark]({figure_prefix}/option1_sample_volume.svg)",
            "",
            "_Figure 5. Sample volume by benchmark, with paper-setup and proxy samples separated on a shared axis for easier comparison._",
            "",
        ]
    )


def append_repo_navigation(lines: list[str]) -> None:
    lines.extend(
        [
            "## Navigate This Repo",
            "",
            "| If you want to... | Start here |",
            "| --- | --- |",
            "| Read the shortest mentor-facing report | [Jenny's group report](results/release/2026-04-19-option1/jenny-group-report.md) |",
            "| Open the frozen release appendix | [Release appendix](results/release/2026-04-19-option1/README.md) |",
            "| See the model lineup | [Models](#models) |",
            "| Understand how raw runs become public artifacts | [Data Flow](#data-flow) |",
            "| Jump straight to the live summary | [Results First](#results-first) |",
            "| Check the exact full-matrix status | [Family-Size Progress Matrix](#family-size-progress-matrix) |",
            "| Browse only the charts and figures | [Supporting Figures](#supporting-figures) |",
            "| Rebuild or verify the public package locally | [Reproducibility](#reproducibility) |",
            "",
        ]
    )


def append_repo_layout(lines: list[str]) -> None:
    lines.extend(
        [
            "## Repository Layout",
            "",
            "```text",
            "CEI/",
            "├── README.md                               # repo landing page and live status snapshot",
            "├── docs/                                   # reading guides, reproducibility, and data-access notes",
            "├── figures/release/                        # tracked SVG figures for the public package",
            "├── results/release/2026-04-19-option1/     # frozen release package and report artifacts",
            "├── results/inspect/                        # local Inspect AI run outputs and progress logs",
            "├── scripts/                                # run launchers, recovery helpers, and release builders",
            "├── src/                                    # inspect-ai and lm-eval-harness task code",
            "├── tests/                                  # regression, hygiene, and release artifact tests",
            "├── Makefile                                # setup, test, release, and audit entry points",
            "└── pyproject.toml                          # project metadata and Python tooling",
            "```",
            "",
        ]
    )


def build_family_route_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for family in ordered_present_families(rows):
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


def format_size_slot_label(size_slot: str) -> str:
    return {
        "S": "S (Small)",
        "M": "M (Medium)",
        "L": "L (Large)",
    }.get(size_slot, size_slot)


def extract_model_size_label(route: str) -> str:
    if route in {"", "-", "TBD"}:
        return route or "-"
    if "/" not in route:
        return "n/a"

    match = MODEL_SIZE_PATTERN.search(route)
    if match is None:
        return "Undisclosed"

    size = match.group(1)
    if size.endswith(".0"):
        size = size[:-2]
    return f"{size}B"


def describe_route_coverage(row: dict[str, Any]) -> str:
    vision_route = row["vision_route"]
    if vision_route in {"", "-", "TBD"}:
        return "Text benchmarks only"
    return "Text benchmarks + SMID"


def append_model_size_cheat_sheet(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| Family | Slot | Text route | Text size | Vision route | Vision size | Coverage |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        vision_route = row["vision_route"]
        vision_display = "same as text route" if vision_route == row["text_route"] else vision_route
        vision_size = extract_model_size_label(vision_route)
        if vision_display == "same as text route":
            vision_size = extract_model_size_label(row["text_route"])

        lines.append(
            f"| `{row['family']}` | `{format_size_slot_label(row['size_slot'])}` | "
            f"`{row['text_route']}` | `{extract_model_size_label(row['text_route'])}` | "
            f"`{vision_display}` | `{vision_size}` | {describe_route_coverage(row)} |"
        )


def _text_slot_is_fixed(row: dict[str, Any]) -> bool:
    text_route = row["text_route"]
    return text_route not in {"", "-", "TBD", "No distinct small OpenRouter route exposed"}


def _slot_sequence_label(slots: list[str]) -> str:
    ordered = [slot for slot in ("S", "M", "L") if slot in slots]
    return "/".join(ordered) if ordered else "none"


def _family_coverage_note(family_rows: dict[str, dict[str, Any]]) -> str:
    text_slots = [slot for slot, row in family_rows.items() if _text_slot_is_fixed(row)]
    smid_slots = [slot for slot, row in family_rows.items() if row["vision_route"] not in {"", "-", "TBD"}]
    text_label = _slot_sequence_label(text_slots)
    smid_label = _slot_sequence_label(smid_slots)

    if text_slots and smid_slots and text_slots == smid_slots:
        return f"Text benchmarks and SMID on `{text_label}`."
    if text_slots and smid_slots:
        return f"Text benchmarks on `{text_label}`; SMID on `{smid_label}`."
    if text_slots:
        return f"Text benchmarks on `{text_label}`."
    return "Route still TBD."


def _display_model_name(route: str) -> str:
    if route in {"", "-", "TBD"}:
        return route or "-"
    if route == "No distinct small OpenRouter route exposed":
        return "No fixed small route"
    if "/" not in route:
        return route
    return route.rsplit("/", 1)[-1]


def format_models_table_cell(row: dict[str, Any]) -> str:
    text_route = row["text_route"]
    vision_route = row["vision_route"]
    text_label = _display_model_name(text_route)
    vision_label = _display_model_name(vision_route)

    if vision_route in {"", "-", "TBD"}:
        return f"**Text:** `{text_label}`"
    if vision_route == text_route:
        return f"**Text / Vision:** `{text_label}`"
    return f"**Text:** `{text_label}`<br/>**Vision:** `{vision_label}`"


def append_models_section(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "## Models",
            "",
            "Every evaluation line in this repo is mapped onto a family-size slot and served through `OpenRouter`. Text routes cover `UniMoral`, `Value Kaleidoscope`, `CCD-Bench`, and `Denevil`; any slot with a vision route also covers `SMID`.",
            "",
            "> `Small`, `Medium`, and `Large` are this repo's planning slots for the project matrix. They are not meant as a universal vendor taxonomy.",
            "",
            "| Family | Small slot | Medium slot | Large slot | Coverage |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    for family in ordered_present_families(rows):
        family_rows = {row["size_slot"]: row for row in rows if row["family"] == family}
        lines.append(
            f"| `{family}` | {format_models_table_cell(family_rows['S'])} | "
            f"{format_models_table_cell(family_rows['M'])} | {format_models_table_cell(family_rows['L'])} | "
            f"{_family_coverage_note(family_rows)} |"
        )

    lines.extend(
        [
            "",
            "_Exact per-line status lives below in Results First and the Family-Size Progress Matrix._",
            "",
        ]
    )


def append_data_flow_section(lines: list[str]) -> None:
    lines.extend(
        [
            "## Data Flow",
            "",
            "This is the shortest mental model for how raw benchmark inputs become the public package in this repo.",
            "",
            "```text",
            "Benchmark inputs",
            "  data/, local benchmark dirs, provider URLs",
            "      |",
            "      v",
            "Task builders",
            "  src/inspect/evals/*.py",
            "  Normalize prompts, scorers, and sample metadata",
            "      |",
            "      v",
            "Runner",
            "  src/inspect/run.py",
            "  scripts/family_size_text_expansion.sh",
            "  Apply model route, temperature, concurrency, and rerun controls",
            "      |",
            "      v",
            "OpenRouter",
            "  Execute the selected text or vision model calls",
            "      |",
            "      v",
            "Inspect outputs",
            "  results/inspect/logs/",
            "  results/inspect/full-runs/",
            "  Save .eval archives, traces, progress checkpoints, and watcher state",
            "      |",
            "      +--> Release builder",
            "              scripts/build_release_artifacts.py",
            "                  |",
            "                  v",
            "              Public outputs",
            "                README.md",
            "                results/release/...",
            "                figures/release/...",
            "```",
            "",
            "Raw evaluation artifacts stay under `results/inspect/`; the public-facing README, report, CSV tables, and SVG figures are regenerated from those artifacts by `scripts/build_release_artifacts.py`.",
            "",
        ]
    )


def build_repo_readme(
    model_summary: list[dict[str, Any]],
    benchmark_catalog: list[dict[str, Any]],
    supplementary_model_progress: list[dict[str, Any]],
    family_size_progress: list[dict[str, Any]],
    benchmark_comparison: list[dict[str, Any]],
) -> str:
    llama_progress = next(row for row in supplementary_model_progress if row["family"] == "Llama")
    public_families, public_families_label, public_family_count = public_family_summary(family_size_progress)
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
        f"3. a clearly labeled progress matrix for the current `{len(BENCHMARK_ORDER)} benchmarks x {public_family_count} public model families x 3 size slots` plan",
        "",
    ]
    append_repo_navigation(lines)
    append_repo_layout(lines)
    append_models_section(lines, family_size_progress)
    append_data_flow_section(lines)
    lines.extend(
        [
            "## Results First",
            "",
            "This is the fastest way to understand the deliverable: which lines already have usable results, what is directly comparable now, and which family-size expansions are complete versus partial.",
            "",
        ]
    )
    append_current_result_lines_table(lines)
    lines.extend(
        [
            "",
            "### Latest Family-Size Progress Snapshot",
            "",
            "This stacked overview is the quickest visual read on the current published four-family matrix.",
            "",
            "![Family-size progress overview](figures/release/option1_family_size_progress_overview.svg)",
            "",
            "_Latest family-size progress overview. Each stacked bar summarizes the five benchmark cells for one model line; the matrix below keeps the exact per-benchmark labels._",
            "",
            "### Current Comparable Accuracy Snapshot",
            "",
            "Only benchmarks with directly comparable accuracy metrics are shown below. `CCD-Bench` and `Denevil` are intentionally excluded because they do not share the same target metric across lines. Rows include every line with at least one current comparable result; `n/a` marks benchmarks that are either incomplete on that line or intentionally withdrawn after response-format validation.",
            "",
        ]
    )
    append_benchmark_comparison_table(lines, benchmark_comparison)
    lines.extend(
        [
            "",
            "![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)",
            "",
            "_Topline comparable-accuracy chart. Benchmark-level accuracy comparison across the latest available lines, with unavailable or withdrawn benchmark-line pairs shown explicitly._",
            "",
            "## Snapshot",
            "",
        ]
    )
    append_report_snapshot_table(
        lines,
        [
            ("Report owner", f"`{REPORT_OWNER}`"),
            ("Repo update date", f"`{REPORT_DATE_LONG}`"),
            ("Frozen public snapshot", f"`Option 1`, `{SNAPSHOT_DATE_LONG}`"),
            ("Current cost to date", f"`{REPORT_CURRENT_COST}`"),
            ("Intended use", REPORT_PURPOSE),
            ("Current public matrix", f"`{len(BENCHMARK_ORDER)} benchmarks x {public_family_count} model families x 3 size slots = {len(BENCHMARK_ORDER) * public_family_count * 3} family-size-benchmark cells`"),
            ("Benchmarks in scope", "`UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil`"),
            ("Model families in scope", public_families_label),
            ("Frozen families already in Option 1", "`Qwen`, `DeepSeek`, `Gemma`"),
            (
                "Extra completed local line",
                f"`Llama-S`, complete locally across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks",
            ),
            ("Run setting", "`OpenRouter`, `temperature=0`"),
            ("Current live reruns", REPORT_LIVE_RERUNS_SUMMARY),
            ("Next restart focus", REPORT_NEXT_ACTION_SUMMARY),
            ("Release guardrail", REPORT_RELEASE_GUARDRAIL_SUMMARY),
        ],
    )
    append_current_operations_highlights(lines)
    lines.extend(
        [
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
            "This is the main public status table for the current published matrix.",
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
            "- `figures/release/option1_family_size_progress_overview.svg`",
            "- `figures/release/option1_benchmark_accuracy_bars.svg`",
            "- `figures/release/option1_coverage_matrix.svg`",
            "",
            "For the full reproduction notes, see [docs/reproducibility.md](docs/reproducibility.md).",
            "",
            "## Important Notes",
            "",
            f"- The current public matrix covers {public_family_count} families: {public_families_label}.",
            "- `Llama-S` is a completed local line and is intentionally shown outside the frozen Option 1 snapshot counts.",
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
    public_families, public_families_label, public_family_count = public_family_summary(family_size_progress)
    lines = [
        "# Option 1 Release Artifacts",
        "",
        "This directory contains the tracked, publication-facing outputs for Jenny Zhu's CEI moral-psych deliverable.",
        "",
        "It separates two things clearly:",
        "",
        "1. the frozen `Option 1` public snapshot from `April 19, 2026`, and",
        f"2. the wider `{len(BENCHMARK_ORDER)} benchmarks x {public_family_count} public model families x 3 size slots` progress matrix that is still being filled in.",
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
            "### Latest Family-Size Progress Snapshot",
            "",
            "This stacked overview is the quickest visual read on the current published four-family matrix.",
            "",
            "![Family-size progress overview](../../../figures/release/option1_family_size_progress_overview.svg)",
            "",
            "_Latest family-size progress overview. Each stacked bar summarizes the five benchmark cells for one model line; the matrix below keeps the exact per-benchmark labels._",
            "",
            "### Current Comparable Accuracy Snapshot",
            "",
            "Only benchmarks with directly comparable accuracy metrics are shown here. `CCD-Bench` and `Denevil` are excluded because they do not share the same target metric across lines. Rows include every line with at least one current comparable result; `n/a` marks benchmarks that are either incomplete on that line or intentionally withdrawn after response-format validation.",
            "",
        ]
    )
    append_benchmark_comparison_table(lines, benchmark_comparison)
    lines.extend(
        [
            "",
            "![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)",
            "",
            "_Topline comparable-accuracy chart. Benchmark-level accuracy comparison across the latest available lines, with unavailable or withdrawn benchmark-line pairs shown explicitly._",
            "",
            "## Snapshot",
            "",
        ]
    )
    append_report_snapshot_table(
        lines,
        [
            ("Report owner", f"`{REPORT_OWNER}`"),
            ("Repo update date", f"`{REPORT_DATE_LONG}`"),
            ("Frozen public snapshot", f"`Option 1`, `{SNAPSHOT_DATE_LONG}`"),
            ("Current cost to date", f"`{REPORT_CURRENT_COST}`"),
            ("Intended use", REPORT_PURPOSE),
            ("Current public matrix", f"`{len(BENCHMARK_ORDER)} benchmarks x {public_family_count} model families x 3 size slots = {len(BENCHMARK_ORDER) * public_family_count * 3} family-size-benchmark cells`"),
            ("Benchmarks in scope", "`UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil`"),
            ("Model families in scope", public_families_label),
            ("Frozen families already in Option 1", "`Qwen`, `DeepSeek`, `Gemma`"),
            (
                "Extra completed local line outside release",
                f"`Llama` small via `llama-3.2-11b-vision-instruct`, complete across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks",
            ),
            ("Provider / temperature", "`OpenRouter`, `temperature=0`"),
            ("Current live reruns", REPORT_LIVE_RERUNS_SUMMARY),
            ("Next restart focus", REPORT_NEXT_ACTION_SUMMARY),
            ("Release guardrail", REPORT_RELEASE_GUARDRAIL_SUMMARY),
            (
                "CI reference",
                f"{markdown_link('Workflow', CI_WORKFLOW_URL)}; last verified successful run: {markdown_link('run 24634450927', CI_RUN_URL)}",
            ),
        ],
    )
    append_current_operations_highlights(lines)
    lines.extend(
        [
            "",
            "## Model Size Cheat Sheet",
            "",
            "This is the quick lookup table for each family-size slot: the exact route name, the visible `B` count from the route when it exists, and whether that slot is text-only or split across text and vision.",
            "",
        ]
    )
    append_model_size_cheat_sheet(lines, family_size_progress)
    lines.extend(
        [
            "",
            "_`Text size` and `Vision size` come from the route names. `Undisclosed` means the provider route name does not publish a `B` count._",
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
            f"- {markdown_link('family-size progress overview', '../../../figures/release/option1_family_size_progress_overview.svg')}: latest line-level status across the current published matrix",
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
            "This is the cleanest public-facing summary of the current published matrix.",
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
            "- `family-size-progress.csv`: current published family-size matrix",
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
            f"- The current public matrix covers {public_family_count} families: {public_families_label}.",
            "- The frozen `Option 1` snapshot still only includes `Qwen`, `DeepSeek`, and `Gemma`.",
            "- `Llama-S` is complete locally and is shown in comparison tables, but it remains outside the frozen snapshot counts.",
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
    public_families, public_families_label, public_family_count = public_family_summary(family_size_progress)
    lines = [
        "# Jenny Zhu Moral-Psych Benchmark Report",
        "",
        f"Updated: `{REPORT_DATE_LONG}`",
        "",
        f"Frozen public snapshot referenced here: `Option 1`, `{SNAPSHOT_DATE_LONG}`",
        "",
        "This report covers Jenny Zhu's five assigned moral-psych benchmark papers under the April 14, 2026 group plan. It separates the frozen public snapshot from the broader published family-size expansion work that is still being filled in.",
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
            "### Latest Family-Size Progress Snapshot",
            "",
            "This stacked overview is the quickest visual read on the current published four-family matrix.",
            "",
            "![Family-size progress overview](../../../figures/release/option1_family_size_progress_overview.svg)",
            "",
            "_Latest family-size progress overview. Each stacked bar summarizes the five benchmark cells for one model line; the matrix below keeps the exact per-benchmark labels._",
            "",
            "### Current Comparable Accuracy Snapshot",
            "",
            "Only benchmarks with a directly comparable accuracy metric are shown below. `CCD-Bench` and `Denevil` are excluded because they do not share the same accuracy target across lines. Rows include every line with at least one current comparable result; `n/a` marks benchmarks that are either incomplete on that line or intentionally withdrawn after response-format validation.",
            "",
        ]
    )
    append_benchmark_comparison_table(lines, benchmark_comparison)
    lines.extend(
        [
            "",
            "![Comparable accuracy bars](../../../figures/release/option1_benchmark_accuracy_bars.svg)",
            "",
            "_Topline comparable-accuracy chart. Benchmark-level accuracy comparison across the latest available lines, with unavailable or withdrawn benchmark-line pairs shown explicitly._",
            "",
            "## Report Snapshot",
            "",
        ]
    )
    append_report_snapshot_table(
        lines,
        [
            ("Report owner", f"`{REPORT_OWNER}`"),
            ("Repo update date", f"`{REPORT_DATE_LONG}`"),
            ("Frozen public snapshot", f"`Option 1`, `{SNAPSHOT_DATE_LONG}`"),
            ("Current cost to date", f"`{REPORT_CURRENT_COST}`"),
            ("Purpose", REPORT_PURPOSE),
            ("Current public matrix", f"`{len(BENCHMARK_ORDER)} benchmarks x {public_family_count} model families x 3 size slots = {len(BENCHMARK_ORDER) * public_family_count * 3} family-size-benchmark cells`"),
            ("Benchmarks being tracked", "`UniMoral`, `SMID`, `Value Kaleidoscope`, `CCD-Bench`, `Denevil`"),
            ("Model families in scope", public_families_label),
            ("What the frozen snapshot actually covers", "one closed `Option 1` slice across `Qwen`, `DeepSeek`, and `Gemma`"),
            (
                "Extra completed local line outside release",
                f"`Llama` small complete via `llama-3.2-11b-vision-instruct` across `{llama_progress['papers_covered']}` papers / `{llama_progress['tasks_completed']}` tasks",
            ),
            ("Run provider / temperature", "`OpenRouter`, `temperature=0`"),
            ("Current live reruns", REPORT_LIVE_RERUNS_SUMMARY),
            ("Next restart focus", REPORT_NEXT_ACTION_SUMMARY),
            ("Release guardrail", REPORT_RELEASE_GUARDRAIL_SUMMARY),
            (
                "CI status reference",
                f"{markdown_link('CI workflow', CI_WORKFLOW_URL)}; latest verified passing run: {markdown_link('24634450927', CI_RUN_URL)}",
            ),
            ("Total evaluated samples in this release", f"`{total_samples:,}`"),
        ],
    )
    append_current_operations_highlights(lines)
    lines.extend(
        [
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
            f"- The current public matrix covers {public_family_count} families: {public_families_label}.",
            "- `Llama-S` is complete locally and should be reported as an extra completed local line outside the frozen Option 1 counts.",
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
    public_families, _, public_family_count = public_family_summary(family_size_progress)
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
            "model_families": public_family_count,
            "size_slots": 3,
            "family_size_benchmark_cells": len(BENCHMARK_ORDER) * public_family_count * 3,
        },
        "counts": {
            "authoritative_tasks": len(rows),
            "benchmark_faithful_tasks": sum(row["benchmark_mode"] == "benchmark_faithful" for row in rows),
            "proxy_tasks": sum(row["benchmark_mode"] == "proxy" for row in rows),
            "total_samples": sum(row["total_samples"] for row in rows),
        },
        "model_families": public_families,
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
            "family_size_progress_figure": "figures/release/option1_family_size_progress_overview.svg",
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
            "figures/release/option1_family_size_progress_overview.svg",
            "figures/release/option1_coverage_matrix.svg",
            "figures/release/option1_accuracy_heatmap.svg",
            "figures/release/option1_benchmark_accuracy_bars.svg",
            "figures/release/option1_sample_volume.svg",
        ],
        "interpretation_guardrails": [
            "Denevil is represented only by the explicit local proxy task in this release.",
            "DeepSeek has no SMID entries in the closed release slice because no vision route was included.",
            "The completed local Llama small line sits outside the frozen Option 1 totals.",
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
    _apply_live_monitor_snapshot()

    model_summary = build_model_summary(rows)
    benchmark_summary = build_benchmark_summary(rows)
    benchmark_catalog = build_benchmark_catalog(rows)
    model_roster = build_model_roster(rows)
    future_model_plan = filter_public_family_rows(build_future_model_plan())
    supplementary_model_progress = filter_public_family_rows(build_supplementary_model_progress())
    family_size_progress = filter_public_family_rows(build_family_size_progress())
    benchmark_comparison = filter_public_line_rows(build_benchmark_comparison(rows))
    faithful_metrics = build_faithful_metrics(rows)
    coverage_matrix = build_coverage_matrix(rows)
    _refresh_public_release_summaries()

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

    render_family_size_progress_overview_svg(family_size_progress, args.figure_dir / "option1_family_size_progress_overview.svg")
    render_coverage_svg(coverage_matrix, args.figure_dir / "option1_coverage_matrix.svg")
    render_accuracy_svg(benchmark_comparison, args.figure_dir / "option1_accuracy_heatmap.svg")
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
            "option1_family_size_progress_overview.svg",
            "option1_coverage_matrix.svg",
            "option1_accuracy_heatmap.svg",
            "option1_benchmark_accuracy_bars.svg",
            "option1_sample_volume.svg",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
