# LLM Chat-bot

这是一个适合课程项目展示的本地 LLM Chat-bot。项目使用 Python、LangChain、Streamlit 和 SQLite，实现多轮会话、多模型切换、流式输出、多用户会话隔离、历史会话管理和预设角色 Prompt。

当前项目已迁移到：

```text
E:\2026暑期实训\Chatbot
```

如果你的实际目录在 D 盘，只需要把下面命令中的 `E:` 改成 `D:` 即可。项目代码使用相对路径读取配置和数据库，移动文件夹后不需要修改 Python 代码。

## 功能亮点

- LangChain 调用 OpenAI 或 OpenAI-compatible 大模型接口
- Streamlit 可视化聊天界面
- 多轮会话，上下文自动传入模型
- 支持在会话开始前或会话中切换模型
- 支持普通助手、代码助手、学习导师、论文润色助手等预设角色
- AI 回复流式输出
- SQLite 本地保存用户、会话和消息
- 使用简单用户名区分用户，不同用户只能看到自己的会话
- 支持历史会话查看、切换、自动生成标题和手动重命名
- 没有 API Key 时应用仍可启动，发送消息时会给出友好提示

## 项目结构

```text
Chatbot/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── services/
│   ├── __init__.py
│   ├── chat_service.py
│   ├── llm_service.py
│   └── title_service.py
├── prompts/
│   ├── __init__.py
│   └── preset_prompts.py
├── utils/
│   ├── __init__.py
│   └── logger.py
└── data/
    └── chatbot.db
```

## 安装依赖

建议使用 Python 3.10 或更高版本。

Windows PowerShell：

```powershell
Set-Location "E:\2026暑期实训\Chatbot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux：

```bash
cd /path/to/Chatbot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置环境变量

复制示例配置文件：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`：

```env
OPENAI_API_KEY=你的_API_KEY
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4o-mini
```

也可以使用 DeepSeek、通义千问等兼容 OpenAI 格式的接口，填写对应的 `*_API_KEY` 和 `*_BASE_URL`。

## 启动项目

```powershell
streamlit run app.py
```

启动后打开 Streamlit 给出的本地地址，一般是：

```text
http://localhost:8501
```

## 使用方式

1. 在左侧输入用户名，例如 `alice`。
2. 选择模型和角色。
3. 点击 `New conversation` 新建会话，或从历史列表切换会话。
4. 在主聊天区输入问题，AI 会流式返回回答。
5. 左侧可以修改当前会话标题。
6. 换一个用户名，例如 `bob`，可以看到不同用户的历史会话互相隔离。

## 数据库设计

SQLite 数据库默认保存到：

```text
data/chatbot.db
```

包含三张表：

- `users`：保存用户名
- `conversations`：保存会话标题、模型、角色和所属用户
- `messages`：保存每条用户消息和 AI 回复

## 测试方法

基础语法检查：

```powershell
python -m compileall -f .
```

数据库初始化检查：

```powershell
python -c "from database.db import init_db; init_db(); print('database ok')"
```

无 API Key 演示：

1. 不填写 `.env` 中的 API Key。
2. 运行 `streamlit run app.py`。
3. 发送一条消息，页面会提示需要配置 API Key。

完整模型调用演示：

1. 在 `.env` 中填写有效 API Key。
2. 运行 `streamlit run app.py`。
3. 新建会话，连续提问两轮。
4. 中途切换模型或角色，再继续提问，确认历史上下文仍然保留。

## 课程展示建议

展示时可以按以下顺序说明：

1. 先展示项目结构，说明没有把所有逻辑写在一个文件里。
2. 输入用户名 `alice`，新建会话并连续提问，展示多轮会话。
3. 切换模型或角色，继续追问，展示配置切换。
4. 修改会话标题并切换历史会话，展示 SQLite 本地保存。
5. 切换到用户名 `bob`，展示多用户会话隔离。

## 迁移说明

本项目的关键路径都基于 `config/settings.py` 中的 `BASE_DIR` 自动计算：

- `.env` 默认读取项目根目录下的 `.env`
- SQLite 默认保存到项目根目录下的 `data/chatbot.db`
- 因此从 C 盘迁移到 `E:\2026暑期实训\Chatbot` 后，无需修改数据库路径或配置读取逻辑
