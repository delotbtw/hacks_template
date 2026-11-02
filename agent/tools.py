from collections.abc import Callable
from typing import Any

TOOLS: dict[str, Callable[..., Any]] = {}


def tool(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Регистрирует функцию как инструмент агента (имя = имя функции)."""
    TOOLS[fn.__name__] = fn  # ty: ignore[unresolved-attribute]
    return fn


@tool
def echo(text: str) -> str:
    """Пример-заглушка: возвращает переданный текст."""
    return text
