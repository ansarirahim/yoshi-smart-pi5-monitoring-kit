# LM393 Sound Sensor Module

## Overview

The LM393 Sound Sensor Module (TekBud) detects ambient audio and sound levels using a microphone and LM393 comparator chip. It outputs a digital LOW signal when sound exceeds the adjustable threshold - ideal for sound-triggered applications.

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Model | TekBud LM393 Sound Sensor Module |
| Operating Voltage | 4V - 6V DC (**3.3V also works**) |
| Comparator IC | LM393 |
| Output Type | Digital (D0) + Analog (A0) |
| Digital Output | **ACTIVE LOW** - LOW when sound detected |
| LED Indicator | ON when sound detected |
| Sensitivity | Adjustable via blue potentiometer |
| Detection | Ambient audio, voice, claps, etc. |
| **Orientation** | **Keep microphone facing DOWN (bottom side up)** |

> **Purpose**: Detects sound levels for audio-activated applications like smart alarms, sound-controlled LEDs, voice-triggered systems, and STEM learning projects.

---

## Pin Configuration

```
    +-----------------------------------------------+
    |          LM393 Sound Sensor Module            |
    |                                               |
    |   +---------+                                 |
    |   |  (MIC)  |  Electret Microphone            |
    |   +---------+                                 |
    |                                               |
    |   +-------------+                             |
    |   | [Sens.]     |  Blue Potentiometer         |
    |   | Sensitivity |  (Adjust threshold)         |
    |   +-------------+                             |
    |                                               |
    |   [LM393 Comparator IC]                       |
    |                                               |
    |      A0       D0      GND      VCC            |
    |       o        o        o        o            |
    |      [A]      [S]      [-]      [+]           |
    +-----------------------------------------------+
```

| Pin | Name | Polarity | Description |
|-----|------|----------|-------------|
| 1 | **A0** | **[A]** | Analog output (not used - RPi has no ADC) |
| 2 | **D0** | **[S]** | Digital output (LOW on sound - ACTIVE LOW) |
| 3 | **GND** | **[-]** | Ground |
| 4 | **VCC** | **[+]** | Power supply (3.3V) |

---

## Wiring to Raspberry Pi 5 (4GB)

### Connection Table

| Sound Sensor Pin | Polarity | Wire Color | RPi Pin | RPi Function |
|------------------|----------|------------|---------|--------------|
| VCC | [+] | Orange | Pin 1 | 3.3V Power |
| GND | [-] | Black | Pin 6 | Ground |
| D0 | [S] | White | Pin 15 | GPIO22 |
| A0 | [A] | - | Not connected | (No native ADC) |

> **Note**: GPIO17 = PIR Sensor, GPIO27 = Vibration Sensor. Sound Sensor uses GPIO22.

### Wiring Diagram

```
+=====================================================================+
|     LM393 Sound Sensor Wiring - Raspberry Pi 5 (4GB)                |
+=====================================================================+
|  Note: D0 output is ACTIVE LOW (LOW when sound detected)            |
+=====================================================================+
|                                                                     |
|   LM393 Sound Module              Raspberry Pi 5                    |
|   +-------------------+           +----------------------+          |
|   | [Mic]             |           | 3.3V (1) o o (2) 5V  |<-Orange  |
|   |  ()               |           | GPIO2(3) o o (4) 5V  |  [+]     |
|   |                   |           | GPIO3(5) o o (6) GND |<-Black   |
|   | [Potentiometer]   |           | GPIO4(7) o o (8)     |  [-]     |
|   |  Sensitivity      |           |   GND(9) o o (10)    |          |
|   |                   |           | GPIO17(11)o o (12)   | [PIR]    |
|   | [LM393 IC]        |           | GPIO27(13)o o (14)   | [VIB]    |
|   |                   |           | GPIO22(15)o o (16)   |<-White   |
|   |  A0  D0  GND VCC  |           |  3.3V(17)o o (18)    |  [S]     |
|   |   o   o   o   o   |           +----------------------+          |
|   +---+---+---+---+---+                                             |
|       |   |   |   |                                                 |
|      N/C  |   |   +-- [+] Orange ------> 3.3V (Pin 1)               |
|           |   +------ [-] Black -------> GND (Pin 6)                |
|           +---------- [S] White -------> GPIO22 (Pin 15)            |
+=====================================================================+
```

---

## Operation

### Output Behavior (ACTIVE LOW)

| State | D0 Output | LED |
|-------|-----------|-----|
| Quiet (no sound) | **HIGH** | OFF |
| Sound detected | **LOW** | ON |

### Sensitivity Adjustment

The blue potentiometer adjusts the detection threshold:
- **Turn CLOCKWISE**: Increase sensitivity (detect quieter sounds)
- **Turn ANTI-CLOCKWISE**: Decrease sensitivity (detect only louder sounds)

### Mounting Orientation

```
    CORRECT ORIENTATION (Microphone facing DOWN):

    +-------------------+
    | [Potentiometer]   |  <-- Top (adjust from here)
    | [LM393 IC]        |
    |  A0  D0  GND VCC  |  <-- Pins
    +-------------------+
    | (( MIC ))         |  <-- Bottom (microphone facing DOWN)
    +-------------------+
           ↓
       Sound source
```

> **Tip**: Keep the microphone (cylindrical silver component) facing **downward** toward the sound source for best detection.

---

## Usage Example

```python
from src.sensors.sound import SoundSensor, SoundState

# Initialize sensor on GPIO22
sensor = SoundSensor(gpio_pin=22)
sensor.initialize()

# Check for sound (ACTIVE LOW - LOW means sound detected)
if sensor.is_sound_detected():
    print("Sound detected!")

# Wait for sound event (with 10 second timeout)
event = sensor.wait_for_sound(timeout_sec=10.0)
if event:
    print(f"Detected: {event}")

# Cleanup when done
sensor.cleanup()
```

---

## Interactive Test

Run the interactive test to verify your wiring:

```bash
sudo python3 tests/test_sensors/test_sound_interactive.py
```

---

## GPIO Pin Assignment

| Sensor | GPIO | Pin | Status |
|--------|------|-----|--------|
| PIR Motion | GPIO17 | Pin 11 | Reserved |
| Vibration | GPIO27 | Pin 13 | Reserved |
| **Sound** | **GPIO22** | **Pin 15** | **This sensor** |

