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
    db.execute("""
        CREATE TABLE IF NOT EXISTS mail (
            mail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender INTEGER NOT NULL REFERENCES users(user_id),
            recipient INTEGER NOT NULL REFERENCES users(user_id),
            message TEXT NOT NULL,
            datetime TEXT NOT NULL
        )
    """)
    db.execute("PRAGMA foreign_keys = ON")
    db.commit()
