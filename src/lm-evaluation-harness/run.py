"""
CLI wrapper for lm-evaluation-harness programmatic evaluation.

Usage:
    python run.py [--model hf] [--model_args pretrained=Qwen/Qwen3-0.6B] \
                  [--tasks hendrycks_ethics] [--num_fewshot 0] \
                  [--limit 5] [--output_path ../../results/lm-harness/] \
                  [--log_samples] [--task_dir tasks/]
"""

import argparse
import json
import os
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Run lm-evaluation-harness benchmarks")
    parser.add_argument("--model", default="hf", help="Model type (default: hf)")
    parser.add_argument(
        "--model_args",
        default="pretrained=Qwen/Qwen3-0.6B",
        help="Model arguments as comma-separated key=value pairs",
    )
    parser.add_argument(
        "--tasks",
        default="cei_ethics",
        help="Comma-separated list of task names (default: cei_ethics)",
    )
    parser.add_argument(
        "--num_fewshot",
        type=int,
        default=0,
        help="Number of few-shot examples (default: 0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of samples per task (useful for smoke testing)",
    )
    parser.add_argument(
        "--output_path",
        default=str(Path(__file__).parent.parent.parent / "results" / "lm-harness"),
        help="Directory to write results JSON",
    )
    parser.add_argument(
        "--log_samples",
        action="store_true",
        help="Include per-sample logs in output",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size for model inference (default: 1)",
    )
    parser.add_argument(
        "--task_dir",
        default=str(Path(__file__).parent / "tasks"),
        help="Path to directory containing custom YAML task configs",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    import lm_eval
    from lm_eval import simple_evaluate
    from lm_eval.tasks import TaskManager

    # Register custom tasks from directory if provided
    include_path = None
    if args.task_dir:
        task_dir = Path(args.task_dir).resolve()
        if not task_dir.is_dir():
            raise ValueError(f"--task_dir does not exist or is not a directory: {task_dir}")
        include_path = str(task_dir)
        print(f"Registered custom tasks from: {task_dir}")

    task_manager = TaskManager(include_path=include_path)

    task_list = [t.strip() for t in args.tasks.split(",")]
    print(f"Running tasks: {task_list}")
    print(f"Model: {args.model} | Args: {args.model_args}")
    if args.limit:
        print(f"Limit: {args.limit} samples per task")

    results = simple_evaluate(
        model=args.model,
        model_args=args.model_args,
        tasks=task_list,
        num_fewshot=args.num_fewshot,
        batch_size=args.batch_size,
        limit=args.limit,
        log_samples=args.log_samples,
        task_manager=task_manager,
    )

    output_dir = Path(args.output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Derive a filename from the model args
    model_slug = args.model_args.replace("/", "_").replace("=", "-").replace(",", "_")
    output_file = output_dir / f"results_{model_slug}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults written to: {output_file}")

    # Print summary table
    if "results" in results:
        print("\n=== Results Summary ===")
        for task, metrics in results["results"].items():
            acc = metrics.get("acc,none", metrics.get("acc", "N/A"))
            print(f"  {task}: acc={acc}")


if __name__ == "__main__":
    main()
