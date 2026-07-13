解决：uv 安装包时的下载速度优化，国内访问 PyPI 默认源确实慢。

**uv 支持配置镜像源（国内镜像），能大幅提速。** 

我来完整讲解。

---

# uv 配置国内镜像源（加速 uv add）

## 一、Why：为什么默认慢

uv 默认从 **PyPI 官方源**（`https://pypi.org`）下载包，服务器在国外，国内访问速度慢。解决办法是切换到**国内镜像源**——它们定期同步 PyPI 的全部包，服务器在国内，速度快十倍以上（嗯，我的估计...）。

## 二、Which：推荐哪个镜像源

国内主流 PyPI 镜像源对比：

| 镜像源        | 地址                                            | 维护方   | 推荐度             |
| ------------- | ----------------------------------------------- | -------- | ------------------ |
| **清华 TUNA** | `https://pypi.tuna.tsinghua.edu.cn/simple`      | 清华大学 | 最稳定，首选       |
| 阿里云        | `https://mirrors.aliyun.com/pypi/simple`        | 阿里云   | 很稳定             |
| 腾讯云        | `https://mirrors.cloud.tencent.com/pypi/simple` | 腾讯云   | 稳定               |
| 中科大        | `https://pypi.mirrors.ustc.edu.cn/simple`       | 中科大   | 稳定               |
| 豆瓣          | `https://pypi.douban.com/simple`                | 豆瓣     | 已不太稳定，不推荐 |

**推荐用清华源**，高校维护、长期稳定、同步及、关键是同在教育科研网内部。

## 三、How：uv 配置镜像源的方法

uv 支持**三种方式**配置镜像源，按作用范围从大到小：

### 方式 A：一次性临时指定（单次命令有效）

在命令后加 `--index-url` 参数：

```bash
uv add pydantic rich --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

特点：只对这条命令生效，不改变全局或项目配置。适合临时用一次。

### 方式 B：项目级配置（推荐，只影响当前项目）

在项目根目录创建 `uv.toml` 文件，配置项目的镜像源：

```toml
# uv.toml —— uv 项目级配置（加速包下载）
[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

特点：只影响当前项目，配置随项目走（但 uv.toml 本身可选择性是否提交到 git）。**教学项目用这种方式**，干净且可控。

### 方式 C：全局配置（影响本机所有 uv 项目）

通过环境变量或全局配置文件设置，一劳永逸。

**环境变量方式**（Windows cmd）：
```cmd
set UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

**全局配置文件方式**：在用户目录下创建 `~/.config/uv/uv.toml`（Windows 是 `%USERPROFILE%\.config\uv\uv.toml`），内容同方式 B。

特点：一次配置，本机所有 uv 项目都走镜像。适合你确定以后所有项目都用这个源。

### 三种方式对比

| 方式                 | 作用范围     | 是否持久         | 推荐场景       |
| -------------------- | ------------ | ---------------- | -------------- |
| A 临时 `--index-url` | 单条命令     | 否               | 临时试一次     |
| B 项目级 `uv.toml`   | 当前项目     | 是（需提交 git） | **本项目推荐** |
| C 全局配置/环境变量  | 本机所有项目 | 是               | 个人长期开发   |

---

## 四、本项目的做法（推荐方案）

建议用**方式 B（项目级 uv.toml）**，理由：
1. 不影响你机器上其他 uv 项目（隔离）。
2. 配置随项目走，清晰可控。
3. 教学项目应显式记录配置，方便学习者复现。

### 关于是否提交 uv.toml 到 git

**建议提交**。理由：
- 这是项目级配置，目的是让任何拿到本项目的人都能快速下载依赖（可复现性）。
- 不含敏感信息（只是个镜像地址）。
- 符合 Step 1 我们坚持的「配置随项目走」原则。

---

## 五、请执行（分两步）

### 第一步：创建 uv.toml 配置镜像源

在项目根目录（`D:\AllMyVC\ZCodeProject\langchain-chat\`）创建文件 `uv.toml`，内容：

```toml
# uv.toml —— uv 项目级配置
# 配置国内镜像源（清华 TUNA），加速 uv add / uv sync 时的包下载
[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

### 第二步：重新执行 uv add（这次应该快很多）

```bash
cd /d D:\AllMyVC\ZCodeProject\langchain-chat
uv add pydantic pydantic-settings python-dotenv pyyaml rich prompt_toolkit
```

如果速度明显提升（几秒到十几秒内完成），说明镜像生效。

---

## 六、验证与排查

### 验证镜像是否生效

执行 uv add 时，uv 辸出中通常会显示下载来源。如果想明确确认走的是哪个源，可以加 `-v`（verbose，详细输出）参数：

```bash
uv add rich -v
```

详细日志里会看到类似 `Downloading from https://pypi.tuna.tsinghua.edu.cn/...` 的字样，说明走了镜像。

### 如果仍然慢

| 可能原因             | 排查方法                                 |
| -------------------- | ---------------------------------------- |
| uv.toml 位置不对     | 必须在项目根目录，和 pyproject.toml 同级 |
| 格式错误             | 检查是不是 `[[index]]` 双括号            |
| 缓存里已有旧版本     | 不影响速度，只是跳过下载                 |
| 镜像同步延迟（极少） | 换阿里云源试试                           |

### 如何删除配置

如果不想用镜像了，直接删除 `uv.toml` 文件即可，uv 会回到默认 PyPI 源。

