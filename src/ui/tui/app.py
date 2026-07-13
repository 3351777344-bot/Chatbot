"""TUI 主应用与菜单路由。"""

import platform

from interface.ui_protocol import AbstractUI
from ui.tui import menu_view, widgets
from ui.tui.chat_view import start_chat

MAIN_MENU_OPTIONS = ["用户管理", "会话管理", "预设管理", "开始对话", "设置", "关于", "退出"]


class TUIApp(AbstractUI):
    def __init__(self) -> None:
        self.current_user = None
        self.current_session = None

    async def display_message(self, role: str, content: str) -> None:
        labels = {"human": "[bold cyan][你][/]", "ai": "[bold green][AI][/]"}
        widgets.console.print(f"{labels.get(role, '[dim][系统][/]')} {content}")

    async def get_user_input(self, prompt_text: str = "") -> str:
        return widgets.read_text(prompt_text)

    async def display_menu(self, title: str, options: list[str]) -> int:
        widgets.print_menu(title, options)
        return widgets.read_choice(len(options))

    async def display_error(self, message: str) -> None:
        widgets.print_error(message)

    async def display_info(self, message: str) -> None:
        widgets.print_info(message)

    async def run(self) -> None:
        widgets.print_banner("0.1.0", platform.python_version())
        while True:
            choice = await self.display_menu("主菜单", MAIN_MENU_OPTIONS)
            if choice == 0:
                menu_view.show_user_menu()
            elif choice == 1:
                menu_view.show_session_menu()
            elif choice == 2:
                menu_view.show_preset_menu()
            elif choice == 3:
                await start_chat()
            elif choice == 4:
                menu_view.show_settings_menu()
            elif choice == 5:
                menu_view.show_about()
            elif choice == 6:
                widgets.print_info("感谢使用，再见。")
                break

