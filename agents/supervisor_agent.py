import re

from agents.agent_registry import AgentRegistry


class SupervisorAgent:

    def __init__(
        self,
        agent_registry: AgentRegistry,
    ):

        self.agent_registry = agent_registry


    def select_agent(
        self,
        question: str,
    ) -> str:
        """
        根据用户问题选择合适的 Agent。

        当前采用稳定的规则路由。
        后续可升级为 Router LLM。
        """

        # ====================================================
        # Production 实时查询
        #
        # 对明显的实时 MES 请求优先识别。
        # ====================================================

        production_keywords = [
            "生产状态",
            "生产运行",
            "生产任务",
            "生产进度",
            "设备状态",
            "设备运行",
            "设备告警",
            "设备报警",
        ]

        production_query_markers = [
            "当前",
            "现在",
            "实时",
            "查询",
            "查看",
            "检查",
            "获取",
            "哪些",
            "多少",
            "进度",
            "告警",
            "报警",
        ]

        has_production_keyword = any(
            keyword in question
            for keyword in production_keywords
        )

        has_production_query_marker = any(
            marker in question
            for marker in production_query_markers
        )

        # ----------------------------------------------------
        # 明确的设备编号，例如 EQ001 / EQ002
        # ----------------------------------------------------

        if re.search(
            r"(?<![A-Z0-9])EQ\d+(?![A-Z0-9])",
            question.upper(),
        ):
            return "production"


        # ----------------------------------------------------
        # 明确要求查询实时生产数据
        # ----------------------------------------------------

        if (
            has_production_keyword
            and has_production_query_marker
        ):
            return "production"


        # ====================================================
        # Knowledge
        #
        # 概念、定义、解释类问题仍然优先进入知识库。
        # ====================================================

        knowledge_keywords = [
            "是什么",
            "什么是",
            "什么意思",
            "解释",
            "介绍",
            "定义",
            "概念",
        ]

        for keyword in knowledge_keywords:

            if keyword in question:
                return "knowledge"


        # ====================================================
        # Production
        #
        # 没有明显知识解释意图，但属于生产执行态信息。
        # ====================================================

        if has_production_keyword:
            return "production"


        # ====================================================
        # Database
        # ====================================================

        database_keywords = [
            "销售订单",
            "客户订单",
            "生产工单",
            "订单",
            "工单",
        ]

        for keyword in database_keywords:

            if keyword in question:
                return "database"


        # ====================================================
        # Default LLM
        # ====================================================

        return "llm"



    def select_agents(
        self,
        question: str,
    ) -> list[str]:
        """
        为 Day12 Multi-Agent Collaboration 生成 Agent 执行计划。

        简单任务：
            保持现有 select_agent() 单 Agent 路由。

        复合任务：
            返回需要协作的多个 Agent。

        当前方法只负责 Agent Selection，
        不负责真正执行 Agent。
        """

        # ----------------------------------------------------
        # Normalize question
        #
        # 允许：
        # "MES 状态"
        # "MES状态"
        #
        # 使用同一套关键词判断。
        # ----------------------------------------------------

        normalized_question = re.sub(
            r"\s+",
            "",
            question,
        )

        upper_question = (
            normalized_question.upper()
        )

        # ====================================================
        # Database capability signals
        # ====================================================

        database_keywords = [
            "销售订单",
            "客户订单",
            "生产工单",
            "订单",
            "工单",
        ]

        # ====================================================
        # Production capability signals
        #
        # 这里描述的是实时生产执行域。
        # 不使用简单的 "生产" 关键词，
        # 避免把 "生产工单" 错误路由到 Production。
        # ====================================================

        production_keywords = [
            "生产状态",
            "生产运行",
            "生产任务",
            "生产进度",
            "生产异常",
            "生产风险",
            "设备状态",
            "设备运行",
            "设备告警",
            "设备报警",
            "MES状态",
            "MES运行",
            "MES告警",
            "MES报警",
            "实时生产",
        ]

        # ====================================================
        # Knowledge capability signals
        #
        # 这里只识别明确要求企业知识 / SOP 的复合任务。
        #
        # 不把：
        # "是什么"
        # "定义"
        #
        # 放进这里。
        #
        # 否则：
        # "生产工单是什么"
        #
        # 会被错误识别为：
        # database + knowledge
        # ====================================================

        knowledge_keywords = [
            "SOP",
            "知识库",
            "操作规程",
            "作业指导书",
            "处理规范",
            "处置规范",
            "工艺规范",
            "设备原理",
        ]

        selected_agents = []

        # ====================================================
        # Database
        # ====================================================

        if any(
            keyword in normalized_question
            for keyword in database_keywords
        ):
            selected_agents.append(
                "database"
            )

        # ====================================================
        # Production
        # ====================================================

        has_equipment_no = (
            re.search(
                r"(?<![A-Z0-9])EQ\d+(?![A-Z0-9])",
                upper_question,
            )
            is not None
        )

        if (
            has_equipment_no
            or any(
                keyword in normalized_question
                for keyword in production_keywords
            )
        ):
            selected_agents.append(
                "production"
            )

        # ====================================================
        # Knowledge
        # ====================================================

        if any(
            keyword in upper_question
            for keyword in knowledge_keywords
        ):
            selected_agents.append(
                "knowledge"
            )

        # ====================================================
        # Multi-Agent Collaboration
        #
        # 两个及以上能力域命中：
        # 认为这是复合任务。
        # ====================================================

        if len(selected_agents) >= 2:
            return selected_agents

        # ====================================================
        # Single-Agent backward compatibility
        #
        # 如果没有形成复合任务，
        # 完全复用 Day11 已经验证过的 select_agent()。
        # ====================================================

        return [
            self.select_agent(
                question
            )
        ]
    
    
     
    def run(
        self,
        agent_name: str,
        question: str,
    ):

        agent = self.agent_registry.get(
            agent_name
        )

        return agent.run(
            question
        )