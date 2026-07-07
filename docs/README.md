# Docs Index

## Public Docs

- [`repo-architecture.md`](repo-architecture.md): the shortest explanation of the repo's three layers: frozen release, tracked regeneration source, and local raw run provenance.
- [`evaluation-methodology.md`](evaluation-methodology.md): metric taxonomy, parser/scorer controls, and the comparison rules that determine what can be claimed from the current release.
- [`reproducibility.md`](reproducibility.md): the main public quickstart, including `make bootstrap`, setup notes, release regeneration, and benchmark run instructions.
- [`how-to-read-results.md`](how-to-read-results.md): plain-language guide to the report terms and progress labels.
- [`openai-reference-runs.md`](openai-reference-runs.md): completed OpenAI text-reference rows, including the promoted GPT-5.5 text-only follow-up.
- [`paper-result-comparison.md`](paper-result-comparison.md): reviewer-facing calibration page with a Safe Citation Matrix separating exact paper-model bars, metric-bridged UniMoral calibration, and blocked/proxy-only cases.
- [`calibration-replication.md`](calibration-replication.md): exact UniMoral/CCD calibration evidence, saved-prior artifacts, and current replication limits.
- [`paper-model-replication-map.md`](paper-model-replication-map.md): benchmark-by-benchmark map separating paper-faithful candidates, route probes, saved/prior artifacts, and proxy-only evidence.
- [`data-access.md`](data-access.md): benchmark-by-benchmark dataset and environment-variable requirements.
- [`legacy-baselines.md`](legacy-baselines.md): how the older lm-evaluation-harness ETHICS path fits into the repo.

## Public Release Entry Points

- [`../README.md`](../README.md): high-level project framing and key results
- [`../figures/README.md`](../figures/README.md): one-screen figure talk track, audience-facing figure order, visual caveats, and secondary QA/provenance figure map
- [`../results/release/2026-04-19-option1/README.md`](../results/release/2026-04-19-option1/README.md): release artifact index
- [`../results/release/2026-04-19-option1/source/README.md`](../results/release/2026-04-19-option1/source/README.md): provenance note for the tracked authoritative snapshot
- [`../results/openrouter-selected-grid-moral-psych-full/README.md`](../results/openrouter-selected-grid-moral-psych-full/README.md): separate text-only OpenRouter selected-grid follow-up, with figures, interpretation, and blocked-cell audit

## Visual Reader Path

For the fastest reviewer path, start with the root README's [`Visual Read In 90 Seconds`](../README.md#visual-read-in-90-seconds). It gives the five-figure talk track before the dense result tables. Use [`../figures/README.md`](../figures/README.md) when you need the full presentation order for result visuals. Its `What To Say From The Figures` table expands the same story into a one-screen talk track; for category rules, use the root README's [`Visual Contract`](../README.md#visual-contract). Together they separate:

- audience-facing figures for the main story
- secondary QA / provenance figures
- replication and calibration figures
- separate OpenRouter selected-grid follow-up figures

The most important boundaries are visible there too: UniMoral RQ4 is generation quality rather than accuracy, CCD-Bench is cultural-choice behavior rather than correctness, and DeNEVIL is proxy behavior rather than paper-faithful MoralPrompt scoring.

For exact wording on what can be cited against original-paper results, use [`paper-result-comparison.md#safe-citation-matrix`](paper-result-comparison.md#safe-citation-matrix).

## Archived Planning And Status

- [`status/`](status/): historical progress/status snapshots moved out of the repository root.
- [`plans/`](plans/): planning notes for older benchmark integration work.
- [`setup/`](setup/): provider setup notes, including historical OpenRouter guidance.

## Historical Run Notes

These files are intentionally kept because they document the recovery path from smoke tests to the current authoritative release:

- [`history/mentor-smoke-brief-2026-04-17.md`](history/mentor-smoke-brief-2026-04-17.md)
- [`history/mentor-full-run-brief-2026-04-17.md`](history/mentor-full-run-brief-2026-04-17.md)
- [`history/mentor-full-run-brief-2026-04-17-funded.md`](history/mentor-full-run-brief-2026-04-17-funded.md)
- [`history/mentor-denevil-proxy-brief-2026-04-18.md`](history/mentor-denevil-proxy-brief-2026-04-18.md)
- [`history/mentor-option1-brief-2026-04-19.md`](history/mentor-option1-brief-2026-04-19.md)
- [`history/jenny-moral-psych-runbook.md`](history/jenny-moral-psych-runbook.md)

For the polished public result package, prefer the curated release outputs under `results/release/` rather than these process notes.
