from abc import ABC, abstractmethod
from runtime.context import AgentContext
from runtime.action import Action


class Planner(ABC):
    """
    Planner Interface

    Planner 根据当前 Context，
    决定 Runtime 下一步 Action。

    Runtime 不关心 Planner 如何思考，
    只依赖这个统一接口。
    """

    @abstractmethod
    def plan(self, context: AgentContext) -> Action:
        """
        根据 Context 生成下一步 Action。
        """
        raise NotImplementedError