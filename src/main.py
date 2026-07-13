"""加载配置并启动异步 TUI。"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


async def async_main() -> None:
    from core.config_manager import get_config
    from storage.factory import StorageFactory
    from ui.tui.app import TUIApp

    config = get_config()
    print(f"[启动] 存储后端: {config.storage_type}，默认模型: {config.default_model}")
    backend = StorageFactory.create(config=config)
    await backend.initialize()
    try:
        await TUIApp(backend).run()
    finally:
        await backend.close()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
