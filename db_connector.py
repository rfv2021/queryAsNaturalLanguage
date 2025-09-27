"""Minimal database connector used by the agentic application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@dataclass
class DBConnector:
    """Execute SQL statements against a configured database."""

    db_id: str

    def __post_init__(self) -> None:
        url_env = f"DB_URL_{self.db_id}"
        database_url = os.environ.get(url_env)
        if not database_url:
            raise RuntimeError(
                f"Environment variable {url_env} must be set to use DBConnector."
            )

        self.engine: Engine = create_engine(database_url)

    def sql_query(self, query: str) -> Any:
        """Execute ``query`` and return the fetched rows."""

        with self.engine.connect() as connection:
            result = connection.execute(text(query))
            return result.fetchall()


__all__ = ["DBConnector"]
