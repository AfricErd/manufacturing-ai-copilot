from typing import TypedDict

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from workflow.task import (
    TaskPlan,
    TaskResult,
)


class WorkflowState(
    TypedDict,
    total=False,
):
    """
    ManufacturingWorkflow 在 LangGraph
    节点之间传递的状态。
    """

    question: str

    task_plan: TaskPlan

    task_results: dict[
        str,
        TaskResult,
    ]

    final_answer: str


class ManufacturingWorkflow:
    """
    制造业 AI Copilot 主工作流。

    主流程：

    用户问题
        ↓
    LLM Task Planner
        ↓
    TaskPlan
        ↓
    TaskDispatcher
        ↓
    TaskResult
        ↓
    Synthesizer
        ↓
    Final Answer
    """

    def __init__(
        self,
        task_planner,
        task_dispatcher,
        synthesizer,
    ):
        self.task_planner = (
            task_planner
        )

        self.task_dispatcher = (
            task_dispatcher
        )

        self.synthesizer = (
            synthesizer
        )

        self.graph = (
            self._build_graph()
        )


    def _build_graph(
        self,
    ):
        """
        构建 LangGraph Workflow。
        """

        builder = StateGraph(
            WorkflowState
        )

        # ==================================================
        # 注册节点
        # ==================================================

        builder.add_node(
            "plan",
            self._plan_node,
        )

        builder.add_node(
            "dispatch",
            self._dispatch_node,
        )

        builder.add_node(
            "synthesize",
            self._synthesize_node,
        )

        # ==================================================
        # 定义主执行路径
        #
        # START
        #   ↓
        # plan
        #   ↓
        # dispatch
        #   ↓
        # synthesize
        #   ↓
        # END
        # ==================================================

        builder.add_edge(
            START,
            "plan",
        )

        builder.add_edge(
            "plan",
            "dispatch",
        )

        builder.add_edge(
            "dispatch",
            "synthesize",
        )

        builder.add_edge(
            "synthesize",
            END,
        )

        return builder.compile()


    def _plan_node(
        self,
        state: WorkflowState,
    ):
        """
        将用户问题转换成经过验证的 TaskPlan。
        """

        question = state[
            "question"
        ]

        plan = (
            self.task_planner
            .create_plan(
                question
            )
        )

        return {
            "task_plan": plan,
        }


    def _dispatch_node(
        self,
        state: WorkflowState,
    ):
        """
        执行 TaskPlan。

        dependency 调度、并行执行、
        FAILED / SKIPPED 传播，
        全部由 TaskDispatcher 负责。

        Workflow 本身不参与具体调度。
        """

        plan = state[
            "task_plan"
        ]

        task_results = (
            self.task_dispatcher
            .dispatch(
                plan
            )
        )

        return {
            "task_results":
                task_results,
        }


    def _synthesize_node(
        self,
        state: WorkflowState,
    ):
        """
        综合全部 TaskResult，
        生成最终面向用户的答案。
        """

        question = state[
            "question"
        ]

        plan = state[
            "task_plan"
        ]

        task_results = state[
            "task_results"
        ]

        final_answer = (
            self.synthesizer
            .synthesize(
                question=question,
                plan=plan,
                task_results=(
                    task_results
                ),
            )
        )

        return {
            "final_answer":
                final_answer,
        }


    def run(
        self,
        question: str,
    ) -> str:
        """
        执行一次完整 Workflow。

        保留简单的字符串返回形式，
        方便现有 API / CLI 继续使用。
        """

        if not question.strip():

            raise ValueError(
                "question 不能为空。"
            )

        final_state = (
            self.graph.invoke(
                {
                    "question":
                        question,
                }
            )
        )

        return final_state[
            "final_answer"
        ]


    def run_detailed(
        self,
        question: str,
    ) -> WorkflowState:
        """
        返回完整 Workflow State。

        主要供：

        - 调试
        - 测试
        - Trace
        - 前端任务执行详情

        使用。
        """

        if not question.strip():

            raise ValueError(
                "question 不能为空。"
            )

        final_state = (
            self.graph.invoke(
                {
                    "question":
                        question,
                }
            )
        )

        return final_state