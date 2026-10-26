import json
from datetime import datetime
from runtime.action import ToolAction
from runtime.observation import Observation
from runtime.event import ToolExecutedEvent

class Executor:
    """
    Agent Tool Executor

    职责：

    1. 接收 Tool Call
    2. 从 ToolRegistry 查找工具
    3. 执行工具
    4. 生成 Observation
    5. 更新 State
    6. 写入 Trace
    """


    def __init__(
        self,
        registry,
        state,
        trace
    ):

        self.registry = registry
        self.state = state
        self.trace = trace



    def execute(self, action: ToolAction):
        """
        执行一次工具调用

        """


        tool_name = action.tool_name

        arguments = action.arguments


        # -----------------------
        # Trace
        # -----------------------

        self.trace.add(
            step=self.state.step,
            role="executor",
            content=f"准备执行工具:{tool_name}"
        )


        try:


            # -----------------------
            # 查找Tool
            # -----------------------

            tool = self.registry.get(
                tool_name
            )


            # -----------------------
            # 执行
            # -----------------------

            result = tool.execute(
                **arguments
            )


            observation = Observation(

                tool_name=
                    tool_name,

                success=
                    True,

                result=
                    result,

                error=
                    None
            )



        except Exception as e:


            observation = Observation(

                tool_name=
                    tool_name,

                success=
                    False,

                result=
                    None,

                error=
                    str(e)
            )


        # -----------------------
        # 更新State
        # -----------------------

        self.state.last_observation = observation



        # -----------------------
        # Trace
        # -----------------------

        self.trace.add(
            step=self.state.step,
            role="observation",
            content=str(observation)
        )
        event = ToolExecutedEvent(

            name="tool.executed",

            timestamp=datetime.now(),

            tool_name=tool_name,

            success=observation.success
        )
        print("工具执行事件:")
        print(event)
        return observation
    
    def execute_batch(
        self,
        actions: list[ToolAction],
    ) -> list[Observation]:

        observations = []

        for action in actions:

            observation = self.execute(action)

            observations.append(observation)

        return observations
    