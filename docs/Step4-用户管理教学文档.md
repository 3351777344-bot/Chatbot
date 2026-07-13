# Step 4：用户管理模块与 TUI 用户菜单（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-25
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-4-user-mgmt`

---

## 阅读说明

本文档是 langchain-chat 项目第四步的完整教学手册。阅读并跟随操作后，你应当能够：

1. 理解「业务层」在分层架构中的角色，以及它如何衔接存储层与界面层。
2. 掌握数据在「界面层 → 业务层 → 存储层」之间的完整流动过程。
3. 掌握 UserManager 业务管理器的设计与实现。
4. 理解 try/except 异常处理在业务错误友好提示中的作用。
5. 理解「当前用户状态」如何在整个应用中维护。
6. 把 Step 2 的桩函数替换为真实功能，完成第一个完整的「端到端」功能。

**本文档的设计原则**（与 Step 1 至 Step 3 文档一致）：

- 每一个概念都用「3W1H」框架讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，由学习者自行创建文件并粘贴内容。
- 每完成若干文件后设有「验证检查点」，便于及时发现问题。

**完成标志（学完本文档后你应达成的目标）**：

- 新增 `src/core/user_manager.py`（用户管理业务层）。
- 改造 `src/ui/tui/app.py`（实现用户管理子菜单，替换桩函数）。
- 改造 `src/main.py`（启动时初始化存储后端并注入 TUIApp）。
- 执行 `uv run python src/main.py`，能在 TUI 中创建、列出、切换、删除用户，数据持久化到 SQLite。
- 本地 Git 仓库存在提交与标签 `step-4-user-mgmt`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置回顾](#二前置回顾)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、动手实践：创建与改造源码](#四动手实践创建与改造源码)
- [五、整体运行验证](#五整体运行验证)
- [六、版本控制](#六版本控制)
- [七、常见问题与排查](#七常见问题与排查)
- [八、本步骤小结与知识清单](#八本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

前三步我们分别建立了：存储层接口（Step 2 base.py）、存储层实现（Step 3 sqlite_backend.py）、界面骨架（Step 2 TUI 菜单）。但它们彼此是**断开**的——界面里的菜单只是桩函数（显示一句提示），存储层的代码只能通过 init_db.py 单独测试，两者没有连通。

Step 4 的目标是：**把断开的层连起来，实现第一个完整的端到端功能——用户管理。**

具体而言，本步骤做四件事：

1. 新建业务层 `UserManager`（core/user_manager.py），封装用户管理的业务逻辑。
2. 改造 `app.py`，实现用户管理子菜单（创建/列出/切换/删除），替换 Step 2 的桩函数。
3. 改造 `main.py`，启动时初始化存储后端，并把它注入 TUIApp。
4. 在 TUI 中验证全部用户管理功能，数据真正存入 SQLite。

### 1.2 本步骤的特殊意义

Step 4 是一个重要转折点。从这一步开始：

- 数据真正在「界面层 → 业务层 → 存储层」之间流动。
- 桩函数开始被真实功能替换（Step 2 的 show_user_menu 退役）。
- 应用开始有「状态」（当前登录用户）。

这是整个项目第一次出现「完整的业务功能」——之前的步骤都在搭建骨架，从 Step 4 起开始实现具体功能。

### 1.3 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 3 完成的 SQLite 存储后端（标签 step-3-sqlite） |
| 输出 | 用户管理完整功能（业务层 + 界面层 + 持久化） |
| MVP 验证点 | 在 TUI 中创建、列出、切换、删除用户，重启程序后数据仍在 |

### 1.4 本步骤产出的文件

```
langchain-chat/
├── src/
│   ├── core/
│   │   └── user_manager.py        用户管理业务层（新建）
│   ├── ui/tui/
│   │   └── app.py                 主应用（改造：用户管理子菜单）
│   └── main.py                    程序入口（改造：初始化存储后端）
```

共新建 1 个文件，改造 2 个文件。无新依赖（复用前三步的库）。

### 1.5 本步骤的设计决策（已确认）

| 决策 | 选择 | 理由 |
|------|------|------|
| UserManager 与 TUI 的交互方式 | 异步（async） | 与项目全链路异步一致（需求 A3） |
| 当前用户状态管理 | 放在 TUIApp 类的 current_user 属性 | 状态集中在应用层，清晰可控 |
| 功能范围 | 实现 B1（创建）/B2（切换）/B3（删除），加「列出用户」辅助功能，B4（隔离）通过 user_id 过滤天然保证 | 覆盖需求，切换/删除需要先列出 |
| 验证方式 | 在 TUI 里手动操作验证 | 符合 MVP「能在 TUI 中操作」的描述 |
| 是否改造 main.py | 改造，启动时初始化存储后端并注入 TUIApp | 否则 TUI 操作时数据库未就绪会报错 |

---

## 二、前置回顾

### 2.1 Step 3 回顾

| 已完成 | 结论 |
|--------|------|
| 存储层实现 | SQLiteBackend 实现了全部 20 个方法，可建库建表、增删改查 |
| 工厂模式 | StorageFactory.create("sqlite") 返回 SQLiteBackend 实例 |
| 数据库初始化 | init_db.py 能建库并通过冒烟测试 |
| 当前短板 | 存储层与界面层断开，TUI 菜单还是桩函数 |

### 2.2 本步骤不需要新依赖

Step 4 复用前三步已安装的全部库（pydantic、aiosqlite、rich、prompt_toolkit 等），无需安装新库。

---

## 三、核心概念讲解（3W1H）

本步骤涉及四个核心概念，逐个讲解。

### 3.1 业务层（core）的角色

**What（是什么）**

业务层是分层架构中「负责业务逻辑」的那一层，位于存储层和界面层之间。它封装了「用户管理的规则」（如用户名必须唯一、删除要二次确认），让界面层不直接碰数据库，让存储层不关心业务规则。

**Why（为什么需要业务层）**

如果没有业务层，界面层会直接调用存储层，像这样：

```python
# 没有业务层的反面教材（界面层直接碰存储层）
async def create_user():
    username = input("用户名: ")
    # 界面层里写满了业务规则和错误处理，混乱
    existing = await backend.get_user_by_name(username)
    if existing:
        print("用户名已存在")
        return
    user = User(id=0, username=username)
    await backend.create_user(user)
    print("创建成功")
```

问题：业务规则（用户名唯一、参数校验、错误处理）散落在界面代码里，与显示逻辑搅在一起。如果将来加 WebUI，这些规则要在 WebUI 里再写一遍。

有了业务层后，界面层只管「获取输入 + 显示结果」，业务规则集中在 UserManager 里：

```python
# 有业务层的正确做法
async def create_user():
    username = input("用户名: ")
    try:
        user = await user_manager.create_user(username)   # 业务规则在 UserManager 内部
        print("创建成功")
    except ValueError as e:
        print(e)    # 友好显示业务错误
```

业务规则只写一次（在 UserManager 里），TUI 和未来 WebUI 都复用。

**Which（业务层与存储层的职责边界）**

| 层 | 职责 | 不做什么 |
|----|------|---------|
| 存储层（storage） | 怎么存、怎么取（SQL） | 不管业务规则（如用户名是否唯一） |
| 业务层（core） | 业务规则、参数校验、错误处理 | 不管 SQL 怎么写、数据存哪 |
| 界面层（ui） | 显示什么、获取什么输入 | 不管业务规则、不管 SQL |

举例区分：用户名唯一校验属于业务层（这是业务规则），而 `username TEXT UNIQUE NOT NULL`（数据库约束）属于存储层（这是数据保护）。业务层主动校验是为了「给用户友好提示」，存储层的约束是「最后防线」（防止业务层漏判时数据出错）。

**How（本项目怎么落地）**

在 `core/user_manager.py` 定义 `UserManager` 类，构造时接收一个 StorageBackend 实例，所有方法通过这个实例操作数据。TUIApp 持有 UserManager 实例，调用它的方法完成业务操作。

### 3.2 数据在三层之间的流动（本步骤最重要的概念）

Step 4 第一次让数据真正在三层之间流动。以「创建用户」为例，追踪一次完整的数据流动：

```
用户在 TUI 输入用户名 "alice"
        │
        ▼
┌─────────────────────────────────────┐
│ 界面层（app.py 的 _create_user）     │  ① 获取输入：username = "alice"
│                                     │  ④ 显示结果：「创建成功」或「用户名已存在」
└────────────────┬────────────────────┘
                 │ ② 调用业务层
                 ▼
┌─────────────────────────────────────┐
│ 业务层（UserManager.create_user）    │  ③ 校验：用户名非空？是否已存在？
│                                     │  ⑤ 通过则构造 User 对象，交给存储层
└────────────────┬────────────────────┘
                 │ ⑥ 调用存储层
                 ▼
┌─────────────────────────────────────┐
│ 存储层（SQLiteBackend.create_user）  │  ⑦ 执行 INSERT INTO users ...
│                                     │  ⑧ 返回含分配 id 的 User
└────────────────┬────────────────────┘
                 │ ⑨ 数据落盘
                 ▼
            data/sqlite/app.db（users 表多了一行）
```

关键理解：每一层只和相邻的层通信。

- 界面层不知道有 SQLite（它只知道调用 UserManager）。
- 业务层不知道有 app.db 文件（它只知道调用 backend）。
- 存储层不知道有 TUI（它只接收 User 对象，存进去）。

这种「相邻通信、互不知晓」就是分层架构的核心价值——任何一层都可以被替换，不影响其他层。

### 3.3 异常处理（try/except）

**What（是什么）**

异常处理是 Python 处理错误的机制。`try` 块里放「可能出错的代码」，`except` 块里放「出错后怎么处理」。

**Why（为什么需要）**

用户管理中有很多会出错的情况：用户名重复、用户名为空、用户不存在等。如果不处理异常，程序会崩溃并显示一堆英文报错（用户体验差）。用 try/except 捕获后，可以显示友好的中文提示。

**How（本项目的用法）**

业务层在出错时抛出 `ValueError`（携带中文错误信息），界面层用 try/except 捕获并显示：

```python
# 业务层（UserManager）：主动抛出异常
if existing is not None:
    raise ValueError(f"用户名 '{username}' 已存在")

# 界面层（app.py）：捕获并显示
try:
    user = await self.user_manager.create_user(username)
    widgets.print_success("创建成功")
except ValueError as e:
    widgets.print_error(str(e))    # 显示「用户名 'alice' 已存在」
```

这是「业务层抛异常、界面层处理异常」的标准模式。

### 3.4 应用状态管理（当前用户）

**What（是什么）**

用户管理涉及「当前登录用户」的概念。切换用户后，后续操作（对话、查会话）都基于当前用户。这个「当前是谁」就是应用状态。

**Why（为什么需要状态）**

没有状态的话，每次操作都要先问「你是谁」，体验很差。维护 current_user 后，程序记住当前用户，直到切换或退出。

**How（本项目怎么管理）**

状态放在 TUIApp 的 `self.current_user` 属性里。Step 2 预留了这个属性（初始为 None），Step 4 正式使用它：

- 创建用户后，如果当前未登录，自动切换为新用户（首次使用体验）。
- 切换用户时，更新 current_user。
- 删除用户时，不允许删除当前用户（避免状态失效）。
- 主菜单顶部显示当前用户（让用户始终知道自己在操作谁的数据）。

---

## 四、动手实践：创建与改造源码

下面依次创建 1 个新文件，改造 2 个文件。每个文件给出完整内容与讲解。

> 文件位置约定：源码在 `src/` 下。文件编码统一 UTF-8（不带 BOM）。
>
> import 约定：相对于 src 目录（如 `from core.user_manager import UserManager`）。
>
> PyCharm 提示：创建文件时如果弹出「是否加入 Git 追踪」，选「不添加」，最后统一 git add。

### 4.1 创建 src/core/user_manager.py（业务层）

文件路径：`langchain-chat/src/core/user_manager.py`。

这是用户管理的业务层，封装创建、查询、列出、删除等业务逻辑。

**设计说明**：

- 构造时接收 StorageBackend 实例（依赖注入），不直接 new 具体后端。
- create_user 内部做参数校验（非空）和业务规则校验（用户名唯一），出错抛 ValueError。
- 所有方法都是 async，与存储层异步一致。

**关于依赖注入**：UserManager 不自己创建存储后端，而是由外部（main.py）创建后「注入」进来。好处是 UserManager 不绑定具体后端，换 MySQL 时 UserManager 一行都不用改。

**文件内容**：

```python
"""用户管理业务层。

封装用户相关的业务逻辑：创建、查询、切换、删除。
对应需求文档 B1 至 B4（用户管理）。

设计说明：
    - UserManager 不直接操作数据库，而是依赖 StorageBackend 抽象。
    - 这样切换存储后端时，UserManager 无需修改。
    - 业务层负责：参数校验、错误处理、业务规则（如用户名唯一）。
"""

from typing import Optional

from models.schemas import User
from storage.base import StorageBackend


class UserManager:
    """用户管理器。

    通过传入的 StorageBackend 实例操作数据。
    使用方式：
        mgr = UserManager(backend)
        user = await mgr.create_user("alice")
    """

    def __init__(self, backend: StorageBackend):
        self.backend = backend

    async def create_user(self, username: str, default_model: Optional[str] = None) -> User:
        """创建用户（B1）。用户名唯一校验。

        参数：
            username: 用户名
            default_model: 默认模型（可选）
        返回：
            创建后的 User
        异常：
            ValueError: 用户名为空 或 用户名已存在
        """
        # 参数校验：用户名非空
        if not username or not username.strip():
            raise ValueError("用户名不能为空")
        username = username.strip()

        # 业务规则：用户名唯一
        existing = await self.backend.get_user_by_name(username)
        if existing is not None:
            raise ValueError(f"用户名 '{username}' 已存在")

        # 创建
        user = User(id=0, username=username, default_model=default_model)
        return await self.backend.create_user(user)

    async def get_user(self, username: str) -> Optional[User]:
        """按用户名查询用户。不存在返回 None。"""
        return await self.backend.get_user_by_name(username)

    async def list_users(self) -> list[User]:
        """列出所有用户。"""
        return await self.backend.list_users()

    async def delete_user(self, user_id: int) -> None:
        """删除用户（B3）。关联数据靠 CASCADE 自动清理。"""
        await self.backend.delete_user(user_id)

    async def user_exists(self, username: str) -> bool:
        """判断用户名是否存在。"""
        return await self.get_user(username) is not None
```

#### 验证检查点 A：UserManager 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.user_manager import UserManager; print('UserManager OK:', UserManager.__name__)"
```

预期输出：`UserManager OK: UserManager`

---

### 4.2 改造 src/ui/tui/app.py（实现用户管理子菜单）

文件路径：`langchain-chat/src/ui/tui/app.py`（Step 2 已创建，本步骤大幅改造）。

这是本步骤改动最大的文件。主要变化：

1. TUIApp 构造时接收 backend 参数，并据此创建 UserManager。
2. 新增「用户管理子菜单」（`_show_user_menu`），含创建/列出/切换/删除四个功能。
3. 主菜单顶部显示当前用户状态。
4. 主菜单的路由：用户管理（choice==0）改为调用 `self._show_user_menu()`。

**改造后的完整文件内容**（替换 Step 2 的 app.py 全部内容）：

```python
"""TUI 主应用（菜单路由、状态管理）。

这是 TUI 的主入口，负责：
    1. 显示启动横幅。
    2. 显示主菜单并路由到对应视图。
    3. 维护主循环（直到用户选择退出）。

Step 4 新增：
    - 持有存储后端与各业务管理器（UserManager 等）。
    - 实现用户管理子菜单（创建/列出/切换/删除）。
    - 维护当前登录用户状态。

TUIApp 继承 AbstractUI，实现其全部抽象方法，满足 UI 接口契约。
"""

import platform

from core.config_manager import get_config
from core.user_manager import UserManager
from interface.ui_protocol import AbstractUI
from storage.factory import StorageFactory
from ui.tui import menu_view, widgets
from ui.tui.chat_view import start_chat

# 主菜单选项（序号与选项的对应关系）
MAIN_MENU_OPTIONS = [
    "用户管理",
    "会话管理",
    "预设管理",
    "开始对话",
    "设置",
    "关于",
    "退出",
]

# 用户管理子菜单选项
USER_MENU_OPTIONS = [
    "创建用户",
    "列出所有用户",
    "切换当前用户",
    "删除用户",
    "返回主菜单",
]


class TUIApp(AbstractUI):
    """TUI 主应用。

    继承 AbstractUI 并实现其全部抽象方法。
    """

    def __init__(self, backend=None) -> None:
        # 存储后端（由 main.py 注入）
        self.backend = backend
        # 业务管理器（backend 注入后初始化）
        self.user_manager: UserManager = None
        if backend is not None:
            self.user_manager = UserManager(backend)

        # 应用状态
        self.current_user = None          # 当前登录用户（User 对象或 None）
        self.current_session = None       # 当前会话（Step 7 起使用）

    # ── AbstractUI 接口实现 ───────────────────────────────────────────────

    async def display_message(self, role: str, content: str) -> None:
        """显示一条消息。"""
        if role == "human":
            widgets.console.print(f"[bold cyan][你][/] {content}")
        elif role == "ai":
            widgets.console.print(f"[bold green][AI][/] {content}")
        else:
            widgets.console.print(f"[dim][系统][/] {content}")

    async def get_user_input(self, prompt_text: str = "") -> str:
        """获取用户输入。"""
        return widgets.read_text(prompt_text)

    async def display_menu(self, title: str, options: list[str]) -> int:
        """显示菜单并获取选择。"""
        widgets.print_menu(title, options)
        return widgets.read_choice(len(options))

    async def display_error(self, message: str) -> None:
        """显示错误。"""
        widgets.print_error(message)

    async def display_info(self, message: str) -> None:
        """显示提示。"""
        widgets.print_info(message)

    # ── 辅助：显示当前用户状态 ────────────────────────────────────────────

    def _show_current_user(self) -> None:
        """在菜单顶部显示当前登录用户。"""
        if self.current_user:
            widgets.console.print(
                f"[dim]当前用户: [bold yellow]{self.current_user.username}[/bold yellow]"
                f"（id={self.current_user.id}）[/dim]"
            )
        else:
            widgets.console.print("[dim]当前用户: 未登录[/dim]")

    # ── 主循环 ────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """启动 TUI 主循环。

        流程：打印横幅 → 显示主菜单 → 读取选择 → 路由 → 循环。
        """
        # 1. 打印启动横幅
        widgets.print_banner(version="0.1.0", python_version=platform.python_version())

        # 2. 主循环
        while True:
            # 显示当前用户状态
            self._show_current_user()

            # 显示主菜单
            choice = await self.display_menu("主菜单", MAIN_MENU_OPTIONS)

            # 路由到对应视图
            if choice == -1:
                # 用户输入 0（返回上层），在主菜单中等同于不做操作
                continue
            elif choice == 0:
                await self._show_user_menu()
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
                # 退出
                widgets.print_info("感谢使用，再见。")
                break

    # ── 用户管理子菜单（Step 4 实现）──────────────────────────────────────

    async def _show_user_menu(self) -> None:
        """用户管理子菜单。"""
        if self.user_manager is None:
            widgets.print_error("用户管理未初始化（存储后端未注入）")
            return

        while True:
            widgets.print_divider()
            self._show_current_user()
            choice = await self.display_menu("用户管理", USER_MENU_OPTIONS)

            if choice == -1 or choice == 4:
                # 返回主菜单
                return
            elif choice == 0:
                await self._create_user()
            elif choice == 1:
                await self._list_users()
            elif choice == 2:
                await self._switch_user()
            elif choice == 3:
                await self._delete_user()

    async def _create_user(self) -> None:
        """创建用户（B1）。"""
        username = await self.get_user_input("请输入新用户名")
        if not username:
            widgets.print_warning("未输入用户名，取消创建")
            return
        try:
            # 默认模型用配置里的默认值
            config = get_config()
            user = await self.user_manager.create_user(
                username, default_model=config.default_model
            )
            widgets.print_success(f"用户创建成功: {user.username}（id={user.id}）")
            # 创建后自动切换为当前用户（首次使用体验更好）
            if self.current_user is None:
                self.current_user = user
                widgets.print_info(f"已自动切换为当前用户: {user.username}")
        except ValueError as e:
            widgets.print_error(str(e))

    async def _list_users(self) -> None:
        """列出所有用户。"""
        users = await self.user_manager.list_users()
        if not users:
            widgets.print_info("目前没有任何用户")
            return

        widgets.console.print("\n[bold]用户列表[/bold]")
        for u in users:
            # 标记当前用户
            mark = " <- 当前" if (self.current_user and u.id == self.current_user.id) else ""
            widgets.console.print(
                f"  id={u.id}  用户名=[cyan]{u.username}[/cyan]"
                f"  模型={u.default_model or '默认'}{mark}"
            )
        widgets.print_info(f"共 {len(users)} 个用户")

    async def _switch_user(self) -> None:
        """切换当前用户（B2）。"""
        username = await self.get_user_input("请输入要切换到的用户名")
        if not username:
            widgets.print_warning("未输入用户名，取消切换")
            return

        user = await self.user_manager.get_user(username)
        if user is None:
            widgets.print_error(f"用户 '{username}' 不存在")
            return

        self.current_user = user
        widgets.print_success(f"已切换到用户: {user.username}（id={user.id}）")

    async def _delete_user(self) -> None:
        """删除用户（B3），需二次确认。"""
        username = await self.get_user_input("请输入要删除的用户名")
        if not username:
            widgets.print_warning("未输入用户名，取消删除")
            return

        user = await self.user_manager.get_user(username)
        if user is None:
            widgets.print_error(f"用户 '{username}' 不存在")
            return

        # 安全检查：不允许删除当前登录的用户
        if self.current_user and user.id == self.current_user.id:
            widgets.print_warning("不允许删除当前正在登录的用户，请先切换到其他用户")
            return

        # 二次确认
        confirm = await self.get_user_input(f"确认删除用户 '{username}'？输入 yes 确认")
        if confirm.lower() != "yes":
            widgets.print_info("已取消删除")
            return

        await self.user_manager.delete_user(user.id)
        widgets.print_success(f"用户 '{username}' 已删除（关联数据已自动清理）")
```

#### 验证检查点 B：app.py 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from ui.tui.app import TUIApp; print('TUIApp OK:', TUIApp.__name__)"
```

预期输出：`TUIApp OK: TUIApp`

---

### 4.3 改造 src/main.py（启动时初始化存储后端）

文件路径：`langchain-chat/src/main.py`（Step 2 已创建，本步骤改造）。

Step 2 的 main.py 只加载配置 + 启动 TUI。Step 4 改造为：加载配置 → 初始化存储后端 → 启动 TUI（注入后端）。

**改造要点**：

1. async_main 里增加「初始化存储后端」步骤。
2. 创建 TUIApp 时传入 backend 参数（依赖注入）。
3. 用 try/finally 确保「无论正常退出还是异常，都关闭存储后端连接」。

**改造后的完整文件内容**（替换 Step 2 的 main.py 全部内容）：

```python
"""langchain-chat 程序总入口。

Step 4 阶段：加载配置、初始化存储后端、启动 TUI 主界面。
运行方式：uv run python src/main.py
"""

import asyncio
import sys
from pathlib import Path

# 将 src 目录加入模块搜索路径，确保 import 链路在任意运行方式下都工作。
# Path(__file__).resolve().parent 是 main.py 所在目录（即 src）。
sys.path.insert(0, str(Path(__file__).resolve().parent))


async def async_main() -> None:
    """异步主函数。

    启动流程（Step 4 起）：
        1. 加载配置（config_manager）
        2. 初始化存储后端（根据 config.storage_type 创建并 initialize）
        3. 启动 TUI 主循环（把存储后端注入 TUIApp）
    """
    # 1. 加载配置（触发单例创建，读取 .env 与 config.yaml）
    from core.config_manager import get_config

    config = get_config()
    print(f"[启动] 存储后端: {config.storage_type}，默认模型: {config.default_model}")

    # 2. 初始化存储后端
    from storage.factory import StorageFactory

    backend = StorageFactory.create(config.storage_type)
    await backend.initialize()
    print(f"[启动] 存储后端已就绪: {type(backend).__name__}")

    # 3. 启动 TUI 主循环（注入存储后端）
    from ui.tui.app import TUIApp

    try:
        app = TUIApp(backend=backend)
        await app.run()
    finally:
        # 无论正常退出还是异常，都关闭存储后端连接
        await backend.close()
        print("[启动] 存储后端已关闭")


def main() -> None:
    """程序主函数（同步入口，内部启动异步事件循环）。"""
    asyncio.run(async_main())


# 入口守护：只有直接运行本文件时才执行，被 import 时不执行。
if __name__ == "__main__":
    main()
```

**讲解：try/finally 的作用**

```python
try:
    app = TUIApp(backend=backend)
    await app.run()
finally:
    await backend.close()
```

`finally` 块的代码「无论如何都会执行」——无论 try 里是正常结束还是中途出错（比如用户按 Ctrl+C 强制退出），finally 里的 `backend.close()` 都会执行，确保数据库连接被正确关闭。如果不关闭，数据库文件可能被锁住，下次运行会报错。这是资源管理的标准做法。

---

## 五、整体运行验证

### 5.1 准备：清理旧数据库（可选）

如果你在 Step 3 运行 init_db.py 时生成了测试数据，建议先清理，从干净状态验证。如果 PyCharm 正连接着 app.db，先断开连接（移除数据源、关闭PyCharm）。

然后：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
rmdir /s /q data
```

如果不清理也可以，因为创建用户时会校验用户名唯一，不会重复创建同名用户。

### 5.2 启动程序

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python src/main.py
```

### 5.3 验证操作（手动在 TUI 里操作）

按以下顺序操作，验证每个功能：

**操作 1：创建用户**

- 主菜单选 1（用户管理）
- 用户管理菜单选 1（创建用户）
- 输入用户名：`alice`
- 预期：显示「用户创建成功: alice（id=1）」，并提示「已自动切换为当前用户: alice」

**操作 2：再创建一个用户**

- 选 1（创建用户）
- 输入用户名：`bob`
- 预期：显示「用户创建成功: bob（id=2）」。注意：此时 current_user 仍是 alice（只有首次未登录时才自动切换）

**操作 3：列出所有用户**

- 选 2（列出所有用户）
- 预期：显示 alice 和 bob 两个用户，alice 标记「<- 当前」

**操作 4：切换用户**

- 选 3（切换当前用户）
- 输入用户名：`bob`
- 预期：显示「已切换到用户: bob（id=2）」，菜单顶部当前用户变为 bob

**操作 5：验证用户名唯一（幂等性）**

- 选 1（创建用户）
- 输入用户名：`alice`（已存在）
- 预期：显示错误「用户名 'alice' 已存在」（不会重复创建）

**操作 6：验证删除的二次确认**

- 选 4（删除用户）
- 输入用户名：`bob`（当前登录的是 bob）
- 预期：显示警告「不允许删除当前正在登录的用户，请先切换到其他用户」

**操作 7：删除用户（正确流程）**

- 选 3（切换当前用户），切换回 `alice`
- 选 4（删除用户），输入 `bob`
- 输入 `yes` 确认
- 预期：显示「用户 'bob' 已删除（关联数据已自动清理）」
- 再选 2（列出），确认只剩 alice

**操作 8：验证持久化（重启程序）**

- 选 5（返回主菜单），再选 7（退出）
- 重新运行 `uv run python src/main.py`
- 进用户管理，选 2（列出）
- 预期：alice 依然存在（数据已持久化到 SQLite）

### 5.4 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 启动时初始化存储 | 显示「存储后端已就绪: SQLiteBackend」 | main.py 改造正确 |
| 创建用户成功 | 显示用户名和 id | 业务层 + 存储层 + 界面层链路通 |
| 用户名唯一校验 | 重复创建时报错 | 业务规则生效 |
| 切换用户 | 当前用户状态更新 | 状态管理正确 |
| 列出用户 | 显示所有用户，标记当前用户 | 查询功能正常 |
| 删除二次确认 | 输入 yes 才删除 | 安全机制生效 |
| 不能删当前用户 | 提示先切换 | 状态安全保护 |
| 重启后数据还在 | alice 依然存在 | 持久化生效 |

---

## 六、版本控制

### 6.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 新增：`src/core/user_manager.py`
- 修改：`src/ui/tui/app.py`、`src/main.py`
- 可能修改：`docs/Step3-...md`（如果你之前修订了 Step 3 文档未提交）
- 不应出现：`data/`（被 gitignore 排除）、`.env`、`.venv/`

### 6.2 提交与打标签

第 1 步：

```bash
git add .
```

第 2 步：

```bash
git status
```

第 3 步：

```bash
git commit -m "feat: step 4 - 用户管理业务层、TUI 用户菜单与存储后端接入"
```

第 4 步：

```bash
git tag step-4-user-mgmt
```

第 5 步：

```bash
git push
git push origin step-4-user-mgmt
```

第 6 步：

```bash
git log --oneline -5
git tag
```

### 6.3 如何查看 Gitee 仓库的当前状态和历史

有三种方式，从直观到命令行：

##### 方式 1：网页查看（最直观）

直接打开你的 Gitee 仓库地址：**https://gitee.com/txsliwei/langchain-chat**

这里能看到：

- **代码**：当前最新版本的文件结构（点开文件夹能看到每个文件内容）。
- **提交（Commits）**：点顶部的「提交」或「Commits」标签，能看到所有提交历史，每条含提交信息、作者、时间、改动文件数。
- **标签（Tags）**：点「标签」或「Tags」标签，能看到所有里程碑标签（step-1-init、step-2-skeleton、step-3-sqlite、step-4-user-mgmt）。
- **分支（Branches）**：目前只有 main 一个分支。

> 网页是最适合「浏览查看」的方式，推荐日常用这个。

##### 方式 2：命令行查看提交历史

```
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
# 查看提交历史（简略版，一行一个提交）git log --oneline
# 查看最近的 5 个提交git log --oneline -5
# 查看详细历史（含作者、时间、完整信息）git log
# 查看某个标签的详情（比如 step-3-sqlite 那次提交改了什么）git show step-3-sqlite --stat
# 查看所有标签git tag
```

##### 方式 3：对比两个标签之间的差异

这是 Git 的强大功能——查看任意两个里程碑之间改了什么：

```
# 查看 step-3-sqlite 和 step-4-user-mgmt 之间的差异统计git diff step-3-sqlite step-4-user-mgmt --stat
# 查看具体代码改动（完整 diff，内容较多）git diff step-3-sqlite step-4-user-mgmt
```

##### 推荐的查看顺序

| 你想看什么         | 用什么方式                            |
| :----------------- | :------------------------------------ |
| 仓库整体长什么样   | 网页（方式 1）                        |
| 提交历史列表       | 网页「Commits」或 `git log --oneline` |
| 某个标签改了什么   | `git show step-X-xxx --stat`          |
| 两个版本之间的差异 | `git diff tag1 tag2 --stat`           |
| 项目演进全景       | 网页看 Commits + Tags                 |

------

## 七、常见问题与排查

### 7.1 启动相关

| 报错 | 原因 | 解决 |
|------|------|------|
| `no such table: users` | 数据库未初始化（main.py 没调 initialize） | 确认 main.py 改造后包含 `await backend.initialize()` |
| `用户管理未初始化（存储后端未注入）` | TUIApp 创建时没传 backend | 确认 main.py 里 `TUIApp(backend=backend)` |

### 7.2 操作相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 创建用户报「用户名已存在」 | 用户名重复（业务幂等性保护） | 换个用户名，或先删除已有用户 |
| 删除用户报「不允许删除当前登录用户」 | 安全保护（避免状态失效） | 先切换到其他用户再删 |
| 切换用户报「用户不存在」 | 用户名输错或该用户已被删 | 先用「列出所有用户」查看存在的用户名 |

### 7.3 数据库被占用

如果运行时报 `unable to open database file` 或数据库被锁，可能是 PyCharm 还连接着 app.db。在 PyCharm 的 Database 面板断开连接后重试。

---

## 八、本步骤小结与知识清单

### 8.1 产出清单

| 类别 | 产出 |
|------|------|
| 业务层 | src/core/user_manager.py（UserManager，5 个方法） |
| 界面层改造 | src/ui/tui/app.py（用户管理子菜单，替换桩函数） |
| 入口改造 | src/main.py（启动时初始化存储后端并注入） |
| 版本控制 | 提交 feat: step 4、标签 step-4-user-mgmt |

### 8.2 知识清单

学完本步骤，应当掌握：

- 业务层（core）的角色（衔接存储层与界面层，封装业务规则）。
- 数据在三层之间的流动过程（界面 → 业务 → 存储 → 数据库）。
- 依赖注入（UserManager 接收 backend，而非自己创建）。
- 异常处理（try/except，业务层抛 ValueError，界面层捕获显示）。
- 应用状态管理（current_user 维护在 TUIApp）。
- try/finally 资源管理（确保数据库连接关闭）。
- 业务幂等性（用户名唯一校验，防止重复创建）。
- 安全保护（删除二次确认、不允许删当前用户）。

### 8.3 项目当前状态

```
langchain-chat @ step-4-user-mgmt
本地 git 仓库：已提交
Gitee 远程仓库：已推送（代码与标签）
用户管理：完整可用（创建/列出/切换/删除），数据持久化到 SQLite
桩函数替换：show_user_menu 已替换为真实功能（其余菜单仍是桩）
可运行：uv run python src/main.py 启动后可操作用户管理
```

### 8.4 后续步骤预告

Step 5：预设管理模块 + TUI 预设菜单。

目标：实现预设的完整 CRUD，加载系统内置预设（从 config/presets.yaml），支持用户自定义预设。

核心技术：PresetManager（业务层）、读取 YAML 内置预设、Step 2 的 show_preset_menu 桩函数将被真实功能替换。

---

> 本文档为 langchain-chat 项目 Step 4 的教学手册。按本文档操作，可从零独立完成用户管理的全部实现。操作过程中如遇问题，可参考第七部分排查，或随时询问。
