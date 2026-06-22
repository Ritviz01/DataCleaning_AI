"""Optional, opt-in OpenAI reasoning for an already-profiled dataset."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


def generate_openai_insights(analysis: dict[str, Any]) -> str:
    """Explain findings without sending raw dataset values to the model."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    safe_context = {
        "metadata": analysis["metadata"],
        "schema": analysis["schema"],
        "profile": analysis["profile"],
        "quality": analysis["quality"],
        "issues": analysis["issues"],
        "recommendations": analysis["recommendations"],
    }
    instructions = (
        "You are a careful data-quality analyst. Explain the supplied aggregate "
        "dataset report in concise plain language. Prioritize risks, explain why "
        "each recommended cleanup is appropriate, and identify actions requiring "
        "human review. Do not invent facts, claim that data was changed, or give "
        "instructions to expose personal data."
    )
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=instructions,
        input=json.dumps(safe_context, default=str),
    )
    return response.output_text
