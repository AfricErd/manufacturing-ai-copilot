from agents.base_agent import BaseAgent


class KnowledgeAgent(BaseAgent):

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
        Knowledge Agent Adapter。

        实际 Tool Calling 和知识库查询
        仍然由独立 Knowledge Runtime 完成。
        """

        state = self.runtime.run(
            question
        )

        return self._build_agent_result(
            agent_name="knowledge",
            state=state,
        )