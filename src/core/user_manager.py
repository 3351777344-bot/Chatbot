"""用户创建、查询、切换与删除的业务规则。"""

from models.schemas import User
from storage.base import StorageBackend


class UserManager:
    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend

    async def create_user(self, username: str, default_model: str | None = None) -> User:
        username = username.strip()
        if not username:
            raise ValueError("用户名不能为空")
        if await self.backend.get_user_by_name(username) is not None:
            raise ValueError(f"用户名 '{username}' 已存在")
        return await self.backend.create_user(User(username=username, default_model=default_model))

    async def get_user(self, username: str) -> User | None:
        return await self.backend.get_user_by_name(username.strip())

    async def list_users(self) -> list[User]:
        return await self.backend.list_users()

    async def delete_user(self, user_id: int) -> None:
        await self.backend.delete_user(user_id)

    async def set_default_model(self, user: User, model_name: str, available: set[str]) -> None:
        if model_name not in available:
            raise ValueError(f"模型不可用: {model_name}")
        user.default_model = model_name
        await self.backend.update_user(user)

    async def user_exists(self, username: str) -> bool:
        return await self.get_user(username) is not None
