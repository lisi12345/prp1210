"""
J1939 message definitions and parsing.
"""

import struct
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .pgn import PGNParser


@dataclass
class J1939Message:
    """Representation of a J1939 message."""
    timestamp: datetime
    can_id: int
    data: bytes
    dlc: int = 8

    # Parsed fields
    priority: Optional[int] = None
    pgn: Optional[int] = None
    source_address: Optional[int] = None
    destination_address: Optional[int] = None

    def __post_init__(self):
        """Parse CAN ID after initialization."""
        self._parse_can_id()

    def _parse_can_id(self):
        """Parse the CAN ID into J1939 fields."""

        self.priority = PGNParser.extract_priority(self.can_id)
        self.pgn = PGNParser.extract_pgn(self.can_id)
        self.source_address = PGNParser.extract_source_address(self.can_id)
        self.destination_address = PGNParser.extract_destination_address(
            self.can_id)

    def is_destination_specific(self) -> bool:
        """Check if this is a destination-specific message (PDU1)."""
        return self.destination_address is not None

    def is_broadcast(self) -> bool:
        """Check if this is a broadcast message (PDU2)."""
        return self.destination_address is None

    def __repr__(self) -> str:
        return (
            f"J1939Message(pgn=0x{self.pgn:04X}, "
            f"src={self.source_address}, "
            f"priority={self.priority}, "
            f"data={self.data.hex()})"
        )


class J1939MessageBuilder:
    """Builder for constructing J1939 messages."""

    def __init__(self, pgn: int, source_address: int):
        """Initialize message builder.

        Args:
            pgn: Parameter Group Number
            source_address: Node address (0-255)
        """
        self.pgn = pgn
        self.source_address = source_address
        self.priority = 6  # Default priority
        self.destination_address: Optional[int] = None
        self.data = bytearray(8)
        self.dlc = 8

    def set_priority(self, priority: int) -> 'J1939MessageBuilder':
        """Set message priority (0-6, lower is higher priority)."""
        if not 0 <= priority <= 6:
            raise ValueError("Priority must be 0-6")
        self.priority = priority
        return self

    def set_destination(self, address: int) -> 'J1939MessageBuilder':
        """Set destination address for PDU1 messages."""
        if not 0 <= address <= 255:
            raise ValueError("Address must be 0-255")
        self.destination_address = address
        return self

    def set_data(self, data: bytes, offset: int = 0) -> 'J1939MessageBuilder':
        """Set message data.

        Args:
            data: Data bytes to write
            offset: Offset into message data
        """
        data_bytes = bytes(data)
        if offset + len(data_bytes) > 8:
            raise ValueError("Data exceeds 8 bytes")
        self.data[offset:offset+len(data_bytes)] = data_bytes
        self.dlc = max(self.dlc, offset + len(data_bytes))
        return self

    def set_data_field(self, value: int, byte_index: int,
                       byte_count: int = 1, signed: bool = False) -> 'J1939MessageBuilder':
        """Set a specific field in the message data.

        Args:
            value: Value to set
            byte_index: Starting byte index
            byte_count: Number of bytes (1, 2, or 4)
            signed: Whether value is signed
        """
        if byte_count == 1:
            fmt = 'b' if signed else 'B'
            self.data[byte_index] = struct.pack(fmt, value)[0]
        elif byte_count == 2:
            fmt = '<h' if signed else '<H'
            self.data[byte_index:byte_index+2] = struct.pack(fmt, value)
        elif byte_count == 4:
            fmt = '<i' if signed else '<I'
            self.data[byte_index:byte_index+4] = struct.pack(fmt, value)
        else:
            raise ValueError("byte_count must be 1, 2, or 4")

        self.dlc = max(self.dlc, byte_index + byte_count)
        return self

    def build(self) -> J1939Message:
        """Build the message.

        Returns:
            Constructed J1939Message
        """
        from .pgn import PGNParser

        can_id = PGNParser.build_can_id(
            self.priority,
            self.pgn,
            self.source_address,
            self.destination_address
        )

        return J1939Message(
            timestamp=datetime.now(),
            can_id=can_id,
            data=bytes(self.data[:self.dlc]),
            dlc=self.dlc,
            priority=self.priority,
            pgn=self.pgn,
            source_address=self.source_address,
            destination_address=self.destination_address
        )


class J1939MessageParser:
    """Parser for extracting data from J1939 messages."""

    def __init__(self, message: J1939Message):
        """Initialize parser with a message.

        Args:
            message: The J1939Message to parse
        """
        self.message = message

    def get_byte(self, index: int) -> int:
        """Get a single byte from the message.

        Args:
            index: Byte index (0-7)

        Returns:
            The byte value
        """
        if index >= len(self.message.data):
            return 0
        return self.message.data[index]

    def get_bytes(self, start_index: int, count: int) -> bytes:
        """Get multiple bytes from the message.

        Args:
            start_index: Starting byte index
            count: Number of bytes

        Returns:
            The bytes
        """
        end_index = min(start_index + count, len(self.message.data))
        return self.message.data[start_index:end_index]

    def get_uint16(self, index: int, little_endian: bool = True) -> int:
        """Get a 16-bit unsigned integer.

        Args:
            index: Starting byte index
            little_endian: Byte order

        Returns:
            The value
        """
        data = self.get_bytes(index, 2)
        if len(data) < 2:
            return 0
        fmt = '<H' if little_endian else '>H'
        return struct.unpack(fmt, data)[0]

    def get_uint32(self, index: int, little_endian: bool = True) -> int:
        """Get a 32-bit unsigned integer.

        Args:
            index: Starting byte index
            little_endian: Byte order

        Returns:
            The value
        """
        data = self.get_bytes(index, 4)
        if len(data) < 4:
            return 0
        fmt = '<I' if little_endian else '>I'
        return struct.unpack(fmt, data)[0]

    def get_int16(self, index: int, little_endian: bool = True) -> int:
        """Get a 16-bit signed integer.

        Args:
            index: Starting byte index
            little_endian: Byte order

        Returns:
            The value
        """
        data = self.get_bytes(index, 2)
        if len(data) < 2:
            return 0
        fmt = '<h' if little_endian else '>h'
        return struct.unpack(fmt, data)[0]

    def get_int32(self, index: int, little_endian: bool = True) -> int:
        """Get a 32-bit signed integer.

        Args:
            index: Starting byte index
            little_endian: Byte order

        Returns:
            The value
        """
        data = self.get_bytes(index, 4)
        if len(data) < 4:
            return 0
        fmt = '<i' if little_endian else '>i'
        return struct.unpack(fmt, data)[0]
