# Individual Sensor Test Scripts

Complete collection of sensor test scripts for the Raspberry Pi Smart Monitoring Kit.

---

## Available Sensors

### 1. **Temperature & Humidity (XY-MD02)**
- **Script**: `md02.py`
- **Protocol**: Modbus RTU (RS485)
- **Features**:
  - Continuous reading loop
  - Configurable parameters
  - Error handling with statistics
  - Auto-detection and validation

**Usage**:
```bash
python md02.py
python md02.py --port /dev/ttyUSB0 --interval 1.0
```

**Documentation**: [MD02_MODBUS_GUIDE.md](MD02_MODBUS_GUIDE.md)

### 2. **Motion Sensor (HC-SR501 PIR)**
- **Test File**: `tests/test_sensors/test_motion.py`
- **Type**: Unit tests (16 tests)
- **GPIO**: GPIO17 (Pin 11)
- **Tests Included**:
  - State enumeration
  - Trigger mode configuration
  - Motion event creation
  - GPIO initialization
  - Motion detection logic

**Usage**:
```bash
python -m pytest tests/test_sensors/test_motion.py -v
python -m pytest tests/test_sensors/test_motion.py::TestMotionSensor -v
```

### 3. **Temperature Sensor (Unit Tests)**
- **Test File**: `tests/test_sensors/test_temperature.py`
- **Type**: Unit tests (34 tests)
- **Interface**: RS485 (USB)
- **Tests Included**:
  - Modbus CRC calculation
  - 16-bit signed parsing
  - Sensor reading validation
  - Hardware diagnostics
  - Error recovery scenarios

**Usage**:
```bash
python -m pytest tests/test_sensors/test_temperature.py -v
python -m pytest tests/test_sensors/test_temperature.py::TestTemperatureSensor -v
```

### 4. **Sound Sensor (LM393)**
- **Test File**: `tests/test_sensors/test_sound_interactive.py`
- **Type**: Interactive hardware test
- **GPIO**: GPIO22 (Pin 15)
- **Requirements**: Physical hardware connected

**Usage**:
```bash
python tests/test_sensors/test_sound_interactive.py
```

### 5. **Vibration Sensor (801S)**
- **Test File**: `tests/test_sensors/test_vibration_interactive.py`
- **Type**: Interactive hardware test
- **GPIO**: GPIO27 (Pin 13)
- **Requirements**: Physical hardware connected

**Usage**:
```bash
python tests/test_sensors/test_vibration_interactive.py
```

### 6. **Door Sensor (MC-38)**
- **Test File**: `tests/test_sensors/test_door_interactive.py`
- **Type**: Interactive hardware test
- **GPIO**: GPIO23 (Pin 16)
- **Requirements**: Physical hardware connected

**Usage**:
```bash
python tests/test_sensors/test_door_interactive.py
```

### 7. **Motion Sensor (Interactive)**
- **Test File**: `tests/test_sensors/test_pir_interactive.py`
- **Type**: Interactive hardware test
- **GPIO**: GPIO17 (Pin 11)
- **Tests Included**:
  - Idle state check
  - Motion detection
  - Signal recovery
  - Callback verification

**Usage**:
```bash
python tests/test_sensors/test_pir_interactive.py
```

---

## Quick Reference

### Run All Unit Tests
```bash
# All sensor tests
python -m pytest tests/test_sensors/test_*.py -v

# Only unit tests (skip interactive)
python -m pytest tests/test_sensors/test_temperature.py tests/test_sensors/test_motion.py -v

# With coverage
python -m pytest tests/test_sensors/ --cov=src.sensors
```

### Run Temperature Modbus Test
```bash
# Help
python md02.py --help

# Default (port: /dev/ttyUSB0)
python md02.py

# Custom port
python md02.py --port /dev/ttyACM0

# Faster interval
python md02.py --interval 0.5

# All options
python md02.py --port /dev/ttyUSB0 --slave 1 --baudrate 9600 --interval 1.0
```

### Run Interactive Hardware Tests
```bash
# PIR Motion Sensor
python tests/test_sensors/test_pir_interactive.py

# Sound Sensor
python tests/test_sensors/test_sound_interactive.py

# Vibration Sensor
python tests/test_sensors/test_vibration_interactive.py

# Door Sensor
python tests/test_sensors/test_door_interactive.py
```

---

## GPIO Pin Assignments

| Sensor | GPIO | Pin | Wire Color |
|--------|------|-----|------------|
| PIR Motion | GPIO17 | 11 | Brown |
| Sound | GPIO22 | 15 | White |
| Door | GPIO23 | 16 | White |
| Vibration | GPIO27 | 13 | Gray |
| Temperature | N/A (USB) | - | RS485 |

**Power**: All sensors use 3.3V (Pin 1) and GND (Pin 6)

---

## Installation

### Install Dependencies

```bash
# Basic Python packages
pip install pytest pytest-cov --break-system-packages

# For Modbus temperature sensor
pip install minimalmodbus pyserial --break-system-packages

# For GPIO sensors (on Raspberry Pi only)
pip install RPi.GPIO --break-system-packages

# Or install all at once
pip install pytest pytest-cov minimalmodbus pyserial RPi.GPIO --break-system-packages
```

### Verify Installation

```bash
python -c "import pytest; print('pytest OK')"
python -c "import minimalmodbus; print('minimalmodbus OK')"
python -c "import serial; print('pyserial OK')"
```

---

## Test Results Summary

### Unit Tests Status

| Test Suite | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| Temperature | 34 | ✅ PASS | 77% |
| Motion | 16 | ✅ PASS | 57% |
| Total | 50 | ✅ PASS | - |

### Example Output

```
tests/test_sensors/test_temperature.py::TestModbusCRC PASSED          [ 11%]
tests/test_sensors/test_temperature.py::TestParseSigned16 PASSED      [ 26%]
tests/test_sensors/test_temperature.py::TestSensorReading PASSED      [ 38%]
tests/test_sensors/test_temperature.py::TestTemperatureSensor PASSED  [ 55%]
tests/test_sensors/test_temperature.py::TestDiagnosticResult PASSED   [ 73%]
tests/test_sensors/test_temperature.py::TestHardwareDiagnostics PASSED[100%]

====================== 34 passed in 2.16s ======================
```

---

## Troubleshooting

### ImportError: No module named...
```bash
# Install missing package
pip install [package_name] --break-system-packages
```

### Serial Port Not Found
```bash
# List available ports
ls /dev/tty* | grep -E "USB|ACM"

# Use detected port
python md02.py --port /dev/ttyACM0
```

### CRC/Timeout Errors
```bash
# Increase timeout
python md02.py --timeout 2.0

# Verify baudrate matches sensor
python md02.py --baudrate 9600
```

### GPIO Related Errors
- Must be run on Raspberry Pi with GPIO enabled
- Some tests require physical hardware connected
- Run as root if permission denied: `sudo python script.py`

---

## File Structure

```
individual-sensor-tests/
├── md02.py                      # XY-MD02 Modbus test script
├── MD02_MODBUS_GUIDE.md         # Complete Modbus documentation
└── README.md                    # This file

tests/test_sensors/
├── test_temperature.py          # Temperature unit tests (34)
├── test_motion.py              # Motion sensor unit tests (16)
├── test_pir_interactive.py      # PIR interactive test
├── test_sound_interactive.py    # Sound sensor test
├── test_vibration_interactive.py# Vibration sensor test
└── test_door_interactive.py     # Door sensor test
```

---

## Common Commands

```bash
# Run single test file
python -m pytest tests/test_sensors/test_temperature.py -v

# Run single test class
python -m pytest tests/test_sensors/test_motion.py::TestMotionSensor -v

# Run single test method
python -m pytest tests/test_sensors/test_temperature.py::TestTemperatureSensor::test_read_success -v

# Run with output capture (see print statements)
python -m pytest tests/test_sensors/test_temperature.py -v -s

# Stop on first failure
python -m pytest tests/test_sensors/ -x

# Run with coverage report
python -m pytest tests/test_sensors/ --cov=src.sensors --cov-report=html

# Run specific test by pattern
python -m pytest tests/test_sensors/ -k "temperature" -v
python -m pytest tests/test_sensors/ -k "motion and success" -v
```

---

## Documentation Files

- **[MD02_MODBUS_GUIDE.md](MD02_MODBUS_GUIDE.md)** - Complete Modbus protocol reference
- **[GPIO_PIN_ASSIGNMENTS.md](../docs/GPIO_PIN_ASSIGNMENTS.md)** - Pin configuration
- **[TEMPERATURE_SENSOR.md](../docs/TEMPERATURE_SENSOR.md)** - Temperature sensor guide
- **[PIR_MOTION_SENSOR.md](../docs/PIR_MOTION_SENSOR.md)** - Motion sensor guide
- **[SOUND_SENSOR.md](../docs/SOUND_SENSOR.md)** - Sound sensor guide
- **[VIBRATION_SENSOR.md](../docs/VIBRATION_SENSOR.md)** - Vibration sensor guide
- **[DOOR_SENSOR.md](../docs/DOOR_SENSOR.md)** - Door sensor guide

---

## Support

For detailed information:
1. Check individual sensor documentation in `docs/` folder
2. Review [MD02_MODBUS_GUIDE.md](MD02_MODBUS_GUIDE.md) for temperature/humidity sensor
3. Run `python script.py --help` for command-line options
4. Check test files for usage examples

---

**Last Updated**: December 13, 2025  
**Status**: All tests passing ✅

