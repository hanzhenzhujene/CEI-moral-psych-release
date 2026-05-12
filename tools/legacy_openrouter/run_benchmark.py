"""Batch benchmark runner for CEI moral psychology evaluation.

Usage:
    python tools/legacy_openrouter/run_benchmark.py --benchmark morebench --models qwen llama --sizes L M S --temps 0.0 0.7
    python tools/legacy_openrouter/run_benchmark.py --benchmark morebench --all-models --temps 0.0
    python tools/legacy_openrouter/run_benchmark.py --list-models
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from client import query, query_with_system
from config import BENCHMARKS, MODELS, TEMPERATURES


RESULTS_DIR = Path("results")


def get_model_list(families: list[str] | None, sizes: list[str] | None, all_models: bool = False) -> list[tuple[str, str]]:
    """Return list of (label, model_id) tuples based on filters."""
    if all_models:
        families = list(MODELS.keys())
    if not families:
        raise ValueError("Specify --models or --all-models")

    sizes = sizes or ["L", "M", "S"]
    result = []
    for family in families:
        if family not in MODELS:
            print(f"Warning: unknown model family '{family}', skipping")
            continue
        for size in sizes:
            if size in MODELS[family]:
                result.append((f"{family}-{size}", MODELS[family][size]))
    return result


def load_prompts(benchmark: str) -> list[dict]:
    """Load prompts for a benchmark from its data file.

    Expected format: prompts/<benchmark>.jsonl
    Each line: {"id": "...", "prompt": "...", "system": "..." (optional), "metadata": {...}}
    """
    prompts_file = Path("prompts") / f"{benchmark}.jsonl"
    if not prompts_file.exists():
        print(f"No prompts file found at {prompts_file}")
        print(f"Create {prompts_file} with one JSON object per line:")
        print('  {"id": "001", "prompt": "...", "system": "..." (optional)}')
        return []

    prompts = []
    with open(prompts_file) as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(json.loads(line))
    return prompts


def run(benchmark: str, models: list[tuple[str, str]], temperatures: list[float], delay: float = 1.0):
    """Run a benchmark across models and temperatures."""
    prompts = load_prompts(benchmark)
    if not prompts:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = RESULTS_DIR / benchmark / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(prompts) * len(models) * len(temperatures)
    print(f"Running {benchmark}: {len(prompts)} prompts × {len(models)} models × {len(temperatures)} temps = {total} queries")

    for label, model_id in models:
        for temp in temperatures:
            results = []
            desc = f"{label} T={temp}"
            for prompt_data in tqdm(prompts, desc=desc):
                try:
                    if "system" in prompt_data:
                        resp = query_with_system(
                            model=model_id,
                            system=prompt_data["system"],
                            prompt=prompt_data["prompt"],
                            temperature=temp,
                        )
                    else:
                        resp = query(
                            model=model_id,
                            prompt=prompt_data["prompt"],
                            temperature=temp,
                        )
                    results.append({
                        "prompt_id": prompt_data.get("id", ""),
                        "prompt": prompt_data["prompt"],
                        "metadata": prompt_data.get("metadata", {}),
                        **resp,
                    })
                except Exception as e:
                    results.append({
                        "prompt_id": prompt_data.get("id", ""),
                        "error": str(e),
                        "model": model_id,
                        "temperature": temp,
                    })
                time.sleep(delay)

            output_file = output_dir / f"{label}_T{temp}.json"
            output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
            print(f"  Saved {len(results)} results → {output_file}")

    # Write run metadata
    meta = {
        "benchmark": benchmark,
        "paper": BENCHMARKS.get(benchmark, {}).get("paper", ""),
        "timestamp": timestamp,
        "models": {label: model_id for label, model_id in models},
        "temperatures": temperatures,
        "num_prompts": len(prompts),
    }
    (output_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nDone. Results in {output_dir}/")


def list_models():
    """Print all available models."""
    for family, sizes in MODELS.items():
        print(f"\n{family}:")
        for size, model_id in sizes.items():
            print(f"  {size}: {model_id}")


def main():
    parser = argparse.ArgumentParser(description="CEI Moral Psychology Benchmark Runner")
    parser.add_argument("--benchmark", "-b", help="Benchmark ID (e.g., morebench, trolleybench)")
    parser.add_argument("--models", "-m", nargs="+", help="Model families (e.g., qwen llama deepseek)")
    parser.add_argument("--sizes", "-s", nargs="+", default=["L", "M", "S"], help="Model sizes (default: L M S)")
    parser.add_argument("--temps", "-t", nargs="+", type=float, default=[0.0], help="Temperatures (default: 0.0)")
    parser.add_argument("--all-models", action="store_true", help="Run all model families")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls in seconds")
    parser.add_argument("--list-models", action="store_true", help="List all available models")
    args = parser.parse_args()

    if args.list_models:
        list_models()
        return

    if not args.benchmark:
        parser.error("--benchmark is required (or use --list-models)")

    models = get_model_list(args.models, args.sizes, args.all_models)
    run(args.benchmark, models, args.temps, args.delay)


if __name__ == "__main__":
    main()
