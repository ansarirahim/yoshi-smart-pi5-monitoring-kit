# 801S Vibration Sensor - Comprehensive Test Suite

## Overview

Complete testing framework for the 801S vibration sensor with 7 test cases ranging from basic to advanced scenarios.

**Status**: ✅ Production Ready
**File**: `vibration_test.py` (502 lines)
**Library**: gpiozero (event-driven GPIO)
**GPIO Pin**: GPIO27 (default, configurable)

---

## Features

### Core Capabilities
- ✓ **7 Comprehensive Test Cases** (Basic → Advanced)
- ✓ **Real-time Event Logging** with timestamps
- ✓ **Vibration Duration Tracking** with measurements
- ✓ **Statistics Tracking** (vibration count, idle count)
- ✓ **Test Pass/Fail Verification** with detailed results
- ✓ **Configurable Parameters** (GPIO pin, timeout, test selection)
- ✓ **Graceful Interrupt Handling** (Ctrl+C)
- ✓ **GPIO Cleanup** on exit

### User Interface
- Color-coded output (✅ PASS, ❌ FAIL, 🚨 VIBRATION, ✓ IDLE)
- Progress indicators and countdown
- User prompts for each test phase
- Detailed test explanations
- Command-line argument parsing
- Help system with examples

---

## Quick Start

### Installation

```bash
# Basic (gpiozero only)
pip install gpiozero

# Raspberry Pi (complete)
pip install gpiozero RPi.GPIO --break-system-packages

# Verify
python -c "from gpiozero import Button; print('OK')"
```

### Run Tests

```bash
# Run all tests (recommended)
python vibration_test.py

# Run specific test
python vibration_test.py --test vibration

# Custom GPIO pin
python vibration_test.py --gpio 23

# Extended timeout
python vibration_test.py --timeout 30

# Combine options
python vibration_test.py --gpio 27 --test sensitivity --timeout 45
```

---

## Test Cases (7 Total)

### Test 1: Idle State Check

**Purpose**: Verify sensor doesn't trigger without vibration

**Duration**: 10 seconds (default)

**Command**:
```bash
python vibration_test.py --test idle
```

**Steps**:
1. Run test
2. Keep sensor completely still (no movement)
3. Observe output for 10 seconds

**Expected Result**: ✅ PASS (no vibrations detected)

**Example Output**:
```
======================================================================
TEST 1: IDLE STATE CHECK
======================================================================
[2025-12-13 17:10:30] ⏳ Waiting 10 seconds with NO vibration...
👉 Keep sensor completely still (no movement or vibration)

[2025-12-13 17:10:40] ✅ PASS - No vibrations detected
```

---

### Test 2: Vibration Detection

**Purpose**: Verify sensor detects vibration

**Duration**: 10 seconds (default)

**Command**:
```bash
python vibration_test.py --test vibration
```

**Steps**:
1. Run test
2. Wait for prompt
3. Tap or vibrate the sensor surface
4. Perform multiple vibrations during the test period

**Expected Result**: ✅ PASS (vibrations detected)

**Example Output**:
```
======================================================================
TEST 2: VIBRATION DETECTION
======================================================================
[2025-12-13 17:10:40] ⏳ Waiting 10 seconds for vibration...
👉 Tap or vibrate the sensor surface when ready!

[2025-12-13 17:10:42] 🚨 VIBRATION DETECTED (#1)
[2025-12-13 17:10:43] ✓ Vibration ended (idle #1, duration: 1.05s)
[2025-12-13 17:10:44] 🚨 VIBRATION DETECTED (#2)
[2025-12-13 17:10:45] ✓ Vibration ended (idle #2, duration: 0.92s)
[2025-12-13 17:10:50] ✅ PASS - Vibrations detected: 3
```

---

### Test 3: Signal Recovery

**Purpose**: Verify vibration→idle transition works correctly

**Duration**: 15 seconds (default)

**Command**:
```bash
python vibration_test.py --test recovery
```

**Steps**:
1. Run test
2. **Phase 1**: Tap/vibrate the sensor
3. **Phase 2**: Stop and keep it still
4. Repeat if needed

**Expected Result**: ✅ PASS (both vibration and idle detected)

**Example Output**:
```
======================================================================
TEST 3: SIGNAL RECOVERY
======================================================================
[2025-12-13 17:10:55] ⏳ Testing vibration→idle transition (15s)...
👉 Phase 1: Tap/vibrate the sensor
👉 Phase 2: Stop and keep it still

[2025-12-13 17:10:57] 🚨 VIBRATION DETECTED (#1)
[2025-12-13 17:10:59] ✓ Vibration ended (idle #1, duration: 2.10s)
[2025-12-13 17:11:10] ✅ PASS - Vibrations: 1, Idle periods: 1
```

---

### Test 4: Repeated Vibration

**Purpose**: Verify reliable multi-cycle detection (3 cycles)

**Duration**: ~10 seconds total (configurable per cycle)

**Command**:
```bash
python vibration_test.py --test repeated
```

**Steps**:
1. Run test
2. Repeat pattern 3 times:
   - Vibrate the sensor
   - Stop and keep still
   - Vibrate again
   - Stop again

**Expected Result**: ✅ PASS (3+ vibration events detected)

**Example Output**:
```
======================================================================
TEST 4: REPEATED VIBRATION
======================================================================
[2025-12-13 17:11:10] ⏳ Testing 3 vibration cycles (10s each)...
👉 Repeat: Vibrate → Stop → Vibrate → Stop (etc.)

[2025-12-13 17:11:12] 🚨 VIBRATION DETECTED (#1)
[2025-12-13 17:11:13] ✓ Vibration ended (idle #1, duration: 1.20s)
[2025-12-13 17:11:15] 🚨 VIBRATION DETECTED (#2)
[2025-12-13 17:11:16] ✓ Vibration ended (idle #2, duration: 0.98s)
[2025-12-13 17:11:18] 🚨 VIBRATION DETECTED (#3)
[2025-12-13 17:11:19] ✓ Vibration ended (idle #3, duration: 1.05s)
[2025-12-13 17:11:40] ✅ PASS - Detected 3 vibrations (expected ~3)
```

---

### Test 5: Sensitivity Test

**Purpose**: Check sensor sensitivity level with varying vibration

**Duration**: 20 seconds (default)

**Command**:
```bash
python vibration_test.py --test sensitivity
```

**Steps**:
1. Run test
2. **Phase 1**: Gentle tapping (light vibration)
3. **Phase 2**: Moderate tapping (medium vibration)
4. **Phase 3**: Strong tapping (heavy vibration)

**Expected Result**: ✅ PASS (multiple vibrations detected: 5+)

**Example Output**:
```
======================================================================
TEST 5: SENSITIVITY TEST
======================================================================
[2025-12-13 17:11:40] ⏳ Testing sensitivity (20s)...
👉 Phase 1: Gentle tapping (light vibration)
👉 Phase 2: Moderate tapping (medium vibration)
👉 Phase 3: Strong tapping (heavy vibration)

[2025-12-13 17:11:42] 🚨 VIBRATION DETECTED (#1)
[2025-12-13 17:11:43] ✓ Vibration ended (idle #1, duration: 0.85s)
[2025-12-13 17:11:44] 🚨 VIBRATION DETECTED (#2)
[2025-12-13 17:11:44] ✓ Vibration ended (idle #2, duration: 0.62s)
[2025-12-13 17:11:45] 🚨 VIBRATION DETECTED (#3)
[2025-12-13 17:11:46] ✓ Vibration ended (idle #3, duration: 0.98s)
[2025-12-13 17:12:00] ✅ PASS - Vibrations detected: 8
```

---

### Test 6: Intensity Test

**Purpose**: Test sensor response at different vibration intensities

**Duration**: 20 seconds (default)

**Command**:
```bash
python vibration_test.py --test intensity
```

**Steps**:
1. Run test
2. Vary vibration intensity:
   - Light touches (soft)
   - Medium taps (normal)
   - Strong vibrations (hard)

**Expected Result**: ✅ PASS (multiple events: 5+)

**Example Output**:
```
======================================================================
TEST 6: INTENSITY TEST
======================================================================
[2025-12-13 17:12:00] ⏳ Testing intensity response (20s)...
👉 Vary vibration intensity:
   - Light touches
   - Medium taps
   - Strong vibrations

[2025-12-13 17:12:02] 🚨 VIBRATION DETECTED (#1)
[2025-12-13 17:12:02] ✓ Vibration ended (idle #1, duration: 0.58s)
[2025-12-13 17:12:04] 🚨 VIBRATION DETECTED (#2)
[2025-12-13 17:12:05] ✓ Vibration ended (idle #2, duration: 0.75s)
[2025-12-13 17:12:20] ✅ PASS - Intensity variations detected: 6
```

---

### Test 7: Duration Test

**Purpose**: Measure vibration duration accuracy

**Duration**: 20 seconds (default)

**Command**:
```bash
python vibration_test.py --test duration
```

**Steps**:
1. Run test
2. Perform vibrations of varying lengths:
   - **Short**: 1-2 seconds continuous vibration
   - **Medium**: 3-5 seconds continuous vibration
   - **Long**: 5+ seconds continuous vibration

**Expected Result**: ✅ PASS (duration measurements recorded: 2+)

**Example Output**:
```
======================================================================
TEST 7: DURATION TEST
======================================================================
[2025-12-13 17:12:20] ⏳ Measuring vibration duration (20s)...
👉 Perform vibrations of varying lengths:
   - Short vibration (1-2 seconds)
   - Medium vibration (3-5 seconds)
   - Long vibration (5+ seconds)

[2025-12-13 17:12:22] 🚨 VIBRATION DETECTED (#1)
[2025-12-13 17:12:23] ✓ Vibration ended (idle #1, duration: 1.82s)
[2025-12-13 17:12:25] 🚨 VIBRATION DETECTED (#2)
[2025-12-13 17:12:30] ✓ Vibration ended (idle #2, duration: 5.18s)
[2025-12-13 17:12:40] ✅ PASS - Duration measurements: 2 (last duration: 5.18s)
```

---

## Example: Run All Tests

```bash
python vibration_test.py
```

**Expected Output**:
```
======================================================================
801S VIBRATION SENSOR - COMPREHENSIVE TEST SUITE
======================================================================
[2025-12-13 17:10:30] GPIO Pin: 27
[2025-12-13 17:10:30] Test Mode: all
[2025-12-13 17:10:30] Timeout: 10s per test

======================================================================
TEST 1: IDLE STATE CHECK
======================================================================
[2025-12-13 17:10:30] ⏳ Waiting 10 seconds with NO vibration...
👉 Keep sensor completely still (no movement or vibration)

[2025-12-13 17:10:40] ✅ PASS - No vibrations detected
----------------------------------------------------------------------

[... Tests 2-7 ...]

======================================================================
TEST SUMMARY
======================================================================
Idle State                     ✅ PASS
Vibration Detection            ✅ PASS
Signal Recovery                ✅ PASS
Repeated Vibration             ✅ PASS
Sensitivity                    ✅ PASS
Intensity                      ✅ PASS
Duration                       ✅ PASS
----------------------------------------------------------------------
Total Vibrations: 23
Total Idle Periods: 12
Results: 7/7 tests passed
🎉 ALL TESTS PASSED!
======================================================================
```

---

## Hardware Setup

### 801S Vibration Sensor Wiring

```
Sensor Pin        Wire Color        Raspberry Pi
─────────────────────────────────────────────────
1 (VCC)          Red               Pin 1 (3.3V)
2 (GND)          Black             Pin 6 (GND)
3 (OUT)          Brown             Pin 13 (GPIO27)
```

### GPIO Pin Reference

```
        Raspberry Pi 5 GPIO Header
        ===========================

     3.3V (1) [*] [*] (2) 5V
I2C SDA GPIO2 (3) [ ] [ ] (4) 5V
I2C SCL GPIO3 (5) [ ] [*] (6) GND
         GPIO4 (7) [ ] [ ] (8) GPIO14 TX
           GND (9) [ ] [ ] (10) GPIO15 RX
 [PIR] --> GPIO17 (11) [*] [ ] (12) GPIO18
[VIBE] --> GPIO27 (13) [*] [ ] (14) GND
[SOUND] --> GPIO22 (15) [*] [*] (16) GPIO23 <-- [DOOR]
        3.3V (17) [ ] [ ] (18) GPIO24
```

⚠️ **IMPORTANT**: Use **3.3V** for VCC, NOT 5V! Will damage GPIO pins.

---

## Command-Line Options

```
Options:
  -h, --help            Show this help message
  --gpio GPIO           GPIO pin number (default: 27)
  --test TEST           Which test to run:
                        - all (default): Run all 7 tests
                        - idle: Idle state only
                        - vibration: Vibration detection only
                        - recovery: Signal recovery only
                        - repeated: Repeated vibration cycles
                        - sensitivity: Sensitivity check
                        - intensity: Intensity response
                        - duration: Duration measurement
  --timeout TIMEOUT     Duration per test in seconds (default: 10)
```

---

## Example Commands

```bash
# Run all tests (recommended first time)
python vibration_test.py

# Test only vibration detection
python vibration_test.py --test vibration

# Test sensitivity with longer duration
python vibration_test.py --test sensitivity --timeout 45

# Use different GPIO pin
python vibration_test.py --gpio 23

# Extended run: 60 second timeout per test
python vibration_test.py --timeout 60

# Combine multiple options
python vibration_test.py --gpio 27 --test repeated --timeout 30

# Run idle state test only (verify no false positives)
python vibration_test.py --test idle --timeout 30

# Run duration test with extended time
python vibration_test.py --test duration --timeout 60
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'gpiozero'"

**Fix**:
```bash
pip install gpiozero --break-system-packages
```

### Error: "GPIOPinMissing: GPIO pin not found"

**Fix**:
- Check wiring (VCC, GND, OUT connections)
- Verify GPIO pin number: `python vibration_test.py --gpio 27`
- Try running with sudo: `sudo python vibration_test.py`

### Error: "Permission denied"

**Fix**:
```bash
sudo python vibration_test.py
```

### Test: "No vibrations detected" (fails when should pass)

**Fix**:
- Check sensor wiring (especially OUT pin)
- Verify GPIO27 is available (not in use)
- Increase vibration force (tap harder)
- Increase timeout: `--timeout 30`
- Check sensor power (indicator LED should be on)

### Test: "False positives in Idle State test"

**Fix**:
- Move sensor away from vibration sources
- Place on stable surface (table)
- Avoid nearby machinery/foot traffic
- Increase test duration: `--timeout 30`

### Sensor Not Responding at All

**Checklist**:
- [ ] Power connected (VCC 3.3V, GND)
- [ ] Output pin connected to GPIO27 (or specified GPIO)
- [ ] GPIO pin number correct in command
- [ ] Sensor powered on (LED indicator active)
- [ ] No GPIO conflicts with other sensors

---

## Sensor Specifications

### 801S Vibration Sensor

| Specification | Value |
|---------------|-------|
| Operating Voltage | 3.3V - 5V |
| Output Type | Digital (HIGH when vibration, LOW when idle) |
| Sensitivity | Adjustable via on-board potentiometer |
| Response Time | ~50-100ms (debounce: 50ms) |
| Current Consumption | ~5mA |
| Detection Threshold | Adjustable |
| Dimensions | ~18 x 20 x 10mm |
| Pin Count | 3 (VCC, GND, OUT) |

### GPIO27 Configuration (gpiozero)

| Parameter | Setting |
|-----------|---------|
| Pin Mode | INPUT (Button) |
| Pull Resistor | Pull-up (internal) |
| Debounce Time | 50ms |
| Edge Trigger | Both (on press and release) |
| Logic Level | HIGH = Vibration, LOW = Idle |

---

## Advanced Usage

### Python API

```python
from vibration_test import VibrationTester

# Create tester instance
tester = VibrationTester(gpio_pin=27)

# Setup callbacks
tester.setup_callbacks()

# Run specific test
tester.test_vibration_detection(duration=20)

# Print summary
tester.print_summary()

# Cleanup
tester.cleanup()
```

### Continuous Monitoring (without tests)

```python
from gpiozero import Button

sensor = Button(27, pull_up=True)

sensor.when_pressed = lambda: print("Vibration!")
sensor.when_released = lambda: print("Idle")

# Keep running
from signal import pause
pause()
```

---

## Statistics Tracked

### Per-Test
- Test name and pass/fail status
- Vibration detection count
- Idle period count
- Event timestamps
- Vibration durations

### Summary Report
- Total vibration events
- Total idle periods
- Number of passed tests
- Number of failed tests
- Overall success rate

---

## Support & Documentation

**Files in this directory**:
- `vibration_test.py` - Main test script (502 lines)
- `VIBRATION_TEST_GUIDE.md` - This documentation
- `../README.md` - Master sensor guide
- `../GPIO_PIN_ASSIGNMENTS.md` - GPIO pinout reference

**For additional help**:
1. Review VIBRATION_TEST_GUIDE.md (this file)
2. Run: `python vibration_test.py --help`
3. Check GPIO pin assignments
4. Review sensor specifications above

---

**Status**: ✅ PRODUCTION READY

**Created**: 2025-12-13  
**Last Updated**: 2025-12-13

Ready to test! Use `python vibration_test.py` to get started.
