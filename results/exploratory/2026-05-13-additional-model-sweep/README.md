# Additional Model Sweep: UniMoral + CCD-Bench

Date: 2026-05-13

This follow-up brings five older or smaller OpenRouter routes into the deliverable as a capability-floor check. It asks whether `Mistral`, `Qwen`, and smaller `Llama` routes change the main moral-psych story, or whether they mainly show where text moral-choice performance starts to fall off.

## Key Findings

- Best UniMoral result: **Mistral Nemo** at **0.648**.
- Weakest UniMoral result: **Llama 3.2 1B** at **0.406**; this is the only clear low-performing line.
- The other four UniMoral lines are tightly clustered from **0.632** to **0.648**, so the main separation is the 1B route versus the 7B-12B routes.
- CCD-Bench is **not accuracy**. All five lines peak on **Nordic Europe**, but concentration differs: **Llama 3.2 1B** is most diffuse at **15.9%**, while **Mistral Nemo** is most concentrated at **25.3%**.
- Scaling readout: this looks like a **capability floor**, not a clean monotonic scaling law. Llama 3.2 1B is much weaker on UniMoral, but the 7B-12B models are tightly clustered.

## Interpretation

**Model-wise:** Mistral Nemo is the top UniMoral line at 0.648, but Qwen2.5 7B, Llama 3.1 8B, and Llama 3 8B are close behind from 0.632 to 0.640. Llama 3.2 1B is the clear weak line at 0.406, with a lower answer rate as well.

**Benchmark-wise:** UniMoral gives a clear performance separation between the very small 1B route and the stronger 7B-12B cluster. CCD-Bench gives a style/concentration readout rather than a correctness score: all models peak on Nordic Europe, but Llama 3.2 1B is most diffuse (15.9% dominant share; 9.12 effective clusters), while Mistral Nemo is most concentrated (25.3%; 7.22 effective clusters).

**Compared with the main release:** the follow-up supports the same high-level interpretation. Once a route is in the mid-sized instruction-model range, text moral-choice scores are close enough that the benchmark-specific story matters more than a simple model-size ranking. The 1B route is the warning case.

**Bottom line:** this is the practical takeaway to report: do not overclaim a universal bigger-is-better trend. Very small routes can fall off sharply, while several older or mid-sized instruction routes remain competitive on selected text moral-choice and cultural-style checks.

## Result Tables

### UniMoral

| Model | Accuracy | Answer rate | Correct | Samples |
|---|---:|---:|---:|---:|
| Mistral Nemo | 0.648 | 0.999 | 5693 | 8784 |
| Qwen2.5 7B | 0.640 | 1.000 | 5624 | 8784 |
| Llama 3.1 8B | 0.639 | 0.993 | 5611 | 8784 |
| Llama 3 8B | 0.632 | 1.000 | 5550 | 8784 |
| Llama 3.2 1B | 0.406 | 0.736 | 3563 | 8784 |

### CCD-Bench

| Model | Valid choice rate | Dominant cluster | Dominant share | Effective clusters |
|---|---:|---|---:|---:|
| Mistral Nemo | 0.998 | Nordic Europe | 0.253 | 7.22 |
| Llama 3.1 8B | 1.000 | Nordic Europe | 0.247 | 7.14 |
| Llama 3 8B | 1.000 | Nordic Europe | 0.220 | 7.91 |
| Qwen2.5 7B | 1.000 | Nordic Europe | 0.178 | 8.78 |
| Llama 3.2 1B | 1.000 | Nordic Europe | 0.159 | 9.12 |

## Figures

![Additional model sweep UniMoral accuracy](../../../figures/exploratory/additional_model_sweep_unimoral_accuracy.svg)

![CCD dominant cluster share](../../../figures/exploratory/additional_model_sweep_ccd_dominant_share.svg)

![Additional model sweep scaling](../../../figures/exploratory/additional_model_sweep_scaling.svg)

## Metric Boundary

- UniMoral accuracy is computed from the completed run records with the same final A/B scoring rule across all five routes; no new API calls were used.
- CCD-Bench reports cultural-choice distribution and concentration, not correctness.
- This follow-up is a capability-floor check, not a replacement for the main release matrix.
