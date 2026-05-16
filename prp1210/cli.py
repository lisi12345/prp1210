"""
RP1210 and J1939 command-line interface tool.

Provides device discovery, diagnostics, and message testing capabilities.
"""

import argparse
import sys

from .common import RP1210Error
from .rp1210.devices import MockRP1210Device, SimulatedRP1210Device


def discover_devices() -> None:
    """Discover and list available RP1210 devices."""
    print("🔍 Scanning for RP1210 devices...\n")

    # In a real implementation, this would query actual hardware
    # For now, show available mock/simulated devices
    devices = [
        {"name": "mock_device", "type": "Mock",
         "description": "Mock device for testing"},
        {"name": "sim_device", "type": "Simulated",
         "description": "Simulated device with realistic behavior"},
    ]

    if devices:
        print("Available devices:")
        for device in devices:
            print(
                f"  • {device['name']:<20} [{device['type']}] - {device['description']}")
    else:
        print("No devices found.")


def check_device_connection(device_name: str, protocol: int = 1) -> None:
    """Test connection to a device."""
    print(
        f"📡 Testing connection to '{device_name}' (protocol: {protocol})...\n")

    try:
        if device_name == "mock_device":
            device = MockRP1210Device()
        elif device_name == "sim_device":
            device = SimulatedRP1210Device()
        else:
            print(f"❌ Unknown device: {device_name}")
            return

        device.connect(device_name, protocol)
        print(f"✅ Connected to {device_name}")
        print(
            f"   Status: {'Connected' if device.is_connected() else 'Disconnected'}")

        # Send test message
        test_data = b"\x18\xFE\xCA\x00\x00\x00\x00\x00"
        device.send_message(test_data, pgn=0xFECA)
        print(f"✅ Test message sent ({len(test_data)} bytes)")

        device.disconnect()
        print(f"✅ Disconnected from {device_name}")

    except RP1210Error as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def list_pgns() -> None:
    """List common J1939 PGNs."""
    print("📋 Common J1939 PGNs:\n")

    pgns = [
        (0xFECA, "DM1 - Active Diagnostic Trouble Codes"),
        (0xFECB, "DM2 - Previously Active Diagnostic Trouble Codes"),
        (0xFECC, "DM3 - Diagnostic Data Clear/Reset for Previously Active DTCs"),
        (0xFECD, "DM4 - Freeze Frame Data"),
        (0xFECE, "DM5 - Expanded Freeze Frame Data"),
        (0x0F004, "Electronic Engine Controller 1 (EEC1)"),
        (0x0F003, "Electronic Retarder Controller (ERC1)"),
        (0x0FEF1, "Cruise Control/Vehicle Speed"),
        (0x0FECA, "Engine Temperature"),
    ]

    for pgn, description in pgns:
        print(f"  • 0x{pgn:05X} - {description}")


def show_info() -> None:
    """Show library information."""
    print("RP1210 and J1939 Communication Library")
    print("=" * 40)
    print("Version: 0.1.0")
    print("Author: Lisi Lei")
    print("License: MIT")
    print("\nSupported Protocols:")
    print("  • RP1210 (Heavy-duty vehicle communication)")
    print("  • J1939 (CAN-based industrial protocol)")
    print("\nFeatures:")
    print("  • Device discovery and management")
    print("  • Message encoding/decoding")
    print("  • Mock and simulated device support")
    print("  • Comprehensive exception handling")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RP1210 and J1939 communication tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rp1210 discover              - Find available RP1210 devices
  rp1210 test mock_device      - Test connection to mock device
  rp1210 pgns                  - List common J1939 PGNs
  rp1210 info                  - Show library information
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # Discover command
    subparsers.add_parser("discover", help="Discover available RP1210 devices")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test device connection")
    test_parser.add_argument("device", help="Device name to test")
    test_parser.add_argument(
        "--protocol", type=int, default=1, help="Protocol ID (default: 1)"
    )

    # PGN list command
    subparsers.add_parser("pgns", help="List common J1939 PGNs")

    # Info command
    subparsers.add_parser("info", help="Show library information")

    args = parser.parse_args()

    if args.command == "discover":
        discover_devices()
    elif args.command == "test":
        check_device_connection(args.device, args.protocol)
    elif args.command == "pgns":
        list_pgns()
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
