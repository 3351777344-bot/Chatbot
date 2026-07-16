"""LangChain LLM client creation and streaming helpers."""

from collections.abc import Iterable
from typing import Any

from config.settings import CHAT_TEMPERATURE, MODEL_CONFIGS


class MissingAPIKeyError(RuntimeError):
    """Raised when the user tries to call an LLM without configuring an API key."""


class LLMDependencyError(RuntimeError):
    """Raised when LangChain dependencies are not installed."""


def ensure_api_key(api_key: str) -> None:
    """Validate that an API key is available before calling the model."""
    if not api_key or api_key == "your_api_key_here":
        raise MissingAPIKeyError("No API key found. Please set OPENAI_API_KEY in your .env file.")


def get_chat_model(model_name: str):
    """Return a LangChain chat model instance.

    All configured providers are treated as OpenAI-compatible chat APIs.
    """
    config = MODEL_CONFIGS.get(model_name)
    if config is None:
        raise ValueError(f"Unknown model: {model_name}")

    api_key = config.get("api_key", "")
    ensure_api_key(api_key)

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise LLMDependencyError(
            "LangChain dependencies are missing. Please run: pip install -r requirements.txt"
        ) from exc

    return ChatOpenAI(
        model=config["model_name"],
        api_key=api_key,
        base_url=config["base_url"],
        temperature=CHAT_TEMPERATURE,
        streaming=True,
    )


def to_langchain_messages(system_prompt: str, history: list[dict[str, str]]) -> list[Any]:
    """Convert stored chat history to LangChain message objects."""
    try:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    except ImportError as exc:
        raise LLMDependencyError(
            "LangChain dependencies are missing. Please run: pip install -r requirements.txt"
        ) from exc

    messages: list[Any] = [SystemMessage(content=system_prompt)]
    for item in history:
        role = item["role"]
        content = item["content"]
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def _chunk_to_text(chunk: Any) -> str:
    """Extract plain text from different LangChain chunk shapes."""
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content) if content else ""


def stream_chat(
    model_name: str, system_prompt: str, history: list[dict[str, str]]
) -> Iterable[str]:
    """Yield assistant response chunks for a conversation."""
    model = get_chat_model(model_name)
    messages = to_langchain_messages(system_prompt, history)
    for chunk in model.stream(messages):
        text = _chunk_to_text(chunk)
        if text:
            yield text
