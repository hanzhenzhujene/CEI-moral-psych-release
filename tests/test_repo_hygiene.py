"""Repository hygiene checks for the public-facing release surface."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parent.parent

PUBLIC_GLOBS = [
    "README.md",
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
    assert "## Public Quickstart" in readme
    assert "`make bootstrap`" in readme
    assert "reviewer-safe path" in readme
    assert "does **not** require `.env`, API keys, or local benchmark datasets" in readme
    assert "make setup && cp .env.example .env && make smoke" in readme


def test_docs_index_mentions_repo_architecture():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "repo-architecture.md" in docs_index


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
