"""Regression checks for Makefile runner resolution."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent.parent
MAKEFILE = ROOT / "Makefile"


def _write_fake_executable(path: Path, script: str) -> Path:
    path.write_text(script)
    path.chmod(0o755)
    return path


def test_makefile_uses_fallback_python_when_uv_is_missing(tmp_path: Path) -> None:
    fake_python = _write_fake_executable(
        tmp_path / "fake-python",
        "#!/bin/sh\nprintf 'fake-python invoked %s\\n' \"$*\"\n",
    )

    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "test",
            "UV=definitely-not-a-real-uv",
            f"VENV_PYTHON={fake_python}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"{fake_python} -m pytest tests -q" in result.stdout
    assert "fake-python invoked -m pytest tests -q" in result.stdout


def test_makefile_reports_clear_error_when_no_runner_is_available(tmp_path: Path) -> None:
    missing_python = tmp_path / "missing-python"
    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "test",
            "UV=definitely-not-a-real-uv",
            f"VENV_PYTHON={missing_python}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Could not resolve either" in result.stderr
    assert str(missing_python) in result.stderr
    assert "make setup" in result.stderr


def test_makefile_release_uses_fallback_python_when_uv_is_missing(tmp_path: Path) -> None:
    fake_python = _write_fake_executable(
        tmp_path / "fake-python",
        "#!/bin/sh\nprintf 'fake-python invoked %s\\n' \"$*\"\n",
    )

    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "release",
            "UV=definitely-not-a-real-uv",
            f"VENV_PYTHON={fake_python}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"{fake_python} scripts/build_release_artifacts.py --input" in result.stdout
    assert "fake-python invoked scripts/build_release_artifacts.py --input" in result.stdout


def test_makefile_audit_uses_fallback_python_for_both_steps_when_uv_is_missing(tmp_path: Path) -> None:
    fake_python = _write_fake_executable(
        tmp_path / "fake-python",
        "#!/bin/sh\nprintf 'fake-python invoked %s\\n' \"$*\"\n",
    )

    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "audit",
            "UV=definitely-not-a-real-uv",
            f"VENV_PYTHON={fake_python}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"{fake_python} -m pytest tests -q" in result.stdout
    assert f"{fake_python} scripts/build_release_artifacts.py --input" in result.stdout
    assert "fake-python invoked -m pytest tests -q" in result.stdout
    assert "fake-python invoked scripts/build_release_artifacts.py --input" in result.stdout


def test_makefile_refresh_authoritative_uses_fallback_python_and_copies_snapshot(tmp_path: Path) -> None:
    fake_python = _write_fake_executable(
        tmp_path / "fake-python",
        "#!/bin/sh\nprintf 'fake-python invoked %s\\n' \"$*\"\n",
    )
    raw_authoritative = tmp_path / "raw" / "authoritative-summary.csv"
    release_source = tmp_path / "release" / "source" / "authoritative-summary.csv"
    raw_authoritative.parent.mkdir(parents=True)
    raw_authoritative.write_text("header\nvalue\n", encoding="utf-8")

    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "refresh-authoritative",
            "UV=definitely-not-a-real-uv",
            f"VENV_PYTHON={fake_python}",
            f"RAW_AUTHORITATIVE={raw_authoritative}",
            f"RELEASE_SOURCE={release_source}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"{fake_python} scripts/build_authoritative_option1_status.py" in result.stdout
    assert "fake-python invoked scripts/build_authoritative_option1_status.py" in result.stdout
    assert release_source.read_text(encoding="utf-8") == raw_authoritative.read_text(encoding="utf-8")


def test_makefile_setup_requires_uv_and_reports_clear_error() -> None:
    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "setup",
            "UV=definitely-not-a-real-uv",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "make setup requires 'definitely-not-a-real-uv' on PATH" in result.stdout


def test_makefile_smoke_uses_fallback_python_when_uv_is_missing(tmp_path: Path) -> None:
    fake_python = _write_fake_executable(
        tmp_path / "fake-python",
        "#!/bin/sh\nprintf 'fake-python invoked %s\\n' \"$*\"\n",
    )

    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "smoke",
            "UV=definitely-not-a-real-uv",
            f"VENV_PYTHON={fake_python}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"{fake_python} src/inspect/run.py" in result.stdout
    assert "fake-python invoked src/inspect/run.py" in result.stdout
    assert "--tasks src/inspect/evals/moral_psych.py::unimoral_action_prediction" in result.stdout


def test_makefile_smoke_keeps_cei_inspect_package_when_uv_is_available(tmp_path: Path) -> None:
    fake_uv = _write_fake_executable(tmp_path / "fake-uv", "#!/bin/sh\nexit 0\n")

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"

    result = subprocess.run(
        [
            "make",
            "-f",
            str(MAKEFILE),
            "-n",
            "smoke",
            "UV=fake-uv",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "fake-uv run --package cei-inspect python src/inspect/run.py" in result.stdout
