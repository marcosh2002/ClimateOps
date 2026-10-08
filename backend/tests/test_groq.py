from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core import groq as groq_module
from app.core.groq import GroqClient


@pytest.mark.asyncio
async def test_invoke_model_uses_langchain_async_call(monkeypatch):
    monkeypatch.setattr(groq_module.settings, "GROQ_API_KEY", "test-api-key")
    model = MagicMock()
    model.ainvoke = AsyncMock(return_value=SimpleNamespace(content='{"summary":"clear"}'))
    chat_groq = MagicMock(return_value=model)
    monkeypatch.setattr(groq_module, "ChatGroq", chat_groq)

    client = GroqClient()
    response = await client.invoke_model("explain risk")

    assert response == '{"summary":"clear"}'
    chat_groq.assert_called_once_with(
        model=groq_module.settings.GROQ_MODEL,
        temperature=0.3,
        api_key="test-api-key",
    )
    model.ainvoke.assert_awaited_once_with("explain risk")


@pytest.mark.asyncio
async def test_invoke_model_requires_api_key(monkeypatch):
    monkeypatch.setattr(groq_module.settings, "GROQ_API_KEY", None)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY is not configured"):
        await GroqClient().invoke_model("explain risk")


def test_parse_response_preserves_non_json_output():
    assert GroqClient._parse_response("not json") == {"raw_response": "not json"}
