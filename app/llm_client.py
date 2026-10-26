from app.config import (
    DASHSCOPE_API_KEY,
    LLM_API_TIMEOUT,
    MODEL_NAME,
)


class LLMClient:
    """
    项目统一 LLM Client。

    负责：

    1. OpenAI-compatible API 初始化
    2. 统一模型配置
    3. 统一网络 timeout
    4. 提供普通 Chat / Tool Calling 调用入口
    """

    def __init__(
        self,
    ):

        # ====================================================
        # Lazy Import
        #
        # 只有真正创建 LLMClient 时，
        # 才要求 OpenAI SDK 已安装。
        # ====================================================

        try:

            from openai import OpenAI

        except ImportError as exc:

            raise RuntimeError(
                "缺少 openai 依赖，"
                "请先安装 requirements.txt。"
            ) from exc

        self.client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=(
                "https://ws-3injdeoc2biyn3gq."
                "cn-beijing.maas.aliyuncs.com/"
                "compatible-mode/v1"
            ),
            timeout=LLM_API_TIMEOUT,
            max_retries=1,
        )


    def complete(
        self,
        messages: list[dict],
        tools: list | None = None,
    ):

        request_kwargs = {
            "model": MODEL_NAME,
            "messages": messages,
        }

        if tools:

            request_kwargs[
                "tools"
            ] = tools

        response = (
            self.client
            .chat.completions
            .create(
                **request_kwargs
            )
        )

        return (
            response
            .choices[0]
            .message
        )