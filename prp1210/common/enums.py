"""
Enumeration types for RP1210 and J1939 protocols.
"""

from enum import Enum, IntEnum


class MessageType(IntEnum):
    """Message types in J1939."""
    PDU1 = 0
    PDU2 = 1
    PGN = 2


class Priority(IntEnum):
    """Priority levels for J1939 messages (0-6, lower is higher priority)."""
    HIGHEST = 0
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    VERY_LOW = 5
    LOWEST = 6


class DeviceState(Enum):
    """Connection states for RP1210 devices."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class ProtocolType(IntEnum):
    """Protocol types supported by RP1210."""
    J1939 = 1
    J1708 = 2
    CAN = 3


class FilterType(IntEnum):
    """Message filter types."""
    INCLUDE = 1
    EXCLUDE = 2
    PASS_THROUGH = 3


class BaudRate(IntEnum):
    """Common baud rates for serial communication."""
    BAUD_9600 = 9600
    BAUD_19200 = 19200
    BAUD_38400 = 38400
    BAUD_57600 = 57600
    BAUD_115200 = 115200
