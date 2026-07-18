"""
database.py
------------
Lightweight SQLite persistence for sensor events, alarms, and automation logs.
"""
import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "home_automation.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            source TEXT NOT NULL,
            event_type TEXT NOT NULL,
            detail TEXT,
            severity TEXT DEFAULT 'info'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS system_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_event(source: str, event_type: str, detail: str = "", severity: str = "info"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO events (timestamp, source, event_type, detail, severity) VALUES (?, ?, ?, ?, ?)",
        (time.time(), source, event_type, detail, severity),
    )
    conn.commit()
    conn.close()


def recent_events(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_state(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO system_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_state(key: str, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM system_state WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default
