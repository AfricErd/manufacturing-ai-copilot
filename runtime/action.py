from abc import ABC
from dataclasses import dataclass, field


class Action(ABC):
    """
    Runtime Action 基类。

    Action 描述 Runtime 下一步应该执行什么。

    Runtime 不关心 Planner 如何思考，
    Executor 不关心 Planner 如何生成，
    Action 只是 Runtime 内部统一协议。
    """
    pass


@dataclass
class ToolAction(Action):

    tool_name: str

    arguments: dict = field(default_factory=dict)


@dataclass
class FinishAction(Action):

    answer: str

@dataclass
class BatchToolAction(Action):

    actions: list[ToolAction]