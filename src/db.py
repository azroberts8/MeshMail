import sqlite3

db: sqlite3.Connection | None = None


def init(path: str = "mesh_mail.db"):
    global db
    db = sqlite3.connect(path, check_same_thread=False)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            private_key TEXT NOT NULL
        )
    """)
    db.commit()
