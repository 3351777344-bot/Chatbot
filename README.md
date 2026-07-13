# langchain-chat

`langchain-chat` 是一个基于 LangChain 的课程实践聊天机器人项目。仓库保留了已有的
Streamlit 聊天界面、多轮会话与 SQLite 持久化功能。目前已完成 Step 2：在 `src/` 下新增
分层数据模型、异步 SQLite 存储、配置管理和可交互 TUI；Step 4 已支持创建、列出、切换
和安全删除用户，并支持内置及用户私有 Prompt 预设的选择与管理。原有 Web 应用仍可独立运行。

Step 7 已将无状态 ChatEngine、会话历史与 TUI 对话视图打通：每轮消息自动保存，历史会
自动注入上下文，终端逐段显示回复并累计 Token 用量。

Step 10 起可从会话菜单导出 Markdown；对话中使用 `/model 模型名` 切换当前会话模型，
使用 `/export` 导出当前会话。设置菜单可修改当前用户后续新会话的默认模型。

## 项目特性

- 基于 LangChain 调用 OpenAI-compatible 大模型接口
- Streamlit 可视化聊天界面与流式回复
- 多轮对话、模型切换和预设角色 Prompt
- SQLite 会话历史持久化与多用户数据隔离
- 历史会话切换、自动标题和手动重命名
- uv 统一管理 Python 版本约束、虚拟环境和依赖锁定
- 环境变量、业务配置、Prompt 数据和日志配置分层管理

## 技术栈

- Python `>=3.10,<3.13`
- uv
- LangChain、langchain-openai
- Streamlit
- SQLite（Python 标准库）
- YAML 配置文件

## 目录结构

```text
Chatbot/
├── app.py                         # 已有 Streamlit 聊天应用入口
├── pyproject.toml                 # 项目元数据、依赖与工具配置
├── uv.lock                        # uv 生成的依赖锁文件
├── requirements.txt               # 保留的原依赖清单（兼容旧流程）
├── config.yaml                    # 全局业务配置与扩展点
├── config/
│   ├── settings.py                # 已有聊天应用环境变量配置
│   ├── presets.yaml               # Step 1 内置 Prompt 预设
│   └── logging.yaml               # 日志配置
├── database/                      # 已有 SQLite 数据访问代码
├── prompts/                       # 已有聊天 Prompt 代码
├── services/                      # 已有聊天与模型服务
├── utils/                         # 已有工具代码
├── src/
│   ├── __init__.py
│   ├── core/                      # 配置与核心业务层
│   ├── interface/                 # UI 抽象接口
│   ├── models/                    # Pydantic 数据模型
│   ├── storage/                   # 可插拔存储接口
│   ├── ui/tui/                    # Rich 终端界面
│   └── main.py                    # TUI 程序入口
├── docs/
│   ├── Step1-项目初始化教学文档.md
│   └── 需求变更与扩展登记.md
├── .env.example                   # 可提交的环境变量模板
└── .gitignore
```

`data/`、`logs/`、`.env` 与 `.venv/` 均为本地运行产物，不应提交到 Git。

## 快速开始

安装 [uv](https://docs.astral.sh/uv/) 后，在项目根目录执行：

```powershell
uv sync
uv run python src/main.py
```

入口会加载 `.env` 与 `config.yaml`，随后显示 Step 2 主菜单。选择“退出”可安全结束程序。

启动已有聊天应用：

```powershell
Copy-Item .env.example .env
# 编辑 .env，填入你自己的 API Key；不要提交该文件
uv run streamlit run app.py
```

Streamlit 默认会提供本地访问地址，通常为 `http://localhost:8501`。

## 配置说明

- `.env`：本地敏感信息，只在本机保存；从 `.env.example` 复制后填写真实值。
- `.env.example`：无真实密钥的变量模板，可提交到 Git。
- `config.yaml`：项目名、模型、存储、LLM、会话标题和导出等全局业务配置。
- `config/presets.yaml`：系统内置 Prompt 预设数据。
- `config/logging.yaml`：控制台、滚动文件和第三方库日志级别。
- `config/settings.py`：现有 chatbot 代码当前使用的环境变量加载逻辑，Step 1 保持不变。

多环境覆盖机制只以注释和需求登记形式预留，当前阶段不加载
`config.dev.yaml`、`config.test.yaml` 或 `config.prod.yaml`。

## 开发步骤

1. 执行 `uv sync` 创建或同步项目虚拟环境。
2. 复制 `.env.example` 为 `.env`，仅在需要调用模型时填写真实密钥。
3. 执行 `uv run python src/main.py` 验证 Step 2 TUI 主菜单。
4. 执行 `uv run streamlit run app.py` 验证原有聊天功能。
5. 修改后运行 `git status`，确认 `.env`、`.venv/`、`data/` 和 `logs/` 未进入提交。

`pyproject.toml` 已保留 pytest 与 Ruff 的工具配置；对应开发依赖可在后续测试阶段按需加入，
Step 1 不额外安装它们。

## 文档列表

- [Step 1 项目初始化教学文档](docs/Step1-项目初始化教学文档.md)
- [需求变更与扩展登记](docs/需求变更与扩展登记.md)

## 依赖说明

原项目的 `streamlit`、`langchain`、`langchain-openai` 和 `python-dotenv` 均为现有聊天功能
所需，因此全部保留并同步到 `pyproject.toml`。`requirements.txt` 暂时保留，避免破坏已有安装
流程；后续依赖变更以 `pyproject.toml` 和 `uv.lock` 为准。
