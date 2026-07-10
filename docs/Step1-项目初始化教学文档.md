# Step 1：项目初始化与工程化配置（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-24
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-1-init`

---

## 阅读说明

本文档是 langchain-chat 项目第一步的完整教学手册。阅读并跟随操作后，你应当能够：

1. 理解虚拟环境、包管理、项目配置、版本控制等工程化基础概念。
2. 理解本项目采用的分层配置体系及其设计理由。
3. 从零开始，独立搭建一个可运行、可追溯、可推送的 Python 项目骨架。

**本文档的设计原则**：

- 每一个概念都用「3W1H」框架讲解（What 是什么、Why 为什么需要、Which 为什么这样选、How 怎么做）。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 不仅讲「怎么做」，还讲「为什么这么做」「不这么做会怎样」「遇到问题怎么排查」。

**完成标志（学完本章后你应达成的目标）**：

- 项目目录结构完整，符合需求文档规定。
- 执行 `uv run python src/main.py` 能打印启动横幅，且横幅显示 Python 版本为 3.12.13。
- 本地 Git 仓库已建立，存在提交 `chore: step 1 - 项目初始化与工程化配置` 与标签 `step-1-init`。
- 代码与标签已成功推送到 Gitee 远程仓库。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置环境确认](#二前置环境确认)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、两个关键设计讨论](#四两个关键设计讨论)
- [五、动手实践：创建项目文件](#五动手实践创建项目文件)
- [六、运行验证](#六运行验证)
- [七、版本控制：Git 提交与标签](#七版本控制git-提交与标签)
- [八、推送到 Gitee 远程仓库](#八推送到-gitee-远程仓库)
- [九、常见问题与经验总结](#九常见问题与经验总结)
- [十、本步骤小结与知识清单](#十本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

搭建项目的「地基」：建立目录骨架、编写工程化配置文件、建立版本控制仓库。这一步故意**不引入任何第三方依赖**，只用 Python 标准库，目的是先证明「项目能跑起来」这个最小闭环，再在后续步骤逐步引入 LangChain、rich 等库。这是**工程纪律**的体现：地基先稳，再加砖。

### 1.2 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | 需求说明文档、实施步骤计划、空的 `langchain-chat/` 目录（仅含 docs 文档） |
| 输出 | 完整的项目骨架（配置文件 + 入口源码 + 本地 Git 仓库 + 远程仓库） |
| MVP 验证点 | `uv run python src/main.py` 能打印启动横幅 |

### 1.3 本步骤产出的文件清单

```
langchain-chat/
├── pyproject.toml          项目元数据与依赖声明
├── .gitignore              Git 忽略规则
├── .env.example            环境变量模板（不含真实值）
├── config.yaml             全局业务配置
├── config/
│   ├── presets.yaml        系统内置预设（数据层）
│   └── logging.yaml        日志配置
├── README.md               项目说明
├── src/
│   ├── __init__.py         源码包标识
│   └── main.py             程序入口
└── uv.lock                 uv 自动生成的依赖锁文件
```

---

## 二、前置环境确认

在动手之前，必须先确认开发环境就绪。这是工程化开发的第一步：**永远先验证工具链，再开始编码**。

### 2.1 需要确认的三件工具

| 工具 | 作用 | 本项目要求 |
|------|------|-----------|
| Git | 版本控制 | 已安装即可 |
| uv | Python 包管理器（管理 Python 版本、虚拟环境、依赖） | 已安装即可 |
| Python | 运行语言 | 需要 3.12 版本 |

### 2.2 检查方法（逐项执行）

打开命令行（Windows 按 Win+R 输入 cmd，或使用 PowerShell），执行：

```bash
git --version
uv --version
```

正常情况下会输出版本号，例如：

```
git version 2.49.0.windows.1
uv 0.11.8 (...)
```

查看 uv 已经管理的 Python 版本：

```bash
uv python list --only-installed
```

### 2.3 关于系统 PATH 上的 Python

初学者常遇到的困惑：执行 `where python` 可能只看到一个「Windows 商店占位符」程序（位于 `WindowsApps` 目录），它并不是一个真正可用的 Python，而是一个引导你前往应用商店下载的跳转程序。

**这不会成为问题**。原因在于：本项目使用 uv 管理依赖，uv 会自动为其管理的 Python 版本创建虚拟环境，命令 `uv run` 会使用项目专属的虚拟环境，完全不依赖系统 PATH 上的 Python。

> 核心结论：只要 uv 已安装，且 uv 管理了 Python 3.12，本项目就能正常运行，无论系统 PATH 上是否有可用的 Python。

### 2.4 Python 版本选择的依据

本项目需求文档要求 Python 3.10 及以上。我们在环境确认时发现机器上同时存在 3.13 与 3.12，最终选择固定使用 3.12，理由如下：

1. 3.12 比 3.13 更成熟稳定，第三方库（尤其 LangChain 全家桶、aiosqlite 等）对 3.12 的兼容性验证更充分。
2. 教学项目应追求稳定可复现，而非追新。

这一选择将通过 `pyproject.toml` 中的 `requires-python` 字段在版本约束层面强制锁定，具体见第五章。

### 2.5 环境确认报告（本步骤实际结果）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| Git | 2.49.0 | 可用 |
| uv | 0.11.8 | 可用 |
| Python（uv 托管） | 3.12.13 | 满足要求，本项目锁定此版本 |
| 系统 PATH 上的 Python | Windows 商店占位符 | 不可用，但不影响项目 |

环境确认通过，可以开始动手。

说明：如果没有显示任何 Python 的版本，即：系统中没有安装任何版本的 Python，需要使用 uv install 命令添加指定版本的 Python，如： uv python install 3.12

---

## 三、核心概念讲解（3W1H）

本步骤涉及五个关键概念，逐个用 3W1H 框架讲解。

### 3.1 虚拟环境与 uv

**What（是什么）**

虚拟环境是一个隔离的、项目专属的 Python 运行空间。可以把整个系统想象成一栋大楼，全局 Python 是公共区域（所有项目共享），而虚拟环境是每个项目独立的房间，房间里只放该项目需要的库。

```
系统（全局 Python）
├── 全局安装的库：所有项目共享
└── langchain-chat 专属虚拟环境（.venv 目录）
    └── 只有本项目需要的库：langchain、rich、aiosqlite 等
        （别的项目看不见、不受影响）
```

**Why（为什么需要）**

没有虚拟环境会出现三类问题：

1. 依赖冲突：项目 A 需要 langchain 1.3，项目 B 需要 langchain 0.3，全局只能装一个版本，必有一方无法运行。
2. 依赖不可追溯：换电脑或重装系统时，无法精确回忆本项目依赖了哪些库。
3. 环境不一致：在「我的电脑上能运行」到别人电脑上就报错，这是开发中经典的灾难场景。

有了虚拟环境，每个项目的依赖相互隔离、可精确复现，这是 Python 工程化的第一原则。

**Which（为什么选 uv）**

| 工具 | 速度 | 特点 | 评价 |
|------|------|------|------|
| venv | 慢 | Python 内置，只能建环境，装包还需 pip | 基础但繁琐 |
| pipenv | 慢 | 环境加依赖一体，但久不更新 | 逐渐被弃用 |
| poetry | 中 | 功能全、成熟，但较重 | 老牌选择 |
| uv | 极快（比传统快 10 到 100 倍） | 集版本管理、环境、依赖、锁文件于一身 | 本项目选用 |

uv 一个工具就把「管理 Python 版本、建虚拟环境、装依赖、锁定版本」全部包揽，且由 Rust 编写，速度极快。

**How（本项目怎么用）**

- uv 在项目里自动创建 `.venv` 目录（虚拟环境），并自动选用 Python 3.12.13。
- 用 `uv run python src/main.py` 运行程序：uv 自动使用项目的 `.venv`，无需手动激活。
- `.venv` 不进入版本库（体积大、不可移植），通过 `.gitignore` 排除。

### 3.2 pyproject.toml

**What（是什么）**

pyproject.toml 是 Python 官方推荐（PEP 621 标准）的项目配置文件，一个文件即可统一管理项目元数据、依赖声明、工具配置。

**Why（为什么需要）**

以前需要 setup.py、requirements.txt、requirements-dev.txt、各种 .cfg 配置文件，分散且混乱。pyproject.toml 把它们统一到一个文件，是当前社区推荐的标准做法。

**How（关键字段）**

- `[project]` 段：项目名、版本、Python 版本要求、依赖列表。
- `[tool.uv]` 段：uv 专属配置。
- `[tool.ruff]` 段、`[tool.pytest.ini_options]` 段：各开发工具的配置。

### 3.3 .gitignore

**What（是什么）**

一个纯文本规则文件，告诉 Git「这些文件或文件夹请忽略，不要追踪、不要提交」。

规则语法要点：

| 写法 | 含义 |
|------|------|
| `.venv/` | 忽略整个目录（末尾的斜杠表示目录） |
| `*.pyc` | 用星号通配符忽略某一类文件 |
| `.env` | 精确忽略某文件 |
| `!文件名` | 叹号表示例外，强制不忽略 |

**Why（为什么需要）**

防止三类东西污染版本库：

1. 敏感信息（`.env` 里的 API Key）：一旦提交，即使删除也留在 Git 历史中，等于永久泄露。
2. 不可移植的（`.venv`、`__pycache__`）：每台机器环境不同，提交毫无意义且体积巨大。
3. 运行时产物（`data/`、日志文件）：属于本地产物。

### 3.4 .env 与 .env.example

**What（是什么）**

- `.env`：存放真正的敏感值（API Key、数据库密码），仅本地存在，绝不提交。
- `.env.example`：存放变量名但不存真值的模板，提交到 Git，告诉协作者「你需要配置这些变量」。

**Why（为什么需要）**

把「密钥本身」和「密钥的结构说明」分开：既能协作，又不泄露。

**Which（方案对比）**

硬编码（危险）、配置文件里写死（可见）、环境变量 `.env`（安全且便捷）三者相比，本项目选用 `.env`。

**How（怎么用）**

用户克隆项目后，复制 `.env.example` 为 `.env`，填入真实值。后续步骤（Step 2 起）代码用 python-dotenv 自动读取 `.env`。

### 3.5 三层配置体系

本项目配置分多个层次，各司其职：

| 层 | 文件 | 存什么 | 是否进 Git |
|----|------|--------|-----------|
| 敏感配置 | `.env` | API Key、数据库密码 | 否 |
| 业务配置 | `config.yaml` | 模型列表、默认设置、存储类型 | 是 |
| 日志配置 | `config/logging.yaml` | 日志格式与级别 | 是 |
| 业务数据 | `config/presets.yaml` | 系统内置预设角色 | 是 |

**一个需要澄清的细节**：presets.yaml 放在 config 目录下，但它的本质是「业务数据」（预设角色定义），而非「配置」。在需求文档的功能描述（G3 配置管理）中，明确点名的配置载体只有三个：`.env`、`config.yaml`、`config/logging.yaml`；presets.yaml 是对应需求文档目录结构（第五章）要求的「数据文件」。理解这一区分有助于建立准确的配置与数据边界意识。

---

## 四、两个关键设计讨论

在动手之前，有两个值得深入讨论的设计问题。这两个问题体现了「先想清楚再动手」的工程思维，本文档完整记录讨论过程，供学习者参考。

### 4.1 讨论 1：如何用 Git 上传到远程仓库

#### 4.1.1 远程平台选哪个

| 平台 | 归属 | 国内访问 | 私有库免费 | 特点 |
|------|------|---------|-----------|------|
| GitHub | 美国（微软） | 时好时坏，有时需代理 | 是 | 全球最大、生态最全 |
| Gitee（码云） | 国内 | 极快 | 是 | 国内快、中文友好 |
| GitLab | 美国公司 | 一般 | 是 | 可自托管，企业 CI/CD 最强 |
| 自建 Gitea/Forgejo | 开源 | 取决于服务器 | 是 | 完全自主可控 |

对于本项目（个人、国内、教学性质），推荐 Gitee：国内访问快、无需代理、私有库免费。若兼顾对外展示，可同时推送到 GitHub 与 Gitee。

#### 4.1.2 本地仓库与远程仓库的关系

```
本地（你的电脑）                   远程（云端）
┌─────────────────┐              ┌──────────────────┐
│ langchain-chat/ │  git push -> │ gitee.com/.../   │
│ (.git/)         | <- git pull  │ langchain-chat   │
└─────────────────┘              └──────────────────┘
```

- `git push`：把本地提交推上去。
- `git pull`：把远程更新拉下来。
- `git remote`：管理远程地址（一个本地仓库可挂多个远程）。

#### 4.1.3 身份验证：HTTPS 与 SSH

| 方式 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| HTTPS | 每次用用户名加令牌认证 | 简单，零前置配置 | 需配置令牌（可让 Git 记住） |
| SSH | 本地生成密钥对，公钥贴到平台 | 一次配置，终身免密 | 初次配置略繁琐 |

本项目先用 HTTPS（最简单），后续可随时切换到 SSH。

> 重要：Gitee 与 GitHub 一样，HTTPS 推送时不能用网页登录密码，必须使用「私人访问令牌」（Personal Access Token）作为密码。详见第八章。

### 4.2 讨论 2：三层配置是否符合需求与企业最佳实践

#### 4.2.1 是否符合需求文档

需求文档 G3（配置管理）原文明确三个载体：

- `.env` 管理敏感信息（API Key、数据库密码）。
- `config.yaml` 管理全局配置（模型列表、默认设置、存储类型）。
- `config/logging.yaml` 管理日志配置。

本项目的三层配置与需求文档逐字对应，完全符合。presets.yaml 属于「数据」而非「配置」，对应需求文档目录结构的要求。

#### 4.2.2 是否符合企业最佳实践

| 业界原则 | 本项目的做法 | 是否符合 |
|---------|------------|---------|
| 敏感信息绝不进代码库（12-Factor 第 3 条） | .env 放密钥，.gitignore 排除，配 .env.example | 符合 |
| 配置与代码分离 | 用 .env 与 config.yaml 而非硬编码 | 符合 |
| 配置校验（类型安全） | 选用 pydantic-settings，Step 2 落地 | 符合（已规划） |
| 日志独立配置 | 单独 config/logging.yaml | 符合 |
| 环境区分（dev/test/prod） | 当前未实现 | 待改进 |

#### 4.2.3 关于环境区分的讨论与决定

企业级最佳实践通常会区分运行环境（开发、测试、生产），因为不同环境用的模型、数据库、密钥各不相同。

对本项目的决定是：**当前阶段（Step 1 至 Step 14）不实现多环境区分，但在项目最终完成后（Step 15）必须实现并验证。**

理由有三：

1. 遵循 YAGNI 原则（You Aren't Gonna Need It，不过度设计）：当前阶段只有一个运行环境，引入多环境会增加复杂度。
2. 多环境属于「运行与部署层面」的增强，放最后实现最合理。
3. 当前阶段在结构上预留扩展点，保证将来无需推倒重来。

#### 4.2.4 这一需求的落地保障

为确保该需求不被遗忘，采取三项保障措施：

1. 新建《需求变更与扩展登记》文档，将该需求登记为 REQ-001，包含完整描述、预留扩展点、验收标准。
2. 更新《实施步骤计划》至 v1.2，新增 Step 15（多环境配置区分实现与验证）。
3. 在 Step 1 的 config.yaml 中以注释形式预留 `app.env` 字段，为将来留好扩展点。

这是一条贯穿全项目的重要约定，记于文档，后续可追溯。

---

## 五、动手实践：创建项目文件

下面依次创建项目骨架的所有文件。每个文件都给出完整内容与字段说明，学习者可直接对照创建。

> 文件位置约定：本章涉及的文件均在项目根目录 `langchain-chat/` 下创建。其中 config 子目录下的两个文件（presets.yaml、logging.yaml）需先建立 `config/` 文件夹；src 子目录下的两个文件需先建立 `src/` 文件夹。文件编码统一使用 UTF-8（不带 BOM），以保证中文正常显示。每个小节标题旁会标注该文件相对于项目根目录的路径。

### 5.1 创建 pyproject.toml

文件路径：`langchain-chat/pyproject.toml`（项目根目录）。

这是项目的「身份证」，最先创建，因为它定义了 Python 版本与依赖。

**文件内容**：

```toml
# pyproject.toml —— langchain-chat 项目配置文件

# [project] 项目本身的信息与依赖（PEP 621 标准段）
[project]
name = "langchain-chat"                       # 项目名，也是包名
version = "0.1.0"                             # 语义化版本：主版本.次版本.修订号
description = "基于 LangChain 的多轮会话系统（教学项目）"
readme = "README.md"                          # 指向 README 文件
requires-python = ">=3.10,<3.13"              # 关键：锁定 Python 版本范围
                                              #   >=3.10：需求文档要求最低 3.10
                                              #   <3.13 ：本项目约定使用 3.12，强制锁定
dependencies = []                             # Step 1 阶段无第三方依赖

# [tool.uv] uv 专属配置
[tool.uv]
package = false                               # 本阶段不是可安装包，而是脚本集合

# [tool.ruff] ruff 配置（代码格式化与 Lint）
[tool.ruff]
line-length = 100                             # 每行最多 100 字符
target-version = "py310"                      # ruff 按 Python 3.10 语法检查

# [tool.pytest.ini_options] pytest 配置（Step 13 单元测试启用）
[tool.pytest.ini_options]
asyncio_mode = "auto"                         # 自动识别异步测试函数
testpaths = ["tests"]                         # 测试文件查找目录
```

**关键讲解：requires-python 的版本约束**

`requires-python = ">=3.10,<3.13"` 这一行精确落实两个要求：

- `>=3.10`：需求文档要求的最低版本。
- `<3.13`：本项目约定使用 3.12，从版本约束层面强制锁定，即使别人拿到项目也装不了 3.13。

**用 uv 创建虚拟环境并验证**

创建 pyproject.toml 后，在项目根目录执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv sync
```

uv 会读取 pyproject.toml，按版本约束选用 Python 3.12.13，创建 `.venv` 虚拟环境，同时会创建 `uv.lock` 依赖锁定文件（项目当前依赖环境的“精确版本清单”） 。

预期输出：

```
Using CPython 3.12.13
Creating virtual environment at: .venv
Resolved 1 package in 5ms
Checked in 0.01ms
```

验证虚拟环境的 Python 版本：

```bash
uv run python --version
```

预期输出（必须是 3.12.13）：

```
Python 3.12.13
```

### 5.2 创建 .gitignore

文件路径：`langchain-chat/.gitignore`（项目根目录）。

**文件内容**：

```gitignore
# 1. Python 虚拟环境（不可移植）
.venv/
venv/
env/
ENV/
.python-version

# 2. Python 字节码缓存
__pycache__/
*.py[cod]
*$py.class
*.so

# 3. 敏感配置（含 API Key / 数据库密码，绝不进版本库）
#    .env.dev/.test/.prod 为 Step 15 多环境预留
.env
.env.local
.env.dev
.env.test
.env.prod
!.env.example

# 4. 运行时数据与日志
data/
logs/
*.log
*.sqlite
*.db

# 5. 测试与覆盖率产物
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/

# 6. IDE / 编辑器个人配置
.idea/
.vscode/
*.swp
*.swo

# 7. 操作系统生成的垃圾文件
Thumbs.db
ehthumbs.db
Desktop.ini
.DS_Store
*~
```

**讲解：两处重点**

第一，`.env` 被忽略，但 `!.env.example` 用叹号强制保留模板。这样协作者能看到需要配置哪些变量，但看不到真实密钥。

第二，`.env.dev`、`.env.test`、`.env.prod` 提前写进忽略规则，是为 Step 15 多环境需求预留。

### 5.3 创建 .env.example

文件路径：`langchain-chat/.env.example`（项目根目录）。

**文件内容**：

```bash
# .env.example —— 环境变量模板（安全配置说明）
# 使用方式：复制本文件为 .env，再填入真实值。
# 重要：永远不要把真实密钥填进 .env.example，也不要 git add .env。

# LLM 服务配置（OpenAI 兼容格式）
API_BASE_URL=https://api.example.com/v1
API_KEY=your_api_key_here
MODEL_NAME=deepseek-chat

# 数据库密码（仅 MySQL 后端需要）
MYSQL_PASSWORD=your_mysql_password_here

# 运行环境（多环境区分预留，Step 15 启用）
# APP_ENV=dev
```

### 5.4 创建 config.yaml

文件路径：`langchain-chat/config.yaml`（项目根目录）。

这是本步骤最需要思考的文件，因为它直接体现「配置分层与多环境扩展点预留」的设计。

**文件内容**：

```yaml
# config.yaml —— langchain-chat 全局业务配置

# 多环境扩展点（REQ-001 / Step 15）：
#   本文件是「基础配置」，所有环境共享。
#   未来通过 config.{env}.yaml（dev/test/prod）做「覆盖」，合并机制为：
#       最终配置 = config.yaml（基础）+ config.{APP_ENV}.yaml（覆盖）
#   当前阶段单环境运行，app.env 留空注释。

# 应用元信息
app:
  name: langchain-chat
  version: 0.1.0
  # env: dev   # 多环境预留，Step 15 启用

# 模型配置（API_BASE_URL/API_KEY/MODEL_NAME 真实值在 .env 中）
models:
  default: deepseek-chat
  available:
    - name: DeepSeek Chat
      value: deepseek-chat
    - name: DeepSeek Reasoner
      value: deepseek-reasoner
  temperature: 0.7
  max_tokens: 2048

# 存储配置
storage:
  type: sqlite
  sqlite:
    path: data/sqlite/app.db
  mysql:
    host: localhost
    port: 3306
    user: root
    database: langchain_chat
    # password 从 .env 的 MYSQL_PASSWORD 读取
  file:
    path: data/filestore

# LLM 调用参数（需求 G1 超时与重试）
llm:
  timeout: 30
  max_retries: 3

# 会话配置（需求 C7 会话标题自动生成）
session:
  title_max_length: 30

# 导出配置（需求 F2）
export:
  dir: data/users/{username}/exports
  filename_template: "{title}_{date}.md"
```

**讲解：多环境扩展点的设计原则**

- config.yaml 写「基础配置与默认值」，所有环境共享。
- 将来 config.{env}.yaml 只写「覆盖项」，实现「基础配置加环境覆盖」的合并。
- 现在 `app.env` 用注释形式预留，字段命名按「将来可被覆盖」组织。
- 这样 Step 15 是纯增量（新增覆盖文件加改造加载逻辑），零修改现有配置。

### 5.5 创建 config/presets.yaml

文件路径：`langchain-chat/config/presets.yaml`（需先建立 config 子目录）。

这是系统内置的角色预设，需求 D1 要求所有用户共享。

**文件内容**：

```yaml
# config/presets.yaml —— 系统内置预设 Prompt（全局共享）
# 性质：业务数据（预设角色定义），非配置。

presets:
  - name: 通用助手
    description: 默认的通用对话助手，无特定角色
    system_prompt: |
      你是一个乐于助人的 AI 助手。请用清晰、准确的中文回答用户问题。

  - name: 翻译助手
    description: 中英互译，支持润色
    system_prompt: |
      你是一个专业翻译助手。用户发送内容后，请：
      1. 如果是中文，翻译成英文；如果是英文，翻译成中文。
      2. 翻译要准确、自然、符合目标语言习惯。

  - name: 代码专家
    description: 编程问题解答与代码审查
    system_prompt: |
      你是一个资深编程专家，精通多种编程语言。请用专业、严谨的态度回答编程问题。

  - name: 创意写手
    description: 文案、故事、创意写作
    system_prompt: |
      你是一个富有创意的写作助手，擅长文案、故事、诗歌等创意写作。

  - name: 英语老师
    description: 英语学习辅导与纠错
    system_prompt: |
      你是一个耐心的英语老师。请用简单易懂的方式解释英语知识点，纠正语法错误。
```

### 5.6 创建 config/logging.yaml

文件路径：`langchain-chat/config/logging.yaml`（config 子目录下）。

**文件内容**：

```yaml
# config/logging.yaml —— 日志配置
# 加载方式（Step 12 实现）：
#   logging.config.dictConfig(yaml.safe_load(open("config/logging.yaml")))

formatters:
  console:
    format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"
  json:
    format: "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt: "%Y-%m-%dT%H:%M:%S"

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: console
    stream: ext://sys.stderr
  file:
    class: logging.handlers.TimedRotatingFileHandler
    level: INFO
    formatter: json
    filename: logs/app.log
    when: midnight
    backupCount: 7
    encoding: utf8

root:
  level: DEBUG
  handlers: [console, file]

loggers:
  urllib3:
    level: WARNING
  asyncio:
    level: WARNING
```

本文件格式严格遵循 Python 标准库 logging.config.dictConfig 的 schema，Step 12 可一行代码加载。

### 5.7 创建 README.md

文件路径：`langchain-chat/README.md`（项目根目录）。

README 是项目的门面，任何人克隆后第一眼看到的就是它。内容包含项目介绍、特性、技术栈、目录结构、快速开始、配置说明、开发步骤。

**文件内容**：

````markdown
# LangChain Chat

> 基于 LangChain 的多轮会话系统（教学项目）

一个以学习企业级 Python 开发流程为目标的项目：从零开始，按步骤搭建一个具备多轮对话、用户管理、会话管理、预设系统、可插拔存储的多功能 AI 对话终端应用。每一步都产出可运行、可验证的最小可用产品（MVP）。

## 项目特性

- 基于 LangChain：使用 langchain 与 langchain-openai 构建，兼容所有 OpenAI 接口格式的模型。
- 多轮对话：基于 Memory 机制保持上下文连贯，逐 token 流式输出。
- 用户管理：多用户隔离，数据互不可见。
- 预设系统：内置角色预设加用户自定义预设。
- 可插拔存储：SQLite、MySQL、文件三种后端，配置文件一键切换。
- 全链路异步：LLM 调用、IO、数据库全部 async/await。
- 教学导向：按 3W1H 框架讲解，每步 Git commit 加 tag 可回退。

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.12（要求 3.10 及以上） |
| LLM 框架 | langchain、langchain-openai |
| 异步数据库 | aiosqlite、aiomysql |
| TUI 终端 | rich、prompt_toolkit |
| 配置校验 | pydantic、pydantic-settings |
| 包管理 | uv |
| 测试 | pytest、pytest-asyncio |
| 代码质量 | ruff |

## 目录结构

langchain-chat/
├── .env.example            环境变量模板（复制为 .env 后填写真实值）
├── .gitignore              Git 忽略规则
├── config.yaml             全局业务配置
├── config/
│   ├── presets.yaml        系统内置预设（角色定义）
│   └── logging.yaml        日志配置
├── pyproject.toml          项目元数据与依赖
├── data/                   运行时数据（gitignore，自动创建）
├── src/                    源码
│   └── main.py             程序入口
├── docs/                   项目文档
└── README.md               本文件

## 快速开始

1. 环境要求：Python 3.12（要求 3.10 及以上）、uv。
2. 检查 uv：`uv --version`。
3. 克隆并配置：

```bash
git clone <仓库地址>
cd langchain-chat
copy .env.example .env
编辑 .env，填入 API_BASE_URL、API_KEY、MODEL_NAME。
```

4. 安装依赖并运行：

```bash
uv sync
uv run python src/main.py
```
````


**配置说明**

本项目采用分层配置：

| 层 | 文件 | 内容 | 进 git |
|----|------|------|--------|
| 敏感配置 | .env | API Key、数据库密码 | 否 |
| 业务配置 | config.yaml | 模型列表、存储类型、超时等 | 是 |
| 日志配置 | config/logging.yaml | 日志格式与级别 | 是 |
| 业务数据 | config/presets.yaml | 系统内置预设角色 | 是 |

**开发步骤**

项目按 15 个步骤推进，每步有对应的 Git tag，可随时回退到任意步骤。完整步骤说明见 docs/实施步骤计划.md。

**文档**：需创建 docs 文件夹，并将下述文件（5个）放入

- docs/需求说明文档.md
- docs/实施步骤计划.md
- docs/需求变更与扩展登记.md
- docs/Git命令与操作教学.md
- docs/uv包管理器教学文档.md

### 5.8 创建 src/__init__.py 与 src/main.py

文件路径：`langchain-chat/src/__init__.py` 与 `langchain-chat/src/main.py`（需先建立 src 子目录）。

**`src/__init__.py` 的作用**：告诉 Python「src 是一个包」。虽然是空文件（或仅含文档字符串），但显式建立它能让 IDE 更好识别项目结构。

**src/main.py 的作用**：程序总入口。Step 1 阶段只打印启动横幅。

**关于 `if __name__ == "__main__"`: 模式**

这是 Python 的经典入口守护模式：

```python
if __name__ == "__main__":
    main()
```



含义：括号里的代码只在「直接运行本文件」时执行，被其他模块 import 时不会执行。好处是这个文件既能直接运行，又能被安全复用，是 Python 工程的基本素养。

**src/main.py 文件内容**：

```python
"""langchain-chat 程序总入口。

Step 1 阶段：仅打印启动横幅，验证项目骨架可运行（零第三方依赖）。
运行方式：uv run python src/main.py
"""

# 仅使用 Python 标准库，体现 Step 1「零依赖」设计意图
import platform
import sys
from datetime import datetime

# 项目常量
APP_NAME = "langchain-chat"
APP_VERSION = "0.1.0"
CURRENT_STEP = "Step 1：项目初始化与工程化配置"


def print_banner() -> None:
    """打印启动横幅。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banner = f"""
================================================================================
  {APP_NAME}  v{APP_VERSION}
================================================================================
  Python 版本  : {platform.python_version()}   ({sys.version.split()[0]})
  运行平台     : {platform.system()} {platform.machine()}
  启动时间     : {now}
  当前进度     : {CURRENT_STEP}
================================================================================
"""
    print(banner)
    print(f"[完成] {APP_NAME} 项目已启动（{CURRENT_STEP}）")


def main() -> None:
    """程序主函数。"""
    print_banner()


if __name__ == "__main__":
    main()
```

---

## 六、运行验证

所有文件创建完毕后，执行核心验证。

### 6.1 执行验证命令

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python src/main.py 
```

### 6.2 预期输出

```
================================================================================
  langchain-chat  v0.1.0
================================================================================
  Python 版本  : 3.12.13   (3.12.13)
  运行平台     : Windows AMD64
  启动时间     : 2026-06-24 13:40:30
  当前进度     : Step 1：项目初始化与工程化配置
================================================================================

[完成] langchain-chat 项目已启动（Step 1：项目初始化与工程化配置）
```

### 6.3 验证要点（确认三件事）

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 程序能跑起来 | 无报错，正常输出 | 项目骨架成立 |
| Python 版本是 3.12.13 | 横幅里显示 3.12.13 | 落实锁定 3.12 的约定 |
| 零第三方依赖 | 无需安装任何包 | 验证 Step 1 纯标准库设计 |

至此，项目的第一个里程碑达成：地基立住了。

---

## 七、版本控制：Git 提交与标签

### 7.1 命令逐条讲解

**git init**：初始化仓库，在当前目录创建 `.git` 隐藏文件夹，把它变成 Git 仓库。

**git branch -M main**：把默认分支命名为 main。新版 Git 默认分支可能叫 master，现代社区统一改为 main。参数 -M 表示强制重命名。

**git add .**：把当前目录所有文件加入暂存区。`.gitignore` 会自动生效，排除不该提交的文件。

**git status**：查看暂存区状态。养成习惯：每次提交前先看这个，确认没有误把敏感文件加进去。

**git commit -m**：提交到仓库，生成一个版本快照。-m 后是提交信息，遵循规范「类型: step X - 描述」。

**git tag**：给当前提交打标签，作为里程碑。

### 7.2 关于 uv.lock 是否提交

uv.lock 是 uv 自动生成的依赖锁文件，记录精确版本，保证别人克隆后 `uv sync` 能装出完全一致的环境。它必须提交，不能被 .gitignore 排除。它和 pyproject.toml 是一对：pyproject 声明「我要什么」，uv.lock 记录「实际锁定了什么版本」，是可复现构建的关键。

### 7.3 提交信息与标签命名规范

提交信息格式：`类型: step 编号 - 简要描述`，类型包括 feat（新功能）、fix（修复）、docs（文档）、refactor（重构）、style（格式）、test（测试）、chore（构建与工具）。

标签格式：`step-编号-简短标识`，本步骤为 `step-1-init`。

### 7.4 请执行的完整命令

> 说明：下面的命令需逐条执行。代码块中用 `#` 开头的是说明文字（注释），不是要执行的命令，跳过即可。其中 `cd /d` 是 Windows 命令提示符（cmd）的写法，PowerShell 用户直接写 `cd D:\AllMyVC\ZCodeProject\langchain-chat` 即可。

第 0 步：配置 git 身份（仅首次需要，已配置过可跳过）：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

关于 你的名字 和 你的邮箱@example.com，是否需要和你的 gitee 账号的名称和邮箱一致：

技术上：**可以不一致，不会影响 `git commit` 本身。**

但实际使用 Gitee 时：**不建议随意写，尤其是 `user.email` 不建议乱写。**

原因：不是 Gitee 登录账号密码，也不是认证信息。是写入 Git 提交记录里的 **提交作者身份**。

Git 官方文档说明，`user.name` 和 `user.email` 会决定 commit 对象中的 author / committer 字段；也就是说，每次提交都会永久记录这两个信息。

**企业级最佳实践：**

**`user.name`**：`user.name` 可以和 Gitee 用户名不一致。

**`user.email`**：推荐一致。

```markdown
me: tjliwei / tjliwei@hotmail.com
```

第 1 步：进入项目目录并初始化仓库：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git init
```

之后，会生成 .git 文件夹。

第 2 步：把默认分支改名为 main：

```bash
git branch -M main
```

第 3 步：把所有文件加入暂存区：

```bash
git add .
```

第 4 步：提交前检查（重点确认没有 .env 或 .venv 混入）：

```bash
git status
```

应该输出，类似如下：

```bash
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   .env.example
        new file:   .gitignore
        new file:   README.md
        new file:   config.yaml
        new file:   config/logging.yaml
        new file:   config/presets.yaml
        new file:   docs/Git命令与操作教学.md
        new file:   docs/uv包管理器教学文档.md
        new file:   docs/实施步骤计划.md
        new file:   docs/需求变更与扩展登记.md
        new file:   docs/需求说明文档.md
        new file:   pyproject.toml
        new file:   src/__init__.py
        new file:   src/main.py
        new file:   uv.lock
```

第 5 步：提交到仓库：

```bash
git commit -m "chore: step 1 - 项目初始化与工程化配置"
```

应该输出，类似如下：

```bash
[main (root-commit) 84d928c] chore: step 1 - 项目初始化与工程化配置
 15 files changed, 2177 insertions(+)
 create mode 100644 .env.example
 create mode 100644 .gitignore
 create mode 100644 README.md
 create mode 100644 config.yaml
 create mode 100644 config/logging.yaml
 create mode 100644 config/presets.yaml
 create mode 100644 docs/Git命令与操作教学.md
 create mode 100644 docs/uv包管理器教学文档.md
 create mode 100644 docs/实施步骤计划.md
 create mode 100644 docs/需求变更与扩展登记.md
 create mode 100644 docs/需求说明文档.md
 create mode 100644 pyproject.toml
 create mode 100644 src/__init__.py
 create mode 100644 src/main.py
 create mode 100644 uv.lock
```

第 6 步：打标签：

```bash
git tag step-1-init
```

第 7 步：验证提交历史与标签：

```bash
git log --oneline
# 输出，类似： 84d928c (HEAD -> main, tag: step-1-init) chore: step 1 - 项目初始化与工程化配置
git tag
# 输出，类似： step-1-init
```

### 7.5 提交前检查（git status）应看到的内容

应被提交的文件列表（不应包含 .env 与 .venv）：

```
new file:   .env.example
new file:   .gitignore
new file:   README.md
new file:   config.yaml
new file:   config/logging.yaml
new file:   config/presets.yaml
new file:   docs/各文档.md
new file:   pyproject.toml
new file:   src/__init__.py
new file:   src/main.py
new file:   uv.lock
```

如果看到 `.venv/` 或 `.env` 出现，说明 .gitignore 没生效，应停止提交并排查。

### 7.6 关于中文文件名显示为转义序列

在 Windows 上，`git status` 默认会把中文文件名显示为八进制转义序列（例如 `\345\256\236`），这不是数据错误，文件内容完全正常，只是 Git 为了「安全」做了转义。

解决方法（永久关闭文件名转义）：

```bash
git config --global core.quotepath false
```

建议同时配置中文编码相关项，让提交信息与日志中的中文正常显示：

```bash
git config --global i18n.commit.encoding utf-8
git config --global i18n.logoutputencoding utf-8
```

### 7.7 验证结果

执行 `git log --oneline` 与 `git tag` 后应看到：

```
9122600 (HEAD -> main, tag: step-1-init) chore: step 1 - 项目初始化与工程化配置

step-1-init
```

其中 `(HEAD -> main, tag: step-1-init)` 表示当前 HEAD 指向 main 分支，且该提交同时贴着 step-1-init 标签，是完美的初始状态。

---

## 八、推送到 Gitee 远程仓库

### 8.1 第一步：在 Gitee 建空仓库（网页操作）

操作步骤：

1. 浏览器打开 gitee.com，登录。（tel ==186...）
2. 右上角加号，选择「新建仓库」。
3. 填写：仓库名称 langchain-chat，仓库介绍可填项目描述，开源与私有按需选择。
4. 关键：初始化仓库的三个勾选框（设置 .gitignore、设置开源许可证、使用 README 初始化）全部不要勾，否则远程会有内容，导致首次推送冲突。
5. 点「创建」，复制仓库地址（形如 `https://gitee.com/用户名/langchain-chat.git`）。

### 8.2 第二步：生成私人访问令牌

Gitee 的 HTTPS 推送不能用网页登录密码，必须用私人访问令牌。

操作步骤：

1. 鼠标移到右上角头像，点「设置」。
2. 左侧菜单找到「私人令牌」。
3. 点「生成新令牌」。
4. 令牌描述填一个能识别的名字（如 langchain-chat-push），权限勾选 projects（仓库权限）。
5. 点「提交」生成令牌。
6. 重要：令牌只显示一次，立刻复制保存到安全的地方。关掉页面后无法再看到，丢失只能重新生成。

### 8.3 第三步：让 Git 记住凭据

```bash
git config --global credential.helper store
```

作用：把凭据明文存到本地文件（`~/.git-credentials`），以后推送无需再输。权衡说明：store 模式方便但令牌明文存储，适合个人开发机；更安全的 cache 模式只在内存存一段时间。本教学项目用 store 足够。安全提示：这台电脑不要借给不可信的人，将来想清除可删除 `~/.git-credentials` 文件。

### 8.4 第四步：关联远程并推送

第 1 步：关联远程仓库（起名 origin，把下面的「用户名」换成你的 Gitee 用户名）：

```bash
git remote add origin https://gitee.com/用户名/langchain-chat.git
```

第 2 步：验证关联：

```bash
git remote -v
```

第 3 步：首次推送代码（执行后会弹认证窗口：用户名填 Gitee 用户名，密码栏填私人令牌，不要填登录密码）：

```bash
git push -u origin main
```

第 4 步：推送标签（标签默认不随 git push 推送，必须单独推）：

```bash
git push origin step-1-init
```

### 8.5 预期输出

`git remote -v` 应显示：

```
origin  https://gitee.com/用户名/langchain-chat.git (fetch)
origin  https://gitee.com/用户名/langchain-chat.git (push)
```

`git push -u origin main` 成功时类似：

```
To https://gitee.com/用户名/langchain-chat.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

`git push origin step-1-init` 成功时类似：

```
To https://gitee.com/用户名/langchain-chat.git
 * [new tag]         step-1-init -> step-1-init
```

再次执行 `git push` 应显示 `Everything up-to-date` 且不再要求密码，证明凭据已被记住。

### 8.6 重要提醒：标签需要单独推送

`git push` 默认不推送标签。每个步骤的标签必须用 `git push origin 标签名` 单独推送，否则远程看不到里程碑标签。

### 8.7 推送失败排查表

| 现象 | 原因 | 解决 |
|------|------|------|
| Authentication failed | 用户名或令牌错误 | 用户名填 Gitee 用户名，密码栏填令牌而非登录密码 |
| remote origin already exists | origin 已关联过 | 先 git remote remove origin 再重新 add |
| rejected, fetch first | 远程有内容（建仓库时勾了初始化） | 删远程仓库重建空的，或先 pull --allow-unrelated-histories |
| 弹窗一直转圈 | 网络问题 | 检查网络，或改用 SSH |

---

## 九、常见问题与经验总结

### 9.1 关于环境

| 问题 | 结论 |
|------|------|
| 系统 PATH 上没有真正的 Python | 不影响，uv 会自动管理 Python，uv run 使用项目虚拟环境 |
| 是否需要手动激活虚拟环境 | 不需要，uv run 自动使用 .venv |
| uv.lock 是否提交 | 必须提交，是可复现构建的关键 |

### 9.2 关于中文显示

| 问题 | 解决 |
|------|------|
| git status 中文文件名显示为八进制转义 | git config --global core.quotepath false |
| commit message 中文乱码 | git config --global i18n.commit.encoding utf-8 |
| git log 中文乱码 | git config --global i18n.logoutputencoding utf-8 |

### 9.3 关于推送

| 问题 | 结论 |
|------|------|
| HTTPS 推送不能用登录密码 | 使用私人访问令牌作为密码 |
| 标签不随 git push 推送 | 必须单独 git push origin 标签名 |

### 9.4 每个步骤的标准收尾流程

每个开发步骤完成后，按以下顺序操作（命令可逐条执行）：

```bash
git add .
git status
git commit -m "feat: step X - 功能描述"
git tag step-X-xxx
git push
git push origin step-X-xxx
```

各命令的作用：

| 命令 | 作用 |
|------|------|
| `git add .` | 暂存所有修改 |
| `git status` | 检查（重点看有没有 .env 混入） |
| `git commit -m "..."` | 提交 |
| `git tag step-X-xxx` | 打标签 |
| `git push` | 推送代码 |
| `git push origin step-X-xxx` | 推送标签（重要，标签默认不随 git push 推送，必须单独推） |

---

## 十、本步骤小结与知识清单

### 10.1 产出清单

| 类别 | 产出 |
|------|------|
| 配置文件 | pyproject.toml、.gitignore、.env.example、config.yaml、config/presets.yaml、config/logging.yaml |
| 源码 | src/__init__.py、src/main.py |
| 文档 | README.md、需求变更与扩展登记.md（新增）、实施步骤计划.md（升级 v1.2，新增 Step 15） |
| 版本控制 | 本地仓库初始化、提交 9122600、标签 step-1-init |
| 远程 | 推送到 Gitee（代码与标签），凭据已记住 |

### 10.2 知识清单

学完本步骤，应当掌握：

- 虚拟环境的概念，以及 uv 的工作流（uv sync、uv run）。
- pyproject.toml 的标准结构与 Python 版本锁定方法。
- 三层配置体系（敏感、业务、数据）的设计，以及多环境扩展点的预留思路。
- .gitignore 如何保护敏感文件与虚拟环境。
- if __name__ == "__main__": 入口守护模式。
- Git 完整工作流：init、add、status、commit、tag。
- 远程仓库：Gitee 建仓、remote add、push、push tags。
- HTTPS 推送的私人令牌机制与凭据存储。
- Windows 中文环境下的 Git 配置。

### 10.3 项目当前状态

```
langchain-chat @ step-1-init  (commit 9122600)
本地 git 仓库：已建立
Gitee 远程仓库：已推送（代码与标签）
Python 版本：锁定 3.12.13
uv 虚拟环境：已建立
可运行：uv run python src/main.py 打印启动横幅
```

### 10.4 下一步预告

Step 2：数据模型、存储接口、配置管理、TUI 骨架。

目标：第一次看到可交互的 TUI 菜单界面（主菜单含用户管理、会话管理、预设管理、开始对话、设置）。

核心技术：Pydantic（数据校验）、ABC 抽象基类、Rich（终端渲染）、prompt_toolkit（输入）。

Step 2 将首次引入第三方依赖，届时会先讲解每个库的用途与安装方法，再动手开发。

---

> 本文档为 langchain-chat 项目 Step 1 的教学手册。按本文档操作，可从零独立完成项目初始化的全部内容。
