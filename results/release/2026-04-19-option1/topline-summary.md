# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

My result TL;DR:

- **Overall model-wise:** `MiniMax-S` is the strongest all-around line on the three comparable accuracy benchmarks: UniMoral 0.661, SMID 0.432, Value Kaleidoscope 0.740, average 0.611. `Qwen-L` is close at 0.600. `Llama-S` is weakest at 0.464, mainly because of low SMID and Value scores.
- **Text-only model-wise:** `MiniMax` is the strongest family on text benchmarks. `MiniMax-S`, `MiniMax-M`, and `MiniMax-L` all score around 0.699-0.701 across UniMoral and Value Kaleidoscope. `Llama-M` is also strong at 0.697. `Llama-S` is weakest at 0.588.
- **Benchmark-wise:** `SMID` is the hardest benchmark. It is the vision task, with the lowest mean accuracy (0.364) and widest spread (0.285), so vision-side moral judgment is the main bottleneck. `UniMoral` is the most saturated benchmark, with models clustered from 0.563 to 0.684. `Value Kaleidoscope` is in the middle, with clear but less extreme spread.
- **Scaling-wise:** There is no universal scaling law. Bigger models are not always better: `Gemma` is non-monotonic on SMID, and `Llama-M` beats `Llama-L` on Value. Size helps on some tasks, but the effect depends on benchmark and route.
- **CCD-Bench:** `CCD-Bench` measures cultural choice style, not accuracy. Most lines over-select `option_6`, the Nordic Europe cluster; `DeepSeek-S` is the exception, peaking on `option_7`, Sub-Saharan Africa. The point is not that one option is "correct," but that models may collapse toward specific cultural styles. Concentration ranges from `DeepSeek-S` at 13.8% to `Llama-S` at 23.9%, so `DeepSeek-S` is more spread out while `Llama-S` is more concentrated.
- **DeNEVIL:** `DeNEVIL` is proxy safety-behavior evidence, not official benchmark-faithful scoring. Since the original MoralPrompt scorer is not available locally, this release classifies visible behaviors: refusal, redirect, corrective/contextual answer, risky continuation, ambiguous answer, or no visible answer. Results show high protective/contextual response rates, 92.4% to 99.5%, meaning models usually refuse, redirect, or add safety context instead of continuing harmful content.


## Frozen Snapshot Scope

- tasks in frozen snapshot: `19`
- paper-setup tasks: `16`
- proxy tasks: `3`
- total evaluated samples: `302,776`
- current project total cost: `$758.83`
- total cost breakdown: MiniMax API: `$504.66`; OpenRouter for all other models: `$254.17`.
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
