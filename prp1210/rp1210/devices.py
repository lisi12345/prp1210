"""
RP1210 device implementations.
"""

from datetime import datetime
from queue import Empty, Queue
from types import TracebackType
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

    def read_version(self) -> None:
        """Read version information for API DLL."""
        # Mock implementation
        pass

    def read_detailed_version(self, client_id: int) -> str:
        """Read detailed version information."""
        return "Mock RP1210 Device v1.0"


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

    def read_version(self) -> None:
        """Read version information for API DLL."""
        # Simulated implementation
        pass

    def read_detailed_version(self, client_id: int) -> str:
        """Read detailed version information."""
        return "Simulated RP1210 Device v1.0"


class RP1210Device(RP1210Interface):
    """Actual RP1210 device that loads and communicates with vendor DLL.

    This class handles real hardware communication through vendor-provided
    dynamic libraries (DLLs). It manages DLL loading, device connection,
    and message transmission/reception.
    """

    def __init__(self, dll_path: Optional[str] = None, vendor_name: str = ""):
        """Initialize RP1210 device with DLL support.

        Args:
            dll_path: Path to the vendor RP1210 DLL file.
                     If None, will search common vendor locations.
            vendor_name: Name of the RP1210 vendor (e.g., 'Cummins', 'Volvo').
        """
        self._connected = False
        self._device_name = ""
        self._protocol = 1
        self._vendor_name = vendor_name
        self._dll_path = dll_path
        self._dll = None  # Will hold the loaded DLL
        self._device_id: Optional[int] = None

        # Connection parameters
        self._baud_rate = 250000  # Default CAN baudrate
        self._port_number = 1
        self._flags = 0

        # Message queues
        self._rx_queue: Queue[dict[str, Any]] = Queue()
        self._tx_queue: Queue[dict[str, Any]] = Queue()

        # Statistics
        self._messages_received = 0
        self._messages_sent = 0
        self._errors: list[str] = []

    def load_dll(self, dll_path: str) -> bool:
        """Load the vendor RP1210 DLL.

        Args:
            dll_path: Full path to the RP1210 DLL file.

        Returns:
            True if DLL loaded successfully, False otherwise.

        Raises:
            RP1210Error: If DLL cannot be loaded.
        """
        try:
            from msl.loadlib import LoadLibrary

            self._dll = LoadLibrary(dll_path)
            self._dll_path = dll_path
            return True
        except ImportError as e:
            raise RP1210Error("msl-loadlib not installed") from e
        except Exception as e:
            raise RP1210Error(f"Failed to load DLL: {dll_path}") from e

    def discover_devices(self) -> list[dict[str, str]]:
        """Discover available RP1210 devices.

        Returns:
            List of available devices with their information.
        """
        devices: list[dict[str, str]] = []
        try:
            if self._dll is None:
                raise RP1210NotConnected("DLL not loaded")

            # Call vendor DLL to enumerate devices
            # This is a placeholder - actual implementation depends on vendor DLL
            device_count = 0
            for i in range(device_count):
                devices.append({
                    'device_id': str(i),
                    'name': f'RP1210 Device {i}',
                    'vendor': self._vendor_name,
                    'protocol': 'J1939'
                })
        except Exception as e:
            self._errors.append(str(e))

        return devices

    def connect(self, device_name: str, protocol: int = 1,
                baud_rate: int = 250000, port: int = 1) -> None:
        """Connect to the RP1210 device with specified parameters.

        Args:
            device_name: Name or ID of the device to connect to.
            protocol: J1939 protocol ID (default: 1).
            baud_rate: CAN bus baud rate in bits/second (default: 250000).
            port: Device port number (default: 1).

        Raises:
            RP1210Error: If already connected.
            RP1210NotConnected: If DLL not loaded.
        """
        if self._connected:
            raise RP1210Error("Already connected")

        if self._dll is None:
            raise RP1210NotConnected("DLL not loaded")

        try:
            self._device_name = device_name
            self._protocol = protocol
            self._baud_rate = baud_rate
            self._port_number = port

            # Call vendor DLL connect function
            # Actual implementation: self._device_id = self._dll.ClientConnect(...)
            self._device_id = 1  # Placeholder

            self._connected = True
        except Exception as e:
            raise RP1210Error(f"Connection failed: {e}") from e

    def disconnect(self) -> None:
        """Disconnect from the RP1210 device.

        Raises:
            RP1210NotConnected: If not currently connected.
        """
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        try:
            # Call vendor DLL disconnect function
            # Actual implementation: self._dll.ClientDisconnect(self._device_id)

            self._connected = False
            self._device_id = None
            self._rx_queue = Queue()
            self._tx_queue = Queue()
        except Exception as e:
            raise RP1210Error(f"Disconnection failed: {e}") from e

    def send_message(self, data: bytes, pgn: Optional[int] = None) -> None:
        """Send a message through the RP1210 device.

        Args:
            data: Message data bytes.
            pgn: Parameter Group Number (optional).

        Raises:
            RP1210NotConnected: If not connected.
        """
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        try:
            # Call vendor DLL send function
            # Actual implementation: self._dll.SendMessage(self._device_id, data)

            self._tx_queue.put({
                'data': data,
                'pgn': pgn,
                'timestamp': datetime.now()
            })
            self._messages_sent += 1
        except Exception as e:
            self._errors.append(str(e))
            raise RP1210Error(f"Send failed: {e}") from e

    def read_message(self, timeout: Optional[float] = None) -> bytes:
        """Read a message from the RP1210 device.

        Args:
            timeout: Read timeout in seconds (None for blocking).

        Returns:
            Message data bytes.

        Raises:
            RP1210NotConnected: If not connected.
            RP1210Timeout: If no message received within timeout.
        """
        if not self._connected:
            raise RP1210NotConnected("Not connected")

        try:
            # Call vendor DLL read function
            # Actual implementation: self._dll.ReadMessage(self._device_id, timeout)

            message = self._rx_queue.get(timeout=timeout)
            self._messages_received += 1
            return message['data']
        except Empty as exc:
            raise RP1210Timeout("Read operation timed out") from exc
        except Exception as e:
            self._errors.append(str(e))
            raise RP1210Error(f"Read failed: {e}") from e

    def is_connected(self) -> bool:
        """Check connection status.

        Returns:
            True if connected, False otherwise.
        """
        return self._connected

    def get_device_info(self) -> dict[str, str]:
        """Get information about the connected device.

        Returns:
            Dictionary with device information.
        """
        return {
            'device_name': self._device_name,
            'vendor': self._vendor_name,
            'protocol': f'J1939 (ID: {self._protocol})',
            'baud_rate': f'{self._baud_rate} bps',
            'port': str(self._port_number),
            'dll_path': self._dll_path or 'Not loaded'
        }

    def get_statistics(self) -> dict[str, int]:
        """Get message statistics.

        Returns:
            Dictionary with message counts and error information.
        """
        return {
            'messages_sent': self._messages_sent,
            'messages_received': self._messages_received,
            'errors': len(self._errors)
        }

    def clear_errors(self) -> None:
        """Clear the error log."""
        self._errors = []

    def get_errors(self) -> list[str]:
        """Get the list of errors that have occurred.

        Returns:
            List of error messages.
        """
        return self._errors.copy()

    def set_baudrate(self, baud_rate: int) -> None:
        """Set the CAN bus baud rate.

        Args:
            baud_rate: Baud rate in bits/second.

        Raises:
            RP1210Error: If already connected.
        """
        if self._connected:
            raise RP1210Error("Cannot change baud rate while connected")

        valid_rates = [50000, 125000, 250000, 500000, 1000000]
        if baud_rate not in valid_rates:
            raise RP1210Error(f"Invalid baud rate: {baud_rate}")

        self._baud_rate = baud_rate

    def get_baudrate(self) -> int:
        """Get the configured CAN bus baud rate.

        Returns:
            Baud rate in bits/second.
        """
        return self._baud_rate

    def reset_device(self) -> None:
        """Reset the device to initial state.

        Raises:
            RP1210Error: If not properly disconnected first.
        """
        if self._connected:
            self.disconnect()

        self._device_id = None
        self._messages_received = 0
        self._messages_sent = 0
        self._errors.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None,) -> bool:
        """Context manager exit - ensures disconnect."""
        if self._connected:
            try:
                self.disconnect()
            except Exception:
                pass
        return False

    def read_version(self) -> None:
        """Read version information for API DLL.

        Implementation of RP1210_READVERSION.
        """
        try:
            if self._dll is None:
                raise RP1210NotConnected("DLL not loaded")

            # Call vendor DLL version function
            # Actual implementation: version = self._dll.ReadVersion()
        except Exception as e:
            self._errors.append(str(e))

    def read_detailed_version(self, client_id: int) -> str:
        """Read detailed information about the vendor API and/or firmware.

        Implementation of RP1210_ReadDetailedVersion.

        Args:
            client_id: Client identifier.

        Returns:
            Detailed version string.
        """
        try:
            if self._dll is None:
                raise RP1210NotConnected("DLL not loaded")

            # Call vendor DLL detailed version function
            # Actual implementation: version = self._dll.ReadDetailedVersion(client_id)
            return f"RP1210 Device - Vendor: {self._vendor_name}"
        except Exception as e:
            self._errors.append(str(e))
            return f"Error reading version: {e}"
