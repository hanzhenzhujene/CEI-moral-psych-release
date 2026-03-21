# CEI — Hendrycks ETHICS Benchmark Runner

Runs the [Hendrycks ETHICS benchmark](https://arxiv.org/abs/2008.02275) across two evaluation frameworks:

- **lm-evaluation-harness** — EleutherAI's standard harness
- **Inspect AI** — UK AISI's evaluation framework

Default model: `Qwen/Qwen3-0.6B` (open-source, runs on CPU for smoke tests).

---

## Project Structure

```
CEI/
├── pyproject.toml                      # uv workspace root
├── uv.lock                             # committed lockfile
├── Dockerfile                          # multi-stage: lm-harness + inspect targets
├── docker-compose.yml
├── .env.example                        # copy to .env and fill in API keys
│
├── src/
│   ├── lm-evaluation-harness/
│   │   ├── pyproject.toml
│   │   ├── run.py                      # CLI wrapping lm_eval.simple_evaluate()
│   │   └── tasks/                      # custom YAML task configs + utils.py
│   │       ├── _cei_ethics.yaml        # task group (all 5 subsets)
│   │       ├── cei_ethics_cm.yaml
│   │       ├── cei_ethics_deontology.yaml
│   │       ├── cei_ethics_justice.yaml
│   │       ├── cei_ethics_utilitarianism.yaml
│   │       ├── cei_ethics_virtue.yaml
│   │       └── utils.py
│   │
│   └── inspect/
│       ├── pyproject.toml
│       ├── run.py                      # CLI calling inspect_ai.eval()
│       └── evals/
│           └── ethics.py              # all 5 ETHICS @task definitions
│
├── tests/                              # pytest test suite
│
└── results/
    ├── lm-harness/                     # JSON results written here
    └── inspect/logs/                   # Inspect eval logs written here
```

---

## Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync all workspace dependencies
uv sync

# Copy and populate API keys (optional, only needed for closed-source models)
cp .env.example .env
```

---

## Running Evaluations

### lm-evaluation-harness

```bash
# Smoke test — 5 samples, CPU, commonsense subset
cd src/lm-evaluation-harness
uv run --package cei-lm-harness python run.py --tasks cei_ethics_cm --limit 5

# Full ETHICS run (all 5 subsets)
uv run --package cei-lm-harness python run.py --tasks cei_ethics

# Single subset
uv run --package cei-lm-harness python run.py --tasks cei_ethics_justice

# Closed-source model (requires OPENAI_API_KEY in .env)
uv run --package cei-lm-harness python run.py \
    --model openai-chat-completions \
    --model_args model=gpt-4o \
    --tasks cei_ethics_cm
```

### Inspect AI

```bash
# Smoke test — 5 samples, CPU
cd src/inspect
uv run --package cei-inspect python run.py --tasks evals/ethics.py --limit 5

# Full ETHICS run (all 5 subsets)
uv run --package cei-inspect python run.py --tasks evals/ethics.py

# Run all evals in the evals/ directory
uv run --package cei-inspect python run.py --tasks "evals/*.py"

# Closed-source model (requires OPENAI_API_KEY in .env)
uv run --package cei-inspect python run.py \
    --model openai/gpt-4o \
    --tasks evals/ethics.py
```

---

## Testing

```bash
uv run pytest tests/ -v
```

---

## Docker

```bash
# Build both images
docker compose build

# Run lm-evaluation-harness (results written to ./results/lm-harness/)
docker compose run --rm lm-harness

# Run Inspect AI (logs written to ./results/inspect/logs/)
docker compose run --rm inspect

# Override args
docker compose run --rm lm-harness --tasks cei_ethics_cm --limit 5
docker compose run --rm inspect --tasks evals/ethics.py --limit 5 --no_sandbox
```

---

## ETHICS Benchmark Subsets

| Subset          | lm-harness task name        | Inspect task function   | Description                              |
|-----------------|-----------------------------|-------------------------|------------------------------------------|
| Commonsense     | `cei_ethics_cm`             | `ethics_commonsense`    | Is an action ethical? (binary)           |
| Deontology      | `cei_ethics_deontology`     | `ethics_deontology`     | Is an excuse acceptable? (binary)        |
| Justice         | `cei_ethics_justice`        | `ethics_justice`        | Is a scenario just? (binary)             |
| Utilitarianism  | `cei_ethics_utilitarianism` | `ethics_utilitarianism` | Which scenario has higher utility?       |
| Virtue          | `cei_ethics_virtue`         | `ethics_virtue`         | Does a person exhibit a trait? (binary)  |

---

## Adding Custom Evaluations

**lm-evaluation-harness**: Add a YAML task config to `src/lm-evaluation-harness/tasks/` following the [lm-eval task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md), then pass `--tasks your_task_name`.

**Inspect AI**: Add a new `.py` file with `@task`-decorated functions to `src/inspect/evals/`, then pass `--tasks evals/your_eval.py`.
