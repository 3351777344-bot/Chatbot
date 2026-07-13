# Step 9：对话搜索 + Bug 修复 + 查看会话记录（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-26
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-9-search`

---

## 阅读说明

本文档是 langchain-chat 项目第九步的完整教学手册。本步骤做三件事：

1. **修复两个 bug**：创建用户和创建会话时，模型名用了错误的配置源。
2. **新增「查看会话记录」功能**：在会话管理里查看某个会话的全部聊天记录。
3. **实现对话搜索功能**（需求 E1）：在当前用户的所有历史会话中按关键词搜索消息。

阅读并跟随操作后，你应当能够：

1. 理解配置源不一致会导致什么问题（bug 的根因）。
2. 掌握在业务层封装搜索功能的方法。
3. 实现会话记录查看和关键词搜索两个界面功能。
4. 理解 LIKE 模糊查询在搜索中的应用。

**本文档的设计原则**（与前八步文档一致）：

- 每一个概念都用「3W1H」框架讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，由学习者自行创建文件并粘贴内容。
- 全面验证，及早发现问题。

**完成标志（学完本文档后你应达成的目标）**：

- 修复 app.py 和 chat_view.py 的模型名配置 bug。
- 新增「查看会话记录」功能（会话管理子菜单新增选项）。
- 新增对话搜索功能（SessionManager 新增 search_messages + 主菜单新增「搜索」入口）。
- 执行 `uv run python src/main.py`，能查看会话记录、按关键词搜索历史消息。
- 本地 Git 仓库存在提交与标签 `step-9-search`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置回顾](#二前置回顾)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、动手实践：Bug 修复 + 功能实现](#四动手实践bug-修复--功能实现)
- [五、整体运行验证](#五整体运行验证)
- [六、版本控制](#六版本控制)
- [七、常见问题与排查](#七常见问题与排查)
- [八、本步骤小结与知识清单](#八本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

本步骤分三部分：

**第一部分：Bug 修复（2 处）**

创建用户时，用户的 `default_model` 存了 `deepseek-chat`（来自 config.yaml 的 models.default），但实际对话用的是 `qwen3.6-flash`（来自 .env 的 MODEL_NAME）。两者不一致。创建会话时也有同样的问题。修复方法是统一使用 `.env` 里的 `MODEL_NAME`。

**第二部分：新增「查看会话记录」功能**

目前用户退出对话后，无法回看之前的聊天记录。在会话管理子菜单里新增「查看会话记录」选项，选中一个会话后，显示该会话的全部消息（按时间正序，标注角色）。

**第三部分：实现对话搜索（需求 E1）**

在当前用户的所有历史会话中按关键词搜索消息内容。比如搜「Python」，所有提到 Python 的消息都会显示出来，并标注属于哪个会话。

### 1.2 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 8 的会话管理完善（标签 step-8-session-mgmt） |
| 输出 | Bug 修复 + 会话记录查看 + 对话搜索 |
| MVP 验证点 | 能查看会话记录、能搜索关键词、模型名正确 |

### 1.3 本步骤产出的文件

```
langchain-chat/
├── src/
│   ├── core/
│   │   └── session_manager.py       新增 search_messages + get_session_messages（改造）
│   ├── ui/tui/
│   │   ├── app.py                   Bug 修复 + 搜索菜单 + 会话记录查看（改造）
│   │   └── chat_view.py             Bug 修复（改造）
│   └── config.yaml                  current_step 改为 Step 9
```

共改造 4 个文件。无新建文件，无新依赖。

### 1.4 本步骤的设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 搜索方法放哪 | SessionManager 新增 search_messages | 保持「不穿透」原则 |
| 搜索入口放哪 | 主菜单新增「搜索」选项 | 搜索是跨会话的全局功能 |
| 会话记录查看放哪 | 会话管理子菜单新增「查看会话记录」 | 与会话管理放一起 |
| 搜索结果显示 | 显示匹配消息 + 所属会话标题 | 用户需要知道消息来自哪个会话 |

---

## 二、前置回顾

### 2.1 Step 8 回顾

| 已完成 | 结论 |
|--------|------|
| 会话管理 | 完整可用（列表/加载/重命名/删除，9 个方法齐全） |
| 分层架构 | 穿透问题已修复 |
| 对话功能 | 多轮流式对话完整可用 |
| 当前短板 | 无法查看历史聊天记录；无法搜索；模型名 bug |

### 2.2 已有的搜索能力

Step 3 的 SQLiteBackend 已经实现了 `search_messages(user_id, keyword)` 方法（LIKE 模糊查询 + 联表查询），但一直没在 TUI 里使用。Step 9 就是把这个能力暴露给用户。

### 2.3 本步骤不需要新依赖

复用前面步骤已安装的库，无需安装新库。

---

## 三、核心概念讲解（3W1H）

### 3.1 配置源的一致性（Bug 根因分析）

**What（是什么）**

本项目有两个地方可以配置「模型名」：

| 配置源 | 字段 | 你当前的值 | 用在哪 |
|--------|------|----------|--------|
| config.yaml | `models.default` | `deepseek-chat` | 创建用户/会话时作为模型名 |
| .env | `MODEL_NAME` | `qwen3.6-flash` | ChatEngine 实际调用的模型 |

两个值不一致，导致：用户表和会话表里记录的模型名是 `deepseek-chat`，但实际对话用的是 `qwen3.6-flash`。

**Why（为什么会出现这个 bug）**

Step 4（用户管理）实现时，用了 `config.default_model`（来自 config.yaml）。当时 .env 里配的也是 `deepseek-chat`，所以两者一致，bug 没暴露。后来把 .env 的 MODEL_NAME 改成了 `qwen3.6-flash`，但 config.yaml 的 models.default 没同步改，两者就不一致了。

**Which（哪个配置源应该为准）**

应该以 `.env` 的 `MODEL_NAME` 为准。原因：

- `.env` 是「实际使用的配置」（敏感配置层），你实际用什么模型就填什么。
- config.yaml 的 `models.default` 是「可选模型的默认值」（业务配置层），它的作用更多是「列出可选模型」，不一定是当前实际用的。

所以创建用户和会话时，应该用 `config.secret.MODEL_NAME`（.env 的值），而不是 `config.default_model`（config.yaml 的值）。

**How（怎么修复）**

把 app.py 的 `_create_user` 和 chat_view.py 的 `_create_new_session` 里，`config.default_model` 改为 `config.secret.MODEL_NAME`。

### 3.2 模糊搜索（LIKE 查询）

**What（是什么）**

模糊搜索是指「不要求完全匹配，只要包含关键词就算命中」的搜索方式。SQL 里用 `LIKE` 操作符实现。

**Why（为什么需要模糊搜索）**

精确搜索要求用户输入的内容和数据库里的完全一样（连标点符号都不能差）。对话消息可能很长，用户不可能记住完整内容。模糊搜索只需要输入一个关键词，所有包含这个词的消息都能找到。

**How（LIKE 的用法）**

Step 3 已经讲过 LIKE 的语法，这里回顾：

```sql
-- 搜索 content 字段包含「Python」的消息
SELECT * FROM messages WHERE content LIKE '%Python%';
```

`%` 是通配符，代表任意数量的任意字符。`%Python%` 表示「前后都可以有任意内容，只要中间出现了 Python」。

本项目 Step 3 的 SQLiteBackend.search_messages 已经实现了这个查询：

```python
# sqlite_backend.py 的 search_messages（Step 3 已实现）
async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
    async with self._conn.execute(
        """SELECT m.* FROM messages m
           JOIN sessions s ON m.session_id = s.id
           WHERE s.user_id = ? AND m.content LIKE ?
           ORDER BY m.id""",
        (user_id, f"%{keyword}%"),
    ) as cursor:
        ...
```

这里用了**联表查询（JOIN）**：messages 表关联 sessions 表，确保只搜索「属于该用户」的消息（用户隔离）。

Step 9 要做的是：在 SessionManager 封装这个方法（保持不穿透），然后在 TUI 提供搜索界面。

### 3.3 搜索结果的展示设计

**What（搜索结果应该显示什么）**

搜索返回的是 Message 列表（匹配的消息）。但用户看到一条消息时，还需要知道它属于哪个会话（否则只知道内容，不知道上下文）。所以搜索结果需要额外显示「所属会话标题」。

**Why（为什么需要会话标题）**

用户搜「Python」，可能有多条匹配的消息，来自不同会话。如果不显示会话标题，用户看到一条「请帮我写快速排序」，不知道这是哪个对话里的。

**How（怎么实现）**

search_messages 返回 Message 列表，每条 Message 有 `session_id`。通过 session_id 可以查到对应的会话标题。在搜索结果里，先按 session_id 分组，每组显示会话标题，再显示该会话下的匹配消息。

---

## 四、动手实践：Bug 修复 + 功能实现

下面依次完成所有改动。全部代码由你亲手创建，我只在文档里给出内容。

### 4.1 Bug 修复：app.py 的 _create_user（模型名）

文件路径：`langchain-chat/src/ui/tui/app.py`。

找到 `_create_user` 方法里的这一行（约第 222 行）：

```python
                username, default_model=config.default_model
```

改为（用 `.env` 的 MODEL_NAME）：

```python
                username, default_model=config.secret.MODEL_NAME
```

### 4.2 Bug 修复：chat_view.py 的 _create_new_session（模型名）

文件路径：`langchain-chat/src/ui/tui/chat_view.py`。

找到 `_create_new_session` 函数里的这一行（约第 199 行）：

```python
        model_name=config.default_model,
```

改为：

```python
        model_name=config.secret.MODEL_NAME,
```

#### 验证检查点 A：Bug 是否修复

启动程序（执行： uv run python src/main.py），创建新用户，列出用户，确认模型名显示的是 .env 里的 MODEL_NAME（如 qwen3.6-flash），而不是 deepseek-chat。

---

### 4.3 改造 src/core/session_manager.py（新增 2 个方法）

文件路径：`langchain-chat/src/core/session_manager.py`（Step 8 已完善，本步骤再追加 2 个方法）。

在文件末尾（`delete_session` 方法之后），追加以下 2 个方法：

```python
    # ── 搜索与记录查看（Step 9 新增）─────────────────────────────────────

    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        """在指定用户的所有会话中按关键词搜索消息（E1 对话搜索）。

        参数：
            user_id: 用户 ID（只搜该用户的消息，用户隔离）
            keyword: 搜索关键词
        返回：
            匹配的 Message 列表（按 id 正序，即时间正序）
        """
        if not keyword or not keyword.strip():
            return []
        keyword = keyword.strip()
        return await self.backend.search_messages(user_id, keyword)

    async def get_session_messages(self, session_id: int) -> list[Message]:
        """获取指定会话的全部消息（用于查看会话记录）。

        参数：
            session_id: 会话 ID
        返回：
            该会话的全部 Message 列表（按 id 正序，即时间正序）
        """
        return await self.backend.list_messages(session_id)
```

**设计说明**：

- `search_messages`：封装 backend.search_messages（保持不穿透）。加了空关键词检查（空关键词直接返回空列表，不查库）。
- `get_session_messages`：封装 backend.list_messages（用于查看会话记录）。和 `load_messages_as_langchain` 的区别：这个返回原始 Message 列表（含 role/content/tokens），而 load_messages_as_langchain 转成 LangChain 格式（供 ChatEngine 用）。

#### 验证检查点 B：新方法能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.session_manager import SessionManager; print('有 search_messages:', hasattr(SessionManager, 'search_messages')); print('有 get_session_messages:', hasattr(SessionManager, 'get_session_messages'))"
```

预期输出：

```
有 search_messages: True
有 get_session_messages: True
```

---

### 4.4 改造 src/ui/tui/app.py（会话记录查看 + 搜索菜单 + Bug 修复）

文件路径：`langchain-chat/src/ui/tui/app.py`（Step 8 已改造，本步骤继续）。

这是本步骤改动最多的文件。有 4 处改动：

**改动 1**：主菜单新增「搜索」选项。

找到文件顶部的 `MAIN_MENU_OPTIONS`：

```python
MAIN_MENU_OPTIONS = [
    "用户管理",
    "会话管理",
    "预设管理",
    "开始对话",
    "设置",
    "关于",
    "退出",
]
```

在「开始对话」之后、「设置」之前，插入「搜索」：

```python
MAIN_MENU_OPTIONS = [
    "用户管理",
    "会话管理",
    "预设管理",
    "开始对话",
    "搜索对话",
    "设置",
    "关于",
    "退出",
]
```

注意：新增了「搜索对话」后，后面的选项序号会变化。原来的「设置」是 choice==4，现在变成 choice==5。「关于」从 choice==5 变成 choice==6。「退出」从 choice==6 变成 choice==7。

**改动 2**：更新主菜单路由（因为序号变了 + 新增搜索路由）。

找到 run 方法里的路由部分（一串 elif），找到：

```python
            elif choice == 3:
                await start_chat(self)
            elif choice == 4:
                menu_view.show_settings_menu()
            elif choice == 5:
                menu_view.show_about()
            elif choice == 6:
                # 退出
                widgets.print_info("感谢使用，再见。")
                break
```

改为（新增搜索路由 choice==4，后面序号顺延）：

```python
            elif choice == 3:
                await start_chat(self)
            elif choice == 4:
                await self._search_messages()
            elif choice == 5:
                menu_view.show_settings_menu()
            elif choice == 6:
                menu_view.show_about()
            elif choice == 7:
                # 退出
                widgets.print_info("感谢使用，再见。")
                break
```

**改动 3**：会话管理子菜单新增「查看会话记录」选项。

找到文件顶部的 `SESSION_MENU_OPTIONS`：

```python
SESSION_MENU_OPTIONS = [
    "查看会话列表",
    "加载会话（设为当前）",
    "重命名会话",
    "删除会话",
    "返回主菜单",
]
```

在「删除会话」之后、「返回主菜单」之前，插入「查看会话记录」：

```python
SESSION_MENU_OPTIONS = [
    "查看会话列表",
    "加载会话（设为当前）",
    "重命名会话",
    "删除会话",
    "查看会话记录",
    "返回主菜单",
]
```

注意：新增后，「查看会话记录」是 choice==4，「返回主菜单」变成 choice==5。

**改动 4**：更新会话管理子菜单的路由 + 新增方法。

找到 `_show_session_menu` 方法里的路由部分：

```python
            if choice == -1 or choice == 4:
                # 返回主菜单
                return
            elif choice == 0:
                await self._list_sessions()
            elif choice == 1:
                await self._load_session()
            elif choice == 2:
                await self._rename_session()
            elif choice == 3:
                await self._delete_session()
```

改为（返回的 choice 变成 5，新增 choice==4 查看记录）：

```python
            if choice == -1 or choice == 5:
                # 返回主菜单
                return
            elif choice == 0:
                await self._list_sessions()
            elif choice == 1:
                await self._load_session()
            elif choice == 2:
                await self._rename_session()
            elif choice == 3:
                await self._delete_session()
            elif choice == 4:
                await self._view_session_messages()
```

然后在 app.py 的末尾（`_delete_session` 方法之后），追加以下 2 个方法：

```python
    # ── 会话记录查看与搜索（Step 9 实现）──────────────────────────────────

    async def _view_session_messages(self) -> None:
        """查看指定会话的全部聊天记录。"""
        if not self._require_login():
            return

        sessions = await self.session_manager.list_sessions(self.current_user.id)
        if not sessions:
            widgets.print_info("目前没有任何会话，无法查看记录")
            return

        # 显示会话列表供选择
        widgets.console.print("\n[bold]选择要查看的会话[/bold]")
        for i, s in enumerate(sessions, start=1):
            widgets.console.print(f"  {i}. {s.title}")
        widgets.console.print("  0. 取消")

        choice_str = widgets.read_text("请输入序号")
        try:
            choice = int(choice_str)
        except ValueError:
            widgets.print_error("请输入有效的数字")
            return

        if choice == 0:
            widgets.print_info("已取消")
            return
        if not (1 <= choice <= len(sessions)):
            widgets.print_error("序号超出范围")
            return

        selected = sessions[choice - 1]

        # 获取该会话的全部消息
        messages = await self.session_manager.get_session_messages(selected.id)
        if not messages:
            widgets.print_info(f"会话 '{selected.title}' 没有任何消息")
            return

        # 显示消息记录
        widgets.console.print(f"\n[bold]会话记录：{selected.title}（id={selected.id}）[/bold]")
        widgets.print_divider()
        for msg in messages:
            if msg.role == "human":
                role_label = "[bold cyan][你][/]  "
            elif msg.role == "ai":
                role_label = "[bold green][AI][/] "
            else:
                role_label = "[dim][系统][/][/] "		#此处会有bug，参考 5.2 中的操作3
            # 消息内容可能很长，直接显示
            widgets.console.print(f"{role_label}{msg.content}")
        widgets.print_divider()

        # 统计
        total = len(messages)
        total_tokens = selected.total_prompt_tokens + selected.total_completion_tokens
        widgets.print_info(f"共 {total} 条消息  |  累计 Token: {total_tokens}")

    async def _search_messages(self) -> None:
        """搜索对话（E1）：在当前用户的所有会话中按关键词搜索。"""
        if not self._require_login():
            return

        keyword = await self.get_user_input("请输入搜索关键词")
        if not keyword:
            widgets.print_warning("未输入关键词，取消搜索")
            return

        # 执行搜索
        results = await self.session_manager.search_messages(self.current_user.id, keyword)

        if not results:
            widgets.print_info(f"未找到包含「{keyword}」的消息")
            return

        # 获取所有涉及的会话（用于显示会话标题）
        sessions = await self.session_manager.list_sessions(self.current_user.id)
        session_map = {s.id: s for s in sessions}  # {session_id: Session}

        # 按 session_id 分组显示
        widgets.console.print(f"\n[bold]搜索「{keyword}」的结果（{len(results)} 条匹配）[/bold]")
        widgets.print_divider()

        current_session_id = None
        for msg in results:
            # 如果进入了新会话，先显示会话标题
            if msg.session_id != current_session_id:
                current_session_id = msg.session_id
                session = session_map.get(msg.session_id)
                title = session.title if session else f"会话id={msg.session_id}"
                widgets.console.print(f"\n[bold yellow]── 会话: {title} ──[/bold yellow]")

            # 显示消息
            if msg.role == "human":
                role_label = "[bold cyan][你][/]  "
            elif msg.role == "ai":
                role_label = "[bold green][AI][/] "
            else:
                role_label = "[dim][系统][/][/] "		#此处会有bug，参考 5.2 中的操作3
            widgets.console.print(f"{role_label}{msg.content}")

        widgets.print_divider()
        widgets.print_info(f"共 {len(results)} 条匹配，涉及会话 {len(set(m.session_id for m in results))} 个")
```

**设计说明**：

- `_view_session_messages`：让用户选一个会话，显示该会话的全部消息（按时间正序，标注角色）。
- `_search_messages`：输入关键词，搜索该用户的所有消息。结果按 session_id 分组显示（先显示会话标题，再显示该会话下的匹配消息）。用 `session_map`（字典）快速查找会话标题，避免每条消息都查一次。

#### 验证检查点 C：app.py 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from ui.tui.app import TUIApp; print('TUIApp OK:', TUIApp.__name__)"
```

预期输出：`TUIApp OK: TUIApp`

---

### 4.5 改造 config.yaml（更新进度文字）

文件路径：`langchain-chat/config.yaml`。

找到：

```yaml
  current_step: "Step 8  会话管理完善"
```

改为：

```yaml
  current_step: "Step 9  对话搜索"
```

---

## 五、整体运行验证

### 5.1 启动程序

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python src/main.py
```

启动后确认横幅显示「Step 9  对话搜索」。

### 5.2 验证操作

先准备数据：确保当前用户有几个会话，每个会话有几轮对话（如果没有，先去「开始对话」创建几个）。

**操作 1：验证 Bug 修复（模型名正确）**

- 创建一个新用户
- 列出用户
- 预期：模型显示的是 .env 里的 MODEL_NAME（如 qwen3.6-flash），不是 deepseek-chat

**操作 2：查看会话记录**

- 主菜单选 2（会话管理）
- 选 5（查看会话记录）
- 输入要查看的会话序号
- 预期：显示该会话的全部消息（按时间正序，标注「你」「AI」「系统」），底部显示消息数和 Token 统计

**操作 3：查看空会话的记录**

- 新建一个会话，**选预设时选 0（不使用预设）**，然后直接 /exit

- 选会话管理 → 查看会话记录 → 选这个空会话

- 预期：显示「会话 xxx 没有任何消息」

  **bug：崩溃，报错。**

  错误原因

  报错信息是 `MarkupError: closing tag '[/]' at position 12 has nothing to close`。

  问题出在 `_view_session_messages` 和 `_search_messages` 方法里，system 角色的 `role_label` 写错了：

  ```python
  # 错误写法（我文档里给的代码）
  role_label = "[dim][系统][/][/] "	
  ```

  这里有两个 `[/]`，但 Rich 的标记语法要求「开标签和闭标签配对」。`[dim]` 需要一个 `[/dim]` 来关闭，`[系统]` 不是合法的 Rich 标签（Rich 会把它当作样式标签解析）。所以 Rich 报错「[/] 没有对应的开标签」。

  当查看「空会话」时不会触发这个 bug（因为空会话没有消息，不进入循环）。但你的空会话实际上**不是真的空**——创建会话时如果选了预设，会保存一条 system 消息（预设的 system_prompt），所以查看到了一条 system 消息，触发了这个 Rich 标记错误。

  修复方案

  需要修改 app.py 里**两处** role_label 的写法（`_view_session_messages` 和 `_search_messages` 方法里都有）。

  找到 `_view_session_messages` 里的：

  ```python
              if msg.role == "human":
                  role_label = "[bold cyan][你][/]  "
              elif msg.role == "ai":
                  role_label = "[bold green][AI][/] "
              else:
                  role_label = "[dim][系统][/][/] "
  ```

  改为（修正 system 的标签）：

  ```python
              if msg.role == "human":
                  role_label = "[bold cyan][你][/]  "
              elif msg.role == "ai":
                  role_label = "[bold green][AI][/] "
              else:
                  role_label = "[dim][系统][/] "
  ```

  改动只有一处：`[dim][系统][/][/] `改为 `[dim][系统][/] `（去掉多余的 `[/]`）。

  同样，找到 `_search_messages` 里**完全相同**的那段代码，做同样的修改。

  **两处都要改**，改的内容一样：把 `[dim][系统][/][/] `改为 `[dim][系统][/] `。

**操作 4：搜索对话（有结果）**

- 主菜单选 5（搜索对话）
- 输入一个你知道存在于对话中的关键词（如「你好」或「Python」）
- 预期：显示匹配的消息，按会话分组，每组先显示会话标题，再显示匹配的消息
- 底部显示「共 N 条匹配，涉及会话 M 个」

**操作 5：搜索对话（无结果）**

- 选搜索对话
- 输入一个不可能存在的关键词（如「zzzzz」）
- 预期：显示「未找到包含 zzzzz 的消息」

**操作 6：空关键词搜索**

- 选搜索对话
- 直接回车（不输入关键词）
- 预期：显示「未输入关键词，取消搜索」

**操作 7：未登录时搜索**

- 重启程序，不登录
- 选搜索对话
- 预期：提示「请先在用户管理中创建或切换用户」

**操作 8：验证用户隔离（搜索）**

- 用户 A 对话几轮
- 切换到用户 B
- 选搜索对话，搜用户 A 对话里的关键词
- 预期：搜不到（用户 B 只能搜自己的消息）

**操作 9： 验证 关于**

* 进入主菜单，选择关于

* 预期：

  **bug：崩溃、退出**

  menu_view.py 里**没有 show_about 函数**

  原因

  报错 `module 'ui.tui.menu_view' has no attribute 'show_about'` 说明 menu_view.py 里缺少 `show_about` 函数。最可能的原因是： `show_about` 误删除

  修复方案

  在 menu_view.py 里补回 `show_about` 函数。在文件末尾追加：

  ```python
  def show_about() -> None:
      """显示关于信息。"""
      widgets.console.print(
          "\n[bold cyan]LangChain Chat[/bold cyan]  "
          "基于 LangChain 的多轮会话系统（教学项目）\n"
          "[dim]按步骤开发中[/dim]\n"
      )
      widgets.print_divider()
  ```

  

### 5.3 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 模型名正确 | 显示 .env 的 MODEL_NAME | Bug 修复生效 |
| 会话记录显示 | 显示全部消息，标注角色 | 会话记录功能可用 |
| 空会话提示 | 「没有任何消息」 | 边界处理正确 |
| 搜索有结果 | 显示匹配消息 + 会话标题 | 需求 E1 实现 |
| 搜索无结果 | 提示未找到 | 空结果处理正确 |
| 空关键词 | 取消搜索 | 边界处理正确 |
| 未登录保护 | 提示先登录 | 登录检查生效 |
| 用户隔离 | 搜不到别人的消息 | 需求 B4 实现 |

---

## 六、版本控制

### 6.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 修改：`src/core/session_manager.py`（新增 2 方法）、`src/ui/tui/app.py`（搜索 + 会话记录 + bug 修复）、`src/ui/tui/chat_view.py`（bug 修复）、`config.yaml`（current_step）
- 不应出现：`.env`、`data/`、`.venv/`

### 6.2 提交与打标签

```bash
git add .
git status
git commit -m "feat: step 9 - 对话搜索（E1）+ 查看会话记录 + 模型名 bug 修复"
git tag step-9-search
git push
git push origin step-9-search
git log --oneline -10
git tag
```

---

## 七、常见问题与排查

### 7.1 搜索相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 搜索无结果 | 关键词不存在于任何消息中 | 换个关键词，或先产生一些对话 |
| 搜索结果显示了别人的消息 | 用户隔离没生效 | 确认 search_messages 传了正确的 user_id |
| 搜索结果不显示会话标题 | session_map 没构建 | 确认 _search_messages 里有 session_map 逻辑 |

### 7.2 会话记录相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 显示「没有任何消息」 | 会话确实没对话过 | 先去对话产生消息 |
| 消息顺序不对 | list_messages 的排序 | 确认 backend 按 id 正序返回（Step 3 已实现） |

### 7.3 Bug 修复相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 模型名还是 deepseek-chat | 没改或改错了位置 | 确认 app.py 和 chat_view.py 都改了 |
| 旧用户的模型名不对 | 旧数据是 bug 时创建的 | 旧数据无法自动修复，删除旧用户重建 |

---

## 八、本步骤小结与知识清单

### 8.1 产出清单

| 类别 | 产出 |
|------|------|
| Bug 修复 | app.py + chat_view.py（模型名统一用 .env 的 MODEL_NAME） |
| 业务层新增 | session_manager.py（search_messages + get_session_messages） |
| 会话记录查看 | app.py（_view_session_messages） |
| 对话搜索 | app.py（_search_messages，需求 E1 实现） |
| 版本控制 | 提交 feat: step 9、标签 step-9-search |

### 8.2 知识清单

学完本步骤，应当掌握：

- 配置源一致性的重要性（两个配置源不一致会导致 bug）。
- 模糊搜索（LIKE 查询）的原理与应用。
- 搜索结果分组显示的设计（按 session_id 分组 + 会话标题）。
- 业务层封装存储层方法（保持不穿透原则）。
- Bug 根因分析方法（追溯数据来源，找出不一致）。

### 8.3 项目当前状态

```
langchain-chat @ step-9-search
对话搜索：已实现（需求 E1）
会话记录查看：已实现
Bug 修复：模型名统一用 .env 的 MODEL_NAME
桩函数替换进度：用户/预设/会话/对话/搜索已实现；设置仍是桩
下一步：Step 10 导出 + 模型切换
```

### 8.4 桩函数替换进度

| 菜单功能 | 状态 | 实现步骤 |
|---------|------|---------|
| 用户管理 | 已实现 | Step 4 |
| 预设管理 | 已实现 | Step 5 |
| 会话管理 | 已实现 | Step 7 + Step 8 |
| 开始对话 | 已实现 | Step 7 |
| 搜索对话 | **已实现** | Step 9 |
| 设置 | 桩函数 | Step 10 |

### 8.5 下一步预告

Step 10：导出（F1/F2）+ 模型切换（A5）。

目标：实现两个功能：

- 导出会话为 Markdown 文件（需求 F1/F2）。
- 运行时切换模型（需求 A5）：在设置菜单里修改默认模型，或在对话中切换模型。

---

> 本文档为 langchain-chat 项目 Step 9 的教学手册。按本文档操作，可修复模型名 bug 并实现对话搜索与会话记录查看。操作过程中如遇问题，可参考第七部分排查，或随时询问。
