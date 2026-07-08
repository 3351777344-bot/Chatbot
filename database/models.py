"""Lightweight data models used by the chat application."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    created_at: datetime


@dataclass
class Conversation:
    id: int
    user_id: int
    title: str
    model_name: str
    role_name: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Message:
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
