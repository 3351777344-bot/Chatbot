# Git 命令与操作教学

> **版本**：v1.1（纯净版）  
> **日期**：2026-06-24  
> **适用项目**：langchain-chat（LangChain 多轮会话项目）

---

## 一、Git 是什么（What）

**一句话定义**：Git 是一个**分布式版本控制系统**，它像一个"时光机"，记录你的项目每一刻的状态，让你可以随时回到过去的任何一个版本。

### 核心概念

Git 管理你的项目文件，通过三个区域协作：

```
你的项目文件夹
      │
      ▼
  ┌───────────┐
  │ Working   │  ← 你正在编辑的文件（工作区）
  │ Directory  │
  └─────┬─────┘
        │ git add
        ▼
  ┌───────────┐
  │ Staging   │  ← 暂存区（你标记了"要提交"的文件）
  │ Area      │
  └─────┬─────┘
        │ git commit
        ▼
  ┌───────────┐
  │ Repository│  ← 本地仓库（版本历史记录，存在 .git/ 文件夹中）
  │ (.git/)   │
  └───────────┘
```

### 四个关键概念

| 概念 | 比喻 | 说明 |
|------|------|------|
| **Working Directory（工作区）** | 你的办公桌 | 你正在编辑的文件，直接看得到、改得到 |
| **Staging Area（暂存区）** | 待寄出的包裹 | 你用 `git add` 把文件放进去，表示"这些改动我要提交" |
| **Repository（仓库）** | 保险柜 | 你用 `git commit` 把暂存区的东西存进去，形成一个"版本快照" |
| **Commit（提交）** | 一张照片 | 每次 commit 就是给项目拍了一张"快照"，记录了那一刻的完整状态 |

---

## 二、为什么要用 Git（Why）

### 没有 Git 的世界

```
project_final.py
project_final_v2.py
project_final_v2_fix.py
project_final_v2_fix_real.py
project_final_v2_fix_real_final.py    ← 你懂的...
```

### 有 Git 的世界

```
project.py          ← 永远只有一个最新文件
                    ← 但你可以随时查看任何历史版本
                    ← 改坏了？一条命令回到上个版本
```

### 对我们项目的价值

| 场景 | 没有 Git | 有 Git |
|------|----------|--------|
| Step 7 改坏了代码 | 手动恢复，可能漏掉改动 | `git checkout step-6-chat-engine` 一键回到 Step 6 |
| 想看 Step 4 的代码是什么样的 | 找不到（已被覆盖） | `git checkout step-4-user-mgmt` 瞬间切换 |
| 想对比 Step 5 和 Step 8 的差异 | 不可能 | `git diff step-5-presets step-8-session-mgmt` |
| 想看看整个项目的演进历程 | 靠记忆 | `git log --oneline` 看完整历史 |

---

## 三、为什么选 Git（Which）

| 工具 | 类型 | 优劣 | 适用场景 |
|------|------|------|----------|
| **Git** | 分布式版本控制 | 免费、无中心依赖、速度快、社区庞大 | **行业标准，企业必备** |
| SVN | 集中式版本控制 | 依赖中央服务器、离线不能用 | 老项目维护 |
| 手动备份 | 复制文件夹 | 无历史追溯、容易混乱 | 个人临时小项目 |
| Mercurial | 分布式 | 社区小、生态弱 | 少数企业内部 |

**结论：Git 是唯一合理的选择，是软件开发的事实标准。**

---

## 四、Git 基本操作（How）

### 4.1 初始化仓库（Step 1 使用）

```bash
git init                          # 在项目根目录执行，创建 .git/ 文件夹
git add .                          # 把所有文件加入暂存区
git status                         # 查看暂存区状态（哪些文件将被提交）
git commit -m "feat: step 1 - 项目初始化"    # 提交到仓库
git tag step-1-init                # 打标签，标记里程碑
```

### 4.2 每个开发步骤（Step 2 ~ Step 14 使用）

```bash
# 第一步：查看当前修改了什么
git status                         # 查看文件修改状态
git diff                           # 查看具体改动内容

# 第二步：将修改加入暂存区
git add .                          # 暂存所有修改
# 或选择性暂存：
git add src/core/chat_engine.py    # 只暂存指定文件

# 第三步：提交到仓库
git commit -m "feat: step X - 功能描述"     # 提交

# 第四步：打标签
git tag step-X-xxx                 # 打标签标记里程碑
```

### 4.3 查看历史和标签

```bash
git log --oneline                  # 查看提交历史（简短版，一行一个 commit）
git log                            # 查看详细历史
git tag                            # 查看所有标签（里程碑）
git show step-5-presets            # 查看某个标签对应的提交详情
```

### 4.4 回退到某个步骤

```bash
# 方式一：查看某个步骤的代码（不影响当前工作）
git checkout step-5-presets        # 切换到 Step 5 的状态
# 此时你可以查看代码，但不在 main 分支

# 回到最新状态
git checkout main                  # 回到最新开发状态
```

### 4.5 查看差异

```bash
# 对比两个步骤的代码差异
git diff step-4-user-mgmt step-5-presets    # 对比 Step 4 和 Step 5

# 查看当前工作区的修改（未暂存的）
git diff

# 查看暂存区的修改（已 git add 但未 commit 的）
git diff --staged
```

### 4.6 撤销操作

```bash
# 撤销工作区修改（未 git add 的）— 危险操作，会丢失修改！
git checkout -- <file>             # 撤销指定文件的修改
git checkout -- .                  # 撤销所有文件的修改

# 从暂存区撤出（已 git add 但未 commit 的）
git restore --staged <file>        # 撤出指定文件
git restore --staged .             # 撤出所有文件

# 修改最近一次 commit（改 commit message 或补充文件）
git commit --amend                 # 修改最近一次 commit
```

---

## 五、本项目中的 Git 工作流程

### 5.1 Commit Message 规范

我们使用企业级 commit message 规范：

```
<类型>: step <编号> - <简要描述>
```

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: step 7 - TUI 对话视图对接` |
| `fix` | 修复 bug | `fix: step 8 - 修复会话标题截断问题` |
| `docs` | 文档变更 | `docs: step 14 - 完善架构文档` |
| `refactor` | 重构 | `refactor: step 12 - 重构存储工厂` |
| `style` | 代码格式（不影响功能） | `style: step 3 - 统一导入顺序` |
| `test` | 测试相关 | `test: step 13 - 添加存储层单元测试` |
| `chore` | 构建/工具变更 | `chore: step 1 - 初始化 pyproject.toml` |

### 5.2 Tag 命名规范

```
step-<编号>-<简短标识>
```

| Tag | 对应步骤 |
|-----|----------|
| `step-1-init` | 项目初始化 |
| `step-2-skeleton` | 数据模型 + TUI 骨架 |
| `step-3-sqlite` | SQLite 后端 |
| `step-4-user-mgmt` | 用户管理 |
| `step-5-presets` | 预设管理 |
| `step-6-chat-engine` | 对话引擎 |
| `step-7-first-chat` | 第一次真实对话（核心里程碑） |
| `step-8-session-mgmt` | 会话管理完善 |
| `step-9-search` | 对话搜索 |
| `step-10-export-switch` | 导出 + 模型切换 |
| `step-11-mysql` | MySQL 后端 |
| `step-12-logging-file` | File 后端 + 日志 |
| `step-13-tests` | 单元测试 |
| `step-14-docs-extend` | 文档 + 扩展预留 |

### 5.3 完整工作流程图

```
Step 1  → commit + tag step-1-init
Step 2  → commit + tag step-2-skeleton
Step 3  → commit + tag step-3-sqlite
Step 4  → commit + tag step-4-user-mgmt
Step 5  → commit + tag step-5-presets
Step 6  → commit + tag step-6-chat-engine
Step 7  → commit + tag step-7-first-chat      [核心里程碑]
Step 8  → commit + tag step-8-session-mgmt
Step 9  → commit + tag step-9-search
Step 10 → commit + tag step-10-export-switch
Step 11 → commit + tag step-11-mysql
Step 12 → commit + tag step-12-logging-file
Step 13 → commit + tag step-13-tests
Step 14 → commit + tag step-14-docs-extend    [项目完成]
```

---

## 六、重要注意事项

| 事项 | 说明 |
|------|------|
| **不要 commit .env** | API Key 等敏感信息不能进入版本库，已在 .gitignore 中排除 |
| **不要 commit data/** | 运行时数据不入版本库，已在 .gitignore 中排除 |
| **不要 commit __pycache__/** | Python 缓存文件不入版本库，已在 .gitignore 中排除 |
| **不要 commit .venv/** | 虚拟环境不入版本库，已在 .gitignore 中排除 |
| **每步 commit 前检查** | 用 `git status` 查看将要提交的文件，确保没有误提交 |
| **tag 是里程碑** | tag 就像照片上的书签，方便快速跳转到某个版本 |
| **checkout 只看不改** | `git checkout step-X` 只是"看一眼"，不会删除后续步骤的代码 |
| **amend 谨慎使用** | `git commit --amend` 只应在尚未 push 时使用 |

---

## 七、常用 Git 命令速查表

| 命令 | 用途 | 使用场景 |
|------|------|----------|
| `git init` | 初始化仓库 | 项目开始时执行一次 |
| `git add .` | 暂存所有修改 | 每步开发完成后 |
| `git add <file>` | 暂存指定文件 | 只想提交部分文件 |
| `git status` | 查看状态 | 提交前检查 |
| `git diff` | 查看修改内容 | 提交前检查 |
| `git commit -m "..."` | 提交 | 每步完成后 |
| `git commit --amend` | 修改上次 commit | 发现上次提交有遗漏 |
| `git tag <name>` | 打标签 | 每个 commit 后标记里程碑 |
| `git tag` | 查看所有标签 | 查看可用版本 |
| `git log --oneline` | 查看历史 | 了解项目演进 |
| `git checkout <tag>` | 切换到某版本 | 查看历史代码 |
| `git checkout main` | 回到最新 | 看完历史后回到主线 |
| `git diff <tag1> <tag2>` | 对比两个版本 | 查看某两步之间的差异 |
| `git restore --staged <file>` | 从暂存区撤出 | 误 git add 后撤回 |
| `git checkout -- <file>` | 丢弃工作区修改 | 改坏了想重来（慎用） |
