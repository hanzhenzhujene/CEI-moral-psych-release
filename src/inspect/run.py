"""
CLI wrapper for Inspect AI programmatic evaluation.

Usage:
    python run.py [--tasks evals/ethics.py] [--model hf/Qwen/Qwen3-0.6B] \
                  [--log_dir ../../results/inspect/logs/] \
                  [--limit 5] [--no_sandbox]
"""

import argparse
import ast
import glob
import importlib.util
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Run Inspect AI benchmarks")
    parser.add_argument(
        "--tasks",
        default="evals/ethics.py",
        help=(
            "Task module path(s) to run. Accepts a single file (evals/ethics.py), "
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
        "--no_sandbox",
        action="store_true",
        help="Disable sandboxing (avoids Docker-in-Docker issues)",
    )
    parser.add_argument(
        "--model_args",
        default="enable_thinking=False",
        help=(
            "Comma-separated key=value pairs passed to the model provider "
            "(default: enable_thinking=False to disable reasoning tokens for Qwen3-style models)"
        ),
    )
    return parser.parse_args()


def load_tasks_from_file(filepath: str) -> list:
    """
    Import a Python module and collect all @task-decorated callables.
    Identifies tasks by finding zero-arg callables defined in the module
    without invoking them (to avoid side effects like dataset downloads).
    """
    import inspect as _inspect

    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Task file not found: {path}")

    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

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


def resolve_task_files(tasks_arg: str) -> list[str]:
    """Resolve a tasks argument (file path, glob, or task name) to file paths."""
    script_dir = Path(__file__).parent

    # Try as glob relative to cwd, then relative to script dir
    matches = glob.glob(tasks_arg) or glob.glob(str(script_dir / tasks_arg))
    if matches:
        return sorted(matches)
    # Try as direct path, then relative to script dir
    if Path(tasks_arg).exists():
        return [tasks_arg]
    if (script_dir / tasks_arg).exists():
        return [str(script_dir / tasks_arg)]
    # Return as-is (may be a registered task name)
    return [tasks_arg]


def main():
    args = parse_args()

    from inspect_ai import eval as inspect_eval
    from pathlib import Path as _Path

    log_dir = _Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    task_files = resolve_task_files(args.tasks)

    all_tasks = []
    for task_file in task_files:
        if task_file.endswith(".py") and Path(task_file).exists():
            task_factories = load_tasks_from_file(task_file)
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

    # Parse model_args from "key=val,key=val" string into a dict
    model_args: dict = {}
    if args.model_args:
        for pair in args.model_args.split(","):
            k, _, v = pair.strip().partition("=")
            if k:
                try:
                    model_args[k] = ast.literal_eval(v)
                except (ValueError, SyntaxError):
                    model_args[k] = v

    eval_kwargs = dict(
        tasks=all_tasks,
        model=args.model,
        model_args=model_args,
        log_dir=str(log_dir),
        max_connections=args.max_connections,
    )
    if args.limit is not None:
        eval_kwargs["limit"] = args.limit
    if args.no_sandbox:
        eval_kwargs["sandbox"] = None

    logs = inspect_eval(**eval_kwargs)

    print("\n=== Eval Complete ===")
    for log in logs:
        print(f"  Log: {log.location}")
        if hasattr(log, "results") and log.results:
            metrics = getattr(log.results, "metrics", {})
            for metric_name, metric_val in metrics.items():
                print(f"    {metric_name}: {metric_val}")


if __name__ == "__main__":
    main()
