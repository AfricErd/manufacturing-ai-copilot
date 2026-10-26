from runtime.action import ToolAction
from runtime.runtime import AgentRuntime


def fake_tool(limit=10):
    return {
        "data": [1, 2, 3],
        "limit": limit,
    }


def test_executor():
    runtime = AgentRuntime()

    runtime.register_tool(
        "fake_tool",
        fake_tool,
    )

    invocation = runtime.create_invocation(
        "测试Executor"
    )

    action = ToolAction(
        tool_name="fake_tool",
        arguments={
            "limit": 5,
        },
    )

    result = invocation.execute_tool(
        action
    )

    assert result.success is True
    assert result.result == {
        "data": [1, 2, 3],
        "limit": 5,
    }


if __name__ == "__main__":
    test_executor()
    print("test_executor pass")