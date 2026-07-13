"""加载环境变量和 YAML 业务配置。"""

from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class SecretConfig(BaseSettings):
    API_BASE_URL: str = "https://api.example.com/v1"
    API_KEY: str = "your_api_key_here"
    MODEL_NAME: str = "deepseek-chat"
    MYSQL_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppConfig:
    def __init__(self, config_path: Path | None = None) -> None:
        self.secret = SecretConfig()
        self.config_path = config_path or PROJECT_ROOT / "config.yaml"
        self._yaml_config = self._load_yaml(self.config_path)

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return data if isinstance(data, dict) else {}

    @property
    def storage_type(self) -> str:
        return self.get("storage", "type", default="sqlite")

    @property
    def default_model(self) -> str:
        return self.get("models", "default", default=self.secret.MODEL_NAME)

    @property
    def available_models(self) -> list[dict[str, str] | str]:
        return self.get("models", "available", default=[])

    @property
    def llm_timeout(self) -> int:
        return int(self.get("llm", "timeout", default=30))

    @property
    def llm_max_retries(self) -> int:
        return int(self.get("llm", "max_retries", default=3))

    @property
    def title_max_length(self) -> int:
        return int(self.get("session", "title_max_length", default=30))

    def get(self, *keys: str, default: Any = None) -> Any:
        value: Any = self._yaml_config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value


_config_instance: AppConfig | None = None


def get_config() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance

