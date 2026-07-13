# Step 7：会话管理 + TUI 对话视图对接（核心里程碑）（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-26
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-7-first-chat`

---

## 阅读说明

本文档是 langchain-chat 项目第七步的完整教学手册。**这是整个项目的核心里程碑**——从 Step 1 到 Step 6 的所有铺垫，都在这一步汇聚成一个完整的成果：**你将在终端里和 LLM 进行真实的多轮流式对话。**

阅读并跟随操作后，你应当能够：

1. 理解会话（Session）的概念，以及它如何组织多轮对话。
2. 实现 SessionManager（会话管理业务层）。
3. 实现完整的对话视图（对话循环、流式渲染、预设选择、标题生成、自动保存）。
4. 用 prompt_toolkit 提升输入体验（兑现 Step 2 的承诺）。
5. 理解消息在「内存—数据库—LLM」三者之间的流动。
6. 在终端里和 LLM 真正聊天。

**本文档的设计原则**（与前六步文档一致）：

- 每一个概念都用「3W1H」框架或通俗比喻讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，由学习者自行创建文件并粘贴内容。
- 从最基础的开始，慢慢进入难点，不回避难点。

**完成标志（学完本文档后你应达成的目标）**：

- 新增 `src/core/session_manager.py`（会话管理业务层）。
- 改造 `src/ui/tui/chat_view.py`（完整对话视图，替换桩函数）。
- 改造 `src/ui/tui/app.py`（路由对接 + ChatEngine 注入）。
- 改造 `src/main.py`（创建 ChatEngine 并注入 TUIApp）。
- 改造 `src/ui/tui/widgets.py`（新增 prompt_toolkit 输入函数）。
- 执行 `uv run python src/main.py`，能在 TUI 中和 LLM 进行多轮流式对话，对话自动保存，重启后能加载历史继续。
- 本地 Git 仓库存在提交与标签 `step-7-first-chat`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、核心里程碑：Step 4-7 的完整铺垫回顾](#二核心里程碑step-4-7-的完整铺垫回顾)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、动手实践：创建与改造源码](#四动手实践创建与改造源码)
- [五、整体运行验证](#五整体运行验证)
- [六、版本控制](#六版本控制)
- [七、常见问题与排查](#七常见问题与排查)
- [八、本步骤小结与知识清单](#八本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

Step 6 实现了对话引擎（ChatEngine），它能调用 LLM。但引擎只是「大脑」，还没有「嘴巴和耳朵」——用户无法在界面上和它交流。Step 7 的目标是：**把大脑装进身体**——实现对话视图，让用户在终端里和 LLM 真正聊天。

具体而言，本步骤做五件事：

1. 新建 SessionManager（core/session_manager.py），管理会话的生命周期（新建、保存、加载、标题生成）。
2. 改造 chat_view.py，实现完整的对话视图（对话循环、流式渲染、预设选择、命令系统）。
3. 改造 app.py，把 ChatEngine 和 SessionManager 注入 TUIApp，路由「开始对话」到对话视图。
4. 改造 main.py，创建 ChatEngine 并传入 TUIApp。
5. 改造 widgets.py，新增基于 prompt_toolkit 的输入函数（兑现 Step 2 承诺）。

### 1.2 核心里程碑的意义

这是整个项目的**核心里程碑**。从 Step 1 到 Step 7 的完整路径：

```
Step 1  项目初始化       → 能跑了
Step 2  分层骨架 + TUI   → 能交互了
Step 3  SQLite 存储后端   → 能存数据了
Step 4  用户管理         → 知道是谁在对话
Step 5  预设管理         → 知道以什么角色对话
Step 6  对话引擎         → 有了大脑（能调 LLM）
Step 7  对话视图         → 大脑装进身体  ← 你在这里，能真正聊天了
```

完成 Step 7 后，你可以打开终端，选择一个预设角色，和 LLM 进行多轮流式对话，对话自动保存，下次还能加载历史继续。这就是项目最初的目标。

### 1.3 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 6 的对话引擎（标签 step-6-chat-engine）+ 真实的 LLM API Key |
| 输出 | 完整的终端对话功能（多轮流式、自动保存、加载历史） |
| MVP 验证点 | 在 TUI 中和 LLM 对话，流式显示回复，对话保存，重启后能加载继续 |

### 1.4 本步骤产出的文件

```
langchain-chat/
├── src/
│   ├── core/
│   │   └── session_manager.py      会话管理业务层（新建）
│   ├── ui/tui/
│   │   ├── app.py                  路由对接 + 引擎注入（改造）
│   │   ├── chat_view.py            完整对话视图（改造，替换桩函数）
│   │   └── widgets.py              prompt_toolkit 输入函数（改造）
│   └── main.py                     创建 ChatEngine 并注入（改造）
```

共新建 1 个文件，改造 4 个文件。无新依赖（复用前六步的库）。

### 1.5 本步骤的设计决策（已确认）

| 决策 | 选择 | 理由 |
|------|------|------|
| SessionManager 职责 | 新建/保存/加载/标题生成；列表/重命名/删除留到 Step 8 | 聚焦核心里程碑 |
| 对话循环设计 | 进入→检查登录→检查会话→对话循环（支持 /exit /new /rename /help） | 流程清晰 |
| 预设选择 | 新建会话时列出预设让用户选 | 落实需求 D3 |
| prompt_toolkit | 对话输入用 prompt_toolkit，菜单选择仍用 input() | 兑现 Step 2 承诺 |
| 标题生成 | LLM 摘要生成（容错兜底截取前 30 字符） | 质量更好 |
| 标题修改 | 对话中 /rename 修改（Step 8 补充会话列表重命名） | 落实需求 C4 |
| 消息历史 | 内存维护 + 同步存库 | 快且持久化 |

---

## 二、核心里程碑：Step 4-7 的完整铺垫回顾

这一节回顾 Step 4 到 Step 7 如何一步步铺垫出对话功能。理解这条线，你就理解了为什么每一步都是必要的。

### 2.1 对话功能的完整依赖链

一次完整的对话，需要这些组件协同：

```
用户在终端输入消息
      │
      ▼
┌─ chat_view.py（对话视图）──────────────────────────┐
│  ① 接收用户输入（prompt_toolkit）                   │
│  ② 把消息加入内存历史                               │
│  ③ 调用 ChatEngine.astream 发给 LLM                │
│  ④ 流式渲染 LLM 回复（逐字显示）                    │
│  ⑤ 把回复加入内存历史                               │
│  ⑥ 调用 SessionManager 保存到数据库                 │
└────────────────────────────────────────────────────┘
      │ uses                    │ uses
      ▼                         ▼
┌─ ChatEngine（Step 6）──┐  ┌─ SessionManager（Step 7）──┐
│  调用 LLM API          │  │  会话增删查（操作 SQLite）   │
│  流式返回              │  │  消息保存                    │
└────────────────────────┘  │  标题生成                    │
                            └─────────────────────────────┘
      │                         │ uses
      ▼                         ▼
┌─ LLM 服务器 ────────────┐  ┌─ SQLiteBackend（Step 3）──┐
│  通义千问/DeepSeek      │  │  sessions 表               │
│  （真实的大模型）        │  │  messages 表               │
└─────────────────────────┘  └────────────────────────────┘
```

### 2.2 每个 Step 的贡献

| Step | 提供了什么 | 在对话中的作用 |
|------|----------|--------------|
| Step 3 | SQLiteBackend | 对话历史存进数据库 |
| Step 4 | UserManager + current_user | 知道对话归属哪个用户 |
| Step 5 | PresetManager + system_prompt | 定义 LLM 的角色（翻译/代码专家等） |
| Step 6 | ChatEngine | 调用 LLM、流式返回 |
| Step 7 | SessionManager + chat_view | 组织对话、渲染界面、保存历史 |

### 2.3 数据在系统中的完整流动

以「用户输入『你好』，LLM 回复『你好！有什么可以帮你？』」为例，追踪完整的数据流动：

```
1. 用户在 chat_view 输入「你好」
2. chat_view 把「你好」封装成 HumanMessage，加入内存历史列表
3. chat_view 调用 engine.astream(内存历史)
4. ChatEngine 把消息列表发给 LLM API
5. LLM 逐 chunk 返回「你」「好」「！」「有什么可以帮你？」
6. chat_view 逐 chunk 显示（流式效果）
7. chat_view 把完整回复封装成 AIMessage，加入内存历史列表
8. chat_view 调用 session_manager.add_message 保存到数据库
9. 下一轮对话时，内存历史列表包含完整上下文，LLM 能记住之前说的
```

关键理解：**内存历史列表**（messages）是对话视图维护的，它既发给 LLM（让 LLM 有上下文），又同步存入数据库（持久化）。这就是决策 6 的「内存 + 持久化双管齐下」。

---

## 三、核心概念讲解（3W1H）

### 3.1 会话（Session）

**What（是什么）**

会话是一次连续的多轮对话。你打开聊天软件和别人聊天，一个「聊天窗口」就是一个会话。本项目里，一个会话包含：

- 标题（如「Python 快速排序实现」）
- 所属用户
- 使用的模型
- 使用的预设（可选）
- 多条消息（用户和 LLM 的来回对话）
- Token 统计

**Why（为什么需要会话）**

没有会话的概念，所有对话混在一起，无法区分「这次聊编程」和「那次聊翻译」。会话把一次主题的对话组织在一起，方便管理和回看。

**How（本项目怎么实现）**

对应数据库的 sessions 表（Step 3 已建）。一个会话（sessions 表一行）对应多条消息（messages 表多行）。SessionManager 负责会话的创建、查询、保存。

### 3.2 对话循环（Chat Loop）

**What（是什么）**

对话循环是「用户输入 → LLM 回复 → 保存 → 等待下一次输入」的循环过程。类似聊天软件：你发一条，对方回一条，你再发一条，对方再回一条……直到你退出。

**Why（为什么需要循环）**

一次对话只有一轮没意义（那不如用搜索引擎）。对话的价值在多轮——基于上下文的连续交流。循环让对话持续进行。

**How（本项目的对话循环设计）**：

```
进入对话视图
    ↓
检查是否登录（必须先登录）
    ↓
检查是否有当前会话（没有则新建：选预设、生成会话）
    ↓
┌─→ 显示提示符，等待用户输入
│       ↓
│   用户输入了什么？
│       ├─ /exit  → 退出循环，返回主菜单
│       ├─ /new   → 新建会话（选预设、清空上下文）
│       ├─ /rename → 修改当前会话标题
│       ├─ /help  → 显示命令帮助
│       └─ 普通文字 → 发给 LLM：
│           ① 加入内存历史
│           ② 流式调用 LLM
│           ③ 逐字显示回复
│           ④ 加入内存历史
│           ⑤ 保存到数据库
│           ⑥ 首轮自动生成标题
└───┘（循环）
```

### 3.3 流式渲染（在终端逐字显示）

**What（是什么）**

Step 6 讲过流式输出（LLM 逐 chunk 返回）。Step 7 要做的是**流式渲染**——把 chunk 逐个显示在终端上，让用户看到文字逐字出现的效果。

**Why（为什么需要）**

需求 A2 明确要求「逐 token 流式输出，终端实时渲染」。体验上，逐字显示比等几秒后一次性出现一大段文字好得多。

**How（怎么实现）**

关键在于 `print(text, end="", flush=True)`：

- `end=""`：不换行（默认 print 会换行，流式输出要接着上一次的位置继续打）。
- `flush=True`：立即刷新到屏幕（不等缓冲区满）。如果不 flush，文字会积攒在缓冲区里，用户看不到逐字效果。

```python
async for text, usage in engine.astream(messages):
    if text:
        print(text, end="", flush=True)   # 逐段打印，不换行，立即刷新
print()   # 回复结束后换行
```

### 3.4 prompt_toolkit（兑现 Step 2 承诺）

**What（是什么）**

prompt_toolkit 是高级命令行输入库，支持输入历史（上下箭头切换之前输入过的内容）、多行输入、自动补全等。

**Why（为什么 Step 7 才用）**

Step 2 文档 3.6 节说过「prompt_toolkit 将在 Step 7 真正使用」。之前步骤的输入都是简单的数字选择（菜单序号），用 input() 够了。但对话输入可能很长（用户输入一段代码、一篇文章），需要历史回看、多行输入，这时候 prompt_toolkit 的优势就体现出来了。

**Which（用在哪、不用在哪）**：

| 场景 | 用什么 | 理由 |
|------|--------|------|
| 对话输入（可能很长） | prompt_toolkit | 支持历史、多行 |
| 菜单序号选择（简单数字） | input()（通过 read_choice） | 简单，不需要 prompt_toolkit 的高级功能 |
| 用户名/预设名输入 | input()（通过 read_text） | 短文本，不需要历史 |

**How（怎么用）**

```python
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

# 创建历史对象（上下箭头切换历史输入）
history = InMemoryHistory()

# 读取用户输入（支持历史回看）
user_input = prompt("> ", history=history)
```

InMemoryHistory 把输入历史存在内存里（程序关闭就消失）。对话过程中，用户按上箭头能切换到之前输入过的内容，方便修改重发。

### 3.5 标题自动生成（LLM 摘要）

**What（是什么）**

用户第一轮输入后，程序自动生成一个简洁的会话标题。本项目用 LLM 来总结用户意图，生成标题。

**Why（为什么用 LLM 而不是截取）**

截取前 30 字符（需求文档原始设计）可能产生不完整的标题。用 LLM 摘要能生成更简洁、更概括的标题：

| 用户首轮输入 | 截取前 30 字符 | LLM 摘要 |
|------------|--------------|---------|
| 帮我用 Python 写一个快速排序算法 | 帮我用 Python 写一个快速排序算法 | Python 快速排序算法实现 |
| 请把这段中文翻译成英文：今天天气真好 | 请把这段中文翻译成英文：今天天气真好 | 中英翻译 |

**How（怎么实现）**

首轮对话后，额外发一个短请求给 LLM：

```
System: 请用 10-20 个字概括以下用户意图，作为对话标题。只输出标题，不要其他内容。
User: {用户的第一轮输入}
```

LLM 返回的就是标题。容错处理：如果 LLM 调用失败（网络错误等），退回到截取前 30 字符（保证有标题）。

### 3.6 消息在三种格式之间的转换

对话涉及三种消息表示，需要互相转换：

| 格式 | 在哪用 | 示例 |
|------|--------|------|
| LangChain 消息（HumanMessage 等） | 调用 LLM 时 | `HumanMessage(content="你好")` |
| Pydantic 模型（Message） | 存取数据库时 | `Message(role="human", content="你好")` |
| 字符串 | 显示给用户时 | `"你好"` |

转换关系：

```
用户输入字符串 → HumanMessage（发给 LLM）→ Message（存入数据库）
                                                     ↓
                                  数据库读出 → Message → HumanMessage（加载历史时）
```

转换规则（基于 role 字段）：

| Message.role | 对应 LangChain 类型 |
|-------------|-------------------|
| "human" | HumanMessage |
| "ai" | AIMessage |
| "system" | SystemMessage |

这个转换在 SessionManager 和 chat_view 里会用到。

---

## 四、动手实践：创建与改造源码

下面依次完成 5 个改动（1 个新建，4 个改造）。全部代码需要手动创建，文档中仅给出内容。

> 文件位置约定：源码在 `src/` 下。文件编码统一 UTF-8（不带 BOM）。
>
> import 约定：相对于 src 目录。
>
> PyCharm 提示：创建文件时选「不添加」到 Git，最后统一 git add。

### 4.1 创建 src/core/session_manager.py（会话管理业务层）

文件路径：`langchain-chat/src/core/session_manager.py`。

这是会话管理的业务层，负责：新建会话、保存消息、加载历史、生成标题。对应需求 C1（新建会话）、C6（自动保存）、C7（标题生成）。

**设计说明**：

- SessionManager 通过依赖注入接收 StorageBackend，不直接操作数据库。
- create_session：创建新会话（用户 + 模型 + 预设），返回 Session 对象。
- add_message：保存一条消息（同时更新会话的 Token 统计）。
- load_messages：加载会话的历史消息，转成 LangChain 消息列表（供 ChatEngine 使用）。
- generate_title：用 ChatEngine 生成会话标题（LLM 摘要），失败时兜底截取。

**文件内容**：

```python
"""会话管理业务层。

封装会话相关的业务逻辑：新建会话、保存消息、加载历史、生成标题。
对应需求文档 C1（新建会话）、C6（自动保存）、C7（标题生成）。

设计说明：
    - SessionManager 通过依赖注入接收 StorageBackend，不直接操作数据库。
    - 消息加载时，把数据库的 Message 转成 LangChain 的 BaseMessage（供 ChatEngine 使用）。
    - 标题生成用 ChatEngine（LLM 摘要），失败时兜底截取前 30 字符。
"""

from typing import Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from core.config_manager import AppConfig
from models.schemas import Message, Session
from storage.base import StorageBackend


class SessionManager:
    """会话管理器。

    通过传入的 StorageBackend 实例操作数据。
    使用方式：
        mgr = SessionManager(backend, config)
        session = await mgr.create_session(user_id=1, model_name="deepseek-chat")
    """

    def __init__(self, backend: StorageBackend, config: AppConfig):
        self.backend = backend
        self.config = config

    async def create_session(
        self,
        user_id: int,
        model_name: str,
        preset_id: Optional[int] = None,
        title: str = "新会话",
    ) -> Session:
        """新建会话（C1）。

        参数：
            user_id: 所属用户 ID
            model_name: 使用的模型名
            preset_id: 使用的预设 ID（可选）
            title: 会话标题（默认「新会话」，后续自动生成或手动修改）
        返回：
            创建后的 Session（含分配的 id）
        """
        session = Session(
            id=0,
            user_id=user_id,
            title=title,
            model_name=model_name,
            preset_id=preset_id,
        )
        return await self.backend.create_session(session)

    async def add_message(
        self,
        session: Session,
        role: str,
        content: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> Message:
        """保存一条消息并更新会话的 Token 统计（C6 自动保存）。

        参数：
            session: 所属会话（会被更新 Token 统计）
            role: 消息角色（human / ai / system）
            content: 消息内容
            prompt_tokens: 本条输入 token 数
            completion_tokens: 本条输出 token 数
        返回：
            创建后的 Message（含分配的 id）
        """
        message = Message(
            id=0,
            session_id=session.id,
            role=role,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        message = await self.backend.add_message(message)

        # 更新会话的 Token 统计
        session.total_prompt_tokens += prompt_tokens
        session.total_completion_tokens += completion_tokens
        await self.backend.update_session(session)

        return message

    async def load_messages_as_langchain(self, session_id: int) -> list[BaseMessage]:
        """加载会话的历史消息，转成 LangChain 消息列表。

        用于加载历史会话时，把数据库里的消息恢复成内存历史（供 ChatEngine 使用）。
        """
        messages = await self.backend.list_messages(session_id)
        return [self._to_langchain_message(m) for m in messages]

    async def generate_title(self, first_user_input: str, engine) -> str:
        """用 LLM 生成会话标题（C7）。

        参数：
            first_user_input: 用户的第一轮输入
            engine: ChatEngine 实例（用于调用 LLM）
        返回：
            生成的标题（10-20 字）。如果 LLM 调用失败，兜底截取前 30 字符。
        """
        title_prompt = [
            SystemMessage(
                content="请用 10-20 个字概括以下用户意图，作为对话标题。只输出标题，不要引号、不要其他内容。"
            ),
            HumanMessage(content=first_user_input),
        ]
        try:
            title, _ = engine.chat(title_prompt)
            # 清理：去掉可能的引号和换行
            title = title.strip().strip('"\'「」""').strip()
            # 限制长度
            if len(title) > 30:
                title = title[:30]
            return title if title else self._fallback_title(first_user_input)
        except Exception:
            # LLM 调用失败，兜底截取
            return self._fallback_title(first_user_input)

    def _fallback_title(self, text: str) -> str:
        """兜底标题：截取前 30 字符。"""
        max_len = self.config.title_max_length
        return text[:max_len] + ("..." if len(text) > max_len else "")

    async def update_title(self, session: Session, new_title: str) -> None:
        """修改会话标题（C4，对话中的 /rename 命令使用）。"""
        session.title = new_title.strip()
        await self.backend.update_session(session)

    @staticmethod
    def _to_langchain_message(message: Message) -> BaseMessage:
        """把数据库的 Message 转成 LangChain 的消息类型。"""
        if message.role == "human":
            return HumanMessage(content=message.content)
        elif message.role == "ai":
            return AIMessage(content=message.content)
        else:  # system
            return SystemMessage(content=message.content)
```

#### 验证检查点 A：SessionManager 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.session_manager import SessionManager; print('SessionManager OK:', SessionManager.__name__)"
```

预期输出：`SessionManager OK: SessionManager`

---

### 4.2 改造 src/ui/tui/widgets.py（新增 prompt_toolkit 输入函数）

文件路径：`langchain-chat/src/ui/tui/widgets.py`。

在文件末尾（read_text 函数之后），新增一个基于 prompt_toolkit 的输入函数。**注意：不修改现有的 read_text 和 read_choice，它们继续用 input()。新增的函数用于对话输入。**

在文件末尾追加以下内容：

```python
async def read_chat_input(session=None) -> str:
    """读取对话输入（使用 prompt_toolkit 异步版本，支持输入历史）。

    与 read_text 的区别：
        - read_text 用 input()，无历史、单行。

    使用 PromptSession 的 prompt_async 方法（官方推荐的异步输入方式）。
    必须用异步版本，因为对话循环在 async 环境里，
    同步的 prompt() 会触发「asyncio.run() cannot be called from a running event loop」。

    参数：
        session: PromptSession 实例（含历史记录）。首次调用传 None，会自动创建。
                 多次调用共享同一个 session，实现输入历史回看。
    返回：
        用户输入的文本（已去除首尾空白）
    """
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory

    # 首次调用时创建 session（绑定输入历史）
    if session is None:
        session = PromptSession(history=InMemoryHistory())

    try:
        # 用 prompt_async（异步版本），配合 await 使用
        raw = await session.prompt_async("> ")
        return raw.strip()
    except (EOFError, KeyboardInterrupt):
        # 用户按 Ctrl+D 或 Ctrl+C，视为退出对话
        return "/exit"
```

**设计说明**：

- 正确的做法是：**创建 PromptSession 实例，调用 `await session.prompt_async(...)`**。而且 PromptSession 的好处是：它本身可以绑定 history，多次调用共享同一个会话（包括输入历史）。
- 确认：`PromptSession.prompt_async` 是协程函数，用 `await session.prompt_async(...)` 调用。
- 捕获 EOFError（Ctrl+D）和 KeyboardInterrupt（Ctrl+C），视为退出对话（返回 /exit），防止程序崩溃。
- 返回值已 strip（去除首尾空白）。

注意：prompt_toolkit 在文件顶部导入（`from prompt_toolkit import PromptSession`
   `from prompt_toolkit.history import InMemoryHistory`）或函数内部导入（延迟导入）都可以。这里用函数内部导入（延迟导入），与 Step 5 讲过的「延迟导入」一致，避免在不需要对话的菜单场景也加载 prompt_toolkit。

---

### 4.3 改造 src/ui/tui/chat_view.py（完整对话视图）

文件路径：`langchain-chat/src/ui/tui/chat_view.py`（Step 2 的桩函数，本步骤替换为完整实现）。

这是本步骤最核心的文件。实现完整的对话视图：对话循环、流式渲染、预设选择、标题生成、自动保存、命令系统。

**设计说明**：

- start_chat 改为接收 app 对象（获取 current_user、engine、session_manager 等）。
- 对话循环：输入 → 流式回复 → 保存 → 循环。
- 命令系统：/exit、/new、/rename、/help。
- 用 prompt_toolkit 读取输入（通过 widgets.read_chat_input）。
- 用 rich 的 Live 实现流式渲染（逐字显示）。实际上用 print(end="", flush=True) 更简单，这里用 Console.print 实现。

**改造后的完整文件内容**（替换 Step 2 的 chat_view.py 全部内容）：

```python
"""对话视图（完整实现）。

实现真实的多轮流式对话，对应需求文档 A1 至 A5（核心对话功能）。
Step 7 的核心里程碑：用户能在终端里和 LLM 真正聊天。

功能：
    - 多轮流式对话（LLM 逐字回复）
    - 预设角色选择（Step 5 的 system_prompt 注入）
    - 会话标题自动生成（LLM 摘要）
    - 对话自动保存（每轮存入数据库）
    - 命令系统：/exit /new /rename /help
    - prompt_toolkit 输入（支持历史回看）

对应需求：A1（多轮）、A2（流式）、C1（新建）、C6（自动保存）、C7（标题生成）、D3（选预设）、E2（Token 统计）
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from ui.tui import widgets


async def start_chat(app) -> None:
    """启动对话视图。

    参数：
        app: TUIApp 实例（从中获取 current_user、engine、session_manager、config 等）
    """
    # 1. 检查是否登录
    if app.current_user is None:
        widgets.print_warning("请先在用户管理中创建或切换用户")
        return

    # 2. 检查引擎和会话管理器
    if app.engine is None or app.session_manager is None:
        widgets.print_error("对话引擎未初始化")
        return

    # 3. 获取或创建会话
    session = app.current_session

    # 3.1 如果当前没有会话，先查数据库有没有历史会话
    if session is None:
        sessions = await app.session_manager.backend.list_sessions(app.current_user.id)
        if sessions:
            # 有历史会话，让用户选择「继续最近的」还是「新建」
            widgets.console.print(f"\n[bold]最近会话:[/bold] {sessions[0].title}")
            widgets.console.print("  1  继续最近的会话")
            widgets.console.print("  2  新建会话")
            choice = widgets.read_choice(2)
            if choice == 0:
                # 继续最近会话
                session = sessions[0]
                app.current_session = session
                widgets.print_info(f"已加载会话: {session.title}")
            elif choice == 1:
                # 新建会话
                session = await _create_new_session(app)
                if session is None:
                    return    # 用户取消创建
                app.current_session = session
            else:
                return    # 输入 0 返回主菜单
        else:
            # 没有历史会话，直接新建
            session = await _create_new_session(app)
            if session is None:
                return
            app.current_session = session

    # 3.2 如果当前已有会话（刚对话完又选开始对话），让用户选择「继续」还是「新建」
    elif session is not None:
        widgets.console.print(f"\n[bold]当前会话:[/bold] {session.title}")
        widgets.console.print("  1  继续当前会话")
        widgets.console.print("  2  新建会话")
        choice = widgets.read_choice(2)
        if choice == 0:
            pass    # 继续当前会话，session 不变
        elif choice == 1:
            # 新建会话
            session = await _create_new_session(app)
            if session is None:
                return
            app.current_session = session
        else:
            return    # 输入 0 返回主菜单

    # 4. 加载历史消息（如果有）
    messages = await app.session_manager.load_messages_as_langchain(session.id)
    if messages:
        widgets.print_info(f"已加载历史对话（{len(messages)} 条消息），继续聊天")

    # 5. 创建输入会话对象（prompt_toolkit，含输入历史）
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    input_session = PromptSession(history=InMemoryHistory())

    # 6. 进入对话循环
    widgets.console.print("\n[bold green]=== 对话开始（输入 /help 查看命令，/exit 退出）===[/bold green]\n")

    while True:
        # 读取用户输入
        user_input = await widgets.read_chat_input(session=input_session)

        if not user_input:
            continue

        # 处理命令
        if user_input.startswith("/"):
            should_exit = await _handle_command(app, session, user_input)
            if should_exit == "exit":
                break
            elif should_exit == "new_session":
                # 用户新建了会话，更新 session 和 messages
                session = app.current_session
                messages = []
            continue

        # 普通对话：发送给 LLM
        # 6.1 把用户输入加入内存历史
        user_msg = HumanMessage(content=user_input)
        messages.append(user_msg)

        # 6.2 显示用户输入
        widgets.console.print(f"\n[bold cyan][你][/] {user_input}")

        # 6.3 流式调用 LLM
        widgets.console.print("[bold green][AI][/] ", end="")
        full_reply = ""
        final_usage = None

        try:
            async for text, usage in app.engine.astream(messages):
                if text:
                    widgets.console.print(text, end="", style="green")
                    full_reply += text
                if usage is not None:
                    final_usage = usage
            widgets.console.print()  # 换行
        except Exception as e:
            widgets.print_error(f"\nLLM 调用失败: {type(e).__name__}: {e}")
            # 移除刚加入的用户消息（因为没得到回复）
            messages.pop()
            continue

        # 6.4 把 AI 回复加入内存历史
        ai_msg = AIMessage(content=full_reply)
        messages.append(ai_msg)

        # 6.5 保存到数据库
        prompt_tokens = final_usage.get("prompt_tokens", 0) if final_usage else 0
        completion_tokens = final_usage.get("completion_tokens", 0) if final_usage else 0
        await app.session_manager.add_message(
            session, role="human", content=user_input
        )
        await app.session_manager.add_message(
            session, role="ai", content=full_reply,
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
        )

        # 6.6 显示 Token 统计
        if final_usage:
            widgets.console.print(
                f"[dim]Token: 输入 {prompt_tokens}，输出 {completion_tokens}，"
                f"累计 {session.total_prompt_tokens + session.total_completion_tokens}[/dim]\n"
            )

        # 6.7 首轮自动生成标题
        if session.title == "新会话":
            widgets.console.print("[dim]正在生成会话标题...[/dim]", end="")
            title = await app.session_manager.generate_title(user_input, app.engine)
            await app.session_manager.update_title(session, title)
            widgets.console.print(f" [bold yellow]{title}[/bold yellow]\n")


async def _create_new_session(app) -> None:
    """创建新会话（含预设选择）。

    返回：创建的 Session，或 None（用户取消）
    """
    widgets.console.print("\n[bold]=== 新建会话 ===[/bold]")

    # 1. 选择预设
    preset_id = await _select_preset(app)

    # 2. 创建会话
    config = app.config
    session = await app.session_manager.create_session(
        user_id=app.current_user.id,
        model_name=config.default_model,
        preset_id=preset_id,
    )
    widgets.print_success(f"新会话已创建（id={session.id}）")
    return session


async def _select_preset(app) -> None:
    """选择预设。返回选中的 preset_id，或 None（不使用预设）。"""
    presets = await app.preset_manager.list_presets(app.current_user.id)

    if not presets:
        widgets.print_info("没有可用预设，将不使用预设")
        return None

    widgets.console.print("\n[bold]可选预设[/bold]")
    widgets.console.print("  0  不使用预设")
    for i, p in enumerate(presets, start=1):
        tag = "[内置]" if p.is_builtin else "[自定义]"
        widgets.console.print(f"  {i}  {tag} {p.name} - {p.description}")

    choice_str = widgets.read_text("请选择预设序号（0=不使用）")
    try:
        choice = int(choice_str)
    except ValueError:
        widgets.print_info("未选择预设")
        return None

    if choice == 0:
        return None
    if 1 <= choice <= len(presets):
        selected = presets[choice - 1]
        widgets.print_info(f"已选择预设: {selected.name}")

        # 如果选了预设，把 system_prompt 作为第一条 system 消息
        # 注意：这里返回 preset_id，实际注入 system_prompt 在对话开始时处理
        return selected.id

    widgets.print_info("序号无效，不使用预设")
    return None


async def _handle_command(app, session, command: str) -> str:
    """处理对话中的 / 命令。

    返回：
        "exit"：退出对话
        "new_session"：新建了会话
        None：其他命令（继续循环）
    """
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd == "/exit":
        widgets.print_info("退出对话，返回主菜单")
        return "exit"

    elif cmd == "/new":
        # 新建会话
        new_session = await _create_new_session(app)
        if new_session is not None:
            app.current_session = new_session
            widgets.print_success(f"已切换到新会话: {new_session.title}")
            return "new_session"
        return None

    elif cmd == "/rename":
        # 修改标题
        if len(parts) < 2:
            new_title = widgets.read_text("请输入新标题")
        else:
            new_title = parts[1].strip()
        if new_title:
            await app.session_manager.update_title(session, new_title)
            widgets.print_success(f"标题已修改为: {new_title}")
        else:
            widgets.print_warning("标题不能为空")
        return None

    elif cmd == "/help":
        widgets.console.print("\n[bold]可用命令[/bold]")
        widgets.console.print("  /exit         退出对话，返回主菜单")
        widgets.console.print("  /new          新建会话（选预设、清空上下文）")
        widgets.console.print("  /rename 标题  修改当前会话标题")
        widgets.console.print("  /help         显示本帮助")
        widgets.console.print("  其他文字      发给 LLM 对话\n")
        return None

    else:
        widgets.print_warning(f"未知命令: {cmd}（输入 /help 查看可用命令）")
        return None
```

**重要设计说明**：

**改动说明** 针对：**# 3. 获取或创建会话**

用户每次选「开始对话」都能明确选择是继续还是新建。

| 场景                         | 原来的行为       | 改后的行为                       |
| ---------------------------- | ---------------- | -------------------------------- |
| 没有当前会话 + 有历史        | 直接加载最近会话 | 让用户选「继续最近」还是「新建」 |
| 没有当前会话 + 无历史        | 新建             | 新建（不变）                     |
| 有当前会话（再次选开始对话） | 直接继续         | 让用户选「继续当前」还是「新建」 |

**关于 system_prompt（预设）的注入**：

上面的代码里，`_select_preset` 返回了 `preset_id`，但 system_prompt 的实际注入需要补充。在创建会话后，如果选了预设，应该把预设的 system_prompt 作为第一条 SystemMessage 加入 messages 列表。需要在 `start_chat` 函数里、加载历史消息之后、进入对话循环之前，补充这段逻辑：

在 start_chat 的第 4 步（加载历史消息）之后，补充预设注入。找到 start_chat 里的：

```python
    # 4. 加载历史消息（如果有）
    messages = await app.session_manager.load_messages_as_langchain(session.id)
    if messages:
        widgets.print_info(f"已加载历史对话（{len(messages)} 条消息），继续聊天")
```

**在其后面补充：**

```python
    # 4.1 如果是新会话且选了预设，注入 system_prompt
    if not messages and session.preset_id is not None:
        preset = await app.preset_manager.get_preset(session.preset_id)
        if preset:
            messages.append(SystemMessage(content=preset.system_prompt))
            # 同时保存到数据库（作为 system 消息）
            await app.session_manager.add_message(
                session, role="system", content=preset.system_prompt
            )
            widgets.print_info(f"已应用预设: {preset.name}")
```

这段逻辑：如果是新会话（没有历史消息）且选了预设，就把预设的 system_prompt 作为第一条 SystemMessage 加入内存历史，同时存入数据库。

#### 验证检查点 B：chat_view.py 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from ui.tui.chat_view import start_chat; print('chat_view OK:', start_chat.__name__)"
```

预期输出：`chat_view OK: start_chat`

---

### 4.4 改造 src/ui/tui/app.py（路由对接 + 引擎注入）

文件路径：`langchain-chat/src/ui/tui/app.py`（Step 5 已改造，本步骤继续改造）。

主要变化：

1. TUIApp 构造时接收 engine（ChatEngine）和 session_manager（SessionManager）。
2. 主菜单路由：开始对话（choice==3）改为调用 `start_chat(self)`。
3. import start_chat 的方式改为 `from ui.tui.chat_view import start_chat`（保持不变，但 start_chat 现在接收 app 参数）。

**需要改动的地方**（只列出改动点，你对照 app.py 找到对应位置修改）：

**改动 1**：TUIApp 的 `__init__` 方法，新增 engine 和 session_manager。

找到 `__init__` 方法里的：

```python
    def __init__(self, backend=None) -> None:
        # 存储后端（由 main.py 注入）
        self.backend = backend
        # 业务管理器（backend 注入后初始化）
        self.user_manager: UserManager = None
        self.preset_manager: PresetManager = None
        if backend is not None:
            self.user_manager = UserManager(backend)
            self.preset_manager = PresetManager(backend)
```

改为：

```python
    def __init__(self, backend=None, engine=None, config=None) -> None:
        # 存储后端（由 main.py 注入）
        self.backend = backend
        # 对话引擎（由 main.py 注入）
        self.engine = engine
        # 应用配置（由 main.py 注入）
        self.config = config
        # 业务管理器（backend 注入后初始化）
        self.user_manager: UserManager = None
        self.preset_manager: PresetManager = None
        self.session_manager: SessionManager = None
        if backend is not None:
            self.user_manager = UserManager(backend)
            self.preset_manager = PresetManager(backend)
            if config is not None:
                self.session_manager = SessionManager(backend, config)
```

**改动 2**：新增 import SessionManager。

在文件顶部的 import 区域，找到：

```python
from core.preset_manager import PresetManager
```

在其后面加一行：

```python
from core.session_manager import SessionManager
```

**改动 3**：主菜单路由，开始对话改为调用 start_chat(self)。

找到 run 方法里的：

```python
            elif choice == 3:
                await start_chat()
```

改为：

```python
            elif choice == 3:
                await start_chat(self)
```

注意：`start_chat` 之前是 `from ui.tui.chat_view import start_chat`（无参数），现在改为接收 `self`（app 对象）。import 语句不用改（还是 `from ui.tui.chat_view import start_chat`），只是调用时传入 self。

**修复 4：app.py 的 _switch_user——切换用户时清空 current_session**

找到 app.py 里的 `_switch_user` 方法：

```python
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
```

在 `self.current_user = user` 之后，加一行清空 current_session：

```python
        self.current_user = user
        self.current_session = None    # 切换用户时清空当前会话（用户隔离）
        widgets.print_success(f"已切换到用户: {user.username}（id={user.id}）")
```

改动说明：切换用户后，current_session 设为 None。这样用户 B 选「开始对话」时，不会加载到用户 A 的会话——用户隔离得到保证。

**同样，`_create_user` 方法里也应该加这行**（虽然新用户通常没有会话，但保持一致）。找到 `_create_user` 里设置 `self.current_user = user` 的地方：

```python
            if self.current_user is None:
                self.current_user = user
                widgets.print_info(f"已自动切换为当前用户: {user.username}")
```

改为（只在「从 None 切换到新用户」时清空，逻辑上 current_session 本来就是 None，但保持规范）：

```python
            if self.current_user is None:
                self.current_user = user
                self.current_session = None
                widgets.print_info(f"已自动切换为当前用户: {user.username}")
```

---

### 4.5 改造 src/main.py（创建 ChatEngine 并注入）

文件路径：`langchain-chat/src/main.py`（Step 5 已改造，本步骤继续改造）。

主要变化：在初始化存储后端之后、启动 TUI 之前，创建 ChatEngine 实例，并传入 TUIApp。

找到 async_main 里的：

```python
    # 4. 启动 TUI 主循环（注入存储后端）
    from ui.tui.app import TUIApp

    try:
        app = TUIApp(backend=backend)
        await app.run()
    finally:
        # 无论正常退出还是异常，都关闭存储后端连接
        await backend.close()
        print("[启动] 存储后端已关闭")
```

改为：

```python
    # 4. 创建对话引擎
    from core.chat_engine import ChatEngine

    engine = ChatEngine(config)
    print(f"[启动] 对话引擎已就绪: {config.secret.MODEL_NAME}")

    # 5. 启动 TUI 主循环（注入存储后端、引擎、配置）
    from ui.tui.app import TUIApp

    try:
        app = TUIApp(backend=backend, engine=engine, config=config)
        await app.run()
    finally:
        # 无论正常退出还是异常，都关闭引擎和存储后端
        await engine.close()
        await backend.close()
        print("[关闭] 对话引擎与存储后端已关闭")
```

**设计说明**：

- ChatEngine 在 main.py 创建（因为它需要 config，而 config 在 main.py 已加载）。
- TUIApp 构造时接收 engine 和 config，注入到 app 对象。
- finally 里增加 engine.close()（虽然当前 ChatEngine 的 close 是空操作，但预留接口，保持一致性）。

---

## 五、整体运行验证

### 5.1 准备：确认 API Key 已配置

确认 .env 里的 API_BASE_URL、API_KEY、MODEL_NAME 是真实值（不是占位符）。Step 6 应该已经填好了。

### 5.2 启动程序

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python src/main.py
```

启动时应看到：

```
[启动] 存储后端: sqlite，默认模型: deepseek-chat
[启动] 存储后端已就绪: SQLiteBackend
[启动] 对话引擎已就绪: deepseek-chat
```

最后一行「对话引擎已就绪」说明 ChatEngine 创建成功。

### 5.3 验证操作（手动在 TUI 里操作）

**操作 1：未登录时尝试对话**

- 主菜单选 4（开始对话）
- 预期：显示警告「请先在用户管理中创建或切换用户」

**操作 2：创建用户并登录**

- 主菜单选 1（用户管理），选 1（创建用户），输入用户名（如 testuser）
- 返回主菜单

**操作 3：开始对话（含预设选择）**

- 主菜单选 4（开始对话）
- 预期：进入「新建会话」，列出预设让你选
- 选 2（翻译助手）
- 预期：显示「已选择预设: 翻译助手」「新会话已创建」

**操作 4：第一轮对话（验证流式 + 标题生成）**

- 输入：`Hello, how are you?`
- 预期：
  - 显示「[你] Hello, how are you?」
  - AI 回复逐字显示（流式，绿色）
  - 显示 Token 统计
  - 显示「正在生成会话标题...」+ 生成的标题（如「英语问候对话」）

**操作 5：第二轮对话（验证多轮记忆）**

- 输入：`我刚才说了什么？`
- 预期：LLM 回答出你刚才说的内容（证明多轮记忆生效）

**操作 6：验证 /help 命令**

- 输入：`/help`
- 预期：显示可用命令列表

**操作 7：验证 /rename 命令**

- 输入：`/rename 我的测试对话`
- 预期：显示「标题已修改为: 我的测试对话」

**操作 8：验证 prompt_toolkit 的历史功能**

- 按上箭头（↑）
- 预期：切换到之前输入过的内容（如「我刚才说了什么？」）

**操作 9：退出对话**

- 输入：`/exit`
- 预期：显示「退出对话，返回主菜单」，回到主菜单

**操作 10：验证持久化（重启后加载历史）**

- 退出程序（主菜单选 7）
- 重新运行 `uv run python src/main.py`
- 切换到刚才的用户
- 选 4（开始对话）
- 预期：显示「已加载历史对话（N 条消息），继续聊天」，可以接着之前的对话继续聊天。这验证了 start_chat 的第 3.1 步逻辑：当 current_session 为 None 时，先从数据库加载该用户最近的会话，让用户选择继续还是新建。

**操作 11：验证用户隔离**

- 用户 A 对话几轮后退出
- 切换到用户 B
- 选 4（开始对话）
- 预期：用户 B 看到的是 B 自己的会话（或新建），不会看到 A 的对话内容

### 5.4 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 引擎就绪 | 显示「对话引擎已就绪」 | ChatEngine 注入成功 |
| 未登录保护 | 提示先登录 | 登录检查生效 |
| 预设选择 | 列出预设，选择后注入 | 需求 D3 落实 |
| 流式输出 | AI 回复逐字显示 | 需求 A2 实现 |
| 多轮记忆 | 第二轮记得第一轮 | 消息历史维护正确 |
| Token 统计 | 显示每轮 Token | 需求 E2 实现 |
| 标题生成 | 首轮后自动生成标题 | 需求 C7 实现（LLM 摘要） |
| /rename | 标题修改成功 | 需求 C4 实现 |
| /help | 显示命令列表 | 命令系统可用 |
| prompt_toolkit 历史 | 上箭头切换历史输入 | Step 2 承诺兑现 |
| 自动保存 | 每轮对话存入数据库 | 需求 C6 实现 |
| 加载历史 | 重启后能继续 | 持久化生效 |

### 5.5 验证数据库（可选）

对话几轮后，用 PyCharm 连接 app.db，查看 messages 表，应看到对话记录（role 为 human/ai/system 的消息）。这验证了自动保存。

---

## 六、版本控制

### 6.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 新增：`src/core/session_manager.py`
- 修改：`src/ui/tui/chat_view.py`（完整对话视图）、`src/ui/tui/app.py`（引擎注入 + 路由）、`src/main.py`（创建引擎）、`src/ui/tui/widgets.py`（prompt_toolkit 输入）
- 可能修改：config.yaml（current_step 改为 Step 7）
- 不应出现：`.env`、`data/`、`.venv/`

### 6.2 更新进度文字

把 config.yaml 的 current_step 改为 Step 7：

```yaml
  current_step: "Step 7  对话视图（核心里程碑）"
```

### 6.3 提交与打标签

```bash
git add .
git status
git commit -m "feat: step 7 - 会话管理与 TUI 对话视图（核心里程碑：多轮流式对话）"
git tag step-7-first-chat
git push
git push origin step-7-first-chat
git log --oneline -8
git tag
```

---

## 七、常见问题与排查

### 7.1 对话相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 「对话引擎未初始化」 | main.py 没创建 engine 并传入 TUIApp | 按 4.5 节改造 main.py |
| 「请先在用户管理中创建或切换用户」 | 未登录 | 先创建/切换用户 |
| LLM 回复报错 | API Key 错误或网络问题 | 参考 Step 6 第十章排查 |
| 流式输出一次性出现 | 看不到逐字效果 | 确认用 `print(text, end="", flush=True)` |

### 7.2 标题生成相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 标题生成失败后用了截取 | LLM 调用失败，兜底生效 | 正常（容错机制） |
| 标题一直是「新会话」 | 首轮对话没触发标题生成 | 确认 session.title 初始是「新会话」 |

### 7.3 持久化相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 重启后不记得历史 | add_message 没调用 | 确认 chat_view 里每轮都调用 add_message |
| 加载历史后 LLM 行为异常 | system 消息位置不对 | 确认 system 消息在列表开头 |

### 7.4 prompt_toolkit 相关

| 现象 | 原因 | 解决 |
|------|------|------|
| Ctrl+C 退出程序 | 没捕获 KeyboardInterrupt | 确认 read_chat_input 里捕获了 EOFError 和 KeyboardInterrupt |
| 上箭头没历史 | history 对象没共享 | 确认对话循环里用同一个 history 对象 |

---

## 八、本步骤小结与知识清单

### 8.1 产出清单

| 类别 | 产出 |
|------|------|
| 业务层 | src/core/session_manager.py（SessionManager：新建/保存/加载/标题） |
| 对话视图 | src/ui/tui/chat_view.py（完整对话循环、流式渲染、命令系统） |
| 路由对接 | src/ui/tui/app.py（引擎注入、start_chat(self)） |
| 入口改造 | src/main.py（创建 ChatEngine 并注入） |
| 输入增强 | src/ui/tui/widgets.py（prompt_toolkit 输入函数） |
| 版本控制 | 提交 feat: step 7、标签 step-7-first-chat |

### 8.2 知识清单

学完本步骤，应当掌握：

- 会话（Session）的概念与组织方式。
- 对话循环的设计（输入→流式回复→保存→循环）。
- 流式渲染（print 的 end="" 和 flush=True）。
- prompt_toolkit 的基本用法（输入历史、多行输入）。
- 消息在三种格式（LangChain 消息、Pydantic 模型、字符串）之间的转换。
- 预设注入（system_prompt 作为第一条 SystemMessage）。
- 标题自动生成（LLM 摘要 + 容错兜底）。
- 对话自动保存（内存历史 + 数据库持久化）。
- 命令系统（/exit /new /rename /help）。
- 依赖注入（engine、session_manager 由 main.py 创建并注入 TUIApp）。

### 8.3 项目当前状态

```
langchain-chat @ step-7-first-chat
核心里程碑达成：能在终端里和 LLM 进行多轮流式对话
对话功能：完整可用（多轮、流式、预设、标题、保存、加载、命令）
桩函数替换进度：用户、预设、开始对话已实现；会话管理列表/重命名/删除、设置仍是桩
下一步：Step 8 完善会话管理（列表/重命名/删除）
```

### 8.4 桩函数替换进度

| 菜单功能 | 状态 | 实现步骤 |
|---------|------|---------|
| 用户管理 | 已实现 | Step 4 |
| 预设管理 | 已实现 | Step 5 |
| 会话管理 | 部分（对话中可新建/重命名） | Step 7（对话）+ Step 8（列表/删除） |
| 开始对话 | 已实现 | Step 7（核心里程碑） |
| 设置 | 桩函数 | Step 10 |

### 8.5 下一步预告

Step 8：会话管理完善（列表/重命名/删除/新建 + 会话菜单对接）。

Step 7 实现了对话中新建和重命名会话，Step 8 会完善会话管理的完整功能：

- 会话列表（展示所有历史会话）
- 从列表加载会话继续对话
- 从列表重命名会话
- 从列表删除会话
- 会话管理子菜单（替换 Step 2 的桩函数）

---

> 本文档为 langchain-chat 项目 Step 7（核心里程碑）的教学手册。按本文档操作，第一次在终端里和 LLM 真正对话——这是从 Step 1 开始的核心目标。操作过程中如遇问题，可参考第七部分排查，或随时询问。
