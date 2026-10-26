from database.query import execute_query




def get_sales_orders(limit=10):
    """
    查询销售订单
    """

    sql = """
    SELECT 
        so_no,
        customer,
        product_name,
        order_qty
    FROM sales_orders
    LIMIT ?
    """

    return execute_query(
        sql,
        (limit,)
    )

def count_sales_orders():
    """
    统计销售订单数量
    """

    sql = """
    SELECT COUNT(*) as total
    FROM sales_orders
    """

    return execute_query(sql)


def get_customer_orders(customer):
    """
    根据客户查询订单
    """

    sql = """
    SELECT
        so_no,
        customer,
        product_name,
        order_qty
    FROM sales_orders
    WHERE customer = ?
    """

    return execute_query(
        sql,
        (customer,)
    )
def count_customer_orders(customer):
    """
    根据客户统计订单数量
    """

    sql = """
    SELECT COUNT(*) as total
    FROM sales_orders
    WHERE customer = ?
    """

    return execute_query(
        sql,
        (customer,)
    )


def get_work_orders(limit=30):

    sql = """
    SELECT *
    FROM work_orders
    LIMIT ?
    """

    return execute_query(
        sql,
        (limit,)
    )
def count_work_orders():
    """
    统计生产工单数量
    """

    sql = """
    SELECT COUNT(*) as total
    FROM work_orders
    """

    return execute_query(sql)