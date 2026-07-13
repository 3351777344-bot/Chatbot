# langchain-chat

基于 LangChain 的异步多用户聊天系统，当前已完成《实施步骤计划》Step 1–15。主线应用为
Rich TUI，支持多轮流式对话、用户与预设管理、历史会话、搜索、Markdown 导出、模型切换，
以及 SQLite、MySQL、JSON File 三种可插拔存储后端。

仓库还保留了早期 `app.py` Streamlit 应用。它使用原有 `database/`、`services/` 等模块，
与 `src/` 下的 Step 1–15 主线架构相互独立。

## 已实现功能

- OpenAI-compatible LLM，异步流式输出、超时重试和 Token 统计
- 多用户创建、切换、删除及数据访问隔离
- 系统内置与用户私有 Prompt 预设
- 会话新建、加载、重命名、删除、自动保存和自动标题
- 当前用户历史消息搜索与会话记录查看
- Markdown 导出、用户默认模型和会话内模型切换
- SQLite、MySQL、JSON File 可插拔存储
- dev/test/prod 配置、密钥、数据库和导出目录隔离
- 控制台日志和 JSON Lines 滚动文件日志
- 13 项离线自动化测试，不访问真实 LLM

## 环境要求

- Python `>=3.10,<3.13`；项目锁定环境当前使用 Python 3.12
- [uv](https://docs.astral.sh/uv/)
- 调用真实模型时需要 OpenAI-compatible API Key
- prod 或手动切换 MySQL 时需要可访问的 MySQL 服务

## 快速开始

在项目根目录执行：

```powershell
uv sync
Copy-Item .env.dev.example .env.dev
# 编辑 .env.dev，填写 API_BASE_URL、API_KEY 和 MODEL_NAME
$env:APP_ENV = "dev"
uv run python src/main.py
```

如果没有配置真实 API Key，菜单、用户、预设、会话和存储功能仍可使用；实际发送对话时模型
调用会失败。真实 `.env*`、`data/` 和 `logs/` 均已被 Git 忽略。

## 多环境配置

最终配置按以下顺序生成：

```text
config.yaml + config.{APP_ENV}.yaml
```

敏感信息从对应的 `.env.{APP_ENV}` 加载。`APP_ENV` 默认是 `dev`，仅接受 `dev`、`test`、
`prod`。为兼容早期项目，只有 dev 在 `.env.dev` 不存在时允许回退到 `.env`；test/prod
不会读取普通 `.env`。

| 环境 | 覆盖配置 | 敏感配置 | 默认存储 | 数据/导出位置 |
|---|---|---|---|---|
| dev | `config.dev.yaml` | `.env.dev` | SQLite | `data/dev/` |
| test | `config.test.yaml` | `.env.test` | SQLite | `data/test/` |
| prod | `config.prod.yaml` | `.env.prod` | MySQL | MySQL + `data/prod/exports/` |

PowerShell 切换示例：

```powershell
$env:APP_ENV = "test"
uv run pytest

$env:APP_ENV = "prod"
uv run python scripts/init_db.py
uv run python src/main.py
```

prod 启动前应从 `.env.prod.example` 创建 `.env.prod`，并填写正式 API Key 和
`MYSQL_PASSWORD`。MySQL 主机、端口、用户和库名在 `config.yaml` 的 `storage.mysql` 中配置。

## TUI 使用说明

主菜单提供用户、会话、预设、对话、搜索和设置功能。首次使用建议：

1. 在“用户管理”中创建用户；第一个用户会自动成为当前用户。
2. 在“预设管理”中选择内置预设，或创建个人预设。
3. 选择“开始对话”；首轮会自动创建并保存会话。
4. 从“会话管理”加载、重命名、删除、查看或导出历史会话。

对话内命令：

| 命令 | 作用 |
|---|---|
| `/help` | 显示命令帮助 |
| `/new` | 新建会话并清空当前上下文 |
| `/rename 新标题` | 修改当前会话标题 |
| `/model 模型名` | 切换当前会话模型并保留历史 |
| `/export` | 导出当前会话为 Markdown |
| `/exit` | 返回主菜单 |

模型名必须存在于 `config.yaml` 的 `models.available` 白名单。

## 存储后端

存储由当前环境覆盖配置中的 `storage.type` 选择：

```yaml
storage:
  type: sqlite  # sqlite | mysql | file
```

- SQLite：默认开发/测试后端，由 `aiosqlite` 异步访问。
- MySQL：生产后端，由 `aiomysql` 异步访问；`scripts/init_db.py` 会创建数据库和表。
- File：将完整数据保存为原子替换的 `store.json`，适合演示和轻量部署。

业务层仅依赖 `StorageBackend`，切换后端不需要修改用户、预设或会话逻辑。

## 测试与质量检查

```powershell
$env:APP_ENV = "test"
uv run pytest
uv run pytest --cov=src --cov-report=term-missing
uv lock --check
uv run python -m compileall -q src tests scripts examples
```

当前基线为 `13 passed`。SQLite 和 File 后端会在临时目录中执行相同的 CRUD、搜索、权限和
级联测试；ChatEngine 使用假模型，不访问网络或消耗 API Key。MySQL 已完成接口、建表 SQL 和
工厂构造验证，真实连接验收需要外部 MySQL 实例。

## 项目结构

```text
Chatbot/
├── config.yaml / config.{dev,test,prod}.yaml
├── .env.example / .env.{dev,test,prod}.example
├── config/                         # 内置预设与日志配置
├── src/
│   ├── core/                       # 配置、日志、对话与领域业务
│   ├── interface/                  # UI 协议及扩展接口
│   ├── models/                     # Pydantic 数据模型
│   ├── storage/                    # 抽象接口、工厂与三种后端
│   ├── ui/tui/                     # Rich + prompt_toolkit TUI
│   └── main.py                     # 主线应用入口
├── scripts/init_db.py              # 当前环境数据库初始化
├── tests/                          # 13 项离线测试
├── examples/                       # 三种 LLM 调用层次示例
├── docs/                           # 需求、架构、状态和 Step 教学文档
├── app.py                          # 早期 Streamlit 兼容入口
├── pyproject.toml
└── uv.lock
```

## 早期 Streamlit 入口

如需运行保留的旧版 Web 应用：

```powershell
Copy-Item .env.example .env
# 按 .env.example 填写旧入口使用的 OPENAI_* 等变量
uv run streamlit run app.py
```

旧入口默认使用 `data/chatbot.db`；主线 dev SQLite 使用 `data/dev/sqlite/app.db`，两者互不覆盖。

## 文档与版本里程碑

- [需求说明](docs/需求说明文档.md)
- [实施步骤计划](docs/实施步骤计划.md)
- [系统架构](docs/architecture.md)
- [实施与验收状态](docs/implementation-status.md)
- [需求变更与扩展登记](docs/需求变更与扩展登记.md)
- `docs/Step1-...` 至 `docs/Step9-...`：对应阶段的历史教学手册，代码片段保留当时状态

Git 已建立 `step-1-init` 至 `step-15-envs` 共 15 个里程碑标签，可按标签查看每一步快照。

## 当前限制与扩展点

- MySQL 真实连通性依赖外部服务，当前本地验收使用构造模拟。
- WebUI、多模型并行对比、图文、语音和 Tool Calling 已在 `AbstractUI` 中预留接口，尚未实现。
- `requirements.txt` 仅为旧入口兼容文件；主线依赖以 `pyproject.toml` 和 `uv.lock` 为准。
