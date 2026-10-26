from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from runtime.action import FinishAction
from runtime.action import ToolAction
from runtime.planner import Planner
from runtime.runtime import AgentRuntime


class EchoPlanner(Planner):
    def plan(self, context):
        if context.observation is None:
            return ToolAction(
                tool_name="echo",
                arguments={
                    "value": context.question,
                },
            )

        return FinishAction(
            answer=context.observation.result
        )


def test_runtime_creates_isolated_invocations():
    runtime = AgentRuntime()
    runtime.set_planner(
        EchoPlanner()
    )

    first = runtime.create_invocation(
        "request-a"
    )
    second = runtime.create_invocation(
        "request-b"
    )

    assert first is not second
    assert first.state is not second.state
    assert first.trace is not second.trace
    assert first.executor is not second.executor


def test_same_runtime_supports_concurrent_request_state_isolation():
    barrier = Barrier(2)

    def echo(value):
        barrier.wait(timeout=5)
        return value

    runtime = AgentRuntime()

    runtime.register_tool(
        name="echo",
        func=echo,
        description="Return the provided value.",
        schema={
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                }
            },
            "required": [
                "value",
            ],
        },
    )

    runtime.set_planner(
        EchoPlanner()
    )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        future_a = executor.submit(
            runtime.run,
            "request-a",
        )
        future_b = executor.submit(
            runtime.run,
            "request-b",
        )

        state_a = future_a.result(
            timeout=5
        )
        state_b = future_b.result(
            timeout=5
        )

    assert state_a is not state_b
    assert state_a.answer == "request-a"
    assert state_b.answer == "request-b"
    assert state_a.last_observation.result == "request-a"
    assert state_b.last_observation.result == "request-b"
    assert state_a.status == "finished"
    assert state_b.status == "finished"

if __name__ == "__main__":
    test_runtime_creates_isolated_invocations()
    test_same_runtime_supports_concurrent_request_state_isolation()
    print("test_runtime_isolation pass")