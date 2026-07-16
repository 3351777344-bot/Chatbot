"""项目各层共享的 Pydantic 数据模型。"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Entity(BaseModel):
    id: int = 0


def utc_now() -> datetime:
    """返回带时区的 UTC 时间。"""
    return datetime.now(timezone.utc)


class User(Entity):
    username: str
    default_model: str | None = None
    default_preset_id: int | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Session(Entity):
    user_id: int
    title: str
    model_name: str
    preset_id: int | None = None
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


MessageRole = Literal["human", "ai", "system"]


class Message(Entity):
    session_id: int
    role: MessageRole
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class Preset(Entity):
    user_id: int | None = None
    name: str
    description: str = ""
    system_prompt: str
    is_builtin: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class UserConfig(Entity):
    user_id: int
    key: str
    value: str
    updated_at: datetime = Field(default_factory=utc_now)
