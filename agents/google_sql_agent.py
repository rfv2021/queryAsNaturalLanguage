"""LLM backed helper that converts natural language to SQL."""

from __future__ import annotations

import os
from typing import Optional

try:
    import google.generativeai as genai
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError(
        "google-generativeai is required for GoogleSQLAgent. Install it with "
        "`pip install google-generativeai`."
    ) from exc

SYSTEM_PROMPT = """You are a senior data engineer. Translate instructions into SQL queries.\n"
SYSTEM_PROMPT += (
    "Follow these rules strictly:\n"
    "- Never fabricate tables or columns.\n"
    "- Only respond with a SQL query that can be executed on a PostgreSQL database.\n"
    "- Do not include markdown fences or commentary, only the SQL query.\n"
)


class GoogleSQLAgent:
    """Generate SQL using Gemini (Google Generative AI)."""

    def __init__(self, *, model_name: str = "gemini-pro", temperature: float = 0.0) -> None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY must be defined in the environment to use GoogleSQLAgent."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature

    def generate_sql(self, instruction: str, *, schema_hint: Optional[str] = None) -> str:
        """Return SQL for the provided ``instruction``."""

        user_prompt = instruction.strip()
        if schema_hint:
            user_prompt += f"\n\nSchema information:\n{schema_hint.strip()}"

        response = self.model.generate_content(
            [
                SYSTEM_PROMPT,
                user_prompt,
            ],
            generation_config={"temperature": self.temperature},
        )

        if not response or not response.candidates:
            raise RuntimeError("The LLM did not return a candidate response.")

        candidate = response.candidates[0]
        if not candidate.content.parts:
            raise RuntimeError("The LLM response did not contain any content parts.")

        sql = "".join(part.text for part in candidate.content.parts if getattr(part, "text", ""))
        sql = sql.strip()
        if not sql:
            raise RuntimeError("Failed to extract SQL from the LLM response.")
        return sql


__all__ = ["GoogleSQLAgent"]
