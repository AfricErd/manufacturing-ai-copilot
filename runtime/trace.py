from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TraceRecord:

    step: int

    role: str

    content: str

    timestamp: str = field(
        default_factory=lambda:
        datetime.now().isoformat()
    )


class AgentTrace:

    def __init__(self):

        self.records = []


    def add(
        self,
        step,
        role,
        content
    ):

        record = TraceRecord(
            step=step,
            role=role,
            content=content
        )

        self.records.append(record)


    def get_all(self):

        return self.records