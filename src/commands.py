import time
from datetime import datetime, timezone
from text_message_interfaces import MessageInterface
from session import Session
import db


def cmd_help(interface: MessageInterface, session: Session):
    messages = [
        f"/help - Show this message\n/register <username> - Create an account\n/login <username> <otp_code> - Log in\n/logout - Log out\n/whoami - Show current user",
        f"/sendmail <recipient> <message> - Send mail\n/inbox - View received mail\n/sent - View sent mail"
    ]
    for msg in messages:
        interface.send_message(msg, session.node_id)
        time.sleep(2)


def cmd_register(interface: MessageInterface, session: Session, args):
    username = args.strip()
    if not username:
        interface.send_message("Usage: /register <username>", session.node_id)
        return

    try:
        secret = session.register(username)
    except ValueError as e:
        interface.send_message(str(e), session.node_id)
        return

    interface.send_message(f"Registered! Add this key to your authenticator app then use /login to login.", session.node_id)
    time.sleep(2)  # Ensure LoRa message propation
    interface.send_message(f"{secret}", session.node_id)


def cmd_login(interface: MessageInterface, session: Session, args):
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        interface.send_message("Usage: /login <username> <otp_code>", session.node_id)
        return

    username, otp_code = parts
    try:
        if session.login(username, otp_code):
            interface.send_message(f"Logged in as {username.lower()}!", session.node_id)
        else:
            interface.send_message("Incorrect credentials.", session.node_id)
    except ValueError as e:
        interface.send_message(str(e), session.node_id)


def cmd_logout(interface: MessageInterface, session: Session):
    if not session.authenticated:
        interface.send_message("You are not logged in.", session.node_id)
        return

    session.logout()
    interface.send_message("Logged out!", session.node_id)


def cmd_whoami(interface: MessageInterface, session: Session):
    if not session.authenticated:
        interface.send_message("You are not logged in.", session.node_id)
        return

    interface.send_message(f"Logged in as {session.username}.", session.node_id)


def cmd_sendmail(interface: MessageInterface, session: Session, args):
    if not session.authenticated:
        interface.send_message("You must be logged in to send mail.", session.node_id)
        return

    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        interface.send_message("Usage: /sendmail <recipient> <message>", session.node_id)
        return

    recipient_name, message = parts
    recipient_name = recipient_name.lower()

    row = db.db.execute("SELECT user_id FROM users WHERE username = ?", (recipient_name,)).fetchone()
    if not row:
        interface.send_message(f"User '{recipient_name}' not found.", session.node_id)
        return

    recipient_id = row[0]
    now = datetime.now(timezone.utc).isoformat()
    db.db.execute(
        "INSERT INTO mail (sender, recipient, message, datetime) VALUES (?, ?, ?, ?)",
        (session.user_id, recipient_id, message, now)
    )
    db.db.commit()
    interface.send_message(f"Mail sent to {recipient_name}.", session.node_id)


def cmd_inbox(interface: MessageInterface, session: Session):
    if not session.authenticated:
        interface.send_message("You must be logged in to check mail.", session.node_id)
        return

    rows = db.db.execute(
        "SELECT u.username, m.message, m.datetime FROM mail m "
        "JOIN users u ON m.sender = u.user_id "
        "WHERE m.recipient = ? ORDER BY m.datetime DESC",
        (session.user_id,)
    ).fetchall()

    if not rows:
        interface.send_message("Inbox is empty.", session.node_id)
        return

    for sender, message, dt in rows:
        formatted = datetime.fromisoformat(dt).astimezone().strftime("%m/%d %H:%M")
        interface.send_message(f"From {sender} {formatted}: {message}", session.node_id)
        time.sleep(2)


def cmd_sent(interface: MessageInterface, session: Session):
    if not session.authenticated:
        interface.send_message("You must be logged in to check sent mail.", session.node_id)
        return

    rows = db.db.execute(
        "SELECT u.username, m.message, m.datetime FROM mail m "
        "JOIN users u ON m.recipient = u.user_id "
        "WHERE m.sender = ? ORDER BY m.datetime DESC",
        (session.user_id,)
    ).fetchall()

    if not rows:
        interface.send_message("No sent mail.", session.node_id)
        return

    for recipient, message, dt in rows:
        formatted = datetime.fromisoformat(dt).astimezone().strftime("%m/%d %H:%M")
        interface.send_message(f"To {recipient} {formatted}: {message}", session.node_id)
        time.sleep(2)