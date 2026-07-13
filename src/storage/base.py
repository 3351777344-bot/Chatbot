"""所有存储后端必须实现的异步接口。"""

from abc import ABC, abstractmethod

from models.schemas import Message, Preset, Session, User, UserConfig


class StorageBackend(ABC):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def create_user(self, user: User) -> User: ...

    @abstractmethod
    async def get_user_by_name(self, username: str) -> User | None: ...

    @abstractmethod
    async def list_users(self) -> list[User]: ...

    @abstractmethod
    async def delete_user(self, user_id: int) -> None: ...

    @abstractmethod
    async def create_session(self, session: Session) -> Session: ...

    @abstractmethod
    async def get_session(self, session_id: int) -> Session | None: ...

    @abstractmethod
    async def list_sessions(self, user_id: int) -> list[Session]: ...

    @abstractmethod
    async def update_session(self, session: Session) -> None: ...

    @abstractmethod
    async def delete_session(self, session_id: int) -> None: ...

    @abstractmethod
    async def add_message(self, message: Message) -> Message: ...

    @abstractmethod
    async def list_messages(self, session_id: int) -> list[Message]: ...

    @abstractmethod
    async def search_messages(self, user_id: int, keyword: str) -> list[Message]: ...

    @abstractmethod
    async def save_preset(self, preset: Preset) -> Preset: ...

    @abstractmethod
    async def list_presets(self, user_id: int) -> list[Preset]: ...

    @abstractmethod
    async def delete_preset(self, preset_id: int) -> None: ...

    @abstractmethod
    async def get_user_config(self, user_id: int, key: str) -> str | None: ...

    @abstractmethod
    async def set_user_config(self, config: UserConfig) -> None: ...

