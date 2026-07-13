"""TUI 主应用与菜单路由。"""

import platform

from interface.ui_protocol import AbstractUI
from core.config_manager import get_config
from core.user_manager import UserManager
from core.preset_manager import PresetManager
from storage.base import StorageBackend
from ui.tui import menu_view, widgets
from ui.tui.chat_view import start_chat

MAIN_MENU_OPTIONS = ["用户管理", "会话管理", "预设管理", "开始对话", "设置", "关于", "退出"]
USER_MENU_OPTIONS = ["创建用户", "列出所有用户", "切换当前用户", "删除用户", "返回主菜单"]
PRESET_MENU_OPTIONS = ["浏览预设", "选择预设", "新建自定义预设", "编辑自定义预设", "删除自定义预设", "返回主菜单"]


class TUIApp(AbstractUI):
    def __init__(self, backend: StorageBackend | None = None) -> None:
        self.backend = backend
        self.user_manager = UserManager(backend) if backend else None
        self.preset_manager = PresetManager(backend) if backend else None
        self.current_user = None
        self.current_session = None
        self.current_preset = None

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
        config = get_config()
        widgets.print_banner(
            config.get("app", "version", default="0.1.0"),
            platform.python_version(),
            config.get("app", "current_step", default=""),
        )
        while True:
            choice = await self.display_menu("主菜单", MAIN_MENU_OPTIONS)
            if choice == 0:
                await self._show_user_menu()
            elif choice == 1:
                menu_view.show_session_menu()
            elif choice == 2:
                await self._show_preset_menu()
            elif choice == 3:
                await start_chat()
            elif choice == 4:
                menu_view.show_settings_menu()
            elif choice == 5:
                menu_view.show_about()
            elif choice == 6:
                widgets.print_info("感谢使用，再见。")
                break

    def _show_current_user(self) -> None:
        if self.current_user:
            widgets.console.print(
                f"[dim]当前用户: [bold yellow]{self.current_user.username}[/]"
                f"（id={self.current_user.id}）[/]"
            )
        else:
            widgets.console.print("[dim]当前用户: 未登录[/]")

    async def _show_user_menu(self) -> None:
        if self.user_manager is None:
            widgets.print_error("用户管理未初始化（存储后端未注入）")
            return
        while True:
            widgets.print_divider()
            self._show_current_user()
            choice = await self.display_menu("用户管理", USER_MENU_OPTIONS)
            if choice in (-1, 4):
                return
            if choice == 0:
                await self._create_user()
            elif choice == 1:
                await self._list_users()
            elif choice == 2:
                await self._switch_user()
            elif choice == 3:
                await self._delete_user()

    async def _create_user(self) -> None:
        username = await self.get_user_input("请输入新用户名")
        try:
            user = await self.user_manager.create_user(username, get_config().default_model)
            widgets.print_success(f"用户创建成功: {user.username}（id={user.id}）")
            if self.current_user is None:
                self.current_user = user
                widgets.print_info(f"已自动切换为当前用户: {user.username}")
        except ValueError as exc:
            widgets.print_error(str(exc))

    async def _list_users(self) -> None:
        users = await self.user_manager.list_users()
        if not users:
            widgets.print_info("目前没有任何用户")
            return
        for user in users:
            current = " <- 当前" if self.current_user and user.id == self.current_user.id else ""
            widgets.console.print(
                f"  id={user.id}  用户名=[cyan]{user.username}[/] "
                f"模型={user.default_model or '默认'}{current}"
            )
        widgets.print_info(f"共 {len(users)} 个用户")

    async def _switch_user(self) -> None:
        username = await self.get_user_input("请输入要切换到的用户名")
        user = await self.user_manager.get_user(username)
        if user is None:
            widgets.print_error(f"用户 '{username}' 不存在")
            return
        self.current_user = user
        self.current_session = None
        widgets.print_success(f"已切换到用户: {user.username}（id={user.id}）")

    async def _delete_user(self) -> None:
        username = await self.get_user_input("请输入要删除的用户名")
        user = await self.user_manager.get_user(username)
        if user is None:
            widgets.print_error(f"用户 '{username}' 不存在")
            return
        if self.current_user and user.id == self.current_user.id:
            widgets.print_warning("不允许删除当前正在登录的用户，请先切换到其他用户")
            return
        confirm = await self.get_user_input(f"确认删除用户 '{username}'？输入 yes 确认")
        if confirm.lower() != "yes":
            widgets.print_info("已取消删除")
            return
        await self.user_manager.delete_user(user.id)
        widgets.print_success(f"用户 '{username}' 已删除（关联数据已自动清理）")

    async def _show_preset_menu(self) -> None:
        if self.current_user is None:
            widgets.print_warning("请先创建或切换用户")
            return
        while True:
            choice = await self.display_menu("预设管理", PRESET_MENU_OPTIONS)
            if choice in (-1, 5):
                return
            try:
                if choice == 0:
                    await self._list_presets()
                elif choice == 1:
                    await self._select_preset()
                elif choice == 2:
                    await self._create_preset()
                elif choice == 3:
                    await self._edit_preset()
                elif choice == 4:
                    await self._delete_preset()
            except ValueError as exc:
                widgets.print_error(str(exc))

    async def _list_presets(self) -> list:
        presets = await self.preset_manager.list_presets(self.current_user.id)
        for preset in presets:
            kind = "内置" if preset.is_builtin else "自定义"
            selected = " <- 当前" if self.current_preset and preset.id == self.current_preset.id else ""
            widgets.console.print(f"  id={preset.id} [{kind}] [cyan]{preset.name}[/] {preset.description}{selected}")
        widgets.print_info(f"共 {len(presets)} 个可用预设")
        return presets

    async def _select_preset(self) -> None:
        await self._list_presets()
        raw = await self.get_user_input("输入预设 id，输入 0 表示不使用预设")
        if raw == "0":
            self.current_preset = None
            widgets.print_success("已取消预设")
            return
        preset = await self.preset_manager.get_preset(int(raw))
        if preset is None or (not preset.is_builtin and preset.user_id != self.current_user.id):
            raise ValueError("预设不存在或不可访问")
        self.current_preset = preset
        widgets.print_success(f"已选择预设: {preset.name}")

    async def _create_preset(self) -> None:
        preset = await self.preset_manager.create_preset(
            self.current_user.id,
            await self.get_user_input("预设名称"),
            await self.get_user_input("预设描述"),
            await self.get_user_input("系统提示词"),
        )
        widgets.print_success(f"已创建预设: {preset.name}（id={preset.id}）")

    async def _edit_preset(self) -> None:
        preset = await self.preset_manager.get_preset(int(await self.get_user_input("要编辑的预设 id")))
        if preset is None:
            raise ValueError("预设不存在")
        name = widgets.read_text("预设名称", preset.name)
        description = widgets.read_text("预设描述", preset.description)
        prompt = widgets.read_text("系统提示词", preset.system_prompt)
        await self.preset_manager.update_preset(preset, name, description, prompt, self.current_user.id)
        widgets.print_success("预设已更新")

    async def _delete_preset(self) -> None:
        preset_id = int(await self.get_user_input("要删除的预设 id"))
        await self.preset_manager.delete_preset(preset_id, self.current_user.id)
        if self.current_preset and self.current_preset.id == preset_id:
            self.current_preset = None
        widgets.print_success("预设已删除")
