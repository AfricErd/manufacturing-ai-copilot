import os

from dotenv import load_dotenv


load_dotenv()


DASHSCOPE_API_KEY = os.getenv(
    "DASHSCOPE_API_KEY"
)


MODEL_NAME = os.getenv(
    "MODEL_NAME",
)


EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "qwen3.7-text-embedding-flash",
)

# ============================================================
# LLM 配置
# ============================================================

LLM_API_TIMEOUT = float(
    os.getenv(
        "LLM_API_TIMEOUT",
        "45",
    )
)


# ============================================================
# MES 配置
# ============================================================

MES_API_BASE_URL = os.getenv(
    "MES_API_BASE_URL",
    "http://127.0.0.1:8001",
)


MES_API_TIMEOUT = float(
    os.getenv(
        "MES_API_TIMEOUT",
        "5",
    )
)