"""
J1939 Parameter Group Number (PGN) definitions and utilities.

A PGN is a 24-bit number that identifies a specific J1939 message.
Format: PDPSPF (1 byte = P, 1 byte = DP/PS, 1 byte = F)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PGNInfo:
    """Information about a specific PGN."""
    pgn: int
    name: str
    transmission_type: str  # "Cyclic", "OnRequest", "OnChange", etc.
    frequency: Optional[float] = None  # Hz or cycles per period
    size: int = 8  # bytes
    data_page: bool = False
    pdu_format: Optional[int] = None
    pdu_specific: Optional[int] = None
    description: str = ""

    def is_pdu1(self) -> bool:
        """Check if this is a PDU1 message (PS is destination)."""
        return (self.pgn >> 8) < 240

    def is_pdu2(self) -> bool:
        """Check if this is a PDU2 message (PS is group extension)."""
        return (self.pgn >> 8) >= 240


class PGNDatabase:
    """Database of common J1939 PGNs."""

    # Electronic Engine Controller 1 (EEC1)
    EEC1 = PGNInfo(
        pgn=0xF004,
        name="Electronic Engine Controller 1",
        transmission_type="Cyclic",
        frequency=10,
        size=8,
        description="Engine speed, torque, and throttle position"
    )

    # Engine Temperature
    ET = PGNInfo(
        pgn=0xFEEA,
        name="Engine Temperature",
        transmission_type="Cyclic",
        frequency=1,
        size=8,
        description="Coolant temperature and fuel temperature"
    )

    # Vehicle Speed
    DM1 = PGNInfo(
        pgn=0xFECA,
        name="Active Diagnostic Trouble Codes",
        transmission_type="OnRequest",
        size=8,
        description="Diagnostic trouble codes"
    )

    # Address Claim
    ADDRESS_CLAIM = PGNInfo(
        pgn=0xEE00,
        name="Address Claim / Cannot Claim Address",
        transmission_type="OnEvent",
        size=8,
        description="Used for address claiming on the network"
    )

    # Request PGN
    REQUEST_PGN = PGNInfo(
        pgn=0xEA00,
        name="Request PGN",
        transmission_type="OnRequest",
        size=3,
        description="Request for a PGN"
    )

    # Commanded Address
    COMMANDED_ADDRESS = PGNInfo(
        pgn=0xFED8,
        name="Commanded Address",
        transmission_type="OnRequest",
        size=8,
        description="Command to change node address"
    )

    # Common J1939 PGNs
    _COMMON_PGNS = {
        0xF004: EEC1,
        0xFEEA: ET,
        0xFECA: DM1,
        0xEE00: ADDRESS_CLAIM,
        0xEA00: REQUEST_PGN,
        0xFED8: COMMANDED_ADDRESS,
    }

    @classmethod
    def get_pgn_info(cls, pgn: int) -> Optional[PGNInfo]:
        """Get information about a PGN.

        Args:
            pgn: The PGN value (0x0000 - 0xFFFF)

        Returns:
            PGNInfo if found, None otherwise
        """
        return cls._COMMON_PGNS.get(pgn & 0xFFFF)

    @classmethod
    def add_pgn(cls, pgn_info: PGNInfo) -> None:
        """Add a custom PGN to the database.

        Args:
            pgn_info: The PGN information to add
        """
        cls._COMMON_PGNS[pgn_info.pgn] = pgn_info

    @classmethod
    def list_pgns(cls) -> dict[int, PGNInfo]:
        """Get all PGNs in the database.

        Returns:
            Dictionary of PGN number to PGNInfo
        """
        return cls._COMMON_PGNS.copy()


class PGNParser:
    """Parser for PGN numbers."""

    @staticmethod
    def extract_pgn(can_id: int) -> int:
        """Extract PGN from a CAN ID.

        J1939 29-bit CAN ID format:
        - Priority (3 bits): bits 26-28
        - Reserved (1 bit): bit 25
        - Data Page (1 bit): bit 24
        - PDU Format (8 bits): bits 16-23
        - PDU Specific (8 bits): bits 8-15
        - Source Address (8 bits): bits 0-7

        Args:
            can_id: The 29-bit CAN identifier

        Returns:
            The 16-bit PGN (bits 24-15 in CAN ID)
        """
        # Mask off the source address (lower 8 bits) and priority/reserved
        return (can_id >> 8) & 0xFFFF

    @staticmethod
    def extract_source_address(can_id: int) -> int:
        """Extract source address from CAN ID.

        Args:
            can_id: The 29-bit CAN identifier

        Returns:
            The source address (0-255)
        """
        return can_id & 0xFF

    @staticmethod
    def extract_priority(can_id: int) -> int:
        """Extract priority from CAN ID.

        Args:
            can_id: The 29-bit CAN identifier

        Returns:
            The priority (0-6)
        """
        return (can_id >> 26) & 0x07

    @staticmethod
    def extract_destination_address(can_id: int) -> Optional[int]:
        """Extract destination address if PDU1 format.

        In PDU1 format, the PS field contains destination address.
        In PDU2 format, it's a group extension.

        Args:
            can_id: The 29-bit CAN identifier

        Returns:
            Destination address if PDU1, None if PDU2
        """
        pdu_format = (can_id >> 16) & 0xFF
        if pdu_format < 240:  # PDU1
            return (can_id >> 8) & 0xFF
        return None

    @staticmethod
    def build_can_id(
        priority: int,
        pgn: int,
        source_address: int,
        destination_address: Optional[int] = None
    ) -> int:
        """Build a J1939 CAN ID.

        Args:
            priority: Priority (0-6)
            pgn: Parameter Group Number (0x0000-0xFFFF)
            source_address: Source address (0-255)
            destination_address: Destination address for PDU1 (optional)

        Returns:
            The 29-bit CAN identifier
        """
        # Priority: bits 26-28
        can_id = (priority & 0x07) << 26

        # Data page and reserved (assume 0)
        # Bits 24-25

        # PDU Format: bits 16-23
        pdu_format = (pgn >> 8) & 0xFF
        can_id |= pdu_format << 16

        # PDU Specific: bits 8-15
        ps = pgn & 0xFF
        can_id |= ps << 8

        # Source address: bits 0-7
        can_id |= source_address & 0xFF

        return can_id & 0x1FFFFFFF  # Mask to 29 bits
