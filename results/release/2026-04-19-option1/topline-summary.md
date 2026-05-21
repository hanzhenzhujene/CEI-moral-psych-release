# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

If you only read one section, read these key takeaways:

- **Best like-for-like line:** `MiniMax-S` is the strongest fully comparable line, averaging 0.611 across UniMoral 0.661, SMID 0.432, and Value 0.740. This is the cleanest overall topline because all three comparable metrics are observed on the same line.
- **Best text-only line:** `GPT-5.5` is the strongest pure text line, reaching UniMoral 0.684 and Value 0.736. It should not be called the best all-around line because there is no public SMID route on that line.
- **OpenAI text-only Batch references:** 6 Responses/Batch API reference lines are now integrated, each with 76,486/76,486 response rows collected and parser coverage from 76,401 to 76,486 parsed rows. Best OpenAI UniMoral is `GPT-5.5` at 0.684; best OpenAI Value is `GPT-5 mini` at 0.739. SMID and DeNEVIL remain intentionally `n/a` for these text-only references.
- **The hardest benchmark is SMID:** `SMID` has the lowest mean accuracy (0.364) and widest spread (0.285), while `UniMoral` is tightly clustered (0.121 spread). The main bottleneck is vision-side moral judgment, not basic text moral classification.
- **There is no universal scaling law:** `Gemma` is non-monotonic on SMID (0.417 -> 0.364 -> 0.412), and `Llama-M` still beats `Llama-L` on Value (0.724 vs 0.692). Size helps on some tasks, but not in one clean monotonic pattern.
- **CCD-Bench shows cultural choice style, not accuracy.** Every released line with valid CCD choices currently peaks on `option_6 (Nordic Europe)`, but concentration still varies meaningfully, from `DeepSeek-S` at 13.8% to `GPT-5 nano` at 27.8%. The key question is how narrowly each line collapses onto one cultural cluster, not who has the highest "accuracy."
- **DeNEVIL is proxy behavioral evidence, not benchmark-faithful scoring.** Among completed lines with usable visible traces, protective/contextual behavior dominates (92.4% to 99.5% protective response rate). `DeepSeek-S` no longer has the old visibility-collapse problem in the May 9 saved rerun (0.2% no-visible proxy traces).
- **Current GitHub-facing boundary:** No MiniMax-M2.5 text benchmark remains live; the saved MiniMax-M2.5 text/proxy pass is already parsed into the public tables and SVGs. SMID remains `TBD`, so the medium MiniMax line is not a fully comparable all-around line yet.


## Frozen Snapshot Scope

- tasks in frozen snapshot: `19`
- paper-setup tasks: `16`
- proxy tasks: `3`
- total evaluated samples: `302,776`
- current project total cost: `$759.59 confirmed before May 16 OpenAI Batch additions`
- total cost breakdown: MiniMax API: `$504.66`; OpenRouter for other model-family runs: `$254.17`; OpenAI API reference sweep: `$0.76 confirmed before May 16; new OpenAI Batch reference sweeps pending billing confirmation`.
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
