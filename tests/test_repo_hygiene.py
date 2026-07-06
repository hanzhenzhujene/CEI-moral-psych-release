"""Repository hygiene checks for the public-facing release surface."""

from __future__ import annotations

import ast
import csv
import re
from pathlib import Path


ROOT = Path(__file__).parent.parent

PUBLIC_GLOBS = [
    "README.md",
    "CITATION.cff",
    "Makefile",
    ".env.example",
    ".gitignore",
    ".github/workflows/*.yml",
    "CONTRIBUTING.md",
    "docs/*.md",
    "figures/*.md",
    "figures/release/*.svg",
    "results/*.md",
    "results/lm-harness/*.md",
    "results/release/**/*.csv",
    "results/release/**/*.md",
    "results/release/**/*.json",
    "scripts/*",
    "src/**/*.py",
    "tests/*.py",
]

FORBIDDEN_PUBLIC_STRINGS = [
    "/" + "Users/" + "hanzhenzhu",
    "Library/Python/" + "3.9/bin/uv",
    "Desktop/" + "moral-psych-harness/data",
]


def test_public_files_do_not_embed_workstation_specific_paths():
    checked_files: list[Path] = []
    for pattern in PUBLIC_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_dir():
                continue
            if path.name == "test_repo_hygiene.py":
                continue
            checked_files.append(path)
            content = path.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_PUBLIC_STRINGS:
                assert forbidden not in content, f"{forbidden!r} found in {path}"

    assert checked_files, "Expected to scan at least one public-facing file."


def test_gitignore_covers_env_local():
    content = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env.local" in content


def test_openrouter_public_surface_uses_selected_grid_label():
    paths = [
        ROOT / "README.md",
        ROOT / ".gitignore",
        ROOT / "scripts" / "openrouter_selected_grid_moral_psych.py",
        ROOT / "scripts" / "run_openrouter_selected_grid_full.sh",
    ]
    for path in ROOT.glob("results/openrouter-selected-grid-moral-psych*/**/*"):
        if path.is_file() and "logs" not in path.parts:
            paths.append(path)

    forbidden = re.compile(r"low[-_ ]cost|openrouter[-_]low[-_]cost", flags=re.IGNORECASE)
    for path in paths:
        assert not forbidden.search(path.read_text(encoding="utf-8")), f"old OpenRouter label found in {path}"


def test_env_example_exists_and_documents_core_inputs():
    env_example = ROOT / ".env.example"
    assert env_example.exists()
    content = env_example.read_text(encoding="utf-8")
    assert "OPENROUTER_API_KEY=" in content
    assert "MINIMAX_API_KEY=" in content
    assert "CEI_MIN_MAX_TOKENS=2048" in content
    assert "UNIMORAL_DATA_DIR=" in content
    assert "SMID_DATA_DIR=" in content
    assert "VALUEPRISM_RELEVANCE_FILE=" in content
    assert "CCD_BENCH_DATA_FILE=" in content
    assert "DENEVIL_DATA_FILE=" in content


def test_root_readme_points_to_final_moral_psych_deliverable():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# CEI Moral-Psych Benchmark Suite")
    assert "github.com/hanzhenzhujene/CEI-moral-psych-release/actions/workflows/ci.yml" in readme
    assert "github.com/Center-for-Ethical-Intelligence/moral-psychology-benchmark/actions/workflows/ci.yml" not in readme
    assert "Jenny Zhu's CEI moral-psych benchmark deliverable" in readme
    assert "## Start Here" in readme
    assert "## Best Results At A Glance" in readme
    assert "## Status: What Is Usable" in readme
    assert "## DATA, CLICK HERE: Result Tables" in readme
    assert "## What To Trust First" in readme
    assert "The public readiness dashboard has `105` model-line x benchmark cells. `72` are Tier 3" in readme
    assert "`33` have no tier because they are blocked, not run, route gaps, data gaps, or proxy-only." in readme
    assert "| `UniMoral RQ1-RQ4` | Text moral reasoning: RQ1-RQ3 use accuracy; RQ4 uses BERTScore F1 and METEOR. | `21/21` Tier 3; `0/21` no tier." in readme
    assert "| `SMID` | Vision moral judgment: moral rating plus foundation classification. | `9/21` Tier 3; `12/21` no tier." in readme
    assert "| `DeNEVIL` | FULCRA-backed proxy behavior from saved traces. | `0/21` Tier 3; `21/21` no tier." in readme
    assert "The main comparison uses three benchmark-faithful accuracy columns." in readme
    assert "benchmark-comparison.csv" not in readme
    assert "Use these three benchmark-specific CSVs for the primary result numbers." in readme
    assert "[unimoral-full-benchmark.csv](results/release/2026-04-19-option1/unimoral-full-benchmark.csv)" in readme
    assert "[smid-results.csv](results/release/2026-04-19-option1/smid-results.csv)" in readme
    assert "[value-kaleidoscope-results.csv](results/release/2026-04-19-option1/value-kaleidoscope-results.csv)" in readme
    assert "[selected-grid readout](results/openrouter-selected-grid-moral-psych-full/README.md)" in readme
    assert "[result_summary.csv](results/openrouter-selected-grid-moral-psych-full/result_summary.csv)" in readme
    assert "[benchmark_summary.csv](results/openrouter-selected-grid-moral-psych-full/benchmark_summary.csv)" in readme
    assert "[model_summary.csv](results/openrouter-selected-grid-moral-psych-full/model_summary.csv)" in readme
    assert "OpenRouter text-only follow-up   results/openrouter-selected-grid-moral-psych-full/" in readme
    assert "it is text-only, excludes SMID/DeNEVIL/MiniMax, and has `102/119` scored rows" in readme
    assert "| Best fully observed comparable line | `MiniMax-S`: UniMoral 0.661, SMID 0.432, Value 0.740; three-metric mean 0.611." in readme
    assert "| Best text-only line | `GPT-5.5`: UniMoral 0.684, Value 0.736; two-metric mean 0.710. No SMID or DeNEVIL route." in readme
    assert "| Best UniMoral RQ4 generation rows | BERTScore F1: `Llama-M` 0.730; METEOR: `GPT-5.5` 0.165." in readme
    assert "UniMoral now has a fresh exact Llama 3.1 RQ1-RQ4 calibration bridge" in readme
    assert "RQ4 METEOR 0.121 and BERTScore F1 0.656" in readme
    assert "CCD-Bench has exact same-model distribution bridges for ten paper routes" in readme
    assert "remaining exact routes are unavailable or blocked rather than substituted" in readme
    assert "[calibration-summary.csv](results/paper-calibration-exact-20260706-unimoral-llama31/calibration-summary.csv)" in readme
    assert "[RQ4 BERTScore rows](results/paper-calibration-exact-20260706-unimoral-llama31/unimoral-rq4-bertscore.csv)" in readme
    assert "[calibration-summary.csv](results/paper-calibration-exact-20260705/calibration-summary.csv)" in readme
    assert "[run-manifest.csv](results/paper-calibration-exact-20260705/run-manifest.csv)" in readme
    assert "`UniMoral action accuracy`" in readme
    assert "`SMID average accuracy`" in readme
    assert "`Value Kaleidoscope average`" in readme
    assert "`CCD-Bench` | Cultural-cluster choice distribution and concentration." in readme
    assert "`DeNEVIL` | FULCRA-backed proxy behavior categories from saved traces." in readme
    assert "## Key Takeaways" in readme
    assert "**Best all-around comparable line:** `MiniMax-S`" in readme
    assert "**Best text-only line:** `GPT-5.5`" in readme
    assert "diagnostic spread" in readme
    assert "UniMoral spans 0.563 to 0.684 across the comparable slice" in readme
    assert "0.048 spread" not in readme
    assert "## Main Figures" in readme
    assert "![UniMoral family-size scaling by RQ](figures/release/option1_unimoral_family_scaling.svg)" in readme
    assert "![UniMoral RQ1-RQ3 heatmap](figures/release/option1_unimoral_task_heatmap.svg)" in readme
    assert "![UniMoral RQ4 generation quality](figures/release/option1_unimoral_generation_quality.svg)" in readme
    assert "![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)" in readme
    assert "![Comparable score spread](figures/release/option1_benchmark_difficulty_profile.svg)" in readme
    assert "![Family scaling profile](figures/release/option1_family_scaling_profile.svg)" in readme
    assert "![CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)" in readme
    assert "![DeNEVIL behavior outcomes](figures/release/option1_denevil_behavior_outcomes.svg)" in readme
    assert "![Paper-result comparison table](figures/release/option1_paper_result_comparison.svg)" in readme
    assert "![Paper-vs-current replication map](figures/release/option1_paper_result_alignment_map.svg)" in readme
    assert readme.count("![") >= 10
    assert "## Result Directory" in readme
    assert "## Readiness Tiers" in readme
    assert "| `T3` | Interpretable: cite/compare it within the stated metric layer. |" in readme
    assert "Current dashboard: `72/105` public summary rows are Tier 3" in readme
    assert "The `105` rows are the `75` family-size cells plus `30` OpenAI text-reference cells." in readme
    assert "Cost/accounting metadata is in the appendix. Current project total: `$897.58`." in readme
    assert "## OpenRouter Selected-Grid Follow-Up" not in readme
    assert "## Results First" not in readme
    assert "### DeepSeek S/M/L Log-Derived Readout" not in readme
    assert "results/release/2026-04-19-option1/README.md" in readme
    assert "figures/release/option1_benchmark_accuracy_bars.svg" in readme
    assert "figures/release/option1_benchmark_difficulty_profile.svg" in readme
    assert "figures/release/option1_unimoral_task_heatmap.svg" in readme
    assert "figures/release/option1_unimoral_generation_quality.svg" in readme
    assert "figures/release/option1_unimoral_family_scaling.svg" in readme
    assert "figures/release/option1_family_scaling_profile.svg" in readme
    assert "figures/release/option1_ccd_choice_distribution.svg" in readme
    assert "figures/release/option1_denevil_behavior_outcomes.svg" in readme
    assert "figures/release/option1_paper_result_alignment_map.svg" in readme
    assert "![Paper-result comparison table](figures/release/option1_paper_result_comparison.svg)" in readme
    assert "![Paper-model calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" not in readme
    assert "[Same-model paper calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" in readme
    assert "Exact paper-model visual bridge only; near-family, blocked, and proxy rows stay out of the plotted comparison." in readme
    assert "[paper-model-calibration-ledger.csv](results/release/2026-04-19-option1/paper-model-calibration-ledger.csv)" in readme
    assert "[paper-model-calibration-bridge.csv](results/release/2026-04-19-option1/paper-model-calibration-bridge.csv)" in readme
    assert "[paper-model-overlap-map.csv](results/release/2026-04-19-option1/paper-model-overlap-map.csv)" in readme
    assert "## UniMoral RQ1-RQ4 Artifact Pointer" in readme
    assert "**DATA, CLICK HERE:**" in readme
    assert "| RQ4 | Consequence generation | BERTScore F1 + METEOR |" in readme
    assert "BERTScore: Llama-M (0.730); METEOR: GPT-5.5 (0.165)" in readme
    assert "RQ1-RQ3 use exact-match accuracy; RQ4 has two higher-better generation rows, BERTScore F1 and METEOR." in readme
    assert "`make bootstrap`" in readme or "make audit" in readme

    figures_readme = (ROOT / "figures/README.md").read_text(encoding="utf-8")
    assert "side" + " metric" not in figures_readme
    assert "## Audience-Facing Result Figures" in figures_readme
    assert "## Appendix QA / Provenance Figures" in figures_readme
    audience_block = figures_readme[
        figures_readme.index("## Audience-Facing Result Figures") : figures_readme.index("## UniMoral figures")
    ]
    appendix_block = figures_readme[figures_readme.index("## Appendix QA / Provenance Figures") :]
    assert "option1_unimoral_family_scaling.svg" in audience_block
    assert "option1_ccd_choice_distribution.svg" in audience_block
    assert "option1_denevil_behavior_outcomes.svg" in audience_block
    assert "option1_paper_result_alignment_map.svg" in audience_block
    assert "option1_family_size_progress_overview.svg" not in audience_block
    assert "option1_coverage_matrix.svg" not in audience_block
    assert "option1_sample_volume.svg" not in audience_block
    assert "option1_family_size_progress_overview.svg" in appendix_block
    assert "option1_coverage_matrix.svg" in appendix_block
    assert "option1_sample_volume.svg" in appendix_block
    assert figures_readme.index("## Audience-Facing Result Figures") < figures_readme.index("## Appendix QA / Provenance Figures")
    assert "two reported generation metrics: BERTScore F1" in figures_readme
    assert "option1_paper_result_comparison.svg" in figures_readme
    assert "option1_paper_model_calibration_bridge.svg" in figures_readme
    assert "## Replication / calibration figures" in figures_readme
    assert "## OpenRouter selected-grid follow-up figures" in figures_readme
    replication_block = figures_readme[
        figures_readme.index("## Replication / calibration figures") : figures_readme.index("## OpenRouter selected-grid follow-up figures")
    ]
    assert "option1_paper_result_alignment_map.svg" in replication_block
    assert "option1_paper_model_calibration_bridge.svg" in replication_block
    assert "option1_paper_result_comparison.svg" in replication_block
    selected_grid_block = figures_readme[
        figures_readme.index("## OpenRouter selected-grid follow-up figures") : figures_readme.index("## Appendix QA / Provenance Figures")
    ]
    assert "within_family_scaling.svg" in selected_grid_block
    assert "time_scaling.svg" in selected_grid_block
    assert "benchmark_score_matrix.svg" in selected_grid_block
    assert "read CCD-Bench as valid-choice behavior, not correctness" in selected_grid_block
    assert "SMID, DeNEVIL, and MiniMax are excluded" in selected_grid_block
    assert figures_readme.index("## Replication / calibration figures") < figures_readme.index("## OpenRouter selected-grid follow-up figures")
    assert figures_readme.index("## OpenRouter selected-grid follow-up figures") < figures_readme.index("## Appendix QA / Provenance Figures")

    unimoral_family_scaling_svg = (ROOT / "figures/release/option1_unimoral_family_scaling.svg").read_text(encoding="utf-8")
    assert "UniMoral family-size scaling by RQ" in unimoral_family_scaling_svg
    assert "OpenAI GPT-5 is the black S/M/L line across RQ1-RQ4" in unimoral_family_scaling_svg
    assert "OpenAI GPT-5 is black and appears across RQ1-RQ4" in unimoral_family_scaling_svg
    assert "GPT-5.5 is strongest inside GPT-5 on RQ2, RQ3, and both RQ4 metrics" in unimoral_family_scaling_svg
    assert "Metric: Accuracy" in unimoral_family_scaling_svg
    assert "Metric: BERTScore F1" in unimoral_family_scaling_svg
    assert "Metric: METEOR" in unimoral_family_scaling_svg

    unimoral_task_spread_svg = (ROOT / "figures/release/option1_unimoral_task_spread.svg").read_text(encoding="utf-8")
    assert "UniMoral RQ1-RQ3 Score Spread: exact-match accuracy" in unimoral_task_spread_svg
    assert "Range is max-min across complete model lines" in unimoral_task_spread_svg
    assert "not proof that the task is solved" in unimoral_task_spread_svg
    assert "RQ4 is excluded here because it uses BERTScore F1 and METEOR generation metrics" in unimoral_task_spread_svg
    assert "saturation" not in unimoral_task_spread_svg.lower()

    paper_calibration_svg = (ROOT / "figures/release/option1_paper_model_calibration_bridge.svg").read_text(encoding="utf-8")
    assert "Same-Model Paper Calibration Bridge" in paper_calibration_svg
    assert "Only exact same-model evidence is plotted here" in paper_calibration_svg
    assert "Llama-3.1-8B Instruct" in paper_calibration_svg
    assert "Mistral Nemo" in paper_calibration_svg
    assert "Llama-3.3-70B-Instruct" in paper_calibration_svg
    assert "Llama-4-Maverick-17B-128E-Instruct" in paper_calibration_svg
    assert "DeepSeek-chat-v3-0324" in paper_calibration_svg
    assert "OpenAI GPT-4.1" in paper_calibration_svg
    assert "Qwen2.5-72B-Instruct" in paper_calibration_svg
    assert "Command-R 08-2024" in paper_calibration_svg
    assert "Microsoft Phi-4" in paper_calibration_svg
    assert "Perplexity Sonar" in paper_calibration_svg
    assert "Claude 4 Sonnet" in paper_calibration_svg
    assert "WizardLM-2-8x22B" in paper_calibration_svg
    assert "Remaining exact-route gaps" in paper_calibration_svg
    assert "Available exact CCD paper routes now have checked" in paper_calibration_svg
    assert "distribution rows. Missing paper routes stay blocked" in paper_calibration_svg
    assert "until exact IDs or data exist." in paper_calibration_svg
    assert "Some paper CCD models are available as exact provider routes" not in paper_calibration_svg

    with (ROOT / "results/release/2026-04-19-option1/paper-model-calibration-bridge.csv").open(newline="", encoding="utf-8") as handle:
        bridge_rows = list(csv.DictReader(handle))
    assert {row["model_match_class"] for row in bridge_rows} == {"exact_same_model"}
    assert {row["paper_model"] for row in bridge_rows} == {
        "Llama-3.1-8B Instruct",
        "Mistral Nemo",
        "Llama-3.3-70B-Instruct",
        "Llama-4-Maverick-17B-128E-Instruct",
        "DeepSeek-chat-v3-0324",
        "Qwen2.5-72B-Instruct",
        "OpenAI GPT-4.1",
        "Command-R 08-2024",
        "Microsoft Phi-4",
        "WizardLM-2-8x22B",
        "Perplexity Sonar",
        "Claude 4 Sonnet",
    }

    with (ROOT / "results/release/2026-04-19-option1/paper-model-calibration-ledger.csv").open(newline="", encoding="utf-8") as handle:
        ledger_rows = list(csv.DictReader(handle))
    assert any(
        row["paper_model"] == "Llama-3.1-8B Instruct"
        and row["repo_evidence_state"] == "current_fresh_verified"
        and "20260706-unimoral-llama31" in row["repo_evidence_path"]
        for row in ledger_rows
    )
    assert any(row["paper_model"] == "Qwen2.5-72B-Instruct" and row["repo_evidence_state"] == "current_fresh_verified" for row in ledger_rows)
    assert any(row["paper_model"] == "Llama-4-Maverick-17B-128E-Instruct" and row["repo_evidence_state"] == "current_release_verified" for row in ledger_rows)
    assert any(row["paper_model"] == "WizardLM-2-8x22B" and row["repo_evidence_state"] == "current_fresh_verified" for row in ledger_rows)
    assert any(row["benchmark"] == "DeNEVIL / MoralPrompt" and "proxy" in row["comparison_boundary"].lower() for row in ledger_rows)

    release_readme = (ROOT / "results/release/2026-04-19-option1/README.md").read_text(encoding="utf-8")
    assert "Fresh exact UniMoral Llama calibration" in release_readme
    assert "results/paper-calibration-exact-20260706-unimoral-llama31/calibration-summary.csv" in release_readme
    assert "results/paper-calibration-exact-20260706-unimoral-llama31/unimoral-rq4-bertscore.csv" in release_readme
    assert "Fresh exact CCD paper-model calibration" in release_readme
    assert "results/paper-calibration-exact-20260705/calibration-summary.csv" in release_readme
    assert "results/paper-calibration-exact-20260705/run-manifest.csv" in release_readme
    assert "Remaining exact routes stay marked unavailable or blocked until the exact model ID exists" in release_readme
    assert "| Tightest comparable spread | `UniMoral` has the tightest range" in release_readme
    assert "not proof of benchmark saturation" in release_readme
    assert "Closest thing to saturation" not in release_readme
    assert "$18.166308` from the full selected-grid OpenRouter follow-up" in release_readme
    assert "$17.760398` from the full selected-grid OpenRouter follow-up" not in release_readme

    paper_comparison_doc = (ROOT / "docs/paper-result-comparison.md").read_text(encoding="utf-8")
    assert "# Paper Result Calibration and Comparison" in paper_comparison_doc
    assert "## Visual Summary" in paper_comparison_doc
    assert "## What This Means" in paper_comparison_doc
    assert "## Benchmark Cards" in paper_comparison_doc
    assert "![Paper-vs-current replication map](../figures/release/option1_paper_result_alignment_map.svg)" in paper_comparison_doc
    assert "![Paper-result comparison table](../figures/release/option1_paper_result_comparison.svg)" in paper_comparison_doc
    assert "![Paper-model calibration bridge](../figures/release/option1_paper_model_calibration_bridge.svg)" in paper_comparison_doc
    assert "[paper-model calibration bridge](../figures/release/option1_paper_model_calibration_bridge.svg)" in paper_comparison_doc
    assert "[paper-result-comparison.csv](../results/release/2026-04-19-option1/paper-result-comparison.csv)" in paper_comparison_doc
    assert "[paper-model-overlap-map.csv](../results/release/2026-04-19-option1/paper-model-overlap-map.csv)" in paper_comparison_doc
    assert "[paper-model-calibration-ledger.csv](../results/release/2026-04-19-option1/paper-model-calibration-ledger.csv)" in paper_comparison_doc
    assert "[paper-model-calibration-bridge.csv](../results/release/2026-04-19-option1/paper-model-calibration-bridge.csv)" in paper_comparison_doc
    assert "fresh exact Llama 3.1 8B UniMoral rerun completed locally" in paper_comparison_doc
    assert "RQ4 offline BERTScore F1 `0.655539`" in paper_comparison_doc
    assert "metric-bridged calibration rather than reproduced paper table values" in paper_comparison_doc
    assert "only exact same-model evidence is plotted" in paper_comparison_doc
    assert "current `Llama-4-Maverick-17B-128E-Instruct`" in paper_comparison_doc
    assert "`WizardLM-2-8x22B`" in paper_comparison_doc
    assert max(len(line) for line in paper_comparison_doc.splitlines()) <= 220

    openrouter_scaling_svg = (ROOT / "results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg").read_text(encoding="utf-8")
    assert "Within-family scaling is mixed" in openrouter_scaling_svg

    openrouter_time_svg = (ROOT / "results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg").read_text(encoding="utf-8")
    assert "Time scaling is not automatic" in openrouter_time_svg

    openrouter_matrix_svg = (ROOT / "results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg").read_text(encoding="utf-8")
    assert "Benchmark comparison matrix" in openrouter_matrix_svg
    assert "CCD is" in openrouter_matrix_svg
    assert "choice-format coverage rather than accuracy" in openrouter_matrix_svg
    assert "GPT 4o-mini 0.711" in unimoral_family_scaling_svg
    assert "GPT-5 nano" in unimoral_family_scaling_svg
    assert "GPT-5 mini" in unimoral_family_scaling_svg
    assert "GPT-5.5" in unimoral_family_scaling_svg
    assert "GPT 4.1-mini" in unimoral_family_scaling_svg
    assert ">Ref<" not in unimoral_family_scaling_svg
    assert "OpenAI GPT-5" in unimoral_family_scaling_svg
    assert "OpenAI Ref" in unimoral_family_scaling_svg
    assert "OpenAI GPT-5 is black and appears across RQ1-RQ4" in unimoral_family_scaling_svg
    assert 'stroke="#000000"' in unimoral_family_scaling_svg
    assert 'fill="#000000"' in unimoral_family_scaling_svg
    assert "#dc2626" in unimoral_family_scaling_svg

    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    paper_alignment_svg = (ROOT / "figures/release/option1_paper_result_alignment_map.svg").read_text(encoding="utf-8")
    paper_result_comparison_svg = (ROOT / "figures/release/option1_paper_result_comparison.svg").read_text(encoding="utf-8")
    release_readme = (ROOT / "results/release/2026-04-19-option1/README.md").read_text(encoding="utf-8")
    family_scaling_summary_csv = (ROOT / "results/release/2026-04-19-option1/family-scaling-summary.csv").read_text(encoding="utf-8")
    paper_result_comparison_csv = (ROOT / "results/release/2026-04-19-option1/paper-result-comparison.csv").read_text(encoding="utf-8")
    paper_model_overlap_csv = (ROOT / "results/release/2026-04-19-option1/paper-model-overlap-map.csv").read_text(encoding="utf-8")
    calibration_surfaces = "\n".join([root_readme, paper_comparison_doc, paper_calibration_svg, paper_alignment_svg, paper_result_comparison_svg, release_readme, family_scaling_summary_csv, paper_result_comparison_csv, paper_model_overlap_csv])
    assert "same RQ1 metric" not in calibration_surfaces
    assert "original paper table values are not tracked" not in calibration_surfaces
    assert "clean paper-faithful metric overlap" not in calibration_surfaces
    assert "I found `CCD-Bench`" not in calibration_surfaces
    assert "same/near" not in calibration_surfaces
    assert "Same/near" not in calibration_surfaces
    assert "calibration points" not in calibration_surfaces
    assert "GPT-5-mini Ref" not in calibration_surfaces
    assert "best OpenAI text row: GPT-5 mini 0.739" in calibration_surfaces
    assert "visible paper metric anchors" in calibration_surfaces
    assert paper_result_comparison_svg.count("UniMoral RQ4 consequence") == 2
    assert "generation - BERTScore F1" in paper_result_comparison_svg
    assert "generation - METEOR" in paper_result_comparison_svg
    assert "Best current METEOR: GPT-5.5 0.165" in paper_result_comparison_svg
    assert "METEOR: Llama-L 0.157; BLEU" not in paper_result_comparison_svg

    openai_reference_doc = (ROOT / "docs" / "openai-reference-runs.md").read_text(encoding="utf-8")
    assert "Use the benchmark-specific result tables first" in openai_reference_doc
    assert "benchmark-comparison.csv` is a supporting generated summary for figures, not the main OpenAI data entry" in openai_reference_doc


def test_repository_root_keeps_legacy_files_archived():
    legacy_root_files = {
        "PROGRESS.md",
        "STATUS.md",
        "moral-psychology-benchmarks.md",
        "openrouter-setup.md",
        "trolleybench-plan.md",
        "client.py",
        "config.py",
        "run_benchmark.py",
        "run_trolleybench.py",
        "eval_trolleybench.py",
        "export_results.py",
        "run_all_benchmarks.sh",
        "run_one_model.sh",
        "run_parallel_remaining.sh",
    }

    for filename in legacy_root_files:
        assert not (ROOT / filename).exists(), f"Move legacy root clutter into docs/, scripts/, or tools/: {filename}"

    assert (ROOT / "docs" / "status" / "PROGRESS.md").exists()
    assert (ROOT / "docs" / "plans" / "trolleybench-plan.md").exists()
    assert (ROOT / "scripts" / "legacy-openrouter" / "run_all_benchmarks.sh").exists()
    assert (ROOT / "tools" / "legacy_openrouter" / "run_trolleybench.py").exists()


def test_docs_index_mentions_repo_architecture():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "repo-architecture.md" in docs_index
    assert "evaluation-methodology.md" in docs_index
    assert "../results/openrouter-selected-grid-moral-psych-full/README.md" in docs_index
    assert "separate text-only OpenRouter selected-grid follow-up" in docs_index


def test_ci_workflow_uses_native_node24_action_releases() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "actions/checkout@v5" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "astral-sh/setup-uv@v8.1.0" in workflow
    assert "actions/checkout@v4" not in workflow
    assert "actions/setup-python@v5" not in workflow
    assert "astral-sh/setup-uv@v5" not in workflow
    assert "make bootstrap" in workflow


def test_supporting_docs_track_current_release_artifacts_and_boundaries():
    reproducibility = (ROOT / "docs" / "reproducibility.md").read_text(encoding="utf-8")
    assert "ccd-choice-distribution.csv" in reproducibility
    assert "denevil-behavior-summary.csv" in reproducibility
    assert "denevil-proxy-summary.csv" in reproducibility
    assert "option1_ccd_choice_distribution.svg" in reproducibility
    assert "option1_denevil_behavior_outcomes.svg" in reproducibility
    assert "appendix QA artifacts" in reproducibility

    figures_readme = (ROOT / "figures" / "README.md").read_text(encoding="utf-8")
    assert "## CCD-Bench figures" in figures_readme
    assert "## DeNEVIL figures" in figures_readme
    assert "option1_ccd_choice_distribution.svg" in figures_readme
    assert "option1_denevil_behavior_outcomes.svg" in figures_readme
    assert "appendix QA / provenance" in figures_readme
    assert "Appendix QA / Provenance Figures" in figures_readme

    results_readme = (ROOT / "results" / "README.md").read_text(encoding="utf-8")
    assert "## Public Result Layers" in results_readme
    assert "## OpenRouter Selected-Grid Follow-Up" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/result_summary.csv" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/benchmark_summary.csv" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/model_summary.csv" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg" in results_readme
    assert "separate from the frozen Option 1 ranking surface" in results_readme
    assert "`benchmark-comparison.csv` is a supporting generated summary for figures, not the main data entry point" in results_readme
    assert "CCD-Bench is valid-choice behavior, not accuracy" in results_readme
    assert "ccd-choice-distribution.csv" in results_readme
    assert "denevil-behavior-summary.csv" in results_readme
    assert "Appendix QA / provenance" in results_readme

    scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
    assert "one canonical reporting path" in scripts_readme
    assert "build_release_artifacts.py" in scripts_readme
    assert "DeNEVIL proxy evidence package" in scripts_readme
    assert "provider_config.sh" in scripts_readme
    assert "MINIMAX_API_KEY" in scripts_readme
    assert "CEI_MIN_MAX_TOKENS=2048" in scripts_readme


def test_pr6_launchers_now_use_provider_routing_for_direct_provider_reruns():
    family_launcher = (ROOT / "scripts" / "family_size_text_expansion.sh").read_text(encoding="utf-8")
    minimax_launcher = (ROOT / "scripts" / "full_option1_runs_minimax_small.sh").read_text(encoding="utf-8")

    for content in (family_launcher, minimax_launcher):
        assert "provider_config.sh" in content
        assert "setup_model_provider" in content
        assert "--model_base_url" in content
        assert "routing_metadata.csv" in content
        assert 'cd "$ROOT"' in content


def test_root_readme_links_release_methodology_and_summary_paths():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/evaluation-methodology.md" in readme or "results/release/2026-04-19-option1/README.md" in readme
    assert "results/release/2026-04-19-option1/README.md" in readme
    assert "results/release/2026-04-19-option1/jenny-group-report.md" in readme


def test_evaluation_methodology_versions_current_metric_definition():
    methodology = (ROOT / "docs" / "evaluation-methodology.md").read_text(encoding="utf-8")
    assert "Current public metric definition version" in methodology
    assert "`2026-04-30`" in methodology
    assert "no longer an RQ1-only surface" in methodology
    assert "RQ1-RQ3 use exact-match accuracy" in methodology
    assert "RQ4 consequence generation appears as two presentation rows per model line" in methodology
    assert "BERTScore F1 plus METEOR as the two headline generation metrics" in methodology
    assert "do not collapse RQ1-RQ4 into one universal moral score" in methodology
    assert "the release should describe current UniMoral release results as action-prediction accuracy" not in methodology
    assert "The current release summary covers RQ1 action prediction only" not in methodology

    how_to_read = (ROOT / "docs" / "how-to-read-results.md").read_text(encoding="utf-8")
    assert "## Result Packages" in how_to_read
    assert "OpenAI text-reference rows" in how_to_read
    assert "OpenRouter selected-grid follow-up" in how_to_read
    assert "results/openrouter-selected-grid-moral-psych-full/" in how_to_read
    assert "Separate from the frozen ranking surface" in how_to_read
    assert "excludes SMID, DeNEVIL, and MiniMax" in how_to_read
    assert "larger in-progress matrix" not in how_to_read


def test_core_python_modules_have_module_docstrings():
    checked: list[Path] = []
    for pattern in ("scripts/*.py", "src/**/*.py"):
        for path in ROOT.glob(pattern):
            if path.is_dir():
                continue
            module = ast.parse(path.read_text(encoding="utf-8"))
            checked.append(path)
            assert ast.get_docstring(module), f"Missing module docstring: {path}"

    assert checked, "Expected to scan at least one core Python module."
