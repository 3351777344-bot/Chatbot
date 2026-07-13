"""从 YAML 初始化控制台与 JSON 滚动文件日志。"""

import logging.config
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def setup_logging() -> None:
    (PROJECT_ROOT / "logs").mkdir(parents=True, exist_ok=True)
    with (PROJECT_ROOT / "config" / "logging.yaml").open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    filename = config["handlers"]["file"]["filename"]
    config["handlers"]["file"]["filename"] = str(PROJECT_ROOT / filename)
    logging.config.dictConfig(config)
