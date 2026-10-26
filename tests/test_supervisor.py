from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from agents.supervisor_agent import SupervisorAgent


class FakeAgent(BaseAgent):

    def run(
        self,
        question: str,
    ):

        return f"answer: {question}"


registry = AgentRegistry()

registry.register(
    "fake",
    FakeAgent(),
)

supervisor = SupervisorAgent(registry)

result = supervisor.run(
    "fake",
    "hello",
)

assert result == "answer: hello"

if __name__=="__main__":
    print(result)