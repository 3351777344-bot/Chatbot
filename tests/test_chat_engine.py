import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from core.chat_engine import ChatEngine
from core.config_manager import get_config


class FakeLLM:
    def invoke(self, messages):
        return AIMessage(content="complete", usage_metadata={"input_tokens": 2, "output_tokens": 3, "total_tokens": 5})

    async def astream(self, messages):
        yield AIMessageChunk(content="stream ")
        yield AIMessageChunk(content="reply", usage_metadata={"input_tokens": 4, "output_tokens": 2, "total_tokens": 6})


@pytest.mark.asyncio
async def test_sync_and_stream_usage_without_network():
    engine = ChatEngine(get_config(), llm=FakeLLM())
    text, usage = engine.chat([HumanMessage(content="hello")])
    assert text == "complete" and usage["total_tokens"] == 5
    chunks = [item async for item in engine.astream([HumanMessage(content="hello")])]
    assert "".join(text for text, _ in chunks) == "stream reply"
    assert chunks[-1][1]["total_tokens"] == 6
