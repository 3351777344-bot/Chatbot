"""使用原子 JSON 文档持久化的文件存储后端。"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from models.schemas import Entity, Message, Preset, Session, User, UserConfig
from storage.base import StorageBackend

ModelT = TypeVar("ModelT", bound=Entity)


class FileBackend(StorageBackend):
    def __init__(self, directory: str = "data/filestore") -> None:
        self.directory = Path(directory)
        self.path = self.directory / "store.json"
        self._lock = asyncio.Lock()
        self._data: dict[str, list[dict[str, Any]]] = {}

    async def initialize(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        self._data = (
            json.loads(await asyncio.to_thread(self.path.read_text, encoding="utf-8"))
            if self.path.exists()
            else self._empty()
        )
        for key in self._empty():
            self._data.setdefault(key, [])
        await self._flush()

    async def close(self) -> None:
        if self._data:
            await self._flush()

    @staticmethod
    def _empty() -> dict[str, list[dict[str, Any]]]:
        return {"users": [], "sessions": [], "messages": [], "presets": [], "user_configs": []}

    async def _flush(self) -> None:
        text = json.dumps(self._data, ensure_ascii=False, indent=2)
        temporary = self.path.with_suffix(".tmp")
        await asyncio.to_thread(temporary.write_text, text, encoding="utf-8")
        await asyncio.to_thread(temporary.replace, self.path)

    def _next_id(self, table: str) -> int:
        return max((int(row["id"]) for row in self._data[table]), default=0) + 1

    @staticmethod
    def _dump(model: BaseModel) -> dict[str, Any]:
        return model.model_dump(mode="json")

    @staticmethod
    def _find(rows: list[dict[str, Any]], row_id: int) -> dict[str, Any] | None:
        return next((row for row in rows if int(row["id"]) == row_id), None)

    async def _insert(self, table: str, model: ModelT) -> ModelT:
        async with self._lock:
            model.id = self._next_id(table)
            self._data[table].append(self._dump(model))
            await self._flush()
            return model

    async def _replace(self, table: str, model: Entity) -> None:
        async with self._lock:
            row = self._find(self._data[table], model.id)
            if row is None:
                raise ValueError(f"{table} id={model.id} 不存在")
            row.update(self._dump(model))
            await self._flush()

    async def create_user(self, user: User) -> User:
        if await self.get_user_by_name(user.username):
            raise ValueError("用户名已存在")
        return await self._insert("users", user)

    async def get_user_by_name(self, username: str) -> User | None:
        row = next((r for r in self._data["users"] if r["username"] == username), None)
        return User(**row) if row else None

    async def list_users(self) -> list[User]:
        return [User(**r) for r in sorted(self._data["users"], key=lambda x: x["id"])]

    async def update_user(self, user: User) -> None:
        user.updated_at = datetime.now(timezone.utc)
        await self._replace("users", user)

    async def delete_user(self, user_id: int) -> None:
        async with self._lock:
            ids = {r["id"] for r in self._data["sessions"] if r["user_id"] == user_id}
            self._data["messages"] = [
                r for r in self._data["messages"] if r["session_id"] not in ids
            ]
            for table in ("sessions", "presets", "user_configs"):
                self._data[table] = [r for r in self._data[table] if r["user_id"] != user_id]
            self._data["users"] = [r for r in self._data["users"] if r["id"] != user_id]
            await self._flush()

    async def create_session(self, session: Session) -> Session:
        return await self._insert("sessions", session)

    async def get_session(self, session_id: int) -> Session | None:
        row = self._find(self._data["sessions"], session_id)
        return Session(**row) if row else None

    async def list_sessions(self, user_id: int) -> list[Session]:
        rows = (r for r in self._data["sessions"] if r["user_id"] == user_id)
        return [
            Session(**r)
            for r in sorted(rows, key=lambda x: (x["updated_at"], x["id"]), reverse=True)
        ]

    async def update_session(self, session: Session) -> None:
        session.updated_at = datetime.now(timezone.utc)
        await self._replace("sessions", session)

    async def delete_session(self, session_id: int) -> None:
        async with self._lock:
            self._data["messages"] = [
                r for r in self._data["messages"] if r["session_id"] != session_id
            ]
            self._data["sessions"] = [r for r in self._data["sessions"] if r["id"] != session_id]
            await self._flush()

    async def add_message(self, message: Message) -> Message:
        return await self._insert("messages", message)

    async def list_messages(self, session_id: int) -> list[Message]:
        return [
            Message(**r)
            for r in sorted(
                (r for r in self._data["messages"] if r["session_id"] == session_id),
                key=lambda x: x["id"],
            )
        ]

    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        ids = {r["id"] for r in self._data["sessions"] if r["user_id"] == user_id}
        needle = keyword.casefold()
        return [
            Message(**r)
            for r in self._data["messages"]
            if r["session_id"] in ids and needle in r["content"].casefold()
        ]

    async def get_preset_by_id(self, preset_id: int) -> Preset | None:
        row = self._find(self._data["presets"], preset_id)
        return Preset(**row) if row else None

    async def save_preset(self, preset: Preset) -> Preset:
        preset.updated_at = datetime.now(timezone.utc)
        if not preset.id:
            return await self._insert("presets", preset)
        await self._replace("presets", preset)
        return preset

    async def list_presets(self, user_id: int) -> list[Preset]:
        return [
            Preset(**r)
            for r in self._data["presets"]
            if r["user_id"] is None or r["user_id"] == user_id
        ]

    async def delete_preset(self, preset_id: int) -> None:
        async with self._lock:
            self._data["presets"] = [
                r for r in self._data["presets"] if r["id"] != preset_id or r["is_builtin"]
            ]
            await self._flush()

    async def get_user_config(self, user_id: int, key: str) -> str | None:
        row = next(
            (r for r in self._data["user_configs"] if r["user_id"] == user_id and r["key"] == key),
            None,
        )
        return row["value"] if row else None

    async def set_user_config(self, config: UserConfig) -> None:
        async with self._lock:
            row = next(
                (
                    r
                    for r in self._data["user_configs"]
                    if r["user_id"] == config.user_id and r["key"] == config.key
                ),
                None,
            )
            if row:
                config.id = row["id"]
                row.update(self._dump(config))
            else:
                config.id = self._next_id("user_configs")
                self._data["user_configs"].append(self._dump(config))
            await self._flush()
