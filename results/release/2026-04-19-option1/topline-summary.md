# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

Key takeaways:

- **What each benchmark means:** `UniMoral` asks whether a model can follow a human moral-choice pipeline; `SMID` asks whether it can see moral cues in images; `Value Kaleidoscope` asks whether it recognizes values, rights, and duties in text; `CCD-Bench` asks which cultural response style it chooses under conflict; `DeNEVIL` asks how it behaves on risky prompts. Only UniMoral, SMID, and Value are comparable accuracy surfaces; CCD-Bench and DeNEVIL are behavior readouts.
- **Best like-for-like line:** `MiniMax-S` is the cleanest overall comparison because it has all three comparable metrics: UniMoral action 0.661, SMID 0.432, and Value 0.740, averaging 0.611. This is the safest single-line topline because it is not missing the vision benchmark.
- **Best text-only line:** `GPT-5-mini Ref` is strongest when the question is only text moral reasoning, reaching UniMoral 0.678 and Value 0.739. It is not an all-around winner because it has no public SMID route.
- **OpenAI/GPT references:** 5 OpenAI text rows are now back in the release. Best OpenAI UniMoral is `GPT-4.1-mini Ref` at 0.679; best OpenAI Value is `GPT-5-mini Ref` at 0.739. Read them as text-side calibration points, not as a GPT S/M/L size curve and not as evidence on SMID.
- **Small-model follow-up:** the May 13 Mistral/Qwen/Llama sweep adds a capability-floor check, not a new leaderboard. `Mistral Nemo` leads that sweep on UniMoral at 0.648, the 7B-12B routes cluster from 0.632 to 0.648, and `Llama 3.2 1B` drops to 0.406 with a lower answer rate. So what: very small routes are risky for human-choice moral reasoning, while several older or mid-sized instruction routes remain usable text/style baselines.
- **The hardest benchmark is SMID:** `SMID` has the lowest mean accuracy (0.364) and widest spread (0.285), while `UniMoral` is tightly clustered (0.121 spread). The bottleneck is seeing moral meaning in images, not basic text moral labeling.
- **UniMoral has different subskills:** do not collapse the four RQs into one moral-reasoning score. Task winners rotate across RQ1 `DeepSeek-M` 0.684, RQ2 `Gemma-S` 0.599, RQ3 `Llama-M` 0.631, RQ4 semantic `Llama-M` 0.730, RQ4 lexical `Llama-L` 0.157. That means models can be good at predicting human choices but weaker at naming the moral frame, explaining the decision factor, or generating consequences.
- **Bigger is not automatically more moral:** `Gemma` is non-monotonic on SMID (0.417 -> 0.364 -> 0.412), and `Llama-M` still beats `Llama-L` on Value (0.724 vs 0.692). Size helps in some places, but the direction depends on the benchmark.
- **CCD-Bench shows cultural choice style, not accuracy.** Every released line with valid CCD choices currently peaks on `option_6 (Nordic Europe)`, but concentration still varies meaningfully, from `DeepSeek-S` at 13.8% to `GPT-5-nano Ref` at 27.8%. The key question is how narrowly each line collapses onto one cultural cluster, not who has the highest "accuracy."
- **DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring.** Among completed lines with usable visible traces, protective/contextual behavior dominates (92.4% to 99.5% protective response rate). `DeepSeek-S` no longer has the old visibility-collapse problem in the May 9 saved rerun (0.2% no-visible proxy traces).


## Frozen Snapshot Scope

- tasks in frozen snapshot: `19`
- paper-setup tasks: `16`
- proxy tasks: `3`
- total evaluated samples: `302,776`
- current project total cost: `$831.08`
- total cost breakdown: MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$325.66`; OpenAI API reference sweep: `$0.76`.
- closed model families in this release: `Qwen`, `DeepSeek`, `Gemma`
- key methodological caveat: `Denevil` uses a clearly labeled local proxy dataset rather than the paper's original `MoralPrompt` setup
- extra local progress outside the frozen snapshot: `Llama` small is complete across `5` papers / `7` tasks and is intentionally excluded from the frozen `19 / 19` totals

## Model Summary

| Model family | Paper-setup tasks | Proxy tasks | Samples | Paper-setup macro accuracy |
| --- | ---: | ---: | ---: | ---: |
| `Qwen` | 6 | 1 | 102,886 | 0.550 |
| `DeepSeek` | 4 | 1 | 97,004 | 0.651 |
| `Gemma` | 6 | 1 | 102,886 | 0.531 |

Macro accuracy is computed over paper-setup tasks with a directly comparable accuracy metric. `CCD-Bench` and `Denevil` are excluded from that average.

For the full public package, move next to `README.md` or `results/release/2026-04-19-option1/README.md`.
