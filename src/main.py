import logging
from threading import Event
from typing import Callable
from interfaces import Meshtastic, MessageInterface
from session import Session, SessionManager
from commands import cmd_help, cmd_register, cmd_login, cmd_logout
import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
session_manager = SessionManager()

def handle_message(message, sender, interface: MessageInterface):
    message = message.strip()
    if not message.startswith("/"):
        interface.send_message("Unknown command. Send /help for usage.", sender)
        return

    parts = message.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    match command:
        # case "/help":
        #     cmd_help(session, interface)
        # case "/register":
        #     cmd_register(session, args, interface)
        # case "/login":
        #     cmd_login(session, args, interface)
        # case "/logout":
        #     cmd_logout(session, interface)
        case _:
            interface.send_message(f"Unknown command: {command}. Send /help for usage.", sender)


def main():
    logging.basicConfig(level=logging.INFO, filename='app.log')

    db.init()
    interface: MessageInterface = Meshtastic()
    interface.add_message_handler(handle_message)

    try:
        Event().wait()
    except KeyboardInterrupt:
        logging.info("stopping...")
        interface.close()


if __name__ == "__main__":
	main()