"""SQLite connection, schema initialization, and small data-access helpers."""

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from config.settings import DATABASE_PATH


def get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Return a SQLite connection using row dictionaries."""
    db_path.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create users, conversations, and messages tables if they do not exist."""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                model_name TEXT NOT NULL,
                role_name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
                ON conversations (user_id, updated_at DESC);

            CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
                ON messages (conversation_id, created_at ASC);
            """
        )


def _fetch_one(query: str, params: Iterable = ()) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(query, tuple(params)).fetchone()


def _fetch_all(query: str, params: Iterable = ()) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(query, tuple(params)).fetchall()


def get_or_create_user(username: str) -> sqlite3.Row:
    """Create a user when needed and return its row."""
    cleaned = username.strip() or "demo_user"
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (username) VALUES (?)",
            (cleaned,),
        )
        return conn.execute(
            "SELECT id, username, created_at FROM users WHERE username = ?",
            (cleaned,),
        ).fetchone()


def create_conversation(user_id: int, title: str, model_name: str, role_name: str) -> int:
    """Create a new conversation and return its id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO conversations (user_id, title, model_name, role_name)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, title, model_name, role_name),
        )
        return int(cursor.lastrowid)


def list_conversations(user_id: int) -> list[sqlite3.Row]:
    """List conversations belonging to a user."""
    return _fetch_all(
        """
        SELECT id, user_id, title, model_name, role_name, created_at, updated_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY updated_at DESC, id DESC
        """,
        (user_id,),
    )


def get_conversation(conversation_id: int, user_id: int | None = None) -> sqlite3.Row | None:
    """Return a conversation, optionally scoped to a user."""
    if user_id is None:
        return _fetch_one(
            """
            SELECT id, user_id, title, model_name, role_name, created_at, updated_at
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        )
    return _fetch_one(
        """
        SELECT id, user_id, title, model_name, role_name, created_at, updated_at
        FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, user_id),
    )


def update_conversation_settings(conversation_id: int, model_name: str, role_name: str) -> None:
    """Update model and role for an existing conversation."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE conversations
            SET model_name = ?, role_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (model_name, role_name, conversation_id),
        )


def rename_conversation(conversation_id: int, title: str) -> None:
    """Rename a conversation."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title.strip() or "New conversation", conversation_id),
        )


def touch_conversation(conversation_id: int) -> None:
    """Refresh the updated_at timestamp."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,),
        )


def add_message(conversation_id: int, role: str, content: str) -> int:
    """Add a message and return its id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )
        conn.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,),
        )
        return int(cursor.lastrowid)


def list_messages(conversation_id: int) -> list[sqlite3.Row]:
    """List all messages for a conversation in chronological order."""
    return _fetch_all(
        """
        SELECT id, conversation_id, role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,),
    )


def count_messages(conversation_id: int) -> int:
    """Return message count for a conversation."""
    row = _fetch_one(
        "SELECT COUNT(*) AS message_count FROM messages WHERE conversation_id = ?",
        (conversation_id,),
    )
    return int(row["message_count"]) if row else 0
