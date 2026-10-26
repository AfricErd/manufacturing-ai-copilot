from dataclasses import dataclass


@dataclass
class AgentContext:

    question: str

    goal: str | None

    observation: object | list[object] | None

    tools: list