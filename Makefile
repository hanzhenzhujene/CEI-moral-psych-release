.PHONY: help bootstrap setup ensure-runner test release refresh-authoritative smoke audit clean-release

RELEASE_DIR := results/release/2026-04-19-option1
RELEASE_SOURCE := $(RELEASE_DIR)/source/authoritative-summary.csv
RAW_AUTHORITATIVE := results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.csv
UV ?= uv
VENV_PYTHON ?= .venv/bin/python

ifneq ($(shell command -v $(UV) 2>/dev/null),)
RUN_PYTHON = $(UV) run python
RUN_PYTEST = $(UV) run pytest
RUN_INSPECT = $(UV) run --package cei-inspect python
RUNNER_NOTE = uv
else
RUN_PYTHON = $(VENV_PYTHON)
RUN_PYTEST = $(VENV_PYTHON) -m pytest
RUN_INSPECT = $(VENV_PYTHON)
RUNNER_NOTE = $(VENV_PYTHON)
endif

help:
	@echo "Available targets:"
	@echo "  make bootstrap     Public QA: install deps when uv is available, then run tests and rebuild the release package"
	@echo "  make setup         Install the pinned uv environment (requires uv)"
	@echo "  make test          Run the test suite (runner: $(RUNNER_NOTE))"
	@echo "  make release       Build public release artifacts from the tracked source snapshot (runner: $(RUNNER_NOTE))"
	@echo "  make refresh-authoritative  Refresh the tracked source snapshot from local raw full-run tables"
	@echo "  make smoke         Run a 2-sample UniMoral smoke test (runner: $(RUNNER_NOTE))"
	@echo "  make audit         Run the public QA gate (tests + release rebuild)"
	@echo "  make clean-release Remove generated release tables and figures"

bootstrap:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(MAKE) setup UV=$(UV) VENV_PYTHON=$(VENV_PYTHON); \
	elif [ -x "$(VENV_PYTHON)" ]; then \
		echo "uv not found; reusing $(VENV_PYTHON) for bootstrap."; \
	else \
		echo "Could not resolve either '$(UV)' on PATH or executable '$(VENV_PYTHON)'. Install uv, run 'make setup', or pass VENV_PYTHON=/absolute/path/to/python." >&2; \
		exit 1; \
	fi
	$(MAKE) audit UV=$(UV) VENV_PYTHON=$(VENV_PYTHON)

setup:
	@if ! command -v $(UV) >/dev/null 2>&1; then \
		echo "make setup requires '$(UV)' on PATH. Install uv or run 'make UV=/absolute/path/to/uv setup'."; \
		exit 1; \
	fi
	$(UV) sync --frozen

ensure-runner:
	@if command -v $(UV) >/dev/null 2>&1; then \
		:; \
	elif [ -x "$(VENV_PYTHON)" ]; then \
		:; \
	else \
		echo "Could not resolve either '$(UV)' on PATH or executable '$(VENV_PYTHON)'. Install uv, run 'make setup', or pass VENV_PYTHON=/absolute/path/to/python." >&2; \
		exit 1; \
	fi

test: ensure-runner
	$(RUN_PYTEST) tests -q

release: ensure-runner
	$(RUN_PYTHON) scripts/build_release_artifacts.py --input $(RELEASE_SOURCE)

audit: test release

refresh-authoritative: ensure-runner
	$(RUN_PYTHON) scripts/build_authoritative_option1_status.py
	mkdir -p $(dir $(RELEASE_SOURCE))
	cp $(RAW_AUTHORITATIVE) $(RELEASE_SOURCE)

smoke: ensure-runner
	$(RUN_INSPECT) src/inspect/run.py \
		--tasks src/inspect/evals/moral_psych.py::unimoral_action_prediction \
		--model openrouter/qwen/qwen3-8b \
		--temperature 0 \
		--limit 2 \
		--no_sandbox \
		--log_dir results/inspect/logs/smoke

clean-release:
	rm -f $(RELEASE_DIR)/*.csv \
		$(RELEASE_DIR)/*.json \
		$(RELEASE_DIR)/*.md \
		$(RELEASE_DIR)/source/README.md
	rm -rf figures/release
