"""Local backend — wraps existing CEI runners for local execution."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

from src.infra.backend import Backend, Instance, JobHandle, JobStatus, RunConfig


class LocalBackend:
    name = "local"

    def provision(self, config: RunConfig) -> Instance:
        return Instance(
            instance_id=f"local-{uuid.uuid4().hex[:8]}",
            provider="local",
            host="localhost",
        )

    def upload(self, instance: Instance, local_path: Path) -> None:
        pass  # already local

    def run(self, instance: Instance, config: RunConfig) -> JobHandle:
        cmd = _build_command(config)
        handle = JobHandle(
            job_id=f"local-{uuid.uuid4().hex[:8]}",
            instance=instance,
            config=config,
            status=JobStatus.RUNNING,
        )

        print(f"[local] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=_project_root())

        handle.status = JobStatus.COMPLETED if result.returncode == 0 else JobStatus.FAILED
        return handle

    def stream_logs(self, handle: JobHandle) -> None:
        pass  # logs go to stdout directly

    def download_results(self, handle: JobHandle, local_path: Path) -> None:
        pass  # results already local

    def teardown(self, instance: Instance) -> None:
        pass

    def status(self, handle: JobHandle) -> JobStatus:
        return handle.status


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _build_command(config: RunConfig) -> list[str]:
    """Build the eval command based on task and model."""
    task = config.task
    model = config.model

    # Detect which runner to use
    if "trolleybench" in task.lower():
        return _trolleybench_cmd(config)

    if task.endswith(".py") or "::" in task:
        return _inspect_cmd(config)

    # Default to lm-harness for named tasks
    return _lm_harness_cmd(config)


def _inspect_cmd(config: RunConfig) -> list[str]:
    cmd = [
        sys.executable, "src/inspect/run.py",
        "--tasks", config.task,
        "--model", config.model,
    ]
    if config.temperature is not None:
        cmd += ["--temperature", str(config.temperature)]
    if config.limit is not None:
        cmd += ["--limit", str(config.limit)]
    if config.max_connections > 1:
        cmd += ["--max_connections", str(config.max_connections)]
    if config.no_sandbox:
        cmd.append("--no_sandbox")
    cmd += config.extra_args
    return cmd


def _lm_harness_cmd(config: RunConfig) -> list[str]:
    cmd = [
        sys.executable, "src/lm-evaluation-harness/run.py",
        "--tasks", config.task,
    ]
    # lm-harness uses --model_args for HF model specification
    if config.model.startswith("hf/"):
        model_name = config.model[3:]  # strip "hf/"
        cmd += ["--model", "hf", "--model_args", f"pretrained={model_name}"]
    else:
        cmd += ["--model_args", f"pretrained={config.model}"]
    if config.limit is not None:
        cmd += ["--limit", str(config.limit)]
    cmd += config.extra_args
    return cmd


def _trolleybench_cmd(config: RunConfig) -> list[str]:
    cmd = [sys.executable, "tools/legacy_openrouter/run_trolleybench.py"]
    # Parse model family and size from model string
    # e.g. "qwen/qwen3-8b" or "qwen-S"
    cmd += config.extra_args
    return cmd
