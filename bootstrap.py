from agents.llm_agent import LLMAgent
from agents.agent_registry import AgentRegistry
from agents.database_agent import DatabaseAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.production_agent import ProductionAgent

from runtime.llm_planner import LLMPlanner
from runtime.runtime import AgentRuntime

from tools.toolset import (
    get_database_tools,
    get_knowledge_tools,
    get_production_tools,
)

from workflow import ManufacturingWorkflow
from workflow.task_planner import LLMTaskPlanner
from workflow.task_dispatcher import TaskDispatcher
from workflow.synthesizer import Synthesizer


# ============================================================
# Knowledge Agent Prompt
# ============================================================

KNOWLEDGE_SYSTEM_PROMPT = """
You are a manufacturing knowledge base assistant.

For manufacturing knowledge questions such as MES,
manufacturing processes, machining processes, SOPs,
equipment principles, and professional manufacturing knowledge:

1. You must first use the retrieve_manufacturing_knowledge tool
   to retrieve information from the knowledge base.

2. Do not invent enterprise knowledge or pretend that information
   exists in the knowledge base.

3. If the tool returns found=true:
   answer the user's question based on the returned context.
   When available, include the returned sources in the answer.

4. If the tool returns found=false:
   clearly tell the user that no reliable relevant information
   was found in the knowledge base. Do not fabricate an answer.

5. After tool results are returned, use those results to produce
   the final answer.
"""


# ============================================================
# Production Agent Prompt
# ============================================================

PRODUCTION_SYSTEM_PROMPT = """
You are the production system agent for a Manufacturing AI Copilot.

Your responsibility is to answer questions about real production
execution data from the connected MES system.

Available tools:

- get_production_status:
  get the current overall production status

- query_production_tasks:
  query production task records

- query_equipment_status:
  query the current status of a specific equipment

Rules:

1. When the user asks for current production status,
   production tasks, equipment status, equipment alarms,
   or other real MES execution data,
   you must use the appropriate tool.

2. Never fabricate real-time production data from model memory.

3. If a specific equipment status is requested but no equipment
   number is provided, ask the user to provide the equipment
   number instead of inventing one.

4. After a tool result is returned,
   answer based only on the real tool result.

5. If tool execution fails or the MES service is unavailable,
   clearly tell the user that the production-system query failed.
   Do not invent data.
"""


# ============================================================
# LLM Runtime
# ============================================================

def build_llm_runtime() -> AgentRuntime:
    """
    普通对话 Runtime。

    不拥有企业 Database / Knowledge / Production Tools。
    """

    runtime = AgentRuntime()

    planner = LLMPlanner()

    runtime.set_planner(
        planner
    )

    return runtime


# ============================================================
# Database Runtime
# ============================================================

def build_database_runtime() -> AgentRuntime:
    """
    DatabaseAgent 独立 Runtime。
    """

    runtime = AgentRuntime()

    for tool in get_database_tools():

        runtime.register_tool(
            name=tool.name,
            func=tool.func,
            description=tool.description,
            schema=tool.schema,
        )

    planner = LLMPlanner()

    runtime.set_planner(
        planner
    )

    return runtime


# ============================================================
# Knowledge Runtime
# ============================================================

def build_knowledge_runtime() -> AgentRuntime:
    """
    KnowledgeAgent 独立 Runtime。
    """

    runtime = AgentRuntime()

    for tool in get_knowledge_tools():

        runtime.register_tool(
            name=tool.name,
            func=tool.func,
            description=tool.description,
            schema=tool.schema,
        )

    planner = LLMPlanner(
        system_prompt=KNOWLEDGE_SYSTEM_PROMPT
    )

    runtime.set_planner(
        planner
    )

    return runtime


# ============================================================
# Production Runtime
# ============================================================

def build_production_runtime() -> AgentRuntime:
    """
    ProductionAgent 独立 Runtime。

    只拥有 MES / Production HTTP Tools。
    """

    runtime = AgentRuntime()

    for tool in get_production_tools():

        runtime.register_tool(
            name=tool.name,
            func=tool.func,
            description=tool.description,
            schema=tool.schema,
        )

    planner = LLMPlanner(
        system_prompt=PRODUCTION_SYSTEM_PROMPT
    )

    runtime.set_planner(
        planner
    )

    return runtime


# ============================================================
# Agent Registry
# ============================================================

def build_agent_registry() -> AgentRegistry:
    """
    构建 Manufacturing AI Copilot Agent Registry。
    """

    registry = AgentRegistry()

    # --------------------------------------------------------
    # LLM Agent
    # --------------------------------------------------------

    llm_runtime = build_llm_runtime()

    llm_agent = LLMAgent(
        llm_runtime
    )

    registry.register(
        "llm",
        llm_agent,
    )

    # --------------------------------------------------------
    # Database Agent
    # --------------------------------------------------------

    database_runtime = build_database_runtime()

    database_agent = DatabaseAgent(
        database_runtime
    )

    registry.register(
        "database",
        database_agent,
    )

    # --------------------------------------------------------
    # Knowledge Agent
    # --------------------------------------------------------

    knowledge_runtime = build_knowledge_runtime()

    knowledge_agent = KnowledgeAgent(
        knowledge_runtime
    )

    registry.register(
        "knowledge",
        knowledge_agent,
    )

    # --------------------------------------------------------
    # Production Agent
    # --------------------------------------------------------

    production_runtime = build_production_runtime()

    production_agent = ProductionAgent(
        production_runtime
    )

    registry.register(
        "production",
        production_agent,
    )

    return registry


# ============================================================
# Workflow
# ============================================================

def build_workflow() -> ManufacturingWorkflow:
    """
    构建 Manufacturing AI Copilot Workflow。

    主执行链：

    用户问题
        ↓
    LLMTaskPlanner
        ↓
    TaskPlan
        ↓
    TaskDispatcher
        ↓
    Agents
        ↓
    TaskResult
        ↓
    Synthesizer
        ↓
    最终回答
    """

    # ========================================================
    # 1. 构建所有业务 Agent
    # ========================================================

    agent_registry = (
        build_agent_registry()
    )

    # ========================================================
    # 2. 构建 LLM Task Planner
    #
    # 负责：
    #
    # 用户问题
    #     ↓
    # TaskPlan
    #
    # 不负责真正执行 Agent。
    # ========================================================

    task_planner = (
        LLMTaskPlanner()
    )

    # ========================================================
    # 3. 构建 Task Dispatcher
    #
    # 负责：
    #
    # - DAG 依赖调度
    # - 独立任务并行执行
    # - 上游结果传递
    # - FAILED 隔离
    # - SKIPPED 传播
    # ========================================================

    task_dispatcher = (
        TaskDispatcher(
            agent_registry=(
                agent_registry
            ),
            max_workers=4,
        )
    )

    # ========================================================
    # 4. 获取通用 LLM Agent
    #
    # Synthesizer 直接复用 Registry 中已经创建好的
    # llm Agent。
    #
    # 不再额外创建第二套 Runtime。
    # ========================================================

    llm_agent = (
        agent_registry.get(
            "llm"
        )
    )

    # ========================================================
    # 5. 构建最终结果综合器
    # ========================================================

    synthesizer = (
        Synthesizer(
            llm_agent=llm_agent
        )
    )

    # ========================================================
    # 6. 构建完整 Workflow
    # ========================================================

    workflow = (
        ManufacturingWorkflow(
            task_planner=(
                task_planner
            ),
            task_dispatcher=(
                task_dispatcher
            ),
            synthesizer=(
                synthesizer
            ),
        )
    )

    return workflow

# ============================================================
# Application Singleton
#
# 模块第一次加载时初始化一次。
#
# 每次请求不会重新创建：
#
# Runtime
# Tool
# Agent
# TaskPlanner
# TaskDispatcher
# Synthesizer
# Workflow
# ============================================================

workflow = build_workflow()