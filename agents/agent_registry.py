from agents.base_agent import BaseAgent


class AgentRegistry:

    def __init__(self):

        self._agents: dict[str, BaseAgent] = {}

    def register(
        self,
        name: str,
        agent: BaseAgent,
    ):

        self._agents[name] = agent

    def get(
        self,
        name: str,
    ) -> BaseAgent:

        if name not in self._agents:
            raise KeyError(
                f"Agent '{name}' not found."
            )

        return self._agents[name]

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._agents

    def names(self):

        return list(self._agents.keys())

    def get_all(self):

        return list(self._agents.values())