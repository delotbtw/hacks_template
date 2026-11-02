import asyncio
import hashlib
import json
import logging
from typing import Protocol

from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str  # system | user | assistant
    content: str


class LLMClient(Protocol):
    async def complete(self, messages: list[Message]) -> str: ...


class StubLLMClient:
    """Запасной вариант без сети: сразу завершает цикл агента."""

    async def complete(self, messages: list[Message]) -> str:
        return json.dumps({"action": "final", "answer": "stub: LLM недоступна, ответ-заглушка"})


class OpenAICompatibleClient:
    """OpenAI-совместимый API (модель онлайн) с таймаутом, ретраем и запасным вариантом.

    Запасной вариант: последний удачный ответ на такие же сообщения, иначе `fallback` (заглушка).
    """

    def __init__(self, fallback: LLMClient | None = None) -> None:
        s = get_settings()
        self.model = s.openai_model
        self.timeout = s.llm_timeout_s
        self.retries = s.llm_retries
        self.fallback = fallback or StubLLMClient()
        self._last_good: dict[str, str] = {}
        self._client = None
        self._settings = s

    def _api(self):
        if self._client is None:
            from openai import AsyncOpenAI  # группа llm: uv sync --group llm

            self._client = AsyncOpenAI(
                api_key=self._settings.openai_api_key,
                base_url=self._settings.openai_base_url,
                timeout=self.timeout,
                max_retries=0,  # ретраи делаем сами ниже
            )
        return self._client

    async def _request(self, messages: list[Message]) -> str:
        resp = await self._api().chat.completions.create(
            model=self.model, messages=[m.model_dump() for m in messages]
        )
        return resp.choices[0].message.content or ""

    async def complete(self, messages: list[Message]) -> str:
        key = hashlib.sha256(json.dumps([m.model_dump() for m in messages]).encode()).hexdigest()
        for attempt in range(self.retries + 1):
            try:
                result = await asyncio.wait_for(self._request(messages), self.timeout)
            except Exception as exc:
                logger.warning("LLM attempt %s failed: %s", attempt + 1, type(exc).__name__)
                await asyncio.sleep(min(2**attempt, 5) * 0.2)
            else:
                self._last_good[key] = result
                return result
        if key in self._last_good:
            logger.warning("LLM недоступна, отдаём кэшированный ответ")
            return self._last_good[key]
        logger.warning("LLM недоступна, используем запасной клиент")
        return await self.fallback.complete(messages)


def get_llm_client() -> LLMClient:
    return OpenAICompatibleClient() if get_settings().openai_api_key else StubLLMClient()
