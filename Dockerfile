# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage: base — shared Python + uv setup
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY vendor/ ./vendor/

# ---------------------------------------------------------------------------
# Stage: lm-harness
# ---------------------------------------------------------------------------
FROM base AS lm-harness

COPY src/lm-evaluation-harness/pyproject.toml ./src/lm-evaluation-harness/
COPY src/inspect/pyproject.toml ./src/inspect/

RUN uv sync --package cei-lm-harness --frozen --no-dev

COPY src/lm-evaluation-harness/ ./src/lm-evaluation-harness/

ENTRYPOINT ["uv", "run", "--package", "cei-lm-harness", "python", "src/lm-evaluation-harness/run.py"]

# ---------------------------------------------------------------------------
# Stage: inspect
# ---------------------------------------------------------------------------
FROM base AS inspect

COPY src/inspect/pyproject.toml ./src/inspect/
COPY src/lm-evaluation-harness/pyproject.toml ./src/lm-evaluation-harness/

RUN uv sync --package cei-inspect --frozen --no-dev

COPY src/inspect/ ./src/inspect/

ENTRYPOINT ["uv", "run", "--package", "cei-inspect", "python", "src/inspect/run.py"]
