---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: lisi12345

---

**Describe the bug**
A clear and concise description of what the bug is (e.g., "J1939 Claim Address fails on Nexiq USB-Link 2").

**To Reproduce**
Steps to reproduce the behavior or a minimal code snippet:
1. Initialize RP1210Client with device '...'
2. Send J1939 PGN '....'
3. Observe RP1210Error or unexpected behavior.

**Expected behavior**
A clear and concise description of what you expected to happen (e.g., "Expected a successful PGN 60928 response within 200ms").

**Logs & Communication Traces**
 - **RP1210 Error Code**: [e.g., 128 (ERR_DLL_NOT_FOUND)]
 - **Bus Trace**: (If possible, paste a snippet of the CAN traffic or log file).

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment Information:**
 - Python Version: [e.g., 3.9.12]
 - Operating System: [e.g., Windows 10 64-bit]
 - Library Version: [e.g., v0.1.0-alpha]

**RP1210 Hardware & Driver:**
 - Adapter: [e.g., Nexiq USB-Link 2, Dearborn DPA5, Peak CAN]
 - Driver Version: [e.g., V4.2.0.1]
 - DLL Architecture: [e.g., 32-bit (PE) or 64-bit]

**Additional context**
Add any other context about the problem here (e.g., "Using SimulatedRP1210Device" or "Terminating resistor is present on the bus").
