# Project Status Log

## 2026-04-21

### TrolleyBench Run — `results/trolleybench/20260421_100038/`

**Started:** 10:00 AM | **Status:** In progress

#### Run Configuration
- **Scenarios:** 18 trolley variants × 3 turns = 54 prompts per model
- **Models:** 15 (5 families × 3 sizes)
- **Temperatures:** 0.0, 0.7
- **Total:** 540 scenario runs, ~1620 API calls
- **API:** OpenRouter (model IDs verified 2026-04-21)

#### Completion Progress

| # | Model | T=0.0 | T=0.7 | Notes |
|---|-------|-------|-------|-------|
| 1 | qwen-L (Qwen3-235B) | Done | Done | ~81 min/temp due to deep reasoning chains |
| 2 | qwen-M (Qwen3-32B) | Done | ~94% | Scenario 9 had long stall at T=0.7 |
| 3 | qwen-S (Qwen3-8B) | Pending | Pending | |
| 4 | deepseek-L (DeepSeek-R1) | Pending | Pending | |
| 5 | deepseek-M (Chat V3.1) | Pending | Pending | |
| 6 | deepseek-S (R1-Distill-70B) | Pending | Pending | |
| 7 | llama-L (Llama-3.3-70B) | Pending | Pending | |
| 8 | llama-M (Llama-3.1-8B) | Pending | Pending | |
| 9 | llama-S (Llama-3.2-3B) | Pending | Pending | |
| 10 | gemma-L (Gemma-3-27B) | Pending | Pending | |
| 11 | gemma-M (Gemma-3-12B) | Pending | Pending | |
| 12 | gemma-S (Gemma-3-4B) | Pending | Pending | |
| 13 | minimax-L (MiniMax-M2.5) | Pending | Pending | |
| 14 | minimax-M (MiniMax-M1) | Pending | Pending | |
| 15 | minimax-S (MiniMax-01) | Pending | Pending | |

**Completed:** 3 of 30 model×temp combos (10%)

#### Preliminary Results (3 completed runs)

| Model | ECI | Entropy | Reversal | Framework |
|-------|-----|---------|----------|-----------|
| qwen-L T=0.0 | 0.714 | 0.333 | 0.0% | consequentialist |
| qwen-L T=0.7 | 0.714 | 0.177 | 10.0% | mixed |
| qwen-M T=0.0 | 0.750 | 0.059 | 10.0% | deontological |

#### Key Early Observations
- Larger models (qwen-L) show lower reversal rate at T=0.0 but temperature degrades stability
- qwen-M reaches same actions as qwen-L but through different ethical frameworks (deontological vs consequentialist)
- Footbridge, trapdoor, and man-in-front variants are the primary divergence points
- ECI ~0.7 across the board — models are moderately consistent but not perfectly so

### Code Changes Today

| Time | Commit | Description |
|------|--------|-------------|
| AM | `96ac6ed` | Add TrolleyBench results and fix eval null handling |
| AM | `7f72735` | Remove obsolete result runs |
| AM | `0472a0f` | Add README and meta.json for results |
| PM | `5820fb1` | Fix action extraction negation bug, variant mapping, API key validation |
| PM | `3dbda7d` | Add architecture diagrams to README |

### Bug Fixes Applied
1. **Action extraction false-positive** — "I would not pull the lever" was misclassified as "act". Fixed by filtering negated sentences before scoring act keywords.
2. **Variant name mismatch** — `organ_01` mapped to "organ" instead of "organ_transplant" in ECI computation. Fixed by using scenario metadata variant field.
3. **Missing bystander column** — `bystander_dilemma` variant was absent from report table. Added.
4. **API key validation** — Added startup check so missing `.env` fails fast instead of silently producing error results.

### GitHub Setup
- **Personal repo:** https://github.com/sunyuding/moral-psychology-benchmark
- **Org repo:** https://github.com/Center-for-Ethical-Intelligence/moral-psychology-benchmark
- **Org profile:** Description, website (ethical-intel.org), topics configured
- **Security:** Secret scanning + push protection enabled

### Next Steps
- [ ] Wait for full run to complete (12 model families remaining)
- [ ] Run `tools/legacy_openrouter/eval_trolleybench.py` on complete results
- [ ] Run `tools/legacy_openrouter/export_results.py` for CSV/markdown exports
- [ ] Commit final results and eval report
- [ ] Start next benchmark (MoReBench or Moral Circuits)
