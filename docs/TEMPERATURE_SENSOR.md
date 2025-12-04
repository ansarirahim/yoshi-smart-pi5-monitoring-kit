# Temperature & Humidity Sensor Module

## Overview

Modbus RTU communication module for RS485 temperature/humidity sensors (e.g., XY-MD02, SHT20-based sensors).

**Author:** A.R. Ansari
**Module:** `src/sensors/temperature.py`
**Tests:** `tests/test_sensors/test_temperature.py`

---

## Features

- ✅ Modbus RTU protocol support (Function Code 0x04)
- ✅ CRC16 validation
- ✅ Signed temperature values (-40°C to +80°C)
- ✅ Timestamp logging on every reading
- ✅ **Comprehensive hardware diagnostics**
- ✅ Root cause analysis for common issues

---

## Hardware Requirements

| Component | Specification |
|-----------|---------------|
| Raspberry Pi | Pi 4 or compatible |
| RS485 Converter | USB-to-RS485 (CH340, CP2102, FTDI) |
| Sensor | Modbus RTU compatible (XY-MD02, SHT20, etc.) |
| Power Supply | 12V or 24V DC (sensor dependent) |
| Wiring | Twisted pair recommended for A/B lines |

### XY-MD02 Sensor

![XY-MD02 Temperature Humidity Sensor](images/xy_md02_sensor.png)

**Terminal Connections:**
| Terminal | Label | Description |
|----------|-------|-------------|
| 1 | B- | RS485 Data B (negative) |
| 2 | A+ | RS485 Data A (positive) |
| 3 | - | Power GND |
| 4 | + | Power VCC (DC 5-30V) |

### Wiring Diagram (Raspberry Pi 5 4GB - Real Setup)

**Wire Colors Used:**
| Wire | Color | Connection |
|------|-------|------------|
| A+ (Data+) | 🔵 Blue | RS485 A+ to Sensor Terminal 2 |
| B- (Data-) | 🟡 Yellow | RS485 B- to Sensor Terminal 1 |
| GND | ⚫ Black | Common Ground |
| +5V Power | 🔴 Red | USB-RS485 Converter to Sensor Power |

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║                    RASPBERRY PI 5 (4GB) TEMPERATURE SENSOR WIRING                      ║
║                              Real Hardware Configuration                               ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                        ║
║  ┌─────────────────────────────┐      ┌──────────────────┐      ┌─────────────────┐   ║
║  │    RASPBERRY PI 5 (4GB)     │      │  USB to RS485    │      │  XY-MD02 SENSOR │   ║
║  │  ┌───────────────────────┐  │      │   Converter      │      │  ┌───────────┐  │   ║
║  │  │ ████████████████████ │  │      │  ┌──────────┐    │      │  │  SHT20    │  │   ║
║  │  │ █  Raspberry Pi 5  █ │  │      │  │ CH340/   │    │      │  │  Probe    │  │   ║
║  │  │ █     4GB RAM      █ │  │      │  │ CP2102   │    │      │  └─────┬─────┘  │   ║
║  │  │ ████████████████████ │  │      │  └──────────┘    │      │        │        │   ║
║  │  │                      │  │      │                  │      │ ┌──────┴──────┐ │   ║
║  │  │  USB-A    USB-A      │  │      │  ┌──┐ ┌──┐      │      │ │ 1  2  3  4  │ │   ║
║  │  │  ┌──┐     ┌──┐       │  │      │  │A+│ │B-│      │      │ │ B- A+ -  +  │ │   ║
║  │  │  │██│     │██│◄──────┼──┼──USB─┼──│  │ │  │      │      │ └─┬──┬──┬──┬──┘ │   ║
║  │  │  └──┘     └──┘       │  │ Cable│  └┬─┘ └┬─┘      │      │   │  │  │  │    │   ║
║  │  └──────────────────────┘  │      │   │    │        │      └───┼──┼──┼──┼────┘   ║
║  │         GPIO Header        │      │  GND  +5V       │          │  │  │  │        ║
║  │   ● ● ● ● ● ● ● ● ● ● ●   │      │   │    │        │          │  │  │  │        ║
║  │   ● ● ● ● ● ● ● ● ● ● ●   │      │   ▼    ▼        │          │  │  │  │        ║
║  └─────────────────────────────┘      └──────────────────┘          │  │  │  │        ║
║                                                                     │  │  │  │        ║
║     WIRE CONNECTIONS:                                               │  │  │  │        ║
║     ════════════════                                                │  │  │  │        ║
║                                                                     │  │  │  │        ║
║     🔵 Blue Wire (A+) ─────────────────────────────────────────────┼──┘  │  │        ║
║        RS485 Converter A+ ──────────────────► Sensor Terminal 2 (A+)      │  │        ║
║                                                                           │  │        ║
║     🟡 Yellow Wire (B-) ──────────────────────────────────────────────────┘  │        ║
║        RS485 Converter B- ──────────────────► Sensor Terminal 1 (B-)         │        ║
║                                                                              │        ║
║     ⚫ Black Wire (GND) ───────────────────────────────────────────────┬─────┘        ║
║        RS485 Converter GND ─────────────────► Sensor Terminal 3 (-)    │              ║
║                                                                        │              ║
║     🔴 Red Wire (+5V) ─────────────────────────────────────────────────┘              ║
║        RS485 Converter +5V ─────────────────► Sensor Terminal 4 (+)                   ║
║                                                                                        ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║  ⚠️  CRITICAL NOTES:                                                                  ║
║  • GND (Black) MUST be connected - floating ground causes garbage data                ║
║  • A+ (Blue) and B- (Yellow) MUST NOT be swapped - causes AB_LINES_SWAPPED error     ║
║  • Sensor requires separate power (+5V from converter or external 5-30V DC)           ║
║  • USB-RS485 converter draws power from Raspberry Pi USB port                         ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝
```

⚠️ **Critical:** Always connect GND between converter and sensor!

---

## Modbus Protocol Reference

### Function Codes

![Modbus Protocol Overview](images/modbus_protocol_overview.png)

| Function Code | Description |
|---------------|-------------|
| 0x03 | Read keep register (holding register) |
| 0x04 | Read input register (temperature/humidity) |
| 0x06 | Write a single keep register |
| 0x10 | Write multiple keep registers |

### Register Map

| Register Type | Address | Contents | Bytes |
|---------------|---------|----------|-------|
| Input Register | 0x0001 | Temperature | 2 |
| Input Register | 0x0002 | Humidity | 2 |
| Keep Register | 0x0101 | Device Address | 2 |
| Keep Register | 0x0102 | Baud Rate (0:9600, 1:14400, 2:19200) | 2 |
| Keep Register | 0x0103 | Temperature Correction (-10°C~10°C) | 2 |
| Keep Register | 0x0104 | Humidity Correction (-10%RH~10%RH) | 2 |

### Communication Frame Format

![Modbus Communication Format](images/modbus_communication_format.png)

#### Master Send Format (Request)

| Device Address | Function Code | Starting Address Hi | Starting Address Li | Quantity Hi | Quantity Li | CRC Hi | CRC Li |
|----------------|---------------|---------------------|---------------------|-------------|-------------|--------|--------|

#### Response Format from Slave

| Device Address | Function Code | Bytes | Register 1 Hi | Register 1 Li | ... | Register N Hi | Register N Li | CRC Hi | CRC Li |
|----------------|---------------|-------|---------------|---------------|-----|---------------|---------------|--------|--------|

### Frame Examples

#### Read Temperature Only (0x04)

| Field | Request | Response |
|-------|---------|----------|
| Device Address | 0x01 | 0x01 |
| Function Code | 0x04 | 0x04 |
| Start Address | 0x00 0x01 | - |
| Quantity | 0x00 0x01 | - |
| Bytes | - | 0x02 |
| Temperature | - | 0x01 0x31 |
| CRC | 0x60 0x0A | 0x79 0x74 |

**Example:** Temperature = 0x0131 = 305 decimal → **30.5°C**

> **Note:** Temperature is a signed hexadecimal. Value 0xFF33 = -205 decimal → **-20.5°C**

#### Read Humidity Only (0x04)

| Field | Request | Response |
|-------|---------|----------|
| Device Address | 0x01 | 0x01 |
| Function Code | 0x04 | 0x04 |
| Start Address | 0x00 0x02 | - |
| Quantity | 0x00 0x01 | - |
| Bytes | - | 0x02 |
| Humidity | - | 0x02 0x22 |
| CRC | 0x90 0x0A | 0xD1 0xBA |

**Example:** Humidity = 0x0222 = 546 decimal → **54.6%RH**

#### Read Temperature & Humidity Combined (0x04)

| Field | Request | Response |
|-------|---------|----------|
| Device Address | 0x01 | 0x01 |
| Function Code | 0x04 | 0x04 |
| Start Address | 0x00 0x01 | - |
| Quantity | 0x00 0x02 | - |
| Bytes | - | 0x04 |
| Temperature | - | 0x01 0x31 |
| Humidity | - | 0x02 0x22 |
| CRC | 0x20 0x0B | 0x2A 0xCE |

**Example:** Temperature = 30.5°C, Humidity = 54.6%RH

---

## Quick Start

```python
from src.sensors.temperature import TemperatureSensor

# Initialize sensor
sensor = TemperatureSensor(
    port="/dev/ttyUSB0",
    baudrate=9600,
    slave_address=0x01
)

# Connect and read
if sensor.connect():
    reading = sensor.read()
    if reading:
        print(reading)  # [2024-01-15 10:30:45] Temperature: 25.5°C, Humidity: 60.2%RH
    sensor.disconnect()
```

---

## Diagnostic System

The module includes comprehensive diagnostics to identify hardware issues.

### Running Diagnostics

```python
sensor = TemperatureSensor(port="/dev/ttyUSB0")
results = sensor.run_full_diagnostic()

for result in results:
    print(result)
    if not result.is_ok:
        print(f"  Suggestion: {result.suggestion}")
```

### Diagnostic Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| `OK` | Operation successful | - |
| `NO_PYSERIAL` | pyserial not installed | Missing dependency |
| `PORT_NOT_FOUND` | Serial port not detected | USB not connected |
| `NO_RS485_CONVERTER` | No serial devices found | Converter unplugged |
| `NO_SENSOR_RESPONSE` | Sensor not responding | Power/wiring issues |
| `AB_LINES_SWAPPED` | A and B signals reversed | Incorrect wiring |
| `GROUND_NOT_CONNECTED` | Missing ground connection | GND not wired |
| `CRC_ERROR` | Data corruption | Interference/long cables |
| `INVALID_RESPONSE` | Unexpected data format | Wrong settings |
| `BAUDRATE_MISMATCH` | Speed mismatch | Wrong baudrate |
| `WRONG_SLAVE_ADDRESS` | Address mismatch | Wrong slave ID |

---

## Troubleshooting Guide

### Issue 1: No Response from Sensor

**Symptoms:**
- `diagnose_sensor_response()` returns `NO_SENSOR_RESPONSE`
- 0 bytes received

**Root Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Sensor not powered | Check 12V/24V power supply |
| A/B lines disconnected | Verify A+ and B- connections |
| Wrong slave address | Try addresses 0x01 through 0x0F |
| Baudrate mismatch | Test 4800, 9600, 19200 baud |

---

### Issue 2: Garbage/Random Data

**Symptoms:**
- `diagnose_sensor_response()` returns `AB_LINES_SWAPPED`
- Random bytes in response

**Root Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| A and B swapped | Swap A+ and B- wires |
| Noise interference | Use shielded twisted pair cable |
| Multiple masters | Only one master on RS485 bus |

**Wire Labeling Note:**
```
Some devices use different labels:
  A+ = D+  = Data+
  B- = D-  = Data-
```

---

### Issue 3: All 0xFF Received

**Symptoms:**
- `diagnose_sensor_response()` returns `GROUND_NOT_CONNECTED`


---

## Test Suite

### Test Module Structure

```
tests/test_sensors/
├── __init__.py
└── test_temperature.py    # 19 test cases (including hardware diagnostics)
```

### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| CRC Calculation | 3 | Modbus CRC16 validation |
| Signed Parsing | 4 | 16-bit signed integer conversion |
| SensorReading | 3 | Dataclass and formatting |
| Hardware Diagnostics | 6 | Root cause analysis for wiring issues |
| Modbus Frame | 3 | Request/response parsing |

### Running Tests

```bash
# Run all temperature sensor tests
python -m pytest tests/test_sensors/test_temperature.py -v

# Run with timestamp logging
python -m pytest tests/test_sensors/test_temperature.py -v 2>&1 | \
  while read line; do echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line"; done
```

---

## Test Report

### Test Execution Summary (19 Tests)

```
[2025-12-04 04:48:08] ============================================
[2025-12-04 04:48:08] Temperature Sensor Test Suite - Full Report
[2025-12-04 04:48:08] ============================================

[2025-12-04 04:48:08] === SECTION 1: CRC CALCULATION TESTS ===
[2025-12-04 04:48:08] ✓ Test 1: CRC known value = 0x0B20 - PASSED
[2025-12-04 04:48:08] ✓ Test 2: CRC empty = 0xFFFF - PASSED
[2025-12-04 04:48:08] ✓ Test 3: CRC deterministic - PASSED

[2025-12-04 04:48:08] === SECTION 2: SIGNED 16-BIT PARSING TESTS ===
[2025-12-04 04:48:08] ✓ Test 4: Parse 0x00FA = 250 (25.0°C) - PASSED
[2025-12-04 04:48:08] ✓ Test 5: Parse 0x0000 = 0 - PASSED
[2025-12-04 04:48:08] ✓ Test 6: Parse 0xFFEC = -20 (-2.0°C) - PASSED
[2025-12-04 04:48:08] ✓ Test 7: Parse 0x8000 = -32768 - PASSED

[2025-12-04 04:48:08] === SECTION 3: SENSOR READING TESTS ===
[2025-12-04 04:48:08] ✓ Test 8: SensorReading creation - PASSED
[2025-12-04 04:48:08] ✓ Test 9: String format with timestamp - PASSED
[2025-12-04 04:48:08] ✓ Test 10: Valid range check (-40 to 80°C) - PASSED

[2025-12-04 04:48:08] === SECTION 4: HARDWARE DIAGNOSTIC TESTS ===
[2025-12-04 04:48:08] ✓ Test 11: No response (0 bytes)
[2025-12-04 04:48:08]   Diagnostic Code: NO_SENSOR_RESPONSE
[2025-12-04 04:48:08]   Root Causes:
[2025-12-04 04:48:08]     • Sensor not powered (check 12V/24V supply)
[2025-12-04 04:48:08]     • A/B lines not connected
[2025-12-04 04:48:08]     • Wrong slave address (try 0x01-0x0F)
[2025-12-04 04:48:08]     • Baudrate mismatch (try 9600, 4800, 19200)

[2025-12-04 04:48:08] ✓ Test 12: All 0xFF received
[2025-12-04 04:48:08]   Diagnostic Code: GROUND_NOT_CONNECTED
[2025-12-04 04:48:08]   Root Causes:
[2025-12-04 04:48:08]     • GND wire not connected between RS485 converter and sensor
[2025-12-04 04:48:08]     • Input is floating, reads as high (0xFF)

[2025-12-04 04:48:08] ✓ Test 13: All 0x00 received
[2025-12-04 04:48:08]   Diagnostic Code: GROUND_NOT_CONNECTED
[2025-12-04 04:48:08]   Root Causes:
[2025-12-04 04:48:08]     • A/B lines shorted together
[2025-12-04 04:48:08]     • Damaged cable causing short circuit

[2025-12-04 04:48:08] ✓ Test 14: Garbage/random data
[2025-12-04 04:48:08]   Diagnostic Code: AB_LINES_SWAPPED
[2025-12-04 04:48:08]   Root Causes:
[2025-12-04 04:48:08]     • A and B signal lines REVERSED
[2025-12-04 04:48:08]     • Swap A↔B wires at the RS485 converter
[2025-12-04 04:48:08]     • Note: Some devices label A=D+, B=D-

[2025-12-04 04:48:08] ✓ Test 15: CRC mismatch
[2025-12-04 04:48:08]   Diagnostic Code: CRC_ERROR
[2025-12-04 04:48:08]   Root Causes:
[2025-12-04 04:48:08]     • Long cable (>100m) without termination resistor
[2025-12-04 04:48:08]     • Electrical interference - use shielded cable
[2025-12-04 04:48:08]     • Loose terminal connections

[2025-12-04 04:48:08] ✓ Test 16: Valid response (25.5°C, 60.0%RH)
[2025-12-04 04:48:08]   Diagnostic Code: OK
[2025-12-04 04:48:08]   Sensor communication successful

[2025-12-04 04:48:08] === SECTION 5: MODBUS FRAME TESTS ===
[2025-12-04 04:48:08] ✓ Test 17: Build request frame
[2025-12-04 04:48:08]   Frame: 01 04 00 01 00 02 20 0B
[2025-12-04 04:48:08] ✓ Test 18: Parse response (25.5°C, 60.0%RH) - PASSED
[2025-12-04 04:48:08] ✓ Test 19: Parse negative temperature (-5.0°C) - PASSED

[2025-12-04 04:48:08] ============================================
[2025-12-04 04:48:08] TEST SUMMARY: 19/19 PASSED
[2025-12-04 04:48:08] ✓ ALL TESTS PASSED SUCCESSFULLY!
[2025-12-04 04:48:08] ============================================
```

### Test Case Details

#### 1. CRC Calculation Tests

| Test | Input | Expected | Status |
|------|-------|----------|--------|
| Known value | `01 04 00 01 00 02` | 0x0B20 | ✅ PASS |
| Empty data | `(empty)` | 0xFFFF | ✅ PASS |
| Single byte | `01` | Valid CRC | ✅ PASS |
| Deterministic | Same input twice | Same CRC | ✅ PASS |

#### 2. Signed 16-bit Parsing Tests

| Test | Input (hex) | Expected | Status |
|------|-------------|----------|--------|
| Positive (25.0°C) | 0x00FA | 250 | ✅ PASS |
| Zero | 0x0000 | 0 | ✅ PASS |
| Negative (-2.0°C) | 0xFFEC | -20 | ✅ PASS |
| Max positive | 0x7FFF | 32767 | ✅ PASS |
| Min negative | 0x8000 | -32768 | ✅ PASS |

#### 3. Modbus Frame Tests

| Test | Description | Expected Frame | Status |
|------|-------------|----------------|--------|
| Build request | Read 2 registers from 0x0001 | `01 04 00 01 00 02 20 0B` | ✅ PASS |
| Parse response | 25.5°C, 60.0%RH | Correct values | ✅ PASS |
| Negative temp | -5.0°C | Correct parsing | ✅ PASS |

---

## Hardware Diagnostic Tests

### Test Scenarios with Root Cause Analysis

| Scenario | Symptom | Diagnostic Code | Root Cause | Solution |
|----------|---------|-----------------|------------|----------|
| No USB device | Port not found | `PORT_NOT_FOUND` | USB disconnected | Reconnect USB cable |
| Sensor unpowered | No response | `NO_SENSOR_RESPONSE` | No 12V/24V | Check power supply |
| A/B swapped | Garbage data | `AB_LINES_SWAPPED` | Reversed wiring | Swap A↔B wires |
| No ground | All 0xFF | `GROUND_NOT_CONNECTED` | GND missing | Connect ground wire |
| Short circuit | All 0x00 | `GROUND_NOT_CONNECTED` | A/B shorted | Check for shorts |
| Long cable | CRC errors | `CRC_ERROR` | Signal degradation | Add 120Ω terminator |
| Wrong address | Different slave | `WRONG_SLAVE_ADDRESS` | Config mismatch | Update slave_address |
| Wrong baud | Garbled data | `BAUDRATE_MISMATCH` | Speed mismatch | Try 9600/4800/19200 |

---

## API Reference

### Classes

#### `TemperatureSensor`

```python
class TemperatureSensor:
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        slave_address: int = 0x01,
        timeout: float = 0.5
    )

    def connect(self) -> bool
    def disconnect(self) -> None
    def read(self) -> Optional[SensorReading]
    def list_serial_ports(self) -> List[dict]
    def diagnose_connection(self) -> DiagnosticResult
    def diagnose_sensor_response(self) -> DiagnosticResult
    def run_full_diagnostic(self) -> List[DiagnosticResult]
```

#### `SensorReading`

```python
@dataclass
class SensorReading:
    temperature: float  # Celsius
    humidity: float     # %RH
    timestamp: datetime

    def is_valid(self) -> bool  # Check if in range
```

#### `DiagnosticResult`

```python
@dataclass
class DiagnosticResult:
    code: DiagnosticCode
    message: str
    suggestion: str
    raw_data: Optional[bytes]
    timestamp: datetime

    @property
    def is_ok(self) -> bool
```

### Functions

```python
def modbus_crc(data: bytes) -> int
    """Compute Modbus RTU CRC16."""

def parse_signed_16(value: int) -> int
    """Convert unsigned 16-bit to signed."""
```

---

## Example: Full Diagnostic Script

```python
#!/usr/bin/env python3
"""Temperature sensor diagnostic script."""

from datetime import datetime
from src.sensors.temperature import TemperatureSensor, DiagnosticCode

def run_diagnostics():
    print(f"[{datetime.now()}] Starting diagnostics...")

    sensor = TemperatureSensor(
        port="/dev/ttyUSB0",
        baudrate=9600,
        slave_address=0x01
    )

    # List available ports
    ports = sensor.list_serial_ports()
    print(f"\nDetected serial ports:")
    for p in ports:
        rs485 = "✓ RS485" if p['is_rs485'] else ""
        print(f"  {p['device']}: {p['description']} {rs485}")

    # Run full diagnostic
    print(f"\nRunning full diagnostic...")
    results = sensor.run_full_diagnostic()

    # Summary
    passed = sum(1 for r in results if r.is_ok)
    print(f"\nResults: {passed}/{len(results)} tests passed")

    for result in results:
        status = "✓" if result.is_ok else "✗"
        print(f"  {status} {result.code.value}: {result.message}")
        if not result.is_ok:
            print(f"    → {result.suggestion}")

if __name__ == "__main__":
    run_diagnostics()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12-04 | Initial release with diagnostics |
