"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*args, **kwargs) -> bool:
        """Fallback used before dependencies are installed."""
        return False


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

APP_NAME = "LLM Chat-bot"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
DATABASE_PATH = DATA_DIR / "chatbot.db"
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0.7"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "30"))

MODEL_CONFIGS = {
    "gpt-4o-mini": {
        "provider": "openai-compatible",
        "model_name": "gpt-4o-mini",
        "base_url": OPENAI_BASE_URL,
        "api_key": OPENAI_API_KEY,
    },
    "deepseek-chat": {
        "provider": "openai-compatible",
        "model_name": "deepseek-chat",
        "base_url": os.getenv("DEEPSEEK_BASE_URL", OPENAI_BASE_URL),
        "api_key": os.getenv("DEEPSEEK_API_KEY", OPENAI_API_KEY),
    },
    "qwen-plus": {
        "provider": "openai-compatible",
        "model_name": "qwen-plus",
        "base_url": os.getenv("QWEN_BASE_URL", OPENAI_BASE_URL),
        "api_key": os.getenv("QWEN_API_KEY", OPENAI_API_KEY),
    },
}

if DEFAULT_MODEL not in MODEL_CONFIGS:
    DEFAULT_MODEL = "gpt-4o-mini"
