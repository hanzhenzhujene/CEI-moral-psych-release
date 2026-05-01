# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

If you only read one section, read these six takeaways:

- **Best like-for-like line:** `Qwen-L` is the strongest fully comparable line, averaging 0.600 across UniMoral 0.665, SMID 0.483, and Value 0.653. This is the cleanest overall topline because all three comparable metrics are observed on the same line.
- **Best text-only line:** `Llama-M` is the strongest pure text line, reaching UniMoral 0.670 and Value 0.724. It should not be called the best all-around line because there is no public SMID route on that line.
- **The hardest benchmark is SMID:** `SMID` has the lowest mean accuracy (0.378) and widest spread (0.266), while `UniMoral` is tightly clustered (0.048 spread). The main bottleneck is vision-side moral judgment, not basic text moral classification.
- **There is no universal scaling law:** `Gemma` is non-monotonic on SMID (0.417 -> 0.364 -> 0.412), and `Llama-M` still beats `Llama-L` on Value (0.724 vs 0.692). Size helps on some tasks, but not in one clean monotonic pattern.
- **CCD-Bench shows cultural choice style, not accuracy.** Every released line with valid CCD choices currently peaks on `option_6 (Nordic Europe)`, but concentration still varies meaningfully, from `Gemma-L` at 17.6% to `Llama-S` at 23.9%. The key question is how narrowly each line collapses onto one cultural cluster, not who has the highest "accuracy."
- **DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring.** Among completed lines with usable visible traces, protective/contextual behavior dominates (92.4% to 99.5% protective response rate). `DeepSeek-M` is the main caveat because 86.0% of prompts surfaced no visible answer, so that line should be read as a trace-surfacing failure rather than a harmful-behavior result.


## Frozen Snapshot Scope

- tasks in frozen snapshot: `19`
- paper-setup tasks: `16`
- proxy tasks: `3`
- total evaluated samples: `302,776`
- current project cost estimate: `$84.02`
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
