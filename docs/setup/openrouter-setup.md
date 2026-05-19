# OpenRouter Setup for CEI Benchmark Evaluation

## Why OpenRouter

Running 13 benchmarks × 10+ models requires calling multiple providers (OpenAI, Anthropic, Google, Meta, DeepSeek). OpenRouter provides a **single API endpoint** for all of them — one key, one SDK, one billing dashboard.

- **Website**: https://openrouter.ai
- **Docs**: https://openrouter.ai/docs
- **Pricing**: https://openrouter.ai/models (pass-through rates, some models free)

## Target Models

| Model | OpenRouter ID | Type |
|-------|--------------|------|
| GPT-4o | `openai/gpt-4o` | Frontier |
| Claude 3.5 Sonnet | `anthropic/claude-3.5-sonnet` | Frontier |
| Gemini 2.5 Pro | `google/gemini-2.5-pro` | Frontier |
| o3 | `openai/o3` | Reasoning |
| Claude (extended thinking) | `anthropic/claude-3.5-sonnet` | Reasoning |
| Gemini (thinking mode) | `google/gemini-2.5-pro` | Reasoning |
| Llama 3 70B | `meta-llama/llama-3-70b` | Open-weight |
| Llama 3 8B | `meta-llama/llama-3-8b` | Open-weight |
| Qwen 2.5 72B | `qwen/qwen-2.5-72b-instruct` | Open-weight |
| DeepSeek-R1 | `deepseek/deepseek-r1` | Open-weight |

> **Note**: Check https://openrouter.ai/models for latest model IDs and availability.

## Quick Start

### 1. Get API Key

Sign up at https://openrouter.ai and generate an API key.

### 2. Install SDK

```bash
pip install openai  # OpenRouter is OpenAI-compatible
```

### 3. Basic Usage

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-v1-xxx",  # your OpenRouter key
)

MODELS = [
    "openai/gpt-4o",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.5-pro",
    "meta-llama/llama-3-70b-instruct",
    "meta-llama/llama-3-8b-instruct",
    "qwen/qwen-2.5-72b-instruct",
    "deepseek/deepseek-r1",
]

def query_model(model: str, prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

### 4. Batch Evaluation Pattern

```python
import json
from pathlib import Path

def run_benchmark(benchmark_name: str, prompts: list[str], models: list[str], output_dir: str = "results"):
    Path(output_dir).mkdir(exist_ok=True)

    for model in models:
        results = []
        for i, prompt in enumerate(prompts):
            response = query_model(model, prompt)
            results.append({
                "prompt_id": i,
                "model": model,
                "prompt": prompt,
                "response": response,
            })

        model_slug = model.replace("/", "_")
        output_path = Path(output_dir) / f"{benchmark_name}_{model_slug}.json"
        output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"Saved {len(results)} results to {output_path}")
```

## Cost Estimation

Rough per-benchmark cost (assuming ~500 prompts, ~500 tokens avg response):

| Model | Input $/1M tok | Output $/1M tok | Est. cost per benchmark |
|-------|---------------|-----------------|------------------------|
| GPT-4o | ~$2.50 | ~$10.00 | ~$1.50 |
| Claude 3.5 Sonnet | ~$3.00 | ~$15.00 | ~$2.00 |
| Gemini 2.5 Pro | ~$1.25 | ~$10.00 | ~$1.25 |
| Llama 3 70B | ~$0.60 | ~$0.80 | ~$0.20 |
| DeepSeek-R1 | ~$0.55 | ~$2.19 | ~$0.35 |

> Prices are approximate. Check OpenRouter for current rates.

**Estimated total**: 13 benchmarks × 10 models × ~$1 avg ≈ **$130** (rough upper bound)

## Alternatives

- **[LiteLLM](https://github.com/BerriAI/litellm)** — Open-source, self-hosted proxy with OpenAI-compatible API. Good if you want to manage your own keys and avoid a middleman.
- **Direct API calls** — More control, but requires separate SDK/key/billing per provider.
