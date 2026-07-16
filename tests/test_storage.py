import pytest

from models.schemas import Message, Preset, Session, User, UserConfig
from storage.mysql_backend import MySQLBackend


@pytest.mark.asyncio
async def test_storage_crud_search_and_cascade(backend):
    user = await backend.create_user(User(username="alice", default_model="m1"))
    preset = await backend.save_preset(Preset(user_id=user.id, name="p", system_prompt="s"))
    session = await backend.create_session(
        Session(user_id=user.id, title="t", model_name="m1", preset_id=preset.id)
    )
    await backend.add_message(Message(session_id=session.id, role="human", content="Needle text"))
    await backend.set_user_config(UserConfig(user_id=user.id, key="theme", value="dark"))
    assert (await backend.get_user_by_name("alice")).id == user.id
    assert len(await backend.search_messages(user.id, "Needle")) == 1
    assert await backend.get_user_config(user.id, "theme") == "dark"
    await backend.delete_user(user.id)
    assert await backend.get_session(session.id) is None
    assert await backend.list_messages(session.id) == []


def test_mysql_backend_implements_contract():
    assert not MySQLBackend.__abstractmethods__
    backend = MySQLBackend({"database": "test_db"}, "secret")
    assert backend.settings["database"] == "test_db"
