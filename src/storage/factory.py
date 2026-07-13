"""根据配置创建可插拔存储后端。"""

from core.config_manager import AppConfig, get_config
from storage.base import StorageBackend


class StorageFactory:
    @staticmethod
    def create(storage_type: str | None = None, config: AppConfig | None = None) -> StorageBackend:
        config = config or get_config()
        backend_type = storage_type or config.storage_type
        if backend_type == "sqlite":
            from storage.sqlite_backend import SQLiteBackend

            return SQLiteBackend(config.get("storage", "sqlite", "path", default="data/sqlite/app.db"))
        if backend_type == "mysql":
            raise NotImplementedError("MySQL 后端将在 Step 11 实现")
        if backend_type == "file":
            raise NotImplementedError("File 后端将在 Step 12 实现")
        raise ValueError(f"不支持的存储类型: {backend_type}")

