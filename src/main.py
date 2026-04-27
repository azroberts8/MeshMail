import logging
from threading import Event
from text_message_interfaces import Meshtastic, MessageInterface
from session import SessionManager
from commands import cmd_help, cmd_register, cmd_login, cmd_logout, cmd_whoami, cmd_sendmail, cmd_inbox, cmd_sent
import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
session_manager = SessionManager()


def handle_message(message, sender, interface: MessageInterface):
    session = session_manager.get_or_create(sender)
    message = message.strip()

    if not message.startswith("/"):
        interface.send_message("Unknown command. Send /help for usage.", sender)
        return

    parts = message.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    match command:
        case "/help":
            cmd_help(interface, session)
        case "/register":
            cmd_register(interface, session, args)
        case "/login":
            cmd_login(interface, session, args)
        case "/logout":
            cmd_logout(interface, session)
        case "/whoami":
            cmd_whoami(interface, session)
        case "/sendmail":
            cmd_sendmail(interface, session, args)
        case "/inbox":
            cmd_inbox(interface, session)
        case "/sent":
            cmd_sent(interface, session)
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