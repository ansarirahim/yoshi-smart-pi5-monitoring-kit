# Dependencies Documentation

Complete guide to dependencies and installation for the Yoshi Smart Pi5 Monitoring Kit.

## Python Dependencies

### Core Libraries

#### 1. gpiozero (≥2.0.1)
**Purpose**: High-level GPIO control and sensor management  
**Used in**: All GPIO-based sensors (motion, vibration, sound, door)  
**Features**:
- Event-driven sensor handling
- Debounce support
- Pull-up/pull-down resistor configuration
- Thread-safe operations

**Installation**:
```bash
pip install gpiozero --break-system-packages
```

**Documentation**: https://gpiozero.readthedocs.io/

---

#### 2. RPi.GPIO (≥0.7.1)
**Purpose**: Low-level GPIO access for Raspberry Pi  
**Used in**: Direct GPIO control, unified monitoring system  
**Features**:
- BCM pin numbering
- GPIO mode configuration
- Interrupt handling
- PWM support

**Installation**:
```bash
pip install RPi.GPIO --break-system-packages
```

**Documentation**: https://sourceforge.net/projects/raspberry-gpio-python/

---

#### 3. minimalmodbus (≥2.1.1)
**Purpose**: Modbus RTU communication protocol  
**Used in**: Temperature sensor (XY-MD02)  
**Features**:
- RTU mode support
- CRC-16 validation
- Multiple register reading
- Configurable serial parameters

**Installation**:
```bash
pip install minimalmodbus --break-system-packages
```

**Documentation**: https://minimalmodbus.readthedocs.io/

---

#### 4. pyserial (≥3.5)
**Purpose**: Serial port communication  
**Used in**: RS485 communication with temperature sensor  
**Features**:
- Cross-platform serial support
- Timeout configuration
- Baudrate and parity settings
- Binary data handling

**Installation**:
```bash
pip install pyserial --break-system-packages
```

**Documentation**: https://pyserial.readthedocs.io/

---

### Standard Library (No Installation Required)

These are included with Python 3.7+:

- **threading**: Multi-threaded sensor monitoring
- **datetime**: Timestamp generation
- **time**: Sleep and timing functions
- **signal**: Graceful shutdown handling
- **sys**: System operations
- **argparse**: Command-line argument parsing
- **os**: Operating system interface
- **collections**: defaultdict for event counting
- **struct**: Binary data packing (temperature sensor)

---

## System Dependencies

### Operating System
- **Raspberry Pi OS** (Bookworm or later recommended)
- 32-bit or 64-bit version
- Kernel version 5.4 or higher

### Python Version
- **Python 3.7 or higher** (Python 3.11+ recommended)
- Check version: `python3 --version`

### System Packages
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python development files (if needed)
sudo apt install python3-dev python3-pip -y

# Install GPIO tools
sudo apt install rpi.gpio-common -y
```

---

## Hardware Dependencies

### Required Hardware

#### 1. Raspberry Pi
- **Model**: Raspberry Pi 5 (or Pi 4/3 with 40-pin GPIO)
- **RAM**: 2GB minimum (4GB+ recommended)
- **Storage**: 8GB microSD minimum (16GB+ recommended)

#### 2. Sensors

| Sensor | Model | Interface | Voltage | Notes |
|--------|-------|-----------|---------|-------|
| Temperature | XY-MD02 | RS485/Modbus | 5V | Requires USB adapter |
| Motion | HC-SR501 | Digital GPIO | 5V | 3-7m detection range |
| Vibration | 801S | Digital GPIO | 3.3V | Adjustable sensitivity |
| Sound | LM393 | Digital GPIO | 3.3-5V | Potentiometer adjustable |
| Door | MC-38 | Digital GPIO | 3.3V | Magnetic reed switch |

#### 3. Additional Components
- **USB to RS485 Converter**: For XY-MD02 temperature sensor
- **Jumper Wires**: Female-to-female for GPIO connections
- **Breadboard** (optional): For prototyping
- **Power Supply**: 5V 3A USB-C for Raspberry Pi 5

---

## Installation Methods

### Method 1: Quick Install (Recommended)
```bash
# Navigate to project directory
cd yoshi-smart-pi5-monitoring-kit

# Install all dependencies
pip install -r requirements.txt --break-system-packages
```

### Method 2: Individual Installation
```bash
# Install each package separately
pip install gpiozero --break-system-packages
pip install RPi.GPIO --break-system-packages
pip install minimalmodbus --break-system-packages
pip install pyserial --break-system-packages
```

### Method 3: Virtual Environment (Development)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

---

## Permissions Setup

### GPIO Access
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Add user to dialout group (for USB serial)
sudo usermod -a -G dialout $USER

# Reboot to apply changes
sudo reboot
```

### USB Device Access
```bash
# Check USB devices
ls -l /dev/ttyUSB*

# If permission denied, check groups
groups $USER

# Should include: gpio, dialout
```

---

## Verification

### Check Python Installation
```bash
python3 --version
# Expected: Python 3.7.0 or higher
```

### Check Installed Packages
```bash
pip list | grep -E "gpiozero|RPi.GPIO|minimalmodbus|pyserial"
```

Expected output:
```
gpiozero        2.0.1
minimalmodbus   2.1.1
pyserial        3.5
RPi.GPIO        0.7.1
```

### Test GPIO Access
```bash
# Check GPIO is available
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"

# Check gpiozero
python3 -c "import gpiozero; print('gpiozero OK')"
```

### Test Serial Access
```bash
# List serial ports
python3 -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

---

## Troubleshooting

### Issue: `--break-system-packages` flag required

**Cause**: Raspberry Pi OS Bookworm uses PEP 668 externally managed environments

**Solution**:
```bash
# Option 1: Use flag
pip install package --break-system-packages

# Option 2: Use virtual environment (recommended for dev)
python3 -m venv venv
source venv/bin/activate
pip install package
```

### Issue: Permission denied on GPIO pins

**Solution**:
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### Issue: `/dev/ttyUSB0` not found

**Solution**:
```bash
# Check USB devices
lsusb

# Check serial devices
ls -l /dev/tty*

# Install USB-serial drivers if needed
sudo apt install usb-modeswitch
```

### Issue: Import errors for RPi.GPIO

**Solution**:
```bash
# Reinstall with correct version
pip uninstall RPi.GPIO
pip install RPi.GPIO --break-system-packages
```

### Issue: Modbus communication fails

**Solution**:
```bash
# Check serial port permissions
ls -l /dev/ttyUSB0

# Install serial tools
sudo apt install setserial

# Test with scanner
cd temperature
python md02_scanner.py
```

---

## Version Compatibility

### Tested Configurations

| Component | Version | Status |
|-----------|---------|--------|
| Raspberry Pi OS | Bookworm (12) | ✅ Fully Tested |
| Python | 3.11.2 | ✅ Fully Tested |
| gpiozero | 2.0.1 | ✅ Fully Tested |
| RPi.GPIO | 0.7.1 | ✅ Fully Tested |
| minimalmodbus | 2.1.1 | ✅ Fully Tested |
| pyserial | 3.5 | ✅ Fully Tested |

### Minimum Requirements

| Component | Minimum Version |
|-----------|----------------|
| Python | 3.7.0 |
| gpiozero | 1.6.0 |
| RPi.GPIO | 0.7.0 |
| minimalmodbus | 2.0.0 |
| pyserial | 3.4 |

---

## Development Dependencies (Optional)

For contributing or development:

```bash
# Code formatting
pip install black

# Linting
pip install pylint

# Type checking
pip install mypy

# Testing
pip install pytest
```

---

## Update Instructions

### Update All Packages
```bash
pip install --upgrade -r requirements.txt --break-system-packages
```

### Update Individual Package
```bash
pip install --upgrade gpiozero --break-system-packages
```

### Check for Updates
```bash
pip list --outdated
```

---

## Uninstallation

### Remove All Dependencies
```bash
pip uninstall gpiozero RPi.GPIO minimalmodbus pyserial -y
```

### Remove with System Packages
```bash
sudo apt remove python3-gpiozero python3-rpi.gpio -y
sudo apt autoremove -y
```

---

## Additional Resources

- **gpiozero Recipes**: https://gpiozero.readthedocs.io/en/stable/recipes.html
- **RPi.GPIO Wiki**: https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
- **Modbus Protocol**: https://www.modbus.org/specs.php
- **PySerial Examples**: https://pyserial.readthedocs.io/en/latest/examples.html

---

## Support

For dependency-related issues:
1. Check this documentation
2. Review troubleshooting section
3. Verify hardware connections
4. Check system logs: `dmesg | tail`
5. Open GitHub issue with details

---

**Last Updated**: 2025-12-18  
**Maintainer**: A.R. Ansari
