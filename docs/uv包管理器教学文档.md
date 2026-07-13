# uv 包管理器教学文档

> **版本**：v1.1  
> **日期**：2026-06-24  
> **适用场景**：Python 项目开发，现代包管理与环境管理  
> **配套项目**：langchain-chat（LangChain 多轮会话项目）

---

## 目录

- [一、uv 是什么](#一uv-是什么)
- [二、为什么要用 uv](#二为什么要用-uv)
- [三、为什么选 uv](#三为什么选-uv)
- [四、安装 uv](#四安装-uv)
- [五、uv 环境变量管理（完整版）](#五uv-环境变量管理完整版)
- [六、用 uv 管理 Python 版本](#六用-uv-管理-python-版本)
- [七、用 uv 管理虚拟环境](#七用-uv-管理虚拟环境)
- [八、用 uv 管理依赖](#八用-uv-管理依赖)
- [九、用 uv 运行项目](#九用-uv-运行项目)
- [十、uv 与系统 Python / Anaconda 的关系](#十uv-与系统-python--anaconda-的关系)
- [十一、完整工作流程示例](#十一完整工作流程示例)
- [附录：命令速查表](#附录命令速查表)

---

## 一、uv 是什么

### 定义

**uv** 是由 **Astral 公司**（一个专注于 Python 工具链的公司）开发的现代化 Python 包管理器，使用 **Rust 语言**编写。

### 核心能力

uv 一个工具整合了传统 Python 开发中多个工具的功能：

| 传统工具组合 | uv 的对应能力 |
|-------------|--------------|
| `pip`（安装包） | `uv add` / `uv pip` |
| `venv`（创建虚拟环境） | `uv venv`（自动创建） |
| `pip-tools`（依赖锁定） | `uv lock`（自动生成 uv.lock） |
| `pyenv`（管理多版本 Python） | `uv python install` |
| `virtualenv`（更快的环境创建） | 内置，比 virtualenv 快很多 |
| `poetry`（项目管理） | `uv init` / `uv add` / `uv sync` |

### 一句话理解

> uv 是一个 **"一个工具搞定 Python 一切环境问题"** 的现代化工具，用 Rust 写的所以极快。

---

## 二、为什么要用 uv

### 传统 Python 环境管理的痛点

#### 痛点 1：工具繁多，需要组合使用

传统方式下，你需要：

```
pyenv      → 管理多个 Python 版本
venv       → 创建虚拟环境
pip        → 安装包
pip-tools  → 锁定依赖版本
poetry     → 项目管理
```

每个工具都要单独学、单独装，组合使用时还容易出问题。

#### 痛点 2：速度慢

传统的 `pip install` 在大型项目中可能很慢（解析依赖、下载、安装）。

#### 痛点 3：环境混乱

- 全局环境 vs 虚拟环境分不清
- 不同项目依赖冲突
- 团队成员环境不一致

### uv 如何解决这些痛点

| 痛点 | uv 的解决方案 |
|------|--------------|
| 工具繁多 | 一个工具搞定一切，命令简洁统一 |
| 速度慢 | 用 Rust 编写，比 pip 快 **10-100 倍** |
| 环境混乱 | 项目级隔离，`pyproject.toml` + `uv.lock` 保证一致性 |

### 速度对比示例

安装 langchain 全家桶：

```
传统 pip：    约 30-60 秒
uv：          约 2-5 秒
```

---

## 三、为什么选 uv

### 与其他工具对比

| 工具 | 语言 | 速度 | 功能覆盖 | 社区活跃度 | 学习成本 |
|------|------|------|----------|-----------|----------|
| **uv** | Rust | 极快 | 全（版本+环境+依赖+锁定） | 快速增长 | 低 |
| pip + venv | Python | 慢 | 基础（无版本管理、无锁定） | 极高 | 低 |
| poetry | Python | 中等 | 部分（无版本管理） | 高 | 中 |
| pipenv | Python | 慢 | 部分 | 下降中 | 中 |
| conda | C/Python | 慢 | 全（含科学计算库） | 高 | 高 |
| hatch | Python | 中等 | 部分 | 中 | 中 |

### 选择 uv 的核心理由

1. **速度快**：Rust 编写，性能碾压同类工具
2. **功能全**：一个工具覆盖 Python 版本管理、虚拟环境、依赖管理、锁定文件
3. **兼容性好**：与 `pip` 生态完全兼容，支持 `requirements.txt`
4. **现代标准**：使用 `pyproject.toml`（PEP 621 标准）
5. **活跃维护**：Astral 公司全职维护，更新频繁
6. **学习成本低**：命令简洁直观，与 pip 命令风格相似

### 什么时候**不**用 uv

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 科学计算（需要 MKL、CUDA 等非 Python 依赖） | conda | conda 能管理非 Python 依赖 |
| 维护老项目（只有 requirements.txt，无 pyproject.toml） | pip | 不必为了老项目引入新工具 |
| 公司强制规定使用特定工具 | 按公司规定 | 团队一致性优先 |

---

## 四、安装 uv

### 4.1 如何验证是否已安装

打开终端（PowerShell 或 CMD），执行：

```bash
uv --version
```

- **已安装**：显示版本号，如 `uv 0.11.8`
- **未安装**：提示 `'uv' 不是内部或外部命令`

### 4.2 如何安装（Windows 11）

#### 方式 1：PowerShell 安装（官方推荐）

打开 **PowerShell**，执行：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**命令解析**：
- `irm` = Invoke-RestMethod，从 astral.sh 下载安装脚本
- `iex` = Invoke-Expression，执行下载的脚本
- `ExecutionPolicy ByPass` = 临时绕过 PowerShell 脚本执行限制（安全）

#### 方式 2：winget 安装

```powershell
winget install --id=astral-sh.uv -e
```

#### 方式 3：pip 安装（需已有 Python）

```bash
pip install uv
```

#### 方式 4：手动下载

1. 访问 https://github.com/astral-sh/uv/releases
2. 下载 `uv-x86_64-pc-windows-msvc.zip`
3. 解压后将 `uv.exe` 放到某目录
4. 把该目录添加到系统环境变量 PATH

### 4.3 安装后如何验证

**关闭并重新打开终端**（让环境变量生效），执行：

```bash
uv --version
```

显示版本号即安装成功。

---

## 五、uv 环境变量管理（完整版）

### 5.1 为什么需要了解环境变量

uv 的很多行为可以通过**环境变量**来定制，例如：
- Python 安装在哪里
- 缓存放哪里
- 包从哪里下载（镜像源）
- 项目虚拟环境叫什么

理解并掌握这些环境变量，可以让你完全掌控 uv 的行为，适应不同的开发环境（如磁盘空间分配、内网镜像、多项目隔离等）。

### 5.2 修改环境变量的通用方法

所有 uv 环境变量，都可以用以下**两种通用方法**修改：

#### 方法 A：用 `setx` 命令永久设置（推荐）

在终端执行：

```bash
setx 变量名 "变量值"
```

- 作用：永久写入用户环境变量，对所有新打开的终端生效
- 注意：**对当前终端不立即生效**，必须关闭并重新打开终端
- 验证：重新打开终端后执行 `echo %变量名%`（CMD）或 `$env:变量名`（PowerShell）

示例：
```bash
setx UV_PYTHON_INSTALL_DIR "D:\uv_python"
```

#### 方法 B：系统环境变量 GUI 设置（图形界面）

1. 按 `Win + R`，输入 `sysdm.cpl`，回车 → 打开"系统属性"
2. 点击 **"高级"** 选项卡 → 点击 **"环境变量"**
3. 在 **"用户变量"** 区域（上半部分），点击 **"新建"**
4. 填写变量名和变量值
5. 点击"确定"保存所有对话框
6. **关闭并重新打开终端**（必须！）

#### 方法 C：临时设置（仅当前终端有效）

CMD 中：
```cmd
set UV_PYTHON_INSTALL_DIR=D:\uv_python
```

PowerShell 中：
```powershell
$env:UV_PYTHON_INSTALL_DIR = "D:\uv_python"
```

- 作用：仅在当前终端窗口有效，关闭窗口后失效
- 适用场景：临时测试某个配置，或单次执行需要特定环境

> 推荐日常使用 **方法 A（setx）** 或 **方法 B（GUI）**，它们是永久生效的。

### 5.3 uv 常用环境变量完整清单

下表列出 uv 所有常用环境变量。每个变量的修改方法都遵循 5.2 节的通用方法，只需替换变量名和变量值即可。

| 环境变量 | 作用 | 默认值（Windows） | 常用度 |
|----------|------|-------------------|--------|
| `UV_PYTHON_INSTALL_DIR` | uv 管理的 Python 安装目录 | `C:\Users\{用户}\AppData\Roaming\uv\python` | 高 |
| `UV_TOOL_DIR` | uv 工具环境安装目录（`uv tool install` 安装的工具） | `C:\Users\{用户}\AppData\Roaming\uv\tools` | 中 |
| `UV_TOOL_BIN_DIR` | uv 工具可执行文件的 bin 目录（工具命令的全局调用入口） | `C:\Users\{用户}\AppData\Roaming\uv\bin` | 中 |
| `UV_CACHE_DIR` | uv 缓存目录（下载缓存、编译缓存等） | `C:\Users\{用户}\AppData\Local\uv\cache` | 高 |
| `UV_PROJECT_ENVIRONMENT` | 项目虚拟环境的路径（默认是项目下的 `.venv`） | `项目目录\.venv` | 中 |
| `UV_INDEX_URL` | Python 包索引的 URL（用于指定镜像源） | `https://pypi.org/simple` | 高（国内必用） |
| `UV_INDEX` | 额外的包索引 URL（可多个，用于私有源） | 无 | 中 |
| `UV_PYTHON_PREFERENCE` | Python 版本选择偏好（`only-managed` / `managed` / `system` / `only-system`） | 自动 | 低 |
| `UV_HTTP_TIMEOUT` | HTTP 请求超时时间（秒） | 30 | 低 |
| `UV_CONCURRENT_DOWNLOADS` | 并发下载数 | 自动 | 低 |
| `UV_NO_CACHE` | 禁用缓存（设为 `1` 时生效） | 未设置 | 低 |
| `UV_INSTALL_DIR` | uv 自身的安装目录（仅在安装 uv 时设置，运行时不可改） | `C:\Users\{用户}.local\bin` | 低 |
| `VIRTUAL_ENV` | 已激活的虚拟环境路径（标准 Python 变量，uv 会识别） | 无 | 低 |

### 5.4 常用环境变量修改示例

下面针对最常用的几个环境变量，给出完整的修改步骤。

#### 示例 1：修改 Python 安装目录（`UV_PYTHON_INSTALL_DIR`）

**目标**：把 uv 管理的 Python 从默认的 C 盘改到 `D:\uv_python`

```bash
# 第 1 步：创建目标目录
mkdir D:\uv_python

# 第 2 步：设置环境变量（永久）
setx UV_PYTHON_INSTALL_DIR "D:\uv_python"

# 第 3 步：关闭并重新打开终端

# 第 4 步：验证
uv python dir
# 应输出：D:\uv_python

# 第 5 步：安装 Python（此时会装到新目录）
uv python install 3.12
```

#### 示例 2：修改缓存目录（`UV_CACHE_DIR`）

**目标**：把 uv 缓存改到 `D:\uv_cache`（节省 C 盘空间）

```bash
mkdir D:\uv_cache
setx UV_CACHE_DIR "D:\uv_cache"
# 关闭并重新打开终端
```

验证：
```bash
uv cache dir
# 应输出：D:\uv_cache
```

#### 示例 3：修改工具安装目录（`UV_TOOL_DIR` 和 `UV_TOOL_BIN_DIR`）

**目标**：把 uv 全局工具（`uv tool install` 安装的工具，如 ruff、black 等命令行工具）改到 D 盘

```bash
mkdir D:\uv_tools
mkdir D:\uv_tools_bin
setx UV_TOOL_DIR "D:\uv_tools"
setx UV_TOOL_BIN_DIR "D:\uv_tools_bin"
# 关闭并重新打开终端
```

验证：
```bash
uv tool dir
# 应输出：D:\uv_tools
uv tool dir --bin
# 应输出：D:\uv_tools_bin
```

> 注意：`UV_TOOL_BIN_DIR` 这个目录需要加入系统 PATH，这样你才能在任意位置直接调用安装的工具命令。

#### 示例 4：修改包索引镜像源（`UV_INDEX_URL`）

**目标**：使用国内镜像源加速下载（解决 PyPI 访问慢的问题）

**清华镜像源**：
```bash
setx UV_INDEX_URL "https://pypi.tuna.tsinghua.edu.cn/simple"
# 关闭并重新打开终端
```

**阿里云镜像源**：
```bash
setx UV_INDEX_URL "https://mirrors.aliyun.com/pypi/simple/"
# 关闭并重新打开终端
```

验证：安装任意包时观察下载源是否变了：
```bash
uv add requests
# 日志中应显示从 tuna.tsinghua.edu.cn 下载
```

#### 示例 5：修改项目虚拟环境名称/路径（`UV_PROJECT_ENVIRONMENT`）

**目标**：把项目的虚拟环境从默认的 `.venv` 改成其他路径

```bash
setx UV_PROJECT_ENVIRONMENT "D:\my_venvs\langchain-chat"
# 关闭并重新打开终端
# 之后在该终端执行 uv sync，虚拟环境会创建到 D:\my_venvs\langchain-chat
```

> 注意：通常不建议改这个，默认的 `.venv`（项目内）是最常见和方便的做法。此变量主要用于把所有虚拟环境集中管理的场景。

### 5.5 一次性搬迁所有 uv 目录到 D 盘（推荐配置）

如果你想彻底把 uv 相关的所有目录都搬到 D 盘（C 盘空间紧张时推荐），一次性设置：

```bash
mkdir D:\uv_python
mkdir D:\uv_tools
mkdir D:\uv_tools_bin
mkdir D:\uv_cache

setx UV_PYTHON_INSTALL_DIR "D:\uv_python"
setx UV_TOOL_DIR "D:\uv_tools"
setx UV_TOOL_BIN_DIR "D:\uv_tools_bin"
setx UV_CACHE_DIR "D:\uv_cache"

# 关闭并重新打开终端

# 验证所有设置
uv python dir
uv tool dir
uv tool dir --bin
uv cache dir
```

四个命令都输出 D 盘路径，说明全部设置成功。

> 注意：如果你之前已经在 C 盘默认目录装过 Python 或缓存，改完环境变量后**旧的文件不会自动迁移**，需要重新执行 `uv python install` 等命令。可以考虑清理旧的默认目录释放 C 盘空间。

### 5.6 查看当前生效的环境变量

```cmd
:: CMD 中查看单个变量
echo %UV_PYTHON_INSTALL_DIR%

:: CMD 中查看所有 UV_ 开头的变量
set UV_

:: PowerShell 中查看单个变量
$env:UV_PYTHON_INSTALL_DIR

:: PowerShell 中查看所有 UV_ 开头的变量
Get-ChildItem env: | Where-Object Name -Like "UV_*"
```

### 5.7 删除环境变量

如果设置错误想删除：

**方法 A：用 `setx` 设为空**（不推荐，会留下空值）
```cmd
setx UV_PYTHON_INSTALL_DIR ""
```

**方法 B：GUI 删除（推荐）**
1. `Win + R` → `sysdm.cpl` → 高级 → 环境变量
2. 在用户变量中选中要删除的变量
3. 点击"删除"
4. 关闭并重新打开终端

---

## 六、用 uv 管理 Python 版本

### 6.1 核心概念

uv 可以帮你安装和管理多个 Python 版本，安装位置由环境变量 `UV_PYTHON_INSTALL_DIR` 决定（详见第五章）。

### 6.2 安装 Python 版本

```bash
# 安装 Python 3.12
uv python install 3.12

# 安装多个版本（可并存，互不冲突）
uv python install 3.10
uv python install 3.11
uv python install 3.13
```

安装后的目录结构：
```
D:\uv_python\（或默认的 C 盘目录）
├── cpython-3.10.x-windows-x86_64-none\    ← Python 3.10
├── cpython-3.11.x-windows-x86_64-none\    ← Python 3.11
├── cpython-3.12.x-windows-x86_64-none\    ← Python 3.12
└── cpython-3.13.x-windows-x86_64-none\    ← Python 3.13
```

> **关键理解**：`uv python install` 是**全局安装命令**，在任意目录执行都一样，与当前所在目录无关。

### 6.3 查看 Python 版本

```bash
# 查看所有已安装的 Python 版本
uv python list
```

输出示例：
```
cpython-3.10.x-windows-x86_64-none    /path/to/3.10
cpython-3.12.x-windows-x86_64-none    /path/to/3.12    ← installed
```

### 6.4 给项目指定 Python 版本

uv 的版本切换是**按项目独立指定**，不是全局切换。每个项目可以绑定不同的 Python 版本。

#### 方式 1：`uv python pin`（最推荐）

在项目目录下执行：

```bash
cd D:\ZCodeProject\langchain-chat
uv python pin 3.12
```

这会生成 `.python-version` 文件（内容只有一行 `3.12`），之后该项目所有 uv 命令自动用 3.12。

**切换版本**（重新 pin 即可）：
```bash
uv python pin 3.11    # 改成 3.11
```

> `.python-version` 文件**应该提交到 git**，这样团队成员 clone 后会用相同的 Python 版本。

#### 方式 2：`pyproject.toml` 声明版本范围

```toml
[project]
requires-python = ">=3.10,<3.13"
```

uv 会从已安装版本中自动选一个满足条件的。

#### 方式 3：创建 venv 时指定

```bash
uv venv --python 3.11
```

### 6.5 卸载 Python 版本

```bash
uv python uninstall 3.10
```

### 6.6 查看当前项目用的 Python 版本

```bash
# 查看当前项目 pin 的版本
uv python pin

# 查看 uv 实际选择的 Python
uv run python --version
```

---

## 七、用 uv 管理虚拟环境

### 7.1 什么是虚拟环境

**虚拟环境（virtual environment）**是 Python 的隔离运行环境。

打个比方：
- Python 安装目录（如 `D:\uv_python`）= **公共仓库**（存各种 Python 版本）
- 虚拟环境（项目里的 `.venv`）= **每个项目的私人工具箱**（存该项目的依赖包）

### 7.2 为什么需要虚拟环境

| 不用虚拟环境 | 用虚拟环境 |
|-------------|-----------|
| 所有项目共用一个全局 Python | 每个项目独立隔离 |
| 项目 A 要 langchain 1.3，项目 B 要 langchain 0.1，冲突 | 各装各的，互不冲突 |
| 装错包可能搞坏系统 Python | 搞坏了删 `.venv` 重建即可 |
| 无法精确定位项目依赖 | `pyproject.toml` 记录精确依赖 |

### 7.3 创建虚拟环境

```bash
cd D:\ZCodeProject\langchain-chat

# 方式 1：显式创建（会在当前目录创建 .venv 文件夹）
uv venv

# 方式 2：用指定 Python 版本创建
uv venv --python 3.12

# 方式 3：不手动创建，uv add 时会自动创建
uv add rich
```

### 7.4 uv 的最大优势：不需要手动激活

对比传统方式和 uv 方式：

| 操作 | 传统方式（venv/pip） | uv 方式 |
|------|---------------------|---------|
| 创建虚拟环境 | `python -m venv .venv` | `uv venv`（或自动创建） |
| **激活虚拟环境** | `.venv\Scripts\activate` | **不需要** |
| 安装依赖 | `pip install xxx` | `uv add xxx` |
| 运行程序 | `python xxx.py` | `uv run python xxx.py` |
| 运行项目 | 手动激活后运行 | `uv run ...`（自动处理一切） |

> **关键理解**：`uv run` 命令会自动使用项目 `.venv` 中的环境，无需手动激活。

### 7.5 多个项目的虚拟环境

每个项目都有自己的 `.venv`，完全独立：

```
D:\ZCodeProject\
├── langchain-chat\
│   ├── .venv\              ← 项目1的虚拟环境（独立的）
│   ├── pyproject.toml
│   └── src\
├── another-project\
│   ├── .venv\              ← 项目2的虚拟环境（独立的）
│   └── pyproject.toml
```

> `.venv` 目录**不要提交到 git**（在 .gitignore 中排除），因为它是可重建的，体积大且平台相关。

### 7.6 删除虚拟环境（重建）

```bash
# 手动删除 .venv 目录
rmdir /s /q .venv

# 然后重新创建
uv sync
# 或
uv venv
```

---

## 八、用 uv 管理依赖

### 8.1 添加依赖

```bash
# 添加运行时依赖（自动写入 pyproject.toml + 安装到 .venv）
uv add langchain
uv add langchain-openai
uv add rich prompt_toolkit

# 添加开发依赖（只在开发时需要，如测试、格式化工具）
uv add --dev pytest
uv add --dev pytest-asyncio
uv add --dev ruff
```

**运行时依赖 vs 开发依赖的区别**：

| 类型 | 用途 | 示例 | 部署时是否需要 |
|------|------|------|---------------|
| 运行时依赖 | 程序运行必需 | langchain、rich | 需要 |
| 开发依赖 | 只在开发/测试时需要 | pytest、ruff | 不需要 |

### 8.2 删除依赖

```bash
uv remove langchain
```

### 8.3 同步依赖

```bash
# 按 pyproject.toml + uv.lock 安装所有依赖
# 场景：clone 了别人的项目，或拉取了新代码后
uv sync
```

> `uv sync` 是团队协作的核心命令，保证每个人的环境完全一致。

### 8.4 查看已安装的包

```bash
uv pip list
```

### 8.5 锁定依赖版本

```bash
# 生成/更新 uv.lock 文件
uv lock
```

> `uv.lock` 文件**应该提交到 git**，它记录了所有依赖的精确版本，保证团队成员安装完全一致的依赖。

### 8.6 关于 pyproject.toml 和 uv.lock

| 文件 | 作用 | 是否提交 git | 谁维护 |
|------|------|-------------|--------|
| `pyproject.toml` | 声明项目元数据和依赖（人为编辑或 uv add 修改） | 提交 | 开发者 |
| `uv.lock` | 锁定所有依赖的精确版本（自动生成） | 提交 | uv 自动 |
| `.venv` | 实际的虚拟环境 | 不提交 | uv 自动创建 |

**三者的关系**：
```
开发者 → pyproject.toml（声明需要什么）
             ↓
   uv lock（解析依赖，生成 uv.lock）
             ↓
   uv sync（按 uv.lock 安装到 .venv）
```

---

## 九、用 uv 运行项目

### 9.1 运行 Python 脚本

```bash
# 在项目虚拟环境中运行脚本（自动处理环境）
uv run python src/main.py
```

### 9.2 运行其他命令

```bash
# 运行测试
uv run pytest

# 运行模块
uv run python -m http.server

# 运行任意命令
uv run rich --version
```

### 9.3 为什么用 `uv run` 而不是直接 `python`

| 直接 `python src/main.py` | `uv run python src/main.py` |
|---------------------------|----------------------------|
| 用系统默认 Python（可能是 conda 或全局） | 自动用项目的 `.venv` |
| 找不到项目依赖（包装在 .venv 里） | 自动找到所有依赖 |
| 可能用了错误的 Python 版本 | 自动用 pin 的版本 |

**黄金法则**：在 uv 项目中，**所有 Python 相关命令都用 `uv run` 前缀**。

---

## 十、uv 与系统 Python / Anaconda 的关系

### 10.1 是否会冲突

**不会冲突**，只要遵循正确的使用规范。

### 10.2 三者对比

| 对比项 | uv 管理的 Python | 系统 Python | Anaconda Python |
|--------|-----------------|-------------|-----------------|
| **位置** | `D:\uv_python`（可自定义） | `C:\Python312\` 等 | `C:\Users\xxx\anaconda3\` |
| **使用方式** | `uv run python` | 直接 `python` | `python`（激活 conda 后） |
| **虚拟环境** | `.venv`（项目内，自动管理） | 需手动 `venv` | conda 环境 |
| **依赖管理** | `pyproject.toml` + `uv.lock` | `requirements.txt` | `environment.yml` |
| **是否互相干扰** | 不干扰 | 不干扰 | PATH 可能干扰直接 `python` |

### 10.3 潜在冲突点：Anaconda

Anaconda 会修改 PATH 环境变量，加入自己的 Python。如果 PATH 中 Anaconda 在前，直接敲 `python` 会调用 Anaconda 的 Python。

**解决方式**：
1. 在 uv 项目中**始终用 `uv run`**，不直接敲 `python`
2. 或者临时不激活 conda 环境

### 10.4 避免冲突的黄金法则

| 原则 | 说明 |
|------|------|
| uv 项目用 `uv run` | 所有 Python 命令都用 `uv run python ...` |
| 不混用 pip 和 uv | uv 项目中用 `uv add`，不要用 `pip install` |
| 不混用 conda 和 uv | 同一个项目只用一个工具管理依赖 |
| PATH 顺序注意 | `uv run` 不受 PATH 顺序影响，但直接 `python` 受影响 |

### 10.5 验证当前用的是哪个 Python

```bash
# 查看 uv 用的 Python（项目虚拟环境）
uv run python -c "import sys; print(sys.executable)"
# 输出：D:\...\langchain-chat\.venv\Scripts\python.exe

# 查看系统默认的 Python（可能指向 conda 或系统 python）
python -c "import sys; print(sys.executable)"
# 输出：C:\...\anaconda3\python.exe 或 C:\Python312\python.exe
```

两个路径不同，说明它们是隔离的。

---

## 十一、完整工作流程示例

以我们的 `langchain-chat` 项目为例，展示从零开始的完整流程。

### 场景 1：从零创建项目

```bash
# 进入工作目录
cd D:\ZCodeProject

# 用 uv 初始化项目（创建 pyproject.toml 等基础文件）
uv init langchain-chat

# 进入项目
cd langchain-chat

# 固定 Python 版本
uv python pin 3.12

# 添加依赖（会自动创建 .venv）
uv add langchain langchain-openai langchain-core
uv add aiosqlite aiomysql
uv add rich prompt_toolkit
uv add pydantic pydantic-settings python-dotenv pyyaml
uv add --dev pytest pytest-asyncio ruff

# 运行项目
uv run python src/main.py
```

### 场景 2：clone 别人的项目后

```bash
# clone 项目（用 git）
git clone https://github.com/xxx/langchain-chat.git
cd langchain-chat

# 安装项目要求的 Python 版本（如果还没装）
uv python install 3.12

# 同步依赖（自动创建 .venv 并安装所有依赖）
uv sync

# 运行项目
uv run python src/main.py
```

### 场景 3：团队协作中添加新依赖

```bash
# 开发者 A 添加了一个新依赖
uv add httpx

# 提交代码（包括 pyproject.toml 和 uv.lock）
git add pyproject.toml uv.lock
git commit -m "feat: add httpx dependency"
git push

# 开发者 B 拉取代码后同步
git pull
uv sync    # 自动安装 httpx 及其依赖
```

---

## 附录：命令速查表

### Python 版本管理

| 命令 | 作用 |
|------|------|
| `uv python install 3.12` | 安装 Python 3.12 |
| `uv python list` | 查看所有已安装的 Python 版本 |
| `uv python pin 3.12` | 给当前项目固定 Python 版本（生成 .python-version） |
| `uv python uninstall 3.12` | 卸载 Python 3.12 |
| `uv python dir` | 查看 Python 安装目录 |

### 虚拟环境管理

| 命令 | 作用 |
|------|------|
| `uv venv` | 创建虚拟环境 |
| `uv venv --python 3.12` | 用指定 Python 版本创建虚拟环境 |

### 依赖管理

| 命令 | 作用 |
|------|------|
| `uv add 包名` | 添加运行时依赖 |
| `uv add --dev 包名` | 添加开发依赖 |
| `uv remove 包名` | 删除依赖 |
| `uv sync` | 同步依赖（按 pyproject.toml + uv.lock） |
| `uv lock` | 生成/更新 uv.lock |
| `uv pip list` | 查看已安装的包 |
| `uv tree` | 查看依赖树 |

### 项目运行

| 命令 | 作用 |
|------|------|
| `uv run python xxx.py` | 在虚拟环境中运行 Python 脚本 |
| `uv run pytest` | 运行测试 |
| `uv run 命令` | 在虚拟环境中运行任意命令 |

### 项目初始化

| 命令 | 作用 |
|------|------|
| `uv init 项目名` | 初始化新项目 |
| `uv init --lib 库名` | 初始化库项目 |
| `uv build` | 构建项目（生成 .whl / .tar.gz） |

### 环境变量与目录查看

| 命令 | 作用 |
|------|------|
| `uv python dir` | 查看 Python 安装目录 |
| `uv tool dir` | 查看工具环境目录 |
| `uv tool dir --bin` | 查看工具可执行文件目录 |
| `uv cache dir` | 查看缓存目录 |
| `uv cache clean` | 清理缓存 |

---

## 核心要点回顾

1. **uv 一个工具搞定 Python 一切**：版本管理 + 虚拟环境 + 依赖管理 + 锁定文件
2. **所有环境变量都可用 `setx` 或 GUI 设置**：详见第五章
3. **`uv python install` 与目录无关**：全局安装到固定位置（由 `UV_PYTHON_INSTALL_DIR` 决定）
4. **每个项目独立指定 Python 版本**：用 `uv python pin`，生成 `.python-version`
5. **不需要手动激活虚拟环境**：用 `uv run` 自动处理
6. **不混用工具**：uv 项目中不用 pip、不用 conda
7. **pyproject.toml + uv.lock 提交 git，.venv 不提交**
8. **`uv sync` 是团队协作的核心**：保证环境一致

---

> **更多信息**：
> - uv 官方环境变量文档：https://docs.astral.sh/uv/reference/environment/
> - uv 官方存储目录文档：https://docs.astral.sh/uv/reference/storage/
> - uv 官方文档：https://docs.astral.sh/uv/
> - uv GitHub：https://github.com/astral-sh/uv
