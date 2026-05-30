"""Repository hygiene checks for the public-facing release surface."""

from __future__ import annotations

import ast
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
    assert "Jenny Zhu's CEI moral-psych benchmark deliverable" in readme
    assert "## Public Quickstart" in readme
    assert "## Deliverables To Use Today" in readme
    assert 'Current project total cost: `$888.06`' in readme
    assert "| Main visual story | What are the benchmark results, and how should each graph be read? | [Benchmark Result Visuals](#benchmark-result-visuals) |" in readme
    assert "| Tier / progress dashboard | Which `model line x benchmark` cells are interpretable now? `87` of `105` cells are Tier 3; `18` are blocked or not run. | [readiness-tier-matrix.csv](results/release/2026-04-19-option1/readiness-tier-matrix.csv) |" in readme
    assert "| Paper comparison / calibration map | What did the original benchmark papers run, what did this repo run, and what can be compared safely? | [calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg), [paper-result-alignment.csv](results/release/2026-04-19-option1/paper-result-alignment.csv), and [paper-result-comparison.md](docs/paper-result-comparison.md) |" in readme
    assert "| OpenRouter selected-grid follow-up | What happened when the text-only OpenRouter grid was run across UniMoral RQ1-RQ4, ValuePrism, and CCD-Bench? | [full readout](results/openrouter-selected-grid-moral-psych-full/README.md), [interpretation](results/openrouter-selected-grid-moral-psych-full/interpretation.md), and [completion audit](results/openrouter-selected-grid-moral-psych-full/completion_audit.md) |" in readme
    assert "## Result Readiness Progress" in readme
    assert "| `T1` | Harness complete | A number exists; no guarantee it is meaningful. |" in readme
    assert "| `T2` | Result valid | No format failure, missing modality, or proxy substitution. |" in readme
    assert "| `T3` | Interpretable | Can be cited and compared across models without caveats. |" in readme
    assert "| `SMID` | 9/21 | 12/21 | Only vision-capable routes receive a tier; text-only routes stay blocked as route gaps. |" in readme
    assert "## Replication And Calibration Snapshot" in readme
    assert "compare each implemented benchmark against its original paper" in readme
    assert "| `CCD-Bench` | Current choice-distribution rows plus saved/prior Mistral Nemo overlap; GPT-5.5 has 2,182/2,182 valid choices. | Partial distributional comparison only; CCD-Bench is not an accuracy benchmark. |" in readme
    assert "![Paper-model calibration bridge](figures/release/option1_paper_model_calibration_bridge.svg)" in readme
    assert "## OpenRouter Selected-Grid Follow-Up" in readme
    assert "119/119` planned model-task rows have terminal states" in readme
    assert "101` are scored successes" in readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/within_family_scaling.svg" in readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/time_scaling.svg" in readme
    assert "results/openrouter-selected-grid-moral-psych-full/figures/benchmark_score_matrix.svg" in readme
    assert "The figures below replace the earlier dense task-score plot as the primary reading path." in readme
    assert "## Navigate This Repo" in readme
    assert "## Results First" in readme
    assert "### DeepSeek S/M/L Log-Derived Readout" in readme
    assert "results/release/2026-04-19-option1/README.md" in readme
    assert "results/release/2026-04-19-option1/jenny-group-report.md" in readme
    assert "figures/release/option1_benchmark_accuracy_bars.svg" in readme
    assert "figures/release/option1_unimoral_task_heatmap.svg" in readme
    assert "figures/release/option1_unimoral_generation_quality.svg" in readme
    assert "figures/release/option1_unimoral_family_scaling.svg" in readme
    assert "figures/release/option1_family_scaling_profile.svg" in readme
    assert "figures/release/option1_ccd_choice_distribution.svg" in readme
    assert "figures/release/option1_ccd_dominant_option_share.svg" in readme
    assert "figures/release/option1_denevil_behavior_outcomes.svg" in readme
    assert "`CCD-Bench` is reported as cultural-cluster choice behavior" in readme
    assert "`DeNEVIL` is reported as proxy behavioral evidence" in readme
    assert "`make bootstrap`" in readme or "make audit" in readme

    unimoral_family_scaling_svg = (ROOT / "figures/release/option1_unimoral_family_scaling.svg").read_text(encoding="utf-8")
    assert "UniMoral family-size scaling by RQ" in unimoral_family_scaling_svg
    assert "OpenAI GPT-5 is the black S/M/L line across RQ1-RQ4" in unimoral_family_scaling_svg
    assert "OpenAI GPT-5 is black and appears across RQ1-RQ4" in unimoral_family_scaling_svg
    assert "GPT-5.5 is strongest inside GPT-5 on RQ2, RQ3, and both RQ4 metrics" in unimoral_family_scaling_svg
    assert "Metric: Accuracy" in unimoral_family_scaling_svg
    assert "Metric: BERTScore F1" in unimoral_family_scaling_svg
    assert "Metric: METEOR" in unimoral_family_scaling_svg

    paper_calibration_svg = (ROOT / "figures/release/option1_paper_model_calibration_bridge.svg").read_text(encoding="utf-8")
    assert "Paper-Model Calibration Bridge" in paper_calibration_svg
    assert "CCD rows compare dominant cultural-cluster share, not accuracy" in paper_calibration_svg
    assert "not Kaleido model replication" in paper_calibration_svg
    assert "FULCRA proxy behavior" in paper_calibration_svg

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

    results_readme = (ROOT / "results" / "README.md").read_text(encoding="utf-8")
    assert "## Public Result Layers" in results_readme
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
