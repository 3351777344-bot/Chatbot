"""TUI 与未来 UI 实现共同遵守的接口。"""

from abc import ABC, abstractmethod


class AbstractUI(ABC):
    @abstractmethod
    async def display_message(self, role: str, content: str) -> None: ...

    @abstractmethod
    async def get_user_input(self, prompt_text: str = "") -> str: ...

    @abstractmethod
    async def display_menu(self, title: str, options: list[str]) -> int: ...

    @abstractmethod
    async def display_error(self, message: str) -> None: ...

    @abstractmethod
    async def display_info(self, message: str) -> None: ...

    @abstractmethod
    async def run(self) -> None: ...

