"""CEI Benchmark Evaluation Configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise EnvironmentError(
        "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
    )
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Open-source models — 3 sizes each (L, M, S)
# Verified against OpenRouter API 2026-04-21
MODELS = {
    "qwen": {
        "L": "qwen/qwen3-235b-a22b",
        "M": "qwen/qwen3-32b",
        "S": "qwen/qwen3-8b",
    },
    "deepseek": {
        "L": "deepseek/deepseek-r1",
        "M": "deepseek/deepseek-chat-v3.1",
        "S": "deepseek/deepseek-r1-distill-llama-70b",
    },
    "llama": {
        "L": "meta-llama/llama-3.3-70b-instruct",
        "M": "meta-llama/llama-3.1-8b-instruct",
        "S": "meta-llama/llama-3.2-3b-instruct",
    },
    "gemma": {
        "L": "google/gemma-3-27b-it",
        "M": "google/gemma-3-12b-it",
        "S": "google/gemma-3-4b-it",
    },
    "minimax": {
        "L": "minimax/minimax-m2.5",
        "M": "minimax/minimax-m1",
        "S": "minimax/minimax-01",
    },
}

# Frontier models (optional track)
FRONTIER_MODELS = {
    "gpt-4o": "openai/gpt-4o",
    "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
    "gemini-2.5-pro": "google/gemini-2.5-pro-preview-03-25",
}

# Temperature sweep values
TEMPERATURES = [0.0, 0.3, 0.7, 1.0]

# Benchmark paper IDs and assignments
BENCHMARKS = {
    "morebench": {"paper": "MoReBench (Chiu 2025)", "assignee": "Joseph"},
    "trolleybench": {"paper": "TrolleyBench (Zhu 2025)", "assignee": "Joseph"},
    "moral_circuits": {"paper": "Moral Circuits (Schacht 2025)", "assignee": "Joseph"},
    "m3oralbench": {"paper": "M³oralBench (Yan 2024)", "assignee": "Joseph"},
    "morallens": {"paper": "MoralLens (Samway 2025)", "assignee": "Joseph"},
    "unimoral": {"paper": "UniMoral (Kumar 2025)", "assignee": "Jenny"},
    "smid": {"paper": "SMID (Crone 2018)", "assignee": "Jenny"},
    "denevil": {"paper": "Denevil (Duan 2023)", "assignee": "Jenny"},
    "value_kaleidoscope": {"paper": "Value Kaleidoscope (Sorensen 2024)", "assignee": "Jenny"},
    "ccd_bench": {"paper": "CCD-Bench (Rahman 2025)", "assignee": "Jenny"},
    "rules_broken": {"paper": "Are Rules Meant to be Broken (Kumar 2025)", "assignee": "Erik"},
    "moralbench": {"paper": "MoralBench (Ji 2024)", "assignee": "Erik"},
    "emnlp_educator": {"paper": "EMNLP Educator-role (Jiang 2025)", "assignee": "Erik"},
}
