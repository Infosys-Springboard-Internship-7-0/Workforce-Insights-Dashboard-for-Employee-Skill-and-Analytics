"""Groq LLM client (chat completions)."""

from functools import lru_cache

from app.core.config import get_settings


class LLMNotConfiguredError(Exception):
    pass


@lru_cache
def _get_client():
    from groq import Groq

    settings = get_settings()
    if not settings.groq_api_key:
        raise LLMNotConfiguredError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys and add it to your .env file."
        )
    return Groq(api_key=settings.groq_api_key)


def chat_completion(system_prompt: str, user_message: str, temperature: float = 0.2) -> str:
    """Single-turn chat completion against the configured Groq model."""
    settings = get_settings()
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.groq_model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content
