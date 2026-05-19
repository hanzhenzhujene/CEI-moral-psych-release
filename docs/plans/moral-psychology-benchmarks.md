# CEI Moral Psychology Benchmarks — Tier-1 Experiment Guide

## Context

From Yaoli Mao's Slack message (2026-04-20):

> I put together a summary for the 13 Tier-1 papers we've selected to run first with some help from Claude. For each paper, it covers the dataset, prompt templates, evaluation protocol, and links.

- **Summary page**: https://moiren.github.io/cei-moralpsy-bench/index.html
- **Slide deck**: https://docs.google.com/presentation/d/10Jp6BFi8qz2GUzN2RLJ2t2IJ1UcWgSF-/edit?usp=sharing&ouid=100501328091998253562&rtpof=true&sd=true
- **Yaoli's Calendly**: https://calendly.com/yaoli-mao/yaoli-s-calendar

## Shared Model Set

**Frontier models:** GPT-4o, Claude 3.5 Sonnet, Gemini 2.5 Pro

**Reasoning variants:** o3, Claude with extended thinking, Gemini thinking mode

**Open-weight baselines:** Llama 3 (70B/8B), Qwen 2.5 72B, DeepSeek-R1

---

## Paper Summaries

### #1 — MoReBench (Chiu 2025)

Tests "process-focused moral reasoning" scored against philosophy-authored rubrics across 5 ethical frameworks. Two roles tested (advisor vs agent); includes 23,000+ evaluation criteria across identification, logic, process clarity, and outcomes.

- **Dataset:** 500 core scenarios + 150 framework-specific variants
- **Key prompt structure:** System sets role (moral advisor/agent); user provides dilemma requesting step-by-step reasoning
- **Links:** [arxiv](https://arxiv.org/abs/2510.16380) | [github](https://github.com/morebench/morebench) | [huggingface](https://huggingface.co/datasets/morebench)

### #2 — TrolleyBench (Zhu 2025)

Examines "ethical consistency across structurally similar trolley-problem variants" with follow-up probes designed to expose contradictions.

- **Dataset:** Trolley variants (switch, footbridge, loop, trapdoor) + clarifying/contradictory follow-ups
- **Evaluation:** Ethical Consistency Index (ECI) using entropy-based scoring
- **Links:** [openreview](https://openreview.net/forum?id=27j9XJQV5O)

### #3 — Moral Circuits (Schacht 2025)

Mechanistic interpretability study identifying which neurons activate for different moral concepts. Requires open-weight model access for activation recording.

- **Approach:** Feed matched moral/immoral statement pairs; measure neuron activation differences; ablate neurons and assess reasoning degradation
- **Models:** Llama 3, Qwen 2.5 only (API models excluded)
- **Links:** [coairesearch](https://coairesearch.org/research/mapping_moral_reasoning) | [github](https://github.com/coairesearch/mapping_moral_reasoning)

### #4 — M³oralBench (Yan 2024)

Multimodal benchmark testing vision-language model moral judgment on 1,160 AI-generated image scenarios mapped to MFT foundations.

- **Tasks:** Moral judgment (right/wrong), foundation classification, moral response generation
- **Evaluation:** Accuracy against human moral foundation votes
- **Links:** [arxiv](https://arxiv.org/abs/2412.20718) | [github](https://github.com/BeiiiY/M3oralBench)

### #5 — MoralLens (Samway 2025)

Reveals a "double standard" where CoT prompting produces deontological reasoning while post-hoc explanations appear consequentialist.

- **Key experiment:** Same 600+ dilemmas under two conditions — think-then-decide vs. decide-then-explain
- **Taxonomy:** Classifies rationales into 16 types (8 consequentialist, 8 deontological)
- **Links:** [aclanthology](https://aclanthology.org/2025.emnlp-main.1563) | [github](https://github.com/keenansamway/moral-lens)

### #6 — UniMoral (Kumar 2025)

Multilingual benchmark spanning Arabic, Chinese, English, Hindi, Russian, Spanish with 8,784 annotated dilemmas. Designated ACL 2025 Best Resource Paper.

- **Tasks:** Action prediction, ethical framework identification, factor attribution, consequence generation
- **Annotator profiles:** Includes MFQ and VSM cultural survey data
- **Links:** [arxiv](https://arxiv.org/abs/2502.14083) | [huggingface](https://huggingface.co/datasets/shivaniku/UniMoral) (gated)

### #7 — SMID (Crone 2018)

Builds on 2,941 real photographs rated by 820 humans with normative data on valence, arousal, moral wrongness, and MFT foundation relevance.

- **Benchmark design:** No standardized script exists; researchers design custom evaluation tasks
- **Evaluation:** Pearson/Spearman correlation between VLM ratings and human norms
- **Links:** [PLOS ONE](https://journals.plos.org/plosone) | [OSF dataset](https://osf.io/2rqad)

### #8 — Denevil (Duan 2023)

Adversarial stress test using 2,397 prompts designed to induce moral violations. Includes ValueCompass alignment intervention.

- **Setup:** Baseline value elicitation → adversarial probing → violation scoring per foundation
- **Focus:** Which foundations are easiest/hardest to compromise
- **Links:** [arxiv](https://arxiv.org/abs/2310.11053) | [github](https://github.com/microsoft/ValueCompass)

### #9 — Value Kaleidoscope (Sorensen 2024)

Tests whether models recognize "multiple right answers coexist and genuinely conflict" using ~218,000 value/right/duty statements.

- **Tasks:** Value identification, conflict recognition, pluralistic reasoning (opposing defensible responses)
- **Evaluation:** Coverage, accuracy, pluralism score
- **Links:** [arxiv](https://arxiv.org/abs/2309.00779) | [github](https://github.com/tsor13/kaleido) | [huggingface](https://huggingface.co/datasets/allenai/ValuePrism)

### #10 — CCD-Bench (Rahman 2025)

Measures "which culture does the LLM silently favour when values clash" using 2,182 dilemmas with 10 anonymized GLOBE cultural cluster options.

- **Analysis:** Cluster frequency distribution, position bias, entropy/Gini diversity, KL divergence
- **Key finding:** Nordic Europe significantly overweighted (20.2% vs. 10% chance)
- **Links:** [arxiv](https://arxiv.org/abs/2510.03553) | [github](https://github.com/smartlab-nyu/CCD-Bench)

### #11 — Are Rules Meant to be Broken (Kumar 2025)

Applies UniMoral framework filtered for rule-vs-principle dilemmas across 24 languages. Tests Kohlberg progression from conventional to post-conventional reasoning.

- **Scoring:** Justification quality on Kohlberg scale (pre-, conventional, post-conventional)
- **Focus:** Can models articulate principled rule-breaking?
- **Links:** Same as UniMoral (#6)

### #12 — MoralBench (Ji 2024)

Creates moral "fingerprint" using adapted MFQ-30 questionnaire and 132 moral foundation vignettes including Liberty dimension.

- **Tasks:** Binary agreement assessment, comparative ranking of moral statements
- **Output:** Radar chart moral profile per model
- **Links:** [arxiv](https://arxiv.org/abs/2406.04428) | [github](https://github.com/agiresearch/MoralBench)

### #13 — EMNLP Educator-role (Jiang 2025)

Tests teacher-role LLMs against professional (CPST-E) and personality (HEXACO-60) standards. Includes soft prompt injection attacks and temperature sweeps.

- **Setup:** Personality profiling → 88 moral dilemmas (Kohlberg-scored) → adversarial injection → temperature variation
- **Risk dimensions:** 4 categories targeted in attack vectors
- **Links:** [arxiv](https://arxiv.org/abs/2508.15250) | [github](https://github.com/E-M-N-L-P/EMNLP-Educator-role)

---

## Key Evaluation Patterns Across Benchmarks

- **Scoring diversity:** Binary choices, Likert scales, rubric checklists (23,000+ items in MoReBench), free-text rationale analysis
- **Consistency metrics:** Entropy-based, pairwise ranking accuracy, Cohen's kappa against human annotators
- **Interpretability:** Circuit ablation (Moral Circuits), activation analysis, hidden preference detection (CCD-Bench cultural bias)
- **Robustness testing:** Adversarial prompts (Denevil), contradictory follow-ups (TrolleyBench), prompt injection (EMNLP Educator)
