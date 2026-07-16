"""Rich TUI 的统一复用组件。"""

import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.output.win32 import NoConsoleScreenBufferError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
_chat_prompt: PromptSession | None = None
_chat_history = InMemoryHistory()


def print_banner(version: str, python_version: str, current_step: str = "") -> None:
    text = Text("LangChain Chat", style="bold cyan")
    text.append(f"  v{version}", style="dim")
    text.append(f"\nPython {python_version}", style="green")
    if current_step:
        text.append(f"\n当前进度：{current_step}", style="yellow")
    console.print(Panel(text, border_style="cyan", title="欢迎", title_align="left"))


def print_info(message: str) -> None:
    console.print(f"[blue][信息][/] {message}")


def print_success(message: str) -> None:
    console.print(f"[bold green][成功][/] {message}")


def print_error(message: str) -> None:
    console.print(f"[bold red][错误][/] {message}")


def print_warning(message: str) -> None:
    console.print(f"[yellow][警告][/] {message}")


def print_menu(title: str, options: list[str]) -> None:
    table = Table(title=title, show_header=False, border_style="cyan", expand=True)
    table.add_column("序号", style="bold yellow", width=6)
    table.add_column("选项", style="white")
    for index, option in enumerate(options, start=1):
        table.add_row(str(index), option)
    console.print(table)


def print_divider() -> None:
    console.print("[dim]" + "-" * 60 + "[/]")


def read_choice(max_choice: int) -> int:
    while True:
        try:
            choice = int(input(f"请输入序号 (1-{max_choice})，或 0 返回上层: ").strip())
            if choice == 0:
                return -1
            if 1 <= choice <= max_choice:
                return choice - 1
            print_error(f"序号超出范围，请输入 0 到 {max_choice} 之间的数字")
        except ValueError:
            print_error("请输入数字")


def read_text(prompt_text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{prompt_text}{suffix}: ").strip()
    return default if not value and default is not None else value


async def read_chat_input(prompt_text: str = "你 > ") -> str:
    """异步读取对话输入，并支持上下箭头回看历史。"""
    global _chat_prompt
    try:
        if _chat_prompt is None:
            _chat_prompt = PromptSession(history=_chat_history)
        return (await _chat_prompt.prompt_async(prompt_text)).strip()
    except NoConsoleScreenBufferError:
        return (await asyncio.to_thread(input, prompt_text)).strip()
    except (EOFError, KeyboardInterrupt):
        return "/exit"
