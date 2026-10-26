from connection import get_connection


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        so_no TEXT NOT NULL UNIQUE,
        customer TEXT NOT NULL,
        product_code TEXT NOT NULL,
        product_name TEXT NOT NULL,
        order_qty INTEGER NOT NULL,
        due_date TEXT,
        status TEXT NOT NULL,
        created_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wo_no TEXT NOT NULL UNIQUE,
        so_no TEXT NOT NULL,
        product_code TEXT NOT NULL,
        planned_qty INTEGER NOT NULL,
        completed_qty INTEGER DEFAULT 0,
        status TEXT NOT NULL,
        workshop TEXT,
        created_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS material_issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wo_no TEXT NOT NULL,
        material_code TEXT NOT NULL,
        material_name TEXT NOT NULL,
        required_qty REAL,
        issued_qty REAL,
        issue_status TEXT,
        issue_time TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wo_no TEXT NOT NULL,
        operation_name TEXT NOT NULL,
        work_center TEXT,
        operator TEXT,
        start_time TEXT,
        end_time TEXT,
        status TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_code TEXT NOT NULL UNIQUE,
        material_name TEXT NOT NULL,
        warehouse TEXT,
        quantity REAL,
        safety_stock REAL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outbound_shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        so_no TEXT NOT NULL,
        shipment_no TEXT,
        shipped_qty INTEGER,
        shipment_date TEXT,
        status TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipment_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_no TEXT NOT NULL UNIQUE,
        equipment_name TEXT,
        workshop TEXT,
        status TEXT,
        alarm_code TEXT,
        last_update TEXT
    );
    """)


    conn.commit()
    conn.close()

    print("数据库初始化完成！")


if __name__ == "__main__":
    init_database()
