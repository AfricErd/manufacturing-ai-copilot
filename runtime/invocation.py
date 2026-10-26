from runtime.action import (
    BatchToolAction,
    FinishAction,
    ToolAction,
)
from runtime.context import AgentContext
from runtime.executor import Executor
from runtime.state import AgentState
from runtime.trace import AgentTrace


class RuntimeInvocation:
    """
    One isolated execution of an AgentRuntime.

    RuntimeInvocation owns all mutable execution state for a single
    request. It is intentionally single-use so concurrent requests never
    share AgentState, AgentTrace, or Executor instances.
    """

    MAX_STEPS = 10

    def __init__(
        self,
        question: str,
        registry,
        planner,
    ):
        self.registry = registry
        self.planner = planner

        self.state = AgentState(
            question=question,
            status="running",
        )

        self.trace = AgentTrace()

        self.executor = Executor(
            registry=self.registry,
            state=self.state,
            trace=self.trace,
        )

        self._started = False

    def get_context(self) -> AgentContext:
        return AgentContext(
            question=self.state.question,
            goal=self.state.current_goal,
            observation=self.state.last_observation,
            tools=self.registry.list_tools(),
        )

    def add_trace(
        self,
        role: str,
        content: str,
    ) -> None:
        self.trace.add(
            self.state.step,
            role,
            content,
        )

    def finish(
        self,
        answer: str,
    ) -> None:
        self.state.answer = answer
        self.state.finished = True
        self.state.status = "finished"

    def execute_tool(
        self,
        action: ToolAction,
    ):
        return self.executor.execute(
            action
        )

    def run(self) -> AgentState:
        if self._started:
            raise RuntimeError(
                "RuntimeInvocation is single-use. "
                "Create a new invocation for each request."
            )

        if self.planner is None:
            raise RuntimeError(
                "Runtime planner has not been configured."
            )

        self._started = True

        self.add_trace(
            "runtime",
            "runtime started",
        )

        try:
            while not self.state.finished:
                context = self.get_context()

                action = self.planner.plan(
                    context
                )

                self.add_trace(
                    "planner",
                    f"generated {action.__class__.__name__}",
                )

                if isinstance(
                    action,
                    FinishAction,
                ):
                    self.finish(
                        action.answer
                    )

                    self.add_trace(
                        "runtime",
                        "runtime finished",
                    )

                    break

                if isinstance(
                    action,
                    ToolAction,
                ):
                    observation = self.execute_tool(
                        action
                    )

                    if observation.success:
                        self.add_trace(
                            "executor",
                            (
                                f"tool {action.tool_name} "
                                "executed successfully"
                            ),
                        )
                    else:
                        self.add_trace(
                            "executor",
                            (
                                f"tool {action.tool_name} failed: "
                                f"{observation.error}"
                            ),
                        )

                    self._advance_step()
                    continue

                if isinstance(
                    action,
                    BatchToolAction,
                ):
                    observations = (
                        self.executor.execute_batch(
                            action.actions
                        )
                    )

                    self.state.last_observation = (
                        observations
                    )

                    self._advance_step()
                    continue

                raise TypeError(
                    "计划器返回了不支持的动作类型: "
                    f"{type(action).__name__}"
                )

        except Exception:
            self.state.status = "failed"
            raise

        return self.state

    def _advance_step(self) -> None:
        self.state.step += 1

        if self.state.step >= self.MAX_STEPS:
            raise RuntimeError(
                "规划器超过最大运行时步骤。"
            )