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

            return SQLiteBackend(
                config.get("storage", "sqlite", "path", default="data/sqlite/app.db")
            )
        if backend_type == "mysql":
            from storage.mysql_backend import MySQLBackend

            return MySQLBackend(
                config.get("storage", "mysql", default={}), config.secret.MYSQL_PASSWORD
            )
        if backend_type == "file":
            from storage.file_backend import FileBackend

            directory = config.get("storage", "file", "path", default=None) or config.get(
                "storage", "file", "dir", default="data/filestore"
            )
            return FileBackend(directory)
        raise ValueError(f"不支持的存储类型: {backend_type}")
