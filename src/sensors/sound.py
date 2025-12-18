#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LM393 Sound Sensor Module for Raspberry Pi.

@file       sound.py
@brief      GPIO-based sound detection using LM393 comparator sensor.
@details    Provides interface for LM393-based sound detection sensor.
            Detects ambient audio levels and outputs digital LOW signal
            when sound exceeds adjustable threshold.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.

@hardware   TekBud LM393 Sound Sensor Module
@interface  GPIO22 (BCM) / Pin 15
@voltage    3.3V DC (4V-6V supported, 3.3V works)

@specifications
    - Model: TekBud LM393 Sound Sensor Module
    - Operating Voltage: 4V - 6V DC (3.3V also works)
    - Comparator IC: LM393
    - Output Type: Digital (D0) + Analog (A0)
    - Digital Output: LOW when sound detected, HIGH when quiet
    - LED Indicator: ON when sound detected
    - Sensitivity: Adjustable via potentiometer (anti-clockwise = reduce)
    - Orientation: Keep microphone facing DOWN (bottom side up)

@wiring
    - VCC  [+] Orange -> Pin 1 (3.3V)
    - GND  [-] Black  -> Pin 6 (GND)
    - D0   [S] White  -> Pin 15 (GPIO22)
    - A0   [A] N/C    -> Not connected (RPi has no native ADC)

@behavior
    - No sound (quiet): D0 = HIGH, LED OFF
    - Sound detected:   D0 = LOW,  LED ON

@note GPIO17 = PIR, GPIO27 = Vibration. Sound uses GPIO22.

@dependencies
    - RPi.GPIO >= 0.7.0

@usage
    >>> from src.sensors.sound import SoundSensor
    >>> sensor = SoundSensor(gpio_pin=22)
    >>> sensor.initialize()
    >>> if sensor.is_sound_detected():
    ...     print("Sound detected!")
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


class SoundState(Enum):
    """Sound detection states."""
    QUIET = 0
    SOUND_DETECTED = 1


@dataclass
class SoundEvent:
    """Represents a sound detection event."""
    state: SoundState
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0

    def __str__(self) -> str:
        if self.state == SoundState.SOUND_DETECTED:
            return f"[{self.timestamp.strftime('%H:%M:%S')}] SOUND DETECTED! duration={self.duration_ms:.1f}ms"
        return f"[{self.timestamp.strftime('%H:%M:%S')}] Quiet"


@dataclass
class SoundConfig:
    """Configuration for sound sensor."""
    gpio_pin: int = 22  # Default GPIO22 (GPIO17=PIR, GPIO27=Vibration)
    debounce_ms: int = 50
    min_event_gap_ms: int = 100

    def __post_init__(self):
        if not 0 <= self.gpio_pin <= 27:
            raise ValueError(f"Invalid GPIO pin: {self.gpio_pin}")
        # Check for known conflicts
        if self.gpio_pin == 17:
            raise ValueError("GPIO17 is reserved for PIR Motion Sensor")
        if self.gpio_pin == 27:
            raise ValueError("GPIO27 is reserved for Vibration Sensor")


class SoundSensor:
    """
    LM393 Sound Sensor interface for Raspberry Pi.

    The sensor uses an LM393 comparator to detect sound levels.
    When sound exceeds the threshold set by potentiometer,
    output goes LOW (active low).

    Wiring to Raspberry Pi 5 (4GB):
    - [+] VCC (Power)  -> Orange wire -> Pin 1 (3.3V)
    - [-] GND (Ground) -> Black wire  -> Pin 6 (GND)
    - [S] D0  (Digital)-> White wire  -> Pin 15 (GPIO22)
    - [A] A0  (Analog) -> Not used (requires external ADC)

    Adjustments:
    - Sensitivity Potentiometer: Turn to adjust detection threshold
    """

    def __init__(
        self,
        gpio_pin: int = 22,
        debounce_ms: int = 50,
        callback: Optional[Callable[[SoundEvent], None]] = None,
        logger=None
    ):
        """
        Initialize the sound sensor.

        Args:
            gpio_pin: BCM GPIO pin number (default: 22)
            debounce_ms: Debounce time in milliseconds
            callback: Optional callback for sound events
            logger: Optional logger instance
        """
        self.config = SoundConfig(gpio_pin=gpio_pin, debounce_ms=debounce_ms)
        self.callback = callback
        self.logger = logger
        self._initialized = False
        self._event_count = 0
        self._events: List[SoundEvent] = []

    def initialize(self) -> bool:
        """Initialize GPIO for sound sensor."""
        if not RPI_AVAILABLE:
            if self.logger:
                self.logger.warning("RPi.GPIO not available")
            return False

        try:
            GPIO.setmode(GPIO.BCM)
            # Use pull-up since output is active LOW
            GPIO.setup(self.config.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._initialized = True
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"GPIO init failed: {e}")
            return False

    def is_sound_detected(self) -> bool:
        """Check if sound is currently detected (active LOW)."""
        if not self._initialized:
            return False
        # Output is LOW when sound is detected
        return GPIO.input(self.config.gpio_pin) == GPIO.LOW

    def read_state(self) -> SoundState:
        """Read current sound state."""
        if self.is_sound_detected():
            return SoundState.SOUND_DETECTED
        return SoundState.QUIET

    def wait_for_sound(self, timeout_sec: float = 10.0) -> Optional[SoundEvent]:
        """Wait for sound event with timeout."""
        if not self._initialized:
            return None

        start = time.time()
        while (time.time() - start) < timeout_sec:
            if self.is_sound_detected():
                event = SoundEvent(
                    state=SoundState.SOUND_DETECTED,
                    timestamp=datetime.now()
                )
                self._events.append(event)
                self._event_count += 1
                if self.callback:
                    self.callback(event)
                return event
            time.sleep(0.005)  # 5ms polling for fast sound detection
        return None

    def start_monitoring(self, duration_sec: float = 60.0) -> List[SoundEvent]:
        """Monitor sound for specified duration."""
        if not self._initialized:
            return []

        events = []
        start = time.time()
        last_state = SoundState.QUIET
        sound_start = None

        while (time.time() - start) < duration_sec:
            current = self.read_state()
            now = time.time()

            # Detect falling edge (sound started - active LOW)
            if current == SoundState.SOUND_DETECTED and last_state == SoundState.QUIET:
                sound_start = now

            # Detect rising edge (sound ended)
            elif current == SoundState.QUIET and last_state == SoundState.SOUND_DETECTED:
                if sound_start:
                    duration_ms = (now - sound_start) * 1000
                    event = SoundEvent(
                        state=SoundState.SOUND_DETECTED,
                        timestamp=datetime.now(),
                        duration_ms=duration_ms
                    )
                    events.append(event)
                    self._events.append(event)
                    if self.callback:
                        self.callback(event)

            last_state = current
            time.sleep(0.005)

        return events

    def get_event_count(self) -> int:
        """Return total sound events detected."""
        return self._event_count

    def get_recent_events(self, count: int = 10) -> List[SoundEvent]:
        """Get most recent sound events."""
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
        """Return ASCII wiring diagram for LM393 Sound Sensor to Raspberry Pi 5."""
        return """
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
|                                                                     |
+=====================================================================+
|  ACTIVE LOW: D0=LOW when sound detected, LED turns ON               |
|  POLARITY: [+] Orange=VCC  [-] Black=GND  [S] White=D0              |
|  A0 (Analog): Not used - RPi has no native ADC                      |
|  Sensitivity: Adjust potentiometer for detection threshold          |
+=====================================================================+
"""

