# prp1210
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build Status](https://img.shields.io/badge/build-alpha-orange)

A modern, developer-friendly Python wrapper for **RP1210** vehicle communication drivers. This library simplifies interfacing with heavy-duty vehicle adapters (Nexiq, Dearborn, etc.) by providing a clean, high-level API for data acquisition and diagnostics.

---

## 🛠 Key Features

- **Automatic DLL Detection:** Smart searching for vendor-specific RP1210 DLLs in Windows system directories (`System32` and `SysWOW64`).
- **Hardware Simulation:** Use the built-in `SimulatedRP1210Device` to develop and test your logic without being tethered to a physical vehicle.
- **Type Safety:** Full type-hinting across the library for a superior developer experience and fewer runtime errors.
- **Modern Packaging:** Built with `pyproject.toml` and fully compatible with modern Python build tools.

---

## 🛣 Supported Protocols

| Protocol           | Status          | Description                                                 |
| :----------------- | :-------------- | :---------------------------------------------------------- |
| **CAN (Raw)**      | ⏳ Planned       | Layer 2 raw frame transmission and reception.               |
| **J1939**          | ✅ Supported     | Address claiming, PGN filtering, and transport layer logic. |
| **J1708 / J1587**  | ❌ Not Supported | Legacy heavy-duty communication.                            |
| **ISO15765 (UDS)** | ❌ Not Supported | Unified Diagnostic Services over CAN.                       |

### Why focus on CAN and J1939?
To ensure the highest quality of service, `prp1210` prioritizes the modern CAN stack. We focus on these protocols because:
- **Data Fidelity:** Modern AI and predictive maintenance models require the high-frequency data rates provided by CAN.
- **Industry Direction:** J1939 is the standard for virtually all heavy-duty vehicles produced in the last two decades.
- **Reliability:** By specializing in the CAN stack, we provide lower latency and a more robust interface for critical diagnostic tasks.

---

## 💻 Quick Start

### Installation
```
pip install prp1210
```

### Basic Usage (Simulated)
Develop your logic anywhere, even without an adapter plugged in:
```
from prp1210 import RP1210Client
from prp1210.devices import SimulatedRP1210Device

# Initialize with the simulator
client = RP1210Client(device=SimulatedRP1210Device())

# Connect to the bus
if client.connect():
    print("Successfully connected to the simulated bus!")
    
    # Example: Send a heartbeat or request a PGN
    # client.send_j1939_msg(pgn=61444, priority=3, data=[...])

client.disconnect()
```

---

## 🤝 Contributing
We welcome contributions! To maintain code quality:
1. Branching: Use feature branches for all changes.
2. Merging: We prefer Squash and Merge to maintain a clean, readable history on main.
3. Templates: Please use the provided [Bug Report](./.github/ISSUE_TEMPLATE/bug_report.md) or [Feature Request](./.github/ISSUE_TEMPLATE//feature_request.md) templates.

---


## 📜 License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
