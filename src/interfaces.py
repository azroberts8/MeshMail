from abc import ABC, abstractmethod
from typing import Callable, List, Protocol
from meshtastic.serial_interface import SerialInterface
from pubsub import pub
import logging
import time


class MessageHandler[T](Protocol):
    """Definition for functions that that processes an incoming message"""
    def __call__(self, message: str, sender: T, interface: MessageInterface[T]) -> None:
        pass


class MessageInterface[T](ABC):
    """Abstract base for text message-based communication interfaces."""

    @abstractmethod
    def __init__(self):
        self._message_handlers: List[MessageHandler[T]] = []

    @abstractmethod
    def send_message(self, message: str, recipient: T):
        """Send a message to the specified recipient."""
        raise NotImplementedError(f"send_message() not implemented on interface {self.__class__.__name__}")

    @abstractmethod
    def close(self):
        """Close the interface and release resources."""
        raise NotImplementedError(f"close() not implemented on interface {self.__class__.__name__}")

    def add_message_handler(self, handler: MessageHandler[T]):
        """Register a handler to be called on incoming messages."""
        self._message_handlers.append(handler)


class Meshtastic(MessageInterface[int]):
    """MessageInterface implementation for Meshtastic radio devices over serial."""

    def __init__(self):
        super().__init__()

        self.interface = SerialInterface()
        self.my_node = self.interface.myInfo.my_node_num
        pub.subscribe(self._on_receive, "meshtastic.receive")

        logging.info(f"connected to meshtastic device {self.my_node}")

    def send_message(self, message, recipient):
        """Calls _split_message() and sends each chunk to recipient"""
        msg_chunks = self._split_message(message)
        for i in range(len(msg_chunks)):
            chunk = f"{msg_chunks[i]} ({i+1}/{len(msg_chunks)})" if len(msg_chunks) > 1 else msg_chunks[0]
            self.interface.sendText(chunk, destinationId=recipient)
            time.sleep(2)

    def close(self):
        """Closes Meshtastic interface"""
        self.interface.close()
        logging.info(f"disconnected from meshtastic device {self.my_node}")

    def _on_receive(self, packet):
        """Handles incoming Meshtastic packets"""
        
        # Only process messages with 'decoded' section available
        decoded = packet.get("decoded")
        if not decoded:
            return

        # Ignore nodeinfo & telemetry - only text messages
        portnum = decoded.get("portnum")
        if portnum != "TEXT_MESSAGE_APP":
            return

        # Respond only when message is addressed directly to us (not group chats)
        recipient = packet.get("to")
        if recipient != self.my_node:
            return

        # Only respond to messages where we know the sender
        sender = packet.get("from")
        if not sender:
            return
        
        text = decoded.get("text", "")

        # Call each subscribed handler with message and direct response function
        for handler in self._message_handlers:
            handler(
                message=text,
                sender=sender,
                interface=self
            )

    def _split_message(self, message: str) -> list[str]:
        """Splits message into list of strings where len(str) < 200 characters to fit meshtastic standard"""
        words = message.split()
        chunks = []
        current = []

        for word in words:
            # If adding this word would exceed the limit, start a new chunk
            if current and len(" ".join(current + [word])) > 192:  # 200 char limit; up to 8 seq chars _(xx/xx)
                chunks.append(" ".join(current))
                current = [word]
            else:
                current.append(word)

        if current:
            chunks.append(" ".join(current))

        return chunks