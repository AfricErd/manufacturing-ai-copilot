from openai import OpenAI

from app.config import (
    DASHSCOPE_API_KEY,
    MODEL_NAME
)


client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://ws-3injdeoc2biyn3gq.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)


def chat(prompt: str):

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

def chat_with_context(
    question,
    context
):
    prompt = f"""
你是一名专业的制造业AI助手。

请严格依据下面提供的知识回答问题。

如果知识中没有相关内容，请直接回答：

"知识库中没有相关信息。"

========================
知识：

{context}

========================

用户问题：

{question}

请给出准确、专业、简洁的回答。
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content

def chat_with_tools(messages, tools):
    """
    支持 Function Calling 的 LLM 调用
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    return response.choices[0].message