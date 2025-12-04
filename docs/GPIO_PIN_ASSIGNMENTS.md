# GPIO Pin Assignments - Raspberry Pi 5 (4GB)

## Overview

This document tracks all GPIO pin assignments for the Smart Monitoring Kit to prevent conflicts when adding new sensors or modules.

---

## Current Assignments

| GPIO (BCM) | Physical Pin | Sensor/Module | Wire Color | Function |
|------------|--------------|---------------|------------|----------|
| **GPIO17** | Pin 11 | HC-SR501 PIR Motion Sensor | Brown | Digital Input (motion detect) |
| **GPIO22** | Pin 15 | LM393 Sound Sensor | White | Digital Input (sound detect) |
| **GPIO23** | Pin 16 | MC-38 Door Sensor | White | Digital Input (door open/close) |
| **GPIO27** | Pin 13 | 801S Vibration Sensor | Gray | Digital Input (vibration detect) |

---

## Power & Ground Assignments

| Physical Pin | Function | Connected To |
|--------------|----------|--------------|
| Pin 1 | 3.3V | PIR VCC (Orange), Vibration VCC (Orange), Sound VCC (Orange) |
| Pin 6 | GND | PIR GND (Black), Vibration GND (Black), Sound GND (Black) |

---

## Available GPIO Pins

| GPIO (BCM) | Physical Pin | Status |
|------------|--------------|--------|
| GPIO2 | Pin 3 | Available (I2C SDA) |
| GPIO3 | Pin 5 | Available (I2C SCL) |
| GPIO4 | Pin 7 | Available |
| GPIO17 | Pin 11 | **USED** - PIR Motion Sensor |
| GPIO22 | Pin 15 | **USED** - Sound Sensor |
| GPIO23 | Pin 16 | **USED** - Door Sensor |
| GPIO24 | Pin 18 | Available |
| GPIO25 | Pin 22 | Available |
| GPIO27 | Pin 13 | **USED** - Vibration Sensor |

---

## Sensor Summary

### HC-SR501 PIR Motion Sensor
- **GPIO**: GPIO17 (Pin 11)
- **VCC**: Pin 1 (3.3V) - Orange wire
- **GND**: Pin 6 - Black wire
- **Signal**: Brown wire
- **Doc**: [PIR_MOTION_SENSOR.md](PIR_MOTION_SENSOR.md)

### 801S Vibration Shock Sensor
- **GPIO**: GPIO27 (Pin 13)
- **VCC**: Pin 1 (3.3V) - Orange wire
- **GND**: Pin 6 - Black wire
- **Signal**: Gray wire
- **Doc**: [VIBRATION_SENSOR.md](VIBRATION_SENSOR.md)

### LM393 Sound Sensor
- **GPIO**: GPIO22 (Pin 15)
- **VCC**: Pin 1 (3.3V) - Orange wire
- **GND**: Pin 6 - Black wire
- **Signal**: White wire
- **Output**: ACTIVE LOW (LOW when sound detected)
- **Doc**: [SOUND_SENSOR.md](SOUND_SENSOR.md)

### MC-38 Door Sensor
- **GPIO**: GPIO23 (Pin 16)
- **GND**: Pin 6 - White wire
- **Signal**: White wire (to GPIO23)
- **Type**: Reed Switch (Normally Closed)
- **No polarity** - wires interchangeable
- **Doc**: [DOOR_SENSOR.md](DOOR_SENSOR.md)

### XY-MD02 Temperature/Humidity Sensor
- **Interface**: RS485 (USB adapter)
- **No GPIO used** - connects via USB-RS485 converter
- **Doc**: [XY-MD02_SENSOR.md](XY-MD02_SENSOR.md)

---

## Pin Reference Diagram

```
                    Raspberry Pi 5 GPIO Header
                    ==========================

                     3.3V (1) [*] [*] (2) 5V
              I2C SDA GPIO2 (3) [ ] [ ] (4) 5V
              I2C SCL GPIO3 (5) [ ] [*] (6) GND
                      GPIO4 (7) [ ] [ ] (8) GPIO14 TX
                        GND (9) [ ] [ ] (10) GPIO15 RX
        [PIR] --> GPIO17 (11) [*] [ ] (12) GPIO18
  [VIBRATION] --> GPIO27 (13) [*] [ ] (14) GND
      [SOUND] --> GPIO22 (15) [*] [*] (16) GPIO23 <-- [DOOR]
                       3.3V (17) [ ] [ ] (18) GPIO24
             SPI MOSI GPIO10 (19) [ ] [ ] (20) GND
              SPI MISO GPIO9 (21) [ ] [ ] (22) GPIO25
             SPI SCLK GPIO11 (23) [ ] [ ] (24) GPIO8 CE0
                        GND (25) [ ] [ ] (26) GPIO7 CE1
                     ID_SD (27) [ ] [ ] (28) ID_SC
                      GPIO5 (29) [ ] [ ] (30) GND
                      GPIO6 (31) [ ] [ ] (32) GPIO12
                     GPIO13 (33) [ ] [ ] (34) GND
                     GPIO19 (35) [ ] [ ] (36) GPIO16
                     GPIO26 (37) [ ] [ ] (38) GPIO20
                        GND (39) [ ] [ ] (40) GPIO21

    Legend: [*] = In Use    [ ] = Available
```

---

## Guidelines for Adding New Sensors

1. **Check this document** before assigning GPIO pins
2. **Avoid conflicts** with existing assignments
3. **Update this document** when adding new sensors
4. **Use 3.3V** for sensor VCC to protect GPIO pins
5. **Document wire colors** for easy identification

---

## Quick Reference

| Sensor | GPIO | Pin | Color |
|--------|------|-----|-------|
| PIR Motion | GPIO17 | 11 | Brown |
| Sound | GPIO22 | 15 | White |
| Door | GPIO23 | 16 | White |
| Vibration | GPIO27 | 13 | Gray |

