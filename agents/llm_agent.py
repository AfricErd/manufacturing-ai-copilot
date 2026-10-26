from agents.base_agent import BaseAgent


class LLMAgent(BaseAgent):

    def __init__(
        self,
        runtime,
    ):

        self.runtime = runtime


    def run(
        self,
        question: str,
    ):

        state = self.runtime.run(
            question
        )

        return self._build_agent_result(
            agent_name="llm",
            state=state,
        )