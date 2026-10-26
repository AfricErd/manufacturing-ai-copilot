from dataclasses import dataclass
from typing import Any


@dataclass
class Observation:
    """
    Tool 执行后的统一结果
    """

    tool_name: str

    success: bool

    result: Any = None

    error: str | None = None