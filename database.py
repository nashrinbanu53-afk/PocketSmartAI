import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from .config import settings

def _connect():
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            planner_type TEXT NOT NULL,
            budget REAL NOT NULL,
            request_json TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

def create_user(name, email, password_hash):
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
            (name, email.lower().strip(), password_hash, datetime.now(timezone.utc).isoformat())
        )
        return cur.lastrowid

def get_user_by_email(email):
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    with db() as conn:
        row = conn.execute(
            "SELECT id,name,email,created_at FROM users WHERE id=?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

def save_recommendation(user_id, planner_type, budget, request_data, response_data):
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO recommendations
            (user_id,planner_type,budget,request_json,response_json,created_at)
            VALUES(?,?,?,?,?,?)""",
            (
                user_id, planner_type, budget,
                json.dumps(request_data, ensure_ascii=False),
                json.dumps(response_data, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat()
            )
        )
        return cur.lastrowid

def list_history(user_id):
    with db() as conn:
        rows = conn.execute(
            """SELECT id,planner_type,budget,created_at
               FROM recommendations WHERE user_id=?
               ORDER BY id DESC""", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def get_recommendation(user_id, recommendation_id):
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM recommendations WHERE id=? AND user_id=?",
            (recommendation_id, user_id)
        ).fetchone()
        if not row:
            return None
        item = dict(row)
        item["request"] = json.loads(item.pop("request_json"))
        item["response"] = json.loads(item.pop("response_json"))
        return item
