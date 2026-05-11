"""Provider-routing checks for direct-provider benchmark reruns."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent.parent


def run_provider_script(script: str, *, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        ["bash", "-lc", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return completed.stdout.strip()


def test_minimax_direct_route_matches_pr7_contract() -> None:
    output = run_provider_script(
        'source "./provider_config.sh"; '
        'printf "%s\\n" "$(resolve_provider "minimax/minimax-m2.5")" "$(provider_url minimax)" "$(provider_key_var minimax)"'
    ).splitlines()

    assert output == [
        "minimax|MiniMax-M2.5",
        "https://api.minimax.io/v1",
        "MINIMAX_API_KEY",
    ]


def test_minimax_01_direct_route_matches_pr6_keepalive_contract() -> None:
    output = run_provider_script(
        'source "./provider_config.sh"; '
        'printf "%s\\n" "$(resolve_provider "minimax/minimax-01")" "$(provider_url minimax)" "$(provider_key_var minimax)"'
    ).splitlines()

    assert output == [
        "minimax|MiniMax-Text-01",
        "https://api.minimax.io/v1",
        "MINIMAX_API_KEY",
    ]


def test_minimax_m2_1_direct_route_uses_minimax_api() -> None:
    output = run_provider_script(
        'source "./provider_config.sh"; '
        'printf "%s\\n" "$(resolve_provider "minimax/minimax-m2.1")" "$(provider_url minimax)" "$(provider_key_var minimax)"'
    ).splitlines()

    assert output == [
        "minimax|MiniMax-M2.1",
        "https://api.minimax.io/v1",
        "MINIMAX_API_KEY",
    ]


def test_setup_model_provider_exports_minimax_direct_api_env() -> None:
    env = os.environ.copy()
    env["MINIMAX_API_KEY"] = "dummy-minimax-key"

    output = run_provider_script(
        'source "./provider_config.sh"; '
        'setup_model_provider "minimax/minimax-m2.5"; '
        'printf "%s\\n" "$EFFECTIVE_MODEL" "$OPENAI_BASE_URL" "$OPENAI_API_KEY"',
        env=env,
    ).splitlines()

    assert output == [
        "MiniMax-M2.5",
        "https://api.minimax.io/v1",
        "dummy-minimax-key",
    ]


def test_setup_model_provider_exports_minimax_01_direct_api_env() -> None:
    env = os.environ.copy()
    env["MINIMAX_API_KEY"] = "dummy-minimax-key"

    output = run_provider_script(
        'source "./provider_config.sh"; '
        'setup_model_provider "minimax/minimax-01"; '
        'printf "%s\\n" "$EFFECTIVE_MODEL" "$OPENAI_BASE_URL" "$OPENAI_API_KEY"',
        env=env,
    ).splitlines()

    assert output == [
        "MiniMax-Text-01",
        "https://api.minimax.io/v1",
        "dummy-minimax-key",
    ]


def test_setup_model_provider_tolerates_missing_key_under_nounset() -> None:
    output = run_provider_script(
        'set -u; '
        'source "./provider_config.sh"; '
        'setup_model_provider "minimax/minimax-m2.5"; '
        'printf "MODEL=%s\\nURL=%s\\nKEY=%s\\n" "$EFFECTIVE_MODEL" "$OPENAI_BASE_URL" "${OPENAI_API_KEY-}"'
    )

    assert output == "MODEL=MiniMax-M2.5\nURL=https://api.minimax.io/v1\nKEY="


def test_setup_model_provider_tolerates_missing_minimax_01_key_under_nounset() -> None:
    output = run_provider_script(
        'set -u; '
        'source "./provider_config.sh"; '
        'setup_model_provider "minimax/minimax-01"; '
        'printf "MODEL=%s\\nURL=%s\\nKEY=%s\\n" "$EFFECTIVE_MODEL" "$OPENAI_BASE_URL" "${OPENAI_API_KEY-}"'
    )

    assert output == "MODEL=MiniMax-Text-01\nURL=https://api.minimax.io/v1\nKEY="
