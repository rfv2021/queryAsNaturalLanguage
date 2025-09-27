"""Command line interface for querying databases with natural language."""

from __future__ import annotations

import argparse
import json
from typing import Optional

from query_processor import QueryProcessor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Turn natural language instructions into SQL and run them",
    )
    parser.add_argument("instruction", help="Instruction describing the desired data")
    parser.add_argument(
        "--db-id",
        default="PREWAVE_PROD",
        help="Identifier used to look up the database URL from the environment",
    )
    parser.add_argument(
        "--schema-hint",
        help="Optional schema description to guide the LLM",
    )
    parser.add_argument(
        "--model-name",
        default="gemini-pro",
        help="Name of the Gemini model to use",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    processor = QueryProcessor(db_id=args.db_id, model_name=args.model_name)
    result = processor.run(args.instruction, schema_hint=args.schema_hint)

    if args.json:
        print(json.dumps({"sql": result.sql, "data": [list(row) for row in result.data]}))
    else:
        print("SQL:\n" + result.sql)
        print("\nResult:")
        for row in result.data:
            print(row)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
