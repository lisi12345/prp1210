"""
RP1210 device implementations.
"""

from datetime import datetime
from queue import Empty, Queue
from typing import Any, Optional

from ..common import RP1210Error, RP1210NotConnected, RP1210Timeout
from .interface import RP1210Interface


class MockRP1210Device(RP1210Interface):
    """Mock RP1210 device for testing and development."""

    def __init__(self):
        """Initialize mock device."""
        self._connected = False
        self._device_name = ""
        self._protocol = 1
        self._rx_queue: Queue[dict[str, Any]] = Queue()
        self._tx_queue: Queue[dict[str, Any]] = Queue()
        self._messages_received = 0
        self._messages_sent = 0

    def connect(self, device_name: str, protocol: int = 1) -> None:
        """Connect to mock device."""
        if self._connected:
            raise RP1210Error("Already connected")

        self._connected = True
        self._device_name = device_name
        self._protocol = protocol

    def disconnect(self) -> None:
        """Disconnect from mock device."""
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        self._connected = False
        self._rx_queue = Queue()
        self._tx_queue = Queue()

    def send_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Send a message (mock stores in queue)."""
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        self._tx_queue.put({
            'data': data,
            'pgn': pgn,
            'timestamp': datetime.now()
        })
        self._messages_sent += 1

    def read_message(self, timeout: Optional[float] = None) -> bytes:
        """Read a message (mock retrieves from queue)."""
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        try:
            message = self._rx_queue.get(timeout=timeout)
            self._messages_received += 1
            return message['data']
        except Empty as exc:
            raise RP1210Timeout("Read operation timed out") from exc

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    def inject_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Inject a message into the receive queue (for testing)."""
        self._rx_queue.put({
            'data': data,
            'pgn': pgn,
            'timestamp': datetime.now()
        })

    def get_sent_messages(self) -> list[dict[str, Any]]:
        """Get all messages that were sent (for testing)."""
        messages: list[dict[str, Any]] = []
        while not self._tx_queue.empty():
            messages.append(self._tx_queue.get())
        return messages


class SimulatedRP1210Device(RP1210Interface):
    """Simulated RP1210 device with realistic behavior."""

    def __init__(self):
        """Initialize simulated device."""
        self._connected = False
        self._device_name = ""
        self._protocol = 1
        self._rx_queue: Queue[dict[str, Any]] = Queue()
        self._tx_queue: Queue[dict[str, Any]] = Queue()

    def connect(self, device_name: str, protocol: int = 1) -> None:
        """Connect to simulated device."""
        if self._connected:
            raise RP1210Error("Already connected")

        # Simulate connection delay and validation
        self._connected = True
        self._device_name = device_name
        self._protocol = protocol

    def disconnect(self) -> None:
        """Disconnect from simulated device."""
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        self._connected = False

    def send_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Send a message through simulated device."""
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        # Simulate message sending with echoing
        self._tx_queue.put({
            'data': data,
            'pgn': pgn,
            'timestamp': datetime.now()
        })

        # Echo back the message to rx queue for loopback testing
        self._rx_queue.put({
            'data': data,
            'pgn': pgn,
            'timestamp': datetime.now(),
            'echoed': True
        })

    def read_message(self, timeout: Optional[float] = None) -> bytes:
        """Read a message from simulated device."""
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        try:
            message = self._rx_queue.get(timeout=timeout)
            return message['data']
        except Empty as exc:
            raise RP1210Timeout("Read operation timed out") from exc

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
