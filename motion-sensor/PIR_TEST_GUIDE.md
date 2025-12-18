# PIR Motion Sensor - Comprehensive Test Suite

Complete test coverage for HC-SR501 PIR motion sensor with gpiozero library.

## Installation

### Requirements
```bash
pip install gpiozero
```

On Raspberry Pi, you also need:
```bash
pip install RPi.GPIO
```

### Install Both
```bash
pip install gpiozero RPi.GPIO --break-system-packages
```

## Quick Start

### Run All Tests (Default)
```bash
python pir_test.py
```

### Run Specific Test
```bash
python pir_test.py --test idle
python pir_test.py --test motion
python pir_test.py --test recovery
```

### Custom GPIO Pin
```bash
python pir_test.py --gpio 27
```

### Longer Timeouts
```bash
python pir_test.py --timeout 30
```

## Available Tests

### 1. Idle State Test
**Purpose**: Verify sensor doesn't trigger when nothing is moving  
**Duration**: 10 seconds (default)  
**Steps**:
1. Stand completely still
2. Don't move near sensor
3. Sensor should NOT detect any motion

**Expected**: ✅ PASS (no motion events)

```bash
python pir_test.py --test idle --timeout 15
```

### 2. Motion Detection Test
**Purpose**: Verify sensor detects movement  
**Duration**: 10 seconds (default)  
**Steps**:
1. Wait for prompt
2. Wave hand in front of sensor
3. Sensor should detect motion

**Expected**: ✅ PASS (motion detected)

```bash
python pir_test.py --test motion --timeout 20
```

### 3. Signal Recovery Test
**Purpose**: Verify sensor correctly identifies when motion stops  
**Duration**: 15 seconds (default)  
**Steps**:
1. Wave hand to trigger motion
2. Stand still to let signal recover
3. Sensor should detect both motion and idle

**Expected**: ✅ PASS (motion & recovery detected)

```bash
python pir_test.py --test recovery --timeout 30
```

### 4. Repeated Motion Test
**Purpose**: Verify sensor works reliably with multiple events  
**Duration**: 3 cycles × 10 seconds (default)  
**Steps**:
1. Cycle 1: Wave hand (motion phase) → Stand still (idle phase)
2. Cycle 2: Repeat
3. Cycle 3: Repeat
4. All cycles should be detected

**Expected**: ✅ PASS (all cycles detected)

```bash
python pir_test.py --test repeated --timeout 20
```

### 5. Sensitivity Test
**Purpose**: Verify sensor sensitivity  
**Duration**: 20 seconds (default)  
**Steps**:
1. Make small movements
2. Try different distances from sensor (1m-5m)
3. Sensor should detect subtle motion

**Expected**: ✅ PASS (detections recorded)

```bash
python pir_test.py --test sensitivity --timeout 30
```

### 6. Detection Range Test
**Purpose**: Verify sensor range  
**Duration**: 20 seconds (default)  
**Steps**:
1. Start close to sensor (1m)
2. Gradually move away (to 5m)
3. Wave hand at different distances
4. Sensor should detect at all distances

**Expected**: ✅ PASS (range detection works)

```bash
python pir_test.py --test range --timeout 30
```

### 7. False Positive Test
**Purpose**: Verify sensor doesn't trigger unnecessarily  
**Duration**: 30 seconds (default)  
**Steps**:
1. Don't move at all
2. Leave lights/fans on (if testing stability)
3. Sensor should NOT detect motion

**Expected**: ✅ PASS (no false positives)

```bash
python pir_test.py --test false_pos --timeout 45
```

## Complete Test Examples

### Run All Tests with Default Settings
```bash
python pir_test.py
```

**Output**:
```
======================================================================
HC-SR501 PIR MOTION SENSOR - COMPREHENSIVE TEST SUITE
======================================================================
[2025-12-13 16:45:30] GPIO Pin: 17
[2025-12-13 16:45:30] Test Mode: all
[2025-12-13 16:45:30] Timeout: 10s per test

======================================================================
TEST 1: IDLE STATE CHECK
======================================================================
[2025-12-13 16:45:30] ⏳ Waiting 10 seconds with NO motion...
[2025-12-13 16:45:30] 👉 Please stand still / don't move near sensor

[2025-12-13 16:45:40] ✅ TEST 1 PASSED - No motion detected
----------------------------------------------------------------------

======================================================================
TEST 2: MOTION DETECTION
======================================================================
[2025-12-13 16:45:40] ⏳ Waiting 10 seconds for motion detection...
[2025-12-13 16:45:40] 👉 Wave your hand in front of sensor NOW!

[2025-12-13 16:45:42] 🚨 MOTION DETECTED (#1)
[2025-12-13 16:45:43] ✓ Motion detected at 8s remaining
[2025-12-13 16:45:50] ✅ TEST 2 PASSED - Motion detected!
----------------------------------------------------------------------

...

======================================================================
TEST SUMMARY
======================================================================
Idle State                     ✅ PASS
Motion Detection               ✅ PASS
Signal Recovery                ✅ PASS
Repeated Motion                ✅ PASS
Sensitivity                    ✅ PASS
Detection Range                ✅ PASS
False Positive                 ✅ PASS
----------------------------------------------------------------------
Total Events: 15 motion, 7 idle
Results: 7/7 tests passed
🎉 ALL TESTS PASSED!
======================================================================
```

### Run Only Motion Detection (Extended Time)
```bash
python pir_test.py --test motion --timeout 30
```

### Run Sensitivity Check (GPIO27, 45 seconds)
```bash
python pir_test.py --gpio 27 --test sensitivity --timeout 45
```

### Run All Tests with Longer Timeouts
```bash
python pir_test.py --timeout 20
```

## Hardware Setup

### Wiring
```
HC-SR501 Sensor          Raspberry Pi 5
───────────────          ──────────────
VCC (Orange)      →      Pin 1 (3.3V)
GND (Black)       →      Pin 6 (GND)
OUT (Brown)       →      GPIO17 (Pin 11)
```

### Pin Assignment
| Connection | Pin | GPIO |
|-----------|-----|------|
| 3.3V | 1 | - |
| GND | 6 | - |
| Motion OUT | 11 | GPIO17 |

⚠️ **WARNING**: Do NOT connect to 5V! GPIO17 is 3.3V tolerant only.

## Sensor Parameters

| Parameter | Value |
|-----------|-------|
| Detection Range | ~3-7 meters |
| Response Time | 0.5-1 second |
| Idle Time | 2.5 seconds (adjustable on PCB) |
| Operating Voltage | 5V (input), 3.3V (output) |
| Output Logic | HIGH = motion, LOW = idle |
| Field of View | ~110 degrees |

## Adjustment Guide

### On-Board Potentiometers
The HC-SR501 has two adjustment screws on the PCB:

1. **Tx (Time Delay)**
   - Determines how long output stays HIGH after motion stops
   - Left (shorter): 2.5s
   - Right (longer): 300s
   - Good default: ~5s

2. **Sx (Sensitivity)**
   - Controls detection range
   - Left (less): ~3m
   - Right (more): ~7m
   - Good default: ~5m

**Note**: Adjust potentiometers with small screwdriver while powered on.

## Troubleshooting

### No Motion Detected
**Problem**: Test fails at "Motion Detection"  
**Solutions**:
1. Check wiring (GND, VCC, OUT)
2. Verify GPIO pin (use `--gpio 27` if different)
3. Increase sensitivity (Sx pot)
4. Move closer to sensor
5. Check if sensor needs warm-up time (wait 30-60 seconds after power)

### False Positives
**Problem**: Idle state test fails  
**Solutions**:
1. Reduce sensitivity (Sx pot - turn left)
2. Increase idle time (Tx pot - turn right)
3. Move sensor away from heat sources/lights
4. Avoid fans/AC vents pointing at sensor
5. Check for reflective surfaces causing issues

### GPIO Error
**Problem**: `gpiozero.exc.GPIOPinMissing`  
**Solutions**:
```bash
# Install RPi.GPIO
pip install RPi.GPIO --break-system-packages

# Run with sudo if permission denied
sudo python pir_test.py
```

### Timeout Errors
**Problem**: Tests always timeout  
**Solutions**:
1. Increase timeout: `--timeout 30`
2. Verify sensor is powered
3. Check 3.3V supply voltage
4. Test with simpler script first

## Signal Flow

```
HC-SR501
┌─────────────────────┐
│ PIR Detector        │
│ (Detects heat)      │
└──────────┬──────────┘
           │
           ├─ Motion detected?
           │
           ├─ YES → Set output HIGH
           │        Wait (Tx time)
           │        Set output LOW
           │
           ├─ NO → Output stays LOW
           │
           └─> Output → GPIO17 → Python
               ↓
        gpiozero.MotionSensor
               ↓
        Callbacks triggered
               ↓
        Test verification
```

## Statistics

The test suite tracks:
- Total motion detections
- Total idle periods
- Test pass/fail status
- Time between events
- Sensitivity metrics

Access via:
```python
tester = PIRTester(gpio_pin=17)
print(f"Motion count: {tester.motion_count}")
print(f"Idle count: {tester.idle_count}")
print(f"Results: {tester.test_results}")
```

## Advanced Usage

### Custom Test Script
```python
from pir_test import PIRTester

tester = PIRTester(gpio_pin=17)
tester.setup_callbacks()
tester.test_motion_detection(duration=20)
tester.print_summary()
```

### Continuous Monitoring
```python
from gpiozero import MotionSensor
from signal import pause

pir = MotionSensor(17)
pir.when_motion = lambda: print("Motion detected!")
pir.when_no_motion = lambda: print("Motion stopped")
pause()  # Keep running
```

## Support

For issues:
1. Check [GPIO_PIN_ASSIGNMENTS.md](GPIO_PIN_ASSIGNMENTS.md)
2. Review wiring diagram
3. Test with multiple GPIO pins
4. Check sensor documentation
5. Try basic script first

---

**Created**: December 13, 2025  
**Status**: ✅ Production Ready  
**Tests**: 7 comprehensive test cases

