# Calibration And Original-Paper Replication

This note supports the Phase 1 goal from Jimmy's May 19 framing: make the model-evaluation data solid enough to compare model size, model era, and current/SOTA routes before doing Phase 2 benchmark-to-benchmark interpretation.

## Available Paper/Reference Material

- `references/UniMoral/`: reference scripts for RQ1/RQ2/RQ3/RQ4. The code names Llama 3 / Llama 3.1 8B-style routes and DeepSeek/Phi-family result consolidation.
- `references/CCD-Bench/`: datasets plus full reference evaluation artifacts for models including Mistral Nemo, Llama 3.3/4, Qwen2.5 72B, GPT-4o latest, GPT-4.1, and others.
- `references/kaleido/`: Kaleido model docs (`tsor13/kaleido-*`) and the `all-mpnet-base-v2` embedding dependency. Access requires a separate Hugging Face route.
- SMID docs/data adapters: SMID is a normed stimulus set, not an original model-evaluation paper with a model roster to rerun.
- DeNEVIL/ValueCompass references: current repo uses FULCRA proxy data; paper-faithful MoralPrompt data is not available locally.

## Original/Reference Models Identified

- UniMoral reference code names `meta-llama/Meta-Llama-3.1-8B-Instruct`, `meta-llama/Meta-Llama-3-8B`, `Phi-3.5-mini-instruct`, `Llama-3.1-8B-Instruct`, and `DeepSeek-R1-Distill-Llama-8B` in the runnable scripts or consolidation paths.
- CCD-Bench reference artifacts include `mistralai/mistral-nemo`, `qwen/qwen-2.5-72b-instruct`, `openai/chatgpt-4o-latest`, `openai/gpt-4.1`, `meta-llama/llama-3.3-70b-instruct`, `meta-llama/llama-4-maverick-17b-128e-instruct`, `deepseek/deepseek-chat-v3-0324`, `google/gemini-2.0-flash-001`, `anthropic/claude-*`, and other provider routes.
- Kaleido reference docs name `tsor13/kaleido-small`, `tsor13/kaleido-base`, `tsor13/kaleido-large`, `tsor13/kaleido-xl`, and `tsor13/kaleido-xxl`; these are not the same as the current prompt-based ValuePrism LLM rows.
- SMID does not provide an original LLM model roster to rerun.
- DeNEVIL paper-faithful model comparison remains blocked until the MoralPrompt-style data path is available locally.

## Representative Calibration Subset

- UniMoral original-model overlap: fresh exact `Llama 3.1 8B` RQ1-RQ4 rerun, summarized at `results/paper-calibration-exact-20260706-unimoral-llama31/calibration-summary.csv`: RQ1 accuracy 0.6219, RQ2 accuracy 0.6022, RQ3 accuracy 0.5948, RQ4 live METEOR 0.1212, and RQ4 offline BERTScore F1 0.6555.
- UniMoral capability floor: `Llama 3.2 1B` saved May 13 artifact, accuracy 0.4056 and lower answer rate.
- CCD exact same-model bridge: the July 2026 exact CCD pass has 11 plottable same-model distribution rows in `results/release/2026-04-19-option1/paper-model-calibration-bridge.csv` and `results/paper-calibration-exact-20260705/calibration-summary.csv`. All plotted CCD rows use the same Nordic Europe top-cluster-share metric, so the public bar chart compares like with like.
- CCD numeric anchors include Mistral Nemo 2,182/2,182 valid choices and 25.57% Nordic Europe share; Qwen2.5-72B-Instruct 2,182/2,182 and 21.13%; OpenAI GPT-4.1 2,182/2,182 and 22.27%; Claude 4 Sonnet 2,182/2,182 and 30.25%; and Perplexity Sonar 2,182/2,182 and 14.34%. DeepSeek-chat-v3-0324 has a valid-choice caveat at 2,108/2,182, and the current Llama-4-Maverick row has a valid-choice caveat at 2,013/2,182.
- CCD context rows only: unavailable, non-exact, metric-mismatched, and route-probe rows stay in the ledger. They should not be substituted into the same-model bar comparison.
- Current-release anchors: Qwen-S, DeepSeek-M, Gemma-S, and the OpenAI text-only reference rows should be used as current/SOTA context, not as original-paper replication or same-model calibration.

The CCD May 13 artifacts and UniMoral exploratory sweep remain saved/prior artifacts unless explicitly labeled as fresh reruns.

## Fresh Rerun Status

- July 2026 exact CCD-Bench pass: completed same-model CCD distribution reruns for Mistral Nemo, Llama-3.3-70B-Instruct, DeepSeek-chat-v3-0324, Qwen2.5-72B-Instruct, OpenAI GPT-4.1, Command-R 08-2024, Microsoft Phi-4, WizardLM-2-8x22B, Perplexity Sonar, and Claude 4 Sonnet. The Llama-4-Maverick-17B-128E-Instruct row uses the verified current release row. These rows support the same-model CCD bar chart, but CCD remains distributional behavior, not accuracy.
- `mistralai/mistral-nemo` CCD-Bench route probe: the earlier 1-sample route check succeeded on May 21, 2026 under `results/inspect/logs/2026-05-21-calibration-route-probes/mistral_nemo_ccd_probe/`. It is retained as route evidence only, not as the CCD performance result.
- `meta-llama/llama-3.1-8b-instruct` UniMoral full rerun: after confirming the data path and exact OpenRouter route, RQ1-RQ4 completed successfully on July 6, 2026. RQ4 now has both live METEOR and offline BERTScore F1. This is fresh same-model calibration evidence, with metric-scale caveats because the paper reports weighted F1 and 0-100 generation metrics while the repo reports 0-1 accuracy / generation metrics.
- Exact Phi-3.5-mini Instruct and DeepSeek-R1-Distill-Llama-8B routes were not found in the checked OpenRouter catalog, so they were not substituted.

## Replication Categories

- Paper-faithful replication: available only for benchmark/task paths where the repo has the same setup and data. Current best candidates are UniMoral RQ1 action prediction and CCD-Bench choice selection.
- Proxy-only evidence: DeNEVIL FULCRA proxy evidence is useful for behavior/provenance, but it is not paper-faithful MoralPrompt replication.
- Saved artifact comparison: May 13 exploratory results and OpenAI text-reference sweeps are valid saved comparisons when labeled as prior artifacts. The July 6 Llama 3.1 UniMoral rerun and the July 2026 exact CCD pass are separate fresh evidence.
- Blocked fresh reruns: Kaleido model replication needs approved HF access/model route and separate model execution; DeNEVIL paper-faithful replication needs MoralPrompt data. UniMoral is no longer blocked by local data path after setting `UNIMORAL_DATA_DIR`; many CCD paper routes are now exact, but unavailable or non-exact CCD routes remain ledger-only.

## Interpretation

Use calibration to check the harness and result scale, not to make broad benchmark-theory claims. The useful Phase 1 comparison is older/smaller paper-era routes versus current release/SOTA routes, with model size and model era kept explicit.

Important boundaries:

- CCD-Bench calibration is a distributional/cultural-choice check, not benchmark-faithful accuracy.
- DeNEVIL proxy evidence should not be described as original-paper replication.
- Saved artifacts should be labeled as saved/prior artifacts whenever they are compared with fresh route probes or current release rows.
