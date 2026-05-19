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


def test_unimoral_launcher_routes_minimax_direct_when_key_exists() -> None:
    env = os.environ.copy()
    env.pop("OPENROUTER_API_KEY", None)
    env["MINIMAX_API_KEY"] = "dummy-minimax-key"

    output = run_provider_script(
        'UNIMORAL_SOURCE_ONLY=1 source "./scripts/run_unimoral_missing_tasks.sh" >/dev/null 2>/dev/null; '
        'unset OPENROUTER_API_KEY; export MINIMAX_API_KEY="dummy-minimax-key"; '
        'configure_routed_model "openrouter/minimax/minimax-m2.5" 2>/dev/null; '
        'printf "%s\\n" "$ROUTED_MODEL" "$ROUTED_PROVIDER" "$ROUTED_BASE_URL" "$ROUTED_KEY_VAR" "$ROUTED_KEY_STATE"',
        env=env,
    ).splitlines()

    assert output == [
        "openai/MiniMax-M2.5",
        "minimax",
        "https://api.minimax.io/v1",
        "MINIMAX_API_KEY",
        "present",
    ]


def test_unimoral_launcher_falls_back_to_openrouter_in_auto_mode() -> None:
    env = os.environ.copy()
    env.pop("MINIMAX_API_KEY", None)
    env["OPENROUTER_API_KEY"] = "dummy-openrouter-key"

    output = run_provider_script(
        'UNIMORAL_SOURCE_ONLY=1 source "./scripts/run_unimoral_missing_tasks.sh" >/dev/null 2>/dev/null; '
        'unset MINIMAX_API_KEY; export OPENROUTER_API_KEY="dummy-openrouter-key"; '
        'configure_routed_model "openrouter/minimax/minimax-m2.5" 2>/dev/null; '
        'printf "%s\\n" "$ROUTED_MODEL" "$ROUTED_PROVIDER" "$ROUTED_BASE_URL" "$ROUTED_KEY_VAR" "$ROUTED_KEY_STATE"',
        env=env,
    ).splitlines()

    assert output == [
        "openai/minimax/minimax-m2.5",
        "openrouter",
        "https://openrouter.ai/api/v1",
        "OPENROUTER_API_KEY",
        "present",
    ]


def test_unimoral_launcher_preserves_true_openai_route() -> None:
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "dummy-openai-key"

    output = run_provider_script(
        'UNIMORAL_SOURCE_ONLY=1 source "./scripts/run_unimoral_missing_tasks.sh" >/dev/null 2>/dev/null; '
        'configure_routed_model "openai/gpt-4o-mini" 2>/dev/null; '
        'printf "MODEL=%s\\nPROVIDER=%s\\nBASE=%s\\nKEY=%s\\nSTATE=%s\\n" "$ROUTED_MODEL" "$ROUTED_PROVIDER" "${ROUTED_BASE_URL:-}" "$ROUTED_KEY_VAR" "$ROUTED_KEY_STATE"',
        env=env,
    )

    assert output == "MODEL=openai/gpt-4o-mini\nPROVIDER=openai\nBASE=\nKEY=OPENAI_API_KEY\nSTATE=present"


def test_unimoral_launcher_can_skip_minimax_lines_before_routing() -> None:
    env = os.environ.copy()
    env["UNIMORAL_SKIP_MODEL_REGEX"] = "MiniMax|minimax"

    output = run_provider_script(
        'UNIMORAL_SOURCE_ONLY=1 source "./scripts/run_unimoral_missing_tasks.sh" >/dev/null 2>/dev/null; '
        'if skip_model_line "MiniMax-S" "minimax_s" "openrouter/minimax/minimax-m2.1" "minimax_reasoning"; then echo skip; else echo run; fi; '
        'if skip_model_line "Qwen-S" "qwen_s" "openrouter/qwen/qwen3-8b" "qwen"; then echo skip; else echo run; fi',
        env=env,
    ).splitlines()

    assert output == ["skip", "run"]


def test_unimoral_launcher_requires_explicit_minimax_execution_opt_in() -> None:
    output = run_provider_script(
        'UNIMORAL_SOURCE_ONLY=1 source "./scripts/run_unimoral_missing_tasks.sh" >/dev/null 2>/dev/null; '
        'if minimax_execution_allowed "minimax_reasoning"; then echo run; else echo block; fi; '
        'UNIMORAL_ALLOW_MINIMAX=1; '
        'if minimax_execution_allowed "minimax_reasoning"; then echo run; else echo block; fi; '
        'if minimax_execution_allowed "plain"; then echo run; else echo block; fi'
    ).splitlines()

    assert output == ["block", "run", "run"]


def test_unimoral_launcher_blocks_minimax_before_execution_side_effects() -> None:
    script = (ROOT / "scripts" / "run_unimoral_missing_tasks.sh").read_text(encoding="utf-8")

    block_idx = script.index('reason=minimax_requires_UNIMORAL_ALLOW_MINIMAX')
    record_idx = script.index('record_routing_metadata "$slug" "$task_name" "$start_at"')
    missing_key_idx = script.index('reason=missing_provider_api_key')

    assert block_idx < record_idx
    assert block_idx < missing_key_idx


def test_unimoral_launcher_dry_run_stays_provider_free() -> None:
    script = (ROOT / "scripts" / "run_unimoral_missing_tasks.sh").read_text(encoding="utf-8")

    dry_run_idx = script.index('if [[ "$UNIMORAL_DRY_RUN" == "1" ]]; then')
    dry_run_return_idx = script.index("return 0", dry_run_idx)
    block_idx = script.index('reason=minimax_requires_UNIMORAL_ALLOW_MINIMAX')
    record_idx = script.index('record_routing_metadata "$slug" "$task_name" "$start_at"')
    missing_key_idx = script.index('reason=missing_provider_api_key')

    assert dry_run_idx < dry_run_return_idx
    assert dry_run_return_idx < block_idx
    assert dry_run_return_idx < record_idx
    assert dry_run_return_idx < missing_key_idx


def test_unimoral_launcher_guards_empty_extra_args_under_nounset() -> None:
    script = (ROOT / "scripts" / "run_unimoral_missing_tasks.sh").read_text(encoding="utf-8")

    assert '${args[@]+"${args[@]}"}' in script
    assert "\n          ${args[@]}\n" not in script
