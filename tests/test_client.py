import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nlquery.client import nlquery


def test_nlquery_returns_clean_sql():
    mock_response = MagicMock()
    mock_response.text = """```sql\nSELECT * FROM users;\n```"""

    model_mock = MagicMock()
    model_mock.generate_content.return_value = mock_response

    genai_stub = MagicMock()
    genai_stub.GenerativeModel.return_value = model_mock

    with patch("nlquery.client._get_genai_module", return_value=genai_stub):
        result = nlquery(
            system_prompt="You are a SQL expert.",
            user_prompt="Get all users.",
            databases=["users(id INT, name TEXT)"],
            model="test-model",
            api_key="fake-key",
            max_output_tokens=256,
        )

    assert result == "SELECT * FROM users;"
    genai_stub.configure.assert_called_once_with(api_key="fake-key")
    genai_stub.GenerativeModel.assert_called_once_with("test-model")
    call_args, call_kwargs = model_mock.generate_content.call_args
    assert call_kwargs["generation_config"]["candidate_count"] == 1
    assert call_kwargs["generation_config"]["max_output_tokens"] == 256

    system_message, user_message = call_args[0]
    assert system_message["role"] == "system"
    assert "users(id INT, name TEXT)" in "\n".join(system_message["parts"])
    assert user_message["parts"] == ["Get all users."]


def test_nlquery_requires_api_key():
    with pytest.raises(RuntimeError):
        nlquery(
            system_prompt="sys",
            user_prompt="user",
            databases=[],
            model="test",
            api_key=None,
        )
