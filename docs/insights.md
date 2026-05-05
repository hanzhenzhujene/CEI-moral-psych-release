# Benchmark Insights

Cross-cutting findings from the CEI moral psychology benchmark evaluation (13 papers, 5 model families, 302K+ samples).

**Key results referenced:**
- [Moral-Psych release report](../results/release/2026-04-19-option1/jenny-group-report.md) — Jenny's 5-benchmark frozen snapshot
- [Topline summary](../results/release/2026-04-19-option1/topline-summary.md) — Shortest frozen-snapshot readout
- [TrolleyBench eval report](../results/trolleybench/20260421_100038/eval_report.md) — Multi-turn ethical consistency results
- [Joseph's progress report](../PROGRESS.md) — Full family-size matrix for all 5 benchmarks (MoReBench, Moral Circuits, M3oralBench, MoralLens, TrolleyBench)

## 1. Bigger Does Not Mean More Moral

There is no universal scaling law for ethical reasoning. Gemma on vision-moral tasks goes 0.417 -> 0.364 -> 0.412 (S->M->L). Llama-M beats Llama-L on value recognition (0.724 vs 0.692). MiniMax-S outperforms MiniMax-L on advisory tasks (0.716 vs 0.435 agent score). Size helps on some tasks, but the pattern is jagged, not monotonic.

_See: [family scaling profile](../results/release/2026-04-19-option1/jenny-group-report.md#family-scaling-profile), [PROGRESS.md MoReBench column](../PROGRESS.md)_

## 2. Vision Is the Real Bottleneck

Text-based moral classification is approaching saturation (UniMoral spread is only 0.048 across all models). But when models have to judge morality from images, accuracy drops to 0.378 mean with massive variance. The next frontier for moral AI is not reading — it is seeing.

_See: [benchmark difficulty profile](../results/release/2026-04-19-option1/jenny-group-report.md#benchmark-difficulty-profile)_

## 3. Longer Reasoning Chains Make Models More Persuadable, Not Less

DeepSeek-R1 (the chain-of-thought heavyweight) hit a 42.9% reversal rate when challenged in multi-turn trolley problems. Meanwhile, smaller distilled models held firm at 0%. The models that "think harder" seem more susceptible to flipping under adversarial follow-ups.

_See: [TrolleyBench eval report](../results/trolleybench/20260421_100038/eval_report.md) — deepseek-L_T0.0 reversal 42.9% vs deepseek-S_T0.7 reversal 0%_

## 4. Same Decision, Different Philosophy

Qwen-32B justifies pulling the lever via deontology. Qwen-235B justifies the same action via consequentialism. The ethical framework is unstable even when the final action is consistent. This matters if we care about why a model decides, not just what it decides.

_See: [TrolleyBench eval report](../results/trolleybench/20260421_100038/eval_report.md) — qwen-M dominant framework "deontological" vs qwen-L "consequentialist"_

## 5. Temperature Is a Safety Lever

At T=0.0, models are consistent and resist persuasion. At T=0.7, framework mixing and position reversals spike. For morally-sensitive deployments, low temperature is not just a preference — it is a guardrail.

_See: [TrolleyBench eval report](../results/trolleybench/20260421_100038/eval_report.md) — compare T0.0 vs T0.7 rows across all models_

## Bottom Line

Moral reasoning in LLMs is task-dependent, scale-inconsistent, and framework-fragile. If you are building anything where ethical consistency matters, do not assume "bigger model = safer model."

---

**Data sources:** TrolleyBench (15 models x 2 temps), Moral-Psych Suite (UniMoral, SMID, Value Kaleidoscope, CCD-Bench, DeNEVIL), MoReBench, Moral Circuits, M3oralBench, MoralLens.

**Last updated:** 2026-05-05
