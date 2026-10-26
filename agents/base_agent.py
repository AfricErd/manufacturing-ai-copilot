from abc import ABC
from abc import abstractmethod

from workflow.agent_result import AgentResult


class BaseAgent(ABC):
    """
    所有业务 Agent 的基础类。

    AgentRuntime 负责真正执行：
    - LLM
    - Tool Calling
    - ReAct / Runtime Loop

    BaseAgent 主要负责把 Runtime 的最终状态
    转换成 Workflow 可以识别的 AgentResult。
    """

    @abstractmethod
    def run(
        self,
        question: str,
    ):
        pass


    def _build_agent_result(
        self,
        agent_name: str,
        state,
    ) -> AgentResult:
        """
        将 AgentRuntime 返回的 AgentState
        转换成统一 AgentResult。

        关键规则：

        1. 没有 Tool Observation：
           认为是普通 LLM 成功执行。

        2. Tool Observation 全部成功：
           Agent success=True。

        3. 任意 Tool Observation 失败：
           Agent success=False。

        这样可以保证：

        Tool Failed
            ↓
        Agent Failed
            ↓
        Task FAILED
            ↓
        Downstream SKIPPED
        """

        answer = state.answer or ""

        # ====================================================
        # Runtime 自身已经明确失败
        # ====================================================

        if state.status == "failed":

            return AgentResult(
                agent_name=agent_name,
                success=False,
                answer=answer,
                error="Agent Runtime 执行失败。",
            )

        observation = (
            state.last_observation
        )

        # ====================================================
        # 没有调用 Tool
        #
        # 例如普通 LLMAgent。
        # ====================================================

        if observation is None:

            return AgentResult(
                agent_name=agent_name,
                success=True,
                answer=answer,
            )

        # ====================================================
        # 统一转换成 list
        #
        # 单工具：
        # Observation
        #
        # 多工具：
        # list[Observation]
        # ====================================================

        if isinstance(
            observation,
            list,
        ):
            observations = observation

        else:
            observations = [
                observation
            ]

        observation_data = []

        failed_errors = []

        # ====================================================
        # 检查所有 Tool Observation
        # ====================================================

        for item in observations:

            tool_name = getattr(
                item,
                "tool_name",
                "unknown_tool",
            )

            success = getattr(
                item,
                "success",
                False,
            )

            result = getattr(
                item,
                "result",
                None,
            )

            error = getattr(
                item,
                "error",
                None,
            )

            observation_data.append(
                {
                    "tool_name": tool_name,
                    "success": success,
                    "result": result,
                    "error": error,
                }
            )

            if not success:

                if error:
                    error_message = (
                        f"{tool_name}: {error}"
                    )

                else:
                    error_message = (
                        f"{tool_name}: "
                        "工具执行失败，"
                        "但没有返回错误信息。"
                    )

                failed_errors.append(
                    error_message
                )

        # ====================================================
        # 任意 Tool 失败
        # → 整个当前 Agent Task 失败
        # ====================================================

        if failed_errors:

            return AgentResult(
                agent_name=agent_name,
                success=False,
                answer=answer,
                data={
                    "observations":
                        observation_data, 
                },
                error="; ".join(
                    failed_errors
                ),
            )

        # ====================================================
        # 所有 Tool 都成功
        # ====================================================

        return AgentResult(
            agent_name=agent_name,
            success=True,
            answer=answer,
            data={
                "observations":
                    observation_data,
            },
        )