from tools.registry import Tool

from tools.data_tool import (
    query_sales_orders,
    query_customer_orders,
    query_work_orders,
    count_sales_orders,
    count_customer_orders,
    count_work_orders,
)

from tools.knowledge_tool import (
    retrieve_manufacturing_knowledge,
)

from tools.production_tool import (
    get_production_status,
    query_production_tasks,
    query_equipment_status,
)   



def get_database_tools() -> list[Tool]:
    """
    返回 Manufacturing AI Copilot 默认 Runtime 使用的工具集合。

    Tool 的定义属于 tools 层，
    不依赖任何 Agent。
    """

    return [

        Tool(
            name="query_sales_orders",
            description="查询制造企业的销售订单列表。",
            schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回订单的最大数量，默认10条",
                    }
                },
            },
            func=query_sales_orders,
        ),

        Tool(
            name="query_customer_orders",
            description="根据客户名称查询该客户的销售订单。",
            schema={
                "type": "object",
                "properties": {
                    "customer": {
                        "type": "string",
                        "description": "客户名称，例如广汽、特斯拉、上汽集团",
                    }
                },
                "required": [
                    "customer"
                ],
            },
            func=query_customer_orders,
        ),

        Tool(
            name="query_work_orders",
            description="查询制造企业生产工单列表。",
            schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回工单的最大数量，默认10条",
                    }
                },
            },
            func=query_work_orders,
        ),

        Tool(
            name="count_sales_orders",
            description="查询制造企业的销售订单总数量。",
            schema={
                "type": "object",
                "properties": {},
            },
            func=count_sales_orders,
        ),

        Tool(
            name="count_customer_orders",
            description="根据客户名称统计制造企业的销售订单数量。",
            schema={
                "type": "object",
                "properties": {
                    "customer": {
                        "type": "string",
                        "description": "客户名称，例如广汽、特斯拉、上汽集团",
                    }
                },
                "required": [
                    "customer"
                ],
            },
            func=count_customer_orders,
        ),

        Tool(
            name="count_work_orders",
            description="查询制造企业的生产工单总数量。",
            schema={
                "type": "object",
                "properties": {},
            },
            func=count_work_orders,
        ),
    ]

def get_knowledge_tools() -> list[Tool]:
    """
    返回 Knowledge Runtime 使用的知识检索工具集合。

    Knowledge Tool 只负责从制造业知识库中检索资料，
    不负责生成最终答案。
    """

    return [
        Tool(
            name="retrieve_manufacturing_knowledge",
            description=(
                "从制造业知识库中检索与用户问题相关的专业资料。"
                "适用于 MES、制造工艺、加工工艺等知识类问题。"
            ),
            schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "需要检索的制造业知识问题",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回最相关的知识片段数量，默认3条",
                        "default": 3,
                    },
                },
                "required": [
                    "question"
                ],
            },
            func=retrieve_manufacturing_knowledge,
        ),
    ]

def get_production_tools() -> list[Tool]:
    """
    返回 Production Runtime 使用的 MES HTTP 工具集合。

    Production Tool 通过 HTTP 访问模拟 MES 服务，
    与 Database / Knowledge ToolSet 保持隔离。
    """

    return [

        Tool(
            name="get_production_status",
            description=(
                "查询当前工厂的生产运行状态。"
            ),
            schema={
                "type": "object",
                "properties": {},
            },
            func=get_production_status,
        ),

        Tool(
            name="query_production_tasks",
            description=(
                "查询 MES 中的生产任务列表。"
            ),
            schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": (
                            "返回生产任务的最大数量，"
                            "默认10条"
                        ),
                    }
                },
            },
            func=query_production_tasks,
        ),

        Tool(
            name="query_equipment_status",
            description=(
                "根据设备编号查询 MES 中的"
                "实时设备状态。"
            ),
            schema={
                "type": "object",
                "properties": {
                    "equipment_no": {
                        "type": "string",
                        "description": (
                            "设备编号，例如 "
                            "EQ001、EQ002"
                        ),
                    }
                },
                "required": [
                    "equipment_no"
                ],
            },
            func=query_equipment_status,
        ),
    ]