"""
Common utilities and data structures for RP1210 and J1939 communication.
"""

from .enums import MessageType, Priority
from .exceptions import RP1210Error, RP1210NotConnected, RP1210Timeout

__all__ = [
    "MessageType",
    "Priority",
    "RP1210Error",
    "RP1210NotConnected",
    "RP1210Timeout",
]
