from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """
    Agent运行状态
    """

    question: str

    current_goal: str | None = None

    step: int = 0

    finished: bool = False

    answer: str | None = None

    last_observation: Any = None

    status: str = "created"