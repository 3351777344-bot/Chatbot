# 实施状态

本文件记录仓库实现与《实施步骤计划》的对应关系，避免教学文档、代码和 Git 标签脱节。

| Step | 状态 | 验证方式 | Git 标签 |
|---|---|---|---|
| Step 1 项目初始化 | 已验收 | `uv run python src/main.py`（Step 1 提交）与 `uv lock --check` | `step-1-init` |
| Step 2 数据模型与 TUI 骨架 | 已验收 | 模型/配置导入检查；TUI 启动后可显示并退出主菜单 | `step-2-skeleton` |
| Step 3 SQLite 存储后端 | 已验收 | `uv run python scripts/init_db.py`；CRUD/搜索/级联删除冒烟测试 | `step-3-sqlite` |
| Step 4 用户管理 | 已验收 | 业务规则自动测试；TUI 创建/列出/切换/删除 | `step-4-user-mgmt` |
| Step 5 预设管理 | 已实现 | 内置预设幂等导入；私有预设 CRUD/权限隔离测试 | `step-5-presets`（提交后创建） |
| Step 6–15 | 待实施 | 见《实施步骤计划》 | 待创建 |

最后更新：2026-07-13。
