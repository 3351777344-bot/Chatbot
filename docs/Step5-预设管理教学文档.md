# Step 5：预设管理模块与 TUI 预设菜单（教学文档）

> 文档版本：v1.0
> 编写日期：2026-06-25
> 适用对象：Python 与工程化开发的初学者
> 配套项目：langchain-chat（LangChain 多轮会话教学项目）
> 配套标签：`step-5-presets`

---

## 阅读说明

本文档是 langchain-chat 项目第五步的完整教学手册。阅读并跟随操作后，你应当能够：

1. 理解预设管理的设计（系统内置预设 + 用户自定义预设）。
2. 掌握从 YAML 文件加载数据到数据库的方法。
3. 理解「幂等导入」的概念与实现（启动时导入，重复不报错）。
4. 掌握 read_text 支持默认值（回车保留）的改造方法。
5. 理解业务层的权限控制（内置只读、自定义可增删改、操作需登录）。
6. 体验一次真实的 bug 发现与修复过程（Step 3 遗留的 save_preset 缺陷）。

**本文档的设计原则**（与前四步文档一致）：

- 每一个概念都用「3W1H」框架讲解。
- 每一个操作都给出可直接复制的命令，并说明预期结果。
- 文件内容以代码块形式给出，自行创建文件并粘贴（其实应该手写输入）内容。
- 每完成若干文件后设有「验证检查点」，便于及时发现问题。

**完成标志（学完本文档后你应达成的目标）**：

- 新增 `src/core/preset_manager.py`（预设管理业务层）。
- 改造 `src/ui/tui/widgets.py`（read_text 支持默认值）。
- 改造 `src/ui/tui/app.py`（实现预设管理子菜单，替换桩函数）。
- 改造 `src/main.py`（启动时导入内置预设）。
- 修复 `src/storage/sqlite_backend.py`（save_preset 的 bug）。
- 执行 `uv run python src/main.py`，能在 TUI 中查看、新增、编辑、删除预设。
- 本地 Git 仓库存在提交与标签 `step-5-presets`，并推送到 Gitee。

---

## 目录

- [一、本步骤概述](#一本步骤概述)
- [二、前置回顾](#二前置回顾)
- [三、核心概念讲解（3W1H）](#三核心概念讲解3w1h)
- [四、动手实践：创建与改造源码](#四动手实践创建与改造源码)
- [五、整体运行验证](#五整体运行验证)
- [六、版本控制](#六版本控制)
- [七、常见问题与排查](#七常见问题与排查)
- [八、本步骤小结与知识清单](#八本步骤小结与知识清单)

---

## 一、本步骤概述

### 1.1 我们要做什么

Step 4 实现了用户管理。Step 5 实现预设管理——让用户能选择不同的 AI 角色（翻译助手、代码专家等）来对话。

预设分两类：

- **系统内置预设**：存在 `config/presets.yaml`，所有用户共享，只读（不能改不能删）。本步骤要在启动时把它们导入数据库。
- **用户自定义预设**：用户自己创建的，可增删改，归属当前用户。

本步骤做五件事：

1. 新建 `PresetManager`（core/preset_manager.py），封装预设的业务逻辑。
2. 改造 `widgets.py`，让 read_text 支持默认值（回车保留原值），为编辑功能服务。
3. 改造 `app.py`，实现预设管理子菜单（查看/新增/编辑/删除），替换 Step 2 的桩函数。
4. 改造 `main.py`，启动时导入内置预设。
5. 修复 Step 3 遗留的 `save_preset` bug。

### 1.2 本步骤的特殊之处：发现并修复一个历史 bug

在开发 Step 5 的过程中，会发现 Step 3 的 `sqlite_backend.py` 里 `save_preset` 方法有一个缺陷——它判断「新增还是更新」的逻辑有问题，导致预设无法正确写入数据库。

这个 bug 在 Step 3 没被发现，因为 Step 3 的冒烟测试只测了 user/session/message，没测 preset。本步骤会暴露并修复它。这是一个很好的真实案例，说明「测试覆盖的重要性」和「渐进式开发中问题如何随步骤暴露」。详见第三章 3.5 节。

### 1.3 本步骤的输入与输出

| 项目 | 内容 |
|------|------|
| 输入 | Step 4 完成的用户管理（标签 step-4-user-mgmt） |
| 输出 | 预设管理完整功能（业务层 + 界面层 + 内置预设导入） |
| MVP 验证点 | 在 TUI 中查看内置预设、新增/编辑/删除自定义预设 |

### 1.4 本步骤产出的文件

```
langchain-chat/
├── src/
│   ├── core/
│   │   └── preset_manager.py       预设管理业务层（新建）
│   ├── storage/
│   │   └── sqlite_backend.py       save_preset bug 修复（改造）
│   ├── ui/tui/
│   │   ├── app.py                  预设管理子菜单（改造）
│   │   └── widgets.py             read_text 支持默认值（改造）
│   └── main.py                     启动时导入内置预设（改造）
```

共新建 1 个文件，改造 4 个文件。无新依赖。

### 1.5 本步骤的设计决策（已确认）

| 决策 | 选择 | 理由 |
|------|------|------|
| 内置预设加载时机 | 启动时导入（幂等，已存在不重复） | 用户无感，一次导入永久有效 |
| 选择功能放哪 | 留到 Step 7（会话创建时选预设） | 本步骤专注预设管理本身 |
| 编辑实现方式 | 提示当前值，回车保留或输入新值 | 编辑体验好 |
| 内置预设权限 | 只读（不能改不能删） | 保护全局共享性 |
| 自定义预设归属 | 关联当前登录用户 | 数据归属明确，操作需先登录 |

---

## 二、前置回顾

### 2.1 Step 4 回顾

| 已完成 | 结论 |
|--------|------|
| 用户管理 | 创建/列出/切换/删除全部可用，数据持久化 |
| 业务层模式 | UserManager 通过依赖注入接收 backend |
| 应用状态 | current_user 维护在 TUIApp |
| 当前短板 | 预设管理仍是桩函数，内置预设未导入 |

### 2.2 本步骤不需要新依赖

复用前面步骤已安装的库（pyyaml 用于读 YAML、pydantic 等），无需安装新库。

---

## 三、核心概念讲解（3W1H）

### 3.1 预设的两类设计（内置 + 自定义）

**What（是什么）**

预设（Preset）是「预定义的 AI 角色」，核心是一个 system_prompt（系统提示词），告诉 AI 它应该扮演什么角色。本项目预设分两类：

| 类型 | 来源 | 归属 | 权限 |
|------|------|------|------|
| 系统内置 | config/presets.yaml 导入 | 全体用户共享（user_id=NULL） | 只读 |
| 用户自定义 | 用户在 TUI 里创建 | 当前用户（user_id=具体值） | 可增删改 |

**Why（为什么分两类）**

- 内置预设保证「开箱即用」：用户不需要自己写提示词就能用翻译助手、代码专家等常用角色。
- 自定义预设提供「灵活扩展」：用户可以为自己的特殊需求定制角色（如「简历优化师」「健身教练」）。
- 内置只读保护全局共享性：如果允许改内置，一个用户的修改会影响所有人，造成混乱。

**How（本项目怎么实现）**

- 内置预设存在 `config/presets.yaml`（Step 1 已创建，含 5 个角色），启动时导入数据库，is_builtin=True。
- 自定义预设由用户在 TUI 里创建，存数据库，is_builtin=False。
- 数据库查询时，`list_presets(user_id)` 返回「所有内置 + 该用户的自定义」。
- 内置预设的删除/编辑操作会被业务层拒绝（抛 ValueError）。

### 3.2 幂等导入（启动时加载内置预设）

**What（是什么）**

幂等导入指：每次程序启动都执行导入操作，但「已存在的不会重复导入」。结果与执行一次相同。

**Why（为什么需要幂等）**

程序会被反复启动。如果每次启动都把 5 个内置预设重新插入一遍，数据库里会有大量重复（启动 10 次就有 50 条「翻译助手」）。幂等导入保证「无论启动多少次，内置预设始终只有一份」。

**How（怎么实现幂等）**

在导入前，先查询数据库里已存在的内置预设名（一个集合），导入时跳过名字已存在的：

```python
existing_names = await self._get_builtin_preset_names()   # 已存在的名字集合
for item in data["presets"]:
    if item["name"] in existing_names:
        continue    # 已存在，跳过
    await self.backend.save_preset(preset)                # 不存在才插入
```

### 3.3 read_text 支持默认值（回车保留）

**What（是什么）**

改造 widgets.py 的 read_text 函数，让它支持「默认值」参数。当传入默认值时，提示中显示当前值，用户直接回车则保留默认值，输入新值则覆盖。

**Why（为什么需要）**

编辑预设时，用户可能只想改其中一个字段（比如只改 description，name 和 system_prompt 不变）。如果没有默认值功能，用户必须把所有字段重新输入一遍，体验很差。有了默认值，用户回车就能保留原值，只改想改的。

**How（怎么改造）**

```python
def read_text(prompt_text: str, default: str = "") -> str:
    if default:
        raw = input(f"{prompt_text}（当前: {default}，回车保留）: ").strip()
        return raw if raw else default    # 用户没输入就返回默认值
    else:
        return input(f"{prompt_text}: ").strip()
```

关键逻辑：`return raw if raw else default`。如果用户输入了内容（raw 非空），返回用户输入；如果用户直接回车（raw 为空），返回默认值。

### 3.4 业务层的权限控制

**What（是什么）**

PresetManager 在执行增删改前，检查权限：

- 内置预设：拒绝修改、拒绝删除（抛 ValueError）。
- 自定义预设：只允许归属用户操作。
- 所有写操作：要求当前已登录（current_user 不为 None）。

**Why（为什么在业务层控制）**

权限控制是业务规则，不是存储规则。存储层（SQLiteBackend）只管「怎么存」，不管「该不该存」。业务层（PresetManager）负责判断「这个操作是否被允许」。

**How（怎么实现）**

```python
async def delete_preset(self, preset_id: int) -> None:
    preset = await self.get_preset(preset_id)
    if preset.is_builtin:
        raise ValueError("内置预设不允许删除")    # 业务规则
    await self.backend.delete_preset(preset_id)
```

界面层捕获 ValueError，显示友好错误。

### 3.5 一个真实 bug 的发现与修复（save_preset）

**背景**

Step 3 的 `sqlite_backend.py` 里，`save_preset` 方法用 `if preset.id is None` 判断「新增还是更新」：

```python
async def save_preset(self, preset: Preset) -> Preset:
    if preset.id is None:       # ← 这里有问题
        # 新增（INSERT）
    else:
        # 更新（UPDATE WHERE id=?）
```

**Bug 的表现**

在 Step 5 开发时，导入内置预设发现数据写不进数据库。排查发现：

- 创建 Preset 对象时写 `Preset(id=0, ...)`，id 的值是 `0`。
- `0 is None` 的结果是 `False`（0 和 None 是不同的值）。
- 于是 save_preset 走进了「更新」分支（UPDATE WHERE id=0）。
- 但数据库里没有 id=0 的记录，UPDATE 影响零行，什么都没发生。

**为什么会漏测**

Step 3 的 init_db.py 冒烟测试只测了 user、session、message 三个实体的增删改查，没有测 preset 的 save_preset。所以这个 bug 在 Step 3 没暴露，潜伏到 Step 5 才被发现。

这印证了 Step 3 文档里讲过的：「冒烟测试不追求覆盖所有情况，只追求核心链路畅通」。同时也说明了「测试覆盖」的重要性——没被测到的代码，可能藏着 bug。

**修复方法**

把判断条件从 `if preset.id is None` 改为 `if not preset.id`：

```python
async def save_preset(self, preset: Preset) -> Preset:
    if not preset.id:           # ← 修复后（id 为 None 或 0 都视为新增）
        # 新增（INSERT）
    else:
        # 更新（UPDATE WHERE id=?）
```

`not preset.id` 在 id 为 None、0、空字符串等「假值」时都为 True，符合「未分配真实 id 就视为新增」的语义。

**教训与启发**

1. 边界值要小心：`id=0` 和 `id=None` 是不同的，但业务上都表示「还没分配」。
2. 测试覆盖要全面：每个实体的核心方法都应该被测到（Step 13 的单元测试会更系统地覆盖）。
3. 渐进式开发的价值：每一步都验证，问题能及时暴露，不会积累到最后大爆发。

---

## 四、动手实践：创建与改造源码

下面依次完成 5 个改动（1 个新建，4 个改造）。每个给出完整内容与讲解。

> 文件位置约定：源码在 `src/` 下。文件编码统一 UTF-8（不带 BOM）。
>
> import 约定：相对于 src 目录。
>
> PyCharm 提示：创建文件时如果弹出「是否加入 Git 追踪」，选「不添加」，最后统一 git add。

### 4.1 修复 src/storage/sqlite_backend.py（save_preset bug）

文件路径：`langchain-chat/src/storage/sqlite_backend.py`（Step 3 已创建，本步骤修复一个方法）。

**这是本步骤要做的第一件事——先修 bug，否则后续预设功能都无法工作。**

找到 `save_preset` 方法（在「预设相关」注释段下方），把第一行的判断条件改掉。

**修改前**：

```python
    async def save_preset(self, preset: Preset) -> Preset:
        if preset.id is None:
            # 新增
```

**修改后**：

```python
    async def save_preset(self, preset: Preset) -> Preset:
        if not preset.id:
            # 新增（id 为 None 或 0 都视为新增）
```

只需改这一行（把 `preset.id is None` 改为 `not preset.id`，并更新注释）。其余 INSERT 和 UPDATE 的代码都不用动。

#### 验证检查点 A：bug 是否修复

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys, asyncio; sys.path.insert(0,'src'); from models.schemas import Preset; from storage.sqlite_backend import SQLiteBackend; 
async def t():
    b = SQLiteBackend('data/sqlite/_test.db'); await b.initialize()
    p = await b.save_preset(Preset(id=0, user_id=None, name='测试', system_prompt='你'));
    print('保存返回 id:', p.id);
    import aiosqlite
    async with b._conn.execute('SELECT COUNT(*) FROM presets') as c:
        r = await c.fetchone()
    print('presets 表记录数:', r[0])
    await b.close()
asyncio.run(t())"
```

**特别说明：**

上述代码，在 cmd 命令行下，无法直接执行，主要原因：cmd不支持多行解析、引号冲突死锁、中文编码崩溃(GBK vs UTF-8)。解决方案：

方法一：转换为 cmd 专属单行压缩命令行，如下：

```bash
uv run python -c "import sys,asyncio; sys.path.insert(0,'src'); from models.schemas import Preset; from storage.sqlite_backend import SQLiteBackend; exec('async def t():\n    b=SQLiteBackend(\'data/sqlite/_test.db\')\n    try:\n        await b.initialize()\n        p=await b.save_preset(Preset(id=0,user_id=None,name=\'测试\',system_prompt=\'你\'))\n        print(\'保存返回 id:\', p.id)\n        async with b._conn.execute(\'SELECT COUNT(*) FROM presets\') as c:\n            r=await c.fetchone()\n        print(\'presets 表记录数:\', r[0])\n    finally:\n        await b.close()'); asyncio.run(t())"
# 因为里面有 async def 和缩进，不能简单把所有行用分号拼起来。正确做法是：在 python -c 里用 exec('...\n...') 动态定义异步函数。
# 特别讲解：将 多行的Python脚本改换为 cmd 中可以运行的单行命令
# 1. Windows CMD 外层用双引号 "..."
# 2. Python exec 内层用单引号 '...'
# 3. exec 内部需要换行和缩进，所以用 \n 和空格
# 4. 内部字符串里的单引号要写成 \'
# 5. async def 不能直接靠分号压成普通一行，必须通过 exec 或临时脚本处理
# 6. 如果 CMD 显示中文乱码，可以先执行：chcp 65001
```

方法二：创建测试脚本并运行（企业生产环境的最佳实践，但是此处因为是教学项目，不采用此方法），如下：

Step 1: 在当前项目根目录下物理创建一个测试脚本(\test_preset.py)：

```python
# test_preset.py
import sys
import asyncio

# 将 src 物理注入解释器检索路径
sys.path.insert(0, 'src')

from models.schemas import Preset
from storage.sqlite_backend import SQLiteBackend

async def t():
    # 初始化本地 SQLite 沙箱隔离数据库
    b = SQLiteBackend('data/sqlite/_test.db')
    
    try:
        await b.initialize()

        # 执行持久化数据注入
        p = await b.save_preset(Preset(id=0, user_id=None, name='测试', system_prompt='你'))
        print('保存返回 id:', p.id)

        # 物理打捞 presets 表的记录总数进行数据完整性验证
        # 查询 presets 表的记录总数，验证数据完整性
        import aiosqlite
        async with b._conn.execute('SELECT COUNT(*) FROM presets') as c:
            r = await c.fetchone()
        print('presets 表记录数:', r[0])
    finally:
	    # 优雅关闭物理连接流：确保无论是否报错，都关闭 SQLite 连接
    	await b.close()

if __name__ == '__main__':
    asyncio.run(t())
```

Step 2: 在 Windows CMD 中运行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python test_preset.py
```

预期输出（id 不为 0，记录数为 1）：

```
保存返回 id: 1
presets 表记录数: 1
```

如果 id 仍为 0 且记录数为 0，说明 bug 没修复，重新检查 save_preset 的判断条件。

验证后清理测试数据库：

```bash
del data\sqlite\_test.db
```

或者，严格点，如果每次运行前清理旧测试库，可以先执行：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
if exist data\sqlite\_test.db del data\sqlite\_test.db
uv run python test_preset.py
```



---

### 4.2 创建 src/core/preset_manager.py（业务层）

文件路径：`langchain-chat/src/core/preset_manager.py`。

这是预设管理的业务层，封装：加载内置预设、列出预设、创建/编辑/删除自定义预设、权限控制。

**设计说明**：

- load_builtin_presets：从 YAML 读取，基于 name 去重（幂等导入）。
- create_preset/update_preset/delete_preset：校验参数和权限（内置只读），出错抛 ValueError。
- get_preset：按 id 查询单个预设（用于编辑/删除前查找）。

**文件内容**：

```python
"""预设管理业务层。

封装预设相关的业务逻辑：加载内置预设、查看、新增、编辑、删除。
对应需求文档 D1 至 D4（预设 Prompt 管理）。

设计说明：
    - 系统内置预设（is_builtin=True）从 config/presets.yaml 导入，只读，所有用户共享。
    - 用户自定义预设（is_builtin=False）可增删改，归属当前用户。
    - 列出预设时，合并显示内置预设和当前用户的自定义预设。
"""

from pathlib import Path
from typing import Optional

import yaml

from models.schemas import Preset
from storage.base import StorageBackend


class PresetManager:
    """预设管理器。

    通过传入的 StorageBackend 实例操作数据。
    使用方式：
        mgr = PresetManager(backend)
        await mgr.load_builtin_presets()   # 启动时导入内置预设
        presets = await mgr.list_presets(user_id)
    """

    # 内置预设 YAML 文件路径（相对于运行目录）
    BUILTIN_PRESETS_FILE = "config/presets.yaml"

    def __init__(self, backend: StorageBackend):
        self.backend = backend

    # ── 内置预设加载 ──────────────────────────────────────────────────────

    async def load_builtin_presets(self) -> int:
        """从 config/presets.yaml 导入系统内置预设。

        幂等：基于 name 去重，已存在的同名内置预设不重复导入。
        返回：本次新导入的预设数量。
        """
        # 1. 读取 YAML 文件
        path = Path(self.BUILTIN_PRESETS_FILE)
        if not path.exists():
            print(f"[预设] 内置预设文件 {self.BUILTIN_PRESETS_FILE} 不存在，跳过导入")
            return 0

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "presets" not in data:
            print(f"[预设] 内置预设文件格式异常，无 presets 字段")
            return 0

        # 2. 查询已存在的内置预设名（用于去重）
        existing_builtin = await self._get_builtin_preset_names()

        # 3. 逐个导入（跳过已存在的）
        imported = 0
        for item in data["presets"]:
            name = item.get("name", "").strip()
            if not name or name in existing_builtin:
                continue    # 名字为空或已存在，跳过

            preset = Preset(
                id=0,
                user_id=None,                     # None 表示系统内置
                name=name,
                description=item.get("description", ""),
                system_prompt=item.get("system_prompt", ""),
                is_builtin=True,
            )
            await self.backend.save_preset(preset)
            imported += 1

        return imported

    async def _get_builtin_preset_names(self) -> set[str]:
        """获取已存在的内置预设名集合（用于去重）。

        内置预设 user_id 为 None，不属于任何用户。
        这里传 user_id=0（不存在的用户），list_presets 会返回所有内置预设。
        """
        all_presets = await self.backend.list_presets(user_id=0)
        return {p.name for p in all_presets if p.is_builtin}

    # ── 查询 ──────────────────────────────────────────────────────────────

    async def list_presets(self, user_id: int) -> list[Preset]:
        """列出内置预设 + 指定用户的自定义预设。"""
        return await self.backend.list_presets(user_id)

    async def get_preset(self, preset_id: int) -> Optional[Preset]:
        """按 ID 查询单个预设。"""
        # 先从内置预设里找
        presets = await self.backend.list_presets(user_id=0)
        for p in presets:
            if p.id == preset_id:
                return p
        # 自定义预设需要从归属用户里找，这里简化处理返回 None
        # 调用方（app.py）会先用 list_presets 列出再让用户选 id
        return None

    # ── 用户自定义预设的增删改 ────────────────────────────────────────────

    async def create_preset(
        self, user_id: int, name: str, description: str, system_prompt: str
    ) -> Preset:
        """创建用户自定义预设（D2）。

        异常：
            ValueError: 名字为空 / system_prompt 为空 / 名字与内置预设冲突
        """
        if not name or not name.strip():
            raise ValueError("预设名不能为空")
        name = name.strip()

        if not system_prompt or not system_prompt.strip():
            raise ValueError("系统提示词不能为空")

        # 检查名字是否与内置预设冲突
        builtin_names = await self._get_builtin_preset_names()
        if name in builtin_names:
            raise ValueError(f"预设名 '{name}' 与内置预设冲突，请换个名字")

        preset = Preset(
            id=0,
            user_id=user_id,
            name=name,
            description=description.strip(),
            system_prompt=system_prompt.strip(),
            is_builtin=False,
        )
        return await self.backend.save_preset(preset)

    async def update_preset(
        self, preset: Preset, name: str, description: str, system_prompt: str
    ) -> Preset:
        """更新自定义预设。preset 必须是已有的自定义预设。

        异常：
            ValueError: 试图修改内置预设 / 名字为空 / system_prompt 为空
        """
        if preset.is_builtin:
            raise ValueError("内置预设不允许修改")

        if not name or not name.strip():
            raise ValueError("预设名不能为空")
        if not system_prompt or not system_prompt.strip():
            raise ValueError("系统提示词不能为空")

        preset.name = name.strip()
        preset.description = description.strip()
        preset.system_prompt = system_prompt.strip()
        return await self.backend.save_preset(preset)

    async def delete_preset(self, preset_id: int) -> None:
        """删除自定义预设（仅允许删除非内置的）。

        异常：
            ValueError: 试图删除内置预设
        """
        preset = await self.get_preset(preset_id)
        if preset is None:
            raise ValueError("预设不存在")

        if preset.is_builtin:
            raise ValueError("内置预设不允许删除")

        await self.backend.delete_preset(preset_id)
```

**注意：这里的 get_preset 有一个设计缺陷，会在 5.3 节的删除功能验证时暴露并修复。**

#### 验证检查点 B：PresetManager 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from core.preset_manager import PresetManager; print('PresetManager OK:', PresetManager.__name__)"
```

预期输出：`PresetManager OK: PresetManager`

---

### 4.3 改造 src/ui/tui/widgets.py（read_text 支持默认值）

文件路径：`langchain-chat/src/ui/tui/widgets.py`（Step 2 已创建，本步骤改造一个函数）。

找到 `read_text` 函数（文件末尾），替换为以下内容。

**修改前**：

```python
def read_text(prompt_text: str) -> str:
    """读取用户输入的文本。

    参数：
        prompt_text: 提示文字
    返回：
        用户输入的文本（已去除首尾空白）
    """
    return input(f"{prompt_text}: ").strip()
```

**修改后**：

```python
def read_text(prompt_text: str, default: str = "") -> str:
    """读取用户输入的文本，支持默认值（回车保留）。

    参数：
        prompt_text: 提示文字
        default: 默认值。非空时会在提示中显示当前值，用户直接回车则返回默认值
    返回：
        用户输入的文本（已去除首尾空白）；若用户回车且 default 非空，则返回 default
    """
    if default:
        # 显示当前值，提示用户可回车保留
        raw = input(f"{prompt_text}（当前: {default}，回车保留）: ").strip()
        return raw if raw else default
    else:
        return input(f"{prompt_text}: ").strip()
```

改动要点：

- 函数签名加了 `default: str = ""` 参数（默认空字符串，向后兼容）。
- 当 default 非空时，提示中显示当前值，用户回车返回 default。
- 当 default 为空时，行为和原来完全一样（不影响 Step 4 的调用）。

此外，需要改动 Step 5 的横幅显示：

**第 30 行，修改前**：

```python
    banner_text.append("\n当前进度：Step 2  数据模型与 TUI 骨架", style="yellow")
```

**修改后**（改成 Step 5）：

```python
    banner_text.append("\n当前进度：Step 5  预设管理", style="yellow")
```

---

### 4.4 改造 src/ui/tui/app.py（预设管理子菜单）

文件路径：`langchain-chat/src/ui/tui/app.py`（Step 4 已改造，本步骤继续改造）。

这是本步骤改动较大的文件。主要变化：

1. 新增 import PresetManager。
2. TUIApp 构造时创建 preset_manager。
3. 新增「预设管理子菜单」（`_show_preset_menu`），含查看/新增/编辑/删除。
4. get_user_input 方法增加 default 参数（透传给 read_text）。
5. 主菜单路由：预设管理（choice==2）改为调用 `self._show_preset_menu()`。
6. 新增辅助方法 `_require_login`（检查是否登录）。

**改造后的完整文件内容**（替换 Step 4 的 app.py 全部内容）：

```python
"""TUI 主应用（菜单路由、状态管理）。

这是 TUI 的主入口，负责：
    1. 显示启动横幅。
    2. 显示主菜单并路由到对应视图。
    3. 维护主循环（直到用户选择退出）。

Step 4 新增：
    - 持有存储后端与各业务管理器（UserManager 等）。
    - 实现用户管理子菜单（创建/列出/切换/删除）。
    - 维护当前登录用户状态。

Step 5 新增：
    - 持有 PresetManager。
    - 实现预设管理子菜单（查看/新增/编辑/删除）。

TUIApp 继承 AbstractUI，实现其全部抽象方法，满足 UI 接口契约。
"""

import platform

from core.config_manager import get_config
from core.preset_manager import PresetManager
from core.user_manager import UserManager
from interface.ui_protocol import AbstractUI
from storage.factory import StorageFactory
from ui.tui import menu_view, widgets
from ui.tui.chat_view import start_chat

# 主菜单选项（序号与选项的对应关系）
MAIN_MENU_OPTIONS = [
    "用户管理",
    "会话管理",
    "预设管理",
    "开始对话",
    "设置",
    "关于",
    "退出",
]

# 用户管理子菜单选项
USER_MENU_OPTIONS = [
    "创建用户",
    "列出所有用户",
    "切换当前用户",
    "删除用户",
    "返回主菜单",
]

# 预设管理子菜单选项
PRESET_MENU_OPTIONS = [
    "列出所有预设",
    "新增自定义预设",
    "编辑自定义预设",
    "删除自定义预设",
    "返回主菜单",
]


class TUIApp(AbstractUI):
    """TUI 主应用。

    继承 AbstractUI 并实现其全部抽象方法。
    """

    def __init__(self, backend=None) -> None:
        # 存储后端（由 main.py 注入）
        self.backend = backend
        # 业务管理器（backend 注入后初始化）
        self.user_manager: UserManager = None
        self.preset_manager: PresetManager = None
        if backend is not None:
            self.user_manager = UserManager(backend)
            self.preset_manager = PresetManager(backend)

        # 应用状态
        self.current_user = None          # 当前登录用户（User 对象或 None）
        self.current_session = None       # 当前会话（Step 7 起使用）

    # ── AbstractUI 接口实现 ───────────────────────────────────────────────

    async def display_message(self, role: str, content: str) -> None:
        """显示一条消息。"""
        if role == "human":
            widgets.console.print(f"[bold cyan][你][/] {content}")
        elif role == "ai":
            widgets.console.print(f"[bold green][AI][/] {content}")
        else:
            widgets.console.print(f"[dim][系统][/] {content}")

    async def get_user_input(self, prompt_text: str = "", default: str = "") -> str:
        """获取用户输入。"""
        return widgets.read_text(prompt_text, default=default)

    async def display_menu(self, title: str, options: list[str]) -> int:
        """显示菜单并获取选择。"""
        widgets.print_menu(title, options)
        return widgets.read_choice(len(options))

    async def display_error(self, message: str) -> None:
        """显示错误。"""
        widgets.print_error(message)

    async def display_info(self, message: str) -> None:
        """显示提示。"""
        widgets.print_info(message)

    # ── 辅助：显示当前用户状态 ────────────────────────────────────────────

    def _show_current_user(self) -> None:
        """在菜单顶部显示当前登录用户。"""
        if self.current_user:
            widgets.console.print(
                f"[dim]当前用户: [bold yellow]{self.current_user.username}[/bold yellow]"
                f"（id={self.current_user.id}）[/dim]"
            )
        else:
            widgets.console.print("[dim]当前用户: 未登录[/dim]")

    def _require_login(self) -> bool:
        """检查是否已登录。未登录则提示并返回 False。"""
        if self.current_user is None:
            widgets.print_warning("请先在用户管理中创建或切换用户")
            return False
        return True

    # ── 主循环 ────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """启动 TUI 主循环。

        流程：打印横幅 → 显示主菜单 → 读取选择 → 路由 → 循环。
        """
        # 1. 打印启动横幅
        widgets.print_banner(version="0.1.0", python_version=platform.python_version())

        # 2. 主循环
        while True:
            # 显示当前用户状态
            self._show_current_user()

            # 显示主菜单
            choice = await self.display_menu("主菜单", MAIN_MENU_OPTIONS)

            # 路由到对应视图
            if choice == -1:
                # 用户输入 0（返回上层），在主菜单中等同于不做操作
                continue
            elif choice == 0:
                await self._show_user_menu()
            elif choice == 1:
                menu_view.show_session_menu()
            elif choice == 2:
                await self._show_preset_menu()
            elif choice == 3:
                await start_chat()
            elif choice == 4:
                menu_view.show_settings_menu()
            elif choice == 5:
                menu_view.show_about()
            elif choice == 6:
                # 退出
                widgets.print_info("感谢使用，再见。")
                break

    # ── 用户管理子菜单（Step 4 实现）──────────────────────────────────────

    async def _show_user_menu(self) -> None:
        """用户管理子菜单。"""
        if self.user_manager is None:
            widgets.print_error("用户管理未初始化（存储后端未注入）")
            return

        while True:
            widgets.print_divider()
            self._show_current_user()
            choice = await self.display_menu("用户管理", USER_MENU_OPTIONS)

            if choice == -1 or choice == 4:
                # 返回主菜单
                return
            elif choice == 0:
                await self._create_user()
            elif choice == 1:
                await self._list_users()
            elif choice == 2:
                await self._switch_user()
            elif choice == 3:
                await self._delete_user()

    async def _create_user(self) -> None:
        """创建用户（B1）。"""
        username = await self.get_user_input("请输入新用户名")
        if not username:
            widgets.print_warning("未输入用户名，取消创建")
            return
        try:
            # 默认模型用配置里的默认值
            config = get_config()
            user = await self.user_manager.create_user(
                username, default_model=config.default_model
            )
            widgets.print_success(f"用户创建成功: {user.username}（id={user.id}）")
            # 创建后自动切换为当前用户（首次使用体验更好）
            if self.current_user is None:
                self.current_user = user
                widgets.print_info(f"已自动切换为当前用户: {user.username}")
        except ValueError as e:
            widgets.print_error(str(e))

    async def _list_users(self) -> None:
        """列出所有用户。"""
        users = await self.user_manager.list_users()
        if not users:
            widgets.print_info("目前没有任何用户")
            return

        widgets.console.print("\n[bold]用户列表[/bold]")
        for u in users:
            # 标记当前用户
            mark = " <- 当前" if (self.current_user and u.id == self.current_user.id) else ""
            widgets.console.print(
                f"  id={u.id}  用户名=[cyan]{u.username}[/cyan]"
                f"  模型={u.default_model or '默认'}{mark}"
            )
        widgets.print_info(f"共 {len(users)} 个用户")

    async def _switch_user(self) -> None:
        """切换当前用户（B2）。"""
        username = await self.get_user_input("请输入要切换到的用户名")
        if not username:
            widgets.print_warning("未输入用户名，取消切换")
            return

        user = await self.user_manager.get_user(username)
        if user is None:
            widgets.print_error(f"用户 '{username}' 不存在")
            return

        self.current_user = user
        widgets.print_success(f"已切换到用户: {user.username}（id={user.id}）")

    async def _delete_user(self) -> None:
        """删除用户（B3），需二次确认。"""
        username = await self.get_user_input("请输入要删除的用户名")
        if not username:
            widgets.print_warning("未输入用户名，取消删除")
            return

        user = await self.user_manager.get_user(username)
        if user is None:
            widgets.print_error(f"用户 '{username}' 不存在")
            return

        # 安全检查：不允许删除当前登录的用户
        if self.current_user and user.id == self.current_user.id:
            widgets.print_warning("不允许删除当前正在登录的用户，请先切换到其他用户")
            return

        # 二次确认
        confirm = await self.get_user_input(f"确认删除用户 '{username}'？输入 yes 确认")
        if confirm.lower() != "yes":
            widgets.print_info("已取消删除")
            return

        await self.user_manager.delete_user(user.id)
        widgets.print_success(f"用户 '{username}' 已删除（关联数据已自动清理）")

    # ── 预设管理子菜单（Step 5 实现）──────────────────────────────────────

    async def _show_preset_menu(self) -> None:
        """预设管理子菜单。"""
        if self.preset_manager is None:
            widgets.print_error("预设管理未初始化（存储后端未注入）")
            return

        while True:
            widgets.print_divider()
            self._show_current_user()
            choice = await self.display_menu("预设管理", PRESET_MENU_OPTIONS)

            if choice == -1 or choice == 4:
                # 返回主菜单
                return
            elif choice == 0:
                await self._list_presets()
            elif choice == 1:
                await self._create_preset()
            elif choice == 2:
                await self._edit_preset()
            elif choice == 3:
                await self._delete_preset()

    async def _list_presets(self) -> None:
        """列出所有预设（内置 + 当前用户的自定义）。"""
        # 查看预设不需要登录（内置预设是公开的）
        if self.current_user:
            presets = await self.preset_manager.list_presets(self.current_user.id)
        else:
            # 未登录只看内置
            presets = await self.preset_manager.list_presets(0)

        if not presets:
            widgets.print_info("目前没有任何预设")
            return

        widgets.console.print("\n[bold]预设列表[/bold]")
        for p in presets:
            tag = "[内置]" if p.is_builtin else "[自定义]"
            widgets.console.print(
                f"  id={p.id}  {tag} [cyan]{p.name}[/cyan]"
                f"  - {p.description}"
            )
        builtin_count = sum(1 for p in presets if p.is_builtin)
        custom_count = len(presets) - builtin_count
        widgets.print_info(f"共 {len(presets)} 个预设（内置 {builtin_count}，自定义 {custom_count}）")

    async def _create_preset(self) -> None:
        """新增自定义预设（D2）。"""
        if not self._require_login():
            return

        name = await self.get_user_input("请输入预设名")
        if not name:
            widgets.print_warning("未输入预设名，取消创建")
            return

        description = await self.get_user_input("请输入预设描述（可选，回车跳过）")

        system_prompt = await self.get_user_input("请输入系统提示词（定义 AI 角色）")
        if not system_prompt:
            widgets.print_warning("系统提示词不能为空，取消创建")
            return

        try:
            preset = await self.preset_manager.create_preset(
                user_id=self.current_user.id,
                name=name,
                description=description,
                system_prompt=system_prompt,
            )
            widgets.print_success(f"预设创建成功: {preset.name}（id={preset.id}）")
        except ValueError as e:
            widgets.print_error(str(e))

    async def _edit_preset(self) -> None:
        """编辑自定义预设（D2）。"""
        if not self._require_login():
            return

        # 先列出预设，让用户选
        presets = await self.preset_manager.list_presets(self.current_user.id)
        customs = [p for p in presets if not p.is_builtin]
        if not customs:
            widgets.print_info("你没有自定义预设，无法编辑（内置预设不允许修改）")
            return

        widgets.console.print("\n[bold]可编辑的自定义预设[/bold]")
        for p in customs:
            widgets.console.print(f"  id={p.id}  [cyan]{p.name}[/cyan]  - {p.description}")

        preset_id_str = await self.get_user_input("请输入要编辑的预设 id")
        try:
            preset_id = int(preset_id_str)
        except ValueError:
            widgets.print_error("请输入有效的数字 id")
            return

        # 找到对应的预设
        target = None
        for p in customs:
            if p.id == preset_id:
                target = p
                break
        if target is None:
            widgets.print_error(f"id={preset_id} 不在您的自定义预设中（或不存在）")
            return

        # 逐字段编辑（回车保留原值）
        new_name = await self.get_user_input("预设名", default=target.name)
        new_desc = await self.get_user_input("描述", default=target.description)
        new_prompt = await self.get_user_input("系统提示词", default=target.system_prompt)

        try:
            await self.preset_manager.update_preset(
                preset=target, name=new_name, description=new_desc, system_prompt=new_prompt
            )
            widgets.print_success(f"预设 '{new_name}' 已更新")
        except ValueError as e:
            widgets.print_error(str(e))

    async def _delete_preset(self) -> None:
        """删除自定义预设（D2）。"""
        if not self._require_login():
            return

        presets = await self.preset_manager.list_presets(self.current_user.id)
        customs = [p for p in presets if not p.is_builtin]
        if not customs:
            widgets.print_info("你没有自定义预设，无法删除（内置预设不允许删除）")
            return

        widgets.console.print("\n[bold]可删除的自定义预设[/bold]")
        for p in customs:
            widgets.console.print(f"  id={p.id}  [cyan]{p.name}[/cyan]  - {p.description}")

        preset_id_str = await self.get_user_input("请输入要删除的预设 id")
        try:
            preset_id = int(preset_id_str)
        except ValueError:
            widgets.print_error("请输入有效的数字 id")
            return

        # 二次确认
        confirm = await self.get_user_input(f"确认删除预设 id={preset_id}？输入 yes 确认")
        if confirm.lower() != "yes":
            widgets.print_info("已取消删除")
            return

        try:
            await self.preset_manager.delete_preset(preset_id)
            widgets.print_success(f"预设 id={preset_id} 已删除")
        except ValueError as e:
            widgets.print_error(str(e))
```

#### 验证检查点 C：app.py 能否导入

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv run python -c "import sys; sys.path.insert(0,'src'); from ui.tui.app import TUIApp; print('TUIApp OK:', TUIApp.__name__)"
```

预期输出：`TUIApp OK: TUIApp`

---

### 4.5 改造 src/main.py（启动时导入内置预设）

文件路径：`langchain-chat/src/main.py`（Step 4 已改造，本步骤继续改造）。

在「初始化存储后端」之后、「启动 TUI」之前，加一段导入内置预设的逻辑。

**改造后的完整文件内容**（替换 Step 4 的 main.py 全部内容）：

```python
"""langchain-chat 程序总入口。

Step 5 阶段：加载配置、初始化存储后端、导入内置预设、启动 TUI 主界面。
运行方式：uv run python src/main.py
"""

import asyncio
import sys
from pathlib import Path

# 将 src 目录加入模块搜索路径，确保 import 链路在任意运行方式下都工作。
# Path(__file__).resolve().parent 是 main.py 所在目录（即 src）。
sys.path.insert(0, str(Path(__file__).resolve().parent))


async def async_main() -> None:
    """异步主函数。

    启动流程（Step 5 起）：
        1. 加载配置（config_manager）
        2. 初始化存储后端（根据 config.storage_type 创建并 initialize）
        3. 导入系统内置预设（从 config/presets.yaml，幂等）
        4. 启动 TUI 主循环（把存储后端注入 TUIApp）
    """
    # 1. 加载配置（触发单例创建，读取 .env 与 config.yaml）
    from core.config_manager import get_config

    config = get_config()
    print(f"[启动] 存储后端: {config.storage_type}，默认模型: {config.default_model}")

    # 2. 初始化存储后端
    from storage.factory import StorageFactory

    backend = StorageFactory.create(config.storage_type)
    await backend.initialize()
    print(f"[启动] 存储后端已就绪: {type(backend).__name__}")

    # 3. 导入系统内置预设（幂等，已存在的不会重复导入）
    from core.preset_manager import PresetManager

    preset_manager = PresetManager(backend)
    imported = await preset_manager.load_builtin_presets()
    if imported > 0:
        print(f"[启动] 导入了 {imported} 个系统内置预设")

    # 4. 启动 TUI 主循环（注入存储后端）
    from ui.tui.app import TUIApp

    try:
        app = TUIApp(backend=backend)
        await app.run()
    finally:
        # 无论正常退出还是异常，都关闭存储后端连接
        await backend.close()
        print("[启动] 存储后端已关闭")


def main() -> None:
    """程序主函数（同步入口，内部启动异步事件循环）。"""
    asyncio.run(async_main())


# 入口守护：只有直接运行本文件时才执行，被 import 时不执行。
if __name__ == "__main__":
    main()
```

---

## 五、整体运行验证

### 5.1 准备：清理旧数据库（可选）

如果之前测试留下了数据，建议清理（如果 PyCharm 连着 app.db 先断开）：

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
rmdir /s /q data
```

### 5.2 启动程序

```bash
uv run python src/main.py
```

启动时应看到：

```
[启动] 存储后端: sqlite，默认模型: deepseek-chat
[启动] 存储后端已就绪: SQLiteBackend
[启动] 导入了 5 个系统内置预设
```

最后一行「导入了 5 个系统内置预设」说明内置预设导入成功。

### 5.3 验证操作（手动在 TUI 里操作）

**操作 1：查看内置预设**

- 主菜单选 3（预设管理）
- 选 1（列出所有预设）
- 预期：显示 5 个内置预设（通用助手、翻译助手、代码专家、创意写手、英语老师），统计「内置 5，自定义 0」

**操作 2：未登录时尝试新增预设**

- 选 2（新增自定义预设）
- 预期：显示警告「请先在用户管理中创建或切换用户」（因为还没登录）

**操作 3：创建用户并登录**

- 选 5（返回主菜单）
- 主菜单选 1（用户管理），选 1（创建用户），输入用户名 alice
- 返回主菜单

**操作 4：新增自定义预设**

- 主菜单选 3（预设管理）
- 选 2（新增自定义预设）
- 预设名：`我的私人助手`
- 描述：`贴心的私人助手`（或回车跳过）
- 系统提示词：`你是一个贴心的私人助手，主动关心用户。`
- 预期：显示「预设创建成功: 我的私人助手（id=6）」

**操作 5：再次列出预设**

- 选 1（列出所有预设）
- 预期：显示 5 个内置 + 1 个自定义（我的私人助手），统计「内置 5，自定义 1」

**操作 6：编辑自定义预设（验证回车保留）**

- 选 3（编辑自定义预设）
- 输入要编辑的预设 id（我的私人助手的 id，比如 6）
- 预设名：直接回车（保留「我的私人助手」）
- 描述：输入「更贴心的私人助手」后回车
- 系统提示词：直接回车（保留原值）
- 预期：显示「预设 '我的私人助手' 已更新」
- 再选 1 列出，确认描述已变，其他字段不变

**操作 7：尝试编辑内置预设（验证权限控制）**

- 选 3（编辑自定义预设）
- 预期：只列出可编辑的自定义预设，内置预设不在列表里（无法被选中编辑）

**操作 8：删除自定义预设**

- 选 4（删除自定义预设）
- 输入要删除的预设 id
- 输入 yes 确认
- 预期：显示「预设 id=X 已删除」
- 再选 1 列出，确认只剩 5 个内置

### 发现Bug，完成修改

#### **bug：**无法删除自定义预设。

**原因：** `get_preset` 时的缺陷——第 103-104 行：

```
# 自定义预设需要从归属用户里找，这里简化处理返回 None
# 调用方（app.py）会先用 list_presets 列出再让用户选 id
return None
```

但 `delete_preset` 方法内部调用了 `get_preset` 来检查是否是内置预设——如果 get_preset 返回 None，delete_preset 就报「预设不存在」。

设计时的逻辑漏洞：get_preset 应该能找到任意预设（内置 + 自定义），但只查了内置。

#### 解决方案

根本问题是 `list_presets(user_id=0)` 只能返回「内置预设 + user_id=0 的自定义预设」，查不到其他用户的自定义预设。需要一个能查任意预设的方法。

#### 修复方案

稳妥的方案是给存储层加一个 `get_preset_by_id` 方法（直接按 id 查，不经过 user_id 过滤）。这样 get_preset 在业务层就能正确找到任意预设。需要改 3 个文件：

1. `storage/base.py`：加抽象方法声明
2. `storage/sqlite_backend.py`：加实现
3. `core/preset_manager.py`：get_preset 改用新方法

正确的做法：存储层应该支持按 id 查询单条记录（基本能力）

##### 修复 1：storage/base.py 加抽象方法

在 base.py 的「预设相关」段（save_preset 之前），加一个方法声明：

在 base.py 第 104 行（`# ── 预设相关 ──`）和第 107 行（`save_preset`）之间，插入一个新的抽象方法。**修改方式**：

找到这一段（base.py 第 104-106 行附近）：

```python
    # ── 预设相关 ──────────────────────────────────────────────────────────

    @abstractmethod
    async def save_preset(self, preset: Preset) -> Preset:
```

改为（在 save_preset 前插入 get_preset_by_id）：

```
    # ── 预设相关 ──────────────────────────────────────────────────────────

    @abstractmethod
    async def get_preset_by_id(self, preset_id: int) -> Optional[Preset]:
        """按 ID 查询单个预设（含内置和所有用户的自定义）。不存在返回 None。"""
        ...

    @abstractmethod
    async def save_preset(self, preset: Preset) -> Preset:
```

##### 修复 2：storage/sqlite_backend.py 加实现

在 sqlite_backend.py 的「预设相关」段（save_preset 之前），加实现。

在 sqlite_backend.py 第 269 行和第 271 行之间插入实现。找到这一段：

```python
    # ── 预设相关 ──────────────────────────────────────────────────────────

    async def save_preset(self, preset: Preset) -> Preset:
```

改为：

```python
    # ── 预设相关 ──────────────────────────────────────────────────────────

    async def get_preset_by_id(self, preset_id: int) -> Optional[Preset]:
        """按 ID 查询单个预设（含内置和所有用户的自定义）。不存在返回 None。"""
        async with self._conn.execute(
            "SELECT * FROM presets WHERE id = ?", (preset_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return self._row_to_preset(row) if row else None

    async def save_preset(self, preset: Preset) -> Preset:
```

##### 修复 3：preset_manager.py 的 get_preset 改用新方法

把 preset_manager.py 的 get_preset 方法**整个替换**。找到（第 96-105 行）：

```python
    async def get_preset(self, preset_id: int) -> Optional[Preset]:
        """按 ID 查询单个预设。"""
        # 先从内置预设里找
        presets = await self.backend.list_presets(user_id=0)
        for p in presets:
            if p.id == preset_id:
                return p
        # 自定义预设需要从归属用户里找，这里简化处理返回 None
        # 调用方（app.py）会先用 list_presets 列出再让用户选 id
        return None
```

替换为：

```python
    async def get_preset(self, preset_id: int) -> Optional[Preset]:
        """按 ID 查询单个预设（含内置和所有用户的自定义）。不存在返回 None。"""
        return await self.backend.get_preset_by_id(preset_id)
```



### 5.4 验证要点

| 检查项 | 期望 | 意义 |
|--------|------|------|
| 启动时导入 5 个内置预设 | 显示「导入了 5 个系统内置预设」 | YAML 读取 + 幂等导入正确 |
| 列出预设 | 显示内置预设，未登录时也可看 | 查询正确 |
| 未登录不能新增 | 提示先登录 | 登录检查生效 |
| 新增自定义预设 | 创建成功，归属当前用户 | 业务层 + 存储层链路通（save_preset 修复生效） |
| 编辑时回车保留 | 不改的字段保持原值 | read_text 默认值功能正确 |
| 内置预设不可编辑 | 编辑列表只有自定义预设 | 权限控制生效 |
| 删除自定义预设 | 删除成功，二次确认 | 安全机制生效 |
| 重复启动 | 内置预设仍只有 5 个（不重复） | 幂等导入生效 |

### 5.5 验证幂等性（重复启动）

退出程序后，再次运行 `uv run python src/main.py`：

- 预期：**不显示**「导入了 X 个系统内置预设」（因为已存在，本次导入 0 个）。
- 进入预设管理，列出，内置预设仍只有 5 个（没有变 10 个）。

这验证了幂等导入的正确性。

---

## 六、版本控制

### 6.1 提交前检查

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
git status
```

应看到的变化：

- 新增：`src/core/preset_manager.py`
- 修改：`src/storage/sqlite_backend.py`（save_preset bug 修复 + 新增 get_preset_by_id）、`src/storage/base.py`（新增 get_preset_by_id 抽象方法）、`src/ui/tui/widgets.py`（read_text 默认值 + 进度文字改 Step 5）、`src/ui/tui/app.py`（预设子菜单）、`src/main.py`（导入内置预设）
- 可能修改：之前未提交的文档（Step 3、Step 4 文档修订）
- 不应出现：`data/`、`.env`、`.venv/`

### 6.2 提交与打标签

第 1 步：

```bash
git add .
```

第 2 步：

```bash
git status
```

第 3 步：

```bash
git commit -m "feat: step 5 - 预设管理业务层、TUI 预设菜单与内置预设导入"
```

第 4 步：

```bash
git tag step-5-presets
```

第 5 步：

```bash
git push
git push origin step-5-presets
```

第 6 步：

```bash
git log --oneline -6
git tag
```

---

## 七、常见问题与排查

### 7.1 内置预设未导入

| 现象 | 原因 | 解决 |
|------|------|------|
| 启动时没显示「导入了 5 个」 | 可能是上次已导入（幂等），本次导入 0 个 | 进预设管理列出，看是否有 5 个内置 |
| 列出预设显示「没有任何预设」 | save_preset bug 未修复 | 按 4.1 节修复 sqlite_backend.py 的 save_preset |
| 启动时报「内置预设文件不存在」 | 运行目录不对，或 config/presets.yaml 不在 | 确保在项目根目录运行 |

### 7.2 编辑/删除相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 编辑时显示「没有自定义预设」 | 当前用户确实没创建过自定义预设 | 先新增一个 |
| 删除报「内置预设不允许删除」 | 试图删内置预设（被业务层拒绝） | 内置预设不能删，只能删自定义的 |
| 编辑时输入 id 报「不在您的自定义预设中」 | id 输错或该预设不归属当前用户 | 先列出确认 id |

### 7.3 read_text 默认值相关

| 现象 | 原因 | 解决 |
|------|------|------|
| 编辑时没有显示「当前: xxx，回车保留」 | widgets.py 的 read_text 没改造 | 按 4.3 节改造 read_text 函数 |
| Step 4 的用户管理功能受影响吗 | 不受影响（default 默认空字符串，向后兼容） | 无需担心 |

---

## 八、本步骤小结与知识清单

### 8.1 产出清单

| 类别 | 产出 |
|------|------|
| 业务层 | src/core/preset_manager.py（PresetManager） |
| 存储层修复 | src/storage/sqlite_backend.py（save_preset bug 修复 + get_preset_by_id）、src/storage/base.py（get_preset_by_id 抽象方法） |
| 界面层改造 | src/ui/tui/app.py（预设子菜单）、src/ui/tui/widgets.py（read_text 默认值） |
| 入口改造 | src/main.py（启动时导入内置预设） |
| 版本控制 | 提交 feat: step 5、标签 step-5-presets |

### 8.2 知识清单

学完本步骤，应当掌握：

- 预设的两类设计（系统内置只读 + 用户自定义可增删改）。
- 从 YAML 文件加载数据到数据库的方法（PyYAML）。
- 幂等导入的实现（基于 name 去重，重复启动不重复导入）。
- read_text 支持默认值（回车保留原值）的改造方法。
- 业务层权限控制（内置只读、操作需登录）。
- 一个真实的 bug 案例（save_preset 的 `id is None` 缺陷）及其修复（`not preset.id`）。
- 边界值陷阱（`id=0` 与 `id=None` 的区别）。
- 测试覆盖的重要性（没测到的代码可能藏 bug）。

### 8.3 项目当前状态

```
langchain-chat @ step-5-presets
本地 git 仓库：已提交
Gitee 远程仓库：已推送（代码与标签）
用户管理：完整可用（Step 4）
预设管理：完整可用（查看内置/新增/编辑/删除自定义）
桩函数替换进度：用户管理、预设管理已替换；会话/对话/设置仍是桩
可运行：uv run python src/main.py 启动后可操作用户与预设管理
```

### 8.4 桩函数替换进度

| 菜单功能 | 状态 | 实现步骤 |
|---------|------|---------|
| 用户管理 | 已实现 | Step 4 |
| 预设管理 | 已实现 | Step 5（当前） |
| 会话管理 | 桩函数 | Step 7、8 |
| 开始对话 | 桩函数 | Step 7（核心里程碑） |
| 设置 | 桩函数 | Step 10 |

### 8.5 下一步预告

Step 6：对话引擎（LLM 调用 + Memory + 流式 + 超时重试 + Token 统计）。

这是项目的核心技术模块——真正调用 LangChain 与 LLM 通信。Step 6 写的是「引擎」（独立模块，用代码调用验证），不接 TUI 界面。到 Step 7 才把引擎接进 TUI，实现界面上的多轮对话。

Step 6 开始前，你需要准备一个真实的 LLM API Key（如 DeepSeek、通义千问等 OpenAI 兼容的服务），填入 .env。

---

> 本文档为 langchain-chat 项目 Step 5 的教学手册。按本文档操作，可从零独立完成预设管理的全部实现。操作过程中如遇问题，可参考第七部分排查，或随时询问。
