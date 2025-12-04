#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MC-38 Magnetic Door/Window Sensor Module for Raspberry Pi.

@file       door.py
@brief      GPIO-based door/window state detection using magnetic reed switch.
@details    Provides interface for MC-38 wired magnetic reed switch sensor.
            Detects door/window open/close states using magnet and reed switch.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.

@hardware   MC-38 Wired Door Window Sensor (Reed Switch)
@interface  GPIO23 (BCM) / Pin 16
@type       Normally Closed (NC) Reed Switch

@specifications
    - Model: MC-38 Wired Door Window Sensor
    - Type: Reed Switch (Normally Closed - NC)
    - Operation: Magnet near = CLOSED, Magnet away = OPEN
    - No electronics - just a simple switch
    - No polarity - either wire to GPIO or GND
    - Safe for GPIO - no voltage output

@wiring
    - Wire 1 (White) -> Pin 16 (GPIO23)
    - Wire 2 (White) -> Pin 6 (GND)
    - No polarity required - wires are interchangeable

@logic (NC type with internal pull-up)
    - Door CLOSED (magnet near): Switch CLOSED -> GPIO reads LOW (0)
    - Door OPENED (magnet away): Switch OPEN   -> GPIO reads HIGH (1)

@note GPIO17 = PIR, GPIO22 = Sound, GPIO27 = Vibration. Door uses GPIO23.

@dependencies
    - RPi.GPIO >= 0.7.0

@usage
    >>> from src.sensors.door import DoorSensor
    >>> sensor = DoorSensor(gpio_pin=23)
    >>> sensor.initialize()
    >>> if sensor.is_door_open():
    ...     print("Door is open!")
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


class DoorState(Enum):
    """Door/window states."""
    CLOSED = 0
    OPEN = 1


@dataclass
class DoorEvent:
    """Represents a door state change event."""
    state: DoorState
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        status = "OPENED" if self.state == DoorState.OPEN else "CLOSED"
        return f"[{self.timestamp.strftime('%H:%M:%S')}] Door {status}"


@dataclass
class DoorConfig:
    """Configuration for door sensor."""
    gpio_pin: int = 23  # Default GPIO23 (avoids PIR/Sound/Vibration)
    debounce_ms: int = 50

    def __post_init__(self):
        if not 0 <= self.gpio_pin <= 27:
            raise ValueError(f"Invalid GPIO pin: {self.gpio_pin}")
        # Check for known conflicts
        if self.gpio_pin == 17:
            raise ValueError("GPIO17 is reserved for PIR Motion Sensor")
        if self.gpio_pin == 22:
            raise ValueError("GPIO22 is reserved for Sound Sensor")
        if self.gpio_pin == 27:
            raise ValueError("GPIO27 is reserved for Vibration Sensor")


class DoorSensor:
    """
    MC-38 Magnetic Door Sensor interface for Raspberry Pi.

    The MC-38 is a simple reed switch (Normally Closed type).
    When magnet is near, switch closes. When magnet moves away, switch opens.

    Wiring to Raspberry Pi 5 (4GB):
    - Wire 1 (White) -> Pin 16 (GPIO23)
    - Wire 2 (White) -> Pin 6 (GND)

    No polarity - wires are interchangeable.
    Uses internal pull-up resistor.
    """

    def __init__(
        self,
        gpio_pin: int = 23,
        debounce_ms: int = 50,
        callback: Optional[Callable[[DoorEvent], None]] = None,
        logger=None
    ):
        """
        Initialize the door sensor.

        Args:
            gpio_pin: BCM GPIO pin number (default: 23)
            debounce_ms: Debounce time in milliseconds
            callback: Optional callback for door events
            logger: Optional logger instance
        """
        self.config = DoorConfig(gpio_pin=gpio_pin, debounce_ms=debounce_ms)
        self.callback = callback
        self.logger = logger
        self._initialized = False
        self._event_count = 0
        self._events: List[DoorEvent] = []
        self._last_state: Optional[DoorState] = None

    def initialize(self) -> bool:
        """Initialize GPIO for door sensor."""
        if not RPI_AVAILABLE:
            if self.logger:
                self.logger.warning("RPi.GPIO not available")
            return False

        try:
            GPIO.setmode(GPIO.BCM)
            # Use internal pull-up for NC reed switch
            GPIO.setup(self.config.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._initialized = True
            self._last_state = self.read_state()
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"GPIO init failed: {e}")
            return False

    def is_door_open(self) -> bool:
        """Check if door is currently open."""
        if not self._initialized:
            return False
        # NC switch with pull-up: HIGH = open, LOW = closed
        return GPIO.input(self.config.gpio_pin) == GPIO.HIGH

    def is_door_closed(self) -> bool:
        """Check if door is currently closed."""
        return not self.is_door_open()

    def read_state(self) -> DoorState:
        """Read current door state."""
        if self.is_door_open():
            return DoorState.OPEN
        return DoorState.CLOSED

    def wait_for_change(self, timeout_sec: float = 60.0) -> Optional[DoorEvent]:
        """Wait for door state change with timeout."""
        if not self._initialized:
            return None

        initial_state = self.read_state()
        start = time.time()

        while (time.time() - start) < timeout_sec:
            current = self.read_state()
            if current != initial_state:
                event = DoorEvent(state=current, timestamp=datetime.now())
                self._events.append(event)
                self._event_count += 1
                self._last_state = current
                if self.callback:
                    self.callback(event)
                return event
            time.sleep(0.01)  # 10ms polling
        return None

    def start_monitoring(self, duration_sec: float = 60.0) -> List[DoorEvent]:
        """Monitor door for specified duration, recording state changes."""
        if not self._initialized:
            return []

        events = []
        start = time.time()
        last_state = self.read_state()

        while (time.time() - start) < duration_sec:
            current = self.read_state()

            if current != last_state:
                event = DoorEvent(state=current, timestamp=datetime.now())
                events.append(event)
                self._events.append(event)
                self._event_count += 1
                if self.callback:
                    self.callback(event)
                last_state = current

            time.sleep(0.01)

        return events

    def get_event_count(self) -> int:
        """Return total door events detected."""
        return self._event_count

    def get_recent_events(self, count: int = 10) -> List[DoorEvent]:
        """Get most recent door events."""
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
        """Return ASCII wiring diagram for MC-38 Door Sensor to Raspberry Pi 5."""
        return """
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
|   |     |    |        |           +----------|-----------+  [DOOR]  |
|   +-----|----|---------+                     |                      |
|         |    |                               |                      |
|    Wire 1    Wire 2                    GPIO23 (Pin 16)              |
|    (White)   (White)                                                |
|         |    |                                                      |
|         |    +-------------> GND (Pin 6)                            |
|         +------------------> GPIO23 (Pin 16)                        |
|                                                                     |
+=====================================================================+
|  NORMALLY CLOSED (NC):                                              |
|    - Magnet NEAR (door closed): Switch CLOSED -> GPIO reads LOW     |
|    - Magnet AWAY (door open):   Switch OPEN   -> GPIO reads HIGH    |
+=====================================================================+
|  Uses internal pull-up resistor. No external components needed.     |
+=====================================================================+
"""

