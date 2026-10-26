from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query


app = FastAPI(
    title="Mock MES API",
    version="1.0.0",
)


# ============================================================
# Mock MES Data
# ============================================================

PRODUCTION_STATUS = {
    "plant": "示范工厂",
    "status": "Running",
    "running_tasks": 3,
    "delayed_tasks": 1,
    "alarm_equipment": 1,
}


PRODUCTION_TASKS = [
    {
        "task_id": "PT2026001",
        "wo_no": "WO202600001",
        "product_code": "P001",
        "workshop": "冲压车间",
        "planned_qty": 500,
        "completed_qty": 420,
        "status": "Running",
    },
    {
        "task_id": "PT2026002",
        "wo_no": "WO202600002",
        "product_code": "P002",
        "workshop": "焊接车间",
        "planned_qty": 800,
        "completed_qty": 510,
        "status": "Delayed",
    },
    {
        "task_id": "PT2026003",
        "wo_no": "WO202600003",
        "product_code": "P003",
        "workshop": "装配车间",
        "planned_qty": 300,
        "completed_qty": 300,
        "status": "Completed",
    },
    {
        "task_id": "PT2026004",
        "wo_no": "WO202600004",
        "product_code": "P004",
        "workshop": "包装车间",
        "planned_qty": 600,
        "completed_qty": 260,
        "status": "Running",
    },
]


EQUIPMENT_STATUS = {
    "EQ001": {
        "equipment_no": "EQ001",
        "equipment_name": "激光切割机",
        "workshop": "冲压车间",
        "status": "Running",
        "alarm_code": "",
    },
    "EQ002": {
        "equipment_no": "EQ002",
        "equipment_name": "焊接机器人",
        "workshop": "焊接车间",
        "status": "Alarm",
        "alarm_code": "E205",
    },
    "EQ003": {
        "equipment_no": "EQ003",
        "equipment_name": "AGV",
        "workshop": "装配车间",
        "status": "Idle",
        "alarm_code": "",
    },
}


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health():

    return {
        "success": True,
        "service": "mock-mes",
        "status": "ok",
    }


# ============================================================
# Production Status
# ============================================================

@app.get("/api/production/status")
def get_production_status():

    return {
        "success": True,
        "data": PRODUCTION_STATUS,
    }


# ============================================================
# Production Tasks
# ============================================================

@app.get("/api/production/tasks")
def get_production_tasks(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):

    data = PRODUCTION_TASKS[:limit]

    return {
        "success": True,
        "returned": len(data),
        "data": data,
    }


# ============================================================
# Equipment Status
# ============================================================

@app.get(
    "/api/equipment/{equipment_no}/status"
)
def get_equipment_status(
    equipment_no: str,
):

    equipment = EQUIPMENT_STATUS.get(
        equipment_no.upper()
    )

    if equipment is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Equipment "
                f"'{equipment_no}' not found."
            ),
        )

    return {
        "success": True,
        "data": equipment,
    }