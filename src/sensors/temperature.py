"""
Temperature and Humidity Sensor Module.

Modbus RTU communication for reading temperature and humidity
from RS485 sensors (e.g., XY-MD02, SHT20-based sensors).

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import time
from typing import Tuple, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None


class DiagnosticCode(Enum):
    """Diagnostic error codes for hardware troubleshooting."""
    OK = "OK"
    NO_PYSERIAL = "NO_PYSERIAL"
    PORT_NOT_FOUND = "PORT_NOT_FOUND"
    NO_RS485_CONVERTER = "NO_RS485_CONVERTER"
    NO_SENSOR_RESPONSE = "NO_SENSOR_RESPONSE"
    AB_LINES_SWAPPED = "AB_LINES_SWAPPED"
    GROUND_NOT_CONNECTED = "GROUND_NOT_CONNECTED"
    CRC_ERROR = "CRC_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    BAUDRATE_MISMATCH = "BAUDRATE_MISMATCH"
    WRONG_SLAVE_ADDRESS = "WRONG_SLAVE_ADDRESS"
    CONNECTION_ERROR = "CONNECTION_ERROR"


@dataclass
class DiagnosticResult:
    """Result of hardware diagnostic check."""
    code: DiagnosticCode
    message: str
    suggestion: str
    raw_data: Optional[bytes] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_ok(self) -> bool:
        return self.code == DiagnosticCode.OK

    def __str__(self) -> str:
        status = "✓ PASS" if self.is_ok else "✗ FAIL"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {status}: {self.message}"


@dataclass
class SensorReading:
    """Data class for sensor readings with timestamp."""
    temperature: float
    humidity: float
    timestamp: datetime

    def __str__(self) -> str:
        return (f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Temperature: {self.temperature:.1f}°C, "
                f"Humidity: {self.humidity:.1f}%RH")

    def is_valid(self) -> bool:
        """Check if reading is within reasonable range."""
        return -40 <= self.temperature <= 80 and 0 <= self.humidity <= 100


def modbus_crc(data: bytes) -> int:
    """
    Compute Modbus RTU CRC16.
    
    Args:
        data: Bytes to compute CRC for
        
    Returns:
        16-bit CRC value
    """
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            lsb = crc & 0x0001
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc


def parse_signed_16(value: int) -> int:
    """Convert unsigned 16-bit to signed 16-bit integer."""
    if value & 0x8000:
        return value - 0x10000
    return value


class TemperatureSensor:
    """
    Modbus RTU Temperature/Humidity Sensor Handler.

    Supports RS485 sensors using function code 0x04 (Read Input Registers).
    Includes comprehensive hardware diagnostics for troubleshooting.
    """

    # Known USB-to-RS485 converter identifiers
    RS485_IDENTIFIERS = [
        "CH340", "CP210", "FTDI", "RS485", "RS-485",
        "USB-RS485", "USB2.0-Serial", "USB Serial"
    ]

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        slave_address: int = 0x01,
        timeout: float = 0.5,
        logger=None
    ):
        """
        Initialize temperature sensor.

        Args:
            port: Serial port path
            baudrate: Communication speed (default 9600)
            slave_address: Modbus slave address (default 0x01)
            timeout: Read timeout in seconds
            logger: Optional logger instance (for testing without colorlog)
        """
        self.port = port
        self.baudrate = baudrate
        self.slave_address = slave_address
        self.timeout = timeout
        self._serial: Optional['serial.Serial'] = None
        self._last_diagnostic: Optional[DiagnosticResult] = None

        # Use provided logger or create default
        if logger:
            self.logger = logger
        else:
            try:
                from src.utils.logger import setup_logger
                self.logger = setup_logger("TemperatureSensor", "logs/sensors.log")
            except ImportError:
                import logging
                self.logger = logging.getLogger("TemperatureSensor")
        
    def connect(self) -> bool:
        """
        Open serial connection to sensor.
        
        Returns:
            True if connection successful, False otherwise
        """
        if serial is None:
            self.logger.error("pyserial not installed. Run: pip install pyserial")
            return False
            
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            self.logger.info(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            self.logger.info("Disconnected from sensor")
    
    def _build_read_request(self, start_addr: int, quantity: int) -> bytes:
        """Build Modbus RTU read input registers request."""
        payload = bytes([
            self.slave_address,
            0x04,  # Function code: Read Input Registers
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF,
        ])
        crc = modbus_crc(payload)
        return payload + bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    
    def read(self) -> Optional[SensorReading]:
        """
        Read temperature and humidity from sensor.
        
        Returns:
            SensorReading with timestamp, or None on error
        """
        if not self._serial or not self._serial.is_open:
            self.logger.error("Serial port not open")
            return None
        
        try:
            request = self._build_read_request(start_addr=0x0001, quantity=2)
            self.logger.debug(f"Request: {request.hex(' ')}")
            
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            self._serial.write(request)
            self._serial.flush()
            
            time.sleep(0.1)
            response = self._serial.read(9)
            timestamp = datetime.now()
            
            self.logger.debug(f"Response: {response.hex(' ')}")
            
            if len(response) != 9:
                raise RuntimeError(f"Invalid response length: {len(response)}")
            
            # Verify header
            addr, func, byte_count = response[0], response[1], response[2]
            if addr != self.slave_address or func != 0x04 or byte_count != 4:
                raise RuntimeError(f"Invalid header: addr={addr}, func={func}")
            
            # CRC check
            crc_recv = response[-2] | (response[-1] << 8)
            crc_calc = modbus_crc(response[:-2])
            if crc_recv != crc_calc:
                raise RuntimeError(f"CRC mismatch: {crc_recv:04X} != {crc_calc:04X}")
            
            # Parse values
            temp_raw = (response[3] << 8) | response[4]
            hum_raw = (response[5] << 8) | response[6]
            
            temperature = parse_signed_16(temp_raw) / 10.0
            humidity = hum_raw / 10.0
            
            reading = SensorReading(temperature, humidity, timestamp)
            self.logger.info(str(reading))
            return reading

        except Exception as e:
            self.logger.error(f"Read error: {e}")
            return None

    # ==================== DIAGNOSTIC METHODS ====================

    def list_serial_ports(self) -> List[dict]:
        """
        List all available serial ports.

        Returns:
            List of port information dictionaries
        """
        if serial is None:
            return []

        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'is_rs485': any(id in port.description.upper()
                               for id in self.RS485_IDENTIFIERS)
            })
        return ports

    def diagnose_connection(self) -> DiagnosticResult:
        """
        Diagnose RS485 converter connection.

        Returns:
            DiagnosticResult with status and suggestions
        """
        timestamp = datetime.now()

        # Check 1: pyserial installed
        if serial is None:
            return DiagnosticResult(
                code=DiagnosticCode.NO_PYSERIAL,
                message="pyserial library not installed",
                suggestion="Run: pip install pyserial",
                timestamp=timestamp
            )

        # Check 2: List available ports
        ports = self.list_serial_ports()
        if not ports:
            return DiagnosticResult(
                code=DiagnosticCode.NO_RS485_CONVERTER,
                message="No serial ports detected",
                suggestion="Check USB connection. Ensure RS485 converter is plugged in.",
                timestamp=timestamp
            )

        # Check 3: Target port exists
        port_devices = [p['device'] for p in ports]
        if self.port not in port_devices:
            available = ', '.join(port_devices)
            return DiagnosticResult(
                code=DiagnosticCode.PORT_NOT_FOUND,
                message=f"Port {self.port} not found",
                suggestion=f"Available ports: {available}. Check USB connection.",
                timestamp=timestamp
            )

        # Check 4: Try to open port
        try:
            test_serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.5
            )
            test_serial.close()
        except serial.SerialException as e:
            return DiagnosticResult(
                code=DiagnosticCode.CONNECTION_ERROR,
                message=f"Cannot open {self.port}: {e}",
                suggestion="Check if port is in use. Try: sudo chmod 666 " + self.port,
                timestamp=timestamp
            )

        return DiagnosticResult(
            code=DiagnosticCode.OK,
            message=f"RS485 converter detected on {self.port}",
            suggestion="Connection OK. Ready for sensor communication.",
            timestamp=timestamp
        )

    def diagnose_sensor_response(self) -> DiagnosticResult:
        """
        Diagnose sensor communication issues.

        Returns:
            DiagnosticResult with detailed error analysis
        """
        timestamp = datetime.now()

        if not self._serial or not self._serial.is_open:
            # Try to connect first
            conn_result = self.diagnose_connection()
            if not conn_result.is_ok:
                return conn_result

            if not self.connect():
                return DiagnosticResult(
                    code=DiagnosticCode.CONNECTION_ERROR,
                    message="Failed to open serial port",
                    suggestion="Check permissions and port availability",
                    timestamp=timestamp
                )

        # Send request and analyze response
        request = self._build_read_request(start_addr=0x0001, quantity=2)

        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()
        self._serial.write(request)
        self._serial.flush()

        time.sleep(0.2)  # Wait longer for diagnosis
        response = self._serial.read(20)  # Read more bytes for analysis

        return self._analyze_response(response, timestamp)

    def _analyze_response(self, response: bytes, timestamp: datetime) -> DiagnosticResult:
        """
        Analyze response bytes to determine issue.

        Args:
            response: Raw bytes received from sensor
            timestamp: Timestamp of the diagnostic

        Returns:
            DiagnosticResult with root cause analysis
        """
        # Case 1: No response at all
        if len(response) == 0:
            return DiagnosticResult(
                code=DiagnosticCode.NO_SENSOR_RESPONSE,
                message="No response from sensor (0 bytes received)",
                suggestion=(
                    "Possible causes:\n"
                    "  1. Sensor not powered (check 12V/24V supply)\n"
                    "  2. A/B lines not connected\n"
                    "  3. Wrong slave address (try 0x01-0x0F)\n"
                    "  4. Baudrate mismatch (try 9600, 4800, 19200)"
                ),
                raw_data=response,
                timestamp=timestamp
            )

        # Case 2: Garbage data - likely ground issue or A/B swap
        if len(response) > 0:
            # Check for all 0xFF or 0x00 (common with ground issues)
            if all(b == 0xFF for b in response):
                return DiagnosticResult(
                    code=DiagnosticCode.GROUND_NOT_CONNECTED,
                    message="All 0xFF received - likely floating input",
                    suggestion=(
                        "GND (Ground) wire not connected!\n"
                        "  1. Connect GND from RS485 converter to sensor GND\n"
                        "  2. Ensure common ground between all devices"
                    ),
                    raw_data=response,
                    timestamp=timestamp
                )

            if all(b == 0x00 for b in response):
                return DiagnosticResult(
                    code=DiagnosticCode.GROUND_NOT_CONNECTED,
                    message="All 0x00 received - possible short circuit",
                    suggestion=(
                        "Check wiring:\n"
                        "  1. A/B lines might be shorted\n"
                        "  2. Check for damaged cables"
                    ),
                    raw_data=response,
                    timestamp=timestamp
                )

            # Check for random/garbage pattern
            unique_bytes = len(set(response))
            if unique_bytes > 6 and len(response) < 9:
                return DiagnosticResult(
                    code=DiagnosticCode.AB_LINES_SWAPPED,
                    message=f"Garbage data received ({len(response)} bytes, {unique_bytes} unique)",
                    suggestion=(
                        "A and B signal lines likely SWAPPED!\n"
                        "  1. Swap A and B wires at the RS485 converter\n"
                        "  2. A+ connects to A+, B- connects to B-\n"
                        "  3. Some devices label differently: A=D+, B=D-"
                    ),
                    raw_data=response,
                    timestamp=timestamp
                )

        # Case 3: Got some data, check validity
        if len(response) >= 9:
            addr, func = response[0], response[1]

            # Wrong slave address
            if addr != self.slave_address:
                return DiagnosticResult(
                    code=DiagnosticCode.WRONG_SLAVE_ADDRESS,
                    message=f"Response from different slave: got 0x{addr:02X}, expected 0x{self.slave_address:02X}",
                    suggestion=f"Change slave_address to 0x{addr:02X} or reconfigure sensor",
                    raw_data=response,
                    timestamp=timestamp
                )

            # Modbus exception response
            if func == 0x84:  # Exception for function 0x04
                exc_code = response[2] if len(response) > 2 else 0
                exc_msgs = {
                    1: "Illegal function",
                    2: "Illegal data address",
                    3: "Illegal data value",
                    4: "Slave device failure"
                }
                return DiagnosticResult(
                    code=DiagnosticCode.INVALID_RESPONSE,
                    message=f"Modbus exception: {exc_msgs.get(exc_code, 'Unknown')}",
                    suggestion="Check register addresses and sensor documentation",
                    raw_data=response,
                    timestamp=timestamp
                )

            # CRC check
            crc_recv = response[7] | (response[8] << 8)
            crc_calc = modbus_crc(response[:7])
            if crc_recv != crc_calc:
                return DiagnosticResult(
                    code=DiagnosticCode.CRC_ERROR,
                    message=f"CRC mismatch: recv=0x{crc_recv:04X}, calc=0x{crc_calc:04X}",
                    suggestion=(
                        "Data corruption detected:\n"
                        "  1. Check cable length (max 1200m for RS485)\n"
                        "  2. Add termination resistor (120Ω) for long cables\n"
                        "  3. Check for electrical interference"
                    ),
                    raw_data=response,
                    timestamp=timestamp
                )

            # Valid response!
            return DiagnosticResult(
                code=DiagnosticCode.OK,
                message="Valid response received from sensor",
                suggestion="Sensor communication working correctly",
                raw_data=response,
                timestamp=timestamp
            )

        # Case 4: Partial response
        return DiagnosticResult(
            code=DiagnosticCode.INVALID_RESPONSE,
            message=f"Incomplete response: {len(response)} bytes (expected 9)",
            suggestion=(
                "Partial data received:\n"
                "  1. Try increasing timeout\n"
                "  2. Check baudrate setting\n"
                "  3. Sensor may be slow to respond"
            ),
            raw_data=response,
            timestamp=timestamp
        )

    def run_full_diagnostic(self) -> List[DiagnosticResult]:
        """
        Run complete diagnostic suite.

        Returns:
            List of all diagnostic results
        """
        results = []

        # Step 1: Connection diagnostic
        self.logger.info("=" * 50)
        self.logger.info("Running RS485 Temperature Sensor Diagnostics")
        self.logger.info("=" * 50)

        conn_result = self.diagnose_connection()
        results.append(conn_result)
        self.logger.info(str(conn_result))

        if not conn_result.is_ok:
            return results

        # Step 2: Sensor response diagnostic
        if not self._serial or not self._serial.is_open:
            self.connect()

        sensor_result = self.diagnose_sensor_response()
        results.append(sensor_result)
        self.logger.info(str(sensor_result))

        if sensor_result.raw_data:
            self.logger.info(f"Raw data: {sensor_result.raw_data.hex(' ')}")

        # Step 3: If OK, try actual reading
        if sensor_result.is_ok:
            reading = self.read()
            if reading:
                if reading.is_valid():
                    results.append(DiagnosticResult(
                        code=DiagnosticCode.OK,
                        message=f"Reading valid: {reading.temperature}°C, {reading.humidity}%RH",
                        suggestion="Sensor fully operational"
                    ))
                else:
                    results.append(DiagnosticResult(
                        code=DiagnosticCode.INVALID_RESPONSE,
                        message=f"Reading out of range: {reading.temperature}°C, {reading.humidity}%RH",
                        suggestion="Sensor may need calibration or replacement"
                    ))

        self.logger.info("=" * 50)
        self.logger.info(f"Diagnostic complete: {sum(1 for r in results if r.is_ok)}/{len(results)} passed")
        self.logger.info("=" * 50)

        return results

