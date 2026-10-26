from agents.agent_registry import AgentRegistry
from agents.base_agent import BaseAgent


class FakeAgent(BaseAgent):

    def run(self, question):

        return "ok"


registry = AgentRegistry()

registry.register(
    "fake",
    FakeAgent(),
)

assert registry.exists("fake")

assert registry.get("fake").run("hello") == "ok"

assert registry.names() == ["fake"]

if __name__ == "__main__":
    print(registry.get("fake").run("hello"))