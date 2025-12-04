# HC-SR501 PIR Motion Sensor Module

> **Passive Infrared Motion Detection for Raspberry Pi Smart Monitoring Kit**

---

## Table of Contents

1. [Hardware Overview](#hardware-overview)
2. [Pin Configuration](#pin-configuration)
3. [Wiring to Raspberry Pi](#wiring-to-raspberry-pi)
4. [Sensor Adjustments](#sensor-adjustments)
5. [Trigger Modes](#trigger-modes)
6. [Quick Start](#quick-start)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## Hardware Overview

![HC-SR501 PIR Sensor Board](images/hc_sr501_board.png)

The **HC-SR501** (HW-416-B) is a Passive Infrared (PIR) motion sensor module that detects movement by measuring changes in infrared radiation from warm objects (humans, animals).

### Specifications

| Parameter | Value |
|-----------|-------|
| Model | HC-SR501 (HW-416-B) |
| Operating Voltage | 4.5V - 20V DC |
| Quiescent Current | < 50 μA |
| Output Voltage | 3.3V (HIGH) / 0V (LOW) |
| Detection Range | 3 - 7 meters (adjustable via Sx potentiometer) |
| Detection Angle | 120° cone |
| Time Delay | 5 sec - 300 sec (adjustable via Tx potentiometer) |
| Blockade Time | 2.5 seconds (default) |
| Warmup Time | 30 - 60 seconds |
| Operating Temperature | -20°C to +80°C |
| PCB Size | 32mm × 24mm |

> 📍 **Purpose**: The HC-SR501 PIR sensor detects infrared radiation emitted by humans/animals moving within its detection range. It is commonly used to detect whether a human has moved in or out of the sensor's range.

---

## Pin Configuration

![HC-SR501 Pinout](images/hc_sr501_pinout.png)

### Bottom Pins (Left to Right) - With Polarity Markings

```
    ┌─────────────────────────────────────┐
    │          HC-SR501 (Bottom View)     │
    │                                     │
    │   ┌─────────────────────────────┐   │
    │   │                             │   │
    │   │    Zener Diode indicates    │   │
    │   │    positive (+) side        │   │
    │   │                             │   │
    │   └─────────────────────────────┘   │
    │                                     │
    │      [+]        [S]        [-]      │
    │       ●          ●          ●       │
    │      VCC        OUT        GND      │
    │    (Power)    (Signal)   (Ground)   │
    └─────────────────────────────────────┘
```

| Pin | Name | Polarity | Description |
|-----|------|----------|-------------|
| 1 | **VCC** | **[+]** | Power supply (⚠️ Use 3.3V for Raspberry Pi!) |
| 2 | **OUT** | **[S]** | Digital output signal (follows VCC voltage) |
| 3 | **GND** | **[-]** | Ground |

> ⚠️ **CRITICAL WARNING**: The PIR output voltage follows the VCC voltage! If VCC=5V, the OUT pin will output 5V which **WILL DAMAGE** the Raspberry Pi GPIO pins (max 3.3V tolerant). Always use 3.3V for VCC when connecting to Raspberry Pi!

> 📌 **Note**: The board has a Zener diode near the VCC pin indicating the positive (+) 3.3V side.

### Adjustment Potentiometers

![HC-SR501 Board Components](images/hc_sr501_board.png)

```
    ┌─────────────────────────────────────────────────────┐
    │              HC-SR501 Board Layout                  │
    ├─────────────────────────────────────────────────────┤
    │                                                     │
    │   ┌──────┐                      ┌──────┐            │
    │   │  Tx  │ Time Delay Adjust    │  Sx  │ Sensitivity│
    │   │ ◯─◯  │                      │ ◯─◯  │ Adjust     │
    │   └──────┘                      └──────┘            │
    │                                                     │
    │   Turn LEFT:  ~5 sec delay      Turn LEFT:  ~3m     │
    │   Turn RIGHT: ~300 sec delay    Turn RIGHT: ~7m     │
    │                                                     │
    │                   ┌──────────┐                      │
    │                   │ [H] [L]  │ Trigger Mode Jumper  │
    │                   └──────────┘                      │
    │                                                     │
    │            [+]         [S]         [-]              │
    │             ●           ●           ●               │
    │           Power      Output      Ground             │
    └─────────────────────────────────────────────────────┘
```

| Potentiometer | Label | Function | Adjustment |
|---------------|-------|----------|------------|
| Left | **Tx** | Time Delay | Turn RIGHT → Longer delay (5s → 300s) |
| Right | **Sx** | Sensitivity | Turn RIGHT → Distance Increases (~3m → ~7m) |
|       |        |             | Turn LEFT → Distance Decreases (~7m → ~3m) |

### Trigger Mode Jumper

| Position | Mode | Behavior |
|----------|------|----------|
| **L** | Single Trigger | Output goes LOW after delay, re-triggers on new motion |
| **H** | Repeatable Trigger | Output stays HIGH while motion continues |

---

## Wiring to Raspberry Pi 5 (4GB)

### Connection Table (Actual Wire Colors)

| HC-SR501 Pin | Wire Color | Raspberry Pi 5 Pin | BCM GPIO |
|--------------|------------|-------------------|----------|
| VCC (Power) | 🟠 Orange | Pin 1 (3.3V) ⚠️ | 3.3V Power |
| OUT (Signal) | 🟤 Brown | Pin 11 | GPIO17 |
| GND (Ground) | ⚫ Black | Pin 6 | GND |

> ⚠️ **WARNING**: VCC must be connected to 3.3V (Pin 1), **NOT 5V (Pin 2)**! The PIR output voltage equals VCC. A 5V output will permanently damage GPIO pins!

### Wiring Diagram (Raspberry Pi 5 4GB - Real Setup)

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║                    RASPBERRY PI 5 (4GB) PIR MOTION SENSOR WIRING                       ║
║                              Real Hardware Configuration                               ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║  ⚠️ CRITICAL: VCC must connect to 3.3V (Pin 1), NOT 5V! 5V DAMAGES GPIO!              ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                        ║
║   ┌─────────────────────────────────────┐                ┌─────────────────────────┐  ║
║   │        RASPBERRY PI 5 (4GB)          │                │    HC-SR501 (HW-416-B)  │  ║
║   │   ┌─────────────────────────────┐    │                │   ┌─────────────────┐   │  ║
║   │   │  █████████████████████████  │    │                │   │    ┌───────┐    │   │  ║
║   │   │  █   Raspberry Pi 5     █  │    │                │   │    │ Fresnel│   │   │  ║
║   │   │  █      4GB RAM         █  │    │                │   │    │  Lens  │    │   │  ║
║   │   │  █████████████████████████  │    │                │   │    └───────┘    │   │  ║
║   │   │                             │    │                │   │   PIR Sensor    │   │  ║
║   │   │   ┌─ GPIO Header ─────────┐ │    │                │   ├─────────────────┤   │  ║
║   │   │   │ (1)● 3.3V ⚠️   5V ●(2)│◄┼────┼──🟠 Orange ────┼───┤                 │   │  ║
║   │   │   │ (3)●           5V ●(4)│ │    │                │   │  ┌──┐   ┌──┐    │   │  ║
║   │   │   │ (5)●         GND ●(6) │◄┼────┼──⚫ Black ──────┼───┤  │Tx│   │Sx│    │   │  ║
║   │   │   │ (7)●              ●(8)│ │    │                │   │  └──┘   └──┘    │   │  ║
║   │   │   │ (9)●             ●(10)│ │    │                │   │  Time   Sens    │   │  ║
║   │   │   │(11)● GPIO17      ●(12)│◄┼────┼──🟤 Brown ─────┼───┤                 │   │  ║
║   │   │   │(13)●             ●(14)│ │    │                │   │    [H] [L]      │   │  ║
║   │   │   │(15)●             ●(16)│ │    │                │   │   Mode Jumper   │   │  ║
║   │   │   │(17)●             ●(18)│ │    │                │   ├─────────────────┤   │  ║
║   │   │   │(19)●             ●(20)│ │    │                │   │  ●    ●    ●    │   │  ║
║   │   │   └─────────────────────────┘ │    │                │   │ VCC  OUT  GND  │   │  ║
║   │   └─────────────────────────────┘    │                │   └──┬────┬────┬───┘   │  ║
║   │                                      │                │      │    │    │       │  ║
║   │   USB-C │ USB │ USB │ HDMI │ ETH    │                └──────┼────┼────┼───────┘  ║
║   └─────────────────────────────────────┘                       │    │    │          ║
║                                                                 │    │    │          ║
║     WIRE CONNECTIONS:                                           │    │    │          ║
║     ════════════════                                            │    │    │          ║
║                                                                 │    │    │          ║
║     🟠 Orange Wire (VCC/Power) ─────────────────────────────────┘    │    │          ║
║        Raspberry Pi Pin 1 (3.3V) ────────────► HC-SR501 VCC          │    │          ║
║        ⚠️ NOT Pin 2 (5V)! 5V output will damage GPIO!                │    │          ║
║                                                                      │    │          ║
║     🟤 Brown Wire (OUT/Signal) ──────────────────────────────────────┘    │          ║
║        Raspberry Pi Pin 11 (GPIO17) ─────────► HC-SR501 OUT               │          ║
║                                                                           │          ║
║     ⚫ Black Wire (GND/Ground) ───────────────────────────────────────────┘          ║
║        Raspberry Pi Pin 6 (GND) ─────────────► HC-SR501 GND                          ║
║                                                                                        ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║  ⚠️  CRITICAL WARNING - DO NOT USE 5V FOR VCC!                                       ║
║  • PIR output voltage = VCC voltage                                                   ║
║  • If VCC=5V → OUT=5V → This will DAMAGE Raspberry Pi GPIO (max 3.3V tolerant)       ║
║  • Always use 3.3V (Pin 1) for VCC to ensure safe 3.3V output signal                 ║
║  • Warmup: Sensor requires 30-60 seconds to stabilize after power-on                  ║
║  • Adjust Tx (time delay) and Sx (sensitivity) potentiometers as needed              ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝
```

### Raspberry Pi 5 GPIO Header Reference

```
                    Raspberry Pi 5 GPIO Header (40-Pin)
        ┌─────────────────────────────────────────────────────┐
        │  3.3V  (1) ● ◄─VCC ⚠️               ● (2)  5V       │  🟠 Orange Wire
        │ GPIO2  (3) ●                        ● (4)  5V       │
        │ GPIO3  (5) ●                        ● (6)  GND◄─GND │  ⚫ Black Wire
        │ GPIO4  (7) ●                        ● (8)  GPIO14   │
        │   GND  (9) ●                        ● (10) GPIO15   │
  OUT─► │ GPIO17(11) ●  ◄─────────────────────────────────────│  🟤 Brown Wire
        │ GPIO27(13) ●                        ● (14) GND      │
        │ GPIO22(15) ●                        ● (16) GPIO23   │
        │  3.3V (17) ●                        ● (18) GPIO24   │
        │ GPIO10(19) ●                        ● (20) GND      │
        │ GPIO9 (21) ●                        ● (22) GPIO25   │
        │ GPIO11(23) ●                        ● (24) GPIO8    │
        │   GND (25) ●                        ● (26) GPIO7    │
        │ GPIO0 (27) ●                        ● (28) GPIO1    │
        │ GPIO5 (29) ●                        ● (30) GND      │
        │ GPIO6 (31) ●                        ● (32) GPIO12   │
        │ GPIO13(33) ●                        ● (34) GND      │
        │ GPIO19(35) ●                        ● (36) GPIO16   │
        │ GPIO26(37) ●                        ● (38) GPIO20   │
        │   GND (39) ●                        ● (40) GPIO21   │
        └─────────────────────────────────────────────────────┘
```

---

## Sensor Adjustments

### Time Delay Adjustment (Tx Potentiometer)

The **left potentiometer** controls how long the output stays HIGH after motion is detected:

| Direction | Delay Time |
|-----------|------------|
| Fully Counter-Clockwise | ~5 seconds |
| Middle Position | ~2.5 minutes |
| Fully Clockwise | ~5 minutes (300 seconds) |

### Sensitivity Adjustment (Sx Potentiometer)

The **right potentiometer** controls the detection range:

| Direction | Detection Range |
|-----------|-----------------|
| Fully Counter-Clockwise | ~3 meters |
| Middle Position | ~5 meters |
| Fully Clockwise | ~7 meters |

---

## Trigger Modes

### Single Trigger Mode (L Position)

```
Motion:    ████░░░░░░░░░████░░░░░░
Output:    ────┐     ┌──────┐     ┌──
            HIGH│     │ HIGH │     │
                └─────┘      └─────┘
           <--Tx-->  <--Tx-->
```

- Output goes HIGH when motion detected
- After Tx delay, output goes LOW
- New motion during LOW state triggers again

### Repeatable Trigger Mode (H Position)

```
Motion:    ████░░████░░░░████░░░░░
Output:    ────────────────────┐
            HIGH               │
                               └───
           <------Extended Tx------>
```

- Output stays HIGH while motion continues
- Tx delay resets with each new motion
- Output goes LOW only after Tx delay with no motion

---

## Quick Start

### Installation

```bash
# Ensure RPi.GPIO is installed
pip install RPi.GPIO
```

### Basic Usage

```python
from src.sensors.motion import MotionSensor, MotionState

# Create sensor instance (GPIO17 = Pin 11)
sensor = MotionSensor(gpio_pin=17)

# Initialize GPIO
if sensor.initialize():
    print("Sensor ready! Waiting for warmup (30 seconds)...")

    # Simple polling
    while True:
        if sensor.is_motion_detected():
            print("🚨 MOTION DETECTED!")
        time.sleep(0.5)
```

### With Callback (Interrupt-Driven)

```python
from src.sensors.motion import MotionSensor, MotionEvent, MotionState

def on_motion(event: MotionEvent):
    if event.state == MotionState.MOTION_DETECTED:
        print(f"🚨 Motion at {event.timestamp}")
    else:
        print(f"✓ Motion ended (duration: {event.duration:.1f}s)")

# Create sensor with callback
sensor = MotionSensor(gpio_pin=17, callback=on_motion)
sensor.initialize()

# Start monitoring (uses GPIO interrupts)
sensor.start_monitoring(use_interrupt=True)

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sensor.cleanup()
```

---

## API Reference

### MotionSensor Class

```python
MotionSensor(
    gpio_pin: int = 17,           # BCM GPIO pin number
    trigger_mode: TriggerMode = TriggerMode.REPEATABLE,
    debounce_time_ms: int = 200,  # Debounce time in milliseconds
    callback: Callable = None,     # Motion event callback
    logger = None                  # Optional logger
)
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `initialize()` | Setup GPIO pin | `bool` |
| `cleanup()` | Release GPIO resources | `None` |
| `read()` | Get current motion state | `MotionState` |
| `is_motion_detected()` | Check if motion active | `bool` |
| `wait_for_motion(timeout)` | Block until motion | `bool` |
| `start_monitoring(use_interrupt)` | Start continuous detection | `None` |
| `stop_monitoring()` | Stop detection | `None` |
| `get_event_history(limit)` | Get recent events | `List[MotionEvent]` |
| `get_wiring_diagram()` | Get ASCII wiring diagram | `str` |

### MotionEvent Class

| Attribute | Type | Description |
|-----------|------|-------------|
| `state` | `MotionState` | MOTION_DETECTED or NO_MOTION |
| `timestamp` | `datetime` | When event occurred |
| `duration` | `float` | Duration of motion (seconds) |

---

## Troubleshooting

### Common Issues

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| No detection | Sensor in warmup | Wait 30-60 seconds after power-on |
| False triggers | Sensitivity too high | Turn Sx potentiometer counter-clockwise |
| Short detection | Time delay too low | Turn Tx potentiometer clockwise |
| Constant HIGH | Jumper in wrong position | Check H/L jumper setting |
| Erratic behavior | Interference | Keep away from heat sources, motors |

### Hardware Verification

```python
# Test script to verify wiring
from src.sensors.motion import MotionSensor

sensor = MotionSensor(gpio_pin=17)
if sensor.initialize():
    print(sensor.get_wiring_diagram())
    print("\nWave your hand in front of sensor...")

    if sensor.wait_for_motion(timeout=30):
        print("✓ Sensor working correctly!")
    else:
        print("✗ No motion detected. Check wiring.")

    sensor.cleanup()
```

### Important Notes

1. **Warmup Time**: The sensor requires 30-60 seconds to stabilize after power-on
2. **Detection Angle**: 120° cone - position sensor to cover desired area
3. **Power Supply**: ⚠️ Use 3.3V (Pin 1) for VCC - **NOT 5V!** (5V output damages GPIO)
4. **Output Logic**: HIGH = Motion detected, LOW = No motion

---

## Integration with Smart Monitoring Kit

The PIR sensor integrates with the monitoring system for:

- **Security Alerts**: Trigger camera recording on motion
- **Energy Saving**: Turn on lights/systems when presence detected
- **Activity Logging**: Track movement patterns
- **Fall Detection**: Supplement camera-based detection

```python
# Example: Integrate with camera and LINE notifications
from src.sensors.motion import MotionSensor
from src.line_api.messaging import LineMessaging
from src.rtsp.stream_handler import StreamHandler

def on_intrusion(event):
    if event.state == MotionState.MOTION_DETECTED:
        # Capture snapshot
        camera.capture_snapshot("intrusion.jpg")
        # Send alert
        line.send_message("🚨 Motion detected in monitored area!")
```

---

## Test Report

### Unit Test Results (12/12 PASSED)

```
[2025-12-04 12:22:17] ============================================
[2025-12-04 12:22:17] PIR MOTION SENSOR UNIT TESTS
[2025-12-04 12:22:17] ============================================
[2025-12-04 12:22:17] ✓ Imports successful

[2025-12-04 12:22:17] TEST 1: MotionState enum values
[2025-12-04 12:22:17] ✓ PASSED - MotionState enum values correct

[2025-12-04 12:22:17] TEST 2: TriggerMode enum values
[2025-12-04 12:22:17] ✓ PASSED - TriggerMode enum values correct

[2025-12-04 12:22:17] TEST 3: MotionEvent dataclass creation
[2025-12-04 12:22:17] ✓ PASSED - MotionEvent created correctly

[2025-12-04 12:22:17] TEST 4: MotionEvent string format
[2025-12-04 12:22:17] ✓ PASSED - MotionEvent str() = '[2024-12-04 10:30:45] MOTION DETECTED'

[2025-12-04 12:22:17] TEST 5: PIRConfig defaults
[2025-12-04 12:22:17] ✓ PASSED - PIRConfig defaults correct

[2025-12-04 12:22:17] TEST 6: PIRConfig custom values
[2025-12-04 12:22:17] ✓ PASSED - PIRConfig custom values correct

[2025-12-04 12:22:17] TEST 7: MotionSensor initialization
[2025-12-04 12:22:17] ✓ PASSED - MotionSensor created with GPIO=17

[2025-12-04 12:22:17] TEST 8: MotionSensor custom GPIO
[2025-12-04 12:22:17] ✓ PASSED - Custom sensor GPIO=27

[2025-12-04 12:22:17] TEST 9: Wiring diagram content
[2025-12-04 12:22:17] ✓ PASSED - Wiring diagram contains all required info

[2025-12-04 12:22:17] TEST 10: Initialize without RPi.GPIO library
[2025-12-04 12:22:17] ✓ PASSED - Returns False when RPi.GPIO not available

[2025-12-04 12:22:17] TEST 11: MotionEvent with duration
[2025-12-04 12:22:17] ✓ PASSED - Duration shown: '[2024-12-04 10:30:45] MOTION DETECTED (duration: 5.5s)'

[2025-12-04 12:22:17] TEST 12: NO_MOTION event string
[2025-12-04 12:22:17] ✓ PASSED - No motion state: '[2024-12-04 10:30:45] No Motion'

[2025-12-04 12:22:17] ============================================
[2025-12-04 12:22:17] TEST SUMMARY: 12/12 PASSED
[2025-12-04 12:22:17] ✓ ALL TESTS PASSED SUCCESSFULLY!
[2025-12-04 12:22:17] ============================================
```

### Test Script Location

```
tests/test_sensors/test_motion.py
```

### Hardware Diagnostic Scenarios

| Symptom | Possible Root Cause | Solution |
|---------|-------------------|----------|
| `initialize()` returns False | RPi.GPIO not installed | `pip install RPi.GPIO` |
| `initialize()` returns False | Not running on Raspberry Pi | Use actual Raspberry Pi hardware |
| Always reads LOW | Wrong GPIO pin or bad wiring | Check GPIO17 (Pin 11) connection |
| Always reads LOW | Sensor not powered | Check 3.3V (Pin 1) connection |
| Always reads HIGH | GND not connected | Check GND (Pin 6) connection |
| No detection at all | Sensor still in warmup | Wait 30-60 seconds after power-on |
| Short detection range | Sensitivity too low | Adjust Sx potentiometer clockwise |
| False triggers | Sensitivity too high | Adjust Sx potentiometer counter-clockwise |

---

## Save These Images

Please save the sensor images to:

```
docs/images/hc_sr501_board.png   (Board with labeled components)
docs/images/hc_sr501_pinout.png  (Pin diagram)
```

