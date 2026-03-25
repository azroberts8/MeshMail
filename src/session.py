import logging
import pyotp
import db

class Session:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.authenticated = False
        self.username = None
        self.user_id = None
        logging.info(f"new session created for node {node_id}.")

    def register(self, username: str) -> str:
        """Create a new user account. Returns the TOTP secret key."""
        if not username.isalnum():
            raise ValueError("Username must only contain letters and numbers.")

        if len(username) > 30:
            raise ValueError("Username must be 30 characters or less.")

        username = username.lower()
        existing = db.db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            raise ValueError(f"Username '{username}' is already taken.")

        secret = pyotp.random_base32()
        db.db.execute("INSERT INTO users (username, private_key) VALUES (?, ?)", (username, secret))
        db.db.commit()
        logging.info(f"registered new user '{username}'.")
        return secret

    def login(self, username: str, otp_code: str) -> bool:
        """Authenticate with username and OTP code. Returns True on success."""
        if not username.isalnum():
            raise ValueError("Usernames only contain letters and numbers.")

        if len(username) > 30:
            raise ValueError("Username exceeds 30 character limit.")

        username = username.lower()
        row = db.db.execute("SELECT user_id, private_key FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return False

        user_id, private_key = row
        totp = pyotp.TOTP(private_key)
        if not totp.verify(otp_code):
            return False

        self.authenticated = True
        self.username = username
        self.user_id = user_id
        logging.info(f"node {self.node_id} logged in as '{username}'.")
        return True

    def logout(self):
        """End the authenticated session."""
        logging.info(f"node {self.node_id} logged out from '{self.username}'.")
        self.authenticated = False
        self.username = None
        self.user_id = None


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, Session] = {}

    def get_or_create(self, node_id: str) -> Session:
        if node_id not in self.sessions:
            self.sessions[node_id] = Session(node_id)
        return self.sessions[node_id]

    def get(self, node_id: str) -> Session | None:
        return self.sessions.get(node_id)

    def remove(self, node_id: str):
        self.sessions.pop(node_id, None)
