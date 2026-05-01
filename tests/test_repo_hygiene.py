"""Repository hygiene checks for the public-facing release surface."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parent.parent

PUBLIC_GLOBS = [
    "README.md",
    "CITATION.cff",
    "Makefile",
    ".env.example",
    ".gitignore",
    ".github/workflows/*.yml",
    "CONTRIBUTING.md",
    "docs/*.md",
    "figures/*.md",
    "figures/release/*.svg",
    "results/*.md",
    "results/lm-harness/*.md",
    "results/release/**/*.csv",
    "results/release/**/*.md",
    "results/release/**/*.json",
    "scripts/*",
    "src/**/*.py",
    "tests/*.py",
]

FORBIDDEN_PUBLIC_STRINGS = [
    "/Users/" + "hanzhenzhu",
    "Library/Python/" + "3.9/bin/uv",
    "Desktop/" + "moral-psych-harness/data",
]


def test_public_files_do_not_embed_workstation_specific_paths():
    checked_files: list[Path] = []
    for pattern in PUBLIC_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_dir():
                continue
            if path.name == "test_repo_hygiene.py":
                continue
            checked_files.append(path)
            content = path.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_PUBLIC_STRINGS:
                assert forbidden not in content, f"{forbidden!r} found in {path}"

    assert checked_files, "Expected to scan at least one public-facing file."


def test_gitignore_covers_env_local():
    content = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env.local" in content


def test_env_example_exists_and_documents_core_inputs():
    env_example = ROOT / ".env.example"
    assert env_example.exists()
    content = env_example.read_text(encoding="utf-8")
    assert "OPENROUTER_API_KEY=" in content
    assert "UNIMORAL_DATA_DIR=" in content
    assert "SMID_DATA_DIR=" in content
    assert "VALUEPRISM_RELEVANCE_FILE=" in content
    assert "CCD_BENCH_DATA_FILE=" in content
    assert "DENEVIL_DATA_FILE=" in content


def test_root_readme_prefers_public_bootstrap_before_live_setup():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## TL;DR" in readme
    assert "## Research Goal" in readme
    assert "## Method Overview" in readme
    assert "how far do current open-source model families get on five moral-psych benchmark papers" in readme
    assert "Every public table, report, and SVG is regenerated from a tracked authoritative snapshot" in readme
    assert "Best like-for-like line" in readme
    assert "There is no universal scaling law" in readme
    assert "CCD-Bench shows cultural choice style, not accuracy." in readme
    assert "DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring." in readme
    assert "## Benchmark Result Visuals" in readme
    assert "### 1. UniMoral / SMID / Value Kaleidoscope: topline comparable accuracy" in readme
    assert "### 3. CCD-Bench: cultural-cluster choice behavior" in readme
    assert "### 5. DeNEVIL: proxy behavioral outcomes" in readme
    assert "option1_benchmark_accuracy_bars.svg" in readme
    assert "option1_family_scaling_profile.svg" in readme
    assert "option1_ccd_choice_distribution.svg" in readme
    assert "option1_ccd_dominant_option_share.svg" in readme
    assert "option1_denevil_behavior_outcomes.svg" in readme
    assert "## Public Quickstart" in readme
    assert "`make bootstrap`" in readme
    assert "reviewer-safe path" in readme
    assert "does **not** require `.env`, API keys, or local benchmark datasets" in readme
    assert "make setup && cp .env.example .env && make smoke" in readme
    assert readme.count("![Comparable accuracy bars]") == 1
    assert readme.count("![Family scaling profile]") == 1
    assert readme.count("![CCD choice distribution]") == 1
    assert readme.count("![CCD dominant-option share]") == 1
    assert readme.count("![DeNEVIL proxy behavioral outcomes]") == 1
    assert "without re-embedding the same chart" in readme
    assert "without duplicating the same graphics" in readme


def test_citation_metadata_exists_and_is_linked_from_root_readme():
    citation = ROOT / "CITATION.cff"
    assert citation.exists()
    content = citation.read_text(encoding="utf-8")
    assert "cff-version: 1.2.0" in content
    assert 'title: "CEI Moral-Psych Benchmark Suite"' in content
    assert 'repository-code: "https://github.com/hanzhenzhujene/CEI-moral-psych-release"' in content
    assert 'alias: Jenny Zhu' in content

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "[CITATION.cff](CITATION.cff)" in readme
    assert "## Citation" in readme


def test_docs_index_mentions_repo_architecture():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "repo-architecture.md" in docs_index
    assert "evaluation-methodology.md" in docs_index


def test_ci_workflow_uses_native_node24_action_releases() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" not in workflow
    assert "actions/checkout@v5" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "astral-sh/setup-uv@v8.1.0" in workflow
    assert "actions/checkout@v4" not in workflow
    assert "actions/setup-python@v5" not in workflow
    assert "astral-sh/setup-uv@v5" not in workflow


def test_supporting_docs_track_current_release_artifacts_and_boundaries():
    reproducibility = (ROOT / "docs" / "reproducibility.md").read_text(encoding="utf-8")
    assert "ccd-choice-distribution.csv" in reproducibility
    assert "denevil-behavior-summary.csv" in reproducibility
    assert "denevil-proxy-summary.csv" in reproducibility
    assert "option1_ccd_choice_distribution.svg" in reproducibility
    assert "option1_denevil_behavior_outcomes.svg" in reproducibility
    assert "appendix QA artifacts" in reproducibility

    figures_readme = (ROOT / "figures" / "README.md").read_text(encoding="utf-8")
    assert "## CCD-Bench figures" in figures_readme
    assert "## DeNEVIL figures" in figures_readme
    assert "option1_ccd_choice_distribution.svg" in figures_readme
    assert "option1_denevil_behavior_outcomes.svg" in figures_readme
    assert "appendix QA / provenance" in figures_readme

    results_readme = (ROOT / "results" / "README.md").read_text(encoding="utf-8")
    assert "## Public Result Layers" in results_readme
    assert "ccd-choice-distribution.csv" in results_readme
    assert "denevil-behavior-summary.csv" in results_readme
    assert "Appendix QA / provenance" in results_readme

    scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
    assert "one canonical reporting path" in scripts_readme
    assert "build_release_artifacts.py" in scripts_readme
    assert "DeNEVIL proxy evidence package" in scripts_readme


def test_root_readme_links_evaluation_methodology():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/evaluation-methodology.md" in readme
    assert "[Benchmark Result Visuals](#benchmark-result-visuals)" in readme


def test_root_readme_frames_denevil_as_proxy_only_evidence():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "### DeNEVIL Proxy Behavioral Evidence" in readme
    assert "### DeNEVIL Appendix QA / Provenance" in readme
    assert "proxy-only behavioral evidence and traceability support" in readme
    assert "not benchmark-faithful ethical-quality scoring" in readme
    assert "denevil-proxy-summary.csv" in readme
    assert "denevil-behavior-summary.csv" in readme
    assert "denevil-prompt-family-breakdown.csv" in readme
    assert "option1_denevil_behavior_outcomes.svg" in readme
    assert "option1_denevil_prompt_family_heatmap.svg" in readme
    assert "denevil-proxy-examples.csv" in readme
    assert "option1_denevil_proxy_status_matrix.svg" in readme
    assert "option1_denevil_proxy_pipeline.svg" in readme
    assert "macro-accuracy claim" in readme


def test_evaluation_methodology_versions_current_metric_definition():
    methodology = (ROOT / "docs" / "evaluation-methodology.md").read_text(encoding="utf-8")
    assert "Current public metric definition version" in methodology
    assert "`2026-04-30`" in methodology


def test_core_python_modules_have_module_docstrings():
    checked: list[Path] = []
    for pattern in ("scripts/*.py", "src/**/*.py"):
        for path in ROOT.glob(pattern):
            if path.is_dir():
                continue
            module = ast.parse(path.read_text(encoding="utf-8"))
            checked.append(path)
            assert ast.get_docstring(module), f"Missing module docstring: {path}"

    assert checked, "Expected to scan at least one core Python module."
