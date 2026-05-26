# CEI — Moral Psychology Benchmark Evaluation

Systematic evaluation of LLM moral reasoning across 13 Tier-1 papers from the [Center for Ethical Intelligence](https://www.ethical-intel.org/).

**[Tier-1 Benchmark Experiment Guide](https://moiren.github.io/cei-moralpsy-bench/index.html)** — Full reference for all 13 benchmarks: datasets, prompt templates, evaluation methods, and theory coverage matrix.

## Architecture

```
                                    CEI Benchmark Pipeline
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 ��                                                                                 │
 │  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
 │  │   Scenario    │     │   Runner     │     │  Evaluator   │     │  Exporter  │ │
 │  │   Prompts     │────▶│              │────▶│              │────▶│            │ │
 │  │              │     │              │     │              │     │            │ │
 │  │ trolleybench │     │ run_trolley  │     │ eval_trolley │     │ export_    │ │
 │  │   .jsonl     │     │  bench.py    │     │  bench.py    │     │ results.py │ │
 │  └──────────────┘     └──────┬───────┘     └──────────────┘     └────────────┘ │
 │                              │                                                  │
 │  ┌──────────────┐     ┌──────┴───────┐                                         │
 │  │   Config     │     │   Client     │                                         │
 │  │              │────▶│              │                                         │
 │  │ config.py    │     │ client.py    │                                         │
 │  │ • 15 models  │     │ • query()    │                                         │
 │  │ • 4 temps    │     │ • multiturn()│                                         │
 │  │ • 13 papers  │     │ • w/ system()│                                         │
 │  └──────────────┘     └──────┬───────┘                                         │
 │                              │                                                  │
 └──────────────────────────────┼──────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    OpenRouter API      │
                    │  openrouter.ai/api/v1  │
                    ├───────────────────────┤
                    │ Qwen3    (235B/32B/8B)│
                    │ DeepSeek (R1/V3/70B)  │
                    │ Llama    (70B/8B/3B)  │
                    │ Gemma    (27B/12B/4B) │
                    │ MiniMax  (M2.5/M1/01) │
                    └───────────────────────┘
```

### Data Flow (TrolleyBench)

```
prompts/trolleybench.jsonl          18 scenarios × 3 turns each
         │
         ▼
run_trolleybench.py                 For each model × temperature:
         │                            T1: Present dilemma ──▶ R1
         │                            T2: Clarifying followup (with R1 context) ──▶ R2
         │                            T3: Contradictory challenge (with R1+R2) ──▶ R3
         ▼
results/<timestamp>/
  ├── qwen-L_T0.0.json             Raw multi-turn conversations
  ├── qwen-L_T0.7.json
  ├── ...
  └── meta.json
         │
         ▼
eval_trolleybench.py                Extract actions + frameworks via regex
         │                          ┌─────────────────────────────────────┐
         │                          │  Response ──▶ extract_action()      │
         │                          │    "I would pull the lever"  → act  │
         │                          │    "I refuse to act"     → no_act   │
         │                          │                                     │
         │                          │  Response ──▶ extract_framework()   │
         │                          │    "greatest good"  → consequentialist │
         │                          │    "moral duty"     → deontological    │
         │                          └─────────────────────────────────────┘
         │
         ├──▶ ECI (Ethical Consistency Index)
         │      Compare dominant action across variant pairs
         │      1.0 = always same choice, 0.0 = always different
         │
         ├──▶ Entropy Inconsistency
         │      Binary entropy of act/no_act across 3 turns
         │      0.0 = never wavers, 1.0 = maximally unpredictable
         │
         ├──▶ Follow-up Reversal Rate
         │      % of T3 responses that flip T1 position
         │
         ▼
  ├── eval_summary.json             Per-model metrics
  └── eval_report.md                Human-readable report
         │
         ▼
export_results.py
  ├── export/summary.csv            One row per model
  ├── export/all_responses.csv      One row per scenario × model
  └── export/conversations.md       Full conversations, readable
```

### Trolley Variant Coverage

```
                        ┌─────────────────────┐
                        │   Classic Trolley    │
                        │      Problem         │
                        └──────────┬──────────┘
           ┌───────────┬───────────┼───────────┬────────────┐
           ▼           ▼           ▼           ▼            ▼
      ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
      │ Switch  │ │Footbridge│ │  Loop   │ │Trapdoor │ │Man-in-  │
      │ (lever) │ │ (push)  │ │(divert) │ │(button) │ │ front   │
      └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
       action vs    physical    intended     indirect     direct
       inaction     contact     vs foreseen  mechanism    force
           ┌───────────┬───────────┬────────────┬────────────┐
           ▼           ▼           ▼            ▼            ▼
      ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐
      │Saboteur │ │ Organ   │ │  Self-  │ │Autonomous│ │Bystander│
      │ (guilt) │ │Transplant│ │Sacrifice│ │ Vehicle  │ │ Dilemma │
      └─────────┘ └─────────┘ └─────────┘ └──────────┘ └─────────┘
       desert/      institu-    self vs      programmed   certainty
       guilt        tional      other        ethics       vs uncert.
                    trust
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env with your OpenRouter API key (and optionally HF_TOKEN, OPENAI/ANTHROPIC keys)

# --- TrolleyBench (multi-turn, OpenRouter API) ---

# Run TrolleyBench (smoke test)
python run_trolleybench.py -m qwen -s S -t 0.0

# Run full evaluation
python run_trolleybench.py --all-models -t 0.0 0.7

# Evaluate results
python eval_trolleybench.py -r results/trolleybench/<timestamp>

# Export to CSV/markdown
python export_results.py -r results/trolleybench/<timestamp>

# --- Hendrycks ETHICS (via Inspect AI) ---

python src/inspect/run.py --model hf/Qwen/Qwen3-0.6B --limit 5 --no_sandbox

# --- Hendrycks ETHICS (via lm-evaluation-harness) ---

python src/lm-evaluation-harness/run.py --tasks cei_ethics --limit 5

# --- Moral-Psych Benchmarks (Inspect AI, Jenny) ---

python src/inspect/run.py --tasks evals/moral_psych.py --model openrouter/qwen/qwen3-8b --no_sandbox --limit 5

# --- Docker ---

docker compose run lm-harness
docker compose run inspect
```

## Hendrycks ETHICS Benchmark

The repo also includes the [Hendrycks ETHICS](https://arxiv.org/abs/2008.02275) benchmark (2020) with two evaluation frameworks, contributed by **Erik Nordby**.

### 5 ETHICS Subsets

| Subset | Task | Label Semantics |
|--------|------|----------------|
| Commonsense | Classify actions as ethical/unethical | 0=unethical, 1=ethical |
| Deontology | Judge scenario+excuse as excusable/inexcusable | 0=inexcusable, 1=excusable |
| Justice | Classify scenarios as just/unjust | 0=unjust, 1=just |
| Utilitarianism | Compare paired scenarios for utility | baseline always preferred |
| Virtue | Determine if trait is exhibited in scenario | 0=not exhibited, 1=exhibited |

### Inspect AI Framework

Uses [Inspect AI](https://inspect.ai/) (UK AISI) with `@task`-decorated functions in `src/inspect/evals/ethics.py`. Each task creates a `Task` with `MemoryDataset`, zero-shot generation (`max_tokens=16, temperature=0.01`), and pattern scoring (`r"\b([01])\b"`).

```bash
python src/inspect/run.py --model hf/Qwen/Qwen3-0.6B --limit 5 --no_sandbox
```

### lm-evaluation-harness Framework

Uses [lm-eval](https://github.com/EleutherAI/lm-evaluation-harness) with custom YAML task configs in `src/lm-evaluation-harness/tasks/`. Supports the `cei_ethics` task group covering all 5 subsets.

```bash
python src/lm-evaluation-harness/run.py --tasks cei_ethics --limit 5
```

## Moral-Psych Benchmark Suite (Jenny Zhu)

The repo also includes **5 moral-psychology benchmarks** from Jenny Zhu's assigned papers, built on the same Inspect AI framework:

| Benchmark | Paper | Modality | Tasks |
|-----------|-------|----------|-------|
| UniMoral | Kumar et al. (ACL 2025 Findings) | Text, multilingual | action_prediction, moral_typology, factor_attribution, consequence_generation |
| SMID | Crone et al. (PLOS ONE 2018) | Vision | moral_rating, foundation_classification |
| Value Kaleidoscope | Sorensen et al. (AAAI 2024) | Text | relevance, valence |
| CCD-Bench | Rahman et al. (arXiv 2025) | Text | selection (Latin square cultural clusters) |
| Denevil | Duan et al. (ICLR 2024) | Text | generation, fulcra_proxy_generation |

### Running Moral-Psych Benchmarks

```bash
# Run all moral-psych tasks
python src/inspect/run.py --tasks evals/moral_psych.py --model openrouter/qwen/qwen3-8b --no_sandbox

# Run a specific benchmark
python src/inspect/run.py --tasks evals/unimoral.py --model openrouter/qwen/qwen3-8b --limit 10 --no_sandbox

# With temperature and concurrency controls
python src/inspect/run.py --tasks evals/smid.py --model openrouter/qwen/qwen3-vl-8b-instruct --temperature 0 --max_tasks 4 --no_sandbox
```

### Data Directory Setup

Each benchmark requires data paths set in `.env`:

```bash
UNIMORAL_DATA_DIR=/path/to/unimoral/data
SMID_DATA_DIR=/path/to/smid/images
VALUEPRISM_RELEVANCE_FILE=/path/to/valueprism/relevance.csv
VALUEPRISM_VALENCE_FILE=/path/to/valueprism/valence.csv
CCD_BENCH_DATA_FILE=/path/to/ccd-bench.json
DENEVIL_DATA_FILE=/path/to/denevil/data
```

### Release Artifact System

```bash
# Build release artifacts (CSVs, SVGs, reports)
make release

# Run all tests
make test

# Smoke test
make smoke

# Audit release
make audit
```

Release outputs go to `results/release/` and `figures/release/`.

### Final Moral-Psych Deliverable

The final public moral-psych release is packaged as a reviewer-facing deliverable, not just raw benchmark logs.

- TL;DR + main visuals: [results/release/2026-04-19-option1/README.md](results/release/2026-04-19-option1/README.md)
- Full PI-facing report: [results/release/2026-04-19-option1/jenny-group-report.md](results/release/2026-04-19-option1/jenny-group-report.md)
- Short summary: [results/release/2026-04-19-option1/topline-summary.md](results/release/2026-04-19-option1/topline-summary.md)

The release explicitly separates:
- benchmark-faithful comparable accuracy for `UniMoral`, `SMID`, and `Value Kaleidoscope`
- `CCD-Bench` as cultural-cluster choice behavior rather than scalar accuracy
- `DeNEVIL` as proxy behavioral evidence rather than benchmark-faithful ethical-quality scoring

Key result visuals:
- [Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)
- [Family scaling profile](figures/release/option1_family_scaling_profile.svg)
- [CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)
- [CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)
- [DeNEVIL behavioral outcomes](figures/release/option1_denevil_behavior_outcomes.svg)

At-a-glance moral-psych result snapshot:

- `Qwen-L` is the strongest fully comparable released line across `UniMoral`, `SMID`, and `Value Kaleidoscope`.
- `Llama-M` is the strongest text-only line, but it does not have a public `SMID` route.
- `SMID` is still the hardest benchmark; `CCD-Bench` and `DeNEVIL` should be read as behavior / proxy surfaces rather than a single scalar accuracy story.

![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)

![Family scaling profile](figures/release/option1_family_scaling_profile.svg)

![CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)

![DeNEVIL behavioral outcomes](figures/release/option1_denevil_behavior_outcomes.svg)

## Project Structure

```
cei/
├── config.py                        # Models, benchmarks, temperatures
├── client.py                        # OpenRouter API client
├── run_benchmark.py                 # Generic single-turn runner
├── run_trolleybench.py              # Multi-turn TrolleyBench runner
├── eval_trolleybench.py             # ECI + entropy evaluation
├── export_results.py                # CSV/markdown exporter
├── prompts/                         # Benchmark prompt files (JSONL)
│   └── trolleybench.jsonl           # 18 trolley scenarios × 3 turns
├── src/
│   ├── inspect/                     # Inspect AI framework
│   │   ├── run.py                   # Enhanced CLI runner (multi-model, TASK_EXPORTS)
│   │   ├── pyproject.toml           # Package dependencies
│   │   └── evals/
│   │       ├── ethics.py            # 5 Hendrycks ETHICS tasks (Erik)
│   │       ├── _benchmark_utils.py  # Shared utilities (Jenny)
│   │       ├── moral_psych.py       # Task registry for all benchmarks (Jenny)
│   │       ├── unimoral.py          # UniMoral benchmark (Jenny)
│   │       ├── smid.py              # SMID vision benchmark (Jenny)
│   │       ├── value_kaleidoscope.py # Value Kaleidoscope (Jenny)
│   │       ├── ccd_bench.py         # CCD-Bench cultural benchmark (Jenny)
│   │       ├── denevil.py           # Denevil generation benchmark (Jenny)
│   │       └── data/unimoral/       # Prompt templates (PROMPTS*.txt)
│   └── lm-evaluation-harness/       # lm-eval framework (Erik)
│       ├── run.py                   # CLI wrapper
│       ├── pyproject.toml           # Package dependencies
│       └── tasks/
│           ├── _cei_ethics.yaml     # Task group config
│           ├── cei_ethics_*.yaml    # 5 subset task configs
│           └── utils.py             # Utilitarianism/virtue helpers
├── scripts/                         # Run launchers, recovery helpers, release builders (Jenny)
│   ├── build_release_artifacts.py   # Generates release package (CSVs, SVGs, reports)
│   ├── build_authoritative_option1_status.py
│   ├── summarize_inspect_eval_progress.py
│   ├── check_denevil_dataset.py
│   └── *.sh                         # Batch run scripts
├── docs/                            # Documentation (Jenny)
│   ├── data-access.md, reproducibility.md, how-to-read-results.md
│   └── history/                     # Historical runbooks and briefs
├── figures/release/                 # SVG charts (Jenny)
├── vendor/                          # Vendored Python wheels
├── tests/                           # Unit tests
├── results/                         # Timestamped run outputs
│   ├── trolleybench/                # TrolleyBench results
│   ├── release/                     # Frozen release packages (Jenny)
│   ├── inspect/logs/                # Inspect AI eval logs
│   └── lm-harness/                  # lm-eval-harness results
├── Makefile                         # setup, test, release, smoke, audit (Jenny)
├── .github/workflows/ci.yml        # GitHub Actions CI (Jenny)
├── CONTRIBUTING.md                  # Contribution guidelines (Jenny)
├── Dockerfile                       # Multi-stage Docker build
├── docker-compose.yml               # Docker services
├── pyproject.toml                   # uv workspace root
├── requirements.txt                 # pip dependencies (TrolleyBench)
├── meeting-notes/                   # Team meeting notes
├── moral-psychology-benchmarks.md   # 13 Tier-1 paper summaries
└── openrouter-setup.md              # OpenRouter setup guide
```

## Models

5 open-source families × 3 sizes (L, M, S) via [OpenRouter](https://openrouter.ai):

| Family | L (Large) | M (Medium) | S (Small) |
|--------|-----------|------------|-----------|
| Qwen3 | 235B-A22B | 32B | 8B |
| DeepSeek | R1 | Chat V3.1 | R1-Distill-70B |
| Llama | 3.3-70B | 3.1-8B | 3.2-3B |
| Gemma 3 | 27B | 12B | 4B |
| MiniMax | M2.5 | M1 | 01 |

## Running the Benchmarks

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY (and optionally HF_TOKEN, OPENAI/ANTHROPIC keys)
```

### Joseph's TrolleyBench

Multi-turn ethical consistency evaluation via OpenRouter.

```bash
# Smoke test (single model, single temperature)
python run_trolleybench.py -m qwen -s S -t 0.0

# Full run (all models, multiple temperatures)
python run_trolleybench.py --all-models -t 0.0 0.7

# Evaluate results
python eval_trolleybench.py -r results/trolleybench/<timestamp>

# Export to CSV/markdown
python export_results.py -r results/trolleybench/<timestamp>
```

### Erik's Hendrycks ETHICS

5 subsets: commonsense, deontology, justice, utilitarianism, virtue.

```bash
# Via Inspect AI
python src/inspect/run.py --model hf/Qwen/Qwen3-0.6B --limit 5 --no_sandbox

# Via lm-evaluation-harness
python src/lm-evaluation-harness/run.py --tasks cei_ethics --limit 5

# Via Docker
docker compose run inspect
docker compose run lm-harness
```

### Jenny's Moral-Psych Benchmarks

5 benchmarks: UniMoral, SMID, Value Kaleidoscope, CCD-Bench, Denevil.

```bash
# Run all 5 benchmarks
python src/inspect/run.py --tasks evals/moral_psych.py --model openrouter/qwen/qwen3-8b --no_sandbox

# Run a single benchmark
python src/inspect/run.py --tasks evals/unimoral.py --model openrouter/qwen/qwen3-8b --limit 10 --no_sandbox
python src/inspect/run.py --tasks evals/smid.py --model openrouter/qwen/qwen3-vl-8b-instruct --temperature 0 --max_tasks 4 --no_sandbox
python src/inspect/run.py --tasks evals/value_kaleidoscope.py --model openrouter/qwen/qwen3-8b --no_sandbox
python src/inspect/run.py --tasks evals/ccd_bench.py --model openrouter/qwen/qwen3-8b --no_sandbox
python src/inspect/run.py --tasks evals/denevil.py --model openrouter/qwen/qwen3-8b --no_sandbox
```

Requires data paths in `.env`: `UNIMORAL_DATA_DIR`, `SMID_DATA_DIR`, `VALUEPRISM_RELEVANCE_FILE`, `VALUEPRISM_VALENCE_FILE`, `CCD_BENCH_DATA_FILE`, `DENEVIL_DATA_FILE`.

### Makefile Shortcuts

```bash
make setup     # install dependencies
make test      # run all tests
make release   # rebuild release artifacts (CSVs, SVGs, reports)
make smoke     # quick smoke test
make audit     # audit release integrity
```

## Adding a Benchmark

1. Prepare prompts as JSONL in `prompts/<benchmark_id>.jsonl`
2. Write a runner (single-turn: use `run_benchmark.py`, multi-turn: see `run_trolleybench.py`)
3. Write an evaluator (see `eval_trolleybench.py` for reference)
4. Results saved to `results/<benchmark_id>/<timestamp>/`

<!-- UNIMORAL_FULL_BENCHMARK_START -->
## UniMoral Full Benchmark Coverage

The release now implements all four UniMoral task definitions and exports scored artifacts where model runs completed, but the current model-line matrix is not yet fully complete. Incomplete or parse-limited cells are listed in `unimoral-failure-checklist.csv`; action prediction remains the legacy comparable scalar and is retained as RQ1.

Metric sanity check: UniMoral has four RQs. Because the frozen RQ1 source exposes only aggregate action accuracy, the main RQ1-RQ3 comparison uses one shared exact-match accuracy metric. In the current strict-complete cells, exact-match accuracy spans RQ2 0.554-0.599 and RQ3 0.561-0.631. RQ4 is a generation task, so it is separated and read with semantic similarity instead of accuracy: BERTScore F1 spans 0.629-0.730, with METEOR 0.077-0.157 as a lexical side metric.

| RQ | Task | Status | Strict complete | Reported cells | Primary metric | Mean | Range | Top line | Diagnostic read |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| RQ1 | Action prediction | complete | 16/16 | 16/16 | accuracy | 0.655 | 0.121 | DeepSeek-M (0.684) | diagnostic |
| RQ2 | Moral typology | incomplete | 15/16 | 16/16 | accuracy | 0.581 | 0.045 | Gemma-S (0.599) | saturated |
| RQ3 | Factor attribution | incomplete | 14/16 | 15/16 | accuracy | 0.592 | 0.070 | Llama-M (0.631) | moderately diagnostic |
| RQ4 | Consequence generation | incomplete | 14/16 | 15/16 | bert_score_f1 | 0.691 | 0.101 | Llama-M (0.730) | diagnostic |

Sample-level predictions for RQ2/RQ3/RQ4 are generated locally as ignored large artifacts; the tracked public package keeps the aggregate summaries in `unimoral-full-benchmark.csv`, `unimoral-coverage.csv`, and `unimoral-completion-audit.md`. Full Inspect `.eval` logs remain under the ignored `results/inspect/logs/2026-05-16-unimoral-full/` run directory.
The provider-free MiniMax handoff is tracked in [`unimoral-minimax-resume-plan.md`](results/release/2026-04-19-option1/unimoral-minimax-resume-plan.md).
The prompt-to-artifact completion audit, including the verifier-checked CSV-level strict blocker inventory, is tracked in [`unimoral-completion-audit.md`](results/release/2026-04-19-option1/unimoral-completion-audit.md).

| Task | What it measures | Scoring note |
| --- | --- | --- |
| RQ1 action prediction | Selects the crowd-endorsed action from a two-action dilemma. | Main figure uses exact-match accuracy because the frozen release source exposes only aggregate action accuracy. |
| RQ2 moral typology | Classifies the selected action as deontological, utilitarian, rights-based, or virtuous using `Action_criteria`. | Main figure uses exact-match accuracy for horizontal comparison with RQ1/RQ3. |
| RQ3 factor attribution | Classifies the main contributor to the annotator decision using `Contributing_factors`. | Main figure uses exact-match accuracy for horizontal comparison with RQ1/RQ2. |
| RQ4 consequence generation | Generates likely consequences for the selected action using `Consequence` references. | BERTScore F1 is the semantic-similarity metric; METEOR, BLEU, and ROUGE-L are lexical side metrics. RQ4 is kept separate from classification accuracy charts. |

![UniMoral classification accuracy heatmap](figures/release/option1_unimoral_task_heatmap.svg)

![UniMoral RQ4 generation quality](figures/release/option1_unimoral_generation_quality.svg)

![UniMoral family-size scaling by RQ](figures/release/option1_unimoral_family_scaling.svg)
<!-- UNIMORAL_FULL_BENCHMARK_END -->
## Claude Code Slash Commands

This repo includes project-level [Claude Code](https://claude.com/claude-code) slash commands that any teammate can use. After cloning the repo, open Claude Code in the project directory and type any of these:

| Command | What it does |
|---------|-------------|
| `/run-trolleybench` | Run Joseph's TrolleyBench pipeline (run, evaluate, export) |
| `/run-ethics` | Run Erik's Hendrycks ETHICS benchmark (Inspect AI or lm-eval) |
| `/run-moral-psych` | Run Jenny's 5 moral-psych benchmarks |
| `/release` | Build release artifacts (CSVs, SVGs, reports) |
| `/create-pr` | Create a PR against the org repo with reviewers |
| `/validate-results` | Validate results against three-tier acceptance criteria and saturation policy |

You can pass arguments after the command, e.g.:

```
/run-trolleybench -m qwen -s S -t 0.0
/run-moral-psych --tasks evals/unimoral.py --model openrouter/qwen/qwen3-8b --limit 10
/run-ethics --model hf/Qwen/Qwen3-0.6B --limit 5
/create-pr Add new benchmark results
/validate-results
/validate-results unimoral smid
```

The `/validate-results` command checks every model × task cell against a **three-tier status system**:

| Tier | Label | Meaning |
|------|-------|---------|
| T1 | Harness complete | A number exists — no guarantee it's meaningful |
| T2 | Result valid | No format failure, missing modality, or proxy substitution |
| T3 | Interpretable | Can be cited and compared across models without caveats |

Because proxy substitution fails T2, the current FULCRA-backed `DeNEVIL` proxy rows are **not T3**. They should be cited only as proxy behavioral evidence until the paper-faithful MoralPrompt path exists.

It also checks **saturation** — whether a benchmark still discriminates between models (e.g., UniMoral action prediction was retired at 0.048 spread). Reports are saved to `results/validation/`.

### Setup

1. Install [Claude Code](https://claude.com/claude-code) if you haven't already
2. Install GitHub CLI (needed for `/create-pr`):
   ```bash
   brew install gh
   gh auth login
   ```
3. `cd` into the repo and run `claude` to start a session — the slash commands are available automatically

## Contributing

All changes go through pull requests — no direct pushes to `main`.

1. Create a branch: `git checkout -b my-feature`
2. Make your changes and commit
3. Push: `git push -u origin my-feature`
4. Open a PR and add a teammate as reviewer
5. Or simply use `/create-pr` in Claude Code to do steps 3-4 for you

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## Team

| Person | Papers |
|--------|--------|
| Joseph | #1-5 (MoReBench, TrolleyBench, Moral Circuits, M3oralBench, MoralLens) |
| Jenny | #6-10 (UniMoral, SMID, Denevil, Value Kaleidoscope, CCD-Bench) |
| Erik | #11-13 (Rules Broken, MoralBench, EMNLP Educator) |

<!-- BEGIN JENNY_MORAL_PSYCH_RELEASE -->
## Jenny Moral-Psych Release TL;DR

> Current project total cost: `$870.30` (MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$325.66`; OpenAI API reference sweep: `$39.98`.)

This appended section is Jenny's current release readout. The shared CEI repo overview, TrolleyBench notes, ETHICS docs, Claude Code commands, and team table above remain the canonical repo-level structure.

Key links:

- [Full release appendix](results/release/2026-04-19-option1/README.md)
- [PI-facing report](results/release/2026-04-19-option1/jenny-group-report.md)
- [Topline summary](results/release/2026-04-19-option1/topline-summary.md)
- [Exact family-size progress table](results/release/2026-04-19-option1/family-size-progress.csv)

Metric boundaries:

- `UniMoral`, `SMID`, and `Value Kaleidoscope` are the comparable-accuracy surfaces.
- `CCD-Bench` is reported as cultural-cluster choice behavior, not universal accuracy.
- `DeNEVIL` is reported as proxy behavioral evidence, not benchmark-faithful scoring.

### TL;DR

Key takeaways:

- **Main landscape:** text moral reasoning is much stronger than image moral judgment. UniMoral and Value sit around 0.653-0.673 mean accuracy, but SMID image accuracy averages only 0.364; even the best image line, `Qwen-L` at 0.483, is below 0.50. In plain terms: models can talk through moral choices and values better than they can see morally important cues in images.
- **Best all-around line:** `MiniMax-S` is the cleanest overall winner because it is not missing the image benchmark: UniMoral 0.661, SMID 0.432, Value 0.740, mean 0.611. The main warning is that the best text-only rows can look stronger, but they do not answer the image problem.
- **Scaling law:** there is no reliable bigger-is-better rule. Scale helps in a few places, especially Qwen on images (0.368 -> 0.483) and Llama on Value from S to M (0.529 -> 0.724). But there are clear reversals: Gemma image dips then rebounds (0.417 -> 0.364 -> 0.412), DeepSeek UniMoral falls from M to L (0.684 -> 0.563), and `MiniMax-L` is an image outlier at 0.199.
- **Family read:** Qwen is the clearest case where size helps vision; Gemma is the cleanest full S/M/L family but still non-monotonic; DeepSeek is useful for text but has no image route and its large line is not automatically better; Llama improves after the small line but M can beat L on text; MiniMax-S is the safest all-around line, while MiniMax-L is the clearest bad image outlier.
- **UniMoral is not one skill:** a model can match the human action but still miss the moral frame, the reason, or the consequence. Task winners rotate across RQ1 `DeepSeek-M` 0.684, RQ2 `Gemma-S` 0.599, RQ3 `Llama-M` 0.631, RQ4 semantic `Llama-M` 0.730, RQ4 lexical `Llama-L` 0.157. So the useful story is which part of moral reasoning each family handles, not one single moral score.
- **Cultural-style bias:** CCD-Bench shows a strong Europe/Nordic pull, not a normal accuracy score. 19 of 20 valid lines choose `Nordic Europe` as their dominant style. `GPT-5-nano Ref` is the most collapsed onto one cluster (27.8%), while `DeepSeek-S` is the least collapsed and the only non-Nordic dominant line (13.8%, `Sub Saharan Africa`).
- **OpenAI references:** the GPT rows mostly confirm the text baseline instead of changing the story. `GPT-4o-mini Ref` is close to the strong text band (UniMoral 0.673, Value 0.701); `GPT-5-mini Ref` beats `GPT-5-nano Ref` (0.739 vs 0.617 on Value), and `GPT-4.1-mini Ref` beats `GPT-4.1-nano Ref` (0.679 vs 0.646 on UniMoral). None of these rows has SMID, so they do not solve the image weakness.
- **Small-model follow-up:** Mistral/Qwen/Llama older routes add one simple takeaway: there is a capability floor. `Mistral Nemo`, `Qwen2.5 7B`, `Llama 3.1 8B`, and `Llama 3 8B` cluster on UniMoral from 0.632 to 0.648, but `Llama 3.2 1B` drops to 0.406. So these models are useful baselines, not a new top tier, and the 1B route is too small for this moral-choice setup.


### Benchmark Result Visuals

If you want the benchmark results before the tables, start here. These visuals pull the main result surfaces for the full benchmark set to the front of the deliverable.

OpenAI text-only reference rows are shown in the comparable-accuracy and CCD figures. They are drawn as gray calibration references, not as a GPT/OpenAI S/M/L size series, and they have no SMID or DeNEVIL row.
OpenAI/GPT scope: the scored reference rows are `openai/gpt-4o-mini`, `openai/gpt-5-nano`, `openai/gpt-4.1-nano`, `openai/gpt-5-mini`, and `openai/gpt-4.1-mini`.

#### 1. UniMoral RQ1-RQ4: family-size scaling and task readout

![UniMoral family-size scaling by RQ](figures/release/option1_unimoral_family_scaling.svg)

_What it tests: UniMoral breaks moral reasoning into four human-facing steps: what action someone chooses, what moral frame the choice reflects, what factor shaped the choice, and what consequences the action may cause._

_Why it matters: moral psychology is about choices plus explanations, not just a right/wrong label. The figure shows that the winner changes across RQs, so the honest takeaway is not `larger model = better moral reasoner`; it is `different model families handle different parts of moral reasoning differently`._

![UniMoral RQ1-RQ3 exact-match accuracy](figures/release/option1_unimoral_task_heatmap.svg)

_How to read it: RQ1, RQ2, and RQ3 all use exact-match accuracy, so the three classification surfaces stay comparable inside the same benchmark block. Higher means the model matched the human-labeled action, moral frame, or decision factor more often._

![UniMoral RQ4 generation quality](figures/release/option1_unimoral_generation_quality.svg)

_How to read RQ4: UniMoral RQ4 shows consequence-generation quality, not accuracy. Higher is better for both metrics: BERTScore F1 measures whether the generated consequence is semantically close to the reference answer, while METEOR measures how much the wording overlaps with the reference. Llama is strongest overall._

#### 2. SMID / Value Kaleidoscope: topline comparable accuracy

![Comparable accuracy bars](figures/release/option1_benchmark_accuracy_bars.svg)

_What it tests: SMID asks whether a vision model can see morally important cues in images. Value Kaleidoscope asks whether a text model can spot which values, rights, or duties matter in a situation and whether they support or oppose the action._

_How to read it: UniMoral is handled in Figure 1; this chart starts at SMID for the like-for-like benchmark-faithful accuracy view. Hatched SMID rows for `DeepSeek-S`, `DeepSeek-M`, `DeepSeek-L`, `Qwen-M`, and `Llama-M` mean no public vision route, not an unparsed text result._

#### 3. SMID / Value Kaleidoscope: family-size scaling

![Family scaling profile](figures/release/option1_family_scaling_profile.svg)

_Why it matters: if scale helped moral perception and value recognition in a simple way, every line would climb from S to M to L. They do not. The useful read is where size helps, where it plateaus, and where it can even hurt._

_Use this next to compare size effects on SMID and Value after the combined UniMoral block, without mixing in CCD-Bench or DeNEVIL proxy evidence; missing SMID points are explicit route gaps._

#### 4. CCD-Bench: cultural-cluster choice behavior

![CCD choice distribution](figures/release/option1_ccd_choice_distribution.svg)

_What it tests: CCD-Bench puts models in value conflicts where ten answer options map to cultural clusters. The figure shows which cultural response styles each model over-selects or avoids relative to a 10% uniform baseline._

_Why it matters: this is not a single right-answer benchmark. It tells a moral-psych reader which culturally grounded response style a model tends to privilege when values conflict._

#### 5. CCD-Bench: dominant-option concentration

![CCD dominant-option share](figures/release/option1_ccd_dominant_option_share.svg)

_How to read it: this is the compact CCD-Bench summary, showing how much each line collapses onto one dominant cultural cluster and how broadly it still spreads across the option set._

#### 6. DeNEVIL: proxy behavioral outcomes

![DeNEVIL proxy behavioral outcomes](figures/release/option1_denevil_behavior_outcomes.svg)

_What it tests: DeNEVIL-style evaluation looks for value vulnerabilities under risky or ethically loaded prompts. In this release the paper-faithful MoralPrompt export is not local, so this figure reports auditable proxy behavior categories from saved traces._

_How to read it: protective refusals and corrective/contextual answers are the safer behaviors; risky continuations are the warning sign. This is behavior evidence from saved traces, not benchmark-faithful accuracy._

Lower-level QA/provenance figures are still generated in `figures/release/`, but the README keeps the visual story focused on these audience-facing result surfaces.

<!-- END JENNY_MORAL_PSYCH_RELEASE -->
