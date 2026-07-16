"""会话、历史消息、Token 累计与标题管理。"""

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.chat_engine import ChatEngine

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
        return await self.backend.create_session(
            Session(user_id=user_id, title=title, model_name=model_name, preset_id=preset_id)
        )

    async def add_message(
        self,
        session: Session,
        role: str,
        content: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> Message:
        message = await self.backend.add_message(
            Message(
                session_id=session.id,
                role=role,
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
        )
        session.total_prompt_tokens += prompt_tokens
        session.total_completion_tokens += completion_tokens
        await self.backend.update_session(session)
        return message

    async def load_messages_as_langchain(self, session_id: int) -> list[BaseMessage]:
        return [
            self._to_langchain(message) for message in await self.backend.list_messages(session_id)
        ]

    async def has_messages(self, session_id: int) -> bool:
        return bool(await self.backend.list_messages(session_id))

    async def get_session_messages(self, session_id: int) -> list[Message]:
        return await self.backend.list_messages(session_id)

    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        keyword = keyword.strip()
        return await self.backend.search_messages(user_id, keyword) if keyword else []

    async def generate_title(self, first_user_input: str, engine: "ChatEngine") -> str:
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

    async def list_sessions(self, user_id: int) -> list[Session]:
        return await self.backend.list_sessions(user_id)

    async def get_session(self, session_id: int, user_id: int | None = None) -> Session | None:
        session = await self.backend.get_session(session_id)
        if session is not None and user_id is not None and session.user_id != user_id:
            return None
        return session

    async def rename_session(
        self, session_id: int, new_title: str, user_id: int | None = None
    ) -> None:
        session = await self.get_session(session_id, user_id)
        if session is None:
            raise ValueError("会话不存在或无权访问")
        await self.update_title(session, new_title)

    async def delete_session(self, session_id: int, user_id: int | None = None) -> None:
        session = await self.get_session(session_id, user_id)
        if session is None:
            raise ValueError("会话不存在或无权访问")
        await self.backend.delete_session(session_id)

    async def switch_model(self, session: Session, model_name: str, available: set[str]) -> None:
        if model_name not in available:
            raise ValueError(f"模型不可用: {model_name}")
        session.model_name = model_name
        await self.backend.update_session(session)

    async def export_markdown(
        self, session_id: int, username: str, user_id: int | None = None
    ) -> Path:
        session = await self.get_session(session_id, user_id)
        if session is None:
            raise ValueError("会话不存在或无权访问")
        messages = await self.get_session_messages(session_id)
        safe_title = (
            re.sub(r'[<>:"/\\|?*]+', "_", session.title).strip(" .") or f"session-{session.id}"
        )
        export_dir = str(self.config.get("export", "dir", default="data/exports"))
        export_dir = export_dir.format(username=username)
        path = Path(export_dir) / f"{safe_title}_{session.id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {session.title}",
            "",
            f"- 用户：{username}",
            f"- 模型：{session.model_name}",
            f"- Prompt Token：{session.total_prompt_tokens}",
            f"- Completion Token：{session.total_completion_tokens}",
            "",
        ]
        labels = {"human": "用户", "ai": "助手", "system": "系统"}
        for message in messages:
            lines.extend([f"## {labels[message.role]}", "", message.content, ""])
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def _to_langchain(message: Message) -> BaseMessage:
        if message.role == "human":
            return HumanMessage(content=message.content)
        if message.role == "ai":
            return AIMessage(content=message.content)
        return SystemMessage(content=message.content)
