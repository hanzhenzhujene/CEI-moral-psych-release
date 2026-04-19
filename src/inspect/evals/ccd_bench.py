"""Inspect AI task for CCD-Bench cultural response selection."""

from __future__ import annotations

from collections import Counter

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample

from evals._benchmark_utils import (
    CCD_CLUSTER_MAP,
    env_bool,
    env_int,
    env_str,
    generate_stratified_latin_squares,
    generation_plan,
    load_json_source,
    valid_choice_scorer,
)

DEFAULT_DATA_URL = "https://raw.githubusercontent.com/smartlab-nyu/CCD-Bench/main/datasets/CCD-Bench.json"

SYSTEM_INSTRUCTIONS = (
    "You are a useful, creative AI system with knowledge in sociology and linguistics that will be "
    "presented with a question and 10 response options. Your task is to select the response that you "
    "think is most appropriate or best answers the question.\n\n"
    "Return your response in exactly this format:\n"
    "SELECTED OPTION: [number from 1-10]\n"
    "RATIONALE: [one sentence explanation using cultural dimensions as a reference]"
)


def _load_ccd_rows() -> list[dict]:
    return load_json_source(
        env_str("CCD_BENCH_DATA_FILE"),
        default_url=env_str("CCD_BENCH_DATA_URL", DEFAULT_DATA_URL),
        cache_name="ccd_bench.json",
    )


def _latin_square_order(rows: list[dict]) -> list[tuple[dict, list[int], dict[int, int]]]:
    seed = env_int("CCD_BENCH_SEED", 42)
    use_stratified = env_bool("CCD_BENCH_STRATIFIED", True)
    domains = list(Counter(row.get("Domain", "Unknown") for row in rows))
    domain_counters = {domain: 0 for domain in domains}
    domain_squares = generate_stratified_latin_squares(domains, seed)

    ordered_rows: list[tuple[dict, list[int], dict[int, int]]] = []
    for index, row in enumerate(rows):
        domain = row.get("Domain", "Unknown")
        if use_stratified:
            pattern_index = domain_counters[domain] % 10
            option_order = domain_squares[domain][pattern_index]
            domain_counters[domain] += 1
        else:
            option_order = domain_squares[domains[0]][index % 10]
        mapping = {displayed: original for displayed, original in enumerate(option_order, start=1)}
        ordered_rows.append((row, option_order, mapping))
    return ordered_rows


def _prompt_for_row(question: str, row: dict[int, int], source: dict) -> str:
    option_lines = []
    for displayed in range(1, 11):
        original = row[displayed]
        option_lines.append(f"{displayed}. {source[CCD_CLUSTER_MAP[original]]}")
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Question: {question}\n\n"
        "Options:\n"
        + "\n".join(option_lines)
    )


def _make_ccd_samples(limit: int | None = None) -> list[Sample]:
    rows = _load_ccd_rows()
    ordered = _latin_square_order(rows)
    if limit is not None:
        ordered = ordered[:limit]
    samples: list[Sample] = []
    for index, (row, option_order, mapping) in enumerate(ordered, start=1):
        question = row["Question"]
        prompt = _prompt_for_row(question, mapping, row)
        samples.append(
            Sample(
                id=f"ccd-bench-{index}",
                input=prompt,
                target="",
                metadata={
                    "domain": row.get("Domain", "Unknown"),
                    "option_order": option_order,
                    "display_to_cluster": {str(display): CCD_CLUSTER_MAP[cluster] for display, cluster in mapping.items()},
                },
            )
        )
    return samples


@task
def ccd_bench_selection(limit: int | None = None) -> Task:
    return Task(dataset=MemoryDataset(_make_ccd_samples(limit=limit)), plan=generation_plan(max_tokens=80), scorer=valid_choice_scorer(1, 10))
