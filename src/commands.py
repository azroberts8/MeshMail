import time

from interfaces import MessageInterface
from session import Session

def cmd_help(interface: MessageInterface, session: Session):
    pass


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
    time.sleep(2)
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