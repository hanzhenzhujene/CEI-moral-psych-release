# Benchmark Results Checklist

**Last validated:** 2026-05-15 (re-validated, no changes)

> Run `/validate-results` to regenerate. History tracked via `git log results/CHECKLIST.md`.

---

## Tier Legend

| Tier | Symbol | Meaning |
|------|--------|---------|
| T1 | :red_circle: | Harness complete — number exists but may not reflect true capability |
| T2 | :large_orange_diamond: | Result valid — no format failure, no missing modality, no proxy swap |
| T3 | :white_check_mark: | Interpretable for comparison — cross-model, paper-faithful, caveats resolved |
| — | :black_square_button: | Not run / not applicable |

---

## D1 — Content ("what the model believes")

### UniMoral — Action Prediction

| Model | Score | Tier | Note |
|-------|-------|------|------|
| DeepSeek-M | 0.684 | :white_check_mark: T3 | |
| Qwen-S | 0.647 | :white_check_mark: T3 | |
| Gemma-S | 0.635 | :white_check_mark: T3 | |
| Qwen-M | 0.664 | :white_check_mark: T3 | |
| Qwen-L | 0.665 | :white_check_mark: T3 | |
| Llama-S | 0.648 | :white_check_mark: T3 | |
| Llama-M | 0.670 | :white_check_mark: T3 | |
| Llama-L | 0.660 | :white_check_mark: T3 | |
| Gemma-M | 0.663 | :white_check_mark: T3 | |
| Gemma-L | 0.661 | :white_check_mark: T3 | |

**Saturation:** Spread 0.048 — **RETIRED.** Do not run new models. Score typology task instead.

### SMID — Visual Moral Judgment

| Model | Foundation | Moral Rating | Tier | Note |
|-------|-----------|-------------|------|------|
| Gemma-S | 0.475 | 0.359 | :large_orange_diamond: T2 | Vision route confirmed |
| Qwen-S (VL) | 0.478 | 0.258 | :large_orange_diamond: T2 | Vision route confirmed |
| DeepSeek | — | — | :black_square_button: | No vision route |
| Llama | — | — | :black_square_button: | Needs Llama-4-VL |
| MiniMax | — | — | :black_square_button: | Needs vision route |

**Blocker:** Only 2 families — needs 3rd for T3 promotion.

### Value Kaleidoscope — Relevance + Valence

| Model | Relevance | Valence | Tier | Note |
|-------|-----------|---------|------|------|
| DeepSeek-M | 0.671 | 0.598 | :white_check_mark: T3 | |
| Qwen-S | 0.667 | 0.698 | :white_check_mark: T3 | |
| Gemma-S | 0.606 | 0.579 | :white_check_mark: T3 | |
| Llama-M | — | — | :white_check_mark: T3 | In comparison.csv |

**Saturation:** Relevance spread 0.065 — **FLAG.** Queue conflict resolution task.

### CCD-Bench — Cultural Choice

| Model | Tier | Note |
|-------|------|------|
| DeepSeek-M | :large_orange_diamond: T2 | Cultural choice metric, not accuracy |
| Gemma-S | :large_orange_diamond: T2 | |
| Qwen-S | :large_orange_diamond: T2 | |

### DeNEVIL — Ethical Value Probing

| Model | Tier | Note |
|-------|------|------|
| All 3 lines | :red_circle: **T1** | BLOCKED: MoralPrompt dataset not acquired. Proxy (FULCRA) cannot compute APV/EVR/MVP. |

**Blocker:** Acquire MoralPrompt dataset.

---

## D2 — Process ("how the model reasons")

### TrolleyBench — Ethical Consistency + Reversal

| Model | ECI (T0.7) | Reversal (T0.7) | Tier | Note |
|-------|-----------|----------------|------|------|
| Qwen-S | 0.750 | 0.0% | :white_check_mark: T3 | |
| Qwen-M | 1.000 | 0.0% | :white_check_mark: T3 | |
| Qwen-L | 0.714 | 10.0% | :white_check_mark: T3 | |
| DeepSeek-S | 1.000 | 0.0% | :white_check_mark: T3 | |
| DeepSeek-M | 0.778 | 8.3% | :white_check_mark: T3 | |
| DeepSeek-L | 0.778 | 9.1% | :white_check_mark: T3 | |
| Llama-S | 0.800 | 25.0% | :white_check_mark: T3 | |
| Llama-M | 1.000 | 22.2% | :white_check_mark: T3 | |
| Llama-L | 0.644 | 12.5% | :white_check_mark: T3 | |
| Gemma-S | 0.533 | 25.0% | :white_check_mark: T3 | |
| Gemma-M | 0.467 | 22.2% | :white_check_mark: T3 | |
| Gemma-L | 0.644 | 36.4% | :white_check_mark: T3 | |
| MiniMax-S | 0.750 | 12.5% | :white_check_mark: T3 | |
| MiniMax-M | 0.644 | 40.0% | :white_check_mark: T3 | |
| MiniMax-L | 0.667 | 40.0% | :white_check_mark: T3 | |
| MiniMax-L T0.0 | N/A | N/A | :red_circle: **T1** | BLOCKED: all empty responses at T0.0 |

**Saturation:** Healthy (reversal spread 0–40%, ECI spread 0.467–1.000).

### MoReBench — Moral Reasoning (Advisor + Agent)

| Model | Advisor | Agent | Tier | Note |
|-------|---------|-------|------|------|
| Qwen-S | 0.595 | 0.586 | :large_orange_diamond: T2 | |
| Qwen-M | 0.395 | 0.219 | :red_circle: **T1** | BLOCKED: anomalous drop — investigate thinking-mode / model version |
| Qwen-L | 0.611 | 0.587 | :large_orange_diamond: T2 | |
| DeepSeek-S | 0.360 | 0.273 | :large_orange_diamond: T2 | Low but plausible for R1-distill |
| DeepSeek-M | 0.806 | 0.851 | :large_orange_diamond: T2 | Highest |
| DeepSeek-L | 0.524 | 0.499 | :large_orange_diamond: T2 | |
| Llama-S | 0.573 | 0.566 | :large_orange_diamond: T2 | |
| Llama-M | 0.535 | 0.553 | :large_orange_diamond: T2 | |
| Llama-L | 0.616 | 0.639 | :large_orange_diamond: T2 | |
| Gemma-S | 0.642 | 0.604 | :large_orange_diamond: T2 | |
| Gemma-M | 0.643 | 0.618 | :large_orange_diamond: T2 | |
| Gemma-L | 0.645 | 0.633 | :large_orange_diamond: T2 | Tight cluster (spread 0.041) |
| MiniMax-S | 0.670 | 0.716 | :large_orange_diamond: T2 | |
| MiniMax-M | 0.528 | 0.548 | :large_orange_diamond: T2 | |
| MiniMax-L | 0.445 | 0.435 | :large_orange_diamond: T2 | Inverted scaling |

**Saturation:** Healthy (agent spread 0.273–0.851). Watch Gemma cluster convergence.

### Moral Circuits — Judgment + Reasoning

| Model | Judgment | Reasoning | Tier | Note |
|-------|----------|-----------|------|------|
| Llama-S | 0.913 | 0.683 | :large_orange_diamond: T2 | |
| Llama-M | 0.950 | 0.963 | :large_orange_diamond: T2 | |
| Llama-L | 0.960 | 0.992 | :white_check_mark: T3 | Highest |
| Qwen-S | 0.929 | 0.946 | :large_orange_diamond: T2 | |
| Qwen-M | **0.192** | **0.208** | :red_circle: **T1** | BLOCKED: anomalous drop — investigate thinking-mode / model version |
| Qwen-L | 0.933 | 0.938 | :large_orange_diamond: T2 | |
| DeepSeek | — | — | :black_square_button: | N/A (requires open weights) |
| Gemma | — | — | :black_square_button: | N/A (requires open weights) |
| MiniMax | — | — | :black_square_button: | N/A (requires open weights) |

**Saturation:** Judgment spread 0.047 — **FLAG** (but only 2 families).

### M³oralBench — Multimodal Moral Judgment

| Model | Foundation | Judgment | Response | Tier | Note |
|-------|-----------|----------|----------|------|------|
| All 15 lines | 0.000–0.225 | 0.000–0.500 | 0.001–0.218 | :red_circle: **T1** | BLOCKED: vision pipeline not implemented — text-only fallback |

**Blocker:** Implement vision pipeline. All cells remain T1.

### MoralLens — Framework Detection + Double-Standard

| Model | CoT | Post-hoc | Double-Std | Tier | Note |
|-------|-----|---------|-----------|------|------|
| Qwen-S | 0.921 | 0.887 | 0.378 | :white_check_mark: T3 | |
| Qwen-M | **0.243** | **0.307** | **0.103** | :red_circle: **T1** | BLOCKED: anomalous drop — investigate thinking-mode / model version |
| Qwen-L | 0.921 | 0.847 | 0.440 | :white_check_mark: T3 | |
| DeepSeek-S | **0.012** | **0.062** | **0.006** | :red_circle: **T1** | BLOCKED: scorer needs `<think>` block stripping |
| DeepSeek-M | 0.890 | 0.882 | 0.421 | :large_orange_diamond: T2 | |
| DeepSeek-L | 0.615 | 0.674 | **0.040** | :red_circle: **T1** (ds) | BLOCKED: scorer needs `<think>` block stripping |
| Llama-S | 0.899 | 0.830 | 0.445 | :white_check_mark: T3 | |
| Llama-M | 0.888 | 0.791 | 0.456 | :white_check_mark: T3 | |
| Llama-L | 0.930 | 0.894 | 0.500 | :white_check_mark: T3 | |
| Gemma-S | 0.940 | 0.859 | 0.618 | :white_check_mark: T3 | |
| Gemma-M | 0.921 | 0.837 | 0.567 | :white_check_mark: T3 | |
| Gemma-L | 0.958 | 0.830 | 0.658 | :white_check_mark: T3 | Highest DS |
| MiniMax-S | 0.900 | 0.925 | 0.440 | :large_orange_diamond: T2 | |
| MiniMax-M | **0.273** | 0.586 | 0.211 | :red_circle: **T1** (cot) | BLOCKED: scorer needs `<think>` block stripping |
| MiniMax-L | 0.830 | 0.730 | 0.320 | :large_orange_diamond: T2 | |

**Saturation:** Healthy (DS spread 0.211–0.658).

---

## D3 — Identity ("who the model is")

### EMNLP Educator

| Model | CPST | HEXACO | Moral Dilemmas | Prompt Injection | Tier | Note |
|-------|------|--------|---------------|-----------------|------|------|
| DeepSeek-V3 | 0.913 | 0.597 | 0.949 | 0.855 | :white_check_mark: T3 | |
| DeepSeek-R1 | **0.112** | **0.047** | 0.815 | 0.815 | :red_circle: **T1** (CPST/HEX) | BLOCKED: scorer needs `<think>` block stripping |
| DeepSeek-R1-distill | **0.000** | **0.000** | 0.730 | 0.605 | :red_circle: **T1** (CPST/HEX) | BLOCKED: scorer needs `<think>` block stripping |
| Gemma-4B | 0.628 | 0.547 | 0.946 | 1.000 | :white_check_mark: T3 | |
| Gemma-12B | 0.795 | 0.492 | 0.977 | 0.980 | :white_check_mark: T3 | |
| Gemma-27B | 0.801 | 0.547 | 0.969 | 0.970 | :white_check_mark: T3 | |
| Llama-3B | 0.692 | 0.728 | 0.881 | 0.880 | :white_check_mark: T3 | |
| Llama-8B | 0.821 | 0.533 | 0.756 | 0.845 | :white_check_mark: T3 | |
| Llama-70B | 0.843 | 0.547 | 0.935 | 0.865 | :white_check_mark: T3 | |
| MiniMax-01 | 0.824 | 0.469 | 0.901 | 0.950 | :white_check_mark: T3 | |
| MiniMax-M1 | **0.000** | **0.000** | 0.892 | 0.910 | :red_circle: **T1** (CPST/HEX) | BLOCKED: scorer needs `<think>` block stripping |
| MiniMax-M2.5 | **0.000** | **0.019** | 0.898 | 0.900 | :red_circle: **T1** (CPST/HEX) | BLOCKED: scorer needs `<think>` block stripping |
| Qwen-8B | 0.718 | 0.639 | 0.986 | 0.935 | :white_check_mark: T3 | |
| Qwen-32B | 0.872 | 0.600 | 0.991 | 0.930 | :white_check_mark: T3 | |
| Qwen-235B | 0.837 | 0.561 | 0.972 | 0.920 | :white_check_mark: T3 | |

**Saturation:** All tasks healthy (spreads 0.259–0.395).

### MoralBench

| Model | MFQ Agree | MFQ Compare | Vig Agree | Vig Compare | Tier | Note |
|-------|-----------|------------|-----------|------------|------|------|
| DeepSeek-V3 | 0.180 | 0.500 | 0.911 | 0.542 | :large_orange_diamond: T2 | MFQ low but valid |
| DeepSeek-R1 | **0.000** | 0.250 | **0.000** | **0.000** | :red_circle: **T1** | BLOCKED: scorer needs `<think>` block stripping |
| DeepSeek-R1-distill | **0.000** | **0.000** | **0.000** | **0.000** | :red_circle: **T1** | BLOCKED: scorer needs `<think>` block stripping |
| Gemma-4B | 0.639 | 0.500 | 0.597 | 0.458 | :white_check_mark: T3 | |
| Gemma-12B | 0.842 | 0.350 | 0.921 | 0.583 | :white_check_mark: T3 | |
| Gemma-27B | 0.738 | 0.550 | 0.709 | 0.292 | :white_check_mark: T3 | |
| Llama-3B | 0.380 | 0.200 | **0.038** | 0.500 | :red_circle: **T1** (Vig Agree) | BLOCKED: extract_action_choice too narrow |
| Llama-8B | 0.465 | 0.200 | 0.732 | 0.375 | :large_orange_diamond: T2 | |
| Llama-70B | **0.050** | 0.350 | **0.038** | 0.542 | :red_circle: **T1** (Agree tasks) | BLOCKED: extract_action_choice too narrow |
| MiniMax-01 | 0.912 | 0.500 | 0.933 | 0.458 | :white_check_mark: T3 | |
| MiniMax-M1 | **0.000** | **0.000** | **0.000** | **0.000** | :red_circle: **T1** | BLOCKED: scorer needs `<think>` block stripping |
| MiniMax-M2.5 | **0.000** | 0.050 | **0.000** | 0.083 | :red_circle: **T1** | BLOCKED: scorer needs `<think>` block stripping |
| Qwen-8B | 0.363 | 0.500 | 0.824 | 0.500 | :large_orange_diamond: T2 | |
| Qwen-32B | **0.000** | 0.100 | **0.000** | 0.208 | :red_circle: **T1** (Agree tasks) | BLOCKED: extract_action_choice too narrow + possible `<think>` |
| Qwen-235B | 0.898 | 0.350 | 0.819 | 0.458 | :white_check_mark: T3 | |

**Saturation:** All tasks healthy (MFQ agreement spread 0.732).

---

## Action Items

### Critical — blocks paper claims

- [ ] **Fix reasoning-model scorer** — R1/R1-distill/M1/M2.5 produce systematic zeros on personality + agreement tasks (~30 T1 cells). Adapt scorer to strip `<think>` blocks.
- [ ] **Investigate Qwen-M (Qwen3-32B) anomaly** — Collapses across MC (0.192), MRB (0.219), ML CoT (0.243). Training artifact? Wrong model version? 8 T1 cells.

### High — quality gaps

- [ ] **Audit MoralBench agreement scorer** — Qwen-32B, Llama-70B, Llama-3B score 0.0 on agreement tasks despite passing other tasks. ~6 cells.
- [ ] **Add 3rd SMID vision family** — Only Gemma + Qwen. Need Llama-4-VL or MiniMax-01 for T3 promotion.
- [ ] **Score Value Kaleidoscope conflict resolution task** — Relevance spread 0.065, in FLAG zone.

### Moderate — coverage

- [ ] **Stop running UniMoral action prediction** — RETIRED (spread 0.048). Score typology task instead.
- [ ] **Implement M³oralBench image pipeline** — 15 T1 cells blocked on vision infra.
- [ ] **Acquire MoralPrompt dataset for DeNEVIL** — 3 T1 cells; proxy only.
- [ ] **Extend Moral Circuits to more families** — Judgment spread 0.047, FLAG threshold with only 2 families.

### Monitoring

- [ ] Moral Circuits judgment saturation (0.047 spread, 2 families)
- [ ] Gemma MoReBench convergence (S/M/L spread 0.041)
- [ ] MoralLens CoT top-cluster convergence (0.90–0.96 range)

