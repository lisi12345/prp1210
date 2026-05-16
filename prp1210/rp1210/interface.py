"""
RP1210 protocol interface implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional


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
