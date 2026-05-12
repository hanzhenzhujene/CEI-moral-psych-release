"""Multi-turn TrolleyBench runner.

Usage:
    python tools/legacy_openrouter/run_trolleybench.py --models qwen llama --sizes L M S --temps 0.0 0.7
    python tools/legacy_openrouter/run_trolleybench.py --all-models --temps 0.0
    python tools/legacy_openrouter/run_trolleybench.py --models qwen --sizes S --temps 0.0  # smoke test
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from client import query_multiturn
from config import MODELS


PROMPTS_FILE = Path("prompts/trolleybench.jsonl")
RESULTS_DIR = Path("results/trolleybench")


def load_scenarios() -> list[dict]:
    """Load multi-turn trolley scenarios from JSONL."""
    scenarios = []
    with open(PROMPTS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                scenarios.append(json.loads(line))
    return scenarios


def get_model_list(families: list[str] | None, sizes: list[str] | None, all_models: bool = False) -> list[tuple[str, str]]:
    """Return list of (label, model_id) tuples."""
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


def run_scenario(model_id: str, scenario: dict, temperature: float, delay: float) -> dict:
    """Run a single multi-turn scenario, building conversation history."""
    turns = scenario["turns"]
    conversation = []
    responses = []

    for i, turn in enumerate(turns):
        conversation.append({"role": "user", "content": turn["content"]})

        try:
            result = query_multiturn(
                model=model_id,
                messages=list(conversation),
                temperature=temperature,
            )
            assistant_msg = result["content"]
            responses.append({
                "turn": i + 1,
                "user": turn["content"],
                "assistant": assistant_msg,
                "usage": result["usage"],
            })
            conversation.append({"role": "assistant", "content": assistant_msg})
        except Exception as e:
            responses.append({
                "turn": i + 1,
                "user": turn["content"],
                "error": str(e),
            })
            # Stop further turns if one fails
            break

        time.sleep(delay)

    return {
        "id": scenario["id"],
        "variant": scenario.get("variant", ""),
        "metadata": scenario.get("metadata", {}),
        "model": model_id,
        "temperature": temperature,
        "responses": responses,
    }


def run(models: list[tuple[str, str]], temperatures: list[float], delay: float = 1.0):
    """Run TrolleyBench across all models and temperatures."""
    scenarios = load_scenarios()
    if not scenarios:
        print(f"No scenarios found in {PROMPTS_FILE}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = RESULTS_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    total_scenarios = len(scenarios) * len(models) * len(temperatures)
    print(f"TrolleyBench: {len(scenarios)} scenarios × {len(models)} models × {len(temperatures)} temps = {total_scenarios} runs")
    print(f"Each scenario has 3 turns → ~{total_scenarios * 3} API calls\n")

    for label, model_id in models:
        for temp in temperatures:
            results = []
            desc = f"{label} T={temp}"
            for scenario in tqdm(scenarios, desc=desc):
                result = run_scenario(model_id, scenario, temp, delay)
                results.append(result)

            output_file = output_dir / f"{label}_T{temp}.json"
            output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
            print(f"  Saved {len(results)} scenarios → {output_file}")

    # Write run metadata
    meta = {
        "benchmark": "trolleybench",
        "timestamp": timestamp,
        "models": {label: model_id for label, model_id in models},
        "temperatures": temperatures,
        "num_scenarios": len(scenarios),
        "turns_per_scenario": 3,
    }
    (output_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nDone. Results in {output_dir}/")
    print(f"Next: python tools/legacy_openrouter/eval_trolleybench.py --results-dir {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="TrolleyBench Multi-Turn Runner")
    parser.add_argument("--models", "-m", nargs="+", help="Model families (e.g., qwen llama)")
    parser.add_argument("--sizes", "-s", nargs="+", default=["L", "M", "S"], help="Model sizes")
    parser.add_argument("--temps", "-t", nargs="+", type=float, default=[0.0], help="Temperatures")
    parser.add_argument("--all-models", action="store_true", help="Run all model families")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls (seconds)")
    args = parser.parse_args()

    models = get_model_list(args.models, args.sizes, args.all_models)
    run(models, args.temps, args.delay)


if __name__ == "__main__":
    main()
