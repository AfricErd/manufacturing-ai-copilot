from pathlib import Path
import sqlite3

DATA_DIR = Path("data/sqlite")
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "manufacturing.db"


def get_connection():
    """
    获取 SQLite 数据库连接
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn