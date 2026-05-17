"""Curated Inspect AI registry for the moral-psych benchmark suite.

This file exists so users can point `src/inspect/run.py` at a single module and
still obtain tasks implemented across several benchmark files.
"""

from evals.ccd_bench import ccd_bench_selection
from evals.denevil import denevil_fulcra_proxy_generation, denevil_generation
from evals.m3oralbench import m3oralbench_foundation, m3oralbench_judgment, m3oralbench_response
from evals.moral_circuits import moral_circuits_judgment, moral_circuits_reasoning
from evals.morallens import morallens_cot, morallens_double_standard, morallens_posthoc
from evals.morebench import morebench_advisor, morebench_agent
from evals.smid import smid_foundation_classification, smid_moral_rating
from evals.unimoral import (
    unimoral_action_prediction,
    unimoral_consequence_generation,
    unimoral_factor_attribution,
    unimoral_moral_typology,
)
from evals.value_kaleidoscope import value_prism_relevance, value_prism_valence

TASK_EXPORTS = [
    # Jenny's benchmarks
    unimoral_action_prediction,
    unimoral_moral_typology,
    unimoral_factor_attribution,
    unimoral_consequence_generation,
    smid_moral_rating,
    smid_foundation_classification,
    value_prism_relevance,
    value_prism_valence,
    ccd_bench_selection,
    denevil_generation,
    denevil_fulcra_proxy_generation,
    # Joseph's benchmarks
    morebench_advisor,
    morebench_agent,
    moral_circuits_judgment,
    moral_circuits_reasoning,
    m3oralbench_judgment,
    m3oralbench_foundation,
    m3oralbench_response,
    morallens_cot,
    morallens_posthoc,
    morallens_double_standard,
]
