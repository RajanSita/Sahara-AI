"""
llm_client.py — Swappable LLM abstraction for Sahara.ai
Currently backed by Groq API with automatic model fallback.
To swap to another provider, replace the complete() function.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client: Groq | None = None

# Models tried in order — first available wins
# Active models on user's Groq plan
FALLBACK_MODELS = [
    "qwen/qwen3.8-27b",          # Preview — 27B, 450 t/s (Active & verified)
    "openai/gpt-oss-120b",       # Production — 120B (Active & verified)
    "openai/gpt-oss-20b",        # Production — 20B (Active & verified)
    "llama-3.1-8b-instant",      # Production
    "llama-3.3-70b-versatile",   # Production
]

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
    model: str = "qwen/qwen3.8-27b",
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Call the LLM and return the text response.
    Automatically falls back through FALLBACK_MODELS if the requested model
    returns a 404 (model_not_found).
    """
    client = _get_client()

    # Build the ordered list of models to try (requested first, then fallbacks)
    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]

    last_error = None
    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if m != model:
                print(f"[LLM] Used fallback model: {m} (requested: {model})")
            return response.choices[0].message.content.strip()
        except Exception as e:
            err_str = str(e)
            # Fall through on model unavailability errors (not found, decommissioned, deprecated)
            if any(k in err_str for k in [
                "model_not_found", "model_decommissioned", "model_not_active",
                "404", "400", "does not exist", "no longer supported",
                "decommissioned", "deprecated", "not supported",
            ]):
                print(f"[LLM] Model '{m}' unavailable ({err_str[:80]}), trying next...")
                last_error = e
                continue
            # For auth, rate-limit, network errors — raise immediately
            raise

    raise RuntimeError(
        f"No working Groq model found. Tried: {models_to_try}\n"
        f"Last error: {last_error}\n"
        "Please check your Groq API key at https://console.groq.com"
    )
