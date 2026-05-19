# 2026-04-19 Option 1 Release Summary

This is the shortest frozen-snapshot readout in the repo: what the closed public release contains, which conclusions are safe to repeat, and where the main methodological caveats start.

## TL;DR

Key takeaways:

- **Main landscape:** text moral reasoning is much stronger than image moral judgment. UniMoral and Value sit around 0.653-0.673 mean accuracy, but SMID image accuracy averages only 0.364; even the best image line, `Qwen-L` at 0.483, is below 0.50. In plain terms: models can talk through moral choices and values better than they can see morally important cues in images.
- **Best all-around line:** `MiniMax-S` is the cleanest overall winner because it is not missing the image benchmark: UniMoral 0.661, SMID 0.432, Value 0.740, mean 0.611. The main warning is that the best text-only rows can look stronger, but they do not answer the image problem.
- **Scaling law:** there is no reliable bigger-is-better rule. Scale helps in a few places, especially Qwen on images (0.368 -> 0.483) and Llama on Value from S to M (0.529 -> 0.724). But there are clear reversals: Gemma image dips then rebounds (0.417 -> 0.364 -> 0.412), DeepSeek UniMoral falls from M to L (0.684 -> 0.563), and `MiniMax-L` is an image outlier at 0.199.
- **Family read:** Qwen is the clearest case where size helps vision; Gemma is the cleanest full S/M/L family but still non-monotonic; DeepSeek is useful for text but has no image route and its large line is not automatically better; Llama improves after the small line but M can beat L on text; MiniMax-S is the safest all-around line, while MiniMax-L is the clearest bad image outlier.
- **UniMoral is not one skill:** a model can match the human action but still miss the moral frame, the reason, or the consequence. Task winners rotate across RQ1 `DeepSeek-M` 0.684, RQ2 `Gemma-S` 0.599, RQ3 `Llama-M` 0.631, RQ4 semantic `Llama-M` 0.730, RQ4 lexical `Llama-L` 0.157. So the useful story is which part of moral reasoning each family handles, not one single moral score.
- **Cultural-style bias:** CCD-Bench shows a strong Europe/Nordic pull, not a normal accuracy score. 19 of 20 valid lines choose `Nordic Europe` as their dominant style. `GPT-5-nano Ref` is the most collapsed onto one cluster (27.8%), while `DeepSeek-S` is the least collapsed and the only non-Nordic dominant line (13.8%, `Sub Saharan Africa`).
- **OpenAI references:** the GPT rows mostly confirm the text baseline instead of changing the story. `GPT-4o-mini Ref` is close to the strong text band (UniMoral 0.673, Value 0.701); `GPT-5-mini Ref` beats `GPT-5-nano Ref` (0.739 vs 0.617 on Value), and `GPT-4.1-mini Ref` beats `GPT-4.1-nano Ref` (0.679 vs 0.646 on UniMoral). None of these rows has SMID, so they do not solve the image weakness.
- **Small-model follow-up:** Mistral/Qwen/Llama older routes add one simple takeaway: there is a capability floor. `Mistral Nemo`, `Qwen2.5 7B`, `Llama 3.1 8B`, and `Llama 3 8B` cluster on UniMoral from 0.632 to 0.648, but `Llama 3.2 1B` drops to 0.406. So these models are useful baselines, not a new top tier, and the 1B route is too small for this moral-choice setup.


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
