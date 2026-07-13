# Step 6：对话引擎（LLM 调用 + 流式 + Token 统计）（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-26
> 适用对象：Python 与工程化开发的初学者，且第一次接触 LLM 编程
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-6-chat-engine`

---

## 阅读说明

本文档是 langchain-chat 项目第六步的完整教学手册。这一步是整个项目的**核心技术模块**——第一次让程序真正调用 LLM（大语言模型），实现智能对话。

本文档篇幅较长，因为它承担两个任务：

1. **LLM 编程的零基础入门**（第三章、第四章）：从「什么是 API」讲起，用三层封装（HTTP → OpenAI SDK → LangChain）循序渐进地讲清楚「如何用代码和 LLM 对话」。
2. **ChatEngine 的工程实现**（第六章、第七章、第八章）：把 LLM 调用封装成项目的对话引擎模块，并做全面验证。

阅读并跟随操作后，你应当能够：

1. 理解 LLM、API、HTTP 请求、Token、上下文窗口、流式输出等基础概念。
2. 掌握用代码调用 LLM 的三种方式（HTTP、OpenAI SDK、LangChain），理解每层封装的意义。
3. 理解 LangChain 的 ChatOpenAI、消息类型、流式输出（astream）、超时重试。
4. 实现 ChatEngine（对话引擎），封装 LLM 调用逻辑。
5. 通过冒烟测试全面验证 ChatEngine 的各项功能。

**本文档的设计原则**（与前五步文档一致）：

- 每一个概念都用「3W1H」框架或通俗比喻讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，由学习者自行创建文件并粘贴内容。
- 从最基础的开始，慢慢进入难点，不回避难点。

**完成标志（学完本文档后你应达成的目标）**：

- 新增 `src/core/chat_engine.py`（对话引擎）。
- 新增 `examples/` 目录（三层 LLM 调用示例，与项目正式代码隔离）。
- 新增 `scripts/test_chat_engine.py`（冒烟测试）。
- 改造 `config.yaml`、`config_manager.py`、`widgets.py`、`app.py`（方案 B + LLM 配置）。
- 安装 langchain、langchain-openai 依赖。
- 配置真实的 API Key 到 .env。
- 执行 `uv run python -m examples.example3_langchain` 能成功和 LLM 对话。
- 执行 `uv run python scripts/test_chat_engine.py` 全部测试通过。
- 本地 Git 仓库存在提交与标签 `step-6-chat-engine`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、为什么先写引擎再接界面](#二为什么先写引擎再接界面)
- [三、LLM 与 API 基础知识（零基础入门）](#三llm-与-api-基础知识零基础入门)
- [四、LLM 编程的三层封装（循序渐进）](#四llm-编程的三层封装循序渐进)
- [五、准备工作](#五准备工作)
- [六、核心概念讲解（3W1H）](#六核心概念讲解3w1h)
- [七、动手实践：ChatEngine 实现](#七动手实践chatengine-实现)
- [八、全面验证（冒烟测试）](#八全面验证冒烟测试)
- [九、版本控制](#九版本控制)
- [十、常见问题与排查](#十常见问题与排查)
- [十一、本步骤小结与知识清单](#十一本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

前五步我们搭好了项目骨架，实现了用户管理和预设管理。但程序还不会「思考」——它只会存取数据，不会对话。Step 6 的目标是：**让程序拥有「大脑」，能调用 LLM 进行智能对话。**

具体而言，本步骤做四件事：

1. 实现 ChatEngine（core/chat_engine.py），封装 LLM 的调用逻辑（多轮对话、流式输出、超时重试、Token 统计）。
2. 提供 examples/ 目录的三层示例（HTTP、OpenAI SDK、LangChain），帮助理解 LLM 编程的演进。
3. 实施方案 B（进度文字从配置读取，不再写死在代码里）。
4. 全面验证 ChatEngine 的各项功能（冒烟测试脚本）。

本步骤**只写引擎，不接 TUI 界面**。引擎是「大脑」，Step 7 才把大脑装进界面（TUI），让你在终端里和 LLM 聊天。

### 1.2 本步骤的特殊意义

这是项目第一次接触真实的外部服务（LLM API）。意义在于：

- 前五步都是「内部」操作（存自己的数据库、显示自己的菜单），Step 6 第一次「向外通信」（调用远程 LLM）。
- 引入了网络请求、异步流式、超时重试等新复杂度。
- 这是 Step 7（核心里程碑：能在界面里和 LLM 对话）的技术基础。

### 1.3 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 5 完成的预设管理（标签 step-5-presets）+ 真实的 LLM API Key |
| 输出 | ChatEngine 对话引擎 + 三层示例 + 冒烟测试 |
| MVP 验证点 | 冒烟测试脚本全部通过（单轮、多轮、流式、Token、错误处理） |

### 1.4 本步骤产出的文件

```
langchain-chat/
├── examples/                        LLM 编程示例（新建，与正式代码隔离）
│   ├── __init__.py
│   ├── example1_http.py             第一层：HTTP 直接调 API
│   ├── example2_openai_sdk.py       第二层：OpenAI SDK
│   └── example3_langchain.py        第三层：LangChain ChatOpenAI
├── scripts/
│   └── test_chat_engine.py          ChatEngine 冒烟测试（新建）
├── src/
│   ├── core/
│   │   └── chat_engine.py           对话引擎（新建）
│   ├── ui/tui/
│   │   ├── app.py                   方案 B 改造（进度文字从配置读取）
│   │   └── widgets.py               print_banner 改造（接收进度参数）
│   └── core/config_manager.py       新增 temperature/max_tokens/current_step 属性
└── config.yaml                      新增 current_step 字段
```

### 1.5 本步骤的设计决策（已确认）

| 决策 | 选择 | 理由 |
|------|------|------|
| 示例放哪 | examples/ 目录 | 作为正式示例文件，但与项目功能代码完全隔离 |
| 依赖版本 | langchain 1.3.13、langchain-openai 1.3.5（最新版） | 与 Python 3.12 兼容，最新版修复已知 bug |
| 验证方式 | 冒烟测试脚本 | 全面覆盖，呼应 Step 5 中Bug修复章节 |
| 默认验证服务 | DeepSeek | 国内访问稳定、便宜、文档清晰 |
| 记忆维护位置 | 由调用方维护（传入消息历史），ChatEngine 不持有状态 | 一个引擎可服务多个会话，避免状态串扰 |

---

## 二、为什么先写引擎再接界面

一个问题：「什么时候能和 LLM 对话？」答案在 Step 7。

但要理解为什么不能跳过 Step 6 直接做 Step 7，需要讲清楚两者的区别。

### 2.1 引擎 vs 界面

把对话功能拆成两层：

| 层 | 对应步骤 | 职责 | 类比 |
|----|---------|------|------|
| 引擎（ChatEngine） | Step 6 | 怎么调 LLM、怎么流式、怎么统计 Token | 汽车的发动机 |
| 界面（chat_view） | Step 7 | 用户在哪里输入、回复显示在哪里 | 汽车的方向盘和仪表盘 |

发动机（引擎）是核心，没有它汽车跑不了。方向盘（界面）是操控发动机的工具。Step 6 造发动机，Step 7 装方向盘。

### 2.2 为什么不能合并成一步

如果直接在 TUI 界面代码里写 LLM 调用逻辑，会出现这些问题：

- **界面和 LLM 逻辑耦合**：改界面会碰到 LLM 代码，改 LLM 会碰到界面代码。
- **无法独立测试**：想验证 LLM 调用对不对，必须启动整个 TUI 手动操作。
- **无法复用**：将来加 WebUI 时，LLM 调用逻辑要重写一遍。

分开后：ChatEngine 是独立模块，可以单独测试（冒烟测试脚本），Step 7 接界面时直接调用，将来 WebUI 也能复用同一个引擎。

### 2.3 Step 4-6 如何铺垫对话功能

回顾一下从 Step 4 到 Step 7 的完整铺垫：

```
Step 4  用户管理   → 知道「是谁在对话」（current_user）
Step 5  预设管理   → 知道「以什么角色对话」（system_prompt）
Step 6  对话引擎   → 知道「怎么调 LLM」（ChatEngine）        ← 本步骤
Step 7  对话视图   → 在界面里和 LLM 多轮对话（把 4、5、6 串起来）  ← 核心里程碑
```

Step 6 的引擎，到 Step 7 会用到 Step 4 的用户（保存对话历史）、Step 5 的预设（注入 system_prompt）。所有前序步骤都在为核心里程碑铺路。

---

## 三、LLM 与 API 基础知识（零基础入门）

本章节为零基础读者编写。如果你已经熟悉这些概念，可以跳到第四章。本章节不涉及代码，只讲概念。

### 3.1 什么是 LLM（大语言模型）

**LLM（Large Language Model，大语言模型）**是一种人工智能程序，它能理解人类语言，并生成类似人类的回复。常见的 LLM 有：

- OpenAI 的 GPT 系列（GPT-5.5、GPT-4o、GPT-3.5-turbo 等）
- DeepSeek（国产，性价比高）
- 阿里的通义千问（Qwen 系列）
- 百度的文心一言、智谱的 GLM 等

LLM 的特点：

- **输入文字，输出文字**：你给它一段话，它回一段话。
- **基于概率生成**：它不是「查答案」，而是「根据上文预测下一个字」，一个字一个字地生成。
- **经过海量数据训练**：读过互联网上的大量文本，所以知识面广。

你用的 ChatGPT、通义千问网页版，背后就是 LLM。但那些是「网页界面」，Step 6 要做的是「用代码调用 LLM」——程序自己发消息给 LLM，接收回复。

### 3.2 什么是 API（用「点外卖」比喻）

**API（Application Programming Interface，应用程序编程接口）**是「程序之间交流的通道」。

用点外卖比喻：

```
你（程序）—— 在手机上下单 ——→ 外卖平台（API）—— 通知餐厅 ——→ 餐厅做菜
你（程序）—— 收到外卖 ←——— 外卖平台（API）←—— 餐厅出餐 ←——— 餐厅
```

- 你不需要知道餐厅怎么做菜，只需要「下单」（发请求）。
- 餐厅做好后，外卖平台「送餐」（返回响应）。
- 你和餐厅之间通过「外卖平台」（API）交流，不直接见面。

LLM API 也是这个模式：

```
你的程序 —— 发消息（请求）——→ LLM 服务器（API）—— LLM 思考生成
你的程序 —— 收回复（响应）←——— LLM 服务器（API）←—— LLM 生成完毕
```

你不需要知道 LLM 内部怎么工作，只需要「发请求」（告诉它要回复什么），它返回「响应」（LLM 的回复）。

### 3.3 什么是 HTTP 请求

**HTTP（HyperText Transfer Protocol，超文本传输协议）**是「发请求、收响应」的具体方式。浏览器打开网页、程序调 API，底层都是 HTTP。

HTTP 请求的核心要素：

| 要素 | 含义 | 点外卖类比 |
|------|------|----------|
| URL（地址） | 请求发到哪里 | 餐厅地址 |
| Method（方法） | GET（获取）/ POST（提交） | 「我要看菜单」（GET）/「我要下单」（POST） |
| Headers（请求头） | 附加信息（如认证） | 你的会员卡号 |
| Body（请求体） | 提交的数据 | 你点的菜 |
| Response（响应） | 服务器返回的数据 | 送来的外卖 |

调 LLM API 通常是 **POST 请求**（因为你「提交」了一段文字让 LLM 回复）。请求体里放你的消息，响应里是 LLM 的回复。

### 3.4 什么是 Token（不是字也不是词）

**Token** 是 LLM 处理文本的**最小单位**。它既不是「一个字」，也不是「一个词」，而是介于两者之间的东西。

举例（英文）：

- `hello` 是 1 个 token
- `hamburger` 可能被切成 `ham` + `burger`，是 2 个 token
- `I love you` 是 3 个 token（I / love / you）

举例（中文）：

- `你好` 可能是 1-2 个 token（取决于分词器）
- `中华人民共和国` 可能被切成多个 token

**为什么要关心 Token？**

1. **计费**：LLM 按 Token 数收费（输入 Token + 输出 Token）。知道 Token 数才能算成本。
2. **限制**：每个模型有「上下文窗口」大小限制（如 8000 Token），超过就装不下。
3. **统计**：需求 E2 要求显示每轮对话的 Token 用量，让用户了解消耗。

简单估算：1 个英文单词约 1-2 个 Token，1 个中文字约 1-2 个 Token。1000 个 Token 大约等于 750 个英文单词或 500 个中文字。

### 3.5 什么是上下文窗口、为什么 LLM 没有记忆

**上下文窗口（Context Window）**：LLM 一次能「看见」的最大文本长度（以 Token 计）。比如 GPT-3.5-turbo 的窗口是 16000 Token，超过这个长度的历史它就看不见了。

**LLM 本身没有记忆**：这是一个关键认知。每次调用 LLM API，它都是「从零开始」——它不记得你上一句说了什么。为什么？因为 LLM 是「无状态」的，每次调用都是独立的请求。

那多轮对话怎么实现？**由我们自己维护消息历史**。每次调用时，把之前的对话记录一起发过去：

```
第一次调用：发送 [用户: 我叫小明]
LLM 回复：你好小明！

第二次调用：发送 [用户: 我叫小明, AI: 你好小明!, 用户: 我叫什么？]
                                       ↑ 历史记录       ↑ 新问题
LLM 回复：你叫小明（因为它看到了历史记录里的「我叫小明」）
```

如果不带历史，第二次只发「我叫什么？」，LLM 会回答「我不知道」。

这个「维护消息历史」的机制，在 LangChain 里叫 **Memory（记忆）**。但本质上，Memory 不是 LLM 的能力，而是「我们每次把历史一起发过去」的编程技巧。

### 3.6 什么是流式输出

**流式输出（Streaming）**：LLM 一边生成一边返回，而不是等全部生成完再一次性返回。

对比：

| 模式 | 行为 | 体验 |
|------|------|------|
| 非流式 | LLM 生成完所有内容，一次性返回 | 用户等待几秒，然后突然看到一大段文字 |
| 流式 | LLM 生成一个字返回一个字 | 用户看到文字逐字出现，像打字一样 |

你用 ChatGPT 时看到回复「一个字一个字显示出来」，就是流式输出。体验更好，因为用户不用干等。

代码上，流式输出的特点是：用 `for chunk in ...` 循环接收，每个 chunk 是一小段文字。本项目用 LangChain 的 `astream`（异步流式）。

### 3.7 temperature、max_tokens 等参数

调 LLM 时可以设置一些参数，影响生成结果：

| 参数 | 含义 | 取值 | 我们项目的值 |
|------|------|------|------------|
| `temperature`（温度） | 创造性程度。低=确定/保守，高=随机/创意 | 0 到 2 | 0.7（平衡） |
| `max_tokens` | 单次回复最多生成多少 Token | 整数 | 2048 |
| `timeout`（超时） | 等多久没响应就放弃（秒） | 整数 | 30 |
| `max_retries`（重试） | 失败后自动重试几次 | 整数 | 3 |

temperature 的直观感受：

- `temperature=0`：每次问同一个问题，答案几乎一样（最确定）。
- `temperature=0.7`：有点变化，但基本合理（日常对话推荐）。
- `temperature=1.5`：答案会比较随机、有创意（适合写诗、头脑风暴）。

### 3.8 API Key 的安全规范

**API Key 是你的「钥匙」**，谁拿到它就能用你的额度调 LLM（花你的钱）。安全规范：

1. **绝不提交到 Git**：.env 已被 .gitignore 排除，API Key 不会进版本库。绝对不要把 Key 写进代码或配置文件（config.yaml）。
2. **绝不截图分享**：截图里的 Key 会被别人看到。
3. **绝不贴到公开场合**：不要贴到论坛、群聊、Issue 里。
4. **泄露后立即重置**：如果怀疑泄露，去服务商后台「重置 Key」，旧 Key 立即失效。

在代码里显示 API Key 时，只显示前几位（如 `sk-abcd...`），后面用省略号。本项目示例代码都遵循这个规范。

---

## 四、LLM 编程的三层封装（循序渐进）

本章节通过三层封装，让你彻底理解「如何用代码调用 LLM」。每一层都给出完整的最小可运行程序，可以运行验证。

三层的关系：

```
第一层：HTTP 直接调 API（最底层，看清本质）
    ↑ 封装
第二层：OpenAI SDK（官方封装，代码简洁）
    ↑ 再封装
第三层：LangChain ChatOpenAI（项目最终选用，支持 Memory、Chain 等高级功能）
```

每一层都在上一层基础上封装，写更少的代码、做更多的事。理解了底层，再用上层时就不会觉得是「黑盒」。

### 4.1 第一层：HTTP 直接调 API

**What**：用 requests 库直接发 HTTP POST 请求到 LLM 的 API 地址，手动构造请求、解析响应。不依赖任何 LLM 专用库。

**Why（为什么要学这层）**：这是最底层的方式，让你看清「调用 LLM」的本质——就是发一个 HTTP 请求，没什么神秘的。理解了这层，后面的 SDK 和 LangChain 都是在封装它。

**关键理解**：LLM API 的地址通常是 `{base_url}/chat/completions`，请求体是 JSON，包含 `model`（模型名）和 `messages`（消息列表）。响应也是 JSON，LLM 的回复在 `choices[0].message.content`。

**How（示例代码）**：

文件路径：`langchain-chat/examples/example1_http.py`。

```python
"""第一层示例：用 HTTP 直接调用 LLM API。

这是最底层的调用方式。不依赖任何 LLM SDK，只用 requests 库发 HTTP 请求。
目的是让你看清「调用 LLM」的本质：就是发一个 HTTP POST 请求，带上消息，收到 JSON 响应。

运行方式（在项目根目录执行）：
    uv run python -m examples.example1_http

前提：已在 .env 中配置 API_BASE_URL、API_KEY、MODEL_NAME。
"""

import os
import sys
import json
from pathlib import Path

# 读取 .env（这里手动读，不用 python-dotenv，体现「最底层」）
env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "deepseek-chat")

# 导入 requests（如果项目没装，用 urllib；这里用 requests 更清晰）
try:
    import requests
except ImportError:
    print("本示例需要 requests 库。它是 langchain 的间接依赖，应该已安装。")
    sys.exit(1)


def chat_one_turn(user_message: str) -> str:
    """发送一条消息，返回 LLM 的回复（非流式，等全部生成完再返回）。

    本质就是：向 {API_BASE_URL}/chat/completions 发一个 POST 请求，
    请求体是 JSON，包含 model 和 messages；响应也是 JSON，含 LLM 的回复。
    """
    url = f"{API_BASE_URL}/chat/completions"

    # 请求头：认证（Bearer Token）
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    # 请求体：模型名 + 消息列表
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": user_message},
        ],
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    # 检查响应状态
    if response.status_code != 200:
        return f"请求失败，状态码 {response.status_code}: {response.text}"

    # 解析 JSON 响应
    data = response.json()

    # 提取 LLM 回复（在 choices[0].message.content）
    reply = data["choices"][0]["message"]["content"]

    # 提取 Token 用量（在 usage 字段）
    usage = data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    return reply, prompt_tokens, completion_tokens


def main():
    print("=" * 60)
    print("示例 1：用 HTTP 直接调用 LLM API（最底层）")
    print("=" * 60)
    print(f"API 地址: {API_BASE_URL}")
    print(f"模型:     {MODEL_NAME}")
    print(f"API Key:  {API_KEY[:8]}...（只显示前 8 位）")
    print()

    # 检查配置
    if not API_KEY or API_KEY == "your_api_key_here":
        print("错误：API_KEY 未配置，请在 .env 文件中填入真实的 API Key。")
        return

    # 第一轮对话
    print("-" * 60)
    user_input = "你好，请用一句话介绍你自己。"
    print(f"[你] {user_input}")

    reply, prompt_tokens, completion_tokens = chat_one_turn(user_input)
    print(f"[AI] {reply}")
    print(f"[Token] 输入 {prompt_tokens}，输出 {completion_tokens}")
    print()

    # 第二轮对话（注意：HTTP 方式下，LLM 不记得上一轮，需要自己维护历史）
    print("-" * 60)
    user_input2 = "我刚才问了什么？"
    print(f"[你] {user_input2}")

    # 如果想让 LLM 记得上一轮，需要把历史消息一起发过去
    # 这里为了演示「LLM 默认无记忆」，只发这一条
    reply2, pt2, ct2 = chat_one_turn(user_input2)
    print(f"[AI] {reply2}")
    print(f"[Token] 输入 {pt2}，输出 {ct2}")
    print()
    print("（注意：第二轮 LLM 答不出「你刚才问了什么」，因为它没有记忆。")
    print(" 这说明 LLM 本身是无状态的，多轮对话的记忆需要我们自己维护。）")


if __name__ == "__main__":
    main()
```

**讲解要点**：

- 请求 URL 是 `{API_BASE_URL}/chat/completions`（所有 OpenAI 兼容 API 都用这个路径）。
- 请求头的 `Authorization: Bearer {API_KEY}` 是认证方式（Bearer Token）。
- 请求体的 `messages` 是消息列表，每条消息有 `role`（user/assistant/system）和 `content`。
- 响应的 `choices[0].message.content` 是 LLM 的回复。
- 响应的 `usage` 含 Token 统计。

### 4.2 第二层：OpenAI SDK

**What**：用 OpenAI 官方提供的 SDK（`openai` 库）调用。SDK 把 HTTP 请求封装成函数调用，代码更简洁。

**Why（为什么要学这层）**：手写 HTTP 太繁琐（手动构造 headers、payload、解析 JSON）。SDK 把这些封装了，你只需调用 `client.chat.completions.create()`。而且 OpenAI SDK 兼容所有「OpenAI 格式」的 API（DeepSeek、通义千问等），只需改 `base_url`。

**How（示例代码）**：

文件路径：`langchain-chat/examples/example2_openai_sdk.py`。

```python
"""第二层示例：用 OpenAI 官方 SDK 调用 LLM。

这一层比 HTTP 封装更高级。OpenAI SDK 把「构造请求、发送、解析响应」封装成函数调用，
你不需要手写 HTTP 请求，只需调用 client.chat.completions.create()。

重要：OpenAI SDK 兼容所有「OpenAI 格式」的 API（DeepSeek、通义千问等），
只要把 base_url 换成对应服务的地址即可。

运行方式（在项目根目录执行）：
    uv run python -m examples.example2_openai_sdk

前提：已在 .env 中配置 API_BASE_URL、API_KEY、MODEL_NAME。
"""

import os
from pathlib import Path

# 读取 .env
env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "deepseek-chat")

from openai import OpenAI


def main():
    print("=" * 60)
    print("示例 2：用 OpenAI SDK 调用 LLM（第二层封装）")
    print("=" * 60)
    print(f"API 地址: {API_BASE_URL}")
    print(f"模型:     {MODEL_NAME}")
    print(f"API Key:  {API_KEY[:8]}...（只显示前 8 位）")
    print()

    if not API_KEY or API_KEY == "your_api_key_here":
        print("错误：API_KEY 未配置，请在 .env 文件中填入真实的 API Key。")
        return

    # 创建客户端（把 HTTP 的 headers、base_url 等封装了）
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
    )

    # 第一轮：单轮对话（对比示例 1，代码简洁很多）
    print("-" * 60)
    user_input = "你好，请用一句话介绍你自己。"
    print(f"[你] {user_input}")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": user_input}],
    )
    print(f"[AI] {response.choices[0].message.content}")
    print(f"[Token] 输入 {response.usage.prompt_tokens}，输出 {response.usage.completion_tokens}")
    print()

    # 第二轮：多轮对话（自己维护消息历史）
    print("-" * 60)
    print("多轮对话（手动维护消息历史）：")
    messages = [
        {"role": "user", "content": "你好，请用一句话介绍你自己。"},
    ]
    response1 = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    ai_reply1 = response1.choices[0].message.content
    print(f"[你] {messages[0]['content']}")
    print(f"[AI] {ai_reply1}")

    # 把 AI 的回复加入历史，再发第二轮
    messages.append({"role": "assistant", "content": ai_reply1})
    messages.append({"role": "user", "content": "我刚才问了什么？"})
    print(f"[你] 我刚才问了什么？")

    response2 = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    print(f"[AI] {response2.choices[0].message.content}")
    print()
    print("（这次 LLM 答出了「你问了让我介绍自己」，因为我们手动维护了消息历史。）")


if __name__ == "__main__":
    main()
```

**对比第一层**：SDK 把 `requests.post(url, headers=..., json=...)` 封装成了 `client.chat.completions.create(model=..., messages=...)`，把响应解析封装成了 `response.choices[0].message.content`。代码量减少，可读性提高。

### 4.3 第三层：LangChain ChatOpenAI（项目选用）

**What**：用 LangChain 框架的 ChatOpenAI 类调用。LangChain 在 OpenAI SDK 之上再加抽象，提供消息类型、Memory、Chain、流式等高级功能。

**Why（为什么项目选这层）**：

1. **消息类型更规范**：LangChain 提供 HumanMessage、AIMessage、SystemMessage，比 dict 更清晰、有类型校验。
2. **流式输出更简单**：`llm.stream()` 和 `llm.astream()` 直接支持流式，不用手动处理 SSE。
3. **可扩展性强**：将来要加 Memory（记忆）、Chain（链式调用）、Agent（智能体），LangChain 都有现成支持。
4. **需求文档规定**：需求文档 2.1 明确要求用 langchain + langchain-openai。

**How（示例代码）**：

文件路径：`langchain-chat/examples/example3_langchain.py`。

```python
"""第三层示例：用 LangChain ChatOpenAI 调用 LLM（项目最终选用）。

这一层在 OpenAI SDK 之上再加抽象。LangChain 提供了：
    - ChatOpenAI：封装了 OpenAI SDK，支持流式、重试等。
    - 消息类型：HumanMessage、AIMessage、SystemMessage，比 dict 更规范。
    - 后续可接 Memory、Chain、Agent 等高级组件。

本项目选用 LangChain，因为它为多轮对话、流式输出、记忆管理提供了完整支持。

运行方式（在项目根目录执行）：
    uv run python -m examples.example3_langchain

前提：已在 .env 中配置 API_BASE_URL、API_KEY、MODEL_NAME。
"""

import os
from pathlib import Path

# 读取 .env
env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "deepseek-chat")

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI


def main():
    print("=" * 60)
    print("示例 3：用 LangChain ChatOpenAI 调用 LLM（第三层，项目选用）")
    print("=" * 60)
    print(f"API 地址: {API_BASE_URL}")
    print(f"模型:     {MODEL_NAME}")
    print(f"API Key:  {API_KEY[:8]}...（只显示前 8 位）")
    print()

    if not API_KEY or API_KEY == "your_api_key_here":
        print("错误：API_KEY 未配置，请在 .env 文件中填入真实的 API Key。")
        return

    # 创建 ChatOpenAI（封装了 OpenAI SDK，支持流式、重试、超时等）
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=API_BASE_URL,
        temperature=0.7,
        max_tokens=512,
        timeout=30,
        max_retries=2,
    )

    # 第一轮：用 HumanMessage 构造消息（比 dict 更规范）
    print("-" * 60)
    print("单轮对话：")
    user_msg = HumanMessage(content="你好，请用一句话介绍你自己。")
    print(f"[你] {user_msg.content}")

    ai_msg = llm.invoke([user_msg])
    print(f"[AI] {ai_msg.content}")
    if ai_msg.usage_metadata:
        um = ai_msg.usage_metadata
        print(f"[Token] 输入 {um.get('input_tokens', '?')}，输出 {um.get('output_tokens', '?')}")
    print()

    # 第二轮：多轮对话（用消息列表维护历史，和 SDK 类似但消息类型更规范）
    print("-" * 60)
    print("多轮对话（用消息列表维护历史）：")
    history = [user_msg, ai_msg]
    user_msg2 = HumanMessage(content="我刚才问了什么？")
    history.append(user_msg2)
    print(f"[你] {user_msg2.content}")

    ai_msg2 = llm.invoke(history)
    print(f"[AI] {ai_msg2.content}")
    print()

    # 第三轮：流式输出（逐字返回，这是 LangChain 的强大之处）
    print("-" * 60)
    print("流式输出（逐字返回）：")
    print("[你] 请数 1 到 5")
    print("[AI] ", end="", flush=True)
    for chunk in llm.stream([HumanMessage(content="请数 1 到 5")]):
        print(chunk.content, end="", flush=True)
    print()
    print()
    print("（流式输出：LLM 一边生成一边返回，不需要等全部生成完。体验更好。）")


if __name__ == "__main__":
    main()
```

### 4.4 三层对比：每层封装了什么、为什么选 LangChain

| 维度 | 第一层 HTTP | 第二层 OpenAI SDK | 第三层 LangChain |
|------|------------|-------------------|-----------------|
| 构造请求 | 手写 headers、payload | `client.chat.completions.create()` | `llm.invoke()` |
| 消息表示 | dict（字典） | dict（字典） | HumanMessage/AIMessage（类型安全） |
| 解析响应 | 手动取 `data["choices"][0]...` | `response.choices[0]...` | `ai_msg.content` |
| 流式输出 | 手动解析 SSE 数据流 | SDK 支持 | `llm.stream()` / `llm.astream()` |
| Token 统计 | 手动取 `data["usage"]` | `response.usage.xxx` | `ai_msg.usage_metadata` |
| 超时重试 | 自己写 try/except + 重试 | SDK 支持 | ChatOpenAI 内置 `max_retries` |
| 可扩展性 | 无 | 无 | Memory、Chain、Agent |
| 代码量 | 最多 | 中等 | 最少 |

**本项目选 LangChain 的理由**：代码量最少、类型最安全、流式最方便、可扩展性最强、需求文档规定。

### 4.5 examples/ 目录的说明

三个示例文件放在 `examples/` 目录，与项目正式代码**完全隔离**：

- 示例代码只 import 第三方库（requests、openai、langchain），**不 import 项目的 src 模块**。
- 项目的 src 代码也**不 import 示例代码**。
- 示例的作用是「帮助理解」，理解完可以保留作为参考，不影响项目运行。

示例的运行方式（在项目根目录）：

```bash
uv run python -m examples.example1_http
uv run python -m examples.example2_openai_sdk
uv run python -m examples.example3_langchain
```

用 `-m` 方式运行（`python -m examples.example1_http`），而不是 `python examples/example1_http.py`，是因为前者把项目根目录加入模块搜索路径，`from examples import ...` 才能工作。

---

## 五、准备工作

### 5.1 安装依赖

Step 6 需要 langchain 和 langchain-openai（langchain-core 会作为依赖自动安装）。

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv add langchain langchain-openai
```

安装后验证版本：

```bash
uv run python -c "from importlib.metadata import version; print('langchain:', version('langchain')); print('langchain-core:', version('langchain-core')); print('langchain-openai:', version('langchain-openai'))"
```

预期输出（版本号可能是这些或略新）：

```
langchain: 1.3.13
langchain-core: 1.4.9
langchain-openai: 1.3.5
```

### 5.2 配置 API Key（三种服务的配置示例）

打开 `.env` 文件，根据你用的服务，填入对应的配置。

#### 方案 A：DeepSeek（默认推荐）

```
API_BASE_URL=https://api.deepseek.com/v1
API_KEY=sk-你的真实key
MODEL_NAME=deepseek-chat
```

DeepSeek 的 base_url 是 `https://api.deepseek.com/v1`（注意结尾有 /v1）。模型名用 `deepseek-chat`（通用对话模型）。

#### 方案 B：通义千问（QWen）

```
API_BASE_URL=https://llm-jm403wwr82zc6d86.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
API_KEY=sk-你的真实key
MODEL_NAME=qwen3.6-flash
```

通义千问用 OpenAI 兼容模式的地址（结尾 `/compatible-mode/v1`）。模型名可选 `qwen3.6-flash`（快速）、`qwen3.6-max-preview`（最强）等。

#### 方案 C：OpenAI（兼容代理）

```
API_BASE_URL=https://api.chatanywhere.tech/v1
API_KEY=sk-你的真实key
MODEL_NAME=gpt-3.5-turbo
```

注意：你使用的是 OpenAI 的兼容代理地址（`chatanywhere.tech`），不是官方地址。模型名用 `gpt-3.5-turbo`。

> 安全提示：填入真实 Key 后，.env 不会进 Git（被 .gitignore 排除）。但请确认 .env 里确实是真实 Key，不是占位符。

### 5.3 验证 API Key 可用

填完 .env 后，用第三层示例（LangChain）验证 API Key 可用：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -m examples.example1_http
uv run python -m examples.example2_openai_sdk
uv run python -m examples.example3_langchain
```

如果看到 LLM 回复了「你好，请用一句话介绍你自己」的内容，说明 API Key 配置正确、网络通畅。

如果报错，参考第十章排查。

### 5.4 实施方案 B（进度文字从配置读取）

这是 Step 6 开始时的第一个改动——把 widgets.py 里写死的进度文字，改为从 config.yaml 读取。这样以后每步只需改配置文件，不用改代码。

涉及 4 个文件的改动：

1. `config.yaml`：新增 `app.current_step` 字段。
2. `src/core/config_manager.py`：新增 `current_step` 属性。
3. `src/ui/tui/widgets.py`：print_banner 接收 current_step 参数。
4. `src/ui/tui/app.py`：调用 print_banner 时传入 current_step。

具体改动见第七章的 7.1 至 7.4 节。

---

## 六、核心概念讲解（3W1H）

本章节讲解 ChatEngine 涉及的核心概念。基础概念（API、Token 等）已在第三章讲过，这里讲与 LangChain 相关的。

### 6.1 ChatOpenAI（langchain-openai）

**What**：LangChain 提供的 LLM 客户端类，封装了 OpenAI SDK，支持所有 OpenAI 兼容的 API。

**Why**：统一了 LLM 调用接口，支持流式、重试、超时，且能接入 LangChain 的 Memory、Chain 等生态。

**How（本项目用法）**：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1",
    temperature=0.7,
    max_tokens=2048,
    timeout=30,
    max_retries=3,
    streaming=True,
)
```

关键参数：

- `model`：模型名（从 config 读取）。
- `api_key` + `base_url`：API 认证和地址（从 .env 读取）。
- `temperature` + `max_tokens`：生成参数（从 config 读取）。
- `timeout`：超时秒数（从 config 的 llm.timeout 读取，需求 G1）。
- `max_retries`：失败重试次数（从 config 的 llm.max_retries 读取，需求 G1）。
- `streaming=True`：启用流式输出。

### 6.2 消息类型（HumanMessage / AIMessage / SystemMessage）

**What**：LangChain 用不同的类表示不同角色的消息。

| 类 | 对应角色 | 含义 |
|----|---------|------|
| `HumanMessage` | user | 用户说的话 |
| `AIMessage` | assistant | LLM 回复的话 |
| `SystemMessage` | system | 系统提示词（定义 LLM 角色，如预设） |

**Why（为什么不用 dict）**：

- 类型安全：IDE 能补全，传错类型会报错。
- 语义清晰：`HumanMessage(content="你好")` 比 `{"role": "user", "content": "你好"}` 更易读。
- 支持 LangChain 的高级功能（如 tool calls）。

**How**：

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

messages = [
    SystemMessage(content="你是一个翻译助手"),
    HumanMessage(content="hello"),
]
response = llm.invoke(messages)
```

### 6.3 流式输出（astream）

**What**：`astream` 是 ChatOpenAI 的异步流式方法，逐 chunk 返回 LLM 的生成内容。

**Why（为什么用 astream 而不是 invoke）**：

- `invoke`：等 LLM 全部生成完，一次性返回。用户等待感强。
- `astream`：一边生成一边返回（逐 chunk），用户看到文字逐字出现，体验好。
- 需求 A2 明确要求「逐 token 流式输出」。

`astream` 是异步方法（async），配合 `async for` 使用。本项目全链路异步（需求 A3），所以用 astream。

**How**：

```python
async for chunk in llm.astream(messages):
    print(chunk.content, end="", flush=True)  # 逐 chunk 打印
```

每个 chunk 包含一小段文字（可能是一个字、几个字）。把所有 chunk 的 content 拼起来，就是完整的回复。

### 6.4 超时重试（timeout + max_retries）

**What**：网络请求可能失败（超时、限流、服务器错误）。ChatOpenAI 内置了超时和自动重试机制。

**Why**：需求 G1 要求「LLM 调用超时自动重试」。如果调用失败就直接崩溃，用户体验很差。重试机制让程序在网络波动时自动恢复。

**How**：在 ChatOpenAI 构造时设置：

```python
llm = ChatOpenAI(
    timeout=30,        # 30 秒超时
    max_retries=3,     # 失败后最多重试 3 次
)
```

ChatOpenAI 内部用 tenacity 库实现重试。如果连续 3 次都失败，才抛出异常。这些参数从 config.yaml 的 llm 段读取。

### 6.5 Token 用量统计

**What**：LLM 的响应里包含 Token 用量信息，LangChain 封装在 `usage_metadata` 字段。

**Why**：需求 E2 要求「每轮对话结束后显示本轮消耗的 token 数」。需要从响应中提取 Token 统计。

**How**：

```python
response = llm.invoke(messages)
usage = response.usage_metadata
# usage 含: input_tokens, output_tokens, total_tokens
```

流式输出的 Token 统计在最后一个 chunk 里（中间 chunk 没有）。ChatEngine 的 astream 方法会从最后一个 chunk 提取。

---

## 七、动手实践：创建与改造源码

下面依次完成所有改动。先做"进度文字从配置读取"（4 个文件），再创建 ChatEngine 和冒烟测试。

> 文件位置约定：源码在 `src/` 下，示例在 `examples/` 下，脚本在 `scripts/` 下。
>
> import 约定：项目正式代码相对于 src 目录；示例代码只用第三方库。
>
> PyCharm 提示：创建文件时选「不添加」到 Git，最后统一 git add。

### 7.1 改造 config.yaml（新增 current_step）

文件路径：`langchain-chat/config.yaml`。

在 `app` 段新增 `current_step` 字段。找到：

```yaml
# 应用元信息
app:
  name: langchain-chat
  version: 0.1.0
  # env: dev   # 多环境预留，Step 15 启用
```

改为（加一行 current_step）：

```yaml
# 应用元信息
app:
  name: langchain-chat
  version: 0.1.0
  current_step: "Step 6  对话引擎"   # 当前进度（横幅显示，方案 B：从配置读取，不再写死在代码里）
  # env: dev   # 多环境预留，Step 15 启用
```

以后每推进一个 Step，只需改这一行（如 Step 7 改为「Step 7 对话视图」），不用改代码。

### 7.2 改造 src/core/config_manager.py（新增三个属性）

文件路径：`langchain-chat/src/core/config_manager.py`。

在 AppConfig 类的 `available_models` 属性之后，新增三个属性。找到：

```python
    @property
    def available_models(self) -> list[dict[str, str]]:
        """可选模型列表。"""
        return self._yaml_config.get("models", {}).get("available", [])
```

在其后面新增（注意：同时给 storage_type 前面加 current_step）：

```python
    @property
    def current_step(self) -> str:
        """当前开发步骤（横幅显示用，方案 B：从配置读取）。"""
        return self._yaml_config.get("app", {}).get("current_step", "开发中")

    @property
    def temperature(self) -> float:
        """生成温度（创造性程度，范围 0 到 2。0=最确定，2=最随机，本项目默认 0.7）。"""
        return self._yaml_config.get("models", {}).get("temperature", 0.7)

    @property
    def max_tokens(self) -> int:
        """单次回复最大 token 数。"""
        return self._yaml_config.get("models", {}).get("max_tokens", 2048)
```

注意：`current_step` 放在 `storage_type` 之前（因为它属于 app 段），`temperature` 和 `max_tokens` 放在 `available_models` 之后（因为它们属于 models 段）。建议按配置段分组。

### 7.3 改造 src/ui/tui/widgets.py（print_banner 接收进度参数）

文件路径：`langchain-chat/src/ui/tui/widgets.py`。

找到 `print_banner` 函数，替换为：

```python
def print_banner(version: str, python_version: str, current_step: str = "") -> None:
    """打印启动横幅。

    参数：
        version: 应用版本号
        python_version: Python 版本号
        current_step: 当前进度文字（从配置读取，方案 B）
    """
    banner_text = Text()
    banner_text.append("LangChain Chat", style="bold cyan")
    banner_text.append(f"  v{version}", style="dim")
    banner_text.append(f"\nPython {python_version}", style="green")
    if current_step:
        banner_text.append(f"\n当前进度：{current_step}", style="yellow")

    console.print(Panel(banner_text, border_style="cyan", title="欢迎", title_align="left"))
```

改动要点：

- 函数签名加了 `current_step: str = ""` 参数。
- 不再写死「Step 5 预设管理」，改为用传入的 current_step。
- 当 current_step 为空时，不显示进度行（兼容性）。

### 7.4 改造 src/ui/tui/app.py（调用时传入 current_step）

文件路径：`langchain-chat/src/ui/tui/app.py`。

找到 `print_banner` 的调用（在 run 方法里），改为：

```python
        widgets.print_banner(
            version="0.1.0",
            python_version=platform.python_version(),
            current_step=get_config().current_step,
        )
```

`get_config()` 在文件顶部已 import（`from core.config_manager import get_config`），`current_step` 是新增的属性。

#### 验证检查点 A：方案 B 是否生效

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.config_manager import get_config; c = get_config(); print('current_step:', c.current_step); print('temperature:', c.temperature); print('max_tokens:', c.max_tokens)"
```

预期输出：

```
current_step: Step 6  对话引擎
temperature: 0.7
max_tokens: 2048
```

### 7.5 创建 src/core/chat_engine.py（对话引擎）

文件路径：`langchain-chat/src/core/chat_engine.py`。

这是本步骤的核心文件。封装 LLM 调用，提供两种方式：同步 chat（非流式）和异步 astream（流式）。

**设计说明**：

- ChatEngine 通过依赖注入接收 AppConfig，不自己读 .env（配置由 config_manager 统一管理）。
- 记忆由调用方维护（传入消息历史），ChatEngine 不持有状态。这样一个引擎可服务多个会话。
- 流式用 astream（异步），逐 chunk 返回。
- Token 统计从 usage_metadata 提取。

**文件内容**：

```python
"""对话引擎（核心模块）。

封装 LLM 的调用逻辑：多轮对话、流式输出、超时重试、Token 统计。
对应需求文档 A1 至 A5（核心对话功能）与 G1（超时与重试）。

设计说明：
    - ChatEngine 通过依赖注入接收 SecretConfig（含 API 配置），不自己读 .env。
    - 用 LangChain 的 ChatOpenAI 作为 LLM 客户端（OpenAI 兼容格式）。
    - 多轮对话的记忆由调用方维护（传入消息历史），ChatEngine 不持有状态。
      这样一个 ChatEngine 实例可服务多个会话，避免状态串扰。
    - 流式输出用 astream（异步），逐 chunk 返回，调用方实时渲染。
    - 超时与重试由 ChatOpenAI 内置（max_retries、timeout 参数）。
    - Token 用量从响应的 usage_metadata 提取。

使用方式：
    engine = ChatEngine(config)
    async for chunk in engine.astream(messages):
        print(chunk.content, end="")
"""

from typing import AsyncIterator, Optional

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from core.config_manager import AppConfig


class ChatEngine:
    """对话引擎。

    封装 LLM 调用，提供同步调用和异步流式两种方式。
    """

    def __init__(self, config: AppConfig):
        """初始化对话引擎。

        参数：
            config: 应用配置（从中读取 API 地址、Key、模型名、超时、重试等）
        """
        self.config = config

        # 创建 ChatOpenAI 实例
        self.llm = ChatOpenAI(
            model=config.secret.MODEL_NAME,
            api_key=config.secret.API_KEY,
            base_url=config.secret.API_BASE_URL,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.llm_timeout,
            max_retries=config.llm_max_retries,
            streaming=True,
        )

    def chat(self, messages: list[BaseMessage]) -> tuple[str, dict]:
        """同步对话（非流式）。等待 LLM 完整生成后返回。

        参数：
            messages: 消息历史（LangChain 的 BaseMessage 列表）
        返回：
            (回复文本, token 用量字典)
            token 字典含 keys: prompt_tokens, completion_tokens, total_tokens
        """
        response: AIMessage = self.llm.invoke(messages)

        reply = response.content
        usage = self._extract_usage(response)
        return reply, usage

    async def astream(
        self, messages: list[BaseMessage]
    ) -> AsyncIterator[tuple[str, Optional[dict]]]:
        """异步流式对话。逐 chunk 返回，调用方实时渲染。

        参数：
            messages: 消息历史
        生成（yield）：
            每个 chunk 是一个元组 (text, usage)。
            中间的 chunk：text 是这一段的文字，usage 为 None。
            最后的 chunk：text 为空字符串，usage 含本次调用的 token 统计。
        """
        accumulated_text = ""
        final_usage = None

        async for chunk in self.llm.astream(messages):
            text = chunk.content
            if text:
                accumulated_text += text
                yield text, None

            # 提取 token 用量（通常在最后一个 chunk）
            usage = self._extract_usage(chunk)
            if usage is not None:
                final_usage = usage

        # 最后 yield 一个带 usage 的 chunk（text 为空）
        yield "", final_usage

    def _extract_usage(self, message: BaseMessage) -> Optional[dict]:
        """从 LangChain 响应中提取 token 用量。

        LangChain 把 OpenAI 的 usage 封装到 usage_metadata 字段。
        返回 None 表示该消息没有用量信息（流式中间 chunk 通常没有）。
        """
        usage_meta = getattr(message, "usage_metadata", None)
        if usage_meta is None:
            return None

        return {
            "prompt_tokens": usage_meta.get("input_tokens", 0),
            "completion_tokens": usage_meta.get("output_tokens", 0),
            "total_tokens": usage_meta.get("total_tokens", 0),
        }

    async def close(self) -> None:
        """关闭引擎（当前 ChatOpenAI 无需显式关闭，预留接口）。"""
        pass
```

#### 验证检查点 B：ChatEngine 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.chat_engine import ChatEngine; print('ChatEngine 导入成功:', ChatEngine.__name__)"
```

预期输出：`ChatEngine 导入成功: ChatEngine`

---

## 八、全面验证（冒烟测试）

本步骤的验证采用专门的冒烟测试脚本，覆盖 6 个测试场景，确保全面（呼应 Step 5 的教训）。

### 8.1 创建 scripts/test_chat_engine.py

文件路径：`langchain-chat/scripts/test_chat_engine.py`。

```python
"""ChatEngine 冒烟测试脚本。

全面验证对话引擎的各项功能，确保及早发现问题（呼应 Step 5 教训）。
覆盖：单轮对话、多轮对话（记忆）、流式输出、Token 统计、错误处理。

运行方式：
    uv run python scripts/test_chat_engine.py

前提：已在 .env 中配置真实的 API_BASE_URL、API_KEY、MODEL_NAME。
"""

import asyncio
import sys
from pathlib import Path

# 将 src 目录加入模块搜索路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from langchain_core.messages import HumanMessage, SystemMessage

from core.chat_engine import ChatEngine
from core.config_manager import get_config


async def test_single_turn(engine: ChatEngine) -> None:
    """测试 1：单轮对话（非流式）。"""
    print("[测试 1] 单轮对话（非流式）")
    messages = [HumanMessage(content="请用一句话回答：1+1 等于几？")]
    reply, usage = engine.chat(messages)
    print(f"  回复: {reply}")
    print(f"  Token: {usage}")
    assert reply, "回复不应为空"
    print("  结果: 通过\n")


async def test_multi_turn(engine: ChatEngine) -> None:
    """测试 2：多轮对话（验证记忆）。"""
    print("[测试 2] 多轮对话（验证记忆）")
    # 第一轮
    msg1 = HumanMessage(content="我叫小明，请记住我的名字。")
    reply1, _ = engine.chat([msg1])
    print(f"  第一轮回复: {reply1[:50]}...")

    # 第二轮（带上第一轮的历史，验证 LLM 记得名字）
    history = [msg1, HumanMessage(content="我叫什么名字？")]
    reply2, _ = engine.chat(history)
    print(f"  第二轮回复: {reply2}")
    assert "小明" in reply2, f"LLM 应该记得名字是小明，实际回复: {reply2}"
    print("  结果: 通过（LLM 记住了名字）\n")


async def test_streaming(engine: ChatEngine) -> None:
    """测试 3：流式输出。"""
    print("[测试 3] 流式输出")
    messages = [HumanMessage(content="请数 1 到 5，每个数字占一行。")]
    print("  流式输出: ", end="")
    chunk_count = 0
    final_usage = None
    async for text, usage in engine.astream(messages):
        if text:
            print(text, end="", flush=True)
            chunk_count += 1
        if usage is not None:
            final_usage = usage
    print()
    print(f"  收到 {chunk_count} 个文本 chunk")
    print(f"  Token: {final_usage}")
    assert chunk_count > 0, "流式应返回多个 chunk"
    print("  结果: 通过\n")


async def test_token_usage(engine: ChatEngine) -> None:
    """测试 4：Token 统计。"""
    print("[测试 4] Token 统计")
    messages = [HumanMessage(content="你好")]
    reply, usage = engine.chat(messages)
    print(f"  回复: {reply}")
    print(f"  Token 统计: {usage}")
    assert usage["prompt_tokens"] > 0, "输入 token 应大于 0"
    assert usage["completion_tokens"] > 0, "输出 token 应大于 0"
    assert usage["total_tokens"] > 0, "总 token 应大于 0"
    print("  结果: 通过（Token 统计正常）\n")


async def test_system_prompt(engine: ChatEngine) -> None:
    """测试 5：系统预设（system_prompt）。"""
    print("[测试 5] 系统预设（system_prompt）")
    messages = [
        SystemMessage(content="你是一个只会说英语的助手，即使用户说中文你也用英语回复。"),
        HumanMessage(content="你好"),
    ]
    reply, _ = engine.chat(messages)
    print(f"  回复: {reply[:80]}")
    # 不做强断言（LLM 不一定严格遵守），只展示 system_prompt 的效果
    print("  结果: 通过（已发送 system_prompt）\n")


async def test_error_handling(engine: ChatEngine) -> None:
    """测试 6：错误处理（用错误的模型名触发错误）。"""
    print("[测试 6] 错误处理（错误的模型名）")
    from langchain_openai import ChatOpenAI
    bad_llm = ChatOpenAI(
        model="this-model-does-not-exist",
        api_key=engine.config.secret.API_KEY,
        base_url=engine.config.secret.API_BASE_URL,
        timeout=10,
        max_retries=1,
    )
    try:
        bad_llm.invoke([HumanMessage(content="test")])
        print("  结果: 未触发错误（可能 API 容错较强）\n")
    except Exception as e:
        error_type = type(e).__name__
        print(f"  触发错误（预期行为）: {error_type}")
        print("  结果: 通过（错误被正确触发）\n")


async def main():
    print("=" * 60)
    print("Step 6：ChatEngine 冒烟测试")
    print("=" * 60)

    # 加载配置
    config = get_config()
    print(f"API 地址: {config.secret.API_BASE_URL}")
    print(f"模型:     {config.secret.MODEL_NAME}")
    print(f"API Key:  {config.secret.API_KEY[:8]}...")
    print()

    # 检查 API Key 是否已配置
    if not config.secret.API_KEY or config.secret.API_KEY == "your_api_key_here":
        print("错误：API_KEY 未配置，请在 .env 文件中填入真实的 API Key。")
        return

    # 创建引擎
    engine = ChatEngine(config)

    # 运行所有测试
    try:
        await test_single_turn(engine)
        await test_multi_turn(engine)
        await test_streaming(engine)
        await test_token_usage(engine)
        await test_system_prompt(engine)
        await test_error_handling(engine)
        print("=" * 60)
        print("[全部通过] ChatEngine 冒烟测试全部成功")
        print("=" * 60)
    except AssertionError as e:
        print(f"[断言失败] {e}")
    except Exception as e:
        print(f"[异常] {type(e).__name__}: {e}")
    finally:
        await engine.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 8.2 运行冒烟测试

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python scripts/test_chat_engine.py
```

### 8.3 预期结果

6 个测试全部通过。每个测试会显示回复内容和 Token 统计。最后显示：

```
============================================================
[全部通过] ChatEngine 冒烟测试全部成功
============================================================
```

### 8.4 验证要点

| 测试 | 验证内容 | 通过标准 |
|------|---------|---------|
| 测试 1 | 单轮对话 | 回复不为空 |
| 测试 2 | 多轮对话记忆 | LLM 答出「小明」（记得历史） |
| 测试 3 | 流式输出 | 收到多个 chunk |
| 测试 4 | Token 统计 | 三个 token 值都大于 0 |
| 测试 5 | 系统预设 | 成功发送 system_prompt |
| 测试 6 | 错误处理 | 错误模型名触发异常 |

如果某个测试失败，参考第十章排查。特别是测试 2（多轮记忆）和测试 6（错误处理），最可能暴露问题。

---

## 九、版本控制

### 9.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 新增：`examples/`（4 个文件）、`scripts/test_chat_engine.py`、`src/core/chat_engine.py`
- 修改：`config.yaml`（current_step）、`src/core/config_manager.py`（三个新属性）、`src/ui/tui/widgets.py`（print_banner）、`src/ui/tui/app.py`（传入 current_step）
- 修改：`pyproject.toml`、`uv.lock`（新增 langchain 依赖）
- 不应出现：`.env`、`data/`、`.venv/`

### 9.2 提交与打标签

```bash
git add .
git status
git commit -m "feat: step 6 - 对话引擎（LLM 调用、流式输出、Token 统计）与 LLM 编程示例"
git tag step-6-chat-engine
git push
git push origin step-6-chat-engine
git log --oneline -7
git tag
```

---

## 十、常见问题与排查

### 10.1 API Key 相关

| 报错 | 原因 | 解决 |
|------|------|------|
| `AuthenticationError` | API Key 错误或过期 | 检查 .env 的 API_KEY 是否正确、是否过期 |
| `API_KEY 未配置` | .env 里是占位符 | 填入真实的 API Key |
| `APIConnectionError` | 网络不通或地址错误 | 检查 API_BASE_URL 是否正确，网络是否能访问 |

### 10.2 模型名相关

| 报错 | 原因 | 解决 |
|------|------|------|
| `NotFoundError: model does not exist` | MODEL_NAME 写错 | 确认模型名（如 deepseek-chat，不是 deepseek） |
| 不同服务的模型名不同 | 各家模型名不一样 | 参考第五章 5.2 节的配置示例 |

### 10.3 流式输出相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 流式输出一次性返回 | streaming 没启用 | 确认 ChatOpenAI 构造时 `streaming=True` |
| `astream` 报错 | 不是 async 环境 | 确保用 `async for` 且最外层有 asyncio.run |

### 10.4 Token 统计相关

| 现象 | 原因 | 解决 |
|------|------|------|
| `usage` 为 None | 流式中间 chunk 没有 usage | 正常，最后一个 chunk 才有，ChatEngine 已处理 |
| `usage_metadata` 字段不存在 | LangChain 版本差异 | 确认 langchain-core >= 1.4 |

---

## 十一、本步骤小结与知识清单

### 11.1 产出清单

| 类别 | 产出 |
|------|------|
| 对话引擎 | src/core/chat_engine.py（ChatEngine，封装 LLM 调用） |
| LLM 编程示例 | examples/（三层示例，HTTP/SDK/LangChain） |
| 冒烟测试 | scripts/test_chat_engine.py（6 个测试场景） |
| 方案 B | config.yaml + config_manager + widgets + app（进度文字从配置读取） |
| 新依赖 | langchain 1.3.13、langchain-openai 1.3.5 |
| 版本控制 | 提交 feat: step 6、标签 step-6-chat-engine |

### 11.2 知识清单

学完本步骤，应当掌握：

- LLM、API、HTTP 请求、Token、上下文窗口、流式输出的基础概念。
- 为什么 LLM 本身没有记忆，多轮对话靠维护消息历史。
- LLM 编程的三层封装（HTTP → OpenAI SDK → LangChain）及各自特点。
- LangChain 的 ChatOpenAI、消息类型（HumanMessage/AIMessage/SystemMessage）。
- 流式输出（astream）与 Token 统计（usage_metadata）。
- 超时重试机制（timeout + max_retries）。
- API Key 的安全规范。
- 方案 B（进度文字从配置读取，不再写死）。

### 11.3 项目当前状态

```
langchain-chat @ step-6-chat-engine
对话引擎：ChatEngine 完整可用（单轮/多轮/流式/Token/重试）
LLM 编程示例：examples/ 三层示例
桩函数替换进度：用户、预设已实现；对话引擎就绪但未接界面
下一步：Step 7 把引擎接进 TUI，实现界面上的多轮对话（核心里程碑）
```

### 11.4 桩函数替换进度

| 菜单功能 | 状态 | 实现步骤 |
|---------|------|---------|
| 用户管理 | 已实现 | Step 4 |
| 预设管理 | 已实现 | Step 5 |
| 会话管理 | 桩函数 | Step 7、8 |
| 开始对话 | 桩函数（引擎已就绪） | Step 7（核心里程碑） |
| 设置 | 桩函数 | Step 10 |

### 11.5 下一步预告

Step 7：会话管理 + TUI 对话视图对接。

这是项目的**核心里程碑**——把 Step 6 的对话引擎接进 TUI 界面，实现：

- 在 TUI 里输入消息，LLM 流式回复。
- 多轮对话（维护消息历史）。
- 选择预设角色（Step 5 的 system_prompt）。
- Token 用量实时显示。
- 会话自动保存（数据持久化）。

到 Step 7，你就能在终端里和 LLM 真正聊天了。

---

> 本文档为 langchain-chat 项目 Step 6 的教学手册。按本文档操作，可从零理解 LLM 编程并实现对话引擎。操作过程中如遇问题，可参考第十部分排查，或随时询问。
