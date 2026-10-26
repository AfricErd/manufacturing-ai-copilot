from agents.base_agent import BaseAgent


class ProductionAgent(BaseAgent):

    def __init__(
        self,
        runtime,
    ):

        self.runtime = runtime


    def run(
        self,
        question: str,
    ):
        """
        Production Agent Adapter。

        实际 MES Tool Calling
        由独立 Production Runtime 完成。
        """

        state = self.runtime.run(
            question
        )

        return self._build_agent_result(
            agent_name="production",
            state=state,
        )