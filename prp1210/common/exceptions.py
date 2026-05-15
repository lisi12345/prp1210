"""
Exception classes for RP1210 and J1939 protocols.
"""
from typing import Optional


class RP1210Error(Exception):
    """Base exception for RP1210 protocol errors."""

    def __init__(self, message: str = "",
                 error_code: Optional[int] = None) -> None:
        self.error_code = error_code
        super().__init__(
            message if error_code is None else f"{message} [Error Code {error_code}]"
        )


class RP1210NotConnected(RP1210Error):
    """Raised when attempting to use a disconnected device."""


class RP1210Timeout(RP1210Error):
    """Raised when an operation times out."""


class RP1210InvalidParameter(RP1210Error):
    """Raised when an invalid parameter is provided."""


class RP1210DeviceError(RP1210Error):
    """Raised when the device reports an error."""


class J1939Error(Exception):
    """Base exception for J1939 protocol errors."""


class J1939InvalidPGN(J1939Error):
    """Raised when an invalid PGN is encountered."""


class J1939InvalidMessage(J1939Error):
    """Raised when a message cannot be parsed."""


class J1939EncodeError(J1939Error):
    """Raised when a message cannot be encoded."""
