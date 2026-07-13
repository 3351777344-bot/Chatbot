"""用 OpenAI SDK 调用兼容接口。"""

import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.config_manager import get_config


def main() -> None:
    config = get_config()
    client = OpenAI(api_key=config.secret.API_KEY, base_url=config.secret.API_BASE_URL)
    result = client.chat.completions.create(model=config.secret.MODEL_NAME, messages=[{"role": "user", "content": "你好"}])
    print(result.choices[0].message.content)


if __name__ == "__main__":
    main()
