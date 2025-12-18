# MC-38 Magnetic Door/Window Sensor

## Overview

The MC-38 is a wired magnetic door/window sensor using a reed switch. It detects open/close states by sensing the proximity of a magnet. Unlike electronic sensors, this is a simple mechanical switch - completely safe for GPIO with no voltage concerns.

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Model | MC-38 Wired Door Window Sensor |
| Type | Reed Switch (Normally Closed - NC) |
| Operation | Magnetic proximity detection |
| Electronics | None - just a switch |
| Polarity | None - wires interchangeable |
| Power | None required (passive switch) |
| Safety | Completely safe for GPIO |

> **Key Point**: This is NOT an electronic sensor. It's a simple reed switch that acts like a button - magnet controls open/close state.

---

## How It Works

### Normally Closed (NC) Type

| Door State | Magnet Position | Switch State | GPIO Reads |
|------------|-----------------|--------------|------------|
| **CLOSED** | Near (touching) | CLOSED | **LOW (0)** |
| **OPEN** | Away (separated) | OPEN | **HIGH (1)** |

The reed switch closes when magnet is near, connecting GPIO to GND (LOW).
With internal pull-up, GPIO reads HIGH when switch is open.

---

## Wiring to Raspberry Pi 5 (4GB)

### Connection Table

| MC-38 Wire | Wire Color | RPi Pin | RPi Function |
|------------|------------|---------|--------------|
| Wire 1 | White | Pin 16 | GPIO23 |
| Wire 2 | White | Pin 6 | Ground |

> **No polarity** - Either wire can go to GPIO or GND.

### Wiring Diagram

```
+=====================================================================+
|     MC-38 Magnetic Door Sensor Wiring - Raspberry Pi 5 (4GB)        |
+=====================================================================+
|  Type: Reed Switch (Normally Closed - NC)                           |
|  No polarity - wires are interchangeable                            |
+=====================================================================+
|                                                                     |
|   MC-38 Door Sensor               Raspberry Pi 5                    |
|   +-------------------+           +----------------------+          |
|   |  +-----------+    |           | 3.3V (1) o o (2) 5V  |          |
|   |  |  MAGNET   |    |           | GPIO2(3) o o (4) 5V  |          |
|   |  +-----------+    |           | GPIO3(5) o o (6) GND |<--White  |
|   |                   |           | GPIO4(7) o o (8)     |   Wire 2 |
|   |  +-----------+    |           |   GND(9) o o (10)    |          |
|   |  |   REED    |    |           | GPIO17(11)o o (12)   | [PIR]    |
|   |  |  SWITCH   |    |           | GPIO27(13)o o (14)   | [VIB]    |
|   |  |  (NC)     |    |           | GPIO22(15)o o (16)   |<--White  |
|   |  +-----------+    |           |  3.3V(17)o o (18)    |   Wire 1 |
|   +-------------------+           +----------------------+  [DOOR]  |
|                                                                     |
|     Wire 1 (White) ---------> GPIO23 (Pin 16)                       |
|     Wire 2 (White) ---------> GND (Pin 6)                           |
|                                                                     |
+=====================================================================+
```

---

## Why This Sensor is Perfect for Raspberry Pi

| Advantage | Description |
|-----------|-------------|
| **Zero noise** | No false triggers unlike sound/vibration sensors |
| **No voltage issues** | Just a switch - no 5V/3.3V concerns |
| **No calibration** | Works immediately, every time |
| **Low power** | Passive - consumes almost no power |
| **Reliable** | Simple mechanics = reliable operation |
| **Safe** | Cannot damage GPIO pins |

---

## Usage Example

```python
from src.sensors.door import DoorSensor, DoorState

# Initialize sensor on GPIO23
sensor = DoorSensor(gpio_pin=23)
sensor.initialize()

# Check door state
if sensor.is_door_open():
    print("Door is OPEN!")
else:
    print("Door is CLOSED")

# Wait for state change (with 60 second timeout)
event = sensor.wait_for_change(timeout_sec=60.0)
if event:
    print(f"Door state changed: {event}")

# Cleanup when done
sensor.cleanup()
```

---

## Interactive Test

Run the interactive test to verify your wiring:

```bash
sudo python3 tests/test_sensors/test_door_interactive.py
```

---

## GPIO Pin Assignment

| Sensor | GPIO | Pin | Status |
|--------|------|-----|--------|
| PIR Motion | GPIO17 | Pin 11 | Reserved |
| Sound | GPIO22 | Pin 15 | Reserved |
| Vibration | GPIO27 | Pin 13 | Reserved |
| **Door** | **GPIO23** | **Pin 16** | **This sensor** |

---

## Important Notes

1. **NC vs NO**: This sensor is **Normally Closed (NC)**. If you have a Normally Open (NO) type, the logic is reversed.

2. **Internal Pull-up**: The code uses Raspberry Pi's internal pull-up resistor. No external resistor needed.

3. **Mounting**: Mount the magnet on the door/window, and the reed switch on the frame. They should be aligned and close together when closed.

