# Unified Sensor Monitoring System

Comprehensive real-time monitoring of all sensors with simultaneous event detection, tabular dashboard, and activity logging.

## Overview

This system monitors **5 sensors** simultaneously and catches all activities with live dashboard display:

| Sensor | GPIO | Status |
|--------|------|--------|
| Temperature (XY-MD02) | Modbus | ✅ Active |
| Motion (HC-SR501) | GPIO17 | ✅ Active |
| Vibration (801S) | GPIO27 | ✅ Active |
| Sound (LM393) | GPIO22 | ✅ Active |
| Door (MC-38) | GPIO23 | ✅ Active |

## Features

✨ **Tabular Dashboard**: Live-updating status table showing all sensor data
✨ **Real-time Events**: Immediate logging of sensor activities with timestamps
✨ **Multi-threaded**: Concurrent monitoring of all sensors
✨ **Configurable**: Choose which sensors to monitor
✨ **Flexible Display**: Dashboard mode or event log only

## Quick Start

### Installation

```bash
pip install gpiozero minimalmodbus RPi.GPIO --break-system-packages
```

### Monitor All Sensors with Dashboard

```bash
python monitor.py
```

**Dashboard Display**:
```
╔════════════════════════════════════════════════════════════════════╗
║        UNIFIED SENSOR MONITORING DASHBOARD                         ║
╚════════════════════════════════════════════════════════════════════╝

┌─────────────┬──────────────────────┬────────┬──────────────────────┐
│    Sensor   │      Status          │ Events │    Last Event        │
├─────────────┼──────────────────────┼────────┼──────────────────────┤
│ DOOR        │ OPEN                 │      2 │ 2025-12-13 19:32:15  │
│ MOTION      │ No Motion            │      1 │ 2025-12-13 19:31:45  │
│ SOUND       │ Silent               │      0 │ Never                │
│ TEMPERATURE │ 24.6°C / 45.2%       │     42 │ 2025-12-13 19:32:14  │
│ VIBRATION   │ Stable               │      0 │ Never                │
└─────────────┴──────────────────────┴────────┴──────────────────────┘

Current Time: 2025-12-13 19:32:17
(Updating every 2 seconds... Press CTRL+C to stop)
```

**Event Log Display**:
```
[2025-12-13 19:30:50] 🌡️  TEMPERATURE: 24.6°C | Humidity: 45.2%
[2025-12-13 19:31:05] 🚨 MOTION DETECTED (#1)
[2025-12-13 19:31:06] ✓ Motion stopped
[2025-12-13 19:31:15] 🔊 SOUND DETECTED (#1)
[2025-12-13 19:31:22] 📳 VIBRATION DETECTED (#1)
[2025-12-13 19:31:30] 🔒 DOOR CLOSED (#1)
```

### Monitor Specific Sensors

```bash
# Motion and vibration only
python monitor.py --sensors motion vibration

# Temperature and door only
python monitor.py --sensors temperature door

# Just monitor sound
python monitor.py --sensors sound
```

### Event Log Only (No Dashboard)

```bash
# Disable dashboard, show events only
python monitor.py --no-dashboard

# Specific sensors, events only
python monitor.py --sensors motion door --no-dashboard
```

### Monitor for Limited Time

```bash
# Monitor for 60 seconds then exit
python monitor.py --duration 60

# Monitor specific sensors for 120 seconds
python monitor.py --sensors motion door --duration 120
```

## Features

✅ **Tabular Dashboard** - Live-updating table with all sensor statuses
✅ **Real-time Monitoring**
- All sensors monitored simultaneously
- Instant event detection and logging
- Color-coded output with emoji indicators

✅ **Multi-threaded Design**
- Independent sensor threads
- Thread-safe event counting
- No blocking operations

✅ **Event Logging**
- Timestamp for every event
- Event counter per sensor
- Summary report on exit

✅ **Flexible Configuration**
- Monitor all or specific sensors
- Configurable duration
- Command-line arguments

## Events Caught

### Motion Sensor
- 🚨 Motion detected
- ✓ Motion stopped

### Vibration Sensor
- 📳 Vibration detected

### Sound Sensor
- 🔊 Sound detected

### Door Sensor
- 🔒 Door closed (wires shorted)
- 🚪 Door open (wires separated)

### Temperature Sensor
- 🌡️ Temperature reading
- Temperature & humidity values
- Updates every 5 seconds

## Command Examples

```bash
# Run all sensors indefinitely
python monitor.py

# Run for 2 minutes
python monitor.py --duration 120

# Monitor only motion and door
python monitor.py --sensors motion door

# Monitor motion, vibration, sound for 5 minutes
python monitor.py --sensors motion vibration sound --duration 300

# Monitor temperature only (no GPIO sensors)
python monitor.py --sensors temperature

# Run with sudo (if GPIO permission issues)
sudo python monitor.py
```

## Output Format

Each event is logged with:
- **Timestamp**: `[YYYY-MM-DD HH:MM:SS]`
- **Emoji Indicator**: Visual sensor identification
- **Event Type**: What happened
- **Counter**: Event number for that sensor

Example:
```
[2025-12-13 19:31:22] 📳 VIBRATION DETECTED (#1)
[2025-12-13 19:31:30] 🚪 DOOR OPEN (#1)
[2025-12-13 19:31:45] 🌡️  TEMPERATURE: 24.6°C | Humidity: 45.2%
```

## Summary Report

When monitoring stops (Ctrl+C), a summary is displayed:

```
======================================================================
MONITORING SUMMARY
======================================================================
DOOR                 Events: 2
MOTION               Events: 3
SOUND                Events: 1
TEMPERATURE          Events: 12
VIBRATION            Events: 1
======================================================================
```

## Troubleshooting

### "Permission denied" error
```bash
sudo python monitor.py
```

### "No module named gpiozero"
```bash
pip install gpiozero RPi.GPIO --break-system-packages
```

### "Modbus timeout"
- Check XY-MD02 sensor power
- Verify USB serial connection
- Adjust timeout in code if needed

### "GPIO pin not found"
- Verify all sensors are physically connected
- Check GPIO pin numbers
- Try individual sensor tests first

## Sensor Details

### Motion (HC-SR501) - GPIO17
- Detects movement
- ~7 meter range
- Adjustable sensitivity

### Vibration (801S) - GPIO27
- Detects physical vibration
- Adjustable threshold
- Instant response

### Sound (LM393) - GPIO22
- Detects sound/noise
- Adjustable sensitivity
- ~50-100ms response

### Door (MC-38) - GPIO23
- Detects door position
- Closed = wires shorted (HIGH)
- Open = wires separated (LOW)

### Temperature (XY-MD02) - Modbus RS485
- Temperature measurement
- Humidity measurement
- Updates: Every 5 seconds
- Range: -40 to +80°C

## Individual Sensor Tests

For individual sensor testing, see:
- `/home/yoshi/individual-sensor-tests/motion-sensor/pir_test.py`
- `/home/yoshi/individual-sensor-tests/vibration-sensor/vibration_test.py`
- `/home/yoshi/individual-sensor-tests/sound-sensor/sound_test.py`
- `/home/yoshi/individual-sensor-tests/door-sensor/door-sensor-test.py`
- `/home/yoshi/individual-sensor-tests/md02.py`

## Support

For issues:
1. Check GPIO wiring
2. Verify sensor power connections
3. Test individual sensors first
4. Check hardware initialization messages

---

**Status**: ✅ Production Ready

**Created**: 2025-12-13

**Usage**: `python monitor.py [--sensors SENSOR] [--duration SEC]`
