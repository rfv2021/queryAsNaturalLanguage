"""Interface for translating natural language instructions into SQL queries."""
from __future__ import annotations

import os
import re
from typing import Iterable, List, Optional, Sequence

_DEFAULT_MODEL = "models/gemini-1.5-pro-latest"


def _format_database_context(databases: Iterable[str]) -> str:
    """Return a human readable block describing the accessible databases."""
    formatted: List[str] = []
    for index, db in enumerate(databases, start=1):
        formatted.append(f"{index}. {db.strip()}")
    if not formatted:
        return "No database schemas were provided."
    return "\n".join(formatted)


def _extract_sql_from_text(text: str) -> str:
    """Extract the SQL query from a model response."""
    text = text.strip()
    if not text:
        return text

    fenced_match = re.search(r"```sql\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    generic_fence = re.search(r"```\s*(.*?)\s*```", text, flags=re.DOTALL)
    if generic_fence:
        return generic_fence.group(1).strip()

    return text


def _get_genai_module():  # pragma: no cover - import guard
    try:
        import google.generativeai as genai  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise ModuleNotFoundError(
            "The 'google-generativeai' package is required to use the nlquery module. "
            "Install it with `pip install google-generativeai`."
        ) from exc
    return genai


def nlquery(
    system_prompt: str,
    user_prompt: str,
    databases: Sequence[str],
    *,
    model: str = _DEFAULT_MODEL,
    api_key: Optional[str] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """Return a SQL query that satisfies the ``user_prompt`` against ``databases``.

    Parameters
    ----------
    system_prompt:
        Instructions that describe the assistant's behaviour, typically focusing on
        how it should work with databases and SQL.
    user_prompt:
        A natural language question or request from the end user.
    databases:
        A collection of strings describing the available database schemas or tables.
    model:
        The Gemini model identifier to use when generating the SQL query.
    api_key:
        The Google Generative AI API key. If not provided, the function falls back
        to the ``GOOGLE_API_KEY`` environment variable.
    max_output_tokens:
        Optional limit on the number of tokens to generate.

    Returns
    -------
    str
        The SQL query extracted from the model's response.

    Raises
    ------
    RuntimeError
        If no API key is provided.
    RuntimeError
        If the model fails to return a textual response.
    """

    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "An API key must be supplied either through the `api_key` argument or "
            "the GOOGLE_API_KEY environment variable."
        )

    genai = _get_genai_module()
    genai.configure(api_key=api_key)

    database_context = _format_database_context(databases)

    messages = [
        {
            "role": "system",
            "parts": [
                system_prompt.strip(),
                "You must answer with a single executable SQL query.",
                "The available databases are:\n" + database_context,
            ],
        },
        {
            "role": "user",
            "parts": [user_prompt.strip()],
        },
    ]

    model_client = genai.GenerativeModel(model)
    response = model_client.generate_content(
        messages,
        generation_config={
            "candidate_count": 1,
            **({"max_output_tokens": max_output_tokens} if max_output_tokens else {}),
        },
    )

    text_response = getattr(response, "text", None)
    if not text_response:
        raise RuntimeError("The model did not return a textual response.")

    return _extract_sql_from_text(text_response)


__all__ = ["nlquery"]
