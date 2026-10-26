from connection import get_connection
from faker import Faker
import random

fake = Faker("zh_CN")


def seed_sales_orders(cursor):
    for i in range(1, 21):
        cursor.execute(
            """
        INSERT INTO sales_orders
        (so_no, customer, product_code, product_name, order_qty, due_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"SO202600{i:03}",
                random.choice(["比亚迪", "宁德时代", "特斯拉", "上汽集团", "广汽"]),
                f"P{i:03}",
                random.choice(["电池包", "电机", "控制器", "减速器"]),
                random.randint(100, 1000),
                fake.date_between(start_date="today", end_date="+30d"),
                random.choice(["Open", "Released", "Completed"]),
                fake.date_time_this_year(),
            ),
        )


def seed_work_orders(cursor):
    for i in range(1, 21):
        cursor.execute(
            """
        INSERT INTO work_orders
        (wo_no, so_no, product_code, planned_qty, completed_qty, status, workshop, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"WO202600{i:03}",
                f"SO202600{i:03}",
                f"P{i:03}",
                random.randint(100, 1000),
                random.randint(0, 1000),
                random.choice(["Released", "Running", "Completed"]),
                random.choice(["冲压车间", "焊接车间", "装配车间", "包装车间"]),
                fake.date_time_this_year(),
            ),
        )


def seed_material(cursor):
    for i in range(1, 51):
        cursor.execute(
            """
        INSERT INTO material_issues
        (wo_no, material_code, material_name, required_qty, issued_qty, issue_status, issue_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"WO202600{random.randint(1, 20):03}",
                f"M{i:03}",
                random.choice(["钢板", "轴承", "螺丝", "PCB", "外壳"]),
                random.randint(10, 200),
                random.randint(10, 200),
                random.choice(["未领料", "部分领料", "已领料"]),
                fake.date_time_this_year(),
            ),
        )


def seed_operations(cursor):
    for i in range(100):
        cursor.execute(
            """
        INSERT INTO operations
        (wo_no, operation_name, work_center, operator, start_time, end_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"WO202600{random.randint(1, 20):03}",
                random.choice(["下料", "冲压", "焊接", "喷涂", "装配", "包装"]),
                random.choice(["WC01", "WC02", "WC03", "WC04"]),
                fake.name(),
                fake.date_time_this_year(),
                fake.date_time_this_year(),
                random.choice(["Waiting", "Running", "Finished"]),
            ),
        )


def seed_inventory(cursor):
    for i in range(1, 31):
        cursor.execute(
            """
        INSERT INTO inventory
        (material_code, material_name, warehouse, quantity, safety_stock)
        VALUES (?, ?, ?, ?, ?)
        """,
            (
                f"M{i:03}",
                random.choice(["钢板", "轴承", "螺丝", "PCB", "外壳"]),
                random.choice(["A仓", "B仓", "C仓"]),
                random.randint(100, 5000),
                random.randint(50, 500),
            ),
        )


def seed_outbound(cursor):
    for i in range(1, 16):
        cursor.execute(
            """
        INSERT INTO outbound_shipments
        (so_no, shipment_no, shipped_qty, shipment_date, status)
        VALUES (?, ?, ?, ?, ?)
        """,
            (
                f"SO202600{i:03}",
                f"OUT202600{i:03}",
                random.randint(50, 1000),
                fake.date_time_this_year(),
                random.choice(["待出库", "已出库"]),
            ),
        )


def seed_equipment(cursor):
    for i in range(1, 21):
        cursor.execute(
            """
        INSERT INTO equipment_status
        (equipment_no, equipment_name, workshop, status, alarm_code, last_update)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                f"EQ{i:03}",
                random.choice(["激光切割机", "冲床", "机器人", "焊机", "AGV"]),
                random.choice(["冲压车间", "焊接车间", "装配车间"]),
                random.choice(["Running", "Idle", "Alarm"]),
                random.choice(["", "", "", "E101", "E205", "E310"]),
                fake.date_time_this_year(),
            ),
        )


def main():
    conn = get_connection()
    cursor = conn.cursor()

    seed_sales_orders(cursor)
    seed_work_orders(cursor)
    seed_material(cursor)
    seed_operations(cursor)
    seed_inventory(cursor)
    seed_outbound(cursor)
    seed_equipment(cursor)

    conn.commit()
    conn.close()

    print("模拟企业数据生成完成！")


if __name__ == "__main__":
    main()
