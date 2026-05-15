"""
Data structures for RP1210 and J1939 communication.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Any, cast


@dataclass
class Message:
    """Generic message structure for RP1210 communication."""
    timestamp: datetime
    data: bytes
    priority: int = 6
    pgn: Optional[int] = None
    source_address: Optional[int] = None
    destination_address: Optional[int] = None

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return (
            f"Message(timestamp={self.timestamp}, data={self.data.hex()}, "
            f"priority={self.priority}, pgn={self.pgn})"
        )


@dataclass
class RP1210DeviceInfo:
    """Information about an RP1210 device."""
    name: str
    vendor: str
    device_id: int
    firmware_version: str
    api_version: str
    max_clients: int = 1
    features: list[dict[str, Any]] = field(default_factory=cast(Any, list))

    def __repr__(self) -> str:
        return (
            f"RP1210DeviceInfo(name={self.name}, vendor={self.vendor}, "
            f"device_id={self.device_id}, firmware={self.firmware_version})"
        )


@dataclass
class Configuration:
    """Configuration for RP1210 communication."""
    device_name: str
    protocol: int = 1  # J1939
    baud_rate: int = 250000
    filters: list[dict[str, Any]] = field(default_factory=cast(Any, list))
    loopback: bool = False
    echo: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return all information in a dictionary."""
        return asdict(self)


@dataclass
class Statistics:
    """Communication statistics."""
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    errors: int = 0
    timeouts: int = 0

    def reset(self) -> None:
        """Reset all statistics."""
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.errors = 0
        self.timeouts = 0
