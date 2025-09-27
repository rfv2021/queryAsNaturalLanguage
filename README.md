# Query as Natural Language

Minimal agentic application that turns natural language instructions into SQL
queries using Google's Gemini models and executes them against configured
PostgreSQL databases.

## Quick start

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Provide configuration via environment variables:

   * `GOOGLE_API_KEY` – API key for Google Generative AI.
   * `DB_URL_<DB_ID>` – SQLAlchemy compatible database URL (for example,
     `DB_URL_PREWAVE_PROD=postgresql+psycopg://user:pass@host/db`).

3. Run a query from the command line:

   ```bash
   python app.py "List all active event types" --db-id PREWAVE_PROD
   ```

   Optionally pass `--schema-hint` with table and column descriptions to
   improve SQL generation.

## Integrating in Python

```python
from query_processor import QueryProcessor

processor = QueryProcessor(db_id="PREWAVE_PROD")
result = processor.run("Show all active event types")
print(result.sql)
print(result.data)
```

This example mirrors the existing manual SQL execution flow and extends it
with a Gemini-backed agent that produces the SQL automatically.
