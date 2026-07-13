# Step 8：会话管理完善（列表/重命名/删除/加载 + 分层重构）（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-26
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-8-session-mgmt`

---

## 阅读说明

本文档是 langchain-chat 项目第八步的完整教学手册。Step 7 实现了对话功能（核心里程碑），但会话管理只做了「新建、保存、加载、标题生成」。Step 8 的目标是：**完善会话管理的全部功能——列表、加载、重命名、删除，并修复分层架构的一个穿透问题。**

阅读并跟随操作后，你应当能够：

1. 理解会话管理完整功能的需求（C2~C5）。
2. 给 SessionManager 补充管理能力（列表/查询/重命名/删除）。
3. 实现会话管理子菜单（替换 Step 2 的桩函数）。
4. 修复 Step 7 的分层穿透问题（UI 不再直接访问 backend）。
5. 理解「业务能力下沉到 core，交互逻辑留在 UI」的分层原则。

**本文档的设计原则**（与前七步文档一致）：

- 每一个概念都用「3W1H」框架讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，由学习者自行创建文件并粘贴内容。
- 全面验证，及早发现问题。

**完成标志（学完本文档后你应达成的目标）**：

- SessionManager 新增 4 个方法（list_sessions / get_session / rename_session / delete_session）。
- 改造 app.py，新增会话管理子菜单（替换桩函数）。
- 修复 chat_view.py 的分层穿透（backend.list_sessions → session_manager.list_sessions）。
- 执行 `uv run python src/main.py`，能在 TUI 中查看会话列表、加载、重命名、删除。
- 本地 Git 仓库存在提交与标签 `step-8-session-mgmt`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置回顾](#二前置回顾)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、动手实践：完善与重构源码](#四动手实践完善与重构源码)
- [五、整体运行验证](#五整体运行验证)
- [六、版本控制](#六版本控制)
- [七、常见问题与排查](#七常见问题与排查)
- [八、本步骤小结与知识清单](#八本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

Step 7 实现了对话功能，但「会话管理」菜单（主菜单第 2 项）还是 Step 2 的桩函数——只显示一句「会话管理功能将在 Step 7、Step 8 实现」。Step 8 要把它替换为真实功能。

具体而言，本步骤做四件事：

1. 给 SessionManager 补充 4 个管理方法（list_sessions / get_session / rename_session / delete_session）。
2. 改造 app.py，新增会话管理子菜单（查看列表 / 加载 / 重命名 / 删除）。
3. 修复 chat_view.py 的分层穿透问题（不再直接访问 backend）。
4. 更新 menu_view.py，把 show_session_menu 桩函数的提示信息更新。

### 1.2 本步骤的特殊之处：修复分层穿透

Step 7 的 chat_view.py 有一行代码直接访问了存储层：

```python
# chat_view.py 第 42 行（有问题）
sessions = await app.session_manager.backend.list_sessions(app.current_user.id)
```

这行代码从 UI 层（chat_view）穿透业务层（session_manager），直接访问了存储层（backend）。这违反了分层架构的规则——UI 层应该只和业务层打交道，不直接碰存储层。

Step 8 会修复这个问题：在 SessionManager 新增 list_sessions 方法，chat_view 改为调用 `app.session_manager.list_sessions(...)`（通过业务层）。

### 1.3 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 7 的对话功能（标签 step-7-first-chat） |
| 输出 | 完整的会话管理功能（列表/加载/重命名/删除） |
| MVP 验证点 | 在 TUI 中查看会话列表、加载历史会话、重命名、删除 |

### 1.4 本步骤产出的文件

```
langchain-chat/
├── src/
│   ├── core/
│   │   └── session_manager.py       补充 4 个管理方法（改造）
│   ├── ui/tui/
│   │   ├── app.py                   新增会话管理子菜单（改造）
│   │   ├── chat_view.py             修复分层穿透（改造）
│   │   └── menu_view.py             更新桩函数提示（改造）
│   └── config.yaml                  current_step 改为 Step 8
```

共改造 5 个文件。无新建文件，无新依赖。

### 1.5 本步骤的设计决策（已确认）

| 决策 | 选择 | 理由 |
|------|------|------|
| SessionManager 新增方法 | list_sessions / get_session / rename_session / delete_session | 覆盖需求 C2~C5 |
| 会话管理子菜单 | 查看列表 / 加载 / 重命名 / 删除 / 返回 | 覆盖需求 C2~C5 |
| 删除安全检查 | 二次确认 + 删除当前会话时清空 current_session | 安全 + 状态一致 |
| 分层穿透修复 | chat_view 改为通过 session_manager 访问 | 保证 UI 不碰存储层 |
| current_session 留在哪 | 方案 B：留在 TUIApp（UI 状态），但操作通过 SessionManager | 务实，不过度设计 |

---

## 二、前置回顾

### 2.1 Step 7 回顾

| 已完成 | 结论 |
|--------|------|
| 对话功能 | 多轮流式对话完整可用（核心里程碑达成） |
| SessionManager | 核心能力已有（create_session / add_message / load_messages / generate_title / update_title） |
| 会话管理菜单 | **仍是桩函数**（本步骤替换） |
| 分层穿透 | chat_view 直接访问 backend（本步骤修复） |

### 2.2 SessionManager 当前能力清单

Step 7 完成后，SessionManager 已有的方法：

| 方法 | 功能 | Step 7 已实现 |
|------|------|-------------|
| create_session | 新建会话 | 是 |
| add_message | 保存消息 + 更新 Token | 是 |
| load_messages_as_langchain | 加载历史消息（转 LangChain 格式） | 是 |
| generate_title | LLM 摘要生成标题 | 是 |
| update_title | 修改标题 | 是 |
| **list_sessions** | 列出用户的所有会话 | **否（Step 8 新增）** |
| **get_session** | 按 id 查单个会话 | **否（Step 8 新增）** |
| **rename_session** | 重命名会话 | **否（Step 8 新增）** |
| **delete_session** | 删除会话及其消息 | **否（Step 8 新增）** |

Step 8 补充后 4 个方法，SessionManager 的能力就完整了。

### 2.3 本步骤不需要新依赖

复用前面步骤已安装的库，无需安装新库。

---

## 三、核心概念讲解（3W1H）

### 3.1 分层架构的「不穿透」原则

**What（是什么）**

分层架构有一条核心规则：**上层可以调用下层，但不能「跳过」中间层直接访问更下层。** 用「公司层级」来比喻：

```
总经理（UI 层）——只找——→ 部门经理（业务层）——只找——→ 一线员工（存储层）
```

总经理要办一件事，应该吩咐部门经理，由部门经理安排一线员工。总经理不应该越级直接指挥一线员工——否则部门经理被架空，管理混乱。

对应到本项目：

```
UI 层（app.py、chat_view.py）
    │ 只能调用业务层
    ▼
业务层（session_manager.py、user_manager.py 等）
    │ 只能调用存储层
    ▼
存储层（sqlite_backend.py）
```

UI 层（总经理）要操作数据，应该找业务层（部门经理），由业务层安排存储层（一线员工）执行。UI 层不该直接命令存储层。

**Why（为什么不能穿透——三个具体危害）**

以 Step 7 的穿透代码为例：

```python
# 穿透：UI 层直接访问存储层（反面教材）
sessions = await app.session_manager.backend.list_sessions(user_id)
```

危害一：**业务规则被绕过**

假如将来 SessionManager.list_sessions 要加一个业务规则——「不显示已归档的会话」。如果 UI 层通过 SessionManager 调用，这个规则会自动生效。但如果 UI 层穿透到 backend，就绕过了这个规则，归档会话还是会显示出来。

```
正确的调用链（业务规则生效）：
  UI 层 → session_manager.list_sessions() → 过滤已归档 → backend.list_sessions()

穿透的调用链（业务规则被绕过）：
  UI 层 → session_manager.backend.list_sessions()  ← 没过滤！
```

危害二：**耦合扩散（换存储层时 UI 也要改）**

UI 层穿透访问 backend，意味着 UI 层依赖了 SQLiteBackend 的具体实现。将来如果换 MySQL 后端：

```
不穿透（正确）：只改 storage 层，UI 层不用动
  UI 层 → session_manager → MySQLBackend（换了）

穿透（错误）：UI 层也要改
  UI 层 → session_manager.backend（这是 SQLiteBackend 特有的）→ 也要改
```

危害三：**职责混乱**

UI 层的职责是「显示和交互」，存储层的职责是「怎么存」。如果 UI 层直接访问存储层，UI 层就要关心「数据怎么存的」——这不是它该管的事。职责混乱会导致代码难维护、难测试。

**Which（什么情况算穿透）**

| 调用方式                                         | 是否穿透 | 说明                |
| ------------------------------------------------ | -------- | ------------------- |
| `app.session_manager.list_sessions(...)`         | 不穿透   | UI 通过业务层访问   |
| `app.session_manager.backend.list_sessions(...)` | **穿透** | UI 直接访问了存储层 |
| `app.user_manager.create_user(...)`              | 不穿透   | UI 通过业务层访问   |
| `app.backend.create_user(...)`                   | **穿透** | UI 直接访问了存储层 |

判断标准：**看是否出现了 `.backend.`**。如果 UI 层代码里出现了 `.backend.`，就是在穿透。

**How（本项目怎么落地）**

Step 8 做两件事来修复穿透：

1. SessionManager 新增 `list_sessions` 方法（封装 backend 的调用）。
2. chat_view 的调用从 `app.session_manager.backend.list_sessions` 改为 `app.session_manager.list_sessions`。

修复后的调用链：

```python
# 修复后（正确）：UI 层通过业务层访问
sessions = await app.session_manager.list_sessions(user_id)
```

SessionManager 内部：

```python
# SessionManager.list_sessions（业务层封装存储层）
async def list_sessions(self, user_id: int) -> list[Session]:
    return await self.backend.list_sessions(user_id)  # 这里访问 backend 是合法的
```

业务层访问存储层是合法的（相邻层调用），UI 层访问存储层才是不合法的（跨层穿透）。

### 3.2 会话的完整生命周期

**What（是什么）**

一个会话从创建到删除，经历以下阶段。每个阶段对应不同的操作和不同的步骤实现：

```
┌─────────────────────────────────────────────────────────────────────┐
│                     会话的生命周期                                    │
│                                                                     │
│  创建 ──→ 对话 ──→ 保存 ──→ 加载 ──→ 列表 ──→ 重命名 ──→ 删除       │
│  (C1)     (A1)     (C6)     (C2)     (C3)     (C4)      (C5)        │
│                                                                     │
│  Step 7   Step 7   Step 7   Step 7   Step 8   Step 8     Step 8      │
│  实现     实现     实现     实现     实现     实现       实现         │
└─────────────────────────────────────────────────────────────────────┘
```

每个阶段的详细说明：

| 阶段   | 操作                | 谁触发                                             | 用到的方法                                      | 实现步骤                          |
| ------ | ------------------- | -------------------------------------------------- | ----------------------------------------------- | --------------------------------- |
| 创建   | 新建一个空会话      | 用户选「开始对话」→「新建会话」                    | SessionManager.create_session                   | Step 7                            |
| 对话   | 用户和 LLM 多轮交流 | 用户输入消息                                       | ChatEngine.astream + SessionManager.add_message | Step 7                            |
| 保存   | 每轮对话存入数据库  | 每轮对话自动触发                                   | SessionManager.add_message                      | Step 7                            |
| 加载   | 回到旧会话继续      | 用户选「开始对话」→「继续」或「会话管理」→「加载」 | SessionManager.load_messages_as_langchain       | Step 7                            |
| 列表   | 查看所有历史会话    | 用户选「会话管理」→「查看列表」                    | SessionManager.list_sessions                    | Step 8                            |
| 重命名 | 修改会话标题        | 用户选「会话管理」→「重命名」或对话中输入 /rename  | SessionManager.rename_session                   | Step 7（/rename）+ Step 8（菜单） |
| 删除   | 删除会话及其消息    | 用户选「会话管理」→「删除」                        | SessionManager.delete_session                   | Step 8                            |

数据在各阶段的流动：

```
创建阶段：
  用户选预设 → SessionManager.create_session → backend.create_session → 数据库 sessions 表 +1 行

对话 + 保存阶段：
  用户输入 → ChatEngine.astream → LLM 回复
                ↓                    ↓
          SessionManager.add_message(human) → backend.add_message → messages 表 +1 行
          SessionManager.add_message(ai)     → backend.add_message → messages 表 +1 行

加载阶段：
  backend.list_messages → SessionManager.load_messages_as_langchain → 内存 messages 列表 → ChatEngine

列表阶段：
  backend.list_sessions → SessionManager.list_sessions → TUI 显示列表

删除阶段：
  SessionManager.delete_session → backend.delete_session
                                      ↓
                          数据库 sessions 表 -1 行
                          数据库 messages 表（CASCADE 自动清理该会话的所有消息）
```

**Why（为什么要完整管理）**

对话多了之后，会话列表会很长。用户需要：

- 查看有哪些会话（列表）。
- 回到某个旧会话继续聊（加载）。
- 给会话改个好认的名字（重命名）。
- 清理不需要的会话（删除）。

这些是「会话管理」的核心功能，需求 C2~C5 明确要求。

**How（本项目怎么实现）**

通过 SessionManager 的管理方法 + TUI 的会话管理子菜单实现。

### 3.3 删除会话的安全考虑

**What（是什么）**

删除会话是**不可逆操作**——会话及其所有消息都会被删除（数据库的 ON DELETE CASCADE 会自动清理消息）。所以需要格外谨慎。

**Why（为什么要谨慎）**

用户可能误操作（手滑选错），删除后无法恢复。所以需要：

1. **二次确认**：显示「确认删除？输入 yes」，用户必须明确输入 yes 才删除。
2. **删除当前会话的特殊处理**：如果删除的恰好是 current_session（当前正在用的会话），删除后要清空 current_session（避免引用已删除的数据）。

**How（本项目怎么实现）**

- 删除前显示会话标题，让用户确认删对了。
- 输入 yes 才执行删除。
- 如果删的是 current_session，删除后设 current_session = None。

---

## 四、动手实践：完善与重构源码

下面依次完成 5 个改动。全部代码由你亲手创建，我只在文档里给出内容。

> 文件位置约定：源码在 `src/` 下。文件编码统一 UTF-8（不带 BOM）。
>
> import 约定：相对于 src 目录。
>
> PyCharm 提示：创建文件时选「不添加」到 Git，最后统一 git add。

### 4.1 改造 src/core/session_manager.py（新增 4 个管理方法）

文件路径：`langchain-chat/src/core/session_manager.py`（Step 7 已创建，本步骤补充方法）。

在文件末尾（`_to_langchain_message` 方法之后），追加以下 4 个方法。**注意：不修改已有方法，只追加新方法。**

在文件末尾追加：

```python
    # ── 会话管理（Step 8 新增）──────────────────────────────────────────

    async def list_sessions(self, user_id: int) -> list[Session]:
        """列出指定用户的所有会话（C3 会话列表）。

        按更新时间倒序排列（最近更新的在最前面）。

        参数：
            user_id: 用户 ID
        返回：
            该用户的所有会话列表（按 id 倒序，最新的在前）
        """
        return await self.backend.list_sessions(user_id)

    async def get_session(self, session_id: int) -> Optional[Session]:
        """按 ID 查询单个会话（C2 加载历史会话）。

        参数：
            session_id: 会话 ID
        返回：
            Session 对象，或 None（不存在）
        """
        return await self.backend.get_session(session_id)

    async def rename_session(self, session_id: int, new_title: str) -> None:
        """重命名会话（C4 会话重命名）。

        参数：
            session_id: 会话 ID
            new_title: 新标题

        异常：
            ValueError: 标题为空 或 会话不存在
        """
        if not new_title or not new_title.strip():
            raise ValueError("标题不能为空")
        new_title = new_title.strip()

        session = await self.backend.get_session(session_id)
        if session is None:
            raise ValueError(f"会话 id={session_id} 不存在")

        session.title = new_title
        await self.backend.update_session(session)

    async def delete_session(self, session_id: int) -> None:
        """删除会话及其所有消息（C5 删除会话）。

        关联的消息靠数据库的 ON DELETE CASCADE 自动清理。

        参数：
            session_id: 会话 ID

        异常：
            ValueError: 会话不存在
        """
        session = await self.backend.get_session(session_id)
        if session is None:
            raise ValueError(f"会话 id={session_id} 不存在")

        await self.backend.delete_session(session_id)
```

**设计说明**：

- list_sessions：直接委托给 backend.list_sessions（存储层已有此能力）。这里封装一层是为了「不穿透」——UI 层调用 session_manager.list_sessions，而不是 session_manager.backend.list_sessions。
- get_session：同理，委托给 backend.get_session。
- rename_session：加了业务校验（标题非空、会话存在），校验通过后更新。
- delete_session：加了业务校验（会话存在），删除后消息靠 CASCADE 自动清理。

#### 验证检查点 A：SessionManager 新方法能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.session_manager import SessionManager; print('有 list_sessions:', hasattr(SessionManager, 'list_sessions')); print('有 get_session:', hasattr(SessionManager, 'get_session')); print('有 rename_session:', hasattr(SessionManager, 'rename_session')); print('有 delete_session:', hasattr(SessionManager, 'delete_session'))"
```

预期输出：

```
有 list_sessions: True
有 get_session: True
有 rename_session: True
有 delete_session: True
```

---

### 4.2 修复 src/ui/tui/chat_view.py（分层穿透修复）

文件路径：`langchain-chat/src/ui/tui/chat_view.py`（Step 7 已创建，本步骤修复一处穿透）。

找到第 42 行（start_chat 函数里，第 3.1 步）：

```python
        sessions = await app.session_manager.backend.list_sessions(app.current_user.id)
```

改为（通过业务层，不穿透）：

```python
        sessions = await app.session_manager.list_sessions(app.current_user.id)
```

**只改这一行**：把 `.backend.list_sessions` 改为 `.list_sessions`。这就是分层穿透的修复——UI 层改为通过业务层访问。

---

### 4.3 改造 src/ui/tui/app.py（新增会话管理子菜单）

文件路径：`langchain-chat/src/ui/tui/app.py`（Step 7 已改造，本步骤新增会话管理子菜单）。

这是本步骤改动最大的文件。主要变化：

1. 新增 SESSION_MENU_OPTIONS 常量（会话管理子菜单选项）。
2. 主菜单路由：会话管理（choice==1）改为调用 `self._show_session_menu()`。
3. 新增 `_show_session_menu` 方法（会话管理子菜单循环）。
4. 新增 `_list_sessions`、`_load_session`、`_rename_session`、`_delete_session` 四个方法。

**改动 1**：新增 SESSION_MENU_OPTIONS 常量。

在文件顶部（PRESET_MENU_OPTIONS 之后），加一段：

找到：

```python
# 预设管理子菜单选项
PRESET_MENU_OPTIONS = [
    "列出所有预设",
    "新增自定义预设",
    "编辑自定义预设",
    "删除自定义预设",
    "返回主菜单",
]
```

在其后面加：

```python
# 会话管理子菜单选项
SESSION_MENU_OPTIONS = [
    "查看会话列表",
    "加载会话（设为当前）",
    "重命名会话",
    "删除会话",
    "返回主菜单",
]
```

**改动 2**：主菜单路由，会话管理改为调用子菜单。

找到 run 方法里的：

```python
            elif choice == 1:
                menu_view.show_session_menu()
```

改为：

```python
            elif choice == 1:
                await self._show_session_menu()
```

**改动 3**：新增会话管理子菜单的 5 个方法。

在 app.py 里找到 `_delete_preset` 方法的末尾（预设管理子菜单之后），在其后面追加以下 5 个方法：

```python
    # ── 会话管理子菜单（Step 8 实现）──────────────────────────────────────

    async def _show_session_menu(self) -> None:
        """会话管理子菜单。"""
        if self.session_manager is None:
            widgets.print_error("会话管理未初始化（存储后端未注入）")
            return

        while True:
            widgets.print_divider()
            self._show_current_user()
            choice = await self.display_menu("会话管理", SESSION_MENU_OPTIONS)

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

    async def _list_sessions(self) -> None:
        """查看会话列表（C3）。"""
        if not self._require_login():
            return

        sessions = await self.session_manager.list_sessions(self.current_user.id)
        if not sessions:
            widgets.print_info("目前没有任何会话")
            return

        widgets.console.print("\n[bold]会话列表[/bold]")
        for i, s in enumerate(sessions, start=1):
            # 标记当前会话
            mark = " <- 当前" if (self.current_session and s.id == self.current_session.id) else ""
            # 格式化时间（只显示日期和时分）
            created = s.created_at.strftime("%Y-%m-%d %H:%M")
            updated = s.updated_at.strftime("%Y-%m-%d %H:%M")
            total_tokens = s.total_prompt_tokens + s.total_completion_tokens
            widgets.console.print(
                f"  {i}. [cyan]{s.title}[/cyan]{mark}"
            )
            widgets.console.print(
                f"     模型: {s.model_name}  |  创建: {created}  |  更新: {updated}  |  Token: {total_tokens}"
            )
        widgets.print_info(f"共 {len(sessions)} 个会话")

    async def _load_session(self) -> None:
        """加载会话（设为当前会话，C2）。"""
        if not self._require_login():
            return

        sessions = await self.session_manager.list_sessions(self.current_user.id)
        if not sessions:
            widgets.print_info("目前没有任何会话，无法加载")
            return

        # 显示列表供选择
        widgets.console.print("\n[bold]选择要加载的会话[/bold]")
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
        self.current_session = selected
        widgets.print_success(f"已加载会话: {selected.title}（id={selected.id}）")
        widgets.print_info("选择「开始对话」可继续此会话")

    async def _rename_session(self) -> None:
        """重命名会话（C4）。"""
        if not self._require_login():
            return

        sessions = await self.session_manager.list_sessions(self.current_user.id)
        if not sessions:
            widgets.print_info("目前没有任何会话，无法重命名")
            return

        # 显示列表供选择
        widgets.console.print("\n[bold]选择要重命名的会话[/bold]")
        for i, s in enumerate(sessions, start=1):
            widgets.console.print(f"  {i}. {s.title}")

        choice_str = widgets.read_text("请输入序号")
        try:
            choice = int(choice_str)
        except ValueError:
            widgets.print_error("请输入有效的数字")
            return

        if not (1 <= choice <= len(sessions)):
            widgets.print_error("序号超出范围")
            return

        selected = sessions[choice - 1]
        new_title = widgets.read_text("请输入新标题", default=selected.title)
        if not new_title:
            widgets.print_warning("标题不能为空")
            return

        try:
            await self.session_manager.rename_session(selected.id, new_title)
            widgets.print_success(f"会话已重命名为: {new_title}")
            # 如果改的是当前会话，更新 current_session 的标题
            if self.current_session and selected.id == self.current_session.id:
                self.current_session.title = new_title
        except ValueError as e:
            widgets.print_error(str(e))

    async def _delete_session(self) -> None:
        """删除会话（C5），需二次确认。"""
        if not self._require_login():
            return

        sessions = await self.session_manager.list_sessions(self.current_user.id)
        if not sessions:
            widgets.print_info("目前没有任何会话，无法删除")
            return

        # 显示列表供选择
        widgets.console.print("\n[bold]选择要删除的会话[/bold]")
        for i, s in enumerate(sessions, start=1):
            mark = " <- 当前" if (self.current_session and s.id == self.current_session.id) else ""
            widgets.console.print(f"  {i}. {s.title}{mark}")

        choice_str = widgets.read_text("请输入序号")
        try:
            choice = int(choice_str)
        except ValueError:
            widgets.print_error("请输入有效的数字")
            return

        if not (1 <= choice <= len(sessions)):
            widgets.print_error("序号超出范围")
            return

        selected = sessions[choice - 1]

        # 二次确认
        confirm = await self.get_user_input(f"确认删除会话 '{selected.title}'？此操作不可恢复。输入 yes 确认")
        if confirm.lower() != "yes":
            widgets.print_info("已取消删除")
            return

        try:
            await self.session_manager.delete_session(selected.id)
            widgets.print_success(f"会话 '{selected.title}' 已删除（含全部消息）")
            # 如果删的是当前会话，清空 current_session
            if self.current_session and selected.id == self.current_session.id:
                self.current_session = None
                widgets.print_info("已清空当前会话（因为删除的就是当前会话）")
        except ValueError as e:
            widgets.print_error(str(e))
```

**设计说明**：

- `_list_sessions`：显示会话列表（标题、模型、时间、Token），标记当前会话。未登录时提示先登录。
- `_load_session`：从列表选一个会话，设为 current_session。之后选「开始对话」就能继续这个会话。
- `_rename_session`：从列表选一个会话，输入新标题（支持回车保留原值——用了 Step 5 的 read_text 默认值功能）。如果改的是当前会话，同步更新 current_session.title。
- `_delete_session`：从列表选一个会话，二次确认后删除。如果删的是当前会话，删除后清空 current_session。

#### 验证检查点 B：app.py 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from ui.tui.app import TUIApp; print('TUIApp OK:', TUIApp.__name__)"
```

预期输出：`TUIApp OK: TUIApp`

---

### 4.4 改造 src/ui/tui/menu_view.py（更新桩函数提示）

文件路径：`langchain-chat/src/ui/tui/menu_view.py`（Step 2 创建，Step 4/5 没改过它）。

menu_view.py 里的 `show_session_menu` 还是 Step 2 的桩函数，但 Step 8 后它不再被调用了（app.py 改为调用 `self._show_session_menu()`）。为了保持代码整洁，把桩函数的提示更新一下。

找到 `show_session_menu`：

```python
def show_session_menu() -> None:
    """会话管理菜单（桩）。Step 7/8 实现。"""
    widgets.print_info("会话管理功能将在 Step 7、Step 8 实现")
    widgets.print_divider()
```

改为（说明已实现，此桩函数不再使用）：

```python
def show_session_menu() -> None:
    """会话管理菜单。

    注意：此函数在 Step 8 后不再被调用（app.py 改为调用 self._show_session_menu）。
    保留是为了兼容性。会话管理功能已在 app.py 的 _show_session_menu 实现。
    """
    widgets.print_info("请通过主菜单的「会话管理」访问此功能")
    widgets.print_divider()
```

---

### 4.5 改造 config.yaml（更新进度文字）

文件路径：`langchain-chat/config.yaml`。

找到：

```yaml
  current_step: "Step 7  对话视图（核心里程碑）"
```

改为：

```yaml
  current_step: "Step 8  会话管理完善"
```

---

## 五、整体运行验证

### 5.1 启动程序

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python src/main.py
```

启动后确认横幅显示「Step 8  会话管理完善」。

### 5.2 验证操作（手动在 TUI 里操作）

先准备数据：确保当前用户有几个会话（如果没有，先去「开始对话」创建几个）。

**操作 1：查看会话列表（C3）**

- 主菜单选 2（会话管理）
- 选 1（查看会话列表）
- 预期：显示该用户的所有会话（标题、模型、时间、Token），当前会话标记「<- 当前」

**操作 2：未登录时尝试会话管理**

- 切换到未登录状态（重启程序，不登录）
- 主菜单选 2（会话管理）
- 选 1（查看会话列表）
- 预期：提示「请先在用户管理中创建或切换用户」

**操作 3：加载会话（C2）**

- 登录用户
- 主菜单选 2（会话管理）
- 选 2（加载会话）
- 输入要加载的会话序号
- 预期：显示「已加载会话: xxx」「选择开始对话可继续此会话」
- （退出当前界面）然后选 4（开始对话），选「继续当前会话」，应该能接着这个会话继续聊

**操作 4：重命名会话（C4）**

- 主菜单选 2（会话管理）
- 选 3（重命名会话）
- 输入要重命名的会话序号
- 输入新标题（或回车保留原值）
- 预期：显示「会话已重命名为: xxx」
- 再选 1（查看列表），确认标题已改变

**操作 5：验证重命名当前会话的同步**

- 重命名「当前会话」（列表里标记了「<- 当前」的那个）
- 预期：重命名成功
- 然后选 4（开始对话），选「继续当前会话」，显示的标题应该是新标题

**操作 6：删除会话（C5）**

- 主菜单选 2（会话管理）
- 选 4（删除会话）
- 输入要删除的会话序号
- 输入 yes 确认
- 预期：显示「会话 xxx 已删除（含全部消息）」
- 再选 1（查看列表），确认该会话已消失

**操作 7：删除当前会话（验证清空逻辑）**

- 先加载一个会话设为当前
- 主菜单选 2（会话管理）→ 选 4（删除会话）→ 删除当前会话
- 输入 yes 确认
- 预期：显示「已删除」+「已清空当前会话（因为删除的就是当前会话）」
- 然后选 4（开始对话），预期会提示新建会话或加载历史（因为 current_session 已清空）

**操作 8：删除时输入非 yes（验证二次确认）**

- 选 4（删除会话）→ 选一个会话 → 输入 no（或任意非 yes 的内容）
- 预期：显示「已取消删除」，会话还在

**操作 9：验证用户隔离**

- 用户 A 创建几个会话
- 切换到用户 B
- 选 2（会话管理）→ 选 1（查看列表）
- 预期：用户 B 看到的是 B 自己的会话，看不到 A 的

### 5.3 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 会话列表显示 | 显示标题/模型/时间/Token | 需求 C3 实现 |
| 标记当前会话 | 当前会话有「<- 当前」标记 | 状态显示正确 |
| 未登录保护 | 提示先登录 | 登录检查生效 |
| 加载会话 | 设为 current_session，可继续对话 | 需求 C2 实现 |
| 重命名会话 | 标题改变，当前会话同步更新 | 需求 C4 实现 |
| 删除会话 | 删除成功，消息一并清理 | 需求 C5 实现 |
| 删除当前会话 | 清空 current_session | 状态一致性 |
| 二次确认 | 非 yes 不删除 | 安全机制 |
| 用户隔离 | 不同用户看到各自的会话 | 需求 B4 实现 |
| 分层穿透修复 | chat_view 不再访问 backend | 分层架构正确 |

---

## 六、版本控制

### 6.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 修改：`src/core/session_manager.py`（新增 4 方法）、`src/ui/tui/app.py`（会话子菜单）、`src/ui/tui/chat_view.py`（穿透修复）、`src/ui/tui/menu_view.py`（桩函数更新）、`config.yaml`（current_step）
- 不应出现：`.env`、`data/`、`.venv/`

### 6.2 提交与打标签

```bash
git add .
git status
git commit -m "feat: step 8 - 会话管理完善（列表/加载/重命名/删除）与分层穿透修复"
git tag step-8-session-mgmt
git push
git push origin step-8-session-mgmt
git log --oneline -9
git tag
```

---

## 七、常见问题与排查

### 7.1 会话列表相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 列表为空 | 当前用户确实没有会话 | 先去「开始对话」创建几个 |
| 列表显示了别人的会话 | 用户隔离没生效 | 确认 _switch_user 里有 current_session = None |
| 时间显示异常 | 时区问题（UTC 存储） | 当前阶段正常，显示的是 UTC 时间 |

### 7.2 加载/重命名/删除相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 加载后对话还是旧的 | current_session 没更新 | 确认 _load_session 里有 self.current_session = selected |
| 重命名后当前会话标题没变 | 没同步更新 current_session | 确认 _rename_session 里有同步逻辑 |
| 删除后程序报错 | 删的是当前会话但没清空 | 确认 _delete_session 里有清空逻辑 |
| 删除时报「会话不存在」 | session_id 输错 | 先查看列表确认 |

### 7.3 分层穿透相关

| 现象 | 原因 | 解决 |
|------|------|------|
| chat_view 报 AttributeError | 还在用 .backend.list_sessions | 改为 .list_sessions（通过业务层） |

---

## 八、本步骤小结与知识清单

### 8.1 产出清单

| 类别 | 产出 |
|------|------|
| 业务层完善 | src/core/session_manager.py（新增 list/get/rename/delete 4 个方法） |
| 会话管理子菜单 | src/ui/tui/app.py（_list/_load/_rename/_delete_session） |
| 分层修复 | src/ui/tui/chat_view.py（穿透修复） |
| 桩函数更新 | src/ui/tui/menu_view.py |
| 版本控制 | 提交 feat: step 8、标签 step-8-session-mgmt |

### 8.2 知识清单

学完本步骤，应当掌握：

- 分层架构的「不穿透」原则（UI 层不直接访问存储层）。
- 会话的完整生命周期（创建→对话→保存→加载→列表→重命名→删除）。
- 删除操作的安全考虑（二次确认、删除当前会话时清空状态）。
- 业务能力与交互逻辑的区分（core 提供「做什么」，UI 决定「怎么做」）。
- SessionManager 的完整能力清单（9 个方法）。

### SessionManager 完整方法清单（Step 8 后）

| 序号 | 方法                         | 功能                              | 实现步骤 | 调用方                        |
| ---- | ---------------------------- | --------------------------------- | -------- | ----------------------------- |
| 1    | `create_session`             | 新建会话（C1）                    | Step 7   | chat_view                     |
| 2    | `add_message`                | 保存消息 + 更新 Token 统计（C6）  | Step 7   | chat_view                     |
| 3    | `load_messages_as_langchain` | 加载历史消息（转 LangChain 格式） | Step 7   | chat_view                     |
| 4    | `generate_title`             | LLM 摘要生成标题（C7）            | Step 7   | chat_view                     |
| 5    | `update_title`               | 修改会话标题                      | Step 7   | chat_view（/rename）          |
| 6    | `list_sessions`              | 列出用户的所有会话（C3）          | Step 8   | chat_view + app（会话子菜单） |
| 7    | `get_session`                | 按 id 查单个会话（C2）            | Step 8   | app（会话子菜单）             |
| 8    | `rename_session`             | 重命名会话（C4）                  | Step 8   | app（会话子菜单）             |
| 9    | `delete_session`             | 删除会话及其消息（C5）            | Step 8   | app（会话子菜单）             |

这 9 个方法分为两组：

| 分组                   | 方法                                                         | 说明                             |
| ---------------------- | ------------------------------------------------------------ | -------------------------------- |
| **对话能力**（Step 7） | create_session、add_message、load_messages_as_langchain、generate_title、update_title | 支撑「和 LLM 对话」这个核心功能  |
| **管理能力**（Step 8） | list_sessions、get_session、rename_session、delete_session   | 支撑「管理历史会话」这个辅助功能 |

**对应的需求覆盖**：

| 需求编号 | 需求内容         | 由哪个方法实现                           |
| -------- | ---------------- | ---------------------------------------- |
| C1       | 新建会话         | create_session                           |
| C2       | 加载历史会话     | get_session + load_messages_as_langchain |
| C3       | 会话列表         | list_sessions                            |
| C4       | 会话重命名       | rename_session + update_title            |
| C5       | 删除会话         | delete_session                           |
| C6       | 会话自动保存     | add_message                              |
| C7       | 会话标题自动生成 | generate_title                           |

需求 C1~C7 全部覆盖，会话管理功能完整。

### 8.3 项目当前状态

```
langchain-chat @ step-8-session-mgmt
会话管理：完整可用（列表/加载/重命名/删除/对话中新建/标题生成）
桩函数替换进度：用户、预设、开始对话、会话管理已实现；设置仍是桩
下一步：Step 9 对话搜索（关键词搜索历史消息）
```

### 8.4 桩函数替换进度

| 菜单功能 | 状态 | 实现步骤 |
|---------|------|---------|
| 用户管理 | 已实现 | Step 4 |
| 预设管理 | 已实现 | Step 5 |
| 会话管理 | **已实现** | Step 7（对话）+ Step 8（列表/加载/重命名/删除） |
| 开始对话 | 已实现 | Step 7（核心里程碑） |
| 设置 | 桩函数 | Step 10 |

### 8.5 下一步预告

Step 9：对话搜索（在历史消息中按关键词搜索）。

目标：实现需求 E1（对话搜索）——在当前用户的所有历史会话中按关键词搜索消息内容，展示匹配的消息及其所属会话。

核心技术：SQLiteBackend.search_messages（Step 3 已实现 LIKE 模糊查询）、搜索结果展示。

---

> 本文档为 langchain-chat 项目 Step 8 的教学手册。按本文档操作，可完善会话管理的全部功能。操作过程中如遇问题，可参考第七部分排查，或随时询问。
