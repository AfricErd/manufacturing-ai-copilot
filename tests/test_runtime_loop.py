from runtime.fake_planner import FakePlanner
from runtime.runtime import AgentRuntime


def fake_tool(name):
    return f"hello {name}"


def test_runtime_loop():
    runtime = AgentRuntime()

    runtime.register_tool(
        name="fake_tool",
        func=fake_tool,
        description="Fake Tool",
    )

    runtime.set_planner(
        FakePlanner()
    )

    invocation = runtime.create_invocation(
        "hello"
    )

    state = invocation.run()

    for record in invocation.trace.records:
        print(record)

    assert state.finished is True
    assert state.status == "finished"
    assert state.answer == "runtime finished"
    assert state.step == 1
    assert state.last_observation.result == "hello runtime"
    assert state.last_observation.success is True


if __name__ == "__main__":
    test_runtime_loop()

print("test_runtime_loop pass")