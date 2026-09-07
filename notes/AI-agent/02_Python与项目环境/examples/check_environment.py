"""检查解释器、关键依赖与环境变量；不会调用网络。"""

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from dotenv import load_dotenv

from settings import ConfigurationError, Settings


PACKAGES = ("openai", "pydantic", "python-dotenv", "pytest")


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    print(f"Python: {sys.version.split()[0]}")
    print(f"解释器: {sys.executable}")
    for package in PACKAGES:
        try:
            print(f"{package}: {version(package)}")
        except PackageNotFoundError:
            print(f"{package}: 未安装")

    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        print(f"配置检查失败：{exc}")
        print("请复制 .env.example 为 .env，并填写实际配置。")
        return 1

    print(f"配置检查通过：{settings.safe_summary()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

