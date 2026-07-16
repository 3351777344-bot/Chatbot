"""无会话状态的 LangChain 对话引擎。"""

from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from core.config_manager import AppConfig


class ChatEngine:
    """封装同步/异步流式调用、重试配置与 Token 统计。"""

    def __init__(
        self, config: AppConfig, llm: Any | None = None, model_name: str | None = None
    ) -> None:
        self.config = config
        self.model_name = model_name or config.secret.MODEL_NAME or config.default_model
        self.llm = llm or ChatOpenAI(
            model=self.model_name,
            api_key=config.secret.API_KEY,
            base_url=config.secret.API_BASE_URL,
            temperature=config.temperature,
            max_tokens=config.max_tokens,  # type: ignore[call-arg]
            timeout=config.llm_timeout,
            max_retries=config.llm_max_retries,
            streaming=True,
            stream_usage=True,
        )

    def chat(self, messages: list[BaseMessage]) -> tuple[str, dict[str, int]]:
        response: AIMessage = self.llm.invoke(messages)
        return self._text(response.content), self._extract_usage(response) or self._empty_usage()

    async def astream(
        self, messages: list[BaseMessage]
    ) -> AsyncIterator[tuple[str, dict[str, int] | None]]:
        final_usage: dict[str, int] | None = None
        async for chunk in self.llm.astream(messages):
            text = self._text(chunk.content)
            if text:
                yield text, None
            usage = self._extract_usage(chunk)
            if usage is not None:
                final_usage = usage
        yield "", final_usage or self._empty_usage()

    @staticmethod
    def _text(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                str(item.get("text", "")) if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content or "")

    @staticmethod
    def _empty_usage() -> dict[str, int]:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    @classmethod
    def _extract_usage(cls, message: BaseMessage) -> dict[str, int] | None:
        usage = getattr(message, "usage_metadata", None)
        if not usage:
            response_usage = getattr(message, "response_metadata", {}).get("token_usage")
            usage = response_usage
        if not usage:
            return None
        prompt = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)))
        completion = int(usage.get("output_tokens", usage.get("completion_tokens", 0)))
        return {
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": int(usage.get("total_tokens", prompt + completion)),
        }

    async def close(self) -> None:
        close = getattr(self.llm, "aclose", None)
        if close is not None:
            await close()

    def for_model(self, model_name: str) -> "ChatEngine":
        return ChatEngine(self.config, model_name=model_name)
