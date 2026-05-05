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

## Claude Code Slash Commands

This repo includes project-level [Claude Code](https://claude.com/claude-code) slash commands that any teammate can use. After cloning the repo, open Claude Code in the project directory and type any of these:

| Command | What it does |
|---------|-------------|
| `/run-trolleybench` | Run Joseph's TrolleyBench pipeline (run, evaluate, export) |
| `/run-ethics` | Run Erik's Hendrycks ETHICS benchmark (Inspect AI or lm-eval) |
| `/run-moral-psych` | Run Jenny's 5 moral-psych benchmarks |
| `/release` | Build release artifacts (CSVs, SVGs, reports) |
| `/create-pr` | Create a PR against the org repo with reviewers |

You can pass arguments after the command, e.g.:

```
/run-trolleybench -m qwen -s S -t 0.0
/run-moral-psych --tasks evals/unimoral.py --model openrouter/qwen/qwen3-8b --limit 10
/run-ethics --model hf/Qwen/Qwen3-0.6B --limit 5
/create-pr Add new benchmark results
```

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
