"""Выгрузка OpenAPI в contracts/openapi.json. `--check` — только сравнить с коммитом."""

import json
import sys
from pathlib import Path

from app.main import app

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "openapi.json"


def render() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    content = render()
    if "--check" in sys.argv:
        current = CONTRACT_PATH.read_text() if CONTRACT_PATH.exists() else ""
        if current != content:
            sys.stderr.write("contracts/openapi.json устарел: выполните `make contracts`\n")
            return 1
        return 0
    CONTRACT_PATH.write_text(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
