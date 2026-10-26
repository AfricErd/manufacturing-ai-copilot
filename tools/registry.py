from dataclasses import dataclass
from typing import Callable


from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Tool:

    name: str

    description: str

    schema: dict

    func: Callable

    def execute(self, **kwargs) -> Any:
        """
        Tool 对外统一执行入口。

        当前只是简单代理到 Python Function，
        后续 HTTP / SQL / MCP Tool
        都实现 execute() 即可。
        """
        return self.func(**kwargs)


class ToolRegistry:
    """
    工具注册中心

    Runtime 不直接管理 Tool，
    而是通过 ToolRegistry 管理所有工具。
    """

    def __init__(self):

        # tool_name -> python function
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        tool: Tool
    ) -> None:
        """
        注册工具
        """
        self._tools[tool.name] = tool

    def get(
        self,
        name: str
    ) -> Callable:
        """
        获取工具
        """

        if name not in self._tools:
            raise KeyError(
                f"Tool '{name}' 不存在。"
            )

        return self._tools[name]

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._tools

    def list_tools(
        self
    ) :

        return self.to_openai_tools()
    def get_all(self):
        """
        返回所有 Tool 对象
        """

        return list(self._tools.values())
    def names(self):
        """
        返回所有工具名称
        """

        return list(self._tools.keys())
    def to_openai_tools(self):
        """
        导出 OpenAI Compatible Tool Schema
        """

        result = []

        for tool in self._tools.values():

            result.append({

                "type": "function",

                "function": {

                    "name": tool.name,

                    "description": tool.description,

                    "parameters": tool.schema

                }

            })

        return result