# Paper-Model Replication Map

This map separates paper-faithful replication candidates from route probes, saved/prior artifacts, and proxy-only evidence. It should be used for planning and audit, not as a new result table.

## Status Vocabulary

- `paper-faithful candidate`: the repo has the benchmark task and local data path needed to rerun the paper-style setup for at least one named reference model.
- `route probe`: a tiny run that checks whether a model route and data path work; it is not a result.
- `saved/prior artifact`: a completed older run that can be compared if labeled as saved/prior, but should not be described as a fresh rerun.
- `proxy only`: the local task is useful evidence, but does not match the original paper data/setup.
- `blocked`: required paper data, model access, or execution path is missing.

## Map

| benchmark | paper/reference model target | local data/access state | current repo task | current evidence | replication status | next safe action |
|---|---|---|---|---|---|---|
| UniMoral | `meta-llama/Meta-Llama-3.1-8B-Instruct`; related reference rows also mention Llama 3 8B, Phi-3.5 mini, and DeepSeek-R1-Distill-Llama-8B | Local data exists at `data/unimoral`; set `UNIMORAL_DATA_DIR` before running | `src/inspect/evals/unimoral.py::unimoral_action_prediction` for RQ1-style action prediction; repo also exposes typology, factor attribution, and consequence-generation tasks | Saved May 13 full Llama 3.1 8B UniMoral artifact; fresh 1-sample Llama 3.1 route probe succeeded at `results/inspect/logs/2026-05-21-calibration-route-probes/llama31_unimoral_probe_retry/` | Paper-faithful candidate for RQ1 only when run on the full paper-style sample set; current fresh probe is route-only | If a fresh result is required, run a bounded full RQ1 rerun with stable `UNIMORAL_DATA_DIR`, provider key, and no duplicated saved sample IDs |
| CCD-Bench | `mistralai/mistral-nemo`; reference artifacts also include Qwen2.5 72B, GPT-4o/latest, GPT-4.1, Llama 3.3/4, DeepSeek V3, Gemini, Claude, and others | Local CCD file exists at `data/ccd-bench/CCD-Bench.json`; set `CCD_BENCH_DATA_FILE` before running | `src/inspect/evals/ccd_bench.py::ccd_bench_selection` | Saved May 13 full Mistral Nemo CCD artifact; fresh 1-sample Mistral Nemo route probe succeeded at `results/inspect/logs/2026-05-21-calibration-route-probes/mistral_nemo_ccd_probe/` | Paper-faithful candidate for choice-distribution behavior, not accuracy; current fresh probe is route-only | Reuse saved full artifact unless a fresh rerun is explicitly needed; never call CCD a correctness benchmark |
| Value Kaleidoscope / ValuePrism | Kaleido model family: `tsor13/kaleido-small`, `base`, `large`, `xl`, `xxl` | Local ValuePrism CSV exports exist; HF token exists locally, but Kaleido model use still requires accepted gated access and separate model execution | Current repo task is prompt-based `value_prism_relevance` / `value_prism_valence`, not Kaleido model inference | Current release/openai rows are prompt-based LLM classification rows | Blocked for paper-model replication; current task is not the original Kaleido model route | Verify HF gated access and run a tiny Kaleido local-model smoke test before any full replication |
| SMID | No original LLM model roster identified in the local reference material | Local norms CSV and image zip exist under `data/smid`; set `SMID_DATA_DIR` before running | `smid_moral_rating` and `smid_foundation_classification` | Current release rows are model-family benchmark runs, not paper-model replication | No paper-model replication target found; benchmark reruns are possible but not paper-model replication | Use SMID only for current benchmark comparison unless a paper-specific model roster is identified |
| DeNEVIL / MoralPrompt | Paper-faithful MoralPrompt setup | Local repo has FULCRA proxy JSONL at `data/denevil/data_hybrid.jsonl`; paper-faithful MoralPrompt export is missing | `denevil_generation` expects a MoralPrompt-style file; `denevil_fulcra_proxy_generation` uses the local proxy data | Current DeNEVIL evidence is FULCRA-backed proxy behavior/provenance only | Blocked for paper-faithful replication; current task is proxy only | Obtain a real MoralPrompt-style export before calling any DeNEVIL run paper-faithful |

## Current Safe Interpretation

The only fresh calibration work completed here is route availability checking: Llama 3.1 8B can now reach UniMoral with the local data path, and Mistral Nemo can reach CCD-Bench. These probes should not be interpreted as model performance. The saved May 13 artifacts remain the reusable comparison evidence until a deliberate full rerun is requested.
