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

- UniMoral original-model overlap: `Llama 3.1 8B` saved May 13 artifact, full 8,784-row UniMoral action-prediction run, accuracy 0.6388.
- UniMoral capability floor: `Llama 3.2 1B` saved May 13 artifact, accuracy 0.4056 and lower answer rate.
- CCD exact same-model overlap: `mistralai/mistral-nemo` saved May 13 CCD artifact, 2,178/2,182 valid choices, dominant Nordic Europe share 25.3%.
- CCD context rows only: saved OpenAI text references and Qwen/Qwen2.5 rows differ from the exact paper model or route version, so they should not be used in the one-to-one calibration bridge.
- Current-release anchors: Qwen-S, DeepSeek-M, Gemma-S, and the OpenAI text-only reference rows should be used as current/SOTA context, not as original-paper replication or same-model calibration.

These are saved/prior artifacts, not fresh reruns.

## Fresh Rerun Status

- `mistralai/mistral-nemo` CCD-Bench route probe: fresh 1-sample route check succeeded on May 21, 2026 under `results/inspect/logs/2026-05-21-calibration-route-probes/mistral_nemo_ccd_probe/`.
- `meta-llama/llama-3.1-8b-instruct` UniMoral route probe: the earlier run was blocked before model call because `UNIMORAL_DATA_DIR` was not set; after setting it to the local `data/unimoral` export, a fresh 1-sample route probe succeeded under `results/inspect/logs/2026-05-21-calibration-route-probes/llama31_unimoral_probe_retry/`.
- Full fresh older-model replication runs were not launched because the saved May 13 artifacts already contain full UniMoral/CCD sample sets, and rerunning the full subset would duplicate cost without changing the release evidence unless explicitly requested.

## Replication Categories

- Paper-faithful replication: available only for benchmark/task paths where the repo has the same setup and data. Current best candidates are UniMoral RQ1 action prediction and CCD-Bench choice selection.
- Proxy-only evidence: DeNEVIL FULCRA proxy evidence is useful for behavior/provenance, but it is not paper-faithful MoralPrompt replication.
- Saved artifact comparison: May 13 exploratory results and OpenAI text-reference sweeps are valid saved comparisons when labeled as prior artifacts.
- Blocked fresh reruns: Kaleido model replication needs approved HF access/model route and separate model execution; DeNEVIL paper-faithful replication needs MoralPrompt data. UniMoral is no longer blocked by local data path after setting `UNIMORAL_DATA_DIR`.

## Interpretation

Use calibration to check the harness and result scale, not to make broad benchmark-theory claims. The useful Phase 1 comparison is older/smaller paper-era routes versus current release/SOTA routes, with model size and model era kept explicit.

Important boundaries:

- CCD-Bench calibration is a distributional/cultural-choice check, not benchmark-faithful accuracy.
- DeNEVIL proxy evidence should not be described as original-paper replication.
- Saved artifacts should be labeled as saved/prior artifacts whenever they are compared with fresh route probes or current release rows.
