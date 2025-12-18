# Yoshi Smart Pi5 Monitoring Kit

A comprehensive sensor monitoring system for Raspberry Pi 5 with support for temperature, humidity, motion, vibration, sound, and door sensors. Built for real-time monitoring and event detection with both unified and individual sensor testing capabilities.

## 🌟 Features

- **Unified Monitoring**: Monitor all sensors simultaneously with live dashboard
- **Individual Tests**: Comprehensive test suites for each sensor
- **Real-time Events**: Immediate event logging with timestamps
- **Multi-threaded**: Concurrent monitoring without blocking
- **Flexible Configuration**: Choose which sensors to monitor
- **Professional Display**: Tabular dashboard with live updates
- **Robust Error Handling**: Graceful degradation and error reporting

## 📦 Hardware Components

| Sensor | Model | GPIO Pin | Interface | Purpose |
|--------|-------|----------|-----------|---------|
| Temperature & Humidity | XY-MD02 | - | RS485/Modbus | Environmental monitoring |
| Motion Sensor | HC-SR501 PIR | GPIO17 | Digital | Motion detection |
| Vibration Sensor | 801S | GPIO27 | Digital | Vibration/shock detection |
| Sound Sensor | LM393 | GPIO22 | Digital | Sound level detection |
| Door Sensor | MC-38 | GPIO23 | Digital | Magnetic reed switch |

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi 5 (or compatible model)
- Python 3.7 or higher
- GPIO access permissions

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/ansarirahim/yoshi-smart-pi5-monitoring-kit.git
cd yoshi-smart-pi5-monitoring-kit
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt --break-system-packages
```

Or install manually:
```bash
pip install gpiozero RPi.GPIO minimalmodbus pyserial --break-system-packages
```

3. **Verify hardware connections** (see [Wiring Guide](#wiring-guide))

### Usage

#### Unified Monitoring (All Sensors)

Monitor all sensors with live dashboard:
```bash
cd unified-monitoring
python monitor.py
```

Monitor specific sensors:
```bash
python monitor.py --sensors motion vibration door
```

Event log only (no dashboard):
```bash
python monitor.py --no-dashboard
```

Monitor for limited time:
```bash
python monitor.py --duration 60  # Monitor for 60 seconds
```

#### Individual Sensor Tests

**Temperature Sensor**:
```bash
cd temperature
python temperature.py
python md02.py --port /dev/ttyUSB0 --interval 2.0
```

**Motion Sensor**:
```bash
cd motion-sensor
python pir_test.py
python pir_test.py --test motion --timeout 30
```

**Vibration Sensor**:
```bash
cd vibration-sensor
python vibration_test.py
python vibration_test.py --test sensitivity
```

**Sound Sensor**:
```bash
cd sound-sensor
python sound_test.py
python sound_live_test.py --duration 30
```

**Door Sensor**:
```bash
cd door-sensor
python door_test_10sec.py
python door-sensor-test.py --duration 60
```

## 📊 Dashboard Display

The unified monitoring system provides a real-time dashboard:

```
╔════════════════════════════════════════════════════════════════════╗
║        UNIFIED SENSOR MONITORING DASHBOARD                         ║
╚════════════════════════════════════════════════════════════════════╝

┌─────────────┬──────────────────────┬────────┬──────────────────────┐
│    Sensor   │      Status          │ Events │    Last Event        │
├─────────────┼──────────────────────┼────────┼──────────────────────┤
│ DOOR        │ CLOSED               │      5 │ 2025-12-18 14:32:15  │
│ MOTION      │ Motion Detected      │     12 │ 2025-12-18 14:32:18  │
│ SOUND       │ Sound Detected       │      3 │ 2025-12-18 14:31:45  │
│ TEMPERATURE │ 24.6°C / 45.2%       │    142 │ 2025-12-18 14:32:17  │
│ VIBRATION   │ Vibrating            │      7 │ 2025-12-18 14:30:22  │
└─────────────┴──────────────────────┴────────┴──────────────────────┘

Current Time: 2025-12-18 14:32:20
(Updating every 2 seconds... Press CTRL+C to stop)
```

## 🔌 Wiring Guide

### GPIO Pin Assignments

```
Raspberry Pi GPIO Layout (BCM numbering):

GPIO17 (Pin 11) - HC-SR501 PIR Motion Sensor (OUT)
GPIO22 (Pin 15) - LM393 Sound Sensor (DOUT)
GPIO23 (Pin 16) - MC-38 Door Sensor
GPIO27 (Pin 13) - 801S Vibration Sensor (DOUT)

USB Port - XY-MD02 Temperature Sensor (RS485 to USB adapter)
```

### Temperature Sensor (XY-MD02)

- **Interface**: RS485 (requires USB to RS485 adapter)
- **Connection**:
  - A+ → RS485 A+
  - B- → RS485 B-
  - VCC → 5V
  - GND → GND
- **Default**: `/dev/ttyUSB0`, Slave ID: 1, Baudrate: 9600

### Motion Sensor (HC-SR501)

- **GPIO**: GPIO17 (Pin 11)
- **Connection**:
  - VCC → 5V
  - GND → GND
  - OUT → GPIO17
- **Detection Range**: 3-7 meters
- **Trigger Mode**: Repeatable (H)

### Vibration Sensor (801S)

- **GPIO**: GPIO27 (Pin 13)
- **Connection**:
  - VCC → 3.3V
  - GND → GND
  - DOUT → GPIO27
- **Output**: Digital (LOW when vibration detected)

### Sound Sensor (LM393)

- **GPIO**: GPIO22 (Pin 15)
- **Connection**:
  - VCC → 3.3V or 5V
  - GND → GND
  - DOUT → GPIO22
- **Adjustable**: Sensitivity via onboard potentiometer

### Door Sensor (MC-38)

- **GPIO**: GPIO23 (Pin 16)
- **Type**: Magnetic reed switch (Normally Closed)
- **Connection**:
  - One wire → GPIO23
  - Other wire → GND
- **State**: LOW = Closed, HIGH = Open

## 📁 Project Structure

```
yoshi-smart-pi5-monitoring-kit/
├── README.md                       # Main documentation
├── requirements.txt                # Python dependencies
├── LICENSE                         # Project license
│
├── unified-monitoring/             # Unified monitoring system
│   ├── monitor.py                  # Main unified monitor
│   └── README.md                   # Unified monitoring guide
│
├── temperature/                    # Temperature sensor
│   ├── temperature.py              # Simple temperature reader
│   ├── md02.py                     # Advanced Modbus reader
│   ├── md02_scanner.py             # Device scanner
│   ├── MD02_MODBUS_GUIDE.md        # Detailed Modbus guide
│   ├── SETUP_SUMMARY.txt           # Setup instructions
│   └── README.md                   # Temperature documentation
│
├── motion-sensor/                  # Motion sensor
│   ├── pir_test.py                 # Comprehensive test suite
│   ├── PIR_TEST_GUIDE.md           # Testing guide
│   └── PIR_SUMMARY.txt             # Quick reference
│
├── vibration-sensor/               # Vibration sensor
│   ├── vibration_test.py           # Full test suite
│   ├── vibration_simple_test.py    # Simple quick test
│   ├── VIBRATION_TEST_GUIDE.md     # Testing guide
│   └── VIBRATION_SUMMARY.txt       # Quick reference
│
├── sound-sensor/                   # Sound sensor
│   ├── sound_test.py               # Test suite
│   ├── sound_live_test.py          # Live monitoring
│   ├── SOUND_TEST_GUIDE.md         # Testing guide
│   └── SOUND_SUMMARY.txt           # Quick reference
│
└── door-sensor/                    # Door sensor
    ├── door-sensor-test.py         # Full test suite
    └── door_test_10sec.py          # Quick 10-second test
```

## 🧪 Testing

### Comprehensive Test Suites

Each sensor includes a comprehensive test suite:

**Motion Sensor** (7 tests):
- Idle state detection
- Motion detection
- Signal recovery
- Repeated motion cycles
- Timeout handling
- State transitions
- Statistics tracking

**Vibration Sensor** (7 tests):
- Idle state verification
- Vibration detection
- Signal recovery
- Repeated vibration cycles
- Sensitivity testing
- Intensity measurement
- Duration accuracy

**Sound Sensor** (2 tests):
- Silent environment detection
- Sound detection and counting

**Door Sensor** (3 tests):
- Closed state detection
- Open state detection
- Debounce verification

### Running Tests

Run all tests for a sensor:
```bash
cd motion-sensor
python pir_test.py
```

Run specific test:
```bash
python pir_test.py --test motion
```

Run with custom parameters:
```bash
python pir_test.py --gpio 17 --timeout 30
```

## 🔧 Configuration

### Environment Variables

Set custom USB port for temperature sensor:
```bash
export TEMP_SENSOR_PORT=/dev/ttyUSB0
```

### Command-Line Arguments

Most scripts support configuration via command-line arguments:

```bash
# Unified monitor
python monitor.py --sensors motion door --duration 60 --no-dashboard

# Temperature sensor
python md02.py --port /dev/ttyUSB0 --slave-id 1 --baudrate 9600 --interval 2.0

# Motion sensor
python pir_test.py --gpio 17 --timeout 30 --test motion

# Vibration sensor
python vibration_test.py --gpio 27 --test sensitivity --timeout 15

# Sound sensor
python sound_test.py --gpio 22 --duration 30

# Door sensor
python door-sensor-test.py --gpio 23 --duration 60
```

## 📚 Documentation

Detailed guides are available for each component:

- **[Unified Monitoring README](unified-monitoring/README.md)**: Complete guide for unified monitoring
- **[Temperature MD02 Guide](temperature/MD02_MODBUS_GUIDE.md)**: Detailed Modbus protocol documentation
- **[Motion PIR Guide](motion-sensor/PIR_TEST_GUIDE.md)**: Comprehensive motion sensor testing
- **[Vibration Test Guide](vibration-sensor/VIBRATION_TEST_GUIDE.md)**: Complete vibration sensor testing
- **[Sound Test Guide](sound-sensor/SOUND_TEST_GUIDE.md)**: Sound sensor usage and testing

## 🐛 Troubleshooting

### Common Issues

**Temperature sensor not detected:**
```bash
# Check USB device
ls -l /dev/ttyUSB*

# Try alternative ports
python md02_scanner.py
```

**GPIO permission denied:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
sudo reboot
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --break-system-packages
```

**Sensors not responding:**
- Verify wiring connections
- Check power supply (5V for most sensors)
- Ensure GPIO pins are correct
- Test individual sensors first before unified monitoring

### Debug Mode

Enable verbose logging:
```bash
# For unified monitoring
python monitor.py --sensors motion --no-dashboard 2>&1 | tee debug.log

# For individual sensors
python pir_test.py --test motion 2>&1 | tee pir_debug.log
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly on Raspberry Pi hardware
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**A.R. Ansari**
- GitHub: [@ansarirahim](https://github.com/ansarirahim)

## 🙏 Acknowledgments

- Built for Raspberry Pi 5
- Uses gpiozero for GPIO management
- minimalmodbus for Modbus RTU communication
- RPi.GPIO for low-level GPIO access

## 📝 Version History

- **v1.0.0** (2025-12-18)
  - Initial release
  - Unified monitoring system
  - Individual sensor test suites
  - Comprehensive documentation
  - Support for 5 sensor types

## 🔗 Related Projects

- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- [minimalmodbus Documentation](https://minimalmodbus.readthedocs.io/)
- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)

## 💬 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in each sensor folder
- Review the troubleshooting section above

---

**Built with ❤️ for Raspberry Pi enthusiasts and IoT developers**
