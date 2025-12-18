# 801S Vibration Shock Sensor Module

## Overview

The 801S Vibration Shock Sensor is a high-sensitivity vibration detection module with digital output. It detects vibrations using a gold-plated spring sensor and outputs a digital HIGH signal via LM393 comparator when vibration exceeds the adjustable threshold.

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Model | 801S Vibration Shock Sensor Module |
| Operating Voltage | 3.3V - 5V DC (Use 3.3V for Raspberry Pi!) |
| Output Type | Digital (TTL level) |
| Output Signal | HIGH when vibration detected |
| Comparator IC | LM393 |
| Durability | 60 million shocks (gold-plated contacts) |
| Detection | Omnidirectional (no specific direction) |
| Sensitivity | Adjustable via onboard potentiometer |

> Purpose: Detects shock, vibration, or impact in any direction. Commonly used for security systems, impact detection, and motion-triggered applications.

---

## Pin Configuration

```
    +-----------------------------------------------+
    |          801S Vibration Sensor Module         |
    |                                               |
    |   +-------------+    +---------+              |
    |   |   [Sens.]   |    | [801S]  |              |
    |   | Potentiometer|    | Gold    |              |
    |   +-------------+    | Sensor  |              |
    |                      +---------+              |
    |                                               |
    |   [LM393 Comparator IC]                       |
    |                                               |
    |      GND       D0       VCC                   |
    |       o         o         o                   |
    |      [-]       [S]       [+]                  |
    +-----------------------------------------------+
```

| Pin | Name | Polarity | Description |
|-----|------|----------|-------------|
| 1 | **GND** | **[-]** | Ground |
| 2 | **D0** | **[S]** | Digital output (HIGH on vibration) |
| 3 | **VCC** | **[+]** | Power supply (Use 3.3V!) |

---

## Wiring to Raspberry Pi 5 (4GB)

### Connection Table

| 801S Pin | Polarity | Wire Color | RPi Pin | RPi Function |
|----------|----------|------------|---------|--------------|
| VCC | [+] | Orange | Pin 1 | 3.3V Power |
| D0 | [S] | Gray | Pin 13 | GPIO27 |
| GND | [-] | Black | Pin 6 | Ground |

> **Note**: GPIO17 is reserved for the PIR Motion Sensor. The vibration sensor uses GPIO27 to avoid conflicts.

### Wiring Diagram

```
+=====================================================================+
|       801S Vibration Sensor Wiring - Raspberry Pi 5 (4GB)           |
+=====================================================================+
|                                                                     |
|   801S Vibration Module             Raspberry Pi 5                  |
|   +-------------------+            +----------------------+         |
|   |  [Potentiometer]  |            | 3.3V (1) o o (2) 5V  |<-Orange |
|   |   Sensitivity     |            | GPIO2(3) o o (4) 5V  |  [+]    |
|   |     Adjust        |            | GPIO3(5) o o (6) GND |<-Black  |
|   |                   |            | GPIO4(7) o o (8)     |  [-]    |
|   | [801S] [LM393]    |            |   GND(9) o o (10)    |         |
|   |  Gold   Comp.     |            | GPIO17(11)o o (12)   | [PIR]   |
|   |                   |            | GPIO27(13)o o (14)   |<-Gray   |
|   |  GND   D0   VCC   |            | GPIO22(15)o o (16)   |  [S]    |
|   |   o     o     o   |                                             |
|   +---+-----+-----+---+                                             |
|       |     |     |                                                 |
|       |     |     +-- [+] Orange ------> 3.3V (Pin 1)               |
|       |     +-------- [S] Gray --------> GPIO27 (Pin 13)            |
|       +-------------- [-] Black -------> GND (Pin 6)                |
+=====================================================================+
```

---

## Operation

### Output Behavior

| State | D0 Output | LED |
|-------|-----------|-----|
| No vibration (idle) | LOW | ON |
| Vibration detected | HIGH | OFF |

### Sensitivity Adjustment

The onboard potentiometer adjusts the detection threshold:
- **Turn clockwise**: Increase sensitivity (detect smaller vibrations)
- **Turn counter-clockwise**: Decrease sensitivity (detect only stronger vibrations)

---

## Usage Example

```python
from src.sensors.vibration import VibrationSensor, VibrationState

# Initialize sensor on GPIO27 (GPIO17 is used by PIR sensor)
sensor = VibrationSensor(gpio_pin=27)
sensor.initialize()

# Check for vibration
if sensor.is_vibration_detected():
    print("Vibration detected!")

# Wait for vibration event (with 10 second timeout)
event = sensor.wait_for_vibration(timeout_sec=10.0)
if event:
    print(f"Detected: {event}")

# Cleanup when done
sensor.cleanup()
```

---

## Interactive Test

Run the interactive test to verify your wiring:

```bash
sudo python3 tests/test_sensors/test_vibration_interactive.py
```

---

## Key Features

| Feature | Details |
|---------|---------|
| Gold-plated sensor | 60 million shock durability |
| LM393 comparator | Clean digital output |
| Adjustable sensitivity | Onboard potentiometer |
| Omnidirectional | Detects vibration from any direction |
| LED indicator | Visual feedback (OFF when triggered) |

