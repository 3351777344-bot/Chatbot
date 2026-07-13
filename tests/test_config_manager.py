import pytest

from core.config_manager import AppConfig


def test_environment_overrides_are_isolated():
    dev = AppConfig(app_env="dev")
    test = AppConfig(app_env="test")
    prod = AppConfig(app_env="prod")
    assert dev.storage_type == "sqlite"
    assert test.storage_type == "sqlite"
    assert prod.storage_type == "mysql"
    assert dev.get("storage", "sqlite", "path") != test.get("storage", "sqlite", "path")
    assert dev.get("app", "name") == "langchain-chat"


def test_invalid_environment_rejected():
    with pytest.raises(ValueError):
        AppConfig(app_env="staging")


def test_non_dev_does_not_fallback_to_plain_dotenv(monkeypatch):
    monkeypatch.setenv("API_KEY", "")
    config = AppConfig(app_env="test")
    assert config.secret.MODEL_NAME == "deepseek-chat"
