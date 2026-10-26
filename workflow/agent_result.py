from typing import Any, Dict


class AgentResult:

    def __init__(
        self,
        agent_name: str,
        success: bool,
        answer: str,
        data: Dict[str, Any] | None = None,
        error: str | None = None,
    ):
        self.agent_name = agent_name
        self.success = success
        self.answer = answer
        self.data = data or {}
        self.error = error

    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "answer": self.answer,
            "data": self.data,
            "error": self.error,
        }