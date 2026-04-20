"""
CLI wrapper for Inspect AI programmatic evaluation.

Usage:
    python run.py [--tasks evals/ethics.py] [--model hf/Qwen/Qwen3-0.6B] \
                  [--log_dir ../../results/inspect/logs/] \
                  [--limit 5] [--no_sandbox]

Examples:
    python run.py --tasks evals/ethics.py
    python run.py --tasks evals/moral_psych.py::unimoral_action_prediction
"""

import argparse
import ast
import glob
import importlib.util
import json
import os
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def load_env_file(path: Path) -> None:
    """Load a simple .env file without overriding variables already in the shell."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue

        if value and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ[key] = value


def parse_args():
    parser = argparse.ArgumentParser(description="Run Inspect AI task suites from the CEI workspace.")
    parser.add_argument(
        "--tasks",
        default="evals/ethics.py",
        help=(
            "Task module path(s) to run. Accepts a single file (evals/ethics.py or evals/moral_psych.py), "
            "a glob pattern (evals/*.py), or a specific task name. "
            "Default: evals/ethics.py"
        ),
    )
    parser.add_argument(
        "--model",
        default="hf/Qwen/Qwen3-0.6B",
        help="Model identifier in Inspect format (default: hf/Qwen/Qwen3-0.6B)",
    )
    parser.add_argument(
        "--log_dir",
        default=str(Path(__file__).parent.parent.parent / "results" / "inspect" / "logs"),
        help="Directory to write eval logs",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of samples per task (useful for smoke testing)",
    )
    parser.add_argument(
        "--max_connections",
        type=int,
        default=1,
        help="Max concurrent samples to evaluate at once (default: 1)",
    )
    parser.add_argument(
        "--max_tasks",
        type=int,
        default=1,
        help="Max task files to evaluate concurrently (default: 1)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Generation temperature passed to CEI task factories via CEI_TEMPERATURE",
    )
    parser.add_argument(
        "--no_sandbox",
        action="store_true",
        help="Disable sandboxing (avoids Docker-in-Docker issues)",
    )
    parser.add_argument(
        "--model_args",
        default="",
        help=(
            "Comma-separated key=value pairs passed to the model provider "
            "(default: none; pass provider-specific options explicitly when needed)"
        ),
    )
    parser.add_argument(
        "--model_args_json",
        default="",
        help=(
            "JSON object merged into model_args. Use this for nested provider routing "
            "config such as extra_body/provider settings."
        ),
    )
    return parser.parse_args()


def parse_model_args(raw_pairs: str = "", raw_json: str = "") -> dict:
    """Parse legacy key=value args plus an optional JSON object for nested provider config."""
    model_args: dict = {}

    if raw_pairs:
        for pair in raw_pairs.split(","):
            k, _, v = pair.strip().partition("=")
            if not k:
                continue
            try:
                model_args[k] = ast.literal_eval(v)
            except (ValueError, SyntaxError):
                model_args[k] = v

    if raw_json:
        try:
            json_args = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid --model_args_json: {exc}") from exc
        if not isinstance(json_args, dict):
            raise ValueError("--model_args_json must decode to a JSON object.")
        model_args.update(json_args)

    return model_args


def eval_log_status(log_location: str | Path) -> str:
    """Read an Inspect `.eval` archive and return its terminal status."""
    try:
        with ZipFile(log_location) as zf:
            header = json.loads(zf.read("header.json").decode("utf-8"))
    except (BadZipFile, FileNotFoundError):
        return "unreadable"
    except KeyError:
        return "missing_header"

    if isinstance(header, dict):
        return str(header.get("status", "success"))
    return "unknown"


def load_tasks_from_file(filepath: str) -> list:
    """
    Import a Python module and collect all @task-decorated callables.
    Identifies tasks by finding zero-arg callables defined in the module
    without invoking them (to avoid side effects like dataset downloads).

    Modules may also expose an explicit TASK_EXPORTS list to curate a suite
    that spans multiple files.
    """
    import inspect as _inspect

    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Task file not found: {path}")

    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    exported_tasks = getattr(module, "TASK_EXPORTS", None)
    if exported_tasks is not None:
        curated = []
        seen = set()
        for obj in exported_tasks:
            if callable(obj) and obj not in seen:
                curated.append(obj)
                seen.add(obj)
        return curated

    tasks = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if not callable(obj):
            continue
        # Only consider functions defined in this module
        if getattr(obj, "__module__", None) != path.stem:
            continue
        # Only zero-arg functions (task factories take no arguments)
        try:
            sig = _inspect.signature(obj)
            if all(
                p.default is not _inspect.Parameter.empty
                for p in sig.parameters.values()
            ):
                tasks.append(obj)
        except (ValueError, TypeError):
            pass

    return tasks


def parse_task_spec(task_spec: str) -> tuple[str, list[str] | None]:
    """Support file.py::task_name or file.py::task_a,task_b selectors."""
    if "::" not in task_spec:
        return task_spec, None
    filepath, names = task_spec.split("::", 1)
    requested = [name.strip() for name in names.split(",") if name.strip()]
    return filepath, requested or None


def resolve_task_files(tasks_arg: str) -> list[str]:
    """Resolve a tasks argument (file path, glob, or task name) to file paths."""
    base_spec, requested = parse_task_spec(tasks_arg)
    script_dir = Path(__file__).parent

    # Try as glob relative to cwd, then relative to script dir
    matches = glob.glob(base_spec) or glob.glob(str(script_dir / base_spec))
    if matches:
        if requested:
            return [f"{match}::{','.join(requested)}" for match in sorted(matches)]
        return sorted(matches)
    # Try as direct path, then relative to script dir
    if Path(base_spec).exists():
        return [tasks_arg]
    if (script_dir / base_spec).exists():
        resolved = str(script_dir / base_spec)
        return [f"{resolved}::{','.join(requested)}" if requested else resolved]
    # Return as-is (may be a registered task name)
    return [tasks_arg]


def main():
    project_root = Path(__file__).resolve().parents[2]
    load_env_file(project_root / ".env")
    load_env_file(project_root / ".env.local")

    args = parse_args()
    if args.temperature is not None:
        os.environ["CEI_TEMPERATURE"] = str(args.temperature)

    from inspect_ai import eval as inspect_eval
    from pathlib import Path as _Path

    log_dir = _Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    task_files = resolve_task_files(args.tasks)

    all_tasks = []
    for task_file in task_files:
        task_path, requested_names = parse_task_spec(task_file)
        if task_path.endswith(".py") and Path(task_path).exists():
            task_factories = load_tasks_from_file(task_path)
            if requested_names is not None:
                requested_set = set(requested_names)
                task_factories = [factory for factory in task_factories if factory.__name__ in requested_set]
            for factory in task_factories:
                task_obj = factory(limit=args.limit) if args.limit is not None else factory()
                all_tasks.append(task_obj)
            print(f"Loaded {len(task_factories)} task(s) from {task_file}")
        else:
            # Assume it's a registered task name — pass directly
            all_tasks.append(task_file)

    if not all_tasks:
        print("No tasks found. Exiting.")
        sys.exit(1)

    print(f"Running {len(all_tasks)} task(s) with model: {args.model}")
    if args.limit:
        print(f"Limit: {args.limit} samples per task")

    try:
        model_args = parse_model_args(args.model_args, args.model_args_json)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    models: str | list[str]
    if "," in args.model:
        models = [model.strip() for model in args.model.split(",") if model.strip()]
    else:
        models = args.model

    eval_kwargs = dict(
        tasks=all_tasks,
        model=models,
        model_args=model_args,
        log_dir=str(log_dir),
        max_connections=args.max_connections,
        max_tasks=args.max_tasks,
    )
    if args.limit is not None:
        eval_kwargs["limit"] = args.limit
    if args.no_sandbox:
        eval_kwargs["sandbox"] = None

    logs = inspect_eval(**eval_kwargs)

    print("\n=== Eval Complete ===")
    had_non_success = False
    for log in logs:
        print(f"  Log: {log.location}")
        log_status = eval_log_status(log.location)
        print(f"    status: {log_status}")
        if log_status != "success":
            had_non_success = True
        if hasattr(log, "results") and log.results:
            metrics = getattr(log.results, "metrics", {})
            for metric_name, metric_val in metrics.items():
                print(f"    {metric_name}: {metric_val}")

    if had_non_success:
        print("\nOne or more eval logs finished with non-success status.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
