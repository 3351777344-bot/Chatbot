"""加载环境变量和 YAML 业务配置。"""

import os
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
    ALLOWED_ENVS = {"dev", "test", "prod"}

    def __init__(self, config_path: Path | None = None, app_env: str | None = None) -> None:
        self.app_env = str(app_env or os.getenv("APP_ENV", "dev")).lower().strip()
        if self.app_env not in self.ALLOWED_ENVS:
            raise ValueError(f"APP_ENV 必须是 dev/test/prod，实际为: {self.app_env}")
        environment_file = PROJECT_ROOT / f".env.{self.app_env}"
        if not environment_file.exists() and self.app_env == "dev":
            environment_file = PROJECT_ROOT / ".env"
        self.secret = SecretConfig(
            _env_file=environment_file if environment_file.exists() else None  # type: ignore[call-arg]
        )
        self.config_path = config_path or PROJECT_ROOT / "config.yaml"
        self._yaml_config = self._load_yaml(self.config_path)
        if config_path is None:
            override = self._load_yaml(PROJECT_ROOT / f"config.{self.app_env}.yaml")
            self._yaml_config = self._deep_merge(self._yaml_config, override)

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return data if isinstance(data, dict) else {}

    @classmethod
    def _deep_merge(cls, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

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
    def available_model_values(self) -> list[str]:
        return [
            str(item.get("value")) if isinstance(item, dict) else str(item)
            for item in self.available_models
        ]

    @property
    def llm_timeout(self) -> int:
        return int(self.get("llm", "timeout", default=30))

    @property
    def llm_max_retries(self) -> int:
        return int(self.get("llm", "max_retries", default=3))

    @property
    def title_max_length(self) -> int:
        return int(self.get("session", "title_max_length", default=30))

    @property
    def temperature(self) -> float:
        return float(self.get("models", "temperature", default=0.7))

    @property
    def max_tokens(self) -> int:
        return int(self.get("models", "max_tokens", default=2048))

    @property
    def current_step(self) -> str:
        return str(self.get("app", "current_step", default=""))

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
