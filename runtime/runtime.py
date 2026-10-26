from runtime.invocation import RuntimeInvocation
from tools.registry import Tool
from tools.registry import ToolRegistry


class AgentRuntime:
    """
    Reusable runtime configuration for an Agent.

    AgentRuntime owns stable dependencies such as ToolRegistry and Planner.
    Mutable request execution state is owned by RuntimeInvocation instead.

    This makes a configured AgentRuntime safe to reuse across independent
    requests, provided its Planner and registered Tool implementations are
    themselves safe for concurrent read/use after application startup.
    """

    def __init__(self):
        self.registry = ToolRegistry()
        self.planner = None

    def register_tool(
        self,
        name,
        func,
        description="",
        schema=None,
    ):
        tool = Tool(
            name=name,
            description=description,
            schema=schema or {},
            func=func,
        )

        self.registry.register(
            tool
        )

    def set_planner(
        self,
        planner,
    ):
        self.planner = planner

    def create_invocation(
        self,
        question: str,
    ) -> RuntimeInvocation:
        """
创建一个独立的一次性运行时调用。
代理状态（AgentState）、代理追踪（AgentTrace）和执行器（Executor）在每次调用时创建，
且永远不会存储在可复用的代理运行时（AgentRuntime）实例上。
        """

        return RuntimeInvocation(
            question=question,
            registry=self.registry,
            planner=self.planner,
        )

    def run(
        self,
        question: str,
    ):
        """
        Execute one isolated request and return its final AgentState.
        """

        invocation = self.create_invocation(
            question
        )

        return invocation.run()