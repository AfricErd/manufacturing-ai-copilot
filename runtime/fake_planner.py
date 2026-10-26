from runtime.planner import Planner
from runtime.action import ToolAction
from runtime.action import FinishAction


class FakePlanner(Planner):

    def plan(self, context):

        if context.observation is None:

            return ToolAction(

                tool_name="fake_tool",

                arguments={

                    "name":"runtime"

                }

            )

        return FinishAction(

            answer="runtime finished"

        )