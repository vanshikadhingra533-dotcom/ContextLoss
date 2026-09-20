import sqlite3
from datetime import datetime


DATABASE = "contextloss.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def setup_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_context TEXT NOT NULL,
            handoff_context TEXT NOT NULL,
            similarity REAL,
            integrity REAL,
            risk TEXT,
            lost_count INTEGER,
            changed_count INTEGER,
            conflict_count INTEGER,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_case(original, handoff, result):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO cases (
            original_context,
            handoff_context,
            similarity,
            integrity,
            risk,
            lost_count,
            changed_count,
            conflict_count,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        original,
        handoff,
        result["similarity"],
        result["integrity"],
        result["risk"],
        len(result["lost"]),
        len(result["changed"]),
        len(result["conflicts"]),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_cases():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM cases
        ORDER BY id DESC
    """)

    cases = cursor.fetchall()

    connection.close()

    return cases