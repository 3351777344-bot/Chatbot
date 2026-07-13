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
| Step 9 对话搜索 | 已验收 | 当前用户关键词搜索、结果分组与原始记录查看测试 | `step-9-search` |
| Step 10 导出与模型切换 | 已验收 | Markdown 导出、默认模型和会话模型白名单切换测试 | `step-10-export-switch` |
| Step 11 MySQL 后端 | 已实现 | 全接口/建表 SQL/工厂构造验证；真实连接需外部 MySQL | `step-11-mysql` |
| Step 12 File 后端与日志 | 已验收 | File 全 CRUD/重载/级联测试；JSON 日志解析测试 | `step-12-logging-file` |
| Step 13 单元测试 | 已验收 | `APP_ENV=test uv run pytest`（当前 13 passed） | `step-13-tests` |
| Step 14 文档与扩展预留 | 已验收 | README/架构文档链接及 UI 扩展协议导入检查 | `step-14-docs-extend` |
| Step 15 多环境配置 | 已验收 | dev 业务链、test 13 tests、prod MySQL 构造模拟与密钥/数据隔离 | `step-15-envs` |

最后更新：2026-07-13。

## 最终交付核验

- `APP_ENV=dev`：TUI 启动通过；SQLite 位于 `data/dev/`；模拟对话与导出链路通过。
- `APP_ENV=test`：独立 SQLite 配置生效，13 项离线测试全部通过。
- `APP_ENV=prod`：MySQL 配置、后端接口、建表 SQL 和工厂构造通过；真实连接需要外部实例。
- Git：`step-1-init` 至 `step-15-envs` 共 15 个标签均存在。
- 安全：真实 `.env*`、数据库、导出物和日志均未被 Git 追踪。

## 已知限制

- 本地环境未提供 MySQL 服务，因此 Step 11/15 的生产后端只完成构造模拟，未执行真实连通测试。
- Markdown 导出当前文件名为“安全化标题 + 会话 ID”，与原需求中“标题 + 日期”的建议格式不同；
  存储目录仍由各环境 `export.dir` 隔离配置。
- WebUI、多模型并行、图文、语音和 Tool Calling 当前仅预留协议接口。
