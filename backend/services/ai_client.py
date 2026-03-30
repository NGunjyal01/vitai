"""
AI client module — Groq (primary) with Gemini (optional, if billing enabled).
"""

import json
import logging
from typing import AsyncGenerator

import httpx

from config import GEMINI_API_KEY, GROQ_API_KEY

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini client (optional — only if API key is set and billing enabled)
# ---------------------------------------------------------------------------
gemini_client = None
GEMINI_MODEL = "gemini-2.0-flash"

if GEMINI_API_KEY:
    try:
        from google import genai
        from google.genai import types as genai_types
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        logger.info("Gemini SDK not available, using Groq only.")

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# ---------------------------------------------------------------------------
# Groq (primary)
# ---------------------------------------------------------------------------
async def _groq_generate(
    prompt: str,
    system: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Generate a completion using the Groq API."""
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload: dict = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    import asyncio as _aio
    for attempt in range(3):
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(GROQ_API_URL, json=payload, headers=headers)
            if response.status_code == 429 and attempt < 2:
                wait = (attempt + 1) * 5  # 5s, 10s
                logger.warning("Groq 429, retrying in %ds (attempt %d/3)", wait, attempt + 1)
                await _aio.sleep(wait)
                continue
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


async def _groq_generate_stream(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """Stream a completion from the Groq API."""
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload: dict = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", GROQ_API_URL, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except Exception:
                        continue
    except httpx.HTTPStatusError as e:
        logger.warning("Groq streaming failed (%s)", e)
        yield "I'm currently experiencing high demand. Please try again in a moment."


# ---------------------------------------------------------------------------
# Gemini generation (only if client is available)
# ---------------------------------------------------------------------------
def _gemini_generate(
    prompt: str,
    system: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    search_grounding: bool = False,
) -> str | None:
    """Try Gemini, return None on failure."""
    if not gemini_client:
        return None
    try:
        config = genai_types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if system:
            config.system_instruction = system
        if json_mode:
            config.response_mime_type = "application/json"
        if search_grounding:
            config.tools = [genai_types.Tool(google_search=genai_types.GoogleSearch())]

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as exc:
        logger.warning("Gemini failed (%s), falling back to Groq.", exc)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def ai_generate(
    prompt: str,
    system: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    search_grounding: bool = False,
) -> str:
    """
    Generate a completion. Tries Gemini first (if available), falls back to Groq.
    """
    # Try Gemini if available
    if gemini_client and not search_grounding:
        result = _gemini_generate(prompt, system, json_mode, max_tokens, temperature, search_grounding)
        if result:
            return result

    # Primary: Groq
    return await _groq_generate(
        prompt=prompt,
        system=system,
        json_mode=json_mode,
        max_tokens=max_tokens,
        temperature=temperature,
    )


async def ai_generate_stream(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """
    Stream a completion. Tries Gemini first (if available), falls back to Groq.
    """
    # Try Gemini streaming if available
    if gemini_client:
        try:
            config = genai_types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            if system:
                config.system_instruction = system

            stream = gemini_client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as exc:
            logger.warning("Gemini streaming failed (%s), falling back to Groq.", exc)

    # Primary: Groq streaming
    async for text in _groq_generate_stream(
        prompt=prompt,
        system=system,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        yield text