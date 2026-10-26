import dashscope
from app.config import DASHSCOPE_API_KEY, EMBEDDING_MODEL

dashscope.api_key = DASHSCOPE_API_KEY


def get_embedding(text: str):
    response = dashscope.TextEmbedding.call(
        model=EMBEDDING_MODEL,
        input=text
    )

    if response.status_code == 200:
        return response.output["embeddings"][0]["embedding"]
    else:
        raise Exception(response.message)