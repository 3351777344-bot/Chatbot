"""按当前配置初始化数据库表。"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.config_manager import get_config
from storage.factory import StorageFactory


async def initialize_database() -> None:
    config = get_config()
    backend = StorageFactory.create(config=config)
    try:
        await backend.initialize()
        print(f"[成功] {config.storage_type} 存储后端初始化完成")
    finally:
        await backend.close()


if __name__ == "__main__":
    asyncio.run(initialize_database())
