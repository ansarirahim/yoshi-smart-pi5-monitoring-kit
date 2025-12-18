# XY-MD02 Temperature/Humidity Sensor - Modbus Protocol Guide

## Overview

The XY-MD02 is an RS485-based temperature and humidity sensor that communicates using the Modbus RTU protocol. This guide explains how to use it with Python and the minimalmodbus library.

---

## Hardware Setup

### Wiring Diagram

```
XY-MD02 Sensor           USB-RS485 Converter        Raspberry Pi
────────────────         ───────────────────        ─────────────
    A (RS485+) ─────────► A (RS485+)
    B (RS485-) ─────────► B (RS485-)
    GND        ─────────► GND  ─────────────────► GND (Pin 6)
               ◄─────────────────────────────────┤ 5V Powered
                                   USB ─────────► USB Port
```

### Connection Details

| Component | Pin/Color | Connection |
|-----------|-----------|------------|
| **XY-MD02** | A | RS485 A (white wire) |
| **XY-MD02** | B | RS485 B (green wire) |
| **XY-MD02** | GND | RS485 GND (black wire) |
| **USB-RS485** | VCC | USB Power (red wire) |
| **USB-RS485** | GND | USB Ground (black wire) |
| **Raspberry Pi** | USB Port | USB-RS485 Converter |

---

## Modbus Protocol Reference

### Read Temperature & Humidity Command

```
Master Request (Read Input Registers 0x0001-0x0002):
┌─────────────────────────────────────────┐
│ Byte Position │ Field         │ Value   │
├───────────────┼───────────────┼─────────┤
│ 0             │ Device Address│ 0x01    │
│ 1             │ Function Code │ 0x04    │
│ 2-3           │ Start Address │ 0x0001  │
│ 4-5           │ Quantity      │ 0x0002  │
│ 6-7           │ CRC-16        │ 0x**** │
└─────────────────────────────────────────┘

Slave Response:
┌─────────────────────────────────────────┐
│ Byte Position │ Field         │ Value   │
├───────────────┼───────────────┼─────────┤
│ 0             │ Device Address│ 0x01    │
│ 1             │ Function Code │ 0x04    │
│ 2             │ Byte Count    │ 0x04    │
│ 3-4           │ Temperature   │ 0x****  │
│ 5-6           │ Humidity      │ 0x****  │
│ 7-8           │ CRC-16        │ 0x**** │
└─────────────────────────────────────────┘
```

### Data Format

#### Temperature (Register 0x0001)
- **Type**: Signed 16-bit integer (big-endian)
- **Range**: -40 to 80°C
- **Resolution**: 0.1°C
- **Formula**: `temperature = raw_value / 10.0`

**Example**:
- Raw: `0x0131` = 305 (decimal)
- Result: 305 / 10 = **30.5°C**

#### Humidity (Register 0x0002)
- **Type**: Unsigned 16-bit integer (big-endian)
- **Range**: 0 to 100% RH
- **Resolution**: 0.1% RH
- **Formula**: `humidity = raw_value / 10.0`

**Example**:
- Raw: `0x0222` = 546 (decimal)
- Result: 546 / 10 = **54.6% RH**

---

## Installation

### Prerequisites

```bash
# Install required packages
pip install minimalmodbus pyserial

# Or with system override
pip install minimalmodbus pyserial --break-system-packages
```

### Verify Installation

```bash
python -c "import minimalmodbus; print('minimalmodbus OK')"
python -c "import serial; print('pyserial OK')"
```

---

## Usage

### Basic Usage

```bash
# Run with defaults (port: /dev/ttyUSB0, slave: 1, baudrate: 9600)
python md02.py

# With custom port
python md02.py --port /dev/ttyACM0

# With custom interval (faster readings)
python md02.py --interval 1.0

# All options
python md02.py --port /dev/ttyUSB0 --slave 1 --baudrate 9600 --interval 2.0 --timeout 1.5
```

### Output Example

```
======================================================================
XY-MD02 TEMPERATURE/HUMIDITY SENSOR - CONTINUOUS TEST
======================================================================
Port:        /dev/ttyUSB0
Slave ID:    1
Baudrate:    9600
Interval:    2.0s
Timeout:     1.5s
======================================================================
Press CTRL+C to stop

[0001] ✓ Temp:  23.5°C | Humidity:  55.2%RH
[0002] ✓ Temp:  23.4°C | Humidity:  55.3%RH
[0003] ✓ Temp:  23.5°C | Humidity:  55.1%RH
[0004] ✓ Temp:  23.6°C | Humidity:  55.0%RH
^C
======================================================================
TEST STOPPED BY USER
======================================================================
Total reads:    4
Errors:         0
Success rate:   100.0%
======================================================================
```

---

## Troubleshooting

### Error: "Device not found"

```
Solution: Check USB connection
1. ls /dev/tty* | grep -E "USB|ACM"
2. Check if device appears as /dev/ttyUSB0 or /dev/ttyACM0
3. Try: python md02.py --port /dev/ttyACM0
```

### Error: "Port timeout"

```
Solution: Adjust timeout value
python md02.py --timeout 2.0

Or check baudrate matches sensor setting (default: 9600)
```

### Error: "CRC error"

```
Solution: Verify wiring
- Check A and B lines are not swapped
- Verify GND connection
- Try different baudrate: python md02.py --baudrate 19200
```

### Error: "No data / All zeros"

```
Solution: Check sensor power
1. Verify 5V power to USB-RS485 converter
2. Check USB connection is secure
3. Test with: dmesg | tail (look for USB messages)
```

---

## Python Code Example

### Using minimalmodbus directly

```python
import minimalmodbus
import serial
import struct

# Create instrument
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.mode = minimalmodbus.MODE_RTU
instrument.serial.baudrate = 9600
instrument.serial.timeout = 1.5

# Read registers
regs = instrument.read_registers(
    registeraddress=0x0001,
    number_of_registers=2,
    functioncode=4
)

# Parse data
temp_raw = struct.unpack('>h', regs[0].to_bytes(2, 'big'))[0]
hum_raw = regs[1]

temperature = temp_raw / 10.0
humidity = hum_raw / 10.0

print(f"Temperature: {temperature:.1f}°C")
print(f"Humidity: {humidity:.1f}%RH")
```

### Using with error handling

```python
import minimalmodbus
import time

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.serial.timeout = 1.5

try:
    for i in range(10):
        try:
            temp = instrument.read_register(0x0001, number_of_decimals=1, functioncode=4) / 10.0
            hum = instrument.read_register(0x0002, number_of_decimals=1, functioncode=4) / 10.0
            print(f"Temp: {temp}°C, Humidity: {hum}%")
        except Exception as e:
            print(f"Read error: {e}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopped")
```

---

## Register Map

### Input Registers (Function Code 4)

| Address | Name | Type | Range | Format |
|---------|------|------|-------|--------|
| 0x0001 | Temperature | Int16 | -40 to 80 | /10 |
| 0x0002 | Humidity | UInt16 | 0 to 100 | /10 |

### Holding Registers (Function Code 3/6)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0001 | Slave Address | Device address (0x01-0xFF) |
| 0x0002 | Baudrate | 0=9600, 1=19200, 2=38400, 3=57600 |

---

## Advanced: Changing Sensor Address

```python
import minimalmodbus

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # Current address
instrument.serial.timeout = 1.5

# Write new address to register 0x0001
instrument.write_register(
    registeraddress=0x0001,
    value=0x02,  # New address
    number_of_decimals=0,
    functioncode=6
)

print("Device address changed to 0x02")

# Next time, create instrument with new address:
# instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 2)
```

---

## Command Reference

### Available Commands

```bash
# Show help
python md02.py --help

# Verbose output with 1-second interval
python md02.py --interval 1.0

# Test different port
python md02.py --port /dev/ttyACM0

# Custom slave ID
python md02.py --slave 2

# Faster baudrate
python md02.py --baudrate 19200

# Longer timeout
python md02.py --timeout 2.5
```

---

## Sensor Specifications

| Parameter | Value |
|-----------|-------|
| **Temperature Range** | -40°C to 80°C |
| **Humidity Range** | 0% to 100% RH |
| **Temperature Accuracy** | ±2°C |
| **Humidity Accuracy** | ±5% RH |
| **Response Time** | <3s |
| **Communication** | Modbus RTU (RS485) |
| **Baudrate** | 9600 bps (default) |
| **Slave Address** | 0x01 (default, configurable) |
| **Power Supply** | 5V via USB-RS485 converter |

---

## Support & Documentation

- **Modbus Specification**: http://www.modbus.org
- **minimalmodbus Docs**: https://minimalmodbus.readthedocs.io
- **RS485 Basics**: https://en.wikipedia.org/wiki/RS-485

