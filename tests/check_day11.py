from agents.supervisor_agent import (
    SupervisorAgent,
)

from runtime.action import (
    ToolAction,
)

from runtime.runtime import (
    AgentRuntime,
)

from tools.toolset import (
    get_database_tools,
    get_knowledge_tools,
    get_production_tools,
)


class FakeRegistry:

    def __init__(
        self,
        names,
    ):

        self._names = list(
            names
        )


    def names(
        self,
    ):

        return list(
            self._names
        )


    def get(
        self,
        name,
    ):

        if name not in self._names:

            raise KeyError(
                name
            )

        return object()


def test_day11_supervisor_routing_regression():

    registry = FakeRegistry(
        [
            "llm",
            "database",
            "knowledge",
            "production",
        ]
    )

    supervisor = SupervisorAgent(
        registry
    )

    route_cases = {
        "你好":
            "llm",

        "MES是什么":
            "knowledge",

        "销售订单有几个":
            "database",

        "查询生产工单":
            "database",

        "当前生产状态怎么样":
            "production",

        "查询前2条生产任务":
            "production",

        "查询设备EQ002状态":
            "production",

        "查看EQ003运行状态":
            "production",
    }

    for (
        question,
        expected_agent,
    ) in route_cases.items():

        assert (
            supervisor.select_agent(
                question
            )
            == expected_agent
        )


def test_day11_toolsets_remain_isolated():

    assert [
        tool.name
        for tool in get_database_tools()
    ] == [
        "query_sales_orders",
        "query_customer_orders",
        "query_work_orders",
        "count_sales_orders",
        "count_customer_orders",
        "count_work_orders",
    ]

    assert [
        tool.name
        for tool in get_knowledge_tools()
    ] == [
        "retrieve_manufacturing_knowledge",
    ]

    assert [
        tool.name
        for tool in get_production_tools()
    ] == [
        "get_production_status",
        "query_production_tasks",
        "query_equipment_status",
    ]


def test_day11_runtime_instances_are_isolated():

    runtimes = [
        AgentRuntime()
        for _ in range(4)
    ]

    assert len(
        {
            id(runtime)
            for runtime in runtimes
        }
    ) == 4

    assert len(
        {
            id(runtime.registry)
            for runtime in runtimes
        }
    ) == 4


def test_day11_executor_converts_exception():

    def failing_tool():

        raise RuntimeError(
            "MES unavailable"
        )

    runtime = AgentRuntime()

    runtime.register_tool(
        name=(
            "get_production_status"
        ),
        func=failing_tool,
        description=(
            "fake production tool"
        ),
        schema={
            "type": "object",
            "properties": {},
        },
    )

    invocation = (
        runtime.create_invocation(
            "当前生产状态怎么样"
        )
    )

    observation = (
        invocation.execute_tool(
            ToolAction(
                tool_name=(
                    "get_production_status"
                ),
                arguments={},
            )
        )
    )

    assert (
        observation.success
        is False
    )

    assert (
        observation.result
        is None
    )

    assert (
        "MES unavailable"
        in observation.error
    )


def test_day11_executor_success():

    runtime = AgentRuntime()

    runtime.register_tool(
        name=(
            "query_equipment_status"
        ),
        func=(
            lambda equipment_no: {
                "equipment_no":
                    equipment_no,

                "status":
                    "running",
            }
        ),
        description=(
            "fake production tool"
        ),
        schema={
            "type": "object",
            "properties": {
                "equipment_no": {
                    "type":
                        "string",
                }
            },
            "required": [
                "equipment_no",
            ],
        },
    )

    invocation = (
        runtime.create_invocation(
            "查询设备EQ002状态"
        )
    )

    observation = (
        invocation.execute_tool(
            ToolAction(
                tool_name=(
                    "query_equipment_status"
                ),
                arguments={
                    "equipment_no":
                        "EQ002",
                },
            )
        )
    )

    assert (
        observation.success
        is True
    )

    assert (
        observation.error
        is None
    )

    assert (
        observation.result
        == {
            "equipment_no":
                "EQ002",

            "status":
                "running",
        }
    )