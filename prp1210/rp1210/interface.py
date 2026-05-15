"""
RP1210 protocol implementation.

RP1210 is a standardized API for accessing vehicle communication hardware and protocols.
This module provides the core interface and client implementation.
"""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional

from ..common import RP1210Error


class RP1210Interface(ABC):
    """Abstract base class for RP1210 device implementations."""

    @abstractmethod
    def connect(self, device_name: str, protocol: int = 1) -> None:
        """Connect to an RP1210 device.

        Args:
            device_name: Name of the device to connect to
            protocol: Protocol type (1=J1939, 2=J1708, 3=CAN)

        Raises:
            RP1210Error: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the RP1210 device.

        Raises:
            RP1210Error: If disconnection fails
        """
        pass

    @abstractmethod
    def send_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Send a message through the RP1210 device.

        Args:
            data: Message data to send
            pgn: Optional PGN for J1939 messages

        Raises:
            RP1210Error: If send fails
        """
        pass

    @abstractmethod
    def read_message(self, timeout: Optional[float] = None) -> bytes:
        """Read a message from the RP1210 device.

        Args:
            timeout: Read timeout in seconds (None for blocking)

        Returns:
            Message data

        Raises:
            RP1210Error: If read fails or timeout occurs
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the device.

        Returns:
            True if connected, False otherwise
        """
        pass


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
        """Disconnect from the RP1210 device."""
        if self.connected:
            self.device.disconnect()
            self.connected = False

    def send_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Send a message.

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
