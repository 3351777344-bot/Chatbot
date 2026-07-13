# Step 3：SQLite 存储后端与数据库初始化（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-25
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-3-sqlite`

---

## 阅读说明

本文档是 langchain-chat 项目第三步的完整教学手册。阅读并跟随操作后，你应当能够：

1. 理解数据库在项目中的作用，以及 SQLite 的特点。
2. 理解同步数据库访问与异步数据库访问的区别。
3. 掌握 aiosqlite 的基本用法。
4. 理解工厂模式在存储层中的应用。
5. 理解 SQL 的基础语法（建表、增删改查、外键、级联删除）。
6. 了解软件测试的常见类型，理解冒烟测试的作用。
7. 从零实现一个可用的 SQLite 存储后端，并通过冒烟测试验证。

**本文档的设计原则**（与 Step 1、Step 2 文档一致）：

- 每一个概念都用「3W1H」框架讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，由学习者自行创建文件并粘贴内容。
- 每完成若干文件后设有「验证检查点」，便于及时发现问题。

**完成标志（学完本文档后你应达成的目标）**：

- src/storage/ 下新增 `sqlite_backend.py`（SQLite 后端实现）和 `factory.py`（工厂）。
- 项目根目录新增 `scripts/init_db.py`（数据库初始化脚本）。
- 执行 `uv run python scripts/init_db.py` 能自动创建数据库和 5 张表，并通过一轮冒烟测试。
- 本地 Git 仓库存在提交与标签 `step-3-sqlite`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置回顾与准备](#二前置回顾与准备)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、软件测试基础](#四软件测试基础)
- [五、动手实践：创建源码文件](#五动手实践创建源码文件)
- [六、整体运行验证](#六整体运行验证)
- [七、版本控制](#七版本控制)
- [八、常见问题与排查](#八常见问题与排查)
- [九、本步骤小结与知识清单](#九本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

Step 2 定义了存储层的接口契约（`storage/base.py` 的抽象基类 `StorageBackend`），但那些方法只有声明、没有实现——就像一份「合同」签了字，但还没有具体执行。Step 3 的目标是：**让合同落地**——用 SQLite 实现这份合同里的全部方法，让数据真正能存进数据库、能取出来。

具体而言，本步骤做三件事：

1. 实现 SQLite 存储后端（`sqlite_backend.py`），实现 base.py 里定义的全部 20 个接口方法。
2. 实现存储工厂（`factory.py`），让业务代码能通过配置选择后端。
3. 编写数据库初始化脚本（`scripts/init_db.py`），一键建库建表并跑冒烟测试。

本步骤**专注存储层，不接入 TUI**。main.py 暂时不动（它现在启动 TUI 菜单，菜单还是桩函数）。存储层接入业务和界面，留到后续步骤（Step 4 用户管理）。

### 1.2 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 2 完成的分层骨架（标签 step-2-skeleton），含 base.py 接口定义 |
| 输出 | 可用的 SQLite 存储后端 + 数据库初始化脚本 |
| MVP 验证点 | `uv run python scripts/init_db.py` 建库建表成功，冒烟测试全通过 |

### 1.3 本步骤产出的文件

```
langchain-chat/
├── scripts/                      工具脚本目录（新建）
│   ├── __init__.py               包标识（新建）
│   └── init_db.py                数据库初始化与冒烟测试脚本（新建）
└── src/storage/
    ├── __init__.py               包标识（Step 2 已建）
    ├── base.py                   抽象基类（Step 2 已建）
    ├── factory.py                工厂模式（新建）
    └── sqlite_backend.py         SQLite 实现（新建）
```

共新建 4 个文件（其中 2 个是实质性代码，1 个是包标识，1 个是脚本）。

> 说明：
>
> 项目根目录下的各个目录，各有明确职责：
>
> | 目录     | 职责                                            | 内容性质                     |
> | -------- | ----------------------------------------------- | ---------------------------- |
> | src/     | 程序源码（被运行时加载的代码）                  | 被主程序 import 和执行的模块 |
> | scripts/ | 辅助脚本（开发/运维工具，不是程序本身的一部分） | 开发时手动运行的独立脚本     |
> | tests/   | 测试代码                                        | 测试用例                     |
> | docs/    | 文档                                            | 说明文档                     |
> | config/  | 配置                                            | 配置文件                     |
>
> 关键区分：**src 里是「程序自己」，scripts 里是「给人用的工具」。**
>
> 区别：
>
> **src 里的代码**：程序运行时会被自动加载执行。比如 `main.py` 启动后，会 import `core/config_manager.py`、`ui/tui/app.py` 等。这些代码是程序的一部分，用户使用程序时它们会被自动调用。
>
> **scripts 里的脚本**：程序运行时**不会**自动执行它们。它们是开发者或运维人员在特定场景下**手动**运行的独立工具。比如：
>
> - `init_db.py`：只在初始化数据库时手动跑一次（`uv run python scripts/init_db.py`）。
> - 将来可能有的 `migrate.py`（数据库迁移）、`backup.py`（数据备份）、`reset.py`（重置数据）等。
>
> 这些脚本的特点：**独立运行、一次性使用、不属于程序的核心运行链路**。
>
> **企业生产环境的最佳实践：**
>
> 这是 Python 项目的通用惯例，在大多数开源项目里看到相同结构：
>
> ```text
> 项目根/
> ├── src/           程序源码
> ├── scripts/       辅助脚本（init、migrate、deploy 等）
> ├── tests/         测试
> ├── docs/          文档
> └── ...
> ```

### 1.4 本步骤的设计决策（已确认）

| 决策 | 选择 | 理由 |
|------|------|------|
| 是否接入 TUI | 不接入 | 职责清晰，每步聚焦一件事 |
| init_db.py 用同步还是异步 | 异步（aiosqlite），同时在文档讲解同步方案 | 与项目全链路异步一致，并提供同步对照学习 |
| 验证深度 | 建表 + 冒烟测试 | 充分验证存储层可用 |

---

## 二、前置回顾与准备

### 2.1 Step 2 回顾

| 已完成 | 结论 |
|--------|------|
| 分层骨架 | models / storage / core / interface / ui 全部建立 |
| 存储接口 | base.py 定义了 StorageBackend 抽象基类，含 20 个抽象方法 |
| 配置管理 | config_manager 能读取 storage.type（当前为 sqlite） |
| TUI 菜单 | 可显示可交互，但选项是桩函数 |
| 当前短板 | 存储后端只有接口没有实现，数据无法真正持久化 |

### 2.2 本步骤需要的新依赖

Step 3 引入 1 个新依赖：

| 库 | 版本 | 用途 |
|----|------|------|
| aiosqlite | 0.22.1 | SQLite 的异步 Python 驱动 |

关于「为什么不用 Python 内置的 sqlite3」，详见第三章 3.2 节的讲解。

### 2.3 准备工作：安装 aiosqlite

按工作方式，安装需要自行完成。

#### 2.3.1 安装方法

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv add aiosqlite
```

uv add 的作用（与 Step 2 一致）：把 aiosqlite 加入 pyproject.toml 的 dependencies，写入 uv.lock，安装到 .venv。

如果你的项目配了清华镜像（uv.toml），下载会很快。

#### 2.3.2 安装后验证

```bash
uv run python -c "import aiosqlite; print('aiosqlite 版本:', aiosqlite.__version__ if hasattr(aiosqlite,'__version__') else '已安装')"
```

预期输出：

`aiosqlite 版本:已安装`

（或显示具体版本号）：

aiosqlite 版本: 0.22.1

如果报 `ModuleNotFoundError`，说明未安装成功，重新执行 uv add。

#### 2.3.3 如何删除（万一装错）

```bash
uv remove aiosqlite
```

---

## 三、核心概念讲解（3W1H）

本步骤涉及五个核心概念，逐个讲解。

### 3.1 数据库与 SQLite

**What（是什么）**

数据库（Database）是「有组织地存储数据的仓库」。

SQLite 是一种轻量级的数据库，它的特点是：整个数据库就是一个文件（比如 `app.db`），不需要单独安装数据库服务器，程序直接读写这个文件即可。

对比其他数据库：

| 数据库 | 类型 | 是否需要服务器 | 适用场景 |
|--------|------|--------------|---------|
| SQLite | 嵌入式 | 否（就是一个文件） | 小型应用、教学、开发测试 |
| MySQL | 客户端/服务器 | 是（要装 MySQL 服务） | 中大型 Web 应用 |
| PostgreSQL | 客户端/服务器 | 是 | 复杂查询、企业级 |
| Redis | 内存数据库 | 是 | 缓存 |

本项目默认用 SQLite（需求文档 4.2 规定），因为：轻量、零配置、适合教学。后期可选切到 MySQL（Step 11）。

**Why（为什么需要数据库）**

不用数据库，数据怎么存？常见做法是写文件（如 JSON、CSV）。但文件存储有几个问题：

- 查询慢：想找「某个用户的所有会话」，要把整个文件读进来再筛选。
- 并发不安全：两个人同时写同一个文件会冲突。
- 难以表达关系：用户、会话、消息之间的从属关系，用文件很难维护。

数据库用「表（table）」来组织数据，类似 Excel 表格。每张表有列（字段）和行（记录）。

数据库提供了高效的查询语言（SQL）和关系维护能力（外键、级联），解决了上述问题。

**Which（本项目选 SQLite 的理由）**

已在需求文档确定：SQLite 为默认后端，MySQL/File 为可选项。理由是 SQLite 零配置、单文件、适合教学和小型应用。

**How（本项目怎么用）**

- 数据库文件路径：`data/sqlite/app.db`（在 config.yaml 的 storage.sqlite.path 中配置）。
- 用 aiosqlite 驱动异步读写。
- 5 张表：users、sessions、messages、presets、user_configs（对应 Step 2 的 5 个 Pydantic 模型）。

### 3.2 同步驱动 sqlite3 与异步驱动 aiosqlite

**What（是什么）**

Python 访问 SQLite 有两种驱动：

| 驱动 | 来源 | 模式 | 用法关键字 |
|------|------|------|----------|
| sqlite3 | Python 标准库（内置） | 同步 | `connect`、`execute`、`fetchone` |
| aiosqlite | 第三方库（需安装） | 异步 | `await connect`、`await execute`、`await fetchone` |

**Why（为什么本项目选 aiosqlite）**

需求文档 A3 要求「全链路异步」。如果用同步的 sqlite3，数据库读写会阻塞事件循环（Step 2 讲过的 asyncio），导致程序在读写数据库时无法响应其他任务。

aiosqlite 把数据库操作放到后台线程，配合 async/await，不阻塞事件循环。

**同步与异步的直观对比**

同样是「插入一条用户记录」，两种写法对比：

同步写法（sqlite3，本项目不采用，仅作对照学习）：

```python
import sqlite3

# 同步：每一步都阻塞，执行完才进入下一行
conn = sqlite3.connect("data/sqlite/app.db")     # 打开连接（阻塞）
cursor = conn.execute(
    "INSERT INTO users (username) VALUES (?)",
    ("alice",),                                    # 执行 SQL（阻塞）
)
conn.commit()                                      # 提交（阻塞）
user_id = cursor.lastrowid                         # 获取刚刚插入的用户记录的数据库主键 ID，放入 user_id 中
conn.close()                                       # 关闭（阻塞）
print("新用户 id:", user_id)
```

user_id = cursor.lastrowid 含义：

```text
常见于 SQLite / Python 数据库操作。
把刚刚插入数据库那条记录自动生成的主键 ID 取出来，并保存到变量 user_id 中。
因为插入用户后，后续可能还要用这个用户 ID 创建关联数据。
适合什么场景？
适合这种表结构（数据库自动生成主键 ID 的情况）：
id INTEGER PRIMARY KEY AUTOINCREMENT
或者：
id INTEGER PRIMARY KEY

cursor.lastrowid 只表示：
当前 cursor 最近一次 INSERT 操作生成的 row id，所以它通常要紧跟在 INSERT 后面使用：
cursor.execute("INSERT INTO users (name) VALUES (?)", ("张三",))
user_id = cursor.lastrowid
不要隔了很多其他 SQL 操作后再取，否则容易造成理解混乱。
```

异步写法（aiosqlite，本项目采用）：

```python
import asyncio
import aiosqlite

async def create_user():
    # 异步：每个 await 处会「让出 CPU」，等待期间事件循环可处理其他任务
    conn = await aiosqlite.connect("data/sqlite/app.db")    # 打开连接（非阻塞）
    cursor = await conn.execute(
        "INSERT INTO users (username) VALUES (?)",
        ("alice",),                                          # 执行 SQL（非阻塞）
    )
    await conn.commit()                                      # 提交（非阻塞）
    user_id = cursor.lastrowid                               # 获取刚刚插入的用户记录的数据库主键 ID，放入 user_id 中
    await conn.close()                                       # 关闭（非阻塞）
    print("新用户 id:", user_id)

asyncio.run(create_user())                                   # 启动事件循环
```

两者的逻辑完全相同，区别只在于：异步版每个数据库操作前加 `await`，函数定义前加 `async`。

**关键理解**：单看「插入一条记录」，同步和异步的速度差不多（因为操作本身很快）。异步的价值体现在「同时做多件事」时——比如同时处理多个用户的对话请求，异步可以在等用户 A 的 LLM 响应时，顺带把用户 B 的消息存入数据库。本项目选择异步，是为后续多用户并发场景做准备。

**Which（方案对比）**

| 方案 | 特点 | 是否选用 |
|------|------|---------|
| sqlite3（同步） | 内置，简单，但阻塞事件循环 | 否（仅作对照学习） |
| aiosqlite（异步） | 不阻塞，与项目异步架构一致 | 是 |
| SQLAlchemy async | 重量级 ORM，学习成本高 | 否 |

**How（本项目怎么用）**

在 `sqlite_backend.py` 中，用 `aiosqlite.connect()` 打开连接，用 `await conn.execute()` 执行 SQL，用 `await conn.commit()` 提交事务。

### 3.3 工厂模式（StorageFactory）

**What（是什么）**

工厂模式是一种设计模式：用一个「工厂」类，根据输入参数（配置）创建并返回不同的对象。调用者不关心对象具体怎么创建，只管向工厂要。

**Why（为什么需要）**

本项目支持三种存储后端（SQLite、MySQL、File）。如果没有工厂，业务代码里会写满 if-else：

```python
# 没有工厂的情况（反面教材）
if config.storage_type == "sqlite":
    backend = SQLiteBackend("data/sqlite/app.db")
elif config.storage_type == "mysql":
    backend = MySQLBackend(host=..., password=...)
elif config.storage_type == "file":
    backend = FileBackend("data/filestore")
```

问题：这段 if-else 会在多处重复（每个要用的地方都要判断一次）。工厂模式把这段逻辑集中到一处：

```python
# 有工厂的正确做法
backend = StorageFactory.create(config.storage_type)   # 工厂内部判断，返回对应后端
```

业务代码只和 StorageBackend 抽象基类打交道，不关心具体是哪种后端。切换后端只需改 config.yaml，无需改代码。

**Which（方案对比）**

| 方案 | 特点 | 是否选用 |
|------|------|---------|
| 直接 new（硬编码） | 简单，但耦合高、难扩展 | 否 |
| 工厂模式 | 解耦，易扩展，符合开闭原则 | 是 |

**How（本项目怎么用）**

在 `factory.py` 中定义 `StorageFactory` 类，提供 `create(storage_type)` 静态方法，根据 storage_type 返回对应后端实例。本步骤只实现 sqlite 分支，mysql 和 file 分支预留（抛出 NotImplementedError）。

### 3.4 SQL 基础（建表、增删改查、外键、级联）

本步骤会用到 SQL（Structured Query Language，结构化查询语言）。如果你没接触过 SQL，本节给出最小的够用的讲解（也许你们也并不需要~~）。

**What（是什么）**

SQL 是操作关系型数据库的标准语言。SQL 标准分为**四类**（四种子语言），本项目用到其中的三类（DDL、DQL、DML），涉及的具体语句如下：

| 类别 | 全称                                       | 作用                  | 本项目是否用到               |
| ---- | ------------------------------------------ | --------------------- | ---------------------------- |
| DDL  | Data Definition Language（数据定义语言）   | 建表、改表结构        | 是（CREATE TABLE）           |
| DQL  | Data Query Language（数据查询语言）        | 查询数据              | 是（SELECT）                 |
| DML  | Data Manipulation Language（数据操作语言） | 增删改数据            | 是（INSERT、UPDATE、DELETE） |
| DCL  | Data Control Language（数据控制语言）      | 权限控制（授权/收回） | 否（GRANT、REVOKE）          |

注意：很多教材把 DQL 归入 DML（因为 SELECT 也是「操作数据」），所以严格分类有时是三类（DDL/DML/DCL），有时是四类（DDL/DQL/DML/DCL）。这是教材间的分歧，不用过多纠结。

**How（本项目用到的 SQL 语句）**

1）建表（CREATE TABLE）：

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 主键，自增
    username TEXT UNIQUE NOT NULL,          -- 用户名，唯一，非空
    created_at TEXT NOT NULL                -- 创建时间，非空
);
```

关键字解释：

- `IF NOT EXISTS`：表不存在才创建，已存在则跳过（保证脚本可重复执行）。
- `PRIMARY KEY AUTOINCREMENT`：主键，每加一行自动加 1。
- `TEXT`：文本类型（SQLite 用 TEXT 存字符串和时间）。
- `INTEGER`：整数类型。
- `UNIQUE`：该列值不能重复。
- `NOT NULL`：该列不能为空。

2）插入（INSERT）：

```sql
INSERT INTO users (username, created_at) VALUES ('alice', '2026-06-25');
```

3）查询（SELECT）：

```sql
SELECT * FROM users WHERE username = 'alice';     -- 查特定用户
SELECT * FROM users ORDER BY id;                  -- 查全部，按 id 排序
```

4）更新（UPDATE）：

```sql
UPDATE users SET default_model = 'gpt-4o' WHERE id = 1;
```

5）删除（DELETE）：

```sql
DELETE FROM users WHERE id = 1;
```

6）外键与级联删除（本项目重点）：

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

- `FOREIGN KEY (user_id) REFERENCES users(id)`：声明 user_id 是外键，指向 users 表的 id。这保证「会话必须属于一个真实存在的用户」。
- `ON DELETE CASCADE`：级联删除——当 users 表里某个用户被删除时，sessions 表里属于该用户的所有会话会自动删除。同理，会话删除时，其下的消息也会自动删除。

级联删除的价值：删用户时不用手动一条条删会话和消息，数据库自动处理，既省代码又不会遗漏。

> 注意：SQLite 默认不启用外键约束，需要执行 `PRAGMA foreign_keys = ON` 才生效。本步骤的代码会启用它。

7）参数化查询（防 SQL 注入，重要安全实践）：

```python
# 正确：用 ? 占位，参数单独传（参数化查询，防注入）
await conn.execute("SELECT * FROM users WHERE username = ?", (username,))

# 错误：用字符串拼接（有 SQL 注入风险，绝不要这样写）
await conn.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

如果用户名是 `alice'; DROP TABLE users; --`，字符串拼接会把 users 表删掉（SQL 注入攻击）。参数化查询用 `?` 占位，数据库会把参数当作「纯数据」而非「SQL 代码」，从根本上杜绝注入。本项目所有 SQL 都用参数化查询。

8）模糊查询（LIKE，用于搜索）：

```sql
SELECT * FROM messages WHERE content LIKE '%关键词%';
```

`%` 是通配符，代表任意字符。`%关键词%` 表示「内容中包含『关键词』的」。本项目搜索功能（需求 E1）用这个。

### 3.5 datetime 的存储与读取

本项目用 TEXT 类型存储 datetime（ISO 格式字符串）。原因：

- SQLite 没有原生的日期时间类型。
- ISO 格式（如 `2026-07-12T14:30:00+00:00`）是国际标准，可排序、可读、可跨语言解析。
- Pydantic 的 datetime 能与 ISO 字符串互转。

代码里提供两个辅助方法：`_dt_to_str`（datetime 转 ISO 字符串存入）和 `_str_to_dt`（ISO 字符串转回 datetime 取出）。这样上层（业务层）拿到的永远是 datetime 对象，感知不到底层的字符串存储。

---

## 四、软件测试基础

本步骤会写一个「冒烟测试」。在讲代码前，先系统讲解软件测试的概念，帮助你建立完整的测试知识体系。

### 4.1 为什么要测试

软件是人写的，人总会犯错。测试的本质是「**用系统化的方法，尽早发现软件中的问题**」。

一个没经过测试的程序，就像没验收就交付的房子——举个例子，可能看着好好的，住进去才发现漏水、断电。测试的价值：

- 尽早发现问题：越早发现，修复成本越低（线上才发现的成本是开发期的几十倍）。
- 保证重构安全：有测试兜底，改代码时不怕改坏。
- 提供文档作用：测试用例本身就是「如何使用这段代码」的示范。

### 4.2 测试的类型（按范围划分）

业界把测试按「测试范围」分为几个层次，从大到小：

| 类型 | 英文 | 测试范围 | 通俗解释 | 例子（本项目） |
|------|------|---------|---------|--------------|
| **系统测试** | System Testing | 整个系统 | 把程序当成黑盒，从用户角度测全流程 | 启动 TUI，建用户，对话，导出，全程跑一遍 |
| **集成测试** | Integration Testing | 多个模块协作 | 测「模块拼起来能不能用」 | 测存储层 + 业务层 + 配置层一起工作 |
| **单元测试** | Unit Testing | 单个函数/类 | 测「最小的代码单元」对不对 | 单独测 create_user 方法是否正确存入数据 |

从大到小，越往下越细、越快、越容易定位问题。本项目在 Step 13 会专门做单元测试（用 pytest）。

### 4.3 测试的类型（按方法划分）

按「怎么测」分：

| 类型 | 英文 | 方法 | 例子 |
|------|------|------|------|
| **黑盒测试** | Black Box | 不看代码，只看输入输出 | 给程序一个输入，看输出对不对 |
| **白盒测试** | White Box | 看代码内部结构来设计测试 | 针对每个 if 分支都测一遍 |
| **灰盒测试** | Gray Box | 介于两者之间 | 看部分代码，结合输入输出 |

### 4.4 特殊用途的测试

除了上述分类，还有几种按「用途」分的测试：

| 类型 | 作用 | 本项目应用 |
|------|------|----------|
| **冒烟测试** | 冒烟测试是最初步的测试，源自硬件行业（新电路板通电，如果冒烟了说明有严重短路，根本不用细测）。软件中指「**验证核心功能能否正常运行**」的最基本测试。如果不通过，说明有严重问题，后续的细致测试也没有意义。 | 本步骤的 init_db.py 就是一次冒烟测试 |
| **回归测试** | 修改代码后，重新跑测试，确认没把原来好的功能改坏 | Step 13 的 pytest 会做回归测试 |
| **压力测试** | 测系统在高负载下的表现 | 本项目暂不涉及 |
| **验收测试** | 用户/客户确认软件满足需求 | 项目最终交付时做 |

### 4.5 本步骤的冒烟测试做什么

本步骤的冒烟测试（在 init_db.py 中）验证存储层的核心链路：

```
建表 → 创建用户 → 创建会话 → 添加消息 → 查询消息 → 搜索消息 → 删除用户（级联清理）
```

这条链路如果全部通过，说明存储层的核心功能（建表、增、查、搜索、删）都可用。如果有任何一环失败，说明有严重问题，需要先修复再继续后续步骤。

冒烟测试不追求「覆盖所有情况」（那是单元测试的职责），只追求「核心链路畅通」。

### 4.6 冒烟测试与单元测试的区别（提前理解，Step 13 会深入）

| 方面 | 冒烟测试 | 单元测试 |
|------|---------|---------|
| 目的 | 验证核心链路通不通 | 验证每个细节对不对 |
| 范围 | 大链路（建表到删除全流程） | 单个方法（只测 create_user） |
| 数量 | 少（一两个场景） | 多（每个方法多个用例） |
| 工具 | 手写脚本（本步骤的 init_db.py） | 测试框架（Step 13 用 pytest） |
| 执行时机 | 开发中随时跑 | 提交前、持续集成中自动跑 |

本步骤先用手写的冒烟测试验证存储层；Step 13 会用 pytest 写正式的单元测试，覆盖更细致的场景。

---

## 五、动手实践：创建源码文件

下面依次创建 4 个文件。每个文件给出完整内容与讲解。

> **文件位置约定**：所有源码文件在 `src/` 下，脚本在 `scripts/` 下。文件编码统一 UTF-8（不带 BOM）。
>
>   PyCharm 设置文件编码：
>
> ​	File → Settings → Editor → File Encodings
>
> ​	建议配置为：
>
> ```text
> Global Encoding: UTF-8
> Project Encoding: UTF-8
> Default encoding for properties files: UTF-8
> ```
> ​	再找到这一项：Create UTF-8 files  选择：without BOM
>
> **import 约定**：文件间 import 相对于 src 目录（如 `from storage.base import StorageBackend`），与 Step 2 一致。
>
> **PyCharm 提示**：创建文件时如果弹出「是否加入 Git 追踪」，按你在 Step 2 的设置处理（选「不添加」，最后统一 git add）。

### 5.1 创建 src/storage/factory.py（工厂模式）

文件路径：`langchain-chat/src/storage/factory.py`。

这个文件实现存储工厂。业务代码通过工厂获取后端实例，不直接 new 具体后端。

**设计说明**：

- 用静态方法 `create(storage_type)` 返回对应后端。
- sqlite 分支用「延迟导入」（只在用到时才 import sqlite_backend），避免无用依赖。
- mysql/file 分支预留，抛出 NotImplementedError（告诉调用者「这个后端还没实现」）。

**文件内容**：

```python
"""存储后端工厂。

根据 config.yaml 中的 storage.type 配置，创建对应的存储后端实例。
对应需求文档第四章「存储架构」的工厂模式设计。

设计说明：
    - 业务代码不直接 new 某个后端，而是通过工厂获取。
    - 这样切换后端（sqlite/mysql/file）只需改配置，无需改业务代码。
    - 新增后端时，只需在工厂里加一个分支。
"""

from storage.base import StorageBackend


class StorageFactory:
    """存储后端工厂。

    使用方式：
        backend = StorageFactory.create("sqlite")
        await backend.initialize()
    """

    @staticmethod
    def create(storage_type: str) -> StorageBackend:
        """根据存储类型创建对应的后端实例。

        参数：
            storage_type: 存储类型字符串（sqlite / mysql / file）
        返回：
            对应的 StorageBackend 实例（未初始化，需再调用 initialize）
        """
        if storage_type == "sqlite":
            # 延迟导入：只用 sqlite 时才加载 sqlite_backend，避免无用依赖
            from storage.sqlite_backend import SQLiteBackend
            return SQLiteBackend()
        elif storage_type == "mysql":
            # MySQL 后端在 Step 11 实现
            raise NotImplementedError("MySQL 后端将在 Step 11 实现")
        elif storage_type == "file":
            # File 后端在 Step 12 实现
            raise NotImplementedError("File 后端将在 Step 12 实现")
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}（可选: sqlite/mysql/file）")
```

**讲解：延迟导入（lazy import）**

注意 sqlite 分支里 `from storage.sqlite_backend import SQLiteBackend` 写在函数内部，而不是文件顶部。这叫「延迟导入」：只有真正用到 sqlite 时才加载 sqlite_backend 模块。好处是：如果将来用户只用 mysql，就不会被迫加载 sqlite 相关代码（虽然本项目都装了，但这是好习惯，减少不必要的模块加载）。

**注意：** 此时，代码中的 from storage.sqlite_backend import SQLiteBackend 会提示错误，因为 SQLiteBackend 还没有创建，这是正常的，创建 5.2 节的 sqlite_backend.py 后错误会消失。

#### 验证检查点 A：工厂能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from storage.factory import StorageFactory; print('StorageFactory OK:', StorageFactory.__name__)"
```

预期输出：`StorageFactory OK: StorageFactory`

---

### 5.2 创建 src/storage/sqlite_backend.py（核心实现）

文件路径：`langchain-chat/src/storage/sqlite_backend.py`。

这是本步骤最核心、最长的文件。它实现 StorageBackend 定义的全部 20 个抽象方法，让数据真正能存进 SQLite。

**设计说明**：

- 用 aiosqlite 异步访问数据库。
- datetime 字段以 ISO 字符串存储（TEXT 类型），用 `_dt_to_str` / `_str_to_dt` 互转。
- 启用外键约束（`PRAGMA foreign_keys = ON`），让级联删除生效。
- 每个实体的方法成组：create、get/list、update、delete，外加一个 `_row_to_xxx` 转换方法（把数据库行转回 Pydantic 模型）。
- 所有 SQL 用参数化查询（`?` 占位），防 SQL 注入。

**文件内容较长，分段讲解后给出完整代码。**

#### 5.2.1 类结构与初始化

```python
class SQLiteBackend(StorageBackend):
    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = db_path
        self._conn = None     # 连接对象，initialize 后才有值

    async def initialize(self) -> None:
        # 建目录、打开连接、启用外键、建表
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row    # 按列名访问
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self._create_tables()
        await self._conn.commit()
```

要点：

- `Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)`：确保 `data/sqlite/` 目录存在，否则建库失败。
- `row_factory = aiosqlite.Row`：让查询结果可以用 `row["username"]` 按列名访问（而非 `row[0]` 按下标），代码更清晰。
- `PRAGMA foreign_keys = ON`：SQLite 默认不启用外键，必须显式开启，级联删除才生效。

#### 5.2.2 建表（_create_tables）

用 `executescript` 一次性执行多张表的建表 SQL。每张表用 `IF NOT EXISTS`，保证脚本可重复执行不报错。表结构严格对应需求文档第四章的数据实体设计，字段、类型、约束、外键、级联都按设计实现。

#### 5.2.3 增删改查方法（以用户为例）

每个实体的方法模式类似，以用户为例：

- `create_user`：INSERT 插入，返回含分配 id 的 User。
- `get_user_by_name`：SELECT 查询单条，row 转 User。
- `list_users`：SELECT 查询多条，逐个 row 转 User。
- `delete_user`：DELETE 删除（关联数据靠 CASCADE 自动清理）。
- `_row_to_user`：把 aiosqlite.Row 转成 User 模型（静态方法）。

其他实体（会话、消息、预设、配置）的方法模式相同，只是字段不同。

#### 5.2.4 搜索方法（search_messages）

搜索用联表查询（JOIN）：messages 表关联 sessions 表，找到属于指定用户的消息，再用 LIKE 模糊匹配关键词。

#### 5.2.5 完整文件内容

```python
"""SQLite 存储后端实现。

实现 StorageBackend 定义的全部接口方法，用 aiosqlite 异步驱动操作 SQLite。
对应需求文档第四章「存储架构」（SQLite 为默认后端）。

设计说明：
    - 用 aiosqlite 异步访问数据库（项目全链路异步，需求 A3）。
    - datetime 字段统一以 ISO 格式字符串存储（TEXT 类型），读取时转回 datetime。
    - id 字段用 INTEGER PRIMARY KEY AUTOINCREMENT 自增。
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiosqlite

from models.schemas import Message, Preset, Session, User, UserConfig
from storage.base import StorageBackend


class SQLiteBackend(StorageBackend):
    """SQLite 存储后端。

    使用前必须先调用 initialize() 建表，使用结束调用 close() 关闭连接。
    """

    def __init__(self, db_path: str = "data/sqlite/app.db"):
        # 数据库文件路径（相对于运行目录）
        self.db_path = db_path
        # 连接对象（initialize 后才有值）
        self._conn: Optional[aiosqlite.Connection] = None

    # ── 初始化与清理 ──────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """初始化：建目录、打开连接、建表。"""
        # 确保数据库所在目录存在（否则 aiosqlite.connect 会失败）
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # 打开连接（启用外键约束，让 ON DELETE CASCADE 生效）
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row  # 查询结果按列名访问
        await self._conn.execute("PRAGMA foreign_keys = ON")

        # 建表
        await self._create_tables()
        await self._conn.commit()

    async def close(self) -> None:
        """关闭连接。"""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def _create_tables(self) -> None:
        """创建所有表（IF NOT EXISTS 保证可重复执行）。"""
        await self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                default_model TEXT,
                default_preset_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (default_preset_id) REFERENCES presets(id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                model_name TEXT NOT NULL,
                preset_id INTEGER,
                total_prompt_tokens INTEGER NOT NULL DEFAULT 0,
                total_completion_tokens INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (preset_id) REFERENCES presets(id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('human','ai','system')),
                content TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                completion_tokens INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                system_prompt TEXT NOT NULL,
                is_builtin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS user_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

    # ── 辅助方法 ──────────────────────────────────────────────────────────

    @staticmethod
    def _dt_to_str(dt: datetime) -> str:
        """datetime 转 ISO 字符串存储。"""
        return dt.isoformat()

    @staticmethod
    def _str_to_dt(s: str) -> datetime:
        """ISO 字符串转回 datetime。"""
        return datetime.fromisoformat(s)

    # ── 用户相关 ──────────────────────────────────────────────────────────

    async def create_user(self, user: User) -> User:
        """创建用户。返回含分配 id 的 User。"""
        cursor = await self._conn.execute(
            """INSERT INTO users (username, default_model, default_preset_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user.username, user.default_model, user.default_preset_id,
             self._dt_to_str(user.created_at), self._dt_to_str(user.updated_at)),
        )
        await self._conn.commit()
        user.id = cursor.lastrowid
        return user

    async def get_user_by_name(self, username: str) -> Optional[User]:
        """按用户名查询。不存在返回 None。"""
        async with self._conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ) as cursor:
            row = await cursor.fetchone()
            return self._row_to_user(row) if row else None

    async def list_users(self) -> list[User]:
        """列出所有用户。"""
        async with self._conn.execute("SELECT * FROM users ORDER BY id") as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_user(r) for r in rows]

    async def delete_user(self, user_id: int) -> None:
        """删除用户（关联数据靠 ON DELETE CASCADE 自动清理）。"""
        await self._conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await self._conn.commit()

    @staticmethod
    def _row_to_user(row: aiosqlite.Row) -> User:
        return User(
            id=row["id"], username=row["username"],
            default_model=row["default_model"], default_preset_id=row["default_preset_id"],
            created_at=SQLiteBackend._str_to_dt(row["created_at"]),
            updated_at=SQLiteBackend._str_to_dt(row["updated_at"]),
        )

    # ── 会话相关 ──────────────────────────────────────────────────────────

    async def create_session(self, session: Session) -> Session:
        cursor = await self._conn.execute(
            """INSERT INTO sessions (user_id, title, model_name, preset_id,
               total_prompt_tokens, total_completion_tokens, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session.user_id, session.title, session.model_name, session.preset_id,
             session.total_prompt_tokens, session.total_completion_tokens,
             self._dt_to_str(session.created_at), self._dt_to_str(session.updated_at)),
        )
        await self._conn.commit()
        session.id = cursor.lastrowid
        return session

    async def get_session(self, session_id: int) -> Optional[Session]:
        async with self._conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return self._row_to_session(row) if row else None

    async def list_sessions(self, user_id: int) -> list[Session]:
        async with self._conn.execute(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_session(r) for r in rows]

    async def update_session(self, session: Session) -> None:
        # 更新 updated_at 为当前时间
        session.updated_at = datetime.now(timezone.utc)
        await self._conn.execute(
            """UPDATE sessions SET title=?, model_name=?, preset_id=?,
               total_prompt_tokens=?, total_completion_tokens=?, updated_at=? WHERE id=?""",
            (session.title, session.model_name, session.preset_id,
             session.total_prompt_tokens, session.total_completion_tokens,
             self._dt_to_str(session.updated_at), session.id),
        )
        await self._conn.commit()

    async def delete_session(self, session_id: int) -> None:
        await self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        await self._conn.commit()

    @staticmethod
    def _row_to_session(row: aiosqlite.Row) -> Session:
        return Session(
            id=row["id"], user_id=row["user_id"], title=row["title"],
            model_name=row["model_name"], preset_id=row["preset_id"],
            total_prompt_tokens=row["total_prompt_tokens"],
            total_completion_tokens=row["total_completion_tokens"],
            created_at=SQLiteBackend._str_to_dt(row["created_at"]),
            updated_at=SQLiteBackend._str_to_dt(row["updated_at"]),
        )

    # ── 消息相关 ──────────────────────────────────────────────────────────

    async def add_message(self, message: Message) -> Message:
        cursor = await self._conn.execute(
            """INSERT INTO messages (session_id, role, content, prompt_tokens,
               completion_tokens, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (message.session_id, message.role, message.content,
             message.prompt_tokens, message.completion_tokens,
             self._dt_to_str(message.created_at)),
        )
        await self._conn.commit()
        message.id = cursor.lastrowid
        return message

    async def list_messages(self, session_id: int) -> list[Message]:
        async with self._conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY id", (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_message(r) for r in rows]

    async def search_messages(self, user_id: int, keyword: str) -> list[Message]:
        # 联表查询：通过 messages 关联 sessions，找到属于该用户的消息
        async with self._conn.execute(
            """SELECT m.* FROM messages m
               JOIN sessions s ON m.session_id = s.id
               WHERE s.user_id = ? AND m.content LIKE ?
               ORDER BY m.id""",
            (user_id, f"%{keyword}%"),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_message(r) for r in rows]

    @staticmethod
    def _row_to_message(row: aiosqlite.Row) -> Message:
        return Message(
            id=row["id"], session_id=row["session_id"], role=row["role"],
            content=row["content"], prompt_tokens=row["prompt_tokens"],
            completion_tokens=row["completion_tokens"],
            created_at=SQLiteBackend._str_to_dt(row["created_at"]),
        )

    # ── 预设相关 ──────────────────────────────────────────────────────────

    async def save_preset(self, preset: Preset) -> Preset:
        if preset.id is None:
            # 新增
            cursor = await self._conn.execute(
                """INSERT INTO presets (user_id, name, description, system_prompt,
                   is_builtin, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (preset.user_id, preset.name, preset.description, preset.system_prompt,
                 1 if preset.is_builtin else 0,
                 self._dt_to_str(preset.created_at), self._dt_to_str(preset.updated_at)),
            )
            await self._conn.commit()
            preset.id = cursor.lastrowid
        else:
            # 更新
            await self._conn.execute(
                """UPDATE presets SET name=?, description=?, system_prompt=?,
                   is_builtin=?, updated_at=? WHERE id=?""",
                (preset.name, preset.description, preset.system_prompt,
                 1 if preset.is_builtin else 0,
                 self._dt_to_str(preset.updated_at), preset.id),
            )
            await self._conn.commit()
        return preset

    async def list_presets(self, user_id: int) -> list[Preset]:
        # 系统内置（user_id IS NULL）+ 该用户的自定义（user_id = ?）
        async with self._conn.execute(
            """SELECT * FROM presets WHERE user_id IS NULL OR user_id = ? ORDER BY id""",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_preset(r) for r in rows]

    async def delete_preset(self, preset_id: int) -> None:
        await self._conn.execute("DELETE FROM presets WHERE id = ?", (preset_id,))
        await self._conn.commit()

    @staticmethod
    def _row_to_preset(row: aiosqlite.Row) -> Preset:
        return Preset(
            id=row["id"], user_id=row["user_id"], name=row["name"],
            description=row["description"], system_prompt=row["system_prompt"],
            is_builtin=bool(row["is_builtin"]),
            created_at=SQLiteBackend._str_to_dt(row["created_at"]),
            updated_at=SQLiteBackend._str_to_dt(row["updated_at"]),
        )

    # ── 用户配置相关 ──────────────────────────────────────────────────────

    async def get_user_config(self, user_id: int, key: str) -> Optional[str]:
        async with self._conn.execute(
            "SELECT value FROM user_configs WHERE user_id = ? AND key = ?",
            (user_id, key),
        ) as cursor:
            row = await cursor.fetchone()
            return row["value"] if row else None

    async def set_user_config(self, config: UserConfig) -> None:
        # 先查是否已存在（user_id + key 视为唯一）
        async with self._conn.execute(
            "SELECT id FROM user_configs WHERE user_id = ? AND key = ?",
            (config.user_id, config.key),
        ) as cursor:
            existing = await cursor.fetchone()

        now_str = self._dt_to_str(config.updated_at)
        if existing:
            await self._conn.execute(
                "UPDATE user_configs SET value=?, updated_at=? WHERE id=?",
                (config.value, now_str, existing["id"]),
            )
        else:
            await self._conn.execute(
                """INSERT INTO user_configs (user_id, key, value, updated_at)
                   VALUES (?, ?, ?, ?)""",
                (config.user_id, config.key, config.value, now_str),
            )
        await self._conn.commit()
```

#### 验证检查点 B：SQLite 后端能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from storage.sqlite_backend import SQLiteBackend; b = SQLiteBackend(); print('SQLiteBackend OK:', type(b).__name__)"
```

预期输出：`SQLiteBackend OK: SQLiteBackend`

如果报 `ModuleNotFoundError: No module named 'aiosqlite'`，说明 aiosqlite 未安装，执行 `uv add aiosqlite`。

---

### 5.3 创建 `scripts/__init__.py`（包标识）

文件路径：`langchain-chat/scripts/__init__.py`（需先建立 scripts 目录）。

**文件内容**：

```python
"""工具脚本包。

包含项目的各类辅助脚本：
    - init_db.py   数据库初始化与冒烟测试
"""
```

---

### 5.4 创建 scripts/init_db.py（初始化与冒烟测试）

文件路径：`langchain-chat/scripts/init_db.py`。

这个脚本完成两件事：建库建表（通过 SQLiteBackend.initialize）+ 冒烟测试（验证 CRUD 全链路）。

**设计说明**：

- 用 asyncio.run 启动异步主函数（与 main.py 一致）。
- sys.path 注入：把 src 目录加入搜索路径，这样脚本能 import 项目模块（init_db.py 在 scripts/ 下，不在 src/ 下，需要手动注入）。
- 冒烟测试链路：建用户 → 建会话 → 加消息 → 查消息 → 搜索 → 列会话 → 删用户（验证级联清理）。
- 测试结束删除测试用户（清理痕迹，CASCADE 自动清关联数据）。

**文件内容**：

```python
"""数据库初始化脚本。

功能：
    1. 创建数据库和所有表（通过 SQLiteBackend.initialize）。
    2. 运行一轮冒烟测试，验证 CRUD 全部可用。

运行方式：
    uv run python scripts/init_db.py

对应需求文档：存储层初始化（scripts/init_db.py 数据库初始化）。
"""

import asyncio
import sys
from pathlib import Path

# 将 src 目录加入模块搜索路径（与 main.py 同样的 sys.path 注入手法）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from models.schemas import Message, Preset, Session, User, UserConfig
from storage.factory import StorageFactory


async def init_and_smoke_test() -> None:
    """初始化数据库并运行冒烟测试。"""
    print("=" * 60)
    print("Step 3：SQLite 存储后端初始化与冒烟测试")
    print("=" * 60)

    # 1. 通过工厂创建后端实例
    backend = StorageFactory.create("sqlite")
    print(f"[1/6] 创建存储后端: {type(backend).__name__}")

    try:
        # 2. 初始化（建目录、建表）
        await backend.initialize()
        print("[2/6] 数据库已初始化（data/sqlite/app.db，5 张表已创建）")

        # 2.5 初始化后清理可能残留的测试数据（保证幂等性）
        #     无论上次运行是否正常结束、是否中途崩溃，都先清理同名测试用户。
        #     delete_user 会触发 ON DELETE CASCADE，自动清理其关联的会话和消息。
        existing = await backend.get_user_by_name("smoke_test_user")
        if existing:
            await backend.delete_user(existing.id)
            print(f"      [清理] 发现残留测试用户 id={existing.id}，已删除")

        # 3. 冒烟测试：创建用户
        user = await backend.create_user(User(id=0, username="smoke_test_user"))
        print(f"[3/6] 创建用户: id={user.id}, username={user.username}")

        # 4. 冒烟测试：创建会话
        session = await backend.create_session(Session(
            id=0, user_id=user.id, title="冒烟测试会话", model_name="deepseek-chat",
        ))
        print(f"[4/6] 创建会话: id={session.id}, title={session.title}")

        # 5. 冒烟测试：添加消息（一轮对话产生 human + ai 两条）
        human_msg = await backend.add_message(Message(
            id=0, session_id=session.id, role="human", content="你好，这是冒烟测试",
        ))
        ai_msg = await backend.add_message(Message(
            id=0, session_id=session.id, role="ai", content="你好，冒烟测试通过",
        ))
        print(f"[5/6] 添加消息: human id={human_msg.id}, ai id={ai_msg.id}")

        # 6. 冒烟测试：查询验证
        # 查消息
        msgs = await backend.list_messages(session.id)
        print(f"[6/6] 查询消息: 会话 {session.id} 共 {len(msgs)} 条")
        for m in msgs:
            print(f"      - [{m.role}] {m.content}")

        # 搜索验证
        results = await backend.search_messages(user.id, "冒烟")
        print(f"      搜索'冒烟': 命中 {len(results)} 条")

        # 列会话验证
        sessions = await backend.list_sessions(user.id)
        print(f"      用户 {user.id} 的会话数: {len(sessions)}")

        # 清理：删除测试用户（关联数据靠 CASCADE 自动清理）
        await backend.delete_user(user.id)
        print(f"\n[清理] 已删除测试用户 {user.id}（关联数据自动清理）")
        print("[完成] 数据库初始化与冒烟测试全部通过")

    finally:
        # 关闭连接
        await backend.close()
        print("[关闭] SQLite 连接已关闭")


def main() -> None:
    """脚本主入口。"""
    asyncio.run(init_and_smoke_test())


if __name__ == "__main__":
    main()
```

**讲解：sys.path 注入的细节**

init_db.py 在 scripts/ 目录下，它要 import 的模块（models、storage）在 src/ 目录下。两个目录是平级的，Python 默认找不到 src 里的模块。所以需要这行：

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
```

拆解：`Path(__file__)` 是 init_db.py 自己的路径，`.resolve()` 转绝对路径，`.parent` 是 scripts/ 目录，再 `.parent` 是项目根目录，再 `/ "src"` 是 src 目录。把这路径加入 sys.path，Python 就能找到 src 里的模块了。

#### 拓展讲解

##### 问题 1：初始化与冒烟测试为何放在一个文件

说明：这是一个教学项目的简化做法

**把初始化和冒烟测试放在一个文件里，是教学项目的简化做法，不是企业级的标准做法。**

设计的出发点（三点）

| 出发点         | 说明                                                         |
| -------------- | ------------------------------------------------------------ |
| 教学聚焦       | 教学项目追求「一个文件能说明白一件事」。如果拆成两个文件，要来回切换，注意力分散。运行一个 init_db.py 就能看到「建表 + 增删改查」的完整效果，因果链完整。 |
| 需求文档的表述 | 需求文档实施计划 Step 3 的涉及文件只列了 scripts/init_db.py 一个文件，描述是「数据库初始化（建表）」。顺带把验证也放进去，是为了落实 MVP 验证点（文档要求「代码中可调用存储后端进行增删改查」）。 |
| 即时验证       | 初始化和验证有先后依赖关系（先建表才能测试）。放一起，运行一次脚本就完成「建库 + 验证」，不漏环节。 |

但这三个出发点都是**教学便利性**，不是企业实践。

**企业中的标准做法（需要分清楚）**

企业级项目会把这些职责严格分开，至少拆成独立的文件甚至独立目录：

| 职责                 | 企业中的典型位置                       | 说明                                |
| -------------------- | -------------------------------------- | ----------------------------------- |
| 数据库初始化（建表） | scripts/init_db.py 或 migrations/ 目录 | 只负责建表/改表结构，不包含测试逻辑 |
| 冒烟测试             | tests/smoke/ 或 scripts/smoke_test.py  | 独立的测试脚本，与初始化解耦        |
| 单元测试             | tests/unit/                            | pytest 管理的正式测试               |
| 集成测试             | tests/integration/                     | 多模块协作测试                      |

为什么需要分开？
| 理由            | 说明                                                         |
| --------------- | ------------------------------------------------------------ |
| 职责单一（SRP） | 一个文件只做一件事。init_db.py 只管建表，测试文件只管测试。改一处不影响另一处。 |
| 执行时机不同    | 初始化只在部署时跑一次；测试要反复跑（每次改代码后）。混在一起，每次跑测试都会重新建表，浪费时间。 |
| 持续集成（CI）  | 企业用 CI 系统（如 Jenkins、GitHub Actions）自动跑测试。测试脚本必须是独立的、可重复执行的，不能掺杂初始化副作用。 |
| 团队协作        | 初始化脚本由运维或 DBA 维护，测试脚本由开发维护。分开后各自修改不冲突。 |

企业做法的示意图

项目结构（企业级）：
项目根/
├── scripts/
│   └── init_db.py              # 只建表，干净
├── migrations/                  # 数据库迁移（更专业的做法）
│   ├── 001_create_tables.sql
│   └── 002_add_index.sql
└── tests/
    ├── smoke/                   # 冒烟测试，独立目录
    │   └── test_storage.py
    ├── unit/                    # 单元测试
    │   └── test_user_manager.py
    └── integration/             # 集成测试

**后续的建议**

**Step 3 当前可以保持合并（教学便利）**，但需要知道：这是教学简化，并不是企业级的工程规范的最佳实践。

到 **Step 13（单元测试）** 时，会建立正式的 `tests/` 目录，用 pytest 写独立的测试。那时 init_db.py 里的冒烟测试就可以「退役」，由正式的 pytest 测试接管。

会在 Step 13 时做这个演进，并呼应（回顾） Step 3 的这段说明。

##### 问题 2：这个冒烟测试是否遵循幂等性

结论：部分遵循，不完全遵循。

什么是幂等性（概念）

**幂等性（Idempotency）**：一个操作执行一次和执行多次，产生的效果（结果）相同。

通俗说：**「做一遍和做 N 遍，结果一样」**。

举例：

| 操作                           | 是否幂等 | 说明                                          |
| ------------------------------ | -------- | --------------------------------------------- |
| x = 5                          | 幂等     | 执行 1 次和 100 次，x 都是 5                  |
| x = x + 1                      | 不幂等   | 每执行一次 x 就加 1，结果不同                 |
| DELETE FROM users WHERE id = 1 | 幂等     | 删一次和删十次，结果都是「id=1 的用户不存在」 |
| INSERT INTO users VALUES (...) | 不幂等   | 每执行一次就多一条记录                        |

幂等性的价值：**操作可以安全地重复执行**，不用担心副作用。这对运维特别重要——脚本失败了重跑，不会把数据搞乱。

**分析 init_db.py 的幂等性**

init_db.py 的冒烟测试链路有 7 个环节，逐一判断：

| 环节          | 代码                            | 是否幂等 | 分析                                       |
| ------------- | ------------------------------- | -------- | ------------------------------------------ |
| 1. 创建后端   | StorageFactory.create("sqlite") | 幂等     | 只是创建对象，无副作用                     |
| 2. 初始化建表 | await backend.initialize()      | 幂等     | CREATE TABLE IF NOT EXISTS，表已存在则跳过 |
| 3. 创建用户   | create_user(...)                | 不幂等   | 每次运行新增一条用户记录                   |
| 4. 创建会话   | create_session(...)             | 不幂等   | 每次新增                                   |
| 5. 添加消息   | add_message(...)                | 不幂等   | 每次新增                                   |
| 6. 查询/搜索  | list_messages / search_messages | 幂等     | 只读，不改数据                             |
| 7. 删除用户   | delete_user(...)                | 幂等     | 删一次和多次，结果都是该用户不存在         |

**核心问题在第 3、4、5 步**：它们是 INSERT 操作，每次运行都会新增数据。虽然第 7 步把测试用户删了（清理），但有两点不完美：

1. **自增 id 会递增**：每次运行，新用户的 id 比上次大（即使上次的被删了）。AUTOINCREMENT 计数器只增不减。所以「第一次运行 user.id=1，第二次运行 user.id=2」，结果不完全相同。
2. **中途失败会留垃圾**：如果脚本在第 5 步崩溃（比如代码有 bug），测试数据会残留在数据库里，不会清理。下次再跑，残留数据可能干扰结果。

**结论：**不是严格幂等

严格说，这个冒烟测试**不是幂等的**，因为：

- 多次运行会产生不同的 id（自增）。
- 中途失败会残留数据。

但它在「正常跑完」的情况下，**数据会被清理**（第 7 步删除测试用户），所以数据库不会无限膨胀。这算是一种「软清理」。

**如何真正幂等（改进思路和建议）**

如果要做成严格幂等，有几种做法：

**做法 A：**每次运行前清空测试数据（推荐）

在创建测试用户前，先删除可能存在的同名用户：

```python
# 在 create_user 之前，先清理可能残留的测试数据
existing = await backend.get_user_by_name("smoke_test_user")
if existing:
    await backend.delete_user(existing.id)   # CASCADE 会清掉关联的会话和消息
```

这样无论之前跑到哪一步、是否崩溃，下次运行都会先清理，保证起点干净。

**做法 B：**使用独立的测试数据库

用一个单独的数据库文件（如 `data/sqlite/test.db`），每次运行前删除整个文件重建：

```python
# 测试用独立的数据库，跑完即删
import os
test_db = "data/sqlite/test.db"
if os.path.exists(test_db):
    os.remove(test_db)
backend = SQLiteBackend(test_db)
```

这样完全隔离测试数据，不影响正式数据库。

**做法 C：**用事务回滚

把整个测试包在一个数据库事务里，测完不提交，直接回滚（数据不真正写入）：

```python
await self._conn.execute("BEGIN")
# ... 所有测试操作 ...
await self._conn.execute("ROLLBACK")   # 回滚，数据全部消失
```

这是单元测试里常用的手法（Step 13 会用到）。

**对本项目的处理**

本项目的 init_db.py 已经采用了做法 A（清理逻辑），在创建测试用户前先检查并清理同名残留用户（见 init_db.py 的 2.5 步）。这样即使上次运行中途崩溃导致数据残留，下次运行也能保证起点干净。

注意：即使加了清理逻辑，由于 SQLite 的 AUTOINCREMENT 计数器（sqlite_sequence 表）只增不减，重复运行的 id 仍会递增。这是 SQLite 的固有特性，不影响数据的正确性，只是 id 数值不同而已。

##### 问题总结

| 问题                       | 结论                                                         |
| -------------------------- | ------------------------------------------------------------ |
| 初始化与冒烟测试放一个文件 | 教学简化做法，企业会分开。可在文档加说明，Step 13 演进到独立 tests 目录。 |
| 是否幂等                   | 不是严格幂等（INSERT 导致 id 递增、中途失败残留数据）。需要加清理逻辑改进。 |

---

## 六、整体运行验证

### 6.1 执行验证命令

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python scripts/init_db.py
```

### 6.2 预期输出

首次运行的输出：

```
============================================================
Step 3：SQLite 存储后端初始化与冒烟测试
============================================================
[1/6] 创建存储后端: SQLiteBackend
[2/6] 数据库已初始化（data/sqlite/app.db，5 张表已创建）
[3/6] 创建用户: id=1, username=smoke_test_user
[4/6] 创建会话: id=1, title=冒烟测试会话
[5/6] 添加消息: human id=1, ai id=2
[6/6] 查询消息: 会话 1 共 2 条
      - [human] 你好，这是冒烟测试
      - [ai] 你好，冒烟测试通过
      搜索'冒烟': 命中 2 条
      用户 1 的会话数: 1

[清理] 已删除测试用户 1（关联数据自动清理）
[完成] 数据库初始化与冒烟测试全部通过
```

（id 编号可能因重复运行而递增，属正常现象。因为每次运行都会创建新用户，删除后自增计数器不回退。）

**重复运行的输出：会多一行清理提示。**

如果第二次运行 init_db.py，且上次运行正常（测试用户已被第 7 步删除），则 `get_user_by_name` 返回 None，清理也不触发，输出仍和首次相同。

清理提示只在「上次运行中途崩溃、测试用户残留」的情况下出现。例如上次在第 5 步崩溃了，测试用户没被清理，这次运行会输出：

```text
[2/6] 数据库已初始化（data/sqlite/app.db，5 张表已创建）
      [清理] 发现残留测试用户 id=3，已删除
[3/6] 创建用户: id=4, username=smoke_test_user
...
```

注意：id 会递增（SQLite AUTOINCREMENT 的特性），这是正常的，不影响幂等性的核心目的（数据状态一致）。

即：首次运行时数据库为空，清理逻辑不触发，输出如上。若上次运行中途崩溃导致测试数据残留，再次运行时会在步骤 2 后多一行「[清理] 发现残留测试用户...」的提示，属正常现象。

### 6.3 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 无报错跑完 | 全部 6 步完成 | 存储后端实现正确 |
| 创建用户成功 | 显示用户 id | INSERT 正常 |
| 创建会话成功 | 显示会话 id 和标题 | 外键关联正常 |
| 添加消息成功 | human 和 ai 各一条 | 消息存储正常 |
| 查询消息成功 | 显示 2 条消息 | SELECT 正常 |
| 搜索成功 | 命中 2 条 | LIKE 模糊查询正常 |
| 删除用户成功 | 关联数据自动清理 | CASCADE 级联删除生效 |

### 6.4 验证数据库文件生成

```bash
dir data\sqlite
```

应看到 `app.db` 文件。这就是 SQLite 数据库文件，所有数据都存在这一个文件里。

> 说明：
>
> 1. 可以在 PyCharm 中双击 app.db，按照向导 完成，在 PyCharm 中可以看到 SQLite 的数据库 app.db
>
> 2. 此时，app.db 中有 7张表：**5 张是程序创建的业务表（users、sessions、messages、presets、user_configs）；2 张是 SQLite 系统表（sqlite_master、sqlite_sequence），是自动生成的，由 SQLite 内部维护，不能也不需要手动删除。**分别为：
>
>    | 表名            | 来源            | 作用                                                         |
>    | --------------- | --------------- | ------------------------------------------------------------ |
>    | users           | 你的代码建的    | 业务表                                                       |
>    | sessions        | 你的代码建的    | 业务表                                                       |
>    | messages        | 你的代码建的    | 业务表                                                       |
>    | presets         | 你的代码建的    | 业务表                                                       |
>    | user_configs    | 你的代码建的    | 业务表                                                       |
>    | sqlite_master   | SQLite 自动生成 | 系统表，记录数据库里所有表、索引、视图的结构信息（SQL标准内置） |
>    | sqlite_sequence | SQLite 自动生成 | 系统表，记录每个 AUTOINCREMENT 表的当前自增计数器值（所以重复运行时 id 会递增，就是它在记录） |
>
> 3. 凡是用了 `AUTOINCREMENT` 的 SQLite 数据库，都会自动有 `sqlite_sequence` 表来跟踪自增计数。`sqlite_master` 则是每个 SQLite 数据库都有的元数据表。这两张表由 SQLite 内部维护，不需要也不能手动删。

### 6.5 关于 data 目录的说明

`data/` 目录被 .gitignore 排除（Step 1 已配置），所以 app.db 不会进入版本库。这是合理的：数据库文件是运行时产物，每人本地生成，不应提交。第一次运行 init_db.py 时，代码会自动创建 data/sqlite/ 目录（`mkdir parents=True, exist_ok=True`），无需手动建。

---

## 七、版本控制

### 7.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 修改：`pyproject.toml`（uv add aiosqlite）、`uv.lock`（锁文件更新）、`docs/Step2-...md`（ Step 2 修订后未提交的文档，如果有）。
- 新增：`src/storage/factory.py`、`src/storage/sqlite_backend.py`、`scripts/`（含 __init__.py 和 init_db.py）。
- 不应出现：`data/`（被 gitignore 排除）、`.env`、`.venv/`。

### 7.2 提交与打标签

第 1 步：暂存所有修改：

```bash
git add .
```

第 2 步：提交前检查：

```bash
git status
```

第 3 步：提交：

```bash
git commit -m "feat: step 3 - SQLite 存储后端、工厂模式与数据库初始化"
```

第 4 步：打标签：

```bash
git tag step-3-sqlite
```

第 5 步：推送代码与标签：

```bash
git push
git push origin step-3-sqlite
```

第 6 步：验证：

```bash
git log --oneline -4
git tag
```

---

## 八、常见问题与排查

### 8.1 aiosqlite 相关

| 报错 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'aiosqlite'` | 未安装 | `uv add aiosqlite` |
| `RuntimeError: no running event loop` | 直接调用了 async 方法但没用 await 或 asyncio.run | 确保用 `await backend.xxx()` 且最外层用 asyncio.run 启动 |

### 8.2 数据库相关

| 报错 | 原因 | 解决 |
|------|------|------|
| `unable to open database file` | data/sqlite 目录不存在且代码没建目录 | 确认 initialize 里有 `Path(self.db_path).parent.mkdir(...)` |
| `no such table: users` | 没调用 initialize 就操作了 | 先 `await backend.initialize()` 再操作 |
| `FOREIGN KEY constraint failed` | 插入了不存在的外键引用（如 user_id 指向不存在的用户） | 先创建被引用的实体（如先建用户再建会话） |

### 8.3 级联删除不生效

如果删除用户后会话没被自动删除，检查两点：

1. 是否执行了 `PRAGMA foreign_keys = ON`（SQLite 默认关闭外键）。
2. 建表时是否写了 `ON DELETE CASCADE`。

### 8.4 重复运行 init_db.py 的 id 递增

每次运行 init_db.py，创建的用户/会话 id 会比上次更大（即使上次删除了）。

原因是 SQLite 用 sqlite_sequence 系统表记录每个 AUTOINCREMENT 表的自增计数器，

该计数器只增不减。这是正常行为，不是 bug。

---

## 九、本步骤小结与知识清单

### 9.1 产出清单

| 类别 | 产出 |
|------|------|
| 存储层 | src/storage/factory.py（工厂模式）、src/storage/sqlite_backend.py（20 个方法实现） |
| 脚本 | scripts/\_\_init\_\_.py、scripts/init_db.py（初始化与冒烟测试） |
| 新依赖 | aiosqlite 0.22.1 |
| 版本控制 | 提交 feat: step 3、标签 step-3-sqlite |

### 9.2 知识清单

学完本步骤，应当掌握：

- SQLite 的特点（轻量、单文件、零配置）与适用场景。
- 同步驱动（sqlite3）与异步驱动（aiosqlite）的区别，以及本项目选异步的理由。
- aiosqlite 的基本用法（connect、execute、commit、fetchone/fetchall、close）。
- 工厂模式的作用（解耦业务代码与具体后端）。
- SQL 基础（CREATE TABLE、INSERT、SELECT、UPDATE、DELETE、WHERE、ORDER BY、LIKE）。
- 外键与级联删除（FOREIGN KEY、ON DELETE CASCADE）。
- 参数化查询（防 SQL 注入，用 `?` 占位）。
- datetime 的存储与读取（ISO 字符串互转）。
- 软件测试的类型体系（单元/集成/系统、黑盒/白盒、冒烟/回归）。
- 冒烟测试的作用与实现。
- sys.path 注入（让 scripts/ 下的脚本能 import src/ 下的模块）。

### 9.3 项目当前状态

```
langchain-chat @ step-3-sqlite
本地 git 仓库：已提交
Gitee 远程仓库：已推送（代码与标签）
Python 版本：3.12.13
第三方依赖：7 个（Step 2 的 6 个 + aiosqlite）
存储层：SQLite 后端已实现，可建库建表、增删改查
可运行：uv run python scripts/init_db.py 建库并通过冒烟测试
```

### 9.4 后续步骤预告

Step 4：用户管理模块 + TUI 用户菜单。

目标：实现用户管理（创建/切换/删除用户），对接 TUI 菜单，让用户数据真正存入 SQLite。

核心技术：UserManager（业务层）、TUI 用户菜单（界面层）、Step 2 的桩函数 show_user_menu 将被真实功能替换。

Step 4 起，存储层将真正接入业务和界面，数据开始在层与层之间流动。

---

> 本文档为 langchain-chat 项目 Step 3 的教学手册。按本文档操作，可从零独立完成 SQLite 存储后端的全部实现。操作过程中如遇问题，可参考第八部分排查，或微信随时询问我。
