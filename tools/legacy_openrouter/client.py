"""OpenRouter API client for CEI benchmark evaluation."""

from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


def query(model: str, prompt: str, temperature: float = 0.0, max_tokens: int = 2048) -> dict:
    """Send a prompt to a model via OpenRouter and return the response."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "model": model,
        "temperature": temperature,
        "content": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    }


def query_multiturn(model: str, messages: list[dict], temperature: float = 0.0, max_tokens: int = 2048) -> dict:
    """Send a multi-turn conversation to a model via OpenRouter."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "model": model,
        "temperature": temperature,
        "content": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    }


def query_with_system(model: str, system: str, prompt: str, temperature: float = 0.0, max_tokens: int = 2048) -> dict:
    """Send a system + user message to a model via OpenRouter."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "model": model,
        "temperature": temperature,
        "system": system,
        "content": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    }
