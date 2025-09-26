# Query as Natural Language

This package exposes a single helper function, `nlquery`, that translates natural
language questions into SQL queries with the help of a Gemini model.

## Usage

```python
from nlquery import nlquery

query = nlquery(
    system_prompt="You are a helpful assistant that only outputs SQL queries.",
    user_prompt="List the total number of orders per customer from the sales database.",
    databases=[
        "sales.customers(id INT, name TEXT)",
        "sales.orders(id INT, customer_id INT, total NUMERIC)",
    ],
    api_key="your-google-api-key",
)

print(query)
```

The function requires the `google-generativeai` package and an API key. You can
set the `GOOGLE_API_KEY` environment variable instead of passing `api_key`
explicitly.

## Development

Install the optional development dependencies and run the test suite:

```bash
pip install -e .[dev]
pytest
```
