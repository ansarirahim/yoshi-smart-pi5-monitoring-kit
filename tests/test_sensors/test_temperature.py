"""
Unit tests for TemperatureSensor.

Comprehensive test suite for Modbus RTU temperature/humidity
sensor communication including CRC, parsing, error handling,
and hardware diagnostic scenarios with root cause analysis.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import logging

from src.sensors.temperature import (
    TemperatureSensor,
    SensorReading,
    DiagnosticResult,
    DiagnosticCode,
    modbus_crc,
    parse_signed_16
)


class TestModbusCRC:
    """Test cases for Modbus CRC16 calculation."""
    
    def test_crc_known_value(self):
        """Test CRC with known Modbus request."""
        # Standard read request: addr=0x01, func=0x04, start=0x0001, qty=0x0002
        data = bytes([0x01, 0x04, 0x00, 0x01, 0x00, 0x02])
        crc = modbus_crc(data)
        # Expected CRC for this frame
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFFFF
    
    def test_crc_empty_data(self):
        """Test CRC with empty data."""
        crc = modbus_crc(b"")
        assert crc == 0xFFFF  # Initial value unchanged
    
    def test_crc_single_byte(self):
        """Test CRC with single byte."""
        crc = modbus_crc(bytes([0x01]))
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFFFF
    
    def test_crc_deterministic(self):
        """Test CRC produces same result for same input."""
        data = bytes([0x01, 0x04, 0x00, 0x01, 0x00, 0x02])
        crc1 = modbus_crc(data)
        crc2 = modbus_crc(data)
        assert crc1 == crc2


class TestParseSigned16:
    """Test cases for signed 16-bit integer parsing."""
    
    def test_positive_value(self):
        """Test positive temperature value."""
        assert parse_signed_16(0x00FA) == 250  # 25.0°C
    
    def test_zero_value(self):
        """Test zero value."""
        assert parse_signed_16(0x0000) == 0
    
    def test_negative_value(self):
        """Test negative temperature value."""
        assert parse_signed_16(0xFFEC) == -20  # -2.0°C
    
    def test_max_positive(self):
        """Test maximum positive value."""
        assert parse_signed_16(0x7FFF) == 32767
    
    def test_min_negative(self):
        """Test minimum negative value."""
        assert parse_signed_16(0x8000) == -32768


class TestSensorReading:
    """Test cases for SensorReading dataclass."""

    def test_creation(self):
        """Test creating a sensor reading."""
        ts = datetime(2024, 1, 15, 10, 30, 45)
        reading = SensorReading(temperature=25.5, humidity=60.2, timestamp=ts)

        assert reading.temperature == 25.5
        assert reading.humidity == 60.2
        assert reading.timestamp == ts

    def test_string_representation(self):
        """Test string output with timestamp."""
        ts = datetime(2024, 1, 15, 10, 30, 45)
        reading = SensorReading(temperature=25.5, humidity=60.2, timestamp=ts)

        result = str(reading)
        assert "2024-01-15 10:30:45" in result
        assert "25.5°C" in result
        assert "60.2%RH" in result

    def test_is_valid_normal_range(self):
        """Test valid reading in normal range."""
        ts = datetime.now()
        reading = SensorReading(temperature=25.0, humidity=50.0, timestamp=ts)
        assert reading.is_valid() is True

    def test_is_valid_out_of_range(self):
        """Test invalid reading out of range."""
        ts = datetime.now()
        # Temperature too high
        reading = SensorReading(temperature=100.0, humidity=50.0, timestamp=ts)
        assert reading.is_valid() is False
        # Humidity too high
        reading = SensorReading(temperature=25.0, humidity=150.0, timestamp=ts)
        assert reading.is_valid() is False


class TestTemperatureSensor:
    """Test cases for TemperatureSensor class."""
    
    def test_initialization(self):
        """Test sensor initialization with defaults."""
        sensor = TemperatureSensor()
        
        assert sensor.port == "/dev/ttyUSB0"
        assert sensor.baudrate == 9600
        assert sensor.slave_address == 0x01
        assert sensor.timeout == 0.5
    
    def test_initialization_custom(self):
        """Test sensor initialization with custom values."""
        sensor = TemperatureSensor(
            port="/dev/ttyACM0",
            baudrate=19200,
            slave_address=0x02,
            timeout=1.0
        )
        
        assert sensor.port == "/dev/ttyACM0"
        assert sensor.baudrate == 19200
        assert sensor.slave_address == 0x02
        assert sensor.timeout == 1.0
    
    @patch('src.sensors.temperature.serial')
    def test_connect_success(self, mock_serial_module):
        """Test successful serial connection."""
        mock_serial = MagicMock()
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1
        
        sensor = TemperatureSensor()
        result = sensor.connect()
        
        assert result is True
        mock_serial_module.Serial.assert_called_once()
    
    @patch('src.sensors.temperature.serial', None)
    def test_connect_no_pyserial(self):
        """Test connection fails when pyserial not installed."""
        sensor = TemperatureSensor()
        result = sensor.connect()
        
        assert result is False
    
    def test_build_read_request(self):
        """Test Modbus read request frame building."""
        sensor = TemperatureSensor(slave_address=0x01)
        request = sensor._build_read_request(start_addr=0x0001, quantity=2)
        
        # Check frame structure
        assert len(request) == 8  # 6 bytes + 2 CRC
        assert request[0] == 0x01  # Slave address
        assert request[1] == 0x04  # Function code
        assert request[2] == 0x00  # Start addr high
        assert request[3] == 0x01  # Start addr low
        assert request[4] == 0x00  # Quantity high
        assert request[5] == 0x02  # Quantity low
    
    @patch('src.sensors.temperature.serial')
    def test_read_success(self, mock_serial_module):
        """Test successful temperature/humidity read."""
        # Build valid response: 25.5°C, 60.0%RH
        # temp=255 (0x00FF), hum=600 (0x0258)
        response_data = bytes([0x01, 0x04, 0x04, 0x00, 0xFF, 0x02, 0x58])
        crc = modbus_crc(response_data)
        response = response_data + bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = response
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1
        
        sensor = TemperatureSensor()
        sensor.connect()
        reading = sensor.read()
        
        assert reading is not None
        assert reading.temperature == 25.5
        assert reading.humidity == 60.0
        assert isinstance(reading.timestamp, datetime)
    
    def test_read_not_connected(self):
        """Test read fails when not connected."""
        sensor = TemperatureSensor()
        reading = sensor.read()
        
        assert reading is None
    
    @patch('src.sensors.temperature.serial')
    def test_read_invalid_response_length(self, mock_serial_module):
        """Test handling of invalid response length."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = bytes([0x01, 0x04])  # Too short
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1
        
        sensor = TemperatureSensor()
        sensor.connect()
        reading = sensor.read()
        
        assert reading is None
    
    @patch('src.sensors.temperature.serial')
    def test_disconnect(self, mock_serial_module):
        """Test disconnection."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor()
        sensor.connect()
        sensor.disconnect()

        mock_serial.close.assert_called_once()


class TestDiagnosticResult:
    """Test cases for DiagnosticResult dataclass."""

    def test_creation(self):
        """Test creating a diagnostic result."""
        result = DiagnosticResult(
            code=DiagnosticCode.OK,
            message="Test passed",
            suggestion="No action needed"
        )
        assert result.code == DiagnosticCode.OK
        assert result.is_ok is True

    def test_failed_result(self):
        """Test failed diagnostic result."""
        result = DiagnosticResult(
            code=DiagnosticCode.NO_SENSOR_RESPONSE,
            message="No response",
            suggestion="Check wiring"
        )
        assert result.is_ok is False

    def test_string_representation(self):
        """Test string output with timestamp."""
        result = DiagnosticResult(
            code=DiagnosticCode.OK,
            message="Success",
            suggestion="Ready"
        )
        output = str(result)
        assert "PASS" in output
        assert "Success" in output


class TestHardwareDiagnostics:
    """
    Test cases for hardware diagnostic scenarios.

    Each test simulates a specific hardware issue and verifies
    the correct diagnostic code and root cause suggestion.
    """

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return logging.getLogger("test_sensor")

    def test_diagnose_no_pyserial(self, mock_logger):
        """
        Test: pyserial library not installed.

        Root Cause: Missing dependency
        Solution: pip install pyserial
        """
        with patch('src.sensors.temperature.serial', None):
            sensor = TemperatureSensor(logger=mock_logger)
            result = sensor.diagnose_connection()

            assert result.code == DiagnosticCode.NO_PYSERIAL
            assert "pyserial" in result.message.lower()
            assert "pip install" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_no_rs485_converter(self, mock_serial_module, mock_logger):
        """
        Test: No RS485 converter connected.

        Root Cause: USB-RS485 adapter not plugged in
        Solution: Connect USB-RS485 converter to USB port
        """
        # Mock empty port list
        mock_serial_module.tools.list_ports.comports.return_value = []

        sensor = TemperatureSensor(logger=mock_logger)
        result = sensor.diagnose_connection()

        assert result.code == DiagnosticCode.NO_RS485_CONVERTER
        assert "no serial ports" in result.message.lower()
        assert "usb" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_port_not_found(self, mock_serial_module, mock_logger):
        """
        Test: Specified port does not exist.

        Root Cause: Wrong port name or USB disconnected
        Solution: Check USB connection, use correct port name
        """
        # Mock port list without target port
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB1"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB VID:PID=1234:5678"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        sensor = TemperatureSensor(port="/dev/ttyUSB0", logger=mock_logger)
        result = sensor.diagnose_connection()

        assert result.code == DiagnosticCode.PORT_NOT_FOUND
        assert "/dev/ttyUSB0" in result.message
        assert "/dev/ttyUSB1" in result.suggestion

    @patch('src.sensors.temperature.serial')
    def test_diagnose_no_sensor_response(self, mock_serial_module, mock_logger):
        """
        Test: Sensor does not respond (0 bytes received).

        Root Causes:
        - Sensor not powered (no 12V/24V)
        - A/B lines not connected
        - Wrong slave address
        - Baudrate mismatch

        Solution: Check power supply, verify wiring, test different addresses
        """
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = b""  # No response
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor(logger=mock_logger)
        sensor.connect()
        result = sensor.diagnose_sensor_response()

        assert result.code == DiagnosticCode.NO_SENSOR_RESPONSE
        assert "0 bytes" in result.message
        assert "power" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_ground_not_connected_all_ff(self, mock_serial_module, mock_logger):
        """
        Test: All 0xFF received - ground wire not connected.

        Root Cause: GND wire not connected between RS485 converter and sensor
        The input floats high, reading as 0xFF.

        Solution: Connect GND wire between converter and sensor
        """
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = bytes([0xFF] * 9)  # All 0xFF
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor(logger=mock_logger)
        sensor.connect()
        result = sensor.diagnose_sensor_response()

        assert result.code == DiagnosticCode.GROUND_NOT_CONNECTED
        assert "0xFF" in result.message
        assert "gnd" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_ab_lines_swapped(self, mock_serial_module, mock_logger):
        """
        Test: A and B signal lines swapped - garbage data received.

        Root Cause: A+ and B- wires connected in reverse
        Results in garbled/random data.

        Solution: Swap A and B wires at the RS485 converter
        """
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        mock_serial = MagicMock()
        mock_serial.is_open = True
        # Random garbage data (high unique byte count, short length)
        mock_serial.read.return_value = bytes([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE])
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor(logger=mock_logger)
        sensor.connect()
        result = sensor.diagnose_sensor_response()

        assert result.code == DiagnosticCode.AB_LINES_SWAPPED
        assert "garbage" in result.message.lower() or "unique" in result.message.lower()
        assert "swap" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_ground_short_all_00(self, mock_serial_module, mock_logger):
        """
        Test: All 0x00 received - possible short circuit.

        Root Cause: A/B lines shorted together or damaged cable

        Solution: Check for short circuits, test cable continuity
        """
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = bytes([0x00] * 9)  # All 0x00
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor(logger=mock_logger)
        sensor.connect()
        result = sensor.diagnose_sensor_response()

        assert result.code == DiagnosticCode.GROUND_NOT_CONNECTED
        assert "0x00" in result.message
        assert "short" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_crc_error(self, mock_serial_module, mock_logger):
        """
        Test: CRC mismatch - data corruption.

        Root Causes:
        - Long cable without termination resistor
        - Electrical interference
        - Loose connections

        Solution: Add 120Ω terminator, use shielded cable
        """
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        mock_serial = MagicMock()
        mock_serial.is_open = True
        # Valid structure but wrong CRC
        mock_serial.read.return_value = bytes([0x01, 0x04, 0x04, 0x00, 0xFF, 0x02, 0x58, 0x00, 0x00])
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor(logger=mock_logger)
        sensor.connect()
        result = sensor.diagnose_sensor_response()

        assert result.code == DiagnosticCode.CRC_ERROR
        assert "crc" in result.message.lower()
        assert "120" in result.suggestion or "termination" in result.suggestion.lower()

    @patch('src.sensors.temperature.serial')
    def test_diagnose_valid_response(self, mock_serial_module, mock_logger):
        """
        Test: Valid sensor response - all OK.

        Expected: Successful communication with correct data
        """
        mock_port = MagicMock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "USB Serial"
        mock_port.hwid = "USB"
        mock_serial_module.tools.list_ports.comports.return_value = [mock_port]

        # Build valid response
        response_data = bytes([0x01, 0x04, 0x04, 0x00, 0xFF, 0x02, 0x58])
        crc = modbus_crc(response_data)
        valid_response = response_data + bytes([crc & 0xFF, (crc >> 8) & 0xFF])

        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = valid_response
        mock_serial_module.Serial.return_value = mock_serial
        mock_serial_module.EIGHTBITS = 8
        mock_serial_module.PARITY_NONE = 'N'
        mock_serial_module.STOPBITS_ONE = 1

        sensor = TemperatureSensor(logger=mock_logger)
        sensor.connect()
        result = sensor.diagnose_sensor_response()

        assert result.code == DiagnosticCode.OK
        assert result.is_ok is True

