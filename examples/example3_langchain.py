"""用项目 ChatEngine 调用 LangChain ChatOpenAI。"""

import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.chat_engine import ChatEngine
from core.config_manager import get_config


def main() -> None:
    text, usage = ChatEngine(get_config()).chat([HumanMessage(content="你好")])
    print(text, usage)


if __name__ == "__main__":
    main()
