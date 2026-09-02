import sqlite3
import os
import datetime
from packages.contracts.schemas import FeedbackRequest

# Ensure data directory exists in the root of the project
DB_PATH = os.path.join("data", "feedback.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            query TEXT,
            conversation_id TEXT,
            is_positive BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def save_feedback(request: FeedbackRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (timestamp, query, conversation_id, is_positive) VALUES (?, ?, ?, ?)",
        (datetime.datetime.utcnow().isoformat(), request.query, request.conversation_id, request.is_positive)
    )
    conn.commit()
    conn.close()

# Initialize table if it doesn't exist on import
init_db()
