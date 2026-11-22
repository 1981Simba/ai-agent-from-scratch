"""
Offline test: checks the tools, the dispatcher and the agent loop without
calling the real API (no key, no cost). Run:  python test_agent_offline.py
"""

import os
from types import SimpleNamespace as NS

os.environ.setdefault("ANTHROPIC_API_KEY", "offline-test")
import agent  # noqa: E402


def text(t):
    return NS(type="text", text=t)


def tool_use(id_, name, input_):
    return NS(type="tool_use", id=id_, name=name, input=input_)


class FakeMessages:
    """Plays back scripted model replies, like the real API would send."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})  # snapshot
        return self.replies.pop(0)


def test_tools():
    assert agent.calculate("multiply", 1234, 56) == 69104
    assert agent.calculate("divide", 1, 0) == "Error: divide by zero"
    assert agent.calculate("power", 2, 3).startswith("Error")
    assert agent.run_tool("delete_everything", {}) == "Error: unknown tool"


def test_loop_and_memory(tmp_path="notes_test.txt"):
    agent.NOTES_FILE = tmp_path
    if os.path.exists(tmp_path):
        os.remove(tmp_path)  # start clean if a previous run failed
    fake = FakeMessages([
        NS(stop_reason="tool_use", content=[tool_use("t1", "calculate", {"operation": "multiply", "a": 1234, "b": 56})]),
        NS(stop_reason="end_turn", content=[text("1234 x 56 = 69,104.")]),
        NS(stop_reason="tool_use", content=[tool_use("t2", "save_note", {"text": "1234 x 56 = 69,104"})]),
        NS(stop_reason="end_turn", content=[text("Saved.")]),
    ])
    agent.client = NS(messages=fake)

    messages = [{"role": "user", "content": "What is 1234 times 56?"}]
    assert agent.run_agent(messages) == "1234 x 56 = 69,104."
    # The tool result went back with the same ID as the request.
    assert messages[2]["content"][0]["tool_use_id"] == "t1"
    assert messages[2]["content"][0]["content"] == "69104"

    messages.append({"role": "user", "content": "Save that result as a note."})
    assert agent.run_agent(messages) == "Saved."
    # Memory: the second call saw the whole first exchange.
    assert len(fake.calls[2]["messages"]) == 5
    with open(tmp_path, encoding="utf-8") as f:
        assert f.read() == "1234 x 56 = 69,104\n"
    os.remove(tmp_path)


def test_step_limit():
    forever = [NS(stop_reason="tool_use", content=[tool_use(f"t{i}", "get_time", {})]) for i in range(20)]
    agent.client = NS(messages=FakeMessages(forever))
    assert agent.run_agent([{"role": "user", "content": "loop"}]) == "Stopped: too many steps."


if __name__ == "__main__":
    test_tools()
    test_loop_and_memory()
    test_step_limit()
    print("All offline tests passed.")