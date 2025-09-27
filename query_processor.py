"""Utilities for translating natural language instructions into SQL and running them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from agents.google_sql_agent import GoogleSQLAgent
from db_connector import DBConnector


@dataclass
class QueryResult:
    """Represents the outcome of a database query."""

    sql: str
    data: Any


class QueryProcessor:
    """High level helper that turns natural language queries into SQL."""

    def __init__(self, db_id: str, *, model_name: str = "gemini-pro") -> None:
        self.db_id = db_id
        self.agent = GoogleSQLAgent(model_name=model_name)
        self.connector = DBConnector(db_id=db_id)

    def run(self, instruction: str, *, schema_hint: Optional[str] = None) -> QueryResult:
        """Create a SQL statement for ``instruction`` and execute it.

        Args:
            instruction: The natural language instruction provided by the user.
            schema_hint: Optional free form text that describes relevant tables
                and columns. Passing this increases the chances of the LLM
                emitting a valid query for your schema.

        Returns:
            ``QueryResult`` with the executed SQL statement and the returned
            data.
        """

        sql = self.agent.generate_sql(instruction, schema_hint=schema_hint)
        data = self.connector.sql_query(sql)
        return QueryResult(sql=sql, data=data)


__all__ = ["QueryProcessor", "QueryResult"]
