import pytest

from core.preset_manager import PresetManager
from core.user_manager import UserManager


@pytest.mark.asyncio
async def test_builtin_idempotency_and_private_permissions(backend):
    users = UserManager(backend)
    alice = await users.create_user("alice")
    bob = await users.create_user("bob")
    manager = PresetManager(backend)
    assert await manager.load_builtin_presets() > 0
    assert await manager.load_builtin_presets() == 0
    custom = await manager.create_preset(alice.id, "private", "", "prompt")
    assert custom not in await manager.list_presets(bob.id)
    with pytest.raises(ValueError):
        await manager.delete_preset(custom.id, bob.id)
    builtin = next(item for item in await manager.list_presets(alice.id) if item.is_builtin)
    with pytest.raises(ValueError):
        await manager.delete_preset(builtin.id, alice.id)
