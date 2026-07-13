# 实施状态

本文件记录仓库实现与《实施步骤计划》的对应关系，避免教学文档、代码和 Git 标签脱节。

| Step | 状态 | 验证方式 | Git 标签 |
|---|---|---|---|
| Step 1 项目初始化 | 已验收 | `uv run python src/main.py`（Step 1 提交）与 `uv lock --check` | `step-1-init` |
| Step 2 数据模型与 TUI 骨架 | 已验收 | 模型/配置导入检查；TUI 启动后可显示并退出主菜单 | `step-2-skeleton` |
| Step 3 SQLite 存储后端 | 已验收 | `uv run python scripts/init_db.py`；CRUD/搜索/级联删除冒烟测试 | `step-3-sqlite` |
| Step 4 用户管理 | 已验收 | 业务规则自动测试；TUI 创建/列出/切换/删除 | `step-4-user-mgmt` |
| Step 5 预设管理 | 已验收 | 内置预设幂等导入；私有预设 CRUD/权限隔离测试 | `step-5-presets` |
| Step 6 对话引擎 | 已验收 | 注入式假模型验证同步、流式、历史消息与 Token 统计 | `step-6-chat-engine` |
| Step 7 多轮流式对话 | 已验收 | 假模型端到端验证会话、历史、流式回复、Token 与持久化 | `step-7-first-chat` |
| Step 8 会话管理完善 | 已验收 | 列表/加载/新建/重命名/删除及跨用户权限测试 | `step-8-session-mgmt` |
| Step 9 对话搜索 | 已实现 | 当前用户关键词搜索、结果分组与原始记录查看测试 | `step-9-search`（提交后创建） |
| Step 10–15 | 待实施 | 见《实施步骤计划》 | 待创建 |

最后更新：2026-07-13。
