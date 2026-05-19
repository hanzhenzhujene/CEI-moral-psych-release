# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

Key takeaways:

- **What each benchmark means:** `UniMoral` is the human moral-reasoning pipeline (choose an action, name the moral frame, identify the decision factor, and generate consequences); `SMID` is moral perception from images; `Value Kaleidoscope` is value/right/duty recognition; `CCD-Bench` is cultural choice style under value conflict; `DeNEVIL` is risky-prompt behavior. That is why only UniMoral, SMID, and Value are treated as comparable accuracy surfaces, while CCD-Bench and DeNEVIL stay behavioral readouts.
- **Best like-for-like line:** `MiniMax-S` is the strongest fully comparable line, averaging 0.611 across UniMoral action 0.661, SMID 0.432, and Value 0.740. This is the cleanest overall topline because all three comparable metrics are observed on the same line.
- **Best text-only line:** `GPT-5-mini Ref` is the strongest pure text line, reaching UniMoral 0.678 and Value 0.739. It should not be called the best all-around line because there is no public SMID route on that line.
- **OpenAI text-only references:** 5 OpenAI reference rows are integrated. Best OpenAI UniMoral is `GPT-4.1-mini Ref` at 0.679; best OpenAI Value is `GPT-5-mini Ref` at 0.739. These calibrate text moral-reasoning results against OpenAI routes, but they are not S/M/L scaling curves and do not provide SMID or DeNEVIL evidence.
- **The hardest benchmark is SMID:** `SMID` has the lowest mean accuracy (0.364) and widest spread (0.285), while `UniMoral` is tightly clustered (0.121 spread). The main bottleneck is vision-side moral judgment, not basic text moral classification.
- **UniMoral RQ-level interpretation:** The four-task view should not be collapsed into one scalar: task winners rotate across RQ1 `DeepSeek-M` 0.684, RQ2 `Gemma-S` 0.599, RQ3 `Llama-M` 0.631, RQ4 semantic `Llama-M` 0.730, RQ4 lexical `Llama-L` 0.157. That pattern supports task-specific moral-reasoning strengths rather than a simple bigger-is-better family scaling story.
- **There is no universal scaling law:** `Gemma` is non-monotonic on SMID (0.417 -> 0.364 -> 0.412), and `Llama-M` still beats `Llama-L` on Value (0.724 vs 0.692). Size helps on some tasks, but not in one clean monotonic pattern.
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
