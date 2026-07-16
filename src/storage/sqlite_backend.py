"""基于 aiosqlite 的默认异步存储后端。"""

from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from models.schemas import Message, Preset, Session, User, UserConfig
from storage.base import StorageBackend


class SQLiteBackend(StorageBackend):
    def __init__(self, db_path: str = "data/sqlite/app.db") -> None:
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("存储后端尚未初始化")
        return self._conn

    async def initialize(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self._conn.executescript(self._schema())
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @staticmethod
    def _schema() -> str:
        return """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            default_model TEXT,
            default_preset_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            system_prompt TEXT NOT NULL,
            is_builtin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            model_name TEXT NOT NULL,
            preset_id INTEGER,
            total_prompt_tokens INTEGER NOT NULL DEFAULT 0,
            total_completion_tokens INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(preset_id) REFERENCES presets(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('human','ai','system')),
            content TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL DEFAULT 0,
            completion_tokens INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS user_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, key),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id);
        """

    async def create_user(self, user: User) -> User:
        cursor = await self.conn.execute(
            "INSERT INTO users(username,default_model,default_preset_id,created_at,updated_at) VALUES(?,?,?,?,?)",
            (
                user.username,
                user.default_model,
                user.default_preset_id,
                user.created_at.isoformat(),
                user.updated_at.isoformat(),
            ),
        )
        await self.conn.commit()
        user.id = int(cursor.lastrowid or 0)
        return user

    async def get_user_by_name(self, username: str) -> User | None:
        row = await self._one("SELECT * FROM users WHERE username=?", (username,))
        return self._user(row) if row else None

    async def list_users(self) -> list[User]:
        return [self._user(row) for row in await self._all("SELECT * FROM users ORDER BY id")]

    async def update_user(self, user: User) -> None:
        user.updated_at = datetime.now(timezone.utc)
        await self.conn.execute(
            "UPDATE users SET username=?,default_model=?,default_preset_id=?,updated_at=? WHERE id=?",
            (
                user.username,
                user.default_model,
                user.default_preset_id,
                user.updated_at.isoformat(),
                user.id,
            ),
        )
        await self.conn.commit()

    async def delete_user(self, user_id: int) -> None:
        await self.conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        await self.conn.commit()

    async def create_session(self, session: Session) -> Session:
        cursor = await self.conn.execute(
            """INSERT INTO sessions(user_id,title,model_name,preset_id,total_prompt_tokens,
            total_completion_tokens,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)""",
            (
                session.user_id,
                session.title,
                session.model_name,
                session.preset_id,
                session.total_prompt_tokens,
                session.total_completion_tokens,
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
            ),
        )
        await self.conn.commit()
        session.id = int(cursor.lastrowid or 0)
        return session

    async def get_session(self, session_id: int) -> Session | None:
        row = await self._one("SELECT * FROM sessions WHERE id=?", (session_id,))
        return self._session(row) if row else None

    async def list_sessions(self, user_id: int) -> list[Session]:
        rows = await self._all(
            "SELECT * FROM sessions WHERE user_id=? ORDER BY updated_at DESC,id DESC", (user_id,)
        )
        return [self._session(row) for row in rows]

    async def update_session(self, session: Session) -> None:
        session.updated_at = datetime.now(timezone.utc)
        await self.conn.execute(
            """UPDATE sessions SET title=?,model_name=?,preset_id=?,total_prompt_tokens=?,
            total_completion_tokens=?,updated_at=? WHERE id=?""",
            (
                session.title,
                session.model_name,
                session.preset_id,
                session.total_prompt_tokens,
                session.total_completion_tokens,
                session.updated_at.isoformat(),
                session.id,
            ),
        )
        await self.conn.commit()

    async def delete_session(self, session_id: int) -> None:
        await self.conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        await self.conn.commit()

    async def add_message(self, message: Message) -> Message:
        cursor = await self.conn.execute(
            """INSERT INTO messages(session_id,role,content,prompt_tokens,completion_tokens,created_at)
            VALUES(?,?,?,?,?,?)""",
            (
                message.session_id,
                message.role,
                message.content,
                message.prompt_tokens,
                message.completion_tokens,
                message.created_at.isoformat(),
            ),
        )
        await self.conn.commit()
        message.id = int(cursor.lastrowid or 0)
        return message

    async def list_messages(self, session_id: int) -> list[Message]:
        return [
            self._message(row)
            for row in await self._all(
                "SELECT * FROM messages WHERE session_id=? ORDER BY id", (session_id,)
            )
        ]

    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        rows = await self._all(
            """SELECT m.* FROM messages m JOIN sessions s ON s.id=m.session_id
            WHERE s.user_id=? AND m.content LIKE ? ORDER BY m.id""",
            (user_id, f"%{keyword}%"),
        )
        return [self._message(row) for row in rows]

    async def save_preset(self, preset: Preset) -> Preset:
        preset.updated_at = datetime.now(timezone.utc)
        if not preset.id:
            cursor = await self.conn.execute(
                """INSERT INTO presets(user_id,name,description,system_prompt,is_builtin,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?)""",
                (
                    preset.user_id,
                    preset.name,
                    preset.description,
                    preset.system_prompt,
                    int(preset.is_builtin),
                    preset.created_at.isoformat(),
                    preset.updated_at.isoformat(),
                ),
            )
            preset.id = int(cursor.lastrowid or 0)
        else:
            await self.conn.execute(
                """UPDATE presets SET name=?,description=?,system_prompt=?,is_builtin=?,updated_at=?
                WHERE id=?""",
                (
                    preset.name,
                    preset.description,
                    preset.system_prompt,
                    int(preset.is_builtin),
                    preset.updated_at.isoformat(),
                    preset.id,
                ),
            )
        await self.conn.commit()
        return preset

    async def get_preset_by_id(self, preset_id: int) -> Preset | None:
        row = await self._one("SELECT * FROM presets WHERE id=?", (preset_id,))
        return self._preset(row) if row else None

    async def list_presets(self, user_id: int) -> list[Preset]:
        rows = await self._all(
            "SELECT * FROM presets WHERE user_id IS NULL OR user_id=? ORDER BY is_builtin DESC,id",
            (user_id,),
        )
        return [self._preset(row) for row in rows]

    async def delete_preset(self, preset_id: int) -> None:
        await self.conn.execute("DELETE FROM presets WHERE id=? AND is_builtin=0", (preset_id,))
        await self.conn.commit()

    async def get_user_config(self, user_id: int, key: str) -> str | None:
        row = await self._one(
            "SELECT value FROM user_configs WHERE user_id=? AND key=?", (user_id, key)
        )
        return str(row["value"]) if row else None

    async def set_user_config(self, config: UserConfig) -> None:
        await self.conn.execute(
            """INSERT INTO user_configs(user_id,key,value,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
            (config.user_id, config.key, config.value, config.updated_at.isoformat()),
        )
        await self.conn.commit()

    async def _one(self, sql: str, params: tuple[object, ...] = ()) -> aiosqlite.Row | None:
        async with self.conn.execute(sql, params) as cursor:
            return await cursor.fetchone()

    async def _all(self, sql: str, params: tuple[object, ...] = ()) -> list[aiosqlite.Row]:
        async with self.conn.execute(sql, params) as cursor:
            return list(await cursor.fetchall())

    @staticmethod
    def _user(row: aiosqlite.Row) -> User:
        return User(**dict(row))

    @staticmethod
    def _session(row: aiosqlite.Row) -> Session:
        return Session(**dict(row))

    @staticmethod
    def _message(row: aiosqlite.Row) -> Message:
        return Message(**dict(row))

    @staticmethod
    def _preset(row: aiosqlite.Row) -> Preset:
        data = dict(row)
        data["is_builtin"] = bool(data["is_builtin"])
        return Preset(**data)
