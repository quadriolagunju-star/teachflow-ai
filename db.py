import sqlite3
import json
from datetime import datetime

def log_event(user_id, event_type, details=None):
    conn = sqlite3.connect("teachflow.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP
        )
    """)
    c.execute(
        "INSERT INTO events (user_id, event_type, details, created_at) VALUES (?, ?, ?, ?)",
        (user_id, event_type, json.dumps(details or {}), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    

def register_teacher(name, email, subject, level, curriculum):
    conn = sqlite3.connect("teachflow.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            subject TEXT,
            level TEXT,
            curriculum TEXT,
            created_at TIMESTAMP
        )
    """)
    try:
        c.execute(
            "INSERT INTO users (name, email, subject, level, curriculum, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, subject, level, curriculum, datetime.utcnow().isoformat())
        )
        conn.commit()
        teacher_id = c.lastrowid
        conn.close()
        return teacher_id
    except sqlite3.IntegrityError:
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None


def get_teacher_by_email(email):
    conn = sqlite3.connect("teachflow.db")
    c = conn.cursor()
    c.execute("SELECT id, name, subject, level, curriculum FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "subject": row[2], "level": row[3], "curriculum": row[4]}
    return None

def get_inactive_teachers(days=5):
    conn = sqlite3.connect("teachflow.db")
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.name, u.email, u.subject, u.level
        FROM users u
        WHERE u.id NOT IN (
            SELECT DISTINCT user_id FROM events
            WHERE created_at >= datetime('now', ?)
        )
    """, (f'-{days} days',))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "email": r[2], "subject": r[3], "level": r[4]} for r in rows]

def log_feedback(user_id, feature, rating, comment=None):
    conn = sqlite3.connect("teachflow.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            feature TEXT NOT NULL,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP
        )
    """)
    c.execute(
        "INSERT INTO feedback (user_id, feature, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, feature, rating, comment, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()