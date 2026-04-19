"""Curated Inspect AI registry for the moral-psych benchmark suite.

This file exists so users can point `src/inspect/run.py` at a single module and
still obtain tasks implemented across several benchmark files.
"""

from evals.ccd_bench import ccd_bench_selection
from evals.denevil import denevil_fulcra_proxy_generation, denevil_generation
from evals.smid import smid_foundation_classification, smid_moral_rating
from evals.unimoral import unimoral_action_prediction
from evals.value_kaleidoscope import value_prism_relevance, value_prism_valence

TASK_EXPORTS = [
    unimoral_action_prediction,
    smid_moral_rating,
    smid_foundation_classification,
    value_prism_relevance,
    value_prism_valence,
    ccd_bench_selection,
    denevil_generation,
    denevil_fulcra_proxy_generation,
]
