"""TUI 主应用与菜单路由。"""

import platform

from interface.ui_protocol import AbstractUI
from core.config_manager import get_config
from core.user_manager import UserManager
from core.preset_manager import PresetManager
from core.session_manager import SessionManager
from core.chat_engine import ChatEngine
from storage.base import StorageBackend
from ui.tui import menu_view, widgets
from ui.tui.chat_view import start_chat

MAIN_MENU_OPTIONS = ["用户管理", "会话管理", "预设管理", "开始对话", "搜索对话", "设置", "关于", "退出"]
USER_MENU_OPTIONS = ["创建用户", "列出所有用户", "切换当前用户", "删除用户", "返回主菜单"]
PRESET_MENU_OPTIONS = ["浏览预设", "选择预设", "新建自定义预设", "编辑自定义预设", "删除自定义预设", "返回主菜单"]
SESSION_MENU_OPTIONS = ["列出会话", "加载会话", "新建会话", "重命名会话", "删除会话", "查看会话记录", "返回主菜单"]


class TUIApp(AbstractUI):
    def __init__(self, backend: StorageBackend | None = None, chat_engine: ChatEngine | None = None) -> None:
        self.config = get_config()
        self.backend = backend
        self.chat_engine = chat_engine
        self.user_manager = UserManager(backend) if backend else None
        self.preset_manager = PresetManager(backend) if backend else None
        self.session_manager = SessionManager(backend, self.config) if backend else None
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
                await self._show_session_menu()
            elif choice == 2:
                await self._show_preset_menu()
            elif choice == 3:
                if self.chat_engine is None:
                    widgets.print_error("对话引擎未初始化")
                else:
                    await start_chat(self)
            elif choice == 4:
                await self._search_messages()
            elif choice == 5:
                menu_view.show_settings_menu()
            elif choice == 6:
                menu_view.show_about()
            elif choice == 7:
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
            user = await self.user_manager.create_user(username, get_config().secret.MODEL_NAME)
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

    async def _show_session_menu(self) -> None:
        if self.current_user is None:
            widgets.print_warning("请先创建或切换用户")
            return
        while True:
            choice = await self.display_menu("会话管理", SESSION_MENU_OPTIONS)
            if choice in (-1, 6):
                return
            try:
                if choice == 0:
                    await self._list_sessions()
                elif choice == 1:
                    await self._load_session()
                elif choice == 2:
                    await self._new_session()
                elif choice == 3:
                    await self._rename_session()
                elif choice == 4:
                    await self._delete_session()
                elif choice == 5:
                    await self._view_session_messages()
            except (ValueError, TypeError) as exc:
                widgets.print_error(str(exc))

    async def _list_sessions(self) -> list:
        sessions = await self.session_manager.list_sessions(self.current_user.id)
        for session in sessions:
            current = " <- 当前" if self.current_session and session.id == self.current_session.id else ""
            widgets.console.print(
                f"  id={session.id} [cyan]{session.title}[/] 模型={session.model_name} "
                f"Token={session.total_prompt_tokens + session.total_completion_tokens}{current}"
            )
        widgets.print_info(f"共 {len(sessions)} 个会话")
        return sessions

    async def _load_session(self) -> None:
        await self._list_sessions()
        session_id = int(await self.get_user_input("要加载的会话 id"))
        session = await self.session_manager.get_session(session_id, self.current_user.id)
        if session is None:
            raise ValueError("会话不存在或无权访问")
        self.current_session = session
        self.current_preset = (
            await self.preset_manager.get_preset(session.preset_id) if session.preset_id else None
        )
        widgets.print_success(f"已加载会话: {session.title}")

    async def _new_session(self) -> None:
        model = self.current_user.default_model or self.config.default_model
        self.current_session = await self.session_manager.create_session(
            self.current_user.id, model, self.current_preset.id if self.current_preset else None
        )
        widgets.print_success(f"已新建会话（id={self.current_session.id}）")

    async def _rename_session(self) -> None:
        session_id = int(await self.get_user_input("要重命名的会话 id"))
        title = await self.get_user_input("新标题")
        await self.session_manager.rename_session(session_id, title, self.current_user.id)
        if self.current_session and self.current_session.id == session_id:
            self.current_session.title = title[: self.config.title_max_length]
        widgets.print_success("会话已重命名")

    async def _delete_session(self) -> None:
        session_id = int(await self.get_user_input("要删除的会话 id"))
        confirm = await self.get_user_input("输入 yes 确认删除")
        if confirm.lower() != "yes":
            widgets.print_info("已取消删除")
            return
        await self.session_manager.delete_session(session_id, self.current_user.id)
        if self.current_session and self.current_session.id == session_id:
            self.current_session = None
        widgets.print_success("会话及其消息已删除")

    async def _view_session_messages(self) -> None:
        session_id = int(await self.get_user_input("要查看的会话 id"))
        session = await self.session_manager.get_session(session_id, self.current_user.id)
        if session is None:
            raise ValueError("会话不存在或无权访问")
        messages = await self.session_manager.get_session_messages(session_id)
        widgets.console.print(f"[bold]{session.title}[/] 的记录")
        for message in messages:
            label = {"human": "你", "ai": "AI", "system": "系统"}[message.role]
            widgets.console.print(f"[bold]{label}[/]: {message.content}")
        widgets.print_info(f"共 {len(messages)} 条消息")

    async def _search_messages(self) -> None:
        if self.current_user is None:
            widgets.print_warning("请先创建或切换用户")
            return
        keyword = await self.get_user_input("搜索关键词")
        results = await self.session_manager.search_messages(self.current_user.id, keyword)
        if not results:
            widgets.print_info("没有匹配的消息")
            return
        sessions = {s.id: s for s in await self.session_manager.list_sessions(self.current_user.id)}
        grouped: dict[int, list] = {}
        for message in results:
            grouped.setdefault(message.session_id, []).append(message)
        for session_id, messages in grouped.items():
            title = sessions.get(session_id).title if session_id in sessions else f"会话 {session_id}"
            widgets.console.print(f"\n[bold cyan]{title}[/]（id={session_id}）")
            for message in messages:
                label = {"human": "你", "ai": "AI", "system": "系统"}[message.role]
                widgets.console.print(f"  [{label}] {message.content}")
        widgets.print_info(f"找到 {len(results)} 条匹配消息")
