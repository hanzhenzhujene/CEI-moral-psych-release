"""Repository hygiene checks for the public-facing release surface."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parent.parent

PUBLIC_GLOBS = [
    "README.md",
    "Makefile",
    ".gitignore",
    ".github/workflows/*.yml",
    "CONTRIBUTING.md",
    "docs/*.md",
    "figures/*.md",
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
