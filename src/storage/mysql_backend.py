"""基于 aiomysql 的异步 MySQL 存储后端。"""

from datetime import datetime, timezone
import re
from typing import Any

import aiomysql

from models.schemas import Message, Preset, Session, User, UserConfig
from storage.base import StorageBackend


class MySQLBackend(StorageBackend):
    def __init__(self, settings: dict[str, Any], password: str) -> None:
        self.settings = settings
        self.password = password
        self.pool: aiomysql.Pool | None = None

    async def initialize(self) -> None:
        database = str(self.settings.get("database", "langchain_chat"))
        if not re.fullmatch(r"[A-Za-z0-9_]+", database):
            raise ValueError("MySQL database 名称只允许字母、数字和下划线")
        common = dict(
            host=self.settings.get("host", "localhost"),
            port=int(self.settings.get("port", 3306)),
            user=self.settings.get("user", self.settings.get("username", "root")),
            password=self.password,
            charset=self.settings.get("charset", "utf8mb4"),
            autocommit=True,
        )
        bootstrap = await aiomysql.create_pool(**common)
        async with bootstrap.acquire() as connection, connection.cursor() as cursor:
            await cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        bootstrap.close()
        await bootstrap.wait_closed()
        self.pool = await aiomysql.create_pool(db=database, minsize=1, maxsize=10, **common)
        for statement in self._schema():
            await self._execute(statement)

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    @staticmethod
    def _schema() -> list[str]:
        return [
            """CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(191) UNIQUE NOT NULL,default_model VARCHAR(191),default_preset_id BIGINT NULL,
            created_at DATETIME(6) NOT NULL,updated_at DATETIME(6) NOT NULL) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS presets (id BIGINT PRIMARY KEY AUTO_INCREMENT,user_id BIGINT NULL,
            name VARCHAR(191) NOT NULL,description TEXT NOT NULL,system_prompt LONGTEXT NOT NULL,
            is_builtin BOOLEAN NOT NULL DEFAULT FALSE,created_at DATETIME(6) NOT NULL,updated_at DATETIME(6) NOT NULL,
            CONSTRAINT fk_presets_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS sessions (id BIGINT PRIMARY KEY AUTO_INCREMENT,user_id BIGINT NOT NULL,
            title VARCHAR(255) NOT NULL,model_name VARCHAR(191) NOT NULL,preset_id BIGINT NULL,
            total_prompt_tokens BIGINT NOT NULL DEFAULT 0,total_completion_tokens BIGINT NOT NULL DEFAULT 0,
            created_at DATETIME(6) NOT NULL,updated_at DATETIME(6) NOT NULL,INDEX idx_sessions_user(user_id,updated_at),
            CONSTRAINT fk_sessions_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_sessions_preset FOREIGN KEY(preset_id) REFERENCES presets(id) ON DELETE SET NULL) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS messages (id BIGINT PRIMARY KEY AUTO_INCREMENT,session_id BIGINT NOT NULL,
            role ENUM('human','ai','system') NOT NULL,content LONGTEXT NOT NULL,prompt_tokens BIGINT NOT NULL DEFAULT 0,
            completion_tokens BIGINT NOT NULL DEFAULT 0,created_at DATETIME(6) NOT NULL,INDEX idx_messages_session(session_id,id),
            CONSTRAINT fk_messages_session FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS user_configs (id BIGINT PRIMARY KEY AUTO_INCREMENT,user_id BIGINT NOT NULL,
            `key` VARCHAR(191) NOT NULL,value LONGTEXT NOT NULL,updated_at DATETIME(6) NOT NULL,
            UNIQUE KEY uq_user_config(user_id,`key`),CONSTRAINT fk_configs_user FOREIGN KEY(user_id)
            REFERENCES users(id) ON DELETE CASCADE) ENGINE=InnoDB""",
        ]

    def _require_pool(self) -> aiomysql.Pool:
        if self.pool is None:
            raise RuntimeError("MySQL 后端尚未初始化")
        return self.pool

    async def _execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        async with self._require_pool().acquire() as connection, connection.cursor() as cursor:
            await cursor.execute(sql, params)
            return int(cursor.lastrowid or 0)

    async def _one(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        async with self._require_pool().acquire() as connection, connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(sql, params)
            return await cursor.fetchone()

    async def _all(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        async with self._require_pool().acquire() as connection, connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(sql, params)
            return list(await cursor.fetchall())

    async def create_user(self, user: User) -> User:
        user.id = await self._execute(
            "INSERT INTO users(username,default_model,default_preset_id,created_at,updated_at) VALUES(%s,%s,%s,%s,%s)",
            (user.username,user.default_model,user.default_preset_id,user.created_at,user.updated_at),
        )
        return user

    async def get_user_by_name(self, username: str) -> User | None:
        row=await self._one("SELECT * FROM users WHERE username=%s",(username,));return User(**row) if row else None

    async def list_users(self) -> list[User]:
        return [User(**row) for row in await self._all("SELECT * FROM users ORDER BY id")]

    async def update_user(self, user: User) -> None:
        user.updated_at=datetime.now(timezone.utc);await self._execute("UPDATE users SET username=%s,default_model=%s,default_preset_id=%s,updated_at=%s WHERE id=%s",(user.username,user.default_model,user.default_preset_id,user.updated_at,user.id))

    async def delete_user(self, user_id: int) -> None:
        await self._execute("DELETE FROM users WHERE id=%s",(user_id,))

    async def create_session(self, session: Session) -> Session:
        session.id=await self._execute("INSERT INTO sessions(user_id,title,model_name,preset_id,total_prompt_tokens,total_completion_tokens,created_at,updated_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(session.user_id,session.title,session.model_name,session.preset_id,session.total_prompt_tokens,session.total_completion_tokens,session.created_at,session.updated_at));return session

    async def get_session(self, session_id: int) -> Session | None:
        row=await self._one("SELECT * FROM sessions WHERE id=%s",(session_id,));return Session(**row) if row else None

    async def list_sessions(self, user_id: int) -> list[Session]:
        return [Session(**row) for row in await self._all("SELECT * FROM sessions WHERE user_id=%s ORDER BY updated_at DESC,id DESC",(user_id,))]

    async def update_session(self, session: Session) -> None:
        session.updated_at=datetime.now(timezone.utc);await self._execute("UPDATE sessions SET title=%s,model_name=%s,preset_id=%s,total_prompt_tokens=%s,total_completion_tokens=%s,updated_at=%s WHERE id=%s",(session.title,session.model_name,session.preset_id,session.total_prompt_tokens,session.total_completion_tokens,session.updated_at,session.id))

    async def delete_session(self, session_id: int) -> None:
        await self._execute("DELETE FROM sessions WHERE id=%s",(session_id,))

    async def add_message(self, message: Message) -> Message:
        message.id=await self._execute("INSERT INTO messages(session_id,role,content,prompt_tokens,completion_tokens,created_at) VALUES(%s,%s,%s,%s,%s,%s)",(message.session_id,message.role,message.content,message.prompt_tokens,message.completion_tokens,message.created_at));return message

    async def list_messages(self, session_id: int) -> list[Message]:
        return [Message(**row) for row in await self._all("SELECT * FROM messages WHERE session_id=%s ORDER BY id",(session_id,))]

    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        return [Message(**row) for row in await self._all("SELECT m.* FROM messages m JOIN sessions s ON s.id=m.session_id WHERE s.user_id=%s AND m.content LIKE %s ORDER BY m.id",(user_id,f"%{keyword}%"))]

    async def get_preset_by_id(self, preset_id: int) -> Preset | None:
        row=await self._one("SELECT * FROM presets WHERE id=%s",(preset_id,));return Preset(**row) if row else None

    async def save_preset(self, preset: Preset) -> Preset:
        preset.updated_at=datetime.now(timezone.utc)
        if not preset.id:preset.id=await self._execute("INSERT INTO presets(user_id,name,description,system_prompt,is_builtin,created_at,updated_at) VALUES(%s,%s,%s,%s,%s,%s,%s)",(preset.user_id,preset.name,preset.description,preset.system_prompt,preset.is_builtin,preset.created_at,preset.updated_at))
        else:await self._execute("UPDATE presets SET name=%s,description=%s,system_prompt=%s,is_builtin=%s,updated_at=%s WHERE id=%s",(preset.name,preset.description,preset.system_prompt,preset.is_builtin,preset.updated_at,preset.id))
        return preset

    async def list_presets(self, user_id: int) -> list[Preset]:
        return [Preset(**row) for row in await self._all("SELECT * FROM presets WHERE user_id IS NULL OR user_id=%s ORDER BY is_builtin DESC,id",(user_id,))]

    async def delete_preset(self, preset_id: int) -> None:
        await self._execute("DELETE FROM presets WHERE id=%s AND is_builtin=FALSE",(preset_id,))

    async def get_user_config(self, user_id: int, key: str) -> str | None:
        row=await self._one("SELECT value FROM user_configs WHERE user_id=%s AND `key`=%s",(user_id,key));return str(row["value"]) if row else None

    async def set_user_config(self, config: UserConfig) -> None:
        await self._execute("INSERT INTO user_configs(user_id,`key`,value,updated_at) VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE value=VALUES(value),updated_at=VALUES(updated_at)",(config.user_id,config.key,config.value,config.updated_at))
