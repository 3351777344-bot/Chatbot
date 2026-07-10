"""Step 1 command-line entry point for project initialization verification."""

from __future__ import annotations

import platform


PROJECT_NAME = "langchain-chat"
PROJECT_VERSION = "0.1.0"
CURRENT_PROGRESS = "Step 1：项目初始化与工程化配置"


def main() -> None:
    """Print the Step 1 startup banner without starting later-stage services."""
    border = "=" * 58
    print(border)
    print(f"项目名：{PROJECT_NAME}")
    print(f"版本号：{PROJECT_VERSION}")
    print(f"Python 版本：{platform.python_version()}")
    print(f"当前进度：{CURRENT_PROGRESS}")
    print("启动成功：Step 1 工程化配置验证通过")
    print(border)


if __name__ == "__main__":
    main()
