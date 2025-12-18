# LM393 Sound Sensor - Comprehensive Test Suite

## Overview

Complete testing framework for the LM393 sound sensor with 7 test cases ranging from basic to advanced scenarios.

**Status**: ✅ Production Ready
**File**: `sound_test.py` (413 lines)
**Library**: gpiozero (event-driven GPIO)
**GPIO Pin**: GPIO22 (default, configurable)

---

## Features

### Core Capabilities
- ✓ **7 Comprehensive Test Cases** (Basic → Advanced)
- ✓ **Real-time Event Logging** with timestamps
- ✓ **Sound Duration Tracking** with measurements
- ✓ **Statistics Tracking** (sound count, silence count)
- ✓ **Test Pass/Fail Verification** with detailed results
- ✓ **Configurable Parameters** (GPIO pin, timeout, test selection)
- ✓ **Graceful Interrupt Handling** (Ctrl+C)
- ✓ **GPIO Debounce** filtering (100ms)
- ✓ **GPIO Cleanup** on exit

### User Interface
- Color-coded output (✅ PASS, ❌ FAIL, 🔊 SOUND, ✓ SILENCE)
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
python sound_test.py

# Run specific test
python sound_test.py --test sound

# Custom GPIO pin
python sound_test.py --gpio 22

# Extended timeout
python sound_test.py --timeout 30

# Combine options
python sound_test.py --gpio 22 --test sensitivity --timeout 45
```

---

## Test Cases (7 Total)

### Test 1: Silence Check

**Purpose**: Verify sensor doesn't trigger without sound

**Duration**: 10 seconds (default)

**Command**:
```bash
python sound_test.py --test silence
```

**Steps**:
1. Run test
2. Keep environment completely quiet (no talking, noise)
3. Observe output for 10 seconds

**Expected Result**: ✅ PASS (no sounds detected)

---

### Test 2: Sound Detection

**Purpose**: Verify sensor detects sound

**Duration**: 10 seconds (default)

**Command**:
```bash
python sound_test.py --test sound
```

**Steps**:
1. Run test
2. Wait for prompt
3. Make sounds: clap, snap, or speak
4. Perform multiple sounds during test period

**Expected Result**: ✅ PASS (sounds detected)

---

### Test 3: Signal Recovery

**Purpose**: Verify sound→silence transition works

**Duration**: 15 seconds (default)

**Command**:
```bash
python sound_test.py --test recovery
```

**Steps**:
1. Run test
2. **Phase 1**: Make a sound (clap, snap, or speak)
3. **Phase 2**: Go silent
4. Repeat if needed

**Expected Result**: ✅ PASS (both events detected)

---

### Test 4: Repeated Sound

**Purpose**: Verify reliable multi-cycle detection (3 cycles)

**Duration**: ~10 seconds total

**Command**:
```bash
python sound_test.py --test repeated
```

**Steps**:
1. Run test
2. Repeat pattern 3 times:
   - Make a sound
   - Go silent
   - Make a sound
   - Go silent

**Expected Result**: ✅ PASS (3+ sound events detected)

---

### Test 5: Sensitivity Test

**Purpose**: Check sensor sensitivity level with varying sound

**Duration**: 20 seconds (default)

**Command**:
```bash
python sound_test.py --test sensitivity
```

**Steps**:
1. Run test
2. **Phase 1**: Soft sounds (whisper or gentle tap)
3. **Phase 2**: Normal sounds (regular voice or snap)
4. **Phase 3**: Loud sounds (shouting or clapping)

**Expected Result**: ✅ PASS (multiple sounds detected: 5+)

---

### Test 6: Intensity Test

**Purpose**: Test sensor response at different sound intensities

**Duration**: 20 seconds (default)

**Command**:
```bash
python sound_test.py --test intensity
```

**Steps**:
1. Run test
2. Vary sound intensity:
   - Soft (whisper, gentle tap)
   - Medium (normal voice, snap)
   - Loud (shout, loud clap)

**Expected Result**: ✅ PASS (multiple events: 5+)

---

### Test 7: Sustained Noise Test

**Purpose**: Detect continuous/sustained sound

**Duration**: 20 seconds (default)

**Command**:
```bash
python sound_test.py --test sustained
```

**Steps**:
1. Run test
2. Make continuous sound:
   - Continuous whistle/humming
   - Running water/fan
   - Sustained speech

**Expected Result**: ✅ PASS (sustained sounds: 2+)

---

## Hardware Setup

### LM393 Sound Sensor Wiring

```
Sensor Pin        Wire Color        Raspberry Pi
─────────────────────────────────────────────────
VCC               Red               Pin 1 (3.3V)
GND               Black             Pin 6 (GND)
OUT (DO)          Yellow            Pin 15 (GPIO22)
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
  --gpio GPIO           GPIO pin number (default: 22)
  --test TEST           Which test to run:
                        - all (default): Run all 7 tests
                        - silence: Silence check only
                        - sound: Sound detection only
                        - recovery: Signal recovery only
                        - repeated: Repeated sound cycles
                        - sensitivity: Sensitivity check
                        - intensity: Intensity response
                        - sustained: Sustained noise test
  --timeout TIMEOUT     Duration per test in seconds (default: 10)
```

---

## Example Commands

```bash
# Run all tests (recommended first time)
python sound_test.py

# Test only sound detection
python sound_test.py --test sound

# Test sensitivity with longer duration
python sound_test.py --test sensitivity --timeout 45

# Use different GPIO pin
python sound_test.py --gpio 22

# Extended run: 60 second timeout per test
python sound_test.py --timeout 60

# Combine multiple options
python sound_test.py --gpio 22 --test repeated --timeout 30

# Run silence check only (verify no false positives)
python sound_test.py --test silence --timeout 30

# Run sustained noise test with extended time
python sound_test.py --test sustained --timeout 60
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
- Verify GPIO pin number: `python sound_test.py --gpio 22`
- Try running with sudo: `sudo python sound_test.py`

### Error: "Permission denied"

**Fix**:
```bash
sudo python sound_test.py
```

### Test: "No sounds detected" (fails when should pass)

**Fix**:
- Check sensor wiring (especially OUT pin to GPIO22)
- Verify GPIO22 is available (not in use)
- Increase sound volume (clap louder)
- Increase timeout: `--timeout 30`
- Check sensor power (indicator LED should be on)
- Adjust sensor potentiometer (sensitivity dial)

### Test: "False positives in Silence Check test"

**Fix**:
- Move sensor away from noise sources
- Place on stable surface (avoid vibration)
- Reduce sensitivity (turn potentiometer left)
- Increase test duration: `--timeout 30`

---

## Sensor Specifications

### LM393 Sound Sensor

| Specification | Value |
|---------------|-------|
| Operating Voltage | 3.3V - 5V |
| Output Type | Digital (HIGH when sound, LOW when silent) |
| Sensitivity | Adjustable via on-board potentiometer |
| Response Time | ~50-100ms |
| Current Consumption | ~5mA |
| Detection Threshold | Adjustable |
| Dimensions | ~18 x 20 x 10mm |
| Pin Count | 3 (VCC, GND, OUT) |

### GPIO22 Configuration (gpiozero)

| Parameter | Setting |
|-----------|---------|
| Pin Mode | INPUT (Button) |
| Pull Resistor | Pull-up (internal) |
| Debounce Time | 100ms |
| Edge Trigger | Both (on sound and silence) |
| Logic Level | HIGH = Sound, LOW = Silence |

---

## Advanced Usage

### Python API

```python
from sound_test import SoundTester

# Create tester instance
tester = SoundTester(gpio_pin=22)

# Setup callbacks
tester.setup_callbacks()

# Run specific test
tester.test_sound_detection(duration=20)

# Print summary
tester.print_summary()

# Cleanup
tester.cleanup()
```

### Continuous Monitoring (without tests)

```python
from gpiozero import Button

sensor = Button(22, pull_up=True)

sensor.when_pressed = lambda: print("Sound!")
sensor.when_released = lambda: print("Silence")

# Keep running
from signal import pause
pause()
```

---

## Statistics Tracked

### Per-Test
- Test name and pass/fail status
- Sound detection count
- Silence period count
- Event timestamps
- Sound durations

### Summary Report
- Total sound events
- Total silence periods
- Number of passed tests
- Number of failed tests
- Overall success rate

---

## Support & Documentation

**Files in this directory**:
- `sound_test.py` - Main test script (413 lines)
- `SOUND_TEST_GUIDE.md` - This documentation
- `../README.md` - Master sensor guide
- `../GPIO_PIN_ASSIGNMENTS.md` - GPIO pinout reference

**For additional help**:
1. Review SOUND_TEST_GUIDE.md (this file)
2. Run: `python sound_test.py --help`
3. Check GPIO pin assignments
4. Review sensor specifications above

---

**Status**: ✅ PRODUCTION READY

**Created**: 2025-12-13  
**Last Updated**: 2025-12-13

Ready to test! Use `python sound_test.py` to get started.
