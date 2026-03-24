from meshtastic.serial_interface import SerialInterface
from session import Session
import pyotp
import db


def cmd_help(session: Session, interface: SerialInterface):
    """Responds with available commands"""
    pass


def send_reply(session: Session, interface: SerialInterface, message: str):
    interface.sendText(message, destinationId=session.node_id)


def cmd_register(session: Session, args: str, interface: SerialInterface):
    """Creates a new user account with specified username - responds with TOTP secret key"""
    username = args.strip()
    if not username:
        send_reply(session, interface, "Usage: /register <username>")
        return

    existing = db.db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        send_reply(session, interface, f"Username '{username}' is already taken.")
        return

    secret = pyotp.random_base32()
    db.db.execute("INSERT INTO users (username, private_key) VALUES (?, ?)", (username, secret))
    db.db.commit()

    send_reply(session, interface, f"Registered! Add this key to your authenticator app: {secret}")


def cmd_login(session: Session, args: str, interface: SerialInterface):
    """Authenticates a user by username and OTP code"""
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        send_reply(session, interface, "Usage: /login <username> <otp_code>")
        return

    username, code = parts

    row = db.db.execute("SELECT user_id, private_key FROM users WHERE username = ?", (username,)).fetchone()
    if not row:
        send_reply(session, interface, "Incorrect credentials.")
        return

    user_id, private_key = row
    totp = pyotp.TOTP(private_key)
    if not totp.verify(code):
        send_reply(session, interface, "Incorrect credentials.")
        return

    session.authenticated = True
    session.username = username
    session.user_id = user_id
    send_reply(session, interface, f"Logged in as {username}.")


def cmd_logout(session: Session, interface: SerialInterface):
    """Destroys current session"""
    pass
