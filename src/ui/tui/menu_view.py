"""Step 2 菜单桩函数。"""

from ui.tui import widgets


def show_user_menu() -> None:
    widgets.print_info("用户管理功能将在 Step 4 实现")


def show_session_menu() -> None:
    widgets.print_info("会话管理功能将在 Step 7、Step 8 实现")


def show_preset_menu() -> None:
    widgets.print_info("预设管理功能将在 Step 5 实现")


def show_settings_menu() -> None:
    widgets.print_info("设置功能将在 Step 10 实现")


def show_about() -> None:
    widgets.console.print("[bold cyan]LangChain Chat[/] - 当前进度：Step 2 TUI 骨架")
