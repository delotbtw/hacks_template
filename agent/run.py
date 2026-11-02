import json
from typing import Literal

from pydantic import BaseModel

from agent.llm import LLMClient, Message, get_llm_client
from agent.tools import TOOLS

SYSTEM_PROMPT = (
    "Отвечай только JSON. Вызов инструмента: "
    '{"action":"tool","tool":"<имя>","args":{...}}. '
    'Финальный ответ: {"action":"final","answer":"..."}. '
    "Доступные инструменты: " + ", ".join(TOOLS)
)


class AgentStep(BaseModel):
    """Ответ модели, валидируется Pydantic-схемой."""

    action: Literal["tool", "final"]
    tool: str | None = None
    args: dict = {}
    answer: str | None = None


async def run_agent(task: str, llm: LLMClient | None = None, max_steps: int = 5) -> str:
    llm = llm or get_llm_client()
    messages = [Message(role="system", content=SYSTEM_PROMPT), Message(role="user", content=task)]
    for _ in range(max_steps):
        raw = await llm.complete(messages)
        step = AgentStep.model_validate_json(
            raw
        )  # TODO: обработать невалидный JSON (повтор запроса)
        if step.action == "final":
            return step.answer or ""
        if step.tool not in TOOLS:
            raise ValueError(f"Неизвестный инструмент: {step.tool!r}")
        result = TOOLS[step.tool](**step.args)
        messages += [
            Message(role="assistant", content=raw),
            Message(
                role="user", content=f"Результат {step.tool}: {json.dumps(result, default=str)}"
            ),
        ]
    raise RuntimeError(f"Агент не завершил работу за {max_steps} шагов")
