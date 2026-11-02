import json

import pytest

from agent.llm import Message, OpenAICompatibleClient, StubLLMClient
from agent.run import run_agent


class ScriptedLLM:
    def __init__(self, replies: list[dict]):
        self.replies = [json.dumps(r) for r in replies]

    async def complete(self, messages):
        return self.replies.pop(0)


async def test_agent_tool_then_final():
    llm = ScriptedLLM(
        [
            {"action": "tool", "tool": "echo", "args": {"text": "hi"}},
            {"action": "final", "answer": "done"},
        ]
    )
    assert await run_agent("task", llm=llm) == "done"


async def test_agent_rejects_invalid_model_output():
    class Bad:
        async def complete(self, messages):
            return '{"action": "dance"}'

    with pytest.raises(ValueError):
        await run_agent("task", llm=Bad())


async def test_client_falls_back_to_stub_after_retries():
    class Failing(OpenAICompatibleClient):
        calls = 0

        async def _request(self, messages):
            Failing.calls += 1
            raise TimeoutError

    client = Failing(fallback=StubLLMClient())
    client.retries = 1
    out = await client.complete([Message(role="user", content="x")])
    assert json.loads(out)["action"] == "final"
    assert Failing.calls == 2


async def test_client_uses_last_good_answer():
    class Flaky(OpenAICompatibleClient):
        ok = True

        async def _request(self, messages):
            if not Flaky.ok:
                raise TimeoutError
            return "cached-answer"

    client = Flaky()
    client.retries = 0
    msgs = [Message(role="user", content="x")]
    assert await client.complete(msgs) == "cached-answer"
    Flaky.ok = False
    assert await client.complete(msgs) == "cached-answer"
