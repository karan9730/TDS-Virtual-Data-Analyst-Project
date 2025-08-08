# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "httpx",
# ]
# ///

import os
import httpx # type: ignore

def generate_planner_response(messages: list[dict]) -> str:
    response = httpx.post(
        "https://aipipe.org/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": messages,
        },
        timeout=60.0,
    )

    try:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception:
        return f"Planner Error: {response.text}"