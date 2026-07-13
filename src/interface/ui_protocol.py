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

    def supports(self, capability: str) -> bool:
        """声明 UI 是否支持可选能力；基础实现默认不支持。"""
        return False

    async def compare_models(self, prompt: str, models: list[str]) -> dict[str, str]:
        """多模型并行对比扩展点（H2）。"""
        raise NotImplementedError("当前 UI 尚未实现多模型并行对比")

    async def receive_attachment(self, path: str, media_type: str) -> object:
        """图片/文件上传扩展点（H3）。"""
        raise NotImplementedError("当前 UI 尚未实现附件上传")

    async def receive_audio(self, audio: bytes, media_type: str) -> str:
        """语音输入与转写扩展点（H4）。"""
        raise NotImplementedError("当前 UI 尚未实现语音输入")

    async def confirm_tool_call(self, tool_name: str, arguments: dict) -> bool:
        """Tool Calling 人工确认扩展点（H5）。"""
        raise NotImplementedError("当前 UI 尚未实现工具调用确认")
