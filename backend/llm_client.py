"""
llm_client.py — Swappable LLM abstraction for Sahara.ai
Currently backed by Groq API (llama-3.3-70b-versatile).
To swap to another provider, replace the _call_groq function.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError(
                "GROQ_API_KEY not set. Please add your Groq API key to backend/.env\n"
                "Get a free key at: https://console.groq.com"
            )
        _client = Groq(api_key=api_key)
    return _client


def complete(
    system_prompt: str,
    user_prompt: str,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Call the LLM and return the text response.
    Raises on API errors.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
