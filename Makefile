.PHONY: help setup test release refresh-authoritative smoke audit clean-release

RELEASE_DIR := results/release/2026-04-19-option1
RELEASE_SOURCE := $(RELEASE_DIR)/source/authoritative-summary.csv
RAW_AUTHORITATIVE := results/inspect/full-runs/2026-04-19-option1-authoritative-status/authoritative-summary.csv
UV ?= uv

help:
	@echo "Available targets:"
	@echo "  make setup         Install the pinned uv environment"
	@echo "  make test          Run the test suite"
	@echo "  make release       Build public release artifacts from the tracked source snapshot"
	@echo "  make refresh-authoritative  Refresh the tracked source snapshot from local raw full-run tables"
	@echo "  make smoke         Run a 2-sample UniMoral smoke test"
	@echo "  make audit         Run the public QA gate (tests + release rebuild)"
	@echo "  make clean-release Remove generated release tables and figures"

setup:
	$(UV) sync --frozen

test:
	$(UV) run pytest tests -q

release:
	$(UV) run python scripts/build_release_artifacts.py --input $(RELEASE_SOURCE)

audit: test release

refresh-authoritative:
	$(UV) run python scripts/build_authoritative_option1_status.py
	mkdir -p $(dir $(RELEASE_SOURCE))
	cp $(RAW_AUTHORITATIVE) $(RELEASE_SOURCE)

smoke:
	$(UV) run --package cei-inspect python src/inspect/run.py \
		--tasks src/inspect/evals/moral_psych.py::unimoral_action_prediction \
		--model openrouter/qwen/qwen3-8b \
		--temperature 0 \
		--limit 2 \
		--no_sandbox \
		--log_dir results/inspect/logs/smoke

clean-release:
	rm -f $(RELEASE_DIR)/README.md \
		$(RELEASE_DIR)/benchmark-summary.csv \
		$(RELEASE_DIR)/coverage-matrix.csv \
		$(RELEASE_DIR)/faithful-metrics.csv \
		$(RELEASE_DIR)/model-summary.csv \
		$(RELEASE_DIR)/release-manifest.json \
		$(RELEASE_DIR)/topline-summary.json \
		$(RELEASE_DIR)/topline-summary.md
	rm -rf figures/release
