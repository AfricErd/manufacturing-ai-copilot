from database.connection import get_connection


def execute_query(sql, params=None):
    """
    执行数据库查询
    """

    conn = get_connection()

    cursor = conn.cursor()

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    rows = cursor.fetchall()

    conn.close()

    return rows