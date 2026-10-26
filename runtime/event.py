from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Event:
    """
    事件基类
    """

    name: str

    timestamp: datetime

    payload: Any = None


@dataclass
class ToolExecutedEvent(Event):
    """
    工具执行事件
    """

    tool_name: str = ""

    success: bool = False