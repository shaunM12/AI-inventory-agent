from typing import Any

import httpx

from agent import config
from agent.tools import TOOL_DEFINITIONS


def call_llm(messages: list[dict[str, Any]]) -> dict[str, Any]:
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": messages,
        "tools": TOOL_DEFINITIONS,
        "tool_choice": "auto",
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{config.OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
    if response.status_code >= 400:
        raise RuntimeError(
            f"LLM request failed ({response.status_code}): {response.text}"
        )
    return response.json()


def extract_assistant_message(completion: dict[str, Any]) -> dict[str, Any]:
    return completion["choices"][0]["message"]
