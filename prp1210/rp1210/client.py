'''
RP1210 protocol implementation.

RP1210 is a standardized API for accessing vehicle communication hardware and protocols.
This module provides the client implementation.
'''

from types import TracebackType
from typing import Optional

from ..common import RP1210Error
from .interface import RP1210Interface


class RP1210Client:
    """Client for RP1210 device communication."""

    def __init__(self, device_impl: RP1210Interface):
        """Initialize RP1210 client.

        Args:
            device_impl: Implementation of RP1210Interface
        """
        self.device = device_impl
        self.connected = False

    def connect(self, device_name: str, protocol: int = 1) -> None:
        """Connect to an RP1210 device.
        
           Implementation of RP1210_CLIENTCONNECT.

        Args:
            device_name: Name of the device to connect to
            protocol: Protocol type (1=J1939, default)

        Raises:
            RP1210Error: If connection fails
        """
        if self.connected:
            raise RP1210Error("Already connected")

        self.device.connect(device_name, protocol)
        self.connected = True

    def disconnect(self) -> None:
        """Disconnect from the RP1210 device.
        
           Implementation of RP1210_CLIENTDISCONNECT.
        """
        if self.connected:
            self.device.disconnect()
            self.connected = False

    def send_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Send a message.
        
           Implementation of RP1210_SENDMESSAGE.

        Args:
            data: Message data
            pgn: Optional PGN for J1939 messages

        Raises:
            RP1210Error: If not connected or send fails
        """
        if not self.connected:
            raise RP1210Error("Not connected")

        self.device.send_message(data, pgn)

    def read_message(self, timeout: Optional[float] = None) -> bytes:
        """Read a message.
        
           Implementation of RP1210_READMESSAGE.

        Args:
            timeout: Read timeout in seconds

        Returns:
            Message data

        Raises:
            RP1210Error: If not connected or read fails
        """
        if not self.connected:
            raise RP1210Error("Not connected")

        return self.device.read_message(timeout)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None,) -> bool:
        """Context manager exit."""
        self.disconnect()
        return False
