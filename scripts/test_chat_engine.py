"""不访问网络的 ChatEngine 冒烟测试；真实服务由用户按需验证。"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from core.chat_engine import ChatEngine
from core.config_manager import get_config


class FakeLLM:
    def invoke(self, messages):
        return AIMessage(content="pong", usage_metadata={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2})

    async def astream(self, messages):
        yield AIMessageChunk(content="po")
        yield AIMessageChunk(content="ng", usage_metadata={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2})


async def main() -> None:
    engine = ChatEngine(get_config(), llm=FakeLLM())
    messages = [HumanMessage(content="ping")]
    text, usage = engine.chat(messages)
    assert text == "pong" and usage["total_tokens"] == 2
    chunks = [item async for item in engine.astream(messages)]
    assert "".join(text for text, _ in chunks) == "pong"
    assert chunks[-1][1]["total_tokens"] == 2
    print("ChatEngine 冒烟测试通过")


if __name__ == "__main__":
    asyncio.run(main())
