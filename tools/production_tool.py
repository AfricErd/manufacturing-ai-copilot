import json

import httpx

from app.config import (
    MES_API_BASE_URL,
    MES_API_TIMEOUT,
)


def _mes_get(
    path: str,
    params: dict | None = None,
) -> str:
    """
    调用 MES HTTP API。

    HTTP 请求失败时直接抛出异常，
    由现有 Executor 统一转换为失败 Observation。
    """

    url = (
        f"{MES_API_BASE_URL.rstrip('/')}"
        f"{path}"
    )

    response = httpx.get(
        url,
        params=params,
        timeout=MES_API_TIMEOUT,
    )

    response.raise_for_status()

    return json.dumps(
        response.json(),
        ensure_ascii=False,
    )



def get_production_status() -> str:
    """
    查询当前工厂生产运行状态。
    """

    return _mes_get(
        "/api/production/status"
    )


def query_production_tasks(
    limit: int = 10,
) -> str:
    """
    查询 MES 中的生产任务。
    """

    return _mes_get(
        "/api/production/tasks",
        params={
            "limit": limit,
        },
    )


def query_equipment_status(
    equipment_no: str,
) -> str:
    """
    查询指定设备的实时状态。
    """

    return _mes_get(
        (
            f"/api/equipment/"
            f"{equipment_no}/status"
        )
    )