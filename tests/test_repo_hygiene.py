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


def test_public_reader_surfaces_use_denevil_display_name():
    display_paths = [
        ROOT / "README.md",
        ROOT / "docs" / "how-to-read-results.md",
        ROOT / "docs" / "evaluation-methodology.md",
        ROOT / "docs" / "data-access.md",
        ROOT / "docs" / "reproducibility.md",
        ROOT / "docs" / "repo-architecture.md",
        ROOT / "scripts" / "README.md",
        ROOT / "results" / "release" / "2026-04-19-option1" / "README.md",
        ROOT / "results" / "release" / "2026-04-19-option1" / "jenny-group-report.md",
        ROOT / "results" / "release" / "2026-04-19-option1" / "topline-summary.md",
        ROOT / "results" / "release" / "2026-04-19-option1" / "release-manifest.json",
        ROOT / "results" / "release" / "2026-04-19-option1" / "topline-summary.json",
    ]
    display_paths.extend((ROOT / "figures" / "release").glob("*.svg"))

    for path in display_paths:
        text = path.read_text(encoding="utf-8")
        assert "Denevil" not in text, f"old DeNEVIL display spelling found in {path}"


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
    assert "## Visual Read In 90 Seconds" in readme
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
    assert "[completion audit](results/openrouter-selected-grid-moral-psych-full/completion_audit.md)" in readme
    assert "[retry log](results/openrouter-selected-grid-moral-psych-full/targeted-retry-log.md)" in readme
    assert "[family scaling](results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg)" in readme
    assert "[time scaling](results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg)" in readme
    assert "[benchmark matrix](results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg)" in readme
    assert "[detailed task matrix](results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg)" in readme
    assert "OpenRouter text-only follow-up   results/openrouter-selected-grid-moral-psych-full/" in readme
    assert "it is text-only, excludes SMID/DeNEVIL/MiniMax, and has `102/119` scored rows" in readme
    assert readme.index("## Start Here") < readme.index("## Visual Read In 90 Seconds")
    assert readme.index("## Visual Read In 90 Seconds") < readme.index("## Best Results At A Glance")
    assert "Use this path when a reviewer or team lead wants the story before the tables." in readme
    assert "| Step | Open | Say this plainly |" in readme
    assert "[UniMoral family-size scaling](figures/release/option1_unimoral_family_scaling.svg)" in readme
    assert "GPT-5 is the black text-only S/M/L line" in readme
    assert "[SMID/Value accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)" in readme
    assert "SMID is the current visual-moral bottleneck" in readme
    assert "[CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)" in readme
    assert "cultural-choice behavior relative to a 10% uniform baseline, not right/wrong accuracy" in readme
    assert "[same-model CCD calibration bars](figures/release/option1_paper_result_alignment_map.svg)" in readme
    assert "[calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" in readme
    assert "Calibration bars include only exact same-model/same-metric rows" in readme
    assert "[DeNEVIL proxy behavior](figures/release/option1_denevil_behavior_outcomes.svg)" in readme
    assert "not paper-faithful MoralPrompt scoring and not Tier 3" in readme
    assert "| Best fully observed comparable line | `MiniMax-S`: UniMoral RQ1/action 0.661, SMID 0.432, Value 0.740; three-metric mean 0.611." in readme
    assert "| Best fully observed comparable line | `MiniMax-S`: UniMoral RQ1/action 0.661, SMID 0.432, Value 0.740; three-metric mean 0.611. | [UniMoral CSV](results/release/2026-04-19-option1/unimoral-full-benchmark.csv), [SMID CSV](results/release/2026-04-19-option1/smid-results.csv), [Value CSV](results/release/2026-04-19-option1/value-kaleidoscope-results.csv), [SMID/Value bars](figures/release/option1_benchmark_accuracy_bars.svg) |" in readme
    assert "| Best text-only line | `GPT-5.5`: UniMoral RQ1/action 0.684, Value 0.736; two-metric mean 0.710. No SMID or DeNEVIL route." in readme
    assert "| Best UniMoral RQ4 generation rows | BERTScore F1: `Llama-M` 0.730; METEOR: `GPT-5.5` 0.165." in readme
    assert "UniMoral now has a fresh exact Llama 3.1 RQ1-RQ4 calibration bridge" in readme
    assert "RQ4 METEOR 0.121 and BERTScore F1 0.656" in readme
    assert "CCD-Bench has 11 exact same-model distribution bridges with a shared Nordic-share metric" in readme
    assert "remaining routes are unavailable, blocked, non-exact, or metric-mismatched rather than substituted" in readme
    assert "[calibration-summary.csv](results/paper-calibration-exact-20260706-unimoral-llama31/calibration-summary.csv)" in readme
    assert "[RQ4 BERTScore rows](results/paper-calibration-exact-20260706-unimoral-llama31/unimoral-rq4-bertscore.csv)" in readme
    assert "[calibration-summary.csv](results/paper-calibration-exact-20260705/calibration-summary.csv)" in readme
    assert "[run-manifest.csv](results/paper-calibration-exact-20260705/run-manifest.csv)" in readme
    assert "[same-model bridge table](results/release/2026-04-19-option1/paper-model-calibration-bridge.csv)" in readme
    assert "[calibration ledger](results/release/2026-04-19-option1/paper-model-calibration-ledger.csv)" in readme
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
    assert "### Visual Contract" in readme
    assert "| Visual category | What it supports | Do not use it for |" in readme
    assert "| Headline result | Current result claims within one metric layer. | One universal moral score across unlike benchmarks. |" in readme
    assert "| Calibration | Exact same-model/same-metric bridges, or clearly labeled context tables. | Non-exact model comparisons or proxy substitution. |" in readme
    assert "| Follow-up | Separate sweeps that add context beyond the frozen Option 1 package. | Replacing the primary release ranking surface. |" in readme
    assert "| QA / provenance | Coverage, parser health, route status, sample volume, and proxy trace boundaries. | Performance leaderboards. |" in readme
    assert readme.index("### Visual Contract") < readme.index("### Figure Shortcuts")
    assert "For a 3-minute skim, use only the first shortcut row." in readme
    assert "| Category | Open in this order | Figure | What it answers |" in readme
    assert "| Headline | 1 | [UniMoral family-size scaling](figures/release/option1_unimoral_family_scaling.svg)" in readme
    assert "| UniMoral deep dive | 2 | [UniMoral four-task dashboard](figures/release/option1_unimoral_four_task_dashboard.svg)" in readme
    assert "| Headline | 7 | [Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)" in readme
    assert "| Headline | 8 | [Comparable accuracy heatmap](figures/release/option1_accuracy_heatmap.svg)" in readme
    assert "| Behavior | 11 | [CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)" in readme
    assert "| Behavior | 12 | [CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)" in readme
    assert "| Calibration | 15 | [Same-model CCD calibration bar chart](figures/release/option1_paper_result_alignment_map.svg)" in readme
    assert "| Calibration | 16 | [Same-model paper calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" in readme
    assert "| Calibration context | 17 | [Paper-result context table](figures/release/option1_paper_result_comparison.svg)" in readme
    assert "![UniMoral family-size scaling by RQ](figures/release/option1_unimoral_family_scaling.svg)" in readme
    assert "![UniMoral four-task dashboard](figures/release/option1_unimoral_four_task_dashboard.svg)" in readme
    assert "![UniMoral RQ1-RQ3 heatmap](figures/release/option1_unimoral_task_heatmap.svg)" in readme
    assert "![UniMoral RQ4 generation quality](figures/release/option1_unimoral_generation_quality.svg)" in readme
    assert "![UniMoral task rankings](figures/release/option1_unimoral_task_rankings.svg)" in readme
    assert "![UniMoral task spread](figures/release/option1_unimoral_task_spread.svg)" in readme
    assert "![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)" in readme
    assert "![Comparable accuracy heatmap](figures/release/option1_accuracy_heatmap.svg)" in readme
    assert "![Comparable score spread](figures/release/option1_benchmark_difficulty_profile.svg)" in readme
    assert "![Family scaling profile](figures/release/option1_family_scaling_profile.svg)" in readme
    assert "![CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)" in readme
    assert "![CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)" in readme
    assert "![DeNEVIL behavior outcomes](figures/release/option1_denevil_behavior_outcomes.svg)" in readme
    assert "![DeNEVIL prompt-family heatmap](figures/release/option1_denevil_prompt_family_heatmap.svg)" in readme
    assert "![Same-model CCD calibration bar chart](figures/release/option1_paper_result_alignment_map.svg)" in readme
    assert "![Same-model paper calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" in readme
    assert "![Paper-result context table](figures/release/option1_paper_result_comparison.svg)" in readme
    assert "![Family-size progress overview](figures/release/option1_family_size_progress_overview.svg)" in readme
    assert "![Coverage matrix](figures/release/option1_coverage_matrix.svg)" in readme
    assert "![Sample volume](figures/release/option1_sample_volume.svg)" in readme
    assert "![CCD valid-choice coverage](figures/release/option1_ccd_valid_choice_coverage.svg)" in readme
    assert "![DeNEVIL proxy status matrix](figures/release/option1_denevil_proxy_status_matrix.svg)" in readme
    assert "![DeNEVIL proxy sample volume](figures/release/option1_denevil_proxy_sample_volume.svg)" in readme
    assert "![DeNEVIL proxy visible-response coverage](figures/release/option1_denevil_proxy_valid_response_rate.svg)" in readme
    assert "![DeNEVIL proxy pipeline](figures/release/option1_denevil_proxy_pipeline.svg)" in readme
    assert "Secondary QA/provenance figures are also embedded below" in readme
    assert "### Figure Shortcuts" in readme
    assert "| If you have... | Open these first | What to say |" in readme
    assert "| 3 minutes | [UniMoral family-size scaling](figures/release/option1_unimoral_family_scaling.svg), [Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg), [CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg) |" in readme
    assert "| Paper calibration questions | [same-model CCD bar chart](figures/release/option1_paper_result_alignment_map.svg), [same-model bridge](figures/release/option1_paper_model_calibration_bridge.svg), [paper-result context](figures/release/option1_paper_result_comparison.svg) |" in readme
    assert "Only exact same-model, same-metric rows become bar comparisons; context/proxy rows stay separate." in readme
    assert "| Secondary QA / provenance visual evidence | What it answers |" in readme
    assert "| Appendix-only visual evidence | What it answers |" not in readme
    assert "Progress QA: shows which family-size cells are complete" in readme
    assert "| [Coverage matrix](figures/release/option1_coverage_matrix.svg) | Which Qwen/DeepSeek/Gemma cells were paper-setup, proxy-only, or absent in frozen Option 1? |" in readme
    assert "Coverage QA: frozen Option 1 Qwen/DeepSeek/Gemma slice only" in readme
    assert "hatched cells are absent from that release slice, not low scores" in readme
    assert "CCD parser QA: visible `1-10` choice coverage only" in readme
    assert "DeNEVIL route QA: proxy route and status provenance only; no Tier 3 benchmark-faithful claim." in readme
    assert readme.count("![") >= 32
    assert "| Separate follow-up visual evidence | What it answers |" in readme
    assert "[Selected-grid family scaling](results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg)" in readme
    assert "[Selected-grid time scaling](results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg)" in readme
    assert "[Selected-grid benchmark matrix](results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg)" in readme
    assert "[Selected-grid detailed task matrix](results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg)" in readme
    assert "![Selected-grid family scaling](results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg)" in readme
    assert "![Selected-grid time scaling](results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg)" in readme
    assert "![Selected-grid benchmark matrix](results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg)" in readme
    assert "![Selected-grid detailed task matrix](results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg)" in readme
    assert "| Exploratory follow-up visual evidence | What it answers |" in readme
    assert "[May 13 UniMoral accuracy](figures/exploratory/additional_model_sweep_unimoral_accuracy.svg)" in readme
    assert "[May 13 size/capability readout](figures/exploratory/additional_model_sweep_scaling.svg)" in readme
    assert "[May 13 CCD concentration](figures/exploratory/additional_model_sweep_ccd_dominant_share.svg)" in readme
    assert "![May 13 additional-model UniMoral accuracy](figures/exploratory/additional_model_sweep_unimoral_accuracy.svg)" in readme
    assert "![May 13 additional-model size and capability readout](figures/exploratory/additional_model_sweep_scaling.svg)" in readme
    assert "![May 13 additional-model CCD concentration](figures/exploratory/additional_model_sweep_ccd_dominant_share.svg)" in readme
    assert "Exploratory follow-up figures    figures/exploratory/" in readme
    assert "Separate from the frozen Option 1 ranking surface." in readme
    assert "CCD-Bench remains valid-choice behavior, not accuracy." in readme
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
    assert "figures/release/option1_accuracy_heatmap.svg" in readme
    assert "figures/release/option1_benchmark_difficulty_profile.svg" in readme
    assert "figures/release/option1_unimoral_task_heatmap.svg" in readme
    assert "figures/release/option1_unimoral_generation_quality.svg" in readme
    assert "figures/release/option1_unimoral_family_scaling.svg" in readme
    assert "figures/release/option1_unimoral_four_task_dashboard.svg" in readme
    assert "figures/release/option1_unimoral_task_rankings.svg" in readme
    assert "figures/release/option1_unimoral_task_spread.svg" in readme
    assert "figures/release/option1_family_scaling_profile.svg" in readme
    assert "figures/release/option1_ccd_choice_distribution.svg" in readme
    assert "figures/release/option1_ccd_dominant_option_share.svg" in readme
    assert "figures/release/option1_denevil_behavior_outcomes.svg" in readme
    assert "figures/release/option1_denevil_prompt_family_heatmap.svg" in readme
    assert "figures/release/option1_paper_result_alignment_map.svg" in readme
    assert "figures/release/option1_paper_model_calibration_bridge.svg" in readme
    assert "figures/release/option1_paper_result_comparison.svg" in readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg" in readme
    assert "![Same-model paper calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" in readme
    assert "![Paper-result context table](figures/release/option1_paper_result_comparison.svg)" in readme
    assert "Use this first: scaling is not uniform across UniMoral RQ1-RQ4" in readme
    assert "the current leaders are `Llama-M` on BERTScore F1 and `GPT-5.5` on METEOR" in readme
    assert "`Qwen-L` is the current SMID leader at 0.483" in readme
    assert "`MiniMax-L` is the current Value leader at 0.741" in readme
    assert "dominant shares ranging from 13.8% to 27.8%" in readme
    assert "11 exact CCD-Bench rows are plotted on the shared Nordic-share metric" in readme
    assert "Bridge view: exact same-model calibration rows are visible, including the fresh Llama 3.1 UniMoral bridge" in readme
    assert "Context view: paper metric anchors are shown for orientation" in readme
    assert "[paper-model-calibration-ledger.csv](results/release/2026-04-19-option1/paper-model-calibration-ledger.csv)" in readme
    assert "[paper-model-calibration-bridge.csv](results/release/2026-04-19-option1/paper-model-calibration-bridge.csv)" in readme
    assert "[paper-model-overlap-map.csv](results/release/2026-04-19-option1/paper-model-overlap-map.csv)" in readme
    assert "## UniMoral RQ1-RQ4 Artifact Pointer" in readme
    assert "**DATA, CLICK HERE:**" in readme
    assert "| RQ4 | Consequence generation | BERTScore F1 + METEOR |" in readme
    assert "BERTScore: Llama-M (0.730); METEOR: GPT-5.5 (0.165)" in readme
    assert "RQ1-RQ3 use exact-match accuracy; RQ4 has two higher-better generation rows, BERTScore F1 and METEOR." in readme
    assert "| Text response selection | Selection |" not in readme
    assert "Text response selection | Ten-option cultural-choice selection/distribution" in readme
    assert "`make bootstrap`" in readme or "make audit" in readme
    assert "Legacy generated PNGs            figures/generated/ (not the current release surface)" in readme

    figures_readme = (ROOT / "figures/README.md").read_text(encoding="utf-8")
    assert "side" + " metric" not in figures_readme
    assert "## Audience-Facing Result Figures" in figures_readme
    assert "### What To Say From The Figures" in figures_readme
    assert "### Visual Contract" in figures_readme
    assert figures_readme.index("### What To Say From The Figures") < figures_readme.index("### Visual Contract")
    assert "| Headline result | Current result claims within one metric layer. | One universal moral score across unlike benchmarks. |" in figures_readme
    assert figures_readme.index("### Visual Contract") < figures_readme.index("| Category | Order | Open | Use it for | Read it as |")
    assert "## Figure Bundles" in figures_readme
    assert "## Secondary QA / Provenance Figures" in figures_readme
    assert "## Legacy Generated PNGs" in figures_readme
    assert "`figures/generated/*.png` are older generated chart outputs kept for historical continuity and teammate context." in figures_readme
    assert "not the current publication-facing release surface" in figures_readme
    assert "## Appendix QA / Provenance Figures" not in figures_readme
    audience_block = figures_readme[
        figures_readme.index("## Audience-Facing Result Figures") : figures_readme.index("## Figure Bundles")
    ]
    bundle_block = figures_readme[
        figures_readme.index("## Figure Bundles") : figures_readme.index("## UniMoral figures")
    ]
    appendix_block = figures_readme[figures_readme.index("## Secondary QA / Provenance Figures") :]
    assert "| Topic | Short readout | Boundary |" in audience_block
    assert "Scaling is not uniform across RQ1-RQ4" in audience_block
    assert "current RQ4 leaders are `Llama-M` on BERTScore F1 and `GPT-5.5` on METEOR" in audience_block
    assert "`Qwen-L` is the current SMID leader at 0.483" in audience_block
    assert "`MiniMax-L` is the current Value leader at 0.741" in audience_block
    assert "SMID has only 9 of 21 model-line cells scored" in audience_block
    assert "dominant shares ranging from 13.8% to 27.8%" in audience_block
    assert "CCD-Bench is cultural-choice behavior relative to a 10% uniform baseline, not accuracy or correctness" in audience_block
    assert "Proxy-only FULCRA evidence; no Tier 3 benchmark-faithful MoralPrompt scoring claim" in audience_block
    assert "11 exact rows on the shared Nordic-share metric: 10 fresh reruns plus 1 current release row" in audience_block
    assert "fresh Llama 3.1 UniMoral exact rerun" in audience_block
    assert "| Category | Order | Open | Use it for | Read it as |" in audience_block
    assert "This list mirrors the first part of the root README `Main Figures` section" in audience_block
    assert "Paper metric anchors and release-result context." in audience_block
    assert "[UniMoral family-size scaling](release/option1_unimoral_family_scaling.svg)" in audience_block
    assert "[UniMoral four-task dashboard](release/option1_unimoral_four_task_dashboard.svg)" in audience_block
    assert "[UniMoral task rankings](release/option1_unimoral_task_rankings.svg)" in audience_block
    assert "[UniMoral task spread](release/option1_unimoral_task_spread.svg)" in audience_block
    assert "[Comparable accuracy bars](release/option1_benchmark_accuracy_bars.svg)" in audience_block
    assert "[Comparable accuracy heatmap](release/option1_accuracy_heatmap.svg)" in audience_block
    assert "[CCD choice distribution](release/option1_ccd_choice_distribution.svg)" in audience_block
    assert "[CCD dominant-option share](release/option1_ccd_dominant_option_share.svg)" in audience_block
    assert "[DeNEVIL behavior outcomes](release/option1_denevil_behavior_outcomes.svg)" in audience_block
    assert "[DeNEVIL prompt-family heatmap](release/option1_denevil_prompt_family_heatmap.svg)" in audience_block
    assert "[Same-model CCD calibration bar chart](release/option1_paper_result_alignment_map.svg)" in audience_block
    assert "[Same-model paper calibration bridge](release/option1_paper_model_calibration_bridge.svg)" in audience_block
    assert "[Paper-result context table](release/option1_paper_result_comparison.svg)" in audience_block
    assert "Context only; not a same-model bar comparison." in audience_block
    assert "Task-by-task scaling, not one overall moral score." in audience_block
    assert "RQ1-RQ3 are accuracy; RQ4 is generation quality." in audience_block
    assert "Presence/absence scan; hatched cells are not low scores." in audience_block
    assert "Rankings within tasks, not one collapsed moral score." in audience_block
    assert "Diagnostic separation, not proof of saturation." in audience_block
    assert "Cultural-choice behavior, not accuracy." in audience_block
    assert "Concentration/style summary, not correctness." in audience_block
    assert "Proxy behavior evidence, not MoralPrompt scoring." in audience_block
    assert "Proxy behavior audit, not paper-faithful scoring." in audience_block
    assert "Same-model behavior comparison, not accuracy." in audience_block
    assert "Same-model calibration only; proxy and non-exact rows stay out." in audience_block
    assert "option1_unimoral_family_scaling.svg" in audience_block
    assert "option1_unimoral_four_task_dashboard.svg" in audience_block
    assert "option1_unimoral_task_rankings.svg" in audience_block
    assert "option1_unimoral_task_spread.svg" in audience_block
    assert "option1_accuracy_heatmap.svg" in audience_block
    assert "option1_ccd_choice_distribution.svg" in audience_block
    assert "option1_ccd_dominant_option_share.svg" in audience_block
    assert "option1_denevil_behavior_outcomes.svg" in audience_block
    assert "option1_denevil_prompt_family_heatmap.svg" in audience_block
    assert "option1_paper_result_alignment_map.svg" in audience_block
    assert "option1_paper_model_calibration_bridge.svg" in audience_block
    assert "option1_paper_result_comparison.svg" in audience_block
    assert "option1_family_size_progress_overview.svg" not in audience_block
    assert "option1_coverage_matrix.svg" not in audience_block
    assert "option1_sample_volume.svg" not in audience_block
    assert "option1_accuracy_heatmap.svg" not in appendix_block
    assert "option1_family_size_progress_overview.svg" in appendix_block
    assert "option1_coverage_matrix.svg" in appendix_block
    assert "option1_sample_volume.svg" in appendix_block
    assert "| 3-slide executive read |" in bundle_block
    assert "Text reasoning, SMID/Value accuracy, and CCD behavior are three different result layers." in bundle_block
    assert "| UniMoral deep dive |" in bundle_block
    assert "[four-task dashboard](release/option1_unimoral_four_task_dashboard.svg)" in bundle_block
    assert "RQ1-RQ3 are exact-match accuracy; RQ4 uses BERTScore F1 and METEOR." in bundle_block
    assert "| Calibration / replication review |" in bundle_block
    assert "The visible comparison starts with exact same-model evidence." in bundle_block
    assert "Current-only, blocked, metric-mismatched, non-exact, and proxy evidence stay in tables/context." in bundle_block
    assert "| QA/provenance audit |" in bundle_block
    assert "| Appendix audit |" not in bundle_block
    assert "QA/provenance audit" in bundle_block
    assert "These explain what ran, parsed, and surfaced visibly" in bundle_block
    assert "they are embedded in the root README but are not headline performance figures." in bundle_block
    assert "These explain what ran and parsed; they are not the headline result figures." not in bundle_block
    assert "| OpenRouter follow-up |" in bundle_block
    assert "pilot_scores.svg" in bundle_block
    assert "Separate text-only follow-up; excludes SMID, DeNEVIL, and MiniMax." in bundle_block
    assert figures_readme.index("## Audience-Facing Result Figures") < figures_readme.index("## Secondary QA / Provenance Figures")
    assert figures_readme.index("## Figure Bundles") < figures_readme.index("## UniMoral figures")
    assert "two reported generation metrics: BERTScore F1" in figures_readme
    assert "## Comparable accuracy figures" in figures_readme
    assert "grouped bar chart for the benchmark-faithful SMID and Value accuracy comparison" in figures_readme
    assert "grouped bar chart for the current benchmark-faithful" not in figures_readme
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
        figures_readme.index("## OpenRouter selected-grid follow-up figures") : figures_readme.index("## Secondary QA / Provenance Figures")
    ]
    assert "within_family_scaling.svg" in selected_grid_block
    assert "time_scaling.svg" in selected_grid_block
    assert "benchmark_score_matrix.svg" in selected_grid_block
    assert "pilot_scores.svg" in selected_grid_block
    assert "read CCD-Bench as valid-choice behavior, not correctness" in selected_grid_block
    assert "SMID, DeNEVIL, and MiniMax are excluded" in selected_grid_block
    assert figures_readme.index("## Replication / calibration figures") < figures_readme.index("## OpenRouter selected-grid follow-up figures")
    assert figures_readme.index("## OpenRouter selected-grid follow-up figures") < figures_readme.index("## Secondary QA / Provenance Figures")
    assert "stay labeled as QA/provenance even when they are embedded in the root README" in figures_readme
    assert "stay in appendix-only visuals" not in figures_readme

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
    assert "## Open First" in release_readme
    assert release_readme.index("## Open First") < release_readme.index("## Benchmark Result Visuals")
    assert "| Visual story | [Benchmark Result Visuals](#benchmark-result-visuals), then [TL;DR](#tldr) |" in release_readme
    assert "| Primary result numbers | [Main result files](#data-click-here-main-result-files) |" in release_readme
    assert "| Line status and readiness | [Results First](#results-first), [Status Key](#status-key), [family-size-progress.csv](family-size-progress.csv), [readiness-tier-matrix.csv](readiness-tier-matrix.csv) |" in release_readme
    assert "Tier is result readiness, not model quality; missing cells are route, data, or proxy boundaries." in release_readme
    assert "Exact same-model rows, blocked routes, current-only rows, and proxy-only evidence stay separate." in release_readme
    assert "Fresh exact UniMoral Llama calibration" in release_readme
    assert "results/paper-calibration-exact-20260706-unimoral-llama31/calibration-summary.csv" in release_readme
    assert "results/paper-calibration-exact-20260706-unimoral-llama31/unimoral-rq4-bertscore.csv" in release_readme
    assert "Fresh exact CCD paper-model calibration" in release_readme
    assert "results/paper-calibration-exact-20260705/calibration-summary.csv" in release_readme
    assert "results/paper-calibration-exact-20260705/run-manifest.csv" in release_readme
    assert "Remaining exact routes stay marked unavailable or blocked until the exact model ID exists" in release_readme
    assert "OpenRouter selected-grid follow-up" in release_readme
    assert "results/openrouter-selected-grid-moral-psych-full/result_summary.csv" in release_readme
    assert "results/openrouter-selected-grid-moral-psych-full/benchmark_summary.csv" in release_readme
    assert "results/openrouter-selected-grid-moral-psych-full/model_summary.csv" in release_readme
    assert "results/openrouter-selected-grid-moral-psych-full/targeted-retry-log.md" in release_readme
    assert "../../openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg" in release_readme
    assert "selected-grid detailed task matrix" in release_readme
    assert "`102/119` model-task rows are scored" in release_readme
    assert "Provider/credit blockers stay documented as non-scored evidence limits" in release_readme
    assert "This package excludes SMID, DeNEVIL, and MiniMax; CCD-Bench is valid-choice behavior, not accuracy." in release_readme
    assert "| Tightest comparable spread | `UniMoral` has the tightest range" in release_readme
    assert "not proof of benchmark saturation" in release_readme
    assert "Closest thing to saturation" not in release_readme
    assert "$18.166308` from the full selected-grid OpenRouter follow-up" in release_readme
    assert "$17.760398` from the full selected-grid OpenRouter follow-up" not in release_readme

    paper_comparison_doc = (ROOT / "docs/paper-result-comparison.md").read_text(encoding="utf-8")
    assert "# Paper Result Calibration and Comparison" in paper_comparison_doc
    assert "## Visual Summary" in paper_comparison_doc
    assert "## Safe Citation Matrix" in paper_comparison_doc
    assert "## What This Means" in paper_comparison_doc
    assert "## Benchmark Cards" in paper_comparison_doc
    assert paper_comparison_doc.index("## Safe Citation Matrix") < paper_comparison_doc.index("## TL;DR")
    assert "| If you need to say... | Cite this | Safe wording |" in paper_comparison_doc
    assert "11 exact CCD-Bench rows share the Nordic-share metric: 10 fresh reruns plus 1 verified current row." in paper_comparison_doc
    assert "Fresh exact Llama 3.1 8B RQ1-RQ4 calibration exists, with metric-scale caveats." in paper_comparison_doc
    assert "No. CCD-Bench is cultural-choice distribution and concentration behavior, not correctness." in paper_comparison_doc
    assert "No. Current rows are prompt-based LLM ValuePrism tasks; Kaleido model inference remains blocked." in paper_comparison_doc
    assert "No. Current DeNEVIL evidence is FULCRA proxy behavior until a MoralPrompt-style export exists." in paper_comparison_doc
    assert "![Same-model CCD calibration bar chart](../figures/release/option1_paper_result_alignment_map.svg)" in paper_comparison_doc
    assert "Same-model CCD calibration bar chart: only the 11 exact CCD-Bench rows with a shared Nordic-share metric are plotted." in paper_comparison_doc
    assert "![Paper-result comparison table](../figures/release/option1_paper_result_comparison.svg)" not in paper_comparison_doc
    assert "[paper result context figure](../figures/release/option1_paper_result_comparison.svg)" in paper_comparison_doc
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

    coverage_svg = (ROOT / "figures/release/option1_coverage_matrix.svg").read_text(encoding="utf-8")
    assert "Frozen Option 1 Coverage: Qwen, DeepSeek, Gemma" in coverage_svg
    assert "This matrix is the frozen Option 1 slice only: Qwen, DeepSeek, and Gemma." in coverage_svg
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
    assert "Same-Model CCD Calibration Bar Chart" in paper_alignment_svg
    assert "Only the 11 exact same-model CCD-Bench rows with the same plottable metric appear here." in paper_alignment_svg
    assert "NORDIC EUROPE SHARE: PAPER/SOURCE VS THIS REPO" in paper_alignment_svg
    assert "DELTA" in paper_alignment_svg
    assert paper_alignment_svg.count('data-calibration-row="ccd-exact"') == 11
    assert paper_alignment_svg.count('data-calibration-bar="paper"') == 11
    assert paper_alignment_svg.count('data-calibration-bar="repo"') == 11
    assert "paper/source Nordic share" in paper_alignment_svg
    assert "current exact rerun or verified row" in paper_alignment_svg
    for forbidden in ("DeNEVIL", "MoralPrompt", "UniMoral", "SMID", "Value Kaleidoscope", "ValuePrism", "APV"):
        assert forbidden not in paper_alignment_svg
    for label in (
        "Mistral Nemo",
        "Llama 3.3 70B",
        "Llama 4 Maverick",
        "DeepSeek V3",
        "Qwen2.5 72B",
        "GPT-4.1",
        "Command-R",
        "Phi-4",
        "WizardLM-2",
        "Sonar",
        "Claude 4 Sonnet",
    ):
        assert label in paper_alignment_svg
    assert "19.0%" in paper_alignment_svg
    assert "25.6%" in paper_alignment_svg
    assert "30.6%" in paper_alignment_svg
    assert "30.2%" in paper_alignment_svg
    assert "+6.6 pp" in paper_alignment_svg
    assert "-7.5 pp" in paper_alignment_svg
    assert "This is not an accuracy leaderboard." in paper_alignment_svg
    for forbidden in (
        "DeNEVIL",
        "MoralPrompt",
        "SMID",
        "Value Kaleidoscope",
        "ValuePrism",
        "Kaleido",
        "UniMoral",
        "Qwen-M 99.5",
        "APV",
    ):
        assert forbidden not in paper_alignment_svg
    assert paper_result_comparison_svg.count("UniMoral RQ4 consequence") == 2
    assert "generation - BERTScore F1" in paper_result_comparison_svg
    assert "generation - METEOR" in paper_result_comparison_svg
    assert "Best current METEOR: GPT-5.5 0.165" in paper_result_comparison_svg
    assert "METEOR: Llama-L 0.157; BLEU" not in paper_result_comparison_svg

    openai_reference_doc = (ROOT / "docs" / "openai-reference-runs.md").read_text(encoding="utf-8")
    assert "Use the benchmark-specific result tables first" in openai_reference_doc
    assert "benchmark-comparison.csv` is a supporting generated summary for figures, not the main OpenAI data entry" in openai_reference_doc

    calibration_doc = (ROOT / "docs" / "calibration-replication.md").read_text(encoding="utf-8")
    assert "the July 2026 exact CCD pass has 11 plottable same-model distribution rows" in calibration_doc
    assert "Qwen2.5-72B-Instruct 2,182/2,182 and 21.13%" in calibration_doc
    assert "OpenAI GPT-4.1 2,182/2,182 and 22.27%" in calibration_doc
    assert "Claude 4 Sonnet 2,182/2,182 and 30.25%" in calibration_doc
    assert "Perplexity Sonar 2,182/2,182 and 14.34%" in calibration_doc
    assert "CCD remains distributional behavior, not accuracy" in calibration_doc
    assert "CCD exact same-model overlap: `mistralai/mistral-nemo` saved May 13" not in calibration_doc
    assert "saved OpenAI text references and Qwen/Qwen2.5 rows differ from the exact paper model" not in calibration_doc

    replication_map = (ROOT / "docs" / "paper-model-replication-map.md").read_text(encoding="utf-8")
    assert "July 2026 strict bridge has 11 exact same-model CCD distribution rows" in replication_map
    assert "The saved May 13 Mistral artifact remains saved/prior evidence" in replication_map
    assert "the May 21 Mistral route probe remains route-only evidence" in replication_map
    assert "Use the same-model CCD bar chart and `paper-model-calibration-bridge.csv` for exact rows" in replication_map


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
    assert "unimoral-full-benchmark.csv" in reproducibility
    assert "smid-results.csv" in reproducibility
    assert "value-kaleidoscope-results.csv" in reproducibility
    assert "supporting generated summaries such as `benchmark-comparison.csv`" in reproducibility
    assert "ccd-choice-distribution.csv" in reproducibility
    assert "denevil-behavior-summary.csv" in reproducibility
    assert "denevil-proxy-summary.csv" in reproducibility
    assert "option1_unimoral_family_scaling.svg" in reproducibility
    assert "option1_unimoral_generation_quality.svg" in reproducibility
    assert "option1_ccd_choice_distribution.svg" in reproducibility
    assert "option1_denevil_behavior_outcomes.svg" in reproducibility
    assert "option1_paper_result_comparison.svg" in reproducibility
    assert "option1_paper_result_alignment_map.svg" in reproducibility
    assert "option1_paper_model_calibration_bridge.svg" in reproducibility
    assert "results/openrouter-selected-grid-moral-psych-full/README.md" in reproducibility
    assert "targeted-retry-log.md" in reproducibility
    assert "benchmark_score_matrix.svg" in reproducibility
    assert "pilot_scores.svg" in reproducibility
    assert "### After Rebuild, Open These" in reproducibility
    assert "[`figures/README.md`](../figures/README.md): the one-screen `What To Say From The Figures` talk track" in reproducibility
    assert "[`paper-result-comparison.md#safe-citation-matrix`](paper-result-comparison.md#safe-citation-matrix)" in reproducibility
    assert "Use these files to verify the regenerated public story before presenting or citing it" in reproducibility
    assert "separate OpenRouter text-only follow-up" in reproducibility
    assert "blocked provider/credit rows stay documented outside scored summaries" in reproducibility
    assert "secondary QA/provenance artifacts" in reproducibility

    figures_readme = (ROOT / "figures" / "README.md").read_text(encoding="utf-8")
    assert "## CCD-Bench figures" in figures_readme
    assert "## DeNEVIL figures" in figures_readme
    assert "option1_ccd_choice_distribution.svg" in figures_readme
    assert "option1_denevil_behavior_outcomes.svg" in figures_readme
    assert "secondary QA / provenance" in figures_readme
    assert "Secondary QA / Provenance Figures" in figures_readme
    assert "appendix QA only" not in figures_readme

    results_readme = (ROOT / "results" / "README.md").read_text(encoding="utf-8")
    assert "## Open First" in results_readme
    assert "[`unimoral-full-benchmark.csv`](release/2026-04-19-option1/unimoral-full-benchmark.csv)" in results_readme
    assert "[`smid-results.csv`](release/2026-04-19-option1/smid-results.csv)" in results_readme
    assert "[`value-kaleidoscope-results.csv`](release/2026-04-19-option1/value-kaleidoscope-results.csv)" in results_readme
    assert "[`../figures/README.md`](../figures/README.md)" in results_readme
    assert "[`readiness-tier-matrix.csv`](release/2026-04-19-option1/readiness-tier-matrix.csv)" in results_readme
    assert "[`paper-model-calibration-ledger.csv`](release/2026-04-19-option1/paper-model-calibration-ledger.csv)" in results_readme
    assert "[`openrouter-selected-grid-moral-psych-full/README.md`](openrouter-selected-grid-moral-psych-full/README.md)" in results_readme
    assert "Audience-facing figures are separated from secondary QA/provenance figures." in results_readme
    assert "Tier is result readiness, not model quality." in results_readme
    assert "Separate text-only follow-up; not folded into the frozen Option 1 ranking surface." in results_readme
    assert "## Public Result Layers" in results_readme
    assert "## OpenRouter Selected-Grid Follow-Up" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/result_summary.csv" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/benchmark_summary.csv" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/model_summary.csv" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/targeted-retry-log.md" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg" in results_readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg" in results_readme
    assert "`within_family_scaling.svg`, `time_scaling.svg`, `benchmark_score_matrix.svg`, and `pilot_scores.svg` are the visual entry points" in results_readme
    assert "`completion_audit.md` and `targeted-retry-log.md` document provider/credit blockers" in results_readme
    assert "separate from the frozen Option 1 ranking surface" in results_readme
    assert "`benchmark-comparison.csv` is a supporting generated summary for figures, not the main data entry point" in results_readme
    assert "CCD-Bench is valid-choice behavior, not accuracy" in results_readme
    assert "ccd-choice-distribution.csv" in results_readme
    assert "denevil-behavior-summary.csv" in results_readme
    assert "Secondary QA / provenance" in results_readme

    selected_grid_readme = (ROOT / "results" / "openrouter-selected-grid-moral-psych-full" / "README.md").read_text(encoding="utf-8")
    assert "## Open First" in selected_grid_readme
    assert selected_grid_readme.index("## Open First") < selected_grid_readme.index("Primary outputs:")
    assert "[Figures To Open First](#figures-to-open-first)" in selected_grid_readme
    assert "[result_summary.csv](result_summary.csv), [benchmark_summary.csv](benchmark_summary.csv), [model_summary.csv](model_summary.csv)" in selected_grid_readme
    assert "Scored rows only; provider/error/cancelled rows stay out of score aggregates." in selected_grid_readme
    assert "Provider, credit, content-filter, and stale-route limits are evidence boundaries, not model failures." in selected_grid_readme
    assert "Planning and pricing metadata explain what was attempted; they are not scored benchmark results." in selected_grid_readme
    assert "CCD-Bench is valid-choice behavior; UniMoral RQ4 uses live METEOR-style generation scoring." in selected_grid_readme

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
    for figure in sorted((ROOT / "figures" / "release").glob("option1_*.svg")):
        relative = figure.relative_to(ROOT).as_posix()
        assert re.search(rf"!\[[^\]]+\]\({re.escape(relative)}\)", readme), (
            f"Root README must embed release visual {relative}"
        )
    for relative in (
        "results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg",
        "results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg",
        "results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg",
        "results/openrouter-selected-grid-moral-psych-full/figures/pilot_scores.svg",
        "figures/exploratory/additional_model_sweep_unimoral_accuracy.svg",
        "figures/exploratory/additional_model_sweep_scaling.svg",
        "figures/exploratory/additional_model_sweep_ccd_dominant_share.svg",
    ):
        assert re.search(rf"!\[[^\]]+\]\({re.escape(relative)}\)", readme), (
            f"Root README must embed follow-up visual {relative}"
        )

    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert "../figures/README.md" in docs_index
    assert "one-screen figure talk track" in docs_index
    assert "audience-facing figure order, visual caveats, and secondary QA/provenance figure map" in docs_index
    assert "Safe Citation Matrix" in docs_index
    assert "paper-result-comparison.md#safe-citation-matrix" in docs_index
    assert "appendix/provenance figure map" not in docs_index
    assert "## Visual Reader Path" in docs_index
    assert "Its `What To Say From The Figures` table gives the one-screen talk track." in docs_index
    assert "[`Figure Shortcuts`](../README.md#figure-shortcuts)" in docs_index
    assert "[`Visual Contract`](../README.md#visual-contract)" in docs_index
    assert "UniMoral RQ4 is generation quality rather than accuracy" in docs_index
    assert "CCD-Bench is cultural-choice behavior rather than correctness" in docs_index
    assert "DeNEVIL is proxy behavior rather than paper-faithful MoralPrompt scoring" in docs_index


def test_evaluation_methodology_versions_current_metric_definition():
    methodology = (ROOT / "docs" / "evaluation-methodology.md").read_text(encoding="utf-8")
    assert "Current public metric definition version" in methodology
    assert "`2026-04-30`" in methodology
    assert "no longer an RQ1-only surface" in methodology
    assert "RQ1-RQ3 use exact-match accuracy" in methodology
    assert "RQ4 consequence generation appears as two presentation rows per model line" in methodology
    assert "BERTScore F1 plus METEOR as the two headline generation metrics" in methodology
    assert "do not collapse RQ1-RQ4 into one universal moral score" in methodology
    assert "visible-choice surfacing / parsing failure" in methodology
    assert "paper-aligned `CCD-Bench` choice-quality or human-preference metric beyond the current choice-distribution/concentration surface" in methodology
    assert "keep each metric layer separate" in methodology
    assert "Accuracy/classification/generation metrics, CCD choice-distribution behavior, DeNEVIL proxy behavior, and QA/provenance coverage should not be merged into one scalar story." in methodology
    assert "top row" not in methodology
    assert "top-row" not in methodology
    assert "bottom row" not in methodology
    assert "bottom-row" not in methodology
    assert "coverage alone" not in methodology
    assert "the release should describe current UniMoral release results as action-prediction accuracy" not in methodology
    assert "The current release summary covers RQ1 action prediction only" not in methodology

    how_to_read = (ROOT / "docs" / "how-to-read-results.md").read_text(encoding="utf-8")
    assert "## Result Packages" in how_to_read
    assert "OpenAI text-reference rows" in how_to_read
    assert "OpenRouter selected-grid follow-up" in how_to_read
    assert "results/openrouter-selected-grid-moral-psych-full/" in how_to_read
    assert "Separate from the frozen ranking surface" in how_to_read
    assert "excludes SMID, DeNEVIL, and MiniMax" in how_to_read
    assert "## Visual Reading Order" in how_to_read
    assert "Its `What To Say From The Figures` table is the one-screen talk track" in how_to_read
    assert "If you have only three minutes, use the first shortcut row" in how_to_read
    assert "../README.md#figure-shortcuts" in how_to_read
    assert "../README.md#visual-contract" in how_to_read
    assert "paper-result-comparison.md#safe-citation-matrix" in how_to_read
    assert "exact same-model numeric bars, UniMoral metric-bridged calibration" in how_to_read
    assert "headline result figures support current result claims within one metric layer" in how_to_read
    assert "QA/provenance figures show coverage, parser health, route status, sample volume, or proxy boundaries rather than performance rankings" in how_to_read
    assert "figures/release/option1_unimoral_family_scaling.svg" in how_to_read
    assert "figures/release/option1_unimoral_generation_quality.svg" in how_to_read
    assert "figures/release/option1_ccd_choice_distribution.svg" in how_to_read
    assert "figures/release/option1_denevil_behavior_outcomes.svg" in how_to_read
    assert "Cultural-cluster choice behavior, not right/wrong correctness." in how_to_read
    assert "Proxy behavior from saved traces, not paper-faithful MoralPrompt scoring." in how_to_read
    assert "Same-model CCD-Bench bars only; not accuracy and not a leaderboard." in how_to_read
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
