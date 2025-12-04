#!/usr/bin/env python3
"""
801S Vibration Shock Sensor Module for Raspberry Pi.

This module provides an interface for the 801S vibration/shock sensor
with LM393 comparator IC. The sensor detects vibration and outputs
a digital HIGH signal when threshold is exceeded.

Specifications:
    - Model: 801S Vibration Shock Sensor
    - Operating Voltage: 3.3V - 5V DC (Use 3.3V for Raspberry Pi!)
    - Output Type: Digital (D0) - HIGH when vibration detected
    - Sensitivity: Adjustable via onboard potentiometer
    - Durability: 60 million shocks (gold-plated contacts)
    - Detection: Omnidirectional (no specific direction)
    - Comparator: LM393 IC

Wiring to Raspberry Pi 5 (4GB) with polarity:
    [+] VCC (Power)  -> Orange wire -> Pin 1 (3.3V) !! NOT 5V !!
    [S] D0  (Signal) -> Gray wire   -> Pin 13 (GPIO27)
    [-] GND (Ground) -> Black wire  -> Pin 6 (GND)

Note: GPIO17 is reserved for PIR Motion Sensor. Use GPIO27 for vibration.

!! WARNING: Use 3.3V for VCC to ensure safe GPIO voltage levels.

Behavior:
    - No vibration: Output LOW, LED ON
    - Vibration detected: Output HIGH, LED OFF
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional, List
import time

try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False


class VibrationState(Enum):
    """Vibration detection states."""
    NO_VIBRATION = 0
    VIBRATION_DETECTED = 1


@dataclass
class VibrationEvent:
    """Represents a vibration detection event."""
    state: VibrationState
    timestamp: datetime = field(default_factory=datetime.now)
    intensity: int = 0  # 0-100 based on duration/frequency
    duration_ms: float = 0.0

    def __str__(self) -> str:
        if self.state == VibrationState.VIBRATION_DETECTED:
            return f"[{self.timestamp.strftime('%H:%M:%S')}] VIBRATION! intensity={self.intensity}%"
        return f"[{self.timestamp.strftime('%H:%M:%S')}] No vibration"


@dataclass
class VibrationConfig:
    """Configuration for vibration sensor."""
    gpio_pin: int = 27  # Default GPIO27 (GPIO17 is used by PIR sensor)
    sample_rate_hz: int = 100  # Samples per second for intensity calc
    debounce_ms: int = 50
    min_event_gap_ms: int = 100

    def __post_init__(self):
        if not 0 <= self.gpio_pin <= 27:
            raise ValueError(f"Invalid GPIO pin: {self.gpio_pin}")


class VibrationSensor:
    """
    801S Vibration Shock Sensor interface for Raspberry Pi.

    The sensor uses an LM393 comparator to convert analog vibration
    to digital output. When vibration exceeds the threshold set by
    the potentiometer, output goes HIGH.

    Wiring to Raspberry Pi 5 (4GB):
    - [+] VCC (Power)  -> Pin 1 (3.3V) !! NOT 5V !!
    - [S] D0  (Signal) -> Pin 13 (GPIO27)
    - [-] GND (Ground) -> Pin 6 (GND)

    Note: GPIO17 is reserved for PIR Motion Sensor.

    Adjustments:
    - Sensitivity Potentiometer: Turn to adjust detection threshold
    """

    def __init__(
        self,
        gpio_pin: int = 17,
        debounce_ms: int = 50,
        callback: Optional[Callable[[VibrationEvent], None]] = None,
        logger=None
    ):
        """
        Initialize the vibration sensor.

        Args:
            gpio_pin: BCM GPIO pin number (default: 17)
            debounce_ms: Debounce time in milliseconds
            callback: Optional callback for vibration events
            logger: Optional logger instance
        """
        self.config = VibrationConfig(gpio_pin=gpio_pin, debounce_ms=debounce_ms)
        self.callback = callback
        self.logger = logger
        self._initialized = False
        self._last_event_time = 0
        self._event_count = 0
        self._events: List[VibrationEvent] = []

    def initialize(self) -> bool:
        """Initialize GPIO for vibration sensor."""
        if not RPI_AVAILABLE:
            if self.logger:
                self.logger.warning("RPi.GPIO not available")
            return False

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.config.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self._initialized = True
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"GPIO init failed: {e}")
            return False

    def is_vibration_detected(self) -> bool:
        """Check if vibration is currently detected."""
        if not self._initialized:
            return False
        return GPIO.input(self.config.gpio_pin) == GPIO.HIGH

    def read_state(self) -> VibrationState:
        """Read current vibration state."""
        if self.is_vibration_detected():
            return VibrationState.VIBRATION_DETECTED
        return VibrationState.NO_VIBRATION

    def wait_for_vibration(self, timeout_sec: float = 10.0) -> Optional[VibrationEvent]:
        """Wait for vibration event with timeout."""
        if not self._initialized:
            return None

        start = time.time()
        while (time.time() - start) < timeout_sec:
            if self.is_vibration_detected():
                event = VibrationEvent(
                    state=VibrationState.VIBRATION_DETECTED,
                    timestamp=datetime.now()
                )
                self._events.append(event)
                self._event_count += 1
                if self.callback:
                    self.callback(event)
                return event
            time.sleep(0.01)
        return None

    def start_monitoring(self, duration_sec: float = 60.0) -> List[VibrationEvent]:
        """Monitor vibration for specified duration."""
        if not self._initialized:
            return []

        events = []
        start = time.time()
        last_state = VibrationState.NO_VIBRATION
        vibration_start = None

        while (time.time() - start) < duration_sec:
            current = self.read_state()
            now = time.time()

            # Detect rising edge (vibration started)
            if current == VibrationState.VIBRATION_DETECTED and last_state == VibrationState.NO_VIBRATION:
                vibration_start = now

            # Detect falling edge (vibration ended)
            elif current == VibrationState.NO_VIBRATION and last_state == VibrationState.VIBRATION_DETECTED:
                if vibration_start:
                    duration_ms = (now - vibration_start) * 1000
                    event = VibrationEvent(
                        state=VibrationState.VIBRATION_DETECTED,
                        timestamp=datetime.now(),
                        duration_ms=duration_ms,
                        intensity=min(100, int(duration_ms / 10))
                    )
                    events.append(event)
                    self._events.append(event)
                    if self.callback:
                        self.callback(event)

            last_state = current
            time.sleep(0.01)

        return events

    def get_event_count(self) -> int:
        """Return total vibration events detected."""
        return self._event_count

    def get_recent_events(self, count: int = 10) -> List[VibrationEvent]:
        """Get most recent vibration events."""
        return self._events[-count:] if self._events else []

    def cleanup(self) -> None:
        """Release GPIO resources."""
        if self._initialized and RPI_AVAILABLE:
            try:
                GPIO.cleanup(self.config.gpio_pin)
            except Exception:
                pass
            self._initialized = False

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False

    @staticmethod
    def get_wiring_diagram() -> str:
        """Return ASCII wiring diagram for 801S to Raspberry Pi 5."""
        return """
+=====================================================================+
|       801S Vibration Sensor Wiring - Raspberry Pi 5 (4GB)           |
+=====================================================================+
|  !! WARNING: Use 3.3V for VCC to ensure safe GPIO voltage levels!   |
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
|   |   o     o     o   |            |  3.3V(17)o o (18)    |         |
|   +---+-----+-----+---+            +----------------------+         |
|       |     |     |                              |                  |
|       |     |     +-- [+] Orange ------> 3.3V (Pin 1)               |
|       |     +-------- [S] Gray --------> GPIO27 (Pin 13)            |
|       +-------------- [-] Black -------> GND (Pin 6)                |
|                                                                     |
+=====================================================================+
|  POLARITY: [+] Orange=VCC(3.3V)  [S] Gray=D0  [-] Black=GND         |
|  Sensitivity: Adjust potentiometer for detection threshold          |
|  Output: HIGH when vibration detected, LED turns OFF                |
|  Durability: 60 million shocks (gold-plated)                        |
+=====================================================================+
"""

