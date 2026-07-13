# Step 2：数据模型 + 存储接口 + 配置管理 + TUI 骨架（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-25
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-2-skeleton`

---

## 阅读说明

本文档是 langchain-chat 项目第二步的完整教学手册。阅读并跟随操作后，你应当能够：

1. 理解分层架构的设计思想，知道每一层的职责与依赖方向。
2. 掌握 Pydantic v2 的数据模型定义方法。
3. 掌握 ABC 抽象基类的接口契约机制。
4. 掌握 Rich 与 prompt_toolkit 的基础用法。
5. 从零搭建一个可交互的 TUI 菜单界面。

**本文档的设计原则**（与 Step 1 文档一致）：

- 每一个概念都用「3W1H」框架讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，可以自行创建文件并粘贴内容。
- 每完成若干文件后设有「验证检查点」，便于及时发现问题。

**完成标志（学完本文档后你应达成的目标）**：

- src 目录形成完整的分层骨架（models / storage / core / interface / ui）。
- 执行 `uv run python src/main.py` 出现可交互的 TUI 主菜单。
- 菜单选项可按键选择，暂以提示信息返回（stub 桩函数）。
- 本地 Git 仓库存在提交与标签 `step-2-skeleton`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置回顾与准备](#二前置回顾与准备)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、动手实践：创建源码文件](#四动手实践创建源码文件)
- [五、整体运行验证](#五整体运行验证)
- [六、版本控制](#六版本控制)
- [七、常见问题与排查](#七常见问题与排查)
- [八、本步骤小结与知识清单](#八本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

Step 1 搭好了项目的「地基」（配置文件、入口、版本控制），但程序只能打印横幅，没有任何交互能力。Step 2 的目标是：**从「能跑」升级到「能交互」**。

具体而言，本步骤做四件事：

1. 定义数据结构（Pydantic 模型）。
2. 定义存储后端的接口契约（ABC 抽象基类）。
3. 实现配置加载（读取 .env 与 config.yaml）。
4. 搭建 TUI 菜单界面骨架（可显示、可选择，功能暂用桩函数）。

本步骤只建**骨架**（结构 + 接口），不实现具体业务逻辑（如真实的数据库读写、真实的 LLM 调用）。这是工程纪律：**先把架子立起来，再逐步填充功能**。

### 1.2 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 1 完成的项目骨架（标签 step-1-init） |
| 输出 | 分层 src 目录 + 可交互 TUI 菜单 |
| MVP 验证点 | `uv run python src/main.py` 出现主菜单，可按键选择 |

### 1.3 本步骤产出的目录结构

Step 2 完成后，src 目录从「只有 main.py」演进为完整的分层骨架：

```
src/
├── __init__.py               源码包标识（Step 1 已建）
├── main.py                   程序入口（本步骤改造：接入 TUI）
├── core/                     核心业务层（新建）
│   ├── __init__.py
│   └── config_manager.py     配置加载与管理
├── models/                   数据模型层（新建）
│   ├── __init__.py
│   └── schemas.py            Pydantic 数据模型
├── storage/                  存储层（新建）
│   ├── __init__.py
│   └── base.py               抽象基类（接口定义）
├── interface/                UI 接口定义层（新建）
│   ├── __init__.py
│   └── ui_protocol.py        UI 协议
└── ui/                       UI 实现层（新建）
    ├── __init__.py
    └── tui/                  TUI 实现（新建）
        ├── __init__.py
        ├── app.py            主应用（菜单路由）
        ├── menu_view.py      菜单视图
        ├── chat_view.py      对话视图骨架
        └── widgets.py        复用组件
```

### 1.4 关于「按需创建目录」的回顾

在 Step 1 的讨论中，我们确立了「**按需创建，用到才建**」的工程原则。Step 2 需要用到 models、storage、core、interface、ui 这些层，所以现在创建它们。这与 Step 1 不提前创建空目录的做法是一致的——**用到某层时，才建对应目录**。

---

## 二、前置回顾与准备

### 2.1 Step 1 回顾

| 已完成 | 结论 |
|--------|------|
| 项目骨架 | 9 个配置文件（pyproject.toml、.gitignore、三层配置文件） + src/main.py 打印横幅 |
| Python 环境 | 锁定 3.12.13，uv 虚拟环境已建立 |
| Git 仓库 | 本地 + Gitee 远程同步，标签 step-1-init |
| 当前能力 | 程序能跑，但只是打印横幅，**没有任何交互** |

### 2.2 本步骤需要的第三方依赖

Step 2 是项目**首次引入第三方依赖**的步骤。需要以下 6 个库：

| 库 | 版本（实测） | 用途 | 用在哪里 |
|----|------------|------|---------|
| pydantic | 2.13.4 | 数据校验与模型定义 | models/schemas.py |
| pydantic-settings | 2.14.2 | 类型安全的配置管理 | core/config_manager.py |
| python-dotenv | - | 加载 .env 环境变量 | core/config_manager.py |
| pyyaml | 6.0.3 | 解析 YAML 配置文件 | core/config_manager.py |
| rich | 15.0.0 | 终端富文本渲染（彩色、边框、表格） | ui/tui/ 全部文件 |
| prompt_toolkit | 3.0.52 | 高级命令行输入（历史、补全） | ui/tui/ 输入相关 |

> 重点注意：pydantic 是 **v2 版本**（2.13.4）。v2 与 v1 语法差异较大，本文档所有代码均按 v2 语法编写。

### 2.3 准备工作：安装依赖

#### 2.3.1 安装方法：uv add

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv add pydantic pydantic-settings python-dotenv pyyaml rich prompt_toolkit
```

**讲解 uv add 的作用**：

- 读取网络上的包信息，解析版本兼容性。
- 把库添加到 `pyproject.toml` 的 `dependencies` 列表。
- 把精确版本写入 `uv.lock`（锁定）。
- 把库安装到 `.venv` 虚拟环境。

**一条命令的优雅**：传统 pip 工作流需要「pip install + 手动改 requirements.txt + pip freeze」，uv add 一条命令即可完成全部操作。

#### 2.3.2 安装后如何验证

```bash
uv run python -c "import pydantic, rich, prompt_toolkit, yaml, dotenv; print('所有库导入成功')"
```

预期输出：`所有库导入成功`

#### 2.3.3 如何删除（万一装错）

```bash
uv remove 库名
```

比如 `uv remove pydantic` 会从 pyproject.toml 和 .venv 同时移除。

#### 2.3.4 安装后的最佳实践

- pyproject.toml 和 uv.lock **都要提交到 Git**（保证可复现）。
- 不要手动改 uv.lock，它由 uv 自动维护。

验证依赖是否已安装：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import pydantic, pydantic_settings, dotenv, yaml, rich, prompt_toolkit; print('全部导入成功')"
```

预期输出：`全部导入成功`

如果报 `ModuleNotFoundError`，说明依赖未安装，执行：

```bash
uv add pydantic pydantic-settings python-dotenv pyyaml rich prompt_toolkit
```

> 关于安装速度：如果下载慢，是因为默认从国外 PyPI 源下载。可以参考：uv 配置国内镜像源（加速 uv add）.md
>
> 可在项目根目录创建 `uv.toml` 配置清华镜像源加速（详见 Step 1 讨论或 uv 包管理器教学文档）。`uv.toml` 内容示例：
>
> ```toml
> [[index]]
> url = "https://pypi.tuna.tsinghua.edu.cn/simple"
> default = true
> ```

### 2.4 准备工作：创建 .env 文件

在 Step 1 的讨论中，我们确立了「**用到时才配**」的原则。Step 2 的 config_manager 需要读取 .env，所以现在创建它。

从模板复制：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
copy .env.example .env
```

复制后，.env 里的值是占位符（`your_api_key_here` 等）。**本步骤先保持占位符，不需要填真实 API Key**。真实 API Key 要等到 Step 6（对话引擎）真正调用 LLM 时才需要。

> 安全提示：.env 已被 .gitignore 排除，不会进入版本库。即使里面填了真实密钥，也不会泄露。

### 2.5 关于 import 写法的约定（重要）

本项目运行方式为 `uv run python src/main.py`。在这种运行方式下，Python 会把脚本所在目录（即 `src`）加入模块搜索路径。因此，**文件之间的 import 写法是相对于 src 目录的**：

```python
from models.schemas import User           # 不是 from src.models.schemas
from core.config_manager import ConfigManager
from ui.tui.app import TUIApp
```

> **不要写成 `from src.models...`**。这是本步骤最常见的错误之一，详见第七部分排查。

---

## 三、核心概念讲解（3W1H）

本步骤涉及六个核心概念，逐个讲解。

### 3.1 分层架构（本步骤最重要的概念）

**What（是什么）**

分层架构是把代码按职责切成若干层，每层只负责一类工作，层与层之间通过明确的接口通信。本项目采用五层架构：

```
┌─────────────────────────────────────┐
│  UI 实现层（ui/）                     │  负责「用户看到什么、怎么交互」
│  TUI / 未来 WebUI                    │
├─────────────────────────────────────┤
│  UI 接口层（interface/）              │  定义「UI 必须遵守的契约」
├─────────────────────────────────────┤
│  核心业务层（core/）                  │  负责「业务逻辑」
│  对话引擎、会话管理、用户管理、配置    │
├─────────────────────────────────────┤
│  数据模型层（models/）                │  定义「数据长什么样」
├─────────────────────────────────────┤
│  存储层（storage/）                   │  负责「数据怎么存、怎么取」
└─────────────────────────────────────┘
```

**Why（为什么需要）**

用一个反例说明。不分层的代码（都堆在一起）长这样：

```python
# 没有分层的代码（反面教材）
def main():
    user_input = input("请输入：")              # UI 逻辑
    api_key = "sk-xxx"                          # 配置（硬编码）
    response = call_llm(api_key, user_input)    # 业务逻辑
    save_to_sqlite(response)                    # 存储逻辑
    print(response)                             # UI 逻辑
```

问题：UI、业务、配置、存储全搅在一起。后果：

- 想把 TUI 换成 WebUI，要改全部代码。
- 想把 SQLite 换成 MySQL，要改全部代码。
- 想测试对话逻辑，必须连着 UI 和数据库一起测，无法独立。

分层后，每层只做自己的事，通过接口通信：

- 换 UI：只改 UI 层，业务层不动。
- 换数据库：只改存储层，业务层不动。
- 测试业务：只测业务层，不碰 UI 和数据库。

**Which（本项目的分层方案）**

本项目采用**五层架构**，对应五个目录。各层职责：

| 层 | 目录 | 职责 | 依赖方向 |
|----|------|------|---------|
| UI 实现层 | ui/ | 渲染界面、接收用户输入 | 调用 interface 和 core |
| UI 接口层 | interface/ | 定义 UI 必须实现的契约 | 被 core 调用 |
| 核心业务层 | core/ | 业务逻辑 | 调用 models 和 storage |
| 数据模型层 | models/ | 定义数据结构 | 被各层引用 |
| 存储层 | storage/ | 数据持久化 | 被 core 调用 |

**依赖规则（核心）：上层依赖下层，下层不依赖上层。** 比如 core 可以用 models 里的数据结构，但 models 不能反过来调用 core。这条规则保证层的可替换性。

**How（本步骤怎么落地）**

Step 2 只建骨架（接口和结构），不实现具体业务逻辑：

- models/schemas.py：定义 User/Session/Message/Preset/UserConfig 数据结构（Step 2 用到的部分）。
- storage/base.py：定义存储后端必须实现的方法（抽象基类，不实现具体读写）。
- interface/ui_protocol.py：定义 UI 必须实现的方法（抽象基类）。
- core/config_manager.py：实现配置加载（本步骤( Step 2 )要真正实现的功能，因为 TUI 要显示配置信息）。
- ui/tui/*：TUI 界面骨架（菜单能显示、可选择，但选项功能是桩函数）。

### 3.2 Pydantic（数据校验库）

**What（是什么）**

Python 的数据校验库，用「类」的方式定义数据结构，自动校验类型、自动序列化。示例：

```python
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int                          # 必须是整数
    username: str                    # 必须是字符串
    created_at: datetime             # 自动把字符串转成 datetime

user = User(id=1, username="alice", created_at="2026-06-24")
# Pydantic 自动校验类型，错了会抛异常
```

**Why（为什么需要）**

企业级项目用它定义数据结构是标配。

- 强类型约束：传错类型会立刻报错。
- 自动校验：不用手写校验代码。
- IDE 补全友好：定义了字段类型后，编辑器能自动提示。
- 自动序列化：模型可以方便地转成字典或 JSON。

**Which（方案对比）**

| 方案 | 特点 | 是否选用 |
|------|------|---------|
| 普通 dict | 无校验、无提示 | 否 |
| dataclass | 标准库自带，但无校验 | 否 |
| attrs | 功能全，但需额外学习 | 否 |
| **Pydantic** | 校验、序列化、IDE 友好 | 是 |

**How（关键语法，Pydantic v2）**

本步骤用到的 v2 关键语法：

1. 继承 `BaseModel` 定义模型。
   * 在 `models/schemas.py` 中定义 BaseModel 子类。
2. 用 `Field(default_factory=函数)` 为字段设置自动默认值（如自动生成当前时间）。
3. 用 `Optional[类型]` 表示字段可以为 None。
4. 用 `Literal["a", "b", "c"]` 限定字段取值范围。

### 3.3 ABC 抽象基类

**What（是什么）**

Python 标准库 `abc` 模块提供的机制，用来定义「接口契约」——规定子类必须实现哪些方法。示例：

```python
from abc import ABC, abstractmethod

class StorageBackend(ABC):           # 继承 ABC，成为抽象基类
    @abstractmethod
    def save_user(self, user):       # 抽象方法，子类必须实现
        ...

class SQLiteBackend(StorageBackend):
    def save_user(self, user):       # 必须实现，否则实例化时报错
        print("保存到 SQLite")
```

**Why（为什么需要）**

强制子类实现所有方法，保证「不同存储后端接口一致」。没有 ABC，开发者可能漏实现某个方法，到运行时才暴露问题；有了 ABC，**实例化时就报错**，及早发现。

**Which（方案对比）**

| 方案 | 特点 | 是否选用 |
|------|------|---------|
| 鸭子类型 | 无强制，靠自觉 | 否 |
| Protocol | 较新，可选检查 | 否 |
| **ABC** | 成熟标准，强制实现 | 是 |

**How（用法）**

在 storage/base.py 定义 `StorageBackend(ABC)`，所有方法加 `@abstractmethod`。将来 Step 3 的 SQLiteBackend 继承它并实现所有方法。

### 3.4 UI 协议（接口解耦）

**What（是什么）**

定义 UI 层必须实现的接口规范，让业务层与 UI 层解耦。

**Why（为什么需要）**

本项目需求 H1 要求「定义统一的 UI 协议接口，TUI/WebUI 通过实现同一接口对接业务层」。没有这层接口，TUI 和业务代码直接耦合，将来换 WebUI 要改全部业务代码。

**How（用法）**

在 interface/ui_protocol.py 中定义 `AbstractUI(ABC)`，声明 UI 必须实现的方法（如显示消息、获取输入、显示菜单等）。

### 3.5 Rich（终端富文本渲染）

**What（是什么）**

Python 终端富文本渲染库，能让终端显示彩色文字、边框面板、表格、Markdown 等。

**Why（为什么需要）**

Step 1 用 print 打印横幅，是纯黑白文本。Step 2 起用 rich，让菜单有颜色、边框、表格，用户体验大幅提升。后续流式输出、Markdown 渲染也依赖 rich。

**Which（方案对比）**

| 方案 | 特点 | 是否选用 |
|------|------|---------|
| print | 无样式 | 否 |
| click | 功能有限 | 否 |
| **rich** | 功能最全（彩色、面板、表格、Markdown、进度条） | 是 |

**How（基础用法）**

```python
# 用 rich.console.Console 进行输出
# 用 rich.panel.Panel 画边框，用 rich.table.Table 画表格
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
console.print("[bold green]绿色粗体文字[/bold green]")
console.print(Panel("这是面板内容", title="标题"))
```

### 3.6 prompt_toolkit（高级命令行输入）

**What（是什么）**

高级命令行输入库，支持输入历史、自动补全、多行输入。

**Why（为什么需要）**

input() 是最基础的（只能读一行、无历史、无补全）。对话系统需要更好的输入体验，prompt_toolkit 能提供类似浏览器地址栏的体验（上下箭头切换历史输入）。

**Which（方案对比）**

| 方案 | 特点 | 是否选用 |
|------|------|---------|
| input() | 最基础，无历史无补全 | 否 |
| **prompt_toolkit** | 全功能（历史、补全、多行） | 是 |

**How（基础用法）**

```python
# 用 prompt_toolkit.prompt() 替代 input()
from prompt_toolkit import prompt
text = prompt("请输入：")
```

说明：**本步骤的输入函数暂用内置 input()，prompt_toolkit 将在后续步骤（Step 7 对话视图）真正使用**。

* 具体见本文档第 4.11 节（widgets.py 的 read_text 函数）

### 3.7 配置加载（python-dotenv 与 PyYAML）

**What**

- python-dotenv：从 .env 文件加载环境变量到 os.environ。
- PyYAML：解析 YAML 文件成 Python 字典。

**Why**

config_manager 需要同时读取两个配置源：.env（敏感信息，如：API Key）与 config.yaml（业务配置），合并成统一的配置对象供全局使用。

**How**

本步骤用 pydantic-settings 的 `BaseSettings` 来统一管理。`BaseSettings` 能自动从环境变量（含 .env）读取值，并结合 config.yaml 的内容。

### 3.8 异步编程（asyncio）
  What：异步是什么（烧水洗菜比喻）
  Why：为什么本项目用异步（A3 全链路异步）
  Which：异步 vs 同步 vs 多线程（简单对比，本项目选 asyncio）
  How：三个关键字用法 + main.py 里的体现 + 最小示例

#### 3.8.1 用一个生活比喻理解异步

先打个比方。假设你要做两件事：烧水（5 分钟）+ 洗菜（3 分钟）。

- **同步做法**：先烧水，盯着水壶等 5 分钟，水开了再去洗菜 3 分钟。总共 8 分钟。期间你干等着，什么都没做。
- **异步做法**：按下烧水开关（不盯），立刻去洗菜 3 分钟，洗完回来水也快开了。总共约 5 分钟。期间你没有闲着。

异步的核心价值：**在「等待」某件事的时候，去做别的事，不浪费时间**。

对应到程序里：网络请求、数据库查询、文件读写这些操作，CPU 大部分时间在「等结果」。异步让 CPU 在等待时去干别的活，大幅提高效率。

#### 3.8.2 三个关键字/模块的含义

| 关键字/模块     | 作用                                                | 比喻                                     |
| :-------------- | :-------------------------------------------------- | :--------------------------------------- |
| `async def`     | 定义一个「协程函数」（coroutine）                   | 标记一个任务是「可以暂停/恢复」的        |
| `await`         | 暂停当前协程，等待另一个协程完成，期间让出 CPU      | 「我等这个结果，你先去忙别的」           |
| `asyncio`       | Python 标准库，提供事件循环（event loop）来调度协程 | 相当于「总调度员」，决定谁先执行、谁暂停 |
| `asyncio.run()` | 启动事件循环，运行一个协程直到完成                  | 「总调度员上岗，开始干活」               |

#### 3.8.3 为什么本项目用异步

需求文档 A3 明确要求「全链路异步」。原因：本项目要同时处理 LLM 网络调用（慢）、数据库读写（有延迟）、用户输入（要响应）。如果用同步，调 LLM 时整个程序卡住无法响应输入；用异步则可以在等 LLM 时继续响应。

#### 3.8.4 你源码里的具体体现

以 main.py 为例，逐行解读：

```python
import asyncio                          # 引入异步标准库

async def async_main() -> None:         # 定义协程函数（注意 async 前缀）
    config = get_config()               # 普通代码，正常执行
    ...
    await app.run()                     # await：暂停 async_main，等 app.run() 完成

def main() -> None:                     # 同步入口函数
    asyncio.run(async_main())           # 启动事件循环，运行协程 async_main
```

为什么要这样分两层（`main` 调 `async_main`）？因为 **asyncio.run() 是同步函数，它是异步世界和同步世界的「边界」**。程序的入口必须是同步的（操作系统调用 main），由它启动事件循环进入异步世界。

再看 storage/base.py：

```python
@abstractmethod
async def create_user(self, user: User) -> User:    # 异步方法
    ...
```

所有存储方法都是 `async def`，意味着将来调用时要写 `await backend.create_user(user)`。

#### 3.8.5 一个最小可运行的异步示例

```python
import asyncio

async def boil_water():                  # 协程：烧水
    print("开始烧水...")
    await asyncio.sleep(3)               # 模拟等 3 秒（非阻塞，可让出 CPU）
    print("水开了")

async def wash_vegetables():             # 协程：洗菜
    print("开始洗菜...")
    await asyncio.sleep(2)               # 模拟等 2 秒
    print("菜洗好了")

async def main():
    # 并发执行两个协程（同时进行，不互相等待）
    await asyncio.gather(boil_water(), wash_vegetables())
    print("两件事都做完了")

asyncio.run(main())                      # 启动事件循环
```

运行后你会发现，洗菜（2 秒）和烧水（3 秒）几乎同时开始，总共约 3 秒（而非 5 秒）完成。这就是异步的作用。



---

## 四、动手实践：创建源码文件

下面依次创建 14 个新文件，并改造 1 个已有文件（main.py），共 15 个小节（4.1 至 4.15）。按创建顺序分为六个模块，每个模块完成后有验证检查点。

> 文件位置约定：所有文件均在 `src/` 目录下。每个小节标题标注了文件相对于项目根目录的路径。文件编码统一使用 UTF-8（不带 BOM）。
>
> import 约定：文件之间的 import 写法是相对于 src 目录的（如 `from models.schemas import User`），不要写成 `from src.models.schemas`。
>
> 建议：在IDE（PyCharm 或者 VSCode）中完成源码的创建和编辑。
>
> 注意：在 PyCharm 中，添加源码时，会提示「要不要把这个新文件加入 Git 追踪？」？
>
> 这是 PyCharm 的一个**贴心提醒**，目的是防止你不小心把不该提交的文件（如 .env、临时文件）加进 Git。
>
> 你自己来选择吧，但是无论如何选择，后续均要手动使用 git 命令完成任务。所以，建议选择： 不添加。
>
> 注意：如果不小心选了 添加（不再询问），那么，可以如下操作：
>
> 1. **改 PyCharm 设置**：File → Settings → Version Control → Confirmation → 创建文件时选「Do not add」。
>
>    * 注意：这个仅仅是影响到当前项目（项目级）的配置，不会影响到PyCharm的后续项目的配置。
>    * **项目级设置，只影响 langchain-chat 这个项目，不影响其他项目。**
>
> 2. **撤出已添加的文件**（可选）：命令行执行 `git restore --staged .`。
>
> 3. **继续按文档操作**：创建文件时 PyCharm 不再弹框，文件显示为红色（Untracked）。
>
> 4. **全部完成后统一提交**：
>
>    git add .
>    git status
>    git commit -m "feat: step 2 - 数据模型、存储接口、配置管理与 TUI 骨架"
>    git tag step-2-skeleton
>    git push
>    git push origin step-2-skeleton

### 关于桩函数（Stub）

**`stub` 在计算机软件工程和测试领域中，对应的标准中文术语是【桩函数】（或称测试桩、存根程序）。**

开发中需要彻底吃透这个概念，从**定义**、**核心作用**以及**源码示例**三个维度对其进行讲解。

#### 1. 什么是桩函数（Stub）？

桩函数是指**在软件测试或微服务联调过程中，用来“欺骗”调用者、顶替那些「还未开发完」或「结构太复杂而无法直接物理运行」的真实函数/组件的虚拟替代品。**

- **通俗比喻**：就像拍电影时的“替身演员”。当主角（真实函数）还没就位，或者要拍跳楼等高危动作（如连接真实的生产环境数据库）时，测试人员就安排一个假人（Stub）站在那里，导演（调用者）喊开始，假人只需要机械地回答一个预设的动作，让剧情（控制流）能顺利往下演即可。
- **物理卡口**：桩函数通常**没有复杂的内部逻辑，也不执行真正的业务计算**。它的内部往往硬编码（Hard-coded）了固定或可控的返回值。

#### 2. 桩函数的核心作用是什么？

尤其在驾驭工程（Harness Engineering）和进行单元测试时，桩函数具有不可替代的三大核心物理防线：

##### 作用一：实现「自顶向下」集成测试的解耦与断轨

当你在开发一个复杂的软件架构（例如一个基于 langchain 的chatbot项目或者是 coding agent 项目）时，高层的业务逻辑已经写好，但底层依赖的物理组件还没有被团队其他人开发出来。

- **没有 Stub 的惨状**：高层代码因为缺少底层依赖，连编译或运行都跑不过，开发直接陷入死锁。
- **使用 Stub 的自愈**：手动写一个临时的 函数，它不真正去实现实际的业务逻辑，直接无脑返回 `True`。高层代码就能顺利往下跑，完成自身的逻辑验证。

##### 作用二：隔离高危/高成本的外部依赖环境

如果一个函数在运行时需要物理连接昂贵的云服务、拉取天量数据的远程数据库、或者去触碰某些涉及真实的资金扣款接口：

- **Stub 的拦截价值**：用桩函数偷换掉这些真实的物理端点，每次调用都返回预设好的虚拟成功/失败报文。**既保护了外部环境安全，又实现了零成本的高频自动化测试。**

##### 作用三：精准构造边界条件与错误路径（Error Paths）

在测试系统的健壮性时，你往往需要模拟一些极端情况（如：目标服务器网络超时、数据库磁盘瞬间爆满、第三方 API 抛出 500 崩溃）。

- 在真实环境里想人工制造这种物理故障极其困难，但通过**编写桩函数，你可以强行让它硬编码抛出特定的物理异常**，从而 100% 审计出你的主控系统是否具备自愈和失败回滚（Rollback）的能力。

#### 3. 高性能最佳实践：最小闭环源码演示

假设你正在为软件工程课程设计一段测试用例，需要测试一个订单处理系统，但支付系统尚未完工。以下是符合企业级最佳实践的 Python 实现方式：

```python
import pytest

# -------------------------------------------------------------
# 1. 被测的目标主控系统 (真实的高层业务逻辑)
# -------------------------------------------------------------
def process_customer_order(order_id: int, total_amount: float, payment_service_fn) -> str:
    """
    处理客户订单的主函数。
    为了解耦，将底层支付函数作为参数动态注入 (Dependency Injection)。
    """
    if total_amount <= 0:
        return "INVALID_AMOUNT"
        
    # 调用底层依赖。在测试时，payment_service_fn 将会被 Stub 强行偷换掉
    payment_status = payment_service_fn(order_id, total_amount)
    
    if payment_status == "SUCCESS":
        return "ORDER_PROCESSED"
    elif payment_status == "INSUFFICIENT_FUNDS":
        return "ORDER_FAILED_NO_MONEY"
    else:
        return "ORDER_SYSTEM_ERROR"

# -------------------------------------------------------------
# 2. 编写测试桩函数 (Stub)
# -------------------------------------------------------------
def payment_service_stub_success(order_id: int, amount: float) -> str:
    """这是一个桩函数：它没有任何物理计算，直接返回预设的成功状态"""
    return "SUCCESS"

def payment_service_stub_no_money(order_id: int, amount: float) -> str:
    """这是另一个桩函数：专门用来构造底层资金不足的极端错误路径"""
    return "INSUFFICIENT_FUNDS"

# -------------------------------------------------------------
# 3. 利用自动化测试马缰 (Harness) 进行审计验证
# -------------------------------------------------------------
def test_order_processing_with_stubs():
    # 验证：当底层支付桩函数返回成功时，主控制流是否能正确产出 ORDER_PROCESSED
    result_1 = process_customer_order(1001, 299.0, payment_service_stub_success)
    assert result_1 == "ORDER_PROCESSED"
    
    # 验证：当底层桩函数模拟扣款失败时，主控制流是否能稳健拦截并返回相应错误码
    result_2 = process_customer_order(1002, 9999.0, payment_service_stub_no_money)
    assert result_2 == "ORDER_FAILED_NO_MONEY"
```

**分析与总结：**

软件工程测试理论中的核心专有名词 `Stub`（桩函数），包括：“自顶向下集成测试”、“依赖隔离”以及提供“依赖注入测试桩”源码，涉及 IEEE 软件测试标准规范。

### 关于 `__init__.py `

`__init__.py` 的作用是**告诉 Python「这个目录是一个包（package）」**。有了它，Python 才允许用 `from storage.base import StorageBackend` 这样的语法导入目录里的模块。

Python 3.3+ 其实支持「命名空间包」（没有 `__init__.py` 也能 import），但显式建一个 `__init__.py` 有两个好处：

1. **明确性**：一眼看出这是个 Python 包，不是普通文件夹。
2. **IDE 友好**：PyCharm 等编辑器靠它识别项目结构，代码补全更准确。

所以本项目所有层目录（models、storage、core、interface、ui、ui/tui）都有 `__init__.py`，内容都是一段文档字符串（说明该包的职责和内容）。

`__init__.py` 可以是空文件，但不建议全空，即：**技术上可以空，但本项目建议放一段文档字符串。** 原因：

| 做法               | 是否有效          | 评价                             |
| ------------------ | ----------------- | -------------------------------- |
| 纯空文件（0 字节） | 有效，Python 认可 | 可以，但信息量少                 |
| 只有文档字符串     | 有效，且更好      | 本项目采用，企业生产实践中推荐。 |

**总结**

- `__init__.py` 可以空，但本项目统一用「文档字符串」填充，兼顾明确性和 IDE 友好。
- 内容文本的目的：只是给阅读者和 IDE 看的说明。它的价值是：**打开这个目录时，一眼就知道 storage 包里有什么、每个文件对应哪个 Step。**

### 模块一：数据模型层（2 个文件）

#### 4.1 创建 `src/models/__init__.py`

文件路径：`langchain-chat/src/models/__init__.py`（需先建立 src/models 目录）。

**文件内容**：

```python
"""数据模型层。

本包定义项目的核心数据结构（Pydantic 模型），所有层共用。
"""
```

#### 4.2 创建 src/models/schemas.py

文件路径：`langchain-chat/src/models/schemas.py`。

这个文件定义项目的核心数据结构，对应需求文档第四部分「数据实体设计」。所有层（core、storage、ui）都引用这些模型。

**字段设计依据**：完全对应需求文档第四部分的数据实体表格，5 个实体一一对应。

##### 需求文档中的：数据实体设计

| 实体           | 表名           | 字段                                                         | 说明                            |
| -------------- | -------------- | ------------------------------------------------------------ | ------------------------------- |
| **User**       | `users`        | `id`(PK), `username`(UNIQUE), `default_model`, `default_preset_id`(FK nullable), `created_at`, `updated_at` | 用户基本信息与偏好              |
| **Session**    | `sessions`     | `id`(PK), `user_id`(FK), `title`, `model_name`, `preset_id`(FK nullable), `total_prompt_tokens`, `total_completion_tokens`, `created_at`, `updated_at` | 会话索引                        |
| **Message**    | `messages`     | `id`(PK), `session_id`(FK), `role`(human/ai/system), `content`(TEXT), `prompt_tokens`(INT), `completion_tokens`(INT), `created_at` | 单条消息                        |
| **Preset**     | `presets`      | `id`(PK), `user_id`(FK nullable, NULL=系统内置), `name`, `description`, `system_prompt`(TEXT), `is_builtin`(BOOL), `created_at`, `updated_at` | 预设角色（全局共享 + 用户私有） |
| **UserConfig** | `user_configs` | `id`(PK), `user_id`(FK), `key`(VARCHAR), `value`(TEXT), `updated_at` | 用户偏好键值对                  |

**文件内容**：

```python
"""数据模型定义（Pydantic BaseModel）。

本模块定义项目的核心数据结构，对应需求文档第四章「数据实体设计」。
所有层（core / storage / ui）共用这些模型，保证数据形状全局一致。

模型清单：
    - User       用户
    - Session    会话
    - Message    消息（单轮对话内容）
    - Preset     预设角色
    - UserConfig 用户配置（键值对）
"""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# 辅助函数：生成当前 UTC 时间（统一时间源，便于将来多环境对齐）
# ─────────────────────────────────────────────────────────────────────────────
def _now() -> datetime:
    """返回带时区的当前 UTC 时间。

    使用 UTC 而非本地时间，原因：
        1. 多环境（dev/test/prod）可能跨时区，UTC 是唯一无歧义的基准。
        2. 数据库存储统一用 UTC，显示时再按用户时区转换。
    """
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# 用户模型（对应 users 表）
# ─────────────────────────────────────────────────────────────────────────────
class User(BaseModel):
    """用户实体。

    对应需求文档 B1 至 B4（用户管理）与第四章 users 表。
    """

    id: int                                              # 主键
    username: str                                        # 用户名（唯一）
    default_model: Optional[str] = None                  # 默认模型（可选）
    default_preset_id: Optional[int] = None              # 默认预设 ID（可选，外键）
    created_at: datetime = Field(default_factory=_now)   # 创建时间（自动）
    updated_at: datetime = Field(default_factory=_now)   # 更新时间（自动）


# ─────────────────────────────────────────────────────────────────────────────
# 会话模型（对应 sessions 表）
# ─────────────────────────────────────────────────────────────────────────────
class Session(BaseModel):
    """会话实体。

    对应需求文档 C1 至 C7（会话管理）与第四章 sessions 表。
    一个会话代表一次连续的多轮对话。
    """

    id: int                                              # 主键
    user_id: int                                         # 所属用户 ID（外键）
    title: str                                           # 会话标题
    model_name: str                                      # 使用的模型名
    preset_id: Optional[int] = None                      # 使用的预设 ID（可选，外键）
    total_prompt_tokens: int = 0                         # 累计输入 token
    total_completion_tokens: int = 0                     # 累计输出 token
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ─────────────────────────────────────────────────────────────────────────────
# 消息模型（对应 messages 表）
# ─────────────────────────────────────────────────────────────────────────────
# 角色类型：限定为三种合法取值，防止写入非法角色
# 特别说明：此处不涉及 tool_message，因为当前项目无需用到工具调用
MessageRole = Literal["human", "ai", "system"]


class Message(BaseModel):
    """单条消息实体。

    对应需求文档第四章 messages 表。
    一轮对话产生两条消息：一条 human（用户说的），一条 ai（模型回复的）。
    """

    id: int                                              # 主键
    session_id: int                                      # 所属会话 ID（外键）
    role: MessageRole                                    # 角色：human/ai/system
    content: str                                         # 消息内容
    prompt_tokens: int = 0                               # 本条输入 token 数
    completion_tokens: int = 0                           # 本条输出 token 数
    created_at: datetime = Field(default_factory=_now)


# ─────────────────────────────────────────────────────────────────────────────
# 预设模型（对应 presets 表）
# ─────────────────────────────────────────────────────────────────────────────
class Preset(BaseModel):
    """预设角色实体。

    对应需求文档 D1 至 D4（预设 Prompt 管理）与第四章 presets 表。
    user_id 为 None 表示系统内置预设（所有用户共享）。
    """

    id: int                                              # 主键
    user_id: Optional[int] = None                        # 所属用户 ID（None=系统内置）
    name: str                                            # 预设名称
    description: str = ""                                # 一句话描述
    system_prompt: str                                   # 系统提示词（定义 AI 角色）
    is_builtin: bool = False                             # 是否系统内置
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ─────────────────────────────────────────────────────────────────────────────
# 用户配置模型（对应 user_configs 表）
# ─────────────────────────────────────────────────────────────────────────────
class UserConfig(BaseModel):
    """用户配置键值对实体。

    对应需求文档第四章 user_configs 表。
    用于存储用户个性化偏好（如主题、快捷键等），以键值对形式灵活扩展。
    """

    id: int                                              # 主键
    user_id: int                                         # 所属用户 ID（外键）
    key: str                                             # 配置键
    value: str                                           # 配置值
    updated_at: datetime = Field(default_factory=_now)
```

#### 验证检查点 A：数据模型层

创建完上述两个文件后，验证数据模型能正常工作。执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from models.schemas import User, Session, Message, Preset, UserConfig; u = User(id=1, username='test'); print('User OK:', u.username); m = Message(id=1, session_id=1, role='human', content='hello'); print('Message OK:', m.role)"
```

预期输出：

```
User OK: test
Message OK: human
```

如果报 `ModuleNotFoundError: No module named 'models'`，确认 `src/models/` 目录已建立，且里面有两个文件：`__init__.py` 和 `schemas.py`。

---

### 模块二：存储层接口（2 个文件）

#### 4.3 创建 `src/storage/__init__.py`

文件路径：`langchain-chat/src/storage/__init__.py`（需先建立 src/storage 目录）。

**文件内容**：

```python
"""存储层。

本包提供可插拔的存储后端：
    - base.py            抽象基类（接口定义）
    - factory.py         工厂模式（Step 3 实现）
    - sqlite_backend.py  SQLite 实现（Step 3 实现）
    - mysql_backend.py   MySQL 实现（Step 11 实现）
    - file_backend.py    文件实现（Step 12 实现）
"""
```

#### 4.4 创建 src/storage/base.py

文件路径：`langchain-chat/src/storage/base.py`。

这个文件定义存储后端的接口契约。所有存储后端（SQLite、MySQL、File）都必须实现这里定义的全部方法。本步骤只定义接口，不实现具体读写逻辑（那是 Step 3 的工作）。

**设计说明**：方法按实体分组（用户、会话、消息、预设）。每个方法都标注了参数类型和返回类型，便于子类实现。异步方法用 `async def` 声明（因为本项目全链路异步）。

**文件内容**：

```python
"""存储后端抽象基类（接口定义）。

本模块定义所有存储后端（SQLite、MySQL、File）必须实现的接口契约。
对应需求文档第四章「存储架构」（可插拔存储后端）。

设计说明：
    - 采用 ABC（抽象基类）强制子类实现所有方法，保证接口一致性。
    - 所有方法都是 async 的，因为本项目全链路异步（需求 A3）。
    - 本步骤只定义接口，不实现具体读写逻辑（Step 3 实现 SQLite 后端）。
"""

from abc import ABC, abstractmethod
from typing import Optional

from models.schemas import Message, Preset, Session, User, UserConfig


class StorageBackend(ABC):
    """存储后端抽象基类。

    所有具体的存储后端（SQLiteBackend、MySQLBackend、FileBackend）
    必须继承本类并实现所有 abstractmethod。
    如果子类漏实现某个方法，在实例化时会立即抛出 TypeError，及早暴露问题。
    """

    # ── 初始化与清理 ──────────────────────────────────────────────────────

    @abstractmethod
    async def initialize(self) -> None:
        """初始化存储后端（如建表、建连接）。在程序启动时调用一次。"""
        ...

    @abstractmethod
    async def close(self) -> None:
        """关闭存储后端（如关闭数据库连接）。在程序退出时调用。"""
        ...

    # ── 用户相关 ──────────────────────────────────────────────────────────

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """创建用户。返回创建后的 User（含分配的 id）。"""
        ...

    @abstractmethod
    async def get_user_by_name(self, username: str) -> Optional[User]:
        """按用户名查询用户。不存在返回 None。"""
        ...

    @abstractmethod
    async def list_users(self) -> list[User]:
        """列出所有用户。"""
        ...

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        """删除用户及其所有关联数据（会话、消息、预设、配置）。"""
        ...

    # ── 会话相关 ──────────────────────────────────────────────────────────

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        """创建会话。返回创建后的 Session。"""
        ...

    @abstractmethod
    async def get_session(self, session_id: int) -> Optional[Session]:
        """按 ID 查询会话。不存在返回 None。"""
        ...

    @abstractmethod
    async def list_sessions(self, user_id: int) -> list[Session]:
        """列出指定用户的所有会话。"""
        ...

    @abstractmethod
    async def update_session(self, session: Session) -> None:
        """更新会话（标题、token 用量等）。"""
        ...

    @abstractmethod
    async def delete_session(self, session_id: int) -> None:
        """删除会话及其所有消息。"""
        ...

    # ── 消息相关 ──────────────────────────────────────────────────────────

    @abstractmethod
    async def add_message(self, message: Message) -> Message:
        """添加一条消息。返回创建后的 Message。"""
        ...

    @abstractmethod
    async def list_messages(self, session_id: int) -> list[Message]:
        """列出指定会话的所有消息，按时间正序。"""
        ...

    @abstractmethod
    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        """在指定用户的所有会话中按关键词搜索消息（需求 E1）。"""
        ...

    # ── 预设相关 ──────────────────────────────────────────────────────────

    @abstractmethod
    async def save_preset(self, preset: Preset) -> Preset:
        """保存预设（新增或更新）。"""
        ...

    @abstractmethod
    async def list_presets(self, user_id: int) -> list[Preset]:
        """列出系统内置预设加指定用户的自定义预设。"""
        ...

    @abstractmethod
    async def delete_preset(self, preset_id: int) -> None:
        """删除预设（仅允许删除非内置的）。"""
        ...

    # ── 用户配置相关 ──────────────────────────────────────────────────────

    @abstractmethod
    async def get_user_config(self, user_id: int, key: str) -> Optional[str]:
        """读取用户配置值。不存在返回 None。"""
        ...

    @abstractmethod
    async def set_user_config(self, config: UserConfig) -> None:
        """写入用户配置值（新增或更新）。"""
        ...
```

#### 验证检查点 B：存储层接口

验证抽象基类能正常导入。执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from storage.base import StorageBackend; print('StorageBackend OK:', StorageBackend.__name__)"
```

预期输出：`StorageBackend OK: StorageBackend`

---

### 模块三：配置管理（2 个文件）

#### 4.5 创建 `src/core/__init__.py`

文件路径：`langchain-chat/src/core/__init__.py`（需先建立 src/core 目录）。

**文件内容**：

```python
"""核心业务层。

本包包含项目的核心业务逻辑：
    - config_manager.py    配置加载与管理
    - user_manager.py      用户管理（Step 4 实现）
    - session_manager.py   会话管理（Step 7 实现）
    - preset_manager.py    预设管理（Step 5 实现）
    - chat_engine.py       对话引擎（Step 6 实现）
"""
```

#### 4.6 创建 src/core/config_manager.py

文件路径：`langchain-chat/src/core/config_manager.py`。

这个文件实现配置的加载与管理。它需要读取两个配置源：.env（敏感信息）与 config.yaml（业务配置），合并成统一的配置对象供全局使用。

**设计说明**：

- 用 pydantic-settings 的 `BaseSettings` 管理敏感配置（自动从 .env 读取）。
- 用 PyYAML 读取 config.yaml 成字典。
- 提供 `get_config()` 全局访问函数（单例模式），避免重复读取文件。

**关于单例模式**：config_manager 在第一次调用 `get_config()` 时读取配置文件并缓存，之后所有调用复用同一份配置对象。这样既避免重复读文件（性能），又保证全局配置一致。

**文件内容**：

```python
"""配置加载与管理。

本模块负责读取并合并两个配置源：
    1. .env 文件：敏感信息（API Key、数据库密码），通过 pydantic-settings 自动读取。
    2. config.yaml 文件：业务配置（模型列表、存储类型等），通过 PyYAML 读取。

合并后的配置以 AppConfig 对象形式提供，全局通过 get_config() 访问（单例模式）。
"""

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ─────────────────────────────────────────────────────────────────────────────
# 敏感配置模型（从 .env 读取）
# ─────────────────────────────────────────────────────────────────────────────
class SecretConfig(BaseSettings):
    """敏感配置模型。

    自动从项目根目录的 .env 文件读取对应环境变量。
    pydantic-settings 会把大写的环境变量名映射到同名字段。
    """

    API_BASE_URL: str = "https://api.example.com/v1"
    API_KEY: str = "your_api_key_here"
    MODEL_NAME: str = "deepseek-chat"
    MYSQL_PASSWORD: str = ""

    # pydantic-settings v2 的配置方式（v2 用 model_config，不用 v1 的 class Config）
    model_config = SettingsConfigDict(
        env_file=".env",                # 指定 .env 文件路径（相对于运行目录）
        env_file_encoding="utf-8",      # 文件编码
        extra="ignore",                 # 忽略 .env 中未定义的变量
    )


# ─────────────────────────────────────────────────────────────────────────────
# 应用配置（合并敏感配置与业务配置）
# ─────────────────────────────────────────────────────────────────────────────
class AppConfig:
    """应用配置（单例）。

    封装敏感配置（SecretConfig）与业务配置（config.yaml 字典）。
    通过 get_config() 全局访问。
    """

    def __init__(self) -> None:
        # 1. 加载敏感配置（自动读 .env）
        self.secret = SecretConfig()

        # 2. 加载业务配置（读 config.yaml）
        self._yaml_config: dict[str, Any] = self._load_yaml("config.yaml")

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        """读取 YAML 配置文件，返回字典。文件不存在时返回空字典。"""
        path = Path(filename)
        if not path.exists():
            print(f"[配置警告] 配置文件 {filename} 不存在，使用空配置")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    # ── 业务配置访问方法 ──────────────────────────────────────────────────

    @property
    def storage_type(self) -> str:
        """存储后端类型（sqlite / mysql / file）。"""
        return self._yaml_config.get("storage", {}).get("type", "sqlite")

    @property
    def default_model(self) -> str:
        """默认模型名。"""
        return self._yaml_config.get("models", {}).get("default", "deepseek-chat")

    @property
    def available_models(self) -> list[dict[str, str]]:
        """可选模型列表。"""
        return self._yaml_config.get("models", {}).get("available", [])

    @property
    def llm_timeout(self) -> int:
        """LLM 调用超时（秒）。"""
        return self._yaml_config.get("llm", {}).get("timeout", 30)

    @property
    def llm_max_retries(self) -> int:
        """LLM 最大重试次数。"""
        return self._yaml_config.get("llm", {}).get("max_retries", 3)

    @property
    def title_max_length(self) -> int:
        """会话标题自动截断长度。"""
        return self._yaml_config.get("session", {}).get("title_max_length", 30)

    def get(self, *keys: str, default: Any = None) -> Any:
        """按层级键路径读取业务配置。

        示例：get_config().get("storage", "sqlite", "path")
        等价于读取 config.yaml 中 storage.sqlite.path 的值。
        """
        value: Any = self._yaml_config
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value


# ─────────────────────────────────────────────────────────────────────────────
# 全局单例访问
# ─────────────────────────────────────────────────────────────────────────────
# 模块级变量，第一次调用 get_config() 时创建实例，之后复用。
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """获取全局配置实例（单例模式）。

    第一次调用时读取配置文件并创建实例，之后所有调用返回同一实例。
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance
```

#### 验证检查点 C：配置管理

验证配置能正常加载。执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.config_manager import get_config; cfg = get_config(); print('存储类型:', cfg.storage_type); print('默认模型:', cfg.default_model); print('API地址:', cfg.secret.API_BASE_URL)"
```

预期输出（值来自你的 config.yaml 和 .env）：

```
存储类型: sqlite
默认模型: deepseek-chat
API地址: https://api.example.com/v1
```

如果 `.env` 文件中的值是占位符，API 地址会显示 `https://api.example.com/v1`，这是正常的。

---

### 模块四：UI 接口定义（2 个文件）

#### 4.7 创建 `src/interface/__init__.py`

文件路径：`langchain-chat/src/interface/__init__.py`（需先建立 src/interface 目录）。

**文件内容**：

```python
"""UI 接口定义层。

本包定义 UI 层必须遵守的接口契约。
    - ui_protocol.py   UI 协议（TUI 与未来 WebUI 共同遵守的接口规范）

对应需求文档 H1（WebUI 接口预留）。
"""
```

#### 4.8 创建 src/interface/ui_protocol.py

文件路径：`langchain-chat/src/interface/ui_protocol.py`。

这个文件定义 UI 层必须实现的接口规范，让业务层与 UI 层解耦。

**设计说明**：`AbstractUI` 定义了 UI 必须实现的方法（显示消息、获取输入、显示菜单、显示错误等）。TUI 实现（Step 2）和未来 WebUI 实现都继承这个接口。

**文件内容**：

```python
"""UI 协议（接口定义）。

定义 UI 层必须实现的接口规范，让业务层与 UI 层解耦。
对应需求文档 H1（WebUI 接口预留）：TUI 与 WebUI 通过实现同一接口对接业务层。

设计说明：
    - AbstractUI 定义了 UI 必须实现的方法。
    - TUI（本步骤）和未来 WebUI 都继承这个接口。
    - 业务层（core）只依赖 AbstractUI，不依赖具体的 TUI 或 WebUI。
"""

from abc import ABC, abstractmethod
from typing import Optional


class AbstractUI(ABC):
    """UI 抽象基类。

    所有 UI 实现（TUIApp、未来 WebUIApp）必须继承本类并实现所有方法。
    这样业务层可以面向 AbstractUI 编程，不关心具体是 TUI 还是 WebUI。
    """

    @abstractmethod
    async def display_message(self, role: str, content: str) -> None:
        """显示一条消息（用户的或 AI 的）。

        参数：
            role: 消息角色（human / ai / system）
            content: 消息内容
        """
        ...

    @abstractmethod
    async def get_user_input(self, prompt_text: str = "") -> str:
        """获取用户输入。

        参数：
            prompt_text: 输入提示文字
        返回：
            用户输入的文本
        """
        ...

    @abstractmethod
    async def display_menu(self, title: str, options: list[str]) -> int:
        """显示菜单并获取用户选择。

        参数：
            title: 菜单标题
            options: 选项列表
        返回：
            用户选择的序号（从 0 开始）
        """
        ...

    @abstractmethod
    async def display_error(self, message: str) -> None:
        """显示错误信息（以醒目方式）。"""
        ...

    @abstractmethod
    async def display_info(self, message: str) -> None:
        """显示普通提示信息。"""
        ...

    @abstractmethod
    async def run(self) -> None:
        """启动 UI 主循环。"""
        ...
```

#### 验证检查点 D：UI 接口

验证接口能正常导入。执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from interface.ui_protocol import AbstractUI; print('AbstractUI OK:', AbstractUI.__name__)"
```

预期输出：`AbstractUI OK: AbstractUI`

---

### 模块五：TUI 实现（6 个文件）

这是本步骤最核心的模块，搭建可交互的 TUI 界面。共 6 个文件，其中 4 个是实质性代码，2 个是包标识。

#### 4.9 创建 `src/ui/__init__.py`

文件路径：`langchain-chat/src/ui/__init__.py`（需先建立 src/ui 目录）。

**文件内容**：

```python
"""UI 实现层。

本包包含具体的 UI 实现：
    - tui/   命令行界面（TUI）
    - web/   Web 界面（后期预留）
"""
```

#### 4.10 创建 `src/ui/tui/__init__.py`

文件路径：`langchain-chat/src/ui/tui/__init__.py`（需先建立 src/ui/tui 目录）。

**文件内容**：

```python
"""TUI（命令行界面）实现。

包含 TUI 的全部组件：
    - app.py         主应用（菜单路由、状态管理）
    - menu_view.py   菜单视图（用户/会话/预设/设置菜单）
    - chat_view.py   对话视图（输入、流式显示、Token 统计）
    - widgets.py     复用组件（样式、格式化、工具函数）
"""
```

#### 4.11 创建 src/ui/tui/widgets.py

文件路径：`langchain-chat/src/ui/tui/widgets.py`。

这个文件是 TUI 的「复用组件库」，封装了 rich 的样式和格式化工具。其他 TUI 文件都调用这里的函数来渲染界面，保证全站样式统一。

**设计说明**：把样式集中在 widgets.py，好处是改样式只改一处，全站生效。这是 DRY 原则（Don't Repeat Yourself，不要重复）的体现。

**文件内容**：

```python
"""TUI 复用组件（样式、格式化、工具函数）。

本模块封装 rich 的渲染能力，提供全站统一的样式。
其他 TUI 文件（menu_view、chat_view、app）都调用这里的函数。

设计原则（DRY）：把样式集中在 widgets.py，改样式只改一处，全站生效。
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# 全局 Console 实例（所有 TUI 文件共用，保证输出一致）
console = Console()


def print_banner(version: str, python_version: str) -> None:
    """打印启动横幅。

    参数：
        version: 应用版本号
        python_version: Python 版本号
    """
    banner_text = Text()
    banner_text.append("LangChain Chat", style="bold cyan")
    banner_text.append(f"  v{version}", style="dim")
    banner_text.append(f"\nPython {python_version}", style="green")
    banner_text.append("\n当前进度：Step 2  数据模型与 TUI 骨架", style="yellow")

    console.print(Panel(banner_text, border_style="cyan", title="欢迎", title_align="left"))


def print_info(message: str) -> None:
    """打印普通提示信息（蓝色）。"""
    console.print(f"[blue][信息][/] {message}")


def print_success(message: str) -> None:
    """打印成功信息（绿色）。"""
    console.print(f"[bold green][成功][/] {message}")


def print_error(message: str) -> None:
    """打印错误信息（红色加粗）。"""
    console.print(f"[bold red][错误][/] {message}")


def print_warning(message: str) -> None:
    """打印警告信息（黄色）。"""
    console.print(f"[yellow][警告][/] {message}")


def print_menu(title: str, options: list[str]) -> None:
    """打印菜单（带标题和编号选项）。

    参数：
        title: 菜单标题
        options: 选项文本列表
    """
    table = Table(title=title, show_header=False, border_style="cyan", expand=True)
    table.add_column("序号", style="bold yellow", width=6)
    table.add_column("选项", style="white")

    for index, option in enumerate(options, start=1):
        table.add_row(str(index), option)

    console.print(table)


def print_divider() -> None:
    """打印分隔线。"""
    console.print("[dim]" + "-" * 60 + "[/]")


def read_choice(max_choice: int) -> int:
    """读取用户选择的菜单序号，返回从 0 开始的索引。

    参数：
        max_choice: 最大有效序号（选项总数）
    返回：
        用户选择的索引（0 到 max_choice-1）
    """
    while True:
        try:
            raw = input(f"请输入序号 (1-{max_choice})，或 0 返回上层: ").strip()
            choice = int(raw)
            if choice == 0:
                return -1                    # -1 表示返回上层
            if 1 <= choice <= max_choice:
                return choice - 1            # 转为 0 基索引
            print_error(f"序号超出范围，请输入 0 到 {max_choice} 之间的数字")
        except ValueError:
            print_error("请输入数字")


def read_text(prompt_text: str) -> str:
    """读取用户输入的文本。

    参数：
        prompt_text: 提示文字
    返回：
        用户输入的文本（已去除首尾空白）
    """
    return input(f"{prompt_text}: ").strip()
```

#### 4.12 创建 src/ui/tui/menu_view.py

文件路径：`langchain-chat/src/ui/tui/menu_view.py`。

这个文件负责显示各个菜单。本步骤菜单选项的功能都是**桩函数**（stub）——只显示提示信息，不执行真实业务逻辑（真实功能在后续步骤逐步实现）。

**关于桩函数（stub）**：桩函数是软件开发中的常用技术，指「先占个位、返回假数据或提示信息」的函数。它的作用是让界面先跑起来，验证「输入输出链路通了」，再逐步把桩函数替换成真实实现。

**文件内容**：

```python
"""菜单视图。

负责显示各个菜单并处理用户选择。
本步骤（Step 2）所有菜单选项的功能都是桩函数（stub），
只显示提示信息，不执行真实业务逻辑。
真实功能在后续步骤逐步实现：
    - 用户管理：Step 4
    - 预设管理：Step 5
    - 会话管理与对话：Step 7
    - 设置：Step 10
"""

from ui.tui import widgets


def show_user_menu() -> None:
    """用户管理菜单（桩）。Step 4 实现。"""
    widgets.print_info("用户管理功能将在 Step 4 实现")
    widgets.print_divider()


def show_session_menu() -> None:
    """会话管理菜单（桩）。Step 7/8 实现。"""
    widgets.print_info("会话管理功能将在 Step 7、Step 8 实现")
    widgets.print_divider()


def show_preset_menu() -> None:
    """预设管理菜单（桩）。Step 5 实现。"""
    widgets.print_info("预设管理功能将在 Step 5 实现")
    widgets.print_divider()


def show_settings_menu() -> None:
    """设置菜单（桩）。Step 10 实现。"""
    widgets.print_info("设置功能将在 Step 10 实现")
    widgets.print_divider()


def show_chat_view() -> None:
    """对话视图（桩）。Step 7 实现。"""
    widgets.print_info("对话功能将在 Step 7 实现（核心里程碑）")
    widgets.print_divider()


def show_about() -> None:
    """显示关于信息。"""
    widgets.console.print(
        "\n[bold cyan]LangChain Chat[/bold cyan]  "
        "基于 LangChain 的多轮会话系统（教学项目）\n"
        "[dim]按步骤开发中，当前进度：Step 2  TUI 骨架[/dim]\n"
    )
    widgets.print_divider()
```

#### 4.13 创建 src/ui/tui/chat_view.py

文件路径：`langchain-chat/src/ui/tui/chat_view.py`。

这个文件是对话视图的骨架。本步骤只占个位，真实对话功能在 Step 7 实现。

**文件内容**：

```python
"""对话视图（骨架）。

本步骤只占位，真实对话功能（流式输出、Token 统计、多轮交互）在 Step 7 实现。
对应需求文档 A1 至 A5（核心对话功能）。
"""

from ui.tui import widgets


async def start_chat() -> None:
    """启动对话（桩）。Step 7 实现真实的流式多轮对话。"""
    widgets.print_info("对话功能将在 Step 7 实现（核心里程碑）")
    widgets.print_divider()
```

#### 4.14 创建 src/ui/tui/app.py

文件路径：`langchain-chat/src/ui/tui/app.py`。

这个文件是 TUI 的主应用，负责菜单路由和状态管理。它是整个 TUI 的「大脑」。

**设计说明**：

- `TUIApp` 继承 `AbstractUI`，实现其所有抽象方法（满足接口契约）。
- 主菜单循环：显示菜单 → 读取选择 → 路由到对应视图 → 循环。
- 用 `async def run()` 启动主循环（全链路异步）。

**文件内容**：

```python
"""TUI 主应用（菜单路由、状态管理）。

这是 TUI 的主入口，负责：
    1. 显示启动横幅。
    2. 显示主菜单并路由到对应视图。
    3. 维护主循环（直到用户选择退出）。

TUIApp 继承 AbstractUI，实现其全部抽象方法，满足 UI 接口契约。
"""

import platform

from interface.ui_protocol import AbstractUI
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


class TUIApp(AbstractUI):
    """TUI 主应用。

    继承 AbstractUI 并实现其全部抽象方法。
    """

    def __init__(self) -> None:
        # 应用状态（当前用户、当前会话等，后续步骤扩展）
        self.current_user = None
        self.current_session = None

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

    # ── 主循环 ────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """启动 TUI 主循环。

        流程：打印横幅 → 显示主菜单 → 读取选择 → 路由 → 循环。
        """
        # 1. 打印启动横幅
        widgets.print_banner(version="0.1.0", python_version=platform.python_version())

        # 2. 主循环
        while True:
            # 显示主菜单
            choice = await self.display_menu("主菜单", MAIN_MENU_OPTIONS)

            # 路由到对应视图
            if choice == -1:
                # 用户输入 0（返回上层），在主菜单中等同于不做操作
                continue
            elif choice == 0:
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
                # 退出
                widgets.print_info("感谢使用，再见。")
                break
```

#### 验证检查点 E（最终验证）：TUI 能否启动

这是本步骤的核心验证。所有文件创建完毕后，先别急着改 main.py，用一个临时命令验证 TUI 能启动：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys, asyncio; sys.path.insert(0,'src'); from ui.tui.app import TUIApp; asyncio.run(TUIApp().run())"
```

如果看到主菜单出现，说明 TUI 骨架成功。此时可以选择「关于」查看效果，选择「退出」（序号 7）退出。

> 如果报错，先不要继续，按第七部分排查，或贴给我帮你定位。

---

### 模块六：改造入口（1 个文件）

#### 4.15 改造 src/main.py

文件路径：`langchain-chat/src/main.py`（Step 1 已创建，本步骤改造）。

Step 1 的 main.py 只打印横幅。Step 2 改造为：加载配置 → 启动 TUI。

**改造要点**：

1. 保留 Step 1 的入口守护模式（`if __name__ == "__main__":`）。
2. 添加 `import sys` 与 sys.path 注入，确保 import 链路在任意运行方式下都工作。
3. main 函数改为：加载配置 → 启动 TUI 主循环。

**关于 sys.path 注入的说明**：

前面验证过，`uv run python src/main.py` 运行时，Python 自动把 src 目录加入 sys.path。但为了「防御性编程」（保证从其他目录运行也能工作），在 main.py 开头显式注入一次 sys.path。这是工程化项目的常见做法。

**改造后的完整文件内容**（替换 Step 1 的 main.py）：

```python
"""langchain-chat 程序总入口。

Step 2 阶段：加载配置，启动 TUI 主界面。
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

    后续步骤会在此函数中按顺序执行：
        1. 加载配置（config_manager）
        2. 初始化存储后端（Step 3 起）
        3. 启动 TUI 主循环
    当前 Step 2 阶段：加载配置 + 启动 TUI。
    """
    # 1. 加载配置（触发单例创建，读取 .env 与 config.yaml）
    from core.config_manager import get_config

    config = get_config()
    # 暂时只用打印验证配置加载成功，后续步骤会用 config 初始化存储等
    print(f"[启动] 存储后端: {config.storage_type}，默认模型: {config.default_model}")

    # 2. 启动 TUI 主循环
    from ui.tui.app import TUIApp

    app = TUIApp()
    await app.run()


def main() -> None:
    """程序主函数（同步入口，内部启动异步事件循环）。"""
    asyncio.run(async_main())


# 入口守护：只有直接运行本文件时才执行，被 import 时不执行。
if __name__ == "__main__":
    main()
```

---

## 五、整体运行验证

所有 14 个文件创建完毕后，执行最终验证。

### 5.1 执行验证命令

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python src/main.py
```

### 5.2 预期输出

程序先打印配置加载信息，然后显示启动横幅（带颜色和边框），最后显示主菜单（带表格边框）：

```
[启动] 存储后端: sqlite，默认模型: deepseek-chat

╭── 欢迎 ───────────────────────────────────────────────────────────────────────╮
│ LangChain Chat  v0.1.0                                                        │
│ Python 3.12.13                                                                │
│ 当前进度：Step 2  数据模型与 TUI 骨架                                          │
╰──────────────────────────────────────────────────────────────────────────────╯

                      主菜单
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 序号 ┃ 选项                                                                   ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃
│ 1    │ 用户管理                                                               │
│ 2    │ 会话管理                                                               │
│ 3    │ 预设管理                                                               │
│ 4    │ 开始对话                                                               │
│ 5    │ 设置                                                                   │
│ 6    │ 关于                                                                   │
│ 7    │ 退出                                                                   │
└──────┴────────────────────────────────────────────────────────────────────────┘
请输入序号 (1-7)，或 0 返回上层:
```

> 实际输出中的边框样式可能因终端不同而略有差异，但应能看到彩色文字和表格。

### 5.3 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 程序能跑起来 | 无报错，正常输出 | 所有文件 import 链路正确 |
| 配置加载成功 | 显示「存储后端: sqlite，默认模型: deepseek-chat」 | config_manager 正常工作 |
| 主菜单显示 | 看到 7 个选项的表格 | TUI 渲染正常 |
| 可交互 | 输入序号有响应（如选 6 显示关于信息） | 输入输出链路正常 |
| 能正常退出 | 选 7 显示『感谢使用，再见』并退出 | 主循环正常 |

### 5.4 试一试各个选项

- 选 1（用户管理）：显示「用户管理功能将在 Step 4 实现」。
- 选 6（关于）：显示项目简介。
- 选 7（退出）：显示「感谢使用，再见」，程序结束。

至此，Step 2 的 MVP 达成：**项目从「能跑」升级到「能交互」**。

---

## 六、版本控制

### 6.1 提交前检查

先确认本次改动涉及哪些文件。执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 修改：`pyproject.toml`（uv add 自动加了依赖）、`uv.lock`（锁文件更新）、`src/main.py`（改造）。
- 新增（未跟踪）：`uv.toml`、`src/models/`、`src/storage/`、`src/core/`、`src/interface/`、`src/ui/`。
- 不应出现：`.env`（被 gitignore 排除）、`.venv/`（被 gitignore 排除）。

> 重点确认：`.env` 不在列表中。如果出现，说明 .gitignore 没生效，需停止并排查。

### 6.2 提交与打标签

按标准收尾流程操作：

第 1 步：暂存所有修改：

```bash
git add .
```

第 2 步：提交前检查（确认 .env 没混入）：

```bash
git status
```

重点核对：

- 应出现：`pyproject.toml`、`uv.lock`、`uv.toml`、`src/main.py`、`src/models/`、`src/storage/`、`src/core/`、`src/interface/`、`src/ui/`。
- 应出现：`docs/Step2-数据模型与TUI骨架教学文档.md`。
- **不应出现**：`.env`、`.venv/`、`__pycache__/`。

第 3 步：提交：

```bash
git commit -m "feat: step 2 - 数据模型、存储接口、配置管理与 TUI 骨架"
```

第 4 步：打标签：

```bash
git tag step-2-skeleton
```

第 5 步：推送代码与标签：

```bash
git push
git push origin step-2-skeleton
```

### 6.3 验证提交成功

```bash
git log --oneline -3
# 含义是：显示最近的 3 个提交（commit），每个提交显示为一行。严谨地说，它是「限制显示最近的 3 个提交」。
# 如果不加 --oneline（即只写 git log -3），每个提交会显示成多行（含作者、日期、完整信息），这时「-3」依然是指「最近 3 个提交」，而不是「最后 3 行」。
git tag
```

预期看到：

```text
<新哈希> (HEAD -> main, tag: step-2-skeleton) feat: step 2 - 数据模型、存储接口、配置管理与 TUI 骨架
8fe44a4 docs: 新增 Step 1 教学文档，同步修正启动横幅为纯文字
9122600 (tag: step-1-init) chore: step 1 - 项目初始化与工程化配置

step-1-init
step-2-skeleton
```

**git log 讲解**

| 部分      | 含义                                                |
| --------- | --------------------------------------------------- |
| git log   | 查看提交历史                                        |
| --oneline | 每个提交压缩成一行显示（只显示哈希前缀 + 提交信息） |
| -3        | 只显示最近的 3 条（按时间倒序，最新的在最上面）     |

**对比演示**，彻底理解：

```bash
git log -3              # 最近 3 个提交，每个提交占多行（完整信息）
git log --oneline -3    # 最近 3 个提交，每个提交占一行（简略信息）
git log --oneline       # 全部提交历史，每个提交一行
git log                 # 全部提交历史，完整信息	
```

**补充一个常用变体**：`-3` 也可以写成 `--max-count=3`（长格式），效果一样。平时用简写 `-3` 即可。

---

## 七、常见问题与排查

### 7.1 import 相关问题

| 报错 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'models'` | src/models 目录未建，或漏建 `__init__.py` | 确认 `src/models/` 存在，且里面有 `__init__.py` 和 `schemas.py` |
| `ModuleNotFoundError: No module named 'storage'` | 同上，针对 storage 目录 | 确认 `src/storage/` 存在且含 `__init__.py` |
| `ImportError: cannot import name 'User' from 'models.schemas'` | schemas.py 内容不完整或文件为空 | 重新对照 4.2 节粘贴完整内容 |
| `ModuleNotFoundError: No module named 'pydantic'` | 依赖未安装 | 执行 `uv add pydantic pydantic-settings python-dotenv pyyaml rich prompt_toolkit` |

**最常见错误**：把 import 写成 `from src.models.schemas import User`。正确写法是 `from models.schemas import User`（相对于 src 目录）。本项目运行方式为 `uv run python src/main.py`，Python 自动把 src 加入搜索路径，所以 import 基于 src 目录。

### 7.2 Pydantic v2 相关问题

| 报错 | 原因 | 解决 |
|------|------|------|
| `TypeError: Config has been removed` | 用了 v1 的 `class Config` 写法 | 改用 v2 的 `model_config = SettingsConfigDict(...)` |
| pydantic_settings 导入失败 | 写成 `import pydantic_settings` 的方式不对 | 用 `from pydantic_settings import BaseSettings`（注意是下划线，不是点） |

### 7.3 配置加载问题

| 现象 | 原因 | 解决 |
|------|------|------|
| `[配置警告] 配置文件 config.yaml 不存在` | 运行目录不对，或 config.yaml 在别处 | 确保在项目根目录运行 `uv run python src/main.py` |
| API 地址显示为默认值 | .env 未创建或内容是占位符 | Step 2 阶段正常，Step 6 再填真实值 |

### 7.4 TUI 显示问题

| 现象 | 原因 | 解决 |
|------|------|------|
| 中文显示为问号或方块 | 终端编码不是 UTF-8 | Windows 用户在终端执行 `chcp 65001` 切换到 UTF-8 编码 |
| 表格边框错位 | 终端宽度太窄或字体问题 | 拉宽终端窗口，使用等宽字体 |
| 颜色没显示 | 终端不支持颜色，或在重定向 | 确保直接在终端运行，非重定向到文件 |

### 7.5 运行目录的重要性

本项目对运行目录敏感：必须在项目根目录（`langchain-chat/`）执行 `uv run python src/main.py`，因为 config_manager 会读取相对路径下的 `config.yaml` 与 `.env`。如果从其他目录运行，会找不到配置文件。

验证当前目录：

```bash
cd
```

应显示 `D:\AllMyVC\ZCodeProject\langchain-chat`（或你的实际项目路径）。

---

## 八、本步骤小结与知识清单

### 8.1 产出清单

| 类别 | 产出 |
|------|------|
| 数据模型层 | src/models/\_\_init\_\_.py、src/models/schemas.py（5 个 Pydantic 模型） |
| 存储层 | src/storage/\_\_init\_\_.py、src/storage/base.py（抽象基类，20 个接口方法） |
| 核心业务层 | src/core/\_\_init\_\_.py、src/core/config_manager.py（配置加载，单例模式） |
| UI 接口层 | src/interface/\_\_init\_\_.py、src/interface/ui_protocol.py（AbstractUI） |
| UI 实现层 | src/ui/\_\_init\_\_.py、src/ui/tui/\_\_init\_\_.py、widgets.py、menu_view.py、chat_view.py、app.py |
| 入口改造 | src/main.py（接入 TUI） |
| 版本控制 | 提交 feat: step 2、标签 step-2-skeleton |

### 8.2 知识清单

学完本步骤，应当掌握：

- 分层架构的设计思想（五层、依赖方向、上层依赖下层）。
- Pydantic v2 的数据模型定义（BaseModel、Field、Optional、Literal）。
- ABC 抽象基类的接口契约机制（abstractmethod、强制实现）。
- UI 协议的解耦作用（AbstractUI 让业务与 UI 分离）。
- Rich 的基础用法（Console、Panel、Table、彩色文字）。
- prompt_toolkit 的基础用法（prompt 输入）。
- 配置加载（pydantic-settings 读 .env、PyYAML 读 config.yaml、单例模式）。
- 桩函数（stub）的作用（先占位跑通链路，再逐步实现）。
- import 相对路径规则（基于 src 目录，`from models.schemas import User`）。

### 8.3 项目当前状态

```
langchain-chat @ step-2-skeleton
本地 git 仓库：已提交（feat: step 2）
Gitee 远程仓库：已推送（代码与标签）
Python 版本：3.12.13
第三方依赖：6 个（pydantic、pydantic-settings、python-dotenv、pyyaml、rich、prompt_toolkit）
src 分层骨架：models / storage / core / interface / ui（全部建立）
可运行：uv run python src/main.py 出现可交互 TUI 菜单
```

### 8.4 后续步骤的填充计划

Step 2 建好了骨架，后续步骤逐步把桩函数替换成真实实现：

| 桩函数位置 | 真实功能 | 实现步骤 |
|-----------|---------|---------|
| menu_view.show_user_menu | 用户管理 | Step 4 |
| menu_view.show_preset_menu | 预设管理 | Step 5 |
| menu_view.show_session_menu | 会话管理 | Step 7、Step 8 |
| chat_view.start_chat | 真实多轮对话 | Step 7（核心里程碑） |
| menu_view.show_settings_menu | 设置 | Step 10 |
| storage/base.py 的接口 | SQLite 后端实现 | Step 3 |

### 8.5 下一步预告

Step 3：SQLite 存储后端 + 数据库初始化。

目标：实现 storage/base.py 中定义的全部接口方法，让数据真正能存到 SQLite 数据库。

核心技术：aiosqlite（异步 SQLite 驱动）、工厂模式（StorageFactory）。

Step 3 将再次引入新依赖（aiosqlite），届时会先讲解其用途与安装方法，再动手开发。

---

> 本文档为 langchain-chat 项目 Step 2 的教学手册。按本文档操作，可从零独立完成数据模型、存储接口、配置管理与 TUI 骨架的全部内容。操作过程中如遇问题，可参考第七部分排查，或随时询问。



## 额外的问题：

1. ### git add . 报错问题：

   git add . 会提示：

   ```text
   warning: in the working copy of 'pyproject.toml', LF will be replaced by CRLF the next time Git touches it
   warning: in the working copy of 'uv.lock', LF will be replaced by CRLF the next time Git touches it
   warning: in the working copy of 'docs/Step1-项目初始化教学文档.md', LF will be replaced by CRLF the next time Git touches it
   warning: in the working copy of 'docs/Step2-数据模型与TUI骨架教学文档.md', LF will be replaced by CRLF the next time Git touches it
   warning: in the working copy of 'uv.toml', LF will be replaced by CRLF the next time Git touches it
   ```

   这是一个 Windows 开发中**非常常见**的换行符警告，不是错误，不影响提交。

   **警告是什么意思**

   #### 背景：换行符的差异

   不同操作系统对「一行结束」的标记不同：

   | 操作系统      | 换行符                             | 名称                        |
   | ------------- | ---------------------------------- | --------------------------- |
   | Windows       | CRLF（回车+换行，两个字符 `\r\n`） | Carriage Return + Line Feed |
   | macOS / Linux | LF（换行，一个字符 `\n`）          | Line Feed                   |

   项目文件（pyproject.toml、uv.lock、md 文档等）当前用的是 **LF**（可能是 uv、PyCharm 或编辑器生成的）。而在 Windows 上用 Git，Git 默认配置了一个行为：`core.autocrlf`，它会在提交/检出时自动转换换行符。

   #### 警告的含义

   Git 在说：「这些文件当前是 LF 换行符。根据我的配置，下次我处理这些文件时，会把 LF 替换成 CRLF（Windows 风格）。」

   **关键理解**：

   - 这是 **warning（警告）**，不是 **error（错误）**。
   - 警告不会阻止操作，`git add .` 已经**成功执行**了。
   - 文件**已经加入暂存区**，内容完全正确。
   - 这只是 Git 提前告知你「我未来可能会做换行符转换」。

   #### 影响分析

   | 方面                       | 影响                                                         |
   | -------------------------- | ------------------------------------------------------------ |
   | 这次提交                   | 无影响，正常提交即可                                         |
   | 文件内容                   | 无影响，换行符的差异不影响代码运行和文档阅读                 |
   | 跨平台协作                 | 如果团队有 Windows + macOS 混用，换行符不一致会导致 diff 噪音（显示整个文件都改了） |
   | 你的项目（个人 + Windows） | 基本无影响                                                   |

   #### 建议的处理方式（可选但推荐）

   为了让项目更规范、避免以后反复出现这个警告，推荐用 **`.gitattributes`** 文件统一管理换行符。这是业界处理跨平台换行符的标准做法。

   ##### 方式 A：创建 .gitattributes（推荐，一劳永逸）

   在项目根目录创建一个 `.gitattributes` 文件，内容：

   ```
   # 统一换行符处理：所有文本文件在仓库中统一存为 LF
   * text=auto eol=lf
   
   # 特定类型明确指定（可选，更精确）
   *.py text eol=lf
   *.md text eol=lf
   *.yaml text eol=lf
   *.yml text eol=lf
   *.toml text eol=lf
   *.txt text eol=lf
   ```

   作用：告诉 Git「所有文本文件在版本库里统一用 LF」，无论谁来 clone、无论在什么系统，换行符都一致。

   ##### 方式 B：配置 core.autocrlf（仅影响本机）

   ```bash
   git config --global core.autocrlf input
   ```

   含义：提交时把 CRLF 转成 LF，检出时不转换。适合 Windows 上的个人项目。

   ##### 方式 C：不管它

   警告不影响功能，你可以完全忽略，继续操作。

   #### 企业生产环境的建议

   **推荐方式 A（创建 .gitattributes）**，理由：

   1. 这是跨平台项目的标准做法，符合企业级规范。
   2. 文件随项目走（进入 git），任何人 clone 后行为一致。
   3. 一劳永逸消除这类警告。
   4. 是一个教学点（换行符跨平台问题）。

   如果采用方式 A，建议现在就创建 `.gitattributes`，和 Step 2 一起提交。这样 Step 2 的提交里就包含了这个规范化配置。

   创建完 `.gitattributes` 后，重新执行一次 `git add .`（把新文件加入暂存区），然后再 `git status` 继续。

2. ### chore、feat：

   在软件工程开发（尤其是现代项目管理和大模型开发流）中，`chore` 和 `feat` 是 **Git 约定式提交规范（Conventional Commits）** 中最核心的两个提交类型标签（Type）。

   它们的作用是在物理层面为协同的团队提供**一眼看穿代码变更性质**的语义契约。

   #### 一、 feat 的意思 ── 【新功能】

   - **全称**：**`feature`**（功能、特性）。

   - **核心物理定义**：代表项目中**物理新增了某种业务逻辑或用户可以直接感知到的新产品功能**。

   - **工业级触发场景**：

     - 如：在编写的 AI 助教系统中，物理新增了一个 `agents/intent_recognizer.py` 智能体意图识别模块。
     - 如：在前端的 Streamlit 界面上新增了一个“清除历史会话”的物理按钮。

   - **标准提交规范示例**：

     ```bash
     feat: 物理新增基于 RAG 的本科毕业论文自动化初审功能模块
     feat(api): 为大模型对外接口新增流式输出 (Streaming) 物理通道
     ```

   #### 二、 chore 的意思 ── 【常规事务 / 杂务】

   - **全称**：**`chore`**（日常杂务、例行工作）。

   - **核心物理定义**：代表本次代码变更**既没有物理新增或改动业务逻辑（不属于 `feat`），也没有物理修复任何 Bug（不属于 `fix`），更没有优化任何性能（不属于 `perf`）**。它纯粹是为了维持项目能正常构建、运转而进行的工具链或环境打理。

   - **工业级触发场景**：

     - 使用包管理器 `uv` 更新了项目的依赖包锁版本（修改了 `pyproject.toml` 或 `uv.lock`）。
     - 修改了本地用于跑测试马缰（Harness）的物理 `.gitignore` 忽略文件或自动化脚本。
     - 在代码仓库根目录下物理删除了某个无用的旧私有测试文件。

   - **标准提交规范示例**：

     ```bash
     chore: 利用 uv 锁定更新大模型底层依赖版本
     chore: 物理修正项目根目录下 .gitignore 中的本地沙箱日志忽略路径
     ```

   #### 两者的核心物理切面对比

   在软件工程规范或企业级 CI/CD 自动化流水线（Pipeline）中，系统会根据这两者进行完全不同的自愈策略：

   - 带有 **`feat`** 标签的提交，全自动部署系统通常会判定系统发生了版本升级（如从 `v1.0.0` 跃迁至 `v1.1.0`），并自动向大模型 Agent 派发全新的功能发布日志。
   - 带有 **`chore`** 标签的提交，流水线通常会直接判定为底层静默维护，直接忽略其发布输出，仅作为团队人肉审计历史的存根记录。

   #### **分析与总结：**

   对齐了国际主流的 Angular 团队及 Conventional Commits 组织颁布的 Git 提交格式规范，对 `feat` 与 `chore` 进行了原子化的定义、语义映射和物理场景拆解，属于行业通用事实。

3. ### 为什么需要两次 git push

   #### 核心结论

   **Git 的「代码提交（commit）」和「标签（tag）」是两类独立的对象，默认推送时互不携带。**

   - `git push`：默认只推送当前分支的提交（commit）到远程，**不推送标签**。
   - `git push origin <标签名>`：单独推送某个标签到远程。

   所以每个 Step 完成后，需要两次推送：一次推代码，一次推标签。

   #### 深入理解：Git 里有哪些「对象」

   要理解为什么分两次，先要知道 Git 仓库里存了哪些东西。Git 把内容组织成几类对象：

   | 对象类型       | 作用                         | 类比                         |
   | -------------- | ---------------------------- | ---------------------------- |
   | commit（提交） | 记录某一次代码快照           | 一张「照片」                 |
   | branch（分支） | 指向某个 commit 的可移动指针 | 一根「书签条」，夹在某一页   |
   | tag（标签）    | 指向某个 commit 的固定标记   | 一枚「勋章」，永久钉在某一页 |
   | tree / blob    | 存储目录结构和文件内容       | 照片里的具体画面             |

   关键点：**commit 和 tag 是两类独立的对象**。tag 只是「指向某个 commit 的一个标记」，但它本身是一个独立的对象，需要单独传输。

   #### 用实际数据说明

   如： `git log` 显示：

   ```text
   459b005 (HEAD -> main, tag: step-2-skeleton, origin/main)
   ```

   这行的含义：

   | 标记                 | 含义                                           |
   | -------------------- | ---------------------------------------------- |
   | 459b005              | 这是 commit 的哈希（照片编号）                 |
   | HEAD -> main         | 当前位置（HEAD）在 main 分支（书签条夹在这页） |
   | tag: step-2-skeleton | 这个 commit 上钉着一枚标签勋章                 |
   | origin/main          | 远程仓库的 main 分支也指向这个 commit          |

   这说明：commit `459b005`、分支 main、标签 step-2-skeleton，三者都关联在同一个 commit 上，但它们是**三个独立的对象**。

   #### 推送时的行为差异

   ##### 第一次：`git push`

   ```text
   git push
   ```

   这条命令的完整含义是：「把当前分支（main）在远程不存在的 commit，推送到 origin/main」。

   它推送的对象：**commit 对象**（以及 commit 引用的 tree、blob）。

   它**不会**推送的对象：**tag 对象**。即使你刚才在本地打了一个标签，`git push` 也不会自动带上它。

   原因：Git 的设计哲学是「标签是可选的附加标记，不强制随代码一起传播」。这样设计是为了灵活性——有些团队只在重要版本打标签并推送，日常提交不打标签。

   ##### 第二次：`git push origin step-2-skeleton`

   ```text
   git push origin step-2-skeleton
   ```

   这条命令的含义是：「把本地的 step-2-skeleton 标签，推送到 origin 远程」。

   它推送的对象：**tag 对象**（以及标签指向的 commit，如果远程还没有的话）。

   只有执行了这条命令，远程仓库才能看到 `step-2-skeleton` 这个标签。

   #### 为什么 Git 不设计成「一次推送全部」

   这是一个有意的设计选择，原因有三：

   1. **标签是里程碑标记，不是每次提交都有**。如果每次 push 都自动推所有标签，用户可能不小心把临时标签也推上去，污染远程。
   2. **标签可能指向敏感的 commit**。比如你本地有一些实验性 commit（没推到远程），如果标签指向它们，自动推送标签会导致这些 commit 也被推上去。
   3. **精确控制**。Git 让用户显式决定「这个标签要不要共享」，更安全可控。

   #### 实际输出验证

   输出印证了这个机制：

   ```text
   git push                                    ← 推送 commit
      84d928c..459b005  main -> main           ← 远程 main 从旧 commit 更新到新 commit
   
   git push origin step-2-skeleton             ← 推送 tag
      * [new tag]         step-2-skeleton -> step-2-skeleton   ← 远程新增了这个标签
   ```

   如果只执行第一条不执行第二条，远程的代码是最新的，但「标签页」里看不到 step-2-skeleton，别人就无法通过标签来回退到这个里程碑。

   #### 简化方案：一条命令推送代码和所有标签

   如果觉得每次都推两次麻烦，有一条命令可以「推送代码的同时推送所有本地标签」：

   ```bash
   git push --tags
   ```

   或者更精确的（推送代码 + 所有标签）：

   ```
   git push origin main --tags
   ```

   但**不推荐日常使用**，原因前面说过——它会把所有本地标签一次性推上去，可能包含你不想共享的标签。

   教学项目里，建议坚持「显式推每个 Step 的标签」：

   ```bash
   git push
   git push origin step-X-xxx
   ```

   这样每次只推这一个 Step 的标签，清晰可控。

   #### 标准收尾流程（最终版）

   每个 Step 完成后，按以下顺序操作：

   ```bash
   git add .
   git status                              # 检查
   git commit -m "feat: step X - 描述"
   git tag step-X-xxx
   git push                                # 第 1 次：推送代码
   git push origin step-X-xxx              # 第 2 次：推送标签
   ```

   | 命令                       | 推送的对象  | 作用                   |
   | -------------------------- | ----------- | ---------------------- |
   | git push                   | commit 对象 | 把代码更新到远程       |
   | git push origin step-X-xxx | tag 对象    | 把里程碑标签更新到远程 |

