"""High-level chat workflow service."""

from collections.abc import Generator

from config.settings import DEFAULT_MODEL, MAX_HISTORY_MESSAGES
from database import db
from prompts.preset_prompts import PRESET_PROMPTS
from services.llm_service import LLMDependencyError, MissingAPIKeyError, stream_chat
from services.title_service import generate_fallback_title


class ChatService:
    """Coordinate users, conversations, messages, and LLM calls."""

    def __init__(self) -> None:
        db.init_db()

    def get_user(self, username: str):
        """Return an existing user or create one."""
        return db.get_or_create_user(username)

    def list_conversations(self, username: str):
        """Return conversations visible to a user."""
        user = self.get_user(username)
        return db.list_conversations(user["id"])

    def create_conversation(
        self,
        username: str,
        model_name: str = DEFAULT_MODEL,
        role_name: str = "普通助手",
        title: str = "New conversation",
    ) -> int:
        """Create a conversation for a user."""
        user = self.get_user(username)
        return db.create_conversation(user["id"], title, model_name, role_name)

    def get_conversation(self, username: str, conversation_id: int):
        """Return a user-scoped conversation."""
        user = self.get_user(username)
        return db.get_conversation(conversation_id, user["id"])

    def get_messages(self, conversation_id: int):
        """Return messages for a conversation."""
        return db.list_messages(conversation_id)

    def update_settings(self, conversation_id: int, model_name: str, role_name: str) -> None:
        """Switch model or role without dropping history."""
        db.update_conversation_settings(conversation_id, model_name, role_name)

    def rename_conversation(self, conversation_id: int, title: str) -> None:
        """Rename a conversation."""
        db.rename_conversation(conversation_id, title)

    def send_message_stream(
        self,
        username: str,
        conversation_id: int,
        user_message: str,
    ) -> Generator[str, None, None]:
        """Save a user message, stream the assistant reply, then save the reply."""
        user = self.get_user(username)
        conversation = db.get_conversation(conversation_id, user["id"])
        if conversation is None:
            yield "当前会话不存在，或不属于当前用户。请新建一个会话后再试。"
            return

        cleaned_message = user_message.strip()
        if not cleaned_message:
            return

        db.add_message(conversation_id, "user", cleaned_message)

        if db.count_messages(conversation_id) == 1:
            db.rename_conversation(conversation_id, generate_fallback_title(cleaned_message))

        history_rows = db.list_messages(conversation_id)[-MAX_HISTORY_MESSAGES:]
        history = [{"role": row["role"], "content": row["content"]} for row in history_rows]
        system_prompt = PRESET_PROMPTS.get(conversation["role_name"], PRESET_PROMPTS["普通助手"])

        assistant_reply = ""
        try:
            for chunk in stream_chat(conversation["model_name"], system_prompt, history):
                assistant_reply += chunk
                yield chunk
        except MissingAPIKeyError:
            assistant_reply = (
                "未检测到可用的 API Key。请复制 .env.example 为 .env，"
                "并填写 OPENAI_API_KEY 或对应模型的专用 API Key。"
            )
            yield assistant_reply
        except LLMDependencyError as exc:
            assistant_reply = str(exc)
            yield assistant_reply
        except Exception as exc:
            assistant_reply = f"模型调用失败：{exc}"
            yield assistant_reply

        if assistant_reply:
            db.add_message(conversation_id, "assistant", assistant_reply)
