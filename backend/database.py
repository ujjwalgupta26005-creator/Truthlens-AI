import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "truthlens_history.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_type TEXT NOT NULL,
                input_preview TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )

def save_analysis(input_type: str, input_preview: str, result: str):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO analyses (input_type, input_preview, result) VALUES (?, ?, ?)",
            (input_type, input_preview[:500], result),
        )
        return cur.lastrowid

def get_history():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, input_type, input_preview, result, created_at FROM analyses ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]

def delete_history(history_id: int):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM analyses WHERE id = ?", (history_id,))
        return cur.rowcount > 0
