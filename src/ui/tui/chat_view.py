"""多轮流式对话视图。"""

from langchain_core.messages import SystemMessage
from ui.tui import widgets


async def start_chat(app) -> None:
    if app.current_user is None:
        widgets.print_warning("请先创建或切换用户")
        return
    if app.current_session is None:
        await _new_session(app)
    widgets.console.print("[bold green]=== 对话开始（/help 查看命令，/exit 退出）===[/]")

    while True:
        user_input = await widgets.read_chat_input()
        if not user_input:
            continue
        if user_input.startswith("/"):
            if await _handle_command(app, user_input):
                return
            continue

        first_turn = not await app.session_manager.has_messages(app.current_session.id)
        await app.session_manager.add_message(app.current_session, "human", user_input)
        history = await app.session_manager.load_messages_as_langchain(app.current_session.id)
        if app.current_preset:
            history.insert(0, SystemMessage(content=app.current_preset.system_prompt))

        widgets.console.print("[bold green]AI > [/bold green]", end="")
        reply_parts: list[str] = []
        usage = None
        try:
            async for text, chunk_usage in app.chat_engine.astream(history):
                if text:
                    reply_parts.append(text)
                    widgets.console.print(text, end="", markup=False)
                if chunk_usage is not None:
                    usage = chunk_usage
            widgets.console.print()
        except Exception as exc:
            widgets.print_error(f"模型调用失败: {exc}")
            continue

        reply = "".join(reply_parts)
        usage = usage or {"prompt_tokens": 0, "completion_tokens": 0}
        await app.session_manager.add_message(
            app.current_session,
            "ai",
            reply,
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )
        widgets.print_info(
            f"Token: 输入 {usage.get('prompt_tokens', 0)} / 输出 {usage.get('completion_tokens', 0)}"
        )
        if first_turn:
            title = await app.session_manager.generate_title(user_input, app.chat_engine)
            await app.session_manager.update_title(app.current_session, title)


async def _new_session(app) -> None:
    model = app.current_user.default_model or app.config.default_model
    app.current_session = await app.session_manager.create_session(
        app.current_user.id,
        model,
        app.current_preset.id if app.current_preset else None,
    )
    widgets.print_success(f"已新建会话（id={app.current_session.id}，模型={model}）")


async def _handle_command(app, command: str) -> bool:
    name, _, argument = command.partition(" ")
    if name == "/exit":
        return True
    if name == "/new":
        app.current_session = None
        await _new_session(app)
    elif name == "/rename":
        if not argument.strip():
            widgets.print_warning("用法: /rename 新标题")
        else:
            await app.session_manager.update_title(app.current_session, argument)
            widgets.print_success("标题已更新")
    elif name == "/help":
        widgets.console.print("/exit 返回  /new 新会话  /rename 标题  /help 帮助")
    else:
        widgets.print_warning(f"未知命令: {name}")
    return False
