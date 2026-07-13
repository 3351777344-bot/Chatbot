"""用标准库 HTTP 请求 OpenAI-compatible chat/completions 接口。"""

import json
import os
from urllib.request import Request, urlopen


def main() -> None:
    base = os.environ["API_BASE_URL"].rstrip("/")
    body = json.dumps({"model": os.environ["MODEL_NAME"], "messages": [{"role": "user", "content": "你好"}]}).encode()
    request = Request(f"{base}/chat/completions", body, {"Authorization": f"Bearer {os.environ['API_KEY']}", "Content-Type": "application/json"})
    with urlopen(request, timeout=30) as response:
        print(json.load(response)["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
