import logging
from threading import Event
from pubsub import pub
from meshtastic.serial_interface import SerialInterface
from session import Session, SessionManager
from commands import cmd_help, cmd_register, cmd_login, cmd_logout
import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
session_manager = SessionManager()
my_node: int = 0

def on_receive(packet, interface: SerialInterface):
    """Handles incoming mesh packets"""

    # Only process messages with 'decoded' section available
    decoded = packet.get("decoded")
    if not decoded:
        return

    # Ignore nodeinfo & telemetry - only text messages
    portnum = decoded.get("portnum")
    if portnum != "TEXT_MESSAGE_APP":
        return

    # Respond only when message is addressed directly to us (not main chat)
    recipient = packet.get("to")
    if recipient != my_node:
        return

    # Only respond to messages where we know the sender
    sender = packet.get("from")
    if not sender:
        return

    text = decoded.get("text", "")
    logging.info(f"received ({sender}): {text}")
    session = session_manager.get_or_create(sender)
    handle_message(session, text, interface)


def send_reply(interface: SerialInterface, session: Session, message: str):
    interface.sendText(message, destinationId=session.node_id)


def handle_message(session: Session, text: str, interface: SerialInterface):
    text = text.strip()
    if not text.startswith("/"):
        send_reply(interface, session, "Unknown command. Send /help for usage.")
        return

    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    match command:
        case "/help":
            cmd_help(session, interface)
        case "/register":
            cmd_register(session, args, interface)
        case "/login":
            cmd_login(session, args, interface)
        case "/logout":
            cmd_logout(session, interface)
        case _:
            send_reply(interface, session, f"Unknown command: {command}. Send /help for usage.")


def main():
    logging.basicConfig(level=logging.INFO, filename='app.log')

    global my_node
    db.init()
    pub.subscribe(on_receive, "meshtastic.receive")
    interface = SerialInterface()
    my_node = interface.myInfo.my_node_num
    logging.info(f"connected to radio {my_node}!")

    try:
        Event().wait()
    except KeyboardInterrupt:
        logging.info("stopping...")
        interface.close()
        logging.info(f"disconnected from radio {my_node}")


if __name__ == "__main__":
	main()