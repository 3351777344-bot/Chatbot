"""会话、历史消息、Token 累计与标题管理。"""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from core.config_manager import AppConfig
from models.schemas import Message, Session
from storage.base import StorageBackend


class SessionManager:
    def __init__(self, backend: StorageBackend, config: AppConfig) -> None:
        self.backend = backend
        self.config = config

    async def create_session(
        self,
        user_id: int,
        model_name: str,
        preset_id: int | None = None,
        title: str = "新会话",
    ) -> Session:
        return await self.backend.create_session(Session(
            user_id=user_id, title=title, model_name=model_name, preset_id=preset_id
        ))

    async def add_message(
        self,
        session: Session,
        role: str,
        content: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> Message:
        message = await self.backend.add_message(Message(
            session_id=session.id,
            role=role,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        ))
        session.total_prompt_tokens += prompt_tokens
        session.total_completion_tokens += completion_tokens
        await self.backend.update_session(session)
        return message

    async def load_messages_as_langchain(self, session_id: int) -> list[BaseMessage]:
        return [self._to_langchain(message) for message in await self.backend.list_messages(session_id)]

    async def generate_title(self, first_user_input: str, engine) -> str:
        prompt = [
            SystemMessage(content="请用简短中文概括用户意图作为对话标题，只输出标题。"),
            HumanMessage(content=first_user_input),
        ]
        try:
            title, _ = engine.chat(prompt)
            title = title.strip().strip("\"'「」“”")
            return title[: self.config.title_max_length] or self._fallback_title(first_user_input)
        except Exception:
            return self._fallback_title(first_user_input)

    async def update_title(self, session: Session, new_title: str) -> None:
        title = new_title.strip()
        if not title:
            raise ValueError("标题不能为空")
        session.title = title[: self.config.title_max_length]
        await self.backend.update_session(session)

    def _fallback_title(self, text: str) -> str:
        limit = self.config.title_max_length
        return text[:limit] + ("..." if len(text) > limit else "")

    @staticmethod
    def _to_langchain(message: Message) -> BaseMessage:
        if message.role == "human":
            return HumanMessage(content=message.content)
        if message.role == "ai":
            return AIMessage(content=message.content)
        return SystemMessage(content=message.content)
