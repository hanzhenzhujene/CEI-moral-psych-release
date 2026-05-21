#!/usr/bin/env python3
"""Provider-free task-builder dry run for UniMoral registry entries."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
SRC_INSPECT = ROOT / "src" / "inspect"
sys.path.insert(0, str(SRC_INSPECT))

from run import load_tasks_from_file  # noqa: E402


TASK_NAMES = [
    "unimoral_action_prediction",
    "unimoral_moral_typology",
    "unimoral_factor_attribution",
    "unimoral_consequence_generation",
]


def _fixture_row() -> dict[str, str]:
    return {
        "Scenario_id": "fixture-1",
        "Annotator_id": "ann1",
        "Scenario": "A doctor must decide whether to report a mistake honestly.",
        "Possible_actions": json.dumps(["Hide the mistake", "Report the mistake honestly"]),
        "Selected_action": "2",
        "Action_criteria": "[4, 0, 0, 0]",
        "Contributing_factors": "[0, 4, 0, 0, 0, 0, 0, 0]",
        "Consequence": "[Trust is preserved.]",
        "Moral_values": json.dumps(
            {
                "Care": 1,
                "Equality": 2,
                "Proportionality": 3,
                "Loyalty": 4,
                "Authority": 5,
                "Purity": 6,
            }
        ),
        "Cultural_values": json.dumps(
            {
                "Power Distance": 1,
                "Individualism": 2,
                "Motivation": 3,
                "Uncertainty Avoidance": 4,
                "Long Term Orientation": 5,
                "Indulgence": 6,
            }
        ),
        "Annotator_self_description": "I value honesty.",
    }


def write_fixture(data_dir: Path) -> None:
    row = _fixture_row()
    for filename in ["English_long.csv", "English_short.csv"]:
        with (data_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)


def verify_task_builders() -> list[str]:
    errors: list[str] = []
    task_file = ROOT / "src" / "inspect" / "evals" / "moral_psych.py"
    with TemporaryDirectory(prefix="cei-unimoral-task-builder-") as tmp:
        data_dir = Path(tmp)
        write_fixture(data_dir)

        old_env = {key: os.environ.get(key) for key in ["UNIMORAL_DATA_DIR", "UNIMORAL_LANGUAGE", "UNIMORAL_SAMPLE_INDICES"]}
        os.environ["UNIMORAL_DATA_DIR"] = str(data_dir)
        os.environ["UNIMORAL_LANGUAGE"] = "English"
        os.environ.pop("UNIMORAL_SAMPLE_INDICES", None)
        try:
            factories = load_tasks_from_file(str(task_file))
            factories_by_name = {factory.__name__: factory for factory in factories}
            for task_name in TASK_NAMES:
                factory = factories_by_name.get(task_name)
                if factory is None:
                    errors.append(f"missing task registry entry: {task_name}")
                    continue
                if getattr(factory, "__module__", "") != "moral_psych":
                    errors.append(f"{task_name} is not defined in moral_psych.py")
                    continue
                try:
                    task = factory(limit=1)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{task_name} failed to build: {type(exc).__name__}: {exc}")
                    continue
                if getattr(task, "dataset", None) is None:
                    errors.append(f"{task_name} built without a dataset")
                if getattr(task, "scorer", None) is None:
                    errors.append(f"{task_name} built without a scorer")
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    return errors


def main() -> int:
    errors = verify_task_builders()
    if errors:
        print("UniMoral task-builder verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("UniMoral task-builder verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
