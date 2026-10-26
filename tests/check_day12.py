import pytest

pytest.importorskip(
    "langgraph"
)

from agents.agent_registry import (
    AgentRegistry,
)

from workflow.agent_result import (
    AgentResult,
)

from workflow.langgraph_workflow import (
    ManufacturingWorkflow,
)

from workflow.task import (
    SubTask,
    TaskPlan,
    TaskStatus,
)

from workflow.task_dispatcher import (
    TaskDispatcher,
)


class RecordingAgent:

    def __init__(
        self,
        name: str,
        calls: list,
        should_fail: bool = False,
    ):

        self.name = name
        self.calls = calls
        self.should_fail = (
            should_fail
        )


    def run(
        self,
        question: str,
    ):

        self.calls.append(
            self.name
        )

        if self.should_fail:

            return AgentResult(
                agent_name=self.name,
                success=False,
                answer="",
                error=(
                    "fake agent failure"
                ),
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            answer=(
                f"{self.name} completed"
            ),
            data={
                "input":
                    question,
            },
        )


class FixedTaskPlanner:

    def __init__(
        self,
        tasks,
    ):

        self.tasks = tuple(
            tasks
        )


    def create_plan(
        self,
        question,
    ):

        return TaskPlan(
            question=question,
            tasks=self.tasks,
        )


class RecordingSynthesizer:

    def __init__(
        self,
    ):

        self.calls = []


    def synthesize(
        self,
        question,
        plan,
        task_results,
    ):

        self.calls.append(
            {
                "question":
                    question,

                "plan":
                    plan,

                "task_results":
                    task_results,
            }
        )

        parts = []

        for task in plan.tasks:

            result = (
                task_results[
                    task.task_id
                ]
            )

            parts.append(
                (
                    f"[{task.agent_name}] "
                    f"{result.status.value}"
                )
            )

        return "\n".join(
            parts
        )


def build_test_workflow(
    tasks,
    production_should_fail=False,
):

    calls = []

    registry = (
        AgentRegistry()
    )

    for name in [
        "llm",
        "database",
        "knowledge",
        "production",
    ]:

        registry.register(
            name,
            RecordingAgent(
                name=name,
                calls=calls,
                should_fail=(
                    production_should_fail
                    and name
                    == "production"
                ),
            ),
        )

    planner = (
        FixedTaskPlanner(
            tasks
        )
    )

    dispatcher = (
        TaskDispatcher(
            registry,
            max_workers=4,
        )
    )

    synthesizer = (
        RecordingSynthesizer()
    )

    workflow = (
        ManufacturingWorkflow(
            task_planner=planner,
            task_dispatcher=dispatcher,
            synthesizer=synthesizer,
        )
    )

    return (
        workflow,
        calls,
        synthesizer,
    )


def test_single_task_workflow():

    task = SubTask(
        task_id="T1",
        description=(
            "查询生产工单"
        ),
        agent_name="database",
    )

    workflow, calls, _ = (
        build_test_workflow(
            [
                task,
            ]
        )
    )

    state = (
        workflow.run_detailed(
            "查询生产工单"
        )
    )

    assert calls == [
        "database",
    ]

    assert (
        state[
            "task_plan"
        ].task_ids
        == (
            "T1",
        )
    )

    assert (
        state[
            "task_results"
        ]["T1"].status
        == TaskStatus.SUCCEEDED
    )

    assert (
        state["final_answer"]
        == "[database] succeeded"
    )


def test_multi_agent_workflow():

    tasks = [
        SubTask(
            task_id="T1",
            description="查询订单",
            agent_name="database",
        ),
        SubTask(
            task_id="T2",
            description="查询生产状态",
            agent_name="production",
        ),
        SubTask(
            task_id="T3",
            description="检索SOP",
            agent_name="knowledge",
        ),
    ]

    workflow, calls, _ = (
        build_test_workflow(
            tasks
        )
    )

    state = (
        workflow.run_detailed(
            "分析订单、生产风险并结合SOP给出建议"
        )
    )

    assert set(
        calls
    ) == {
        "database",
        "production",
        "knowledge",
    }

    assert set(
        state[
            "task_results"
        ].keys()
    ) == {
        "T1",
        "T2",
        "T3",
    }

    assert all(
        result.success
        for result
        in state[
            "task_results"
        ].values()
    )


def test_independent_agent_failure_does_not_stop_others():

    tasks = [
        SubTask(
            task_id="T1",
            description="查询订单",
            agent_name="database",
        ),
        SubTask(
            task_id="T2",
            description="查询生产状态",
            agent_name="production",
        ),
        SubTask(
            task_id="T3",
            description="检索SOP",
            agent_name="knowledge",
        ),
    ]

    workflow, calls, _ = (
        build_test_workflow(
            tasks,
            production_should_fail=True,
        )
    )

    state = (
        workflow.run_detailed(
            "分析订单、生产风险并结合SOP给出建议"
        )
    )

    assert set(
        calls
    ) == {
        "database",
        "production",
        "knowledge",
    }

    assert (
        state[
            "task_results"
        ]["T1"].status
        == TaskStatus.SUCCEEDED
    )

    assert (
        state[
            "task_results"
        ]["T2"].status
        == TaskStatus.FAILED
    )

    assert (
        state[
            "task_results"
        ]["T3"].status
        == TaskStatus.SUCCEEDED
    )

    assert (
        "fake agent failure"
        in state[
            "task_results"
        ]["T2"].error
    )