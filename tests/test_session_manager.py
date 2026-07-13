from pathlib import Path

import pytest
import yaml

from core.config_manager import AppConfig
from core.session_manager import SessionManager
from core.user_manager import UserManager


@pytest.mark.asyncio
async def test_session_permissions_search_and_export(backend, tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump({"export": {"dir": str(tmp_path / "exports")}}), encoding="utf-8")
    manager = SessionManager(backend, AppConfig(config_path))
    users = UserManager(backend)
    alice = await users.create_user("alice")
    bob = await users.create_user("bob")
    session = await manager.create_session(alice.id, "m", title="safe/title")
    await manager.add_message(session, "human", "searchable")
    await manager.add_message(session, "ai", "answer", 2, 3)
    assert len(await manager.search_messages(alice.id, "search")) == 1
    assert await manager.search_messages(bob.id, "search") == []
    with pytest.raises(ValueError):
        await manager.rename_session(session.id, "hack", bob.id)
    exported = await manager.export_markdown(session.id, alice.username, alice.id)
    assert exported.exists() and "searchable" in exported.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        await manager.delete_session(session.id, bob.id)
