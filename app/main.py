import logging
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bootstrap import workflow


# ============================================================
# Logging
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# Path
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

STATIC_DIR = (
    PROJECT_ROOT
    / "static"
)

INDEX_FILE = (
    STATIC_DIR
    / "index.html"
)


# ============================================================
# Request Model
# ============================================================

class ChatRequest(BaseModel):
    """
    Web Dashboard 请求模型。
    """

    question: str


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="Manufacturing AI Copilot",
    version="1.0.0",
)


# ============================================================
# Static Files
#
# Web UI 后面会放到：
#
# static/
#   index.html
#   style.css
#   app.js
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR),

        # 现在 static 目录可能还没创建，
        # 所以先不要因为目录不存在阻止 API 启动。
        check_dir=False,
    ),
    name="static",
)


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health():

    return {
        "success": True,
        "service":
            "manufacturing-ai-copilot",
        "status": "ok",
    }


# ============================================================
# Web Home
# ============================================================

@app.get("/")
def home():
    """
    Web UI 创建完成以后，
    直接访问 http://127.0.0.1:8000/
    即可打开 Dashboard。
    """

    if INDEX_FILE.exists():

        return FileResponse(
            INDEX_FILE
        )

    # Web UI 尚未创建时仍允许 API 正常启动。
    return {
        "message":
            "Manufacturing AI Copilot running",

        "web_ui":
            "static/index.html not created yet",
    }


# ============================================================
# Legacy / Simple Chat API
# ============================================================

@app.post("/chat")
def chat_api(
    question: str,
):
    """
    保留 Day13 之前的简单 Chat API。

    不删除，避免破坏已有调用方式。
    """

    response = workflow.run(
        question
    )

    return {
        "question": question,
        "answer": response,
    }


# ============================================================
# Detailed Workflow API
# ============================================================

@app.post("/api/chat")
def detailed_chat_api(
    request: ChatRequest,
):
    """
    Web Dashboard 使用的详细接口。

    这里只负责把 Workflow 已经存在的：

    TaskPlan
    TaskResult
    Final Answer

    转换成前端可以直接展示的 JSON。

    不参与：
    - Task Planning
    - DAG Scheduling
    - Agent Execution
    - Failure Propagation
    """

    question = (
        request.question.strip()
    )

    if not question:

        raise HTTPException(
            status_code=400,
            detail="question 不能为空。",
        )

    # --------------------------------------------------------
    # 记录一次完整 Workflow 耗时
    # --------------------------------------------------------

    start_time = (
        time.perf_counter()
    )

    try:

        state = (
            workflow.run_detailed(
                question
            )
        )

    except Exception as exc:

        # 完整异常写到后端日志，
        # 不直接把内部异常堆栈暴露到前端。
        logger.exception(
            "Manufacturing workflow execution failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Workflow 执行失败，"
                "请查看后端日志。"
            ),
        ) from exc

    duration_ms = round(
        (
            time.perf_counter()
            - start_time
        )
        * 1000,
        2,
    )

    # --------------------------------------------------------
    # 从 WorkflowState 中取现有结果
    # --------------------------------------------------------

    plan = state[
        "task_plan"
    ]

    task_results = state[
        "task_results"
    ]

    tasks = []

    # --------------------------------------------------------
    # 按 TaskPlan 顺序组织结果
    #
    # 不直接遍历 task_results，
    # 因为 Dashboard 更适合按照计划顺序显示。
    # --------------------------------------------------------

    for task in plan.tasks:

        result = (
            task_results.get(
                task.task_id
            )
        )

        task_item = {
            "task_id":
                task.task_id,

            "description":
                task.description,

            "agent_name":
                task.agent_name,

            "dependencies":
                list(
                    task.dependencies
                ),

            "status":
                "missing",

            "success":
                False,

            "answer":
                "",

            "data":
                {},

            "error":
                None,
        }

        if result is not None:

            result_data = (
                result.to_dict()
            )

            task_item[
                "status"
            ] = result_data[
                "status"
            ]

            task_item[
                "success"
            ] = result_data[
                "success"
            ]

            task_item[
                "answer"
            ] = result_data[
                "answer"
            ]

            task_item[
                "data"
            ] = result_data[
                "data"
            ]

            task_item[
                "error"
            ] = result_data[
                "error"
            ]

        tasks.append(
            task_item
        )

    # --------------------------------------------------------
    # 前端最终数据结构
    # --------------------------------------------------------

    return {
        "question":
            question,

        "answer":
            state[
                "final_answer"
            ],

        "duration_ms":
            duration_ms,

        "tasks":
            tasks,
    } 