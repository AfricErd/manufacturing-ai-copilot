import json

from database.service import (
    get_sales_orders,
    get_customer_orders,
    get_work_orders,

    count_sales_orders as db_count_sales_orders,
    count_customer_orders as db_count_customer_orders,
    count_work_orders as db_count_work_orders,
)


def _rows_to_json(rows):
    """
    将 sqlite3.Row 列表转换成 JSON 字符串
    """
    result = [dict(row) for row in rows]

    return json.dumps(
        {
            "success": True,
            "returned": len(result),
            "data": result
        },
        ensure_ascii=False
    )

def _count_to_json(rows):
    """
    将统计结果转换为 JSON
    """

    result = [dict(row) for row in rows]

    return json.dumps(
        {
            "success": True,
            "total": result[0]["total"] if result else 0
        },
        ensure_ascii=False
    )


def query_sales_orders(limit: int = 10) -> str:
    """
    查询销售订单列表。
    """
    print(
        f"\n[Data Tool] 查询销售订单，limit={limit}"
    )

    rows = get_sales_orders(limit)

    return _rows_to_json(rows)


def query_customer_orders(customer: str) -> str:
    """
    根据客户名称查询销售订单。
    """
    print(
        f"\n[Data Tool] 查询客户订单：{customer}"
    )

    rows = get_customer_orders(customer)

    return _rows_to_json(rows)


def query_work_orders(limit: int = 10) -> str:
    """
    查询生产工单列表。
    """
    print(
        f"\n[Data Tool] 查询生产工单，limit={limit}"
    )

    rows = get_work_orders(limit)

    return _rows_to_json(rows)

def count_sales_orders() -> str:
    """
    查询销售订单总数量。
    """

    print(
        "\n[Data Tool] 统计销售订单数量"
    )

    rows = db_count_sales_orders()

    return _count_to_json(rows)

def count_customer_orders(customer: str) -> str:
    """
    根据客户名称统计订单数量。
    """

    print(
        f"\n[Data Tool] 统计客户订单数量：{customer}"
    )

    rows = db_count_customer_orders(customer)

    return _count_to_json(rows)
def count_work_orders() -> str:
    """
    查询生产工单总数量。
    """

    print(
        "\n[Data Tool] 统计生产工单数量"
    )

    rows = db_count_work_orders()

    return _count_to_json(rows)