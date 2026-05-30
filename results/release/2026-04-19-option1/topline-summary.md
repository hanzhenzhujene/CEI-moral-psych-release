# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

Key takeaways:

- **Bottom line:** text moral reasoning is usable; image moral judgment is the bottleneck. UniMoral and Value average 0.653-0.673, while SMID averages 0.364; even the best SMID line, `Qwen-L` at 0.483, stays below 0.50.
- **Best comparable all-around line:** `MiniMax-S` is the cleanest line with text, image, and value evidence: UniMoral 0.661, SMID 0.432, Value 0.740, three-metric mean 0.611.
- **Best text-only line:** `GPT-5.5` is strongest when SMID is excluded: UniMoral 0.684, Value 0.736, two-metric mean 0.710. Do not call it best overall because it has no image result.
- **Scaling read:** bigger is not reliably better. Scale helps Qwen on SMID (0.368 -> 0.483) and Llama on Value from S to M (0.529 -> 0.724), but reverses or stalls elsewhere: Gemma SMID 0.417 -> 0.364 -> 0.412, DeepSeek UniMoral 0.684 -> 0.563, and `MiniMax-L` SMID 0.198.
- **UniMoral readout:** do not collapse RQ1-RQ4 into one moral score. Winners rotate across RQ1 `DeepSeek-M` 0.684, RQ2 `GPT-5.5` 0.637, RQ3 `Llama-M` 0.631, RQ4 semantic `Llama-M` 0.730, RQ4 lexical `GPT-5.5` 0.165, so the result is task-specific moral reasoning, not one universal rank.
- **CCD-Bench read:** this is cultural-choice behavior, not accuracy. 20 of 21 valid lines choose `Nordic Europe` as the dominant style; `GPT-5 nano` is most concentrated (27.8%), while `DeepSeek-S` is least concentrated and the only non-Nordic dominant line (13.8%, `Sub Saharan Africa`).
- **OpenAI/GPT read:** GPT-5 is a text-only S/M/L series: `GPT-5 nano` = S, `GPT-5 mini` = M, `GPT-5.5` = L. Value jumps from 0.617 to 0.739 and then plateaus at 0.736; UniMoral tops out at `GPT-5.5` (0.684). GPT-4o/GPT-4.1 rows are separate text refs, and none has SMID or DeNEVIL. Completed GPT-5 RQ2-RQ4 follow-up: `GPT-5.5` leads the GPT-5 line on RQ2 accuracy 0.637, RQ3 accuracy 0.601, RQ4 BERTScore F1 0.725, and RQ4 METEOR 0.165. Overall semantic RQ4 still peaks at `Llama-M` 0.730, so this is strong GPT text evidence, not one universal UniMoral winner.
- **DeNEVIL boundary:** current DeNEVIL evidence is FULCRA-backed proxy behavior, not paper-faithful MoralPrompt scoring. Use the behavioral-outcomes figure for refusal/context/risk patterns, not a benchmark accuracy ranking.
- **Small-model floor:** the May 13 Mistral/Qwen/Llama follow-up shows a capability threshold. `Mistral Nemo`, `Qwen2.5 7B`, `Llama 3.1 8B`, and `Llama 3 8B` cluster on UniMoral from 0.632 to 0.648; `Llama 3.2 1B` drops to 0.406.


## Frozen Snapshot Scope

- tasks in frozen snapshot: `19`
- paper-setup tasks: `16`
- proxy tasks: `3`
- total evaluated samples: `302,776`
- current project total cost: `$888.06`
- total cost breakdown: MiniMax API: `$504.66`; OpenRouter model-family runs: `$343.42`, including `$17.760398` from the full selected-grid OpenRouter follow-up; OpenAI API reference sweep: `$39.98`.
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
