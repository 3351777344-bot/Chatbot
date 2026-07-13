import pytest

from core.user_manager import UserManager


@pytest.mark.asyncio
async def test_user_validation_and_default_model(backend):
    manager = UserManager(backend)
    with pytest.raises(ValueError):
        await manager.create_user("  ")
    user = await manager.create_user("alice", "m1")
    with pytest.raises(ValueError):
        await manager.create_user("alice")
    await manager.set_default_model(user, "m2", {"m1", "m2"})
    assert (await manager.get_user("alice")).default_model == "m2"
