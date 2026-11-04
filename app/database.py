import sqlite3

DB_NAME = "metrics.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE  IF NOT EXISTS server_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id TEXT NOT NULL,
        max_temp REAL NOT NULL,
        status TEXT NOT NULL,
        trend TEXT NOT NULL,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    """)

    conn.commit()
    conn.close()
def save_log(server_id: str, max_temp: float, status: str, trend: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO server_logs (server_id, max_temp, status, trend)
    VALUES (?, ?, ?, ?);
    """, (server_id, max_temp, status, trend))

    conn.commit()
    conn.close()
def get_recent_logs(limit: int =5) -> list[dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT server_id, max_temp, status, trend, checked_at
    FROM server_logs
    ORDER BY id DESC
    LIMIT ?;
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]