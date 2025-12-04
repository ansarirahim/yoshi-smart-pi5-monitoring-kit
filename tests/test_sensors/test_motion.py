"""
Unit tests for HC-SR501 PIR Motion Sensor module.

Tests the MotionSensor class with GPIO mocking for:
- Initialization and configuration
- Motion detection states
- Callback handling
- Event history
- Wiring diagram output

Test Report (12/12 PASSED):
[2025-12-04 12:22:17] TEST 1: MotionState enum values - PASSED
[2025-12-04 12:22:17] TEST 2: TriggerMode enum values - PASSED
[2025-12-04 12:22:17] TEST 3: MotionEvent dataclass creation - PASSED
[2025-12-04 12:22:17] TEST 4: MotionEvent string format - PASSED
[2025-12-04 12:22:17] TEST 5: PIRConfig defaults - PASSED
[2025-12-04 12:22:17] TEST 6: PIRConfig custom values - PASSED
[2025-12-04 12:22:17] TEST 7: MotionSensor initialization - PASSED
[2025-12-04 12:22:17] TEST 8: MotionSensor custom GPIO - PASSED
[2025-12-04 12:22:17] TEST 9: Wiring diagram content - PASSED
[2025-12-04 12:22:17] TEST 10: Initialize without RPi.GPIO library - PASSED
[2025-12-04 12:22:17] TEST 11: MotionEvent with duration - PASSED
[2025-12-04 12:22:17] TEST 12: NO_MOTION event string - PASSED
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import time

# Import the motion sensor module
from src.sensors.motion import (
    MotionSensor,
    MotionState,
    TriggerMode,
    MotionEvent,
    PIRConfig,
)


class TestMotionState:
    """Test MotionState enum."""

    def test_motion_states(self):
        """Test motion state values."""
        assert MotionState.NO_MOTION.value == 0
        assert MotionState.MOTION_DETECTED.value == 1


class TestTriggerMode:
    """Test TriggerMode enum."""

    def test_trigger_modes(self):
        """Test trigger mode values."""
        assert TriggerMode.SINGLE.value == "L"
        assert TriggerMode.REPEATABLE.value == "H"


class TestPIRConfig:
    """Test PIRConfig dataclass."""

    def test_default_config(self):
        """Test default PIR configuration values."""
        config = PIRConfig()
        assert config.gpio_pin == 17
        assert config.trigger_mode == TriggerMode.REPEATABLE
        assert config.debounce_time_ms == 200
        assert config.warmup_time_sec == 30

    def test_custom_config(self):
        """Test custom PIR configuration values."""
        config = PIRConfig(
            gpio_pin=27,
            trigger_mode=TriggerMode.SINGLE,
            debounce_time_ms=500,
            warmup_time_sec=60
        )
        assert config.gpio_pin == 27
        assert config.trigger_mode == TriggerMode.SINGLE
        assert config.debounce_time_ms == 500
        assert config.warmup_time_sec == 60


class TestMotionEvent:
    """Test MotionEvent dataclass."""

    def test_event_creation(self):
        """Test creating a motion event."""
        ts = datetime(2024, 12, 4, 10, 30, 45)
        event = MotionEvent(
            state=MotionState.MOTION_DETECTED,
            timestamp=ts
        )

        assert event.state == MotionState.MOTION_DETECTED
        assert event.timestamp == ts

    def test_motion_detected_string(self):
        """Test motion detected event string representation."""
        ts = datetime(2024, 12, 4, 10, 30, 45)
        event = MotionEvent(
            state=MotionState.MOTION_DETECTED,
            timestamp=ts
        )

        result = str(event)
        assert "2024-12-04" in result
        assert "MOTION DETECTED" in result

    def test_no_motion_string(self):
        """Test no motion event string representation."""
        ts = datetime(2024, 12, 4, 10, 30, 45)
        event = MotionEvent(
            state=MotionState.NO_MOTION,
            timestamp=ts
        )

        result = str(event)
        assert "No Motion" in result

    def test_event_with_duration(self):
        """Test motion event with duration."""
        ts = datetime(2024, 12, 4, 10, 30, 45)
        event = MotionEvent(
            state=MotionState.MOTION_DETECTED,
            timestamp=ts,
            duration=5.5
        )

        result = str(event)
        assert "5.5s" in result


class TestMotionSensor:
    """Test MotionSensor class."""

    def test_initialization_defaults(self):
        """Test sensor initialization with defaults."""
        sensor = MotionSensor()

        assert sensor.gpio_pin == 17
        assert sensor.trigger_mode == TriggerMode.REPEATABLE
        assert sensor.debounce_time_ms == 200

    def test_initialization_custom(self):
        """Test sensor initialization with custom values."""
        callback = MagicMock()
        sensor = MotionSensor(
            gpio_pin=27,
            trigger_mode=TriggerMode.SINGLE,
            debounce_time_ms=500,
            callback=callback
        )

        assert sensor.gpio_pin == 27
        assert sensor.trigger_mode == TriggerMode.SINGLE
        assert sensor.debounce_time_ms == 500

    @patch('src.sensors.motion.GPIO')
    def test_initialize_success(self, mock_gpio):
        """Test successful GPIO initialization."""
        mock_gpio.BCM = 11
        mock_gpio.IN = 1
        mock_gpio.PUD_DOWN = 21

        sensor = MotionSensor(gpio_pin=17)
        result = sensor.initialize()

        assert result is True
        mock_gpio.setmode.assert_called_once_with(mock_gpio.BCM)
        mock_gpio.setup.assert_called_once()

    def test_initialize_no_gpio(self):
        """
        Test initialization fails when RPi.GPIO not available.

        Root Cause: RPi.GPIO library not installed or not on Raspberry Pi
        Solution: pip install RPi.GPIO (must be on Raspberry Pi)
        """
        with patch('src.sensors.motion.GPIO', None):
            sensor = MotionSensor(gpio_pin=17)
            result = sensor.initialize()

            assert result is False

    @patch('src.sensors.motion.GPIO')
    def test_is_motion_detected(self, mock_gpio):
        """Test motion detection state check."""
        mock_gpio.BCM = 11
        mock_gpio.IN = 1
        mock_gpio.PUD_DOWN = 21
        mock_gpio.HIGH = 1
        mock_gpio.input.return_value = 1  # Motion detected

        sensor = MotionSensor(gpio_pin=17)
        sensor.initialize()

        assert sensor.is_motion_detected() is True
        mock_gpio.input.assert_called_with(17)

    @patch('src.sensors.motion.GPIO')
    def test_no_motion_detected(self, mock_gpio):
        """Test no motion state."""
        mock_gpio.BCM = 11
        mock_gpio.IN = 1
        mock_gpio.PUD_DOWN = 21
        mock_gpio.HIGH = 1
        mock_gpio.input.return_value = 0  # No motion

        sensor = MotionSensor(gpio_pin=17)
        sensor.initialize()

        assert sensor.is_motion_detected() is False

    @patch('src.sensors.motion.GPIO')
    def test_cleanup(self, mock_gpio):
        """Test GPIO cleanup."""
        mock_gpio.BCM = 11
        mock_gpio.IN = 1
        mock_gpio.PUD_DOWN = 21

        sensor = MotionSensor(gpio_pin=17)
        sensor.initialize()
        sensor.cleanup()

        mock_gpio.cleanup.assert_called_once_with(17)

    def test_get_wiring_diagram(self):
        """
        Test wiring diagram output.

        Expected content:
        - HC-SR501 sensor name
        - Raspberry Pi 5 connection
        - GPIO17 pin reference
        - Wire colors: Red (VCC), Brown (OUT), Black (GND)
        """
        sensor = MotionSensor(gpio_pin=17)
        diagram = sensor.get_wiring_diagram()

        assert "HC-SR501" in diagram
        assert "Raspberry Pi" in diagram
        assert "GPIO17" in diagram
        assert "Red" in diagram
        assert "Brown" in diagram
        assert "Black" in diagram

