"""
PIR Motion Sensor Module (HC-SR501).

GPIO-based motion detection using Passive Infrared (PIR) sensor.
Supports both polling and interrupt-driven detection.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import time
from typing import Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading

try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    GPIO = None
    RPI_AVAILABLE = False


class TriggerMode(Enum):
    """PIR sensor trigger modes (set by jumper on HC-SR501)."""
    SINGLE = "L"      # Single trigger - output LOW after delay, re-triggers on new motion
    REPEATABLE = "H"  # Repeatable trigger - output stays HIGH while motion continues


class MotionState(Enum):
    """Current state of motion detection."""
    NO_MOTION = 0
    MOTION_DETECTED = 1


@dataclass
class MotionEvent:
    """Data class for motion detection events."""
    state: MotionState
    timestamp: datetime
    duration: Optional[float] = None  # Duration of motion in seconds

    def __str__(self) -> str:
        status = "MOTION DETECTED" if self.state == MotionState.MOTION_DETECTED else "No Motion"
        duration_str = f" (duration: {self.duration:.1f}s)" if self.duration else ""
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {status}{duration_str}"


@dataclass
class PIRConfig:
    """Configuration for PIR sensor."""
    gpio_pin: int = 17                    # BCM GPIO pin number
    trigger_mode: TriggerMode = TriggerMode.REPEATABLE
    debounce_time_ms: int = 200           # Debounce time in milliseconds
    warmup_time_sec: int = 30             # Sensor warmup time (recommended: 30-60 sec)


class MotionSensor:
    """
    HC-SR501 PIR Motion Sensor Handler.

    The HC-SR501 (HW-416-B) is a passive infrared motion sensor with:
    - Adjustable sensitivity (3-7 meters detection range)
    - Adjustable time delay (5 seconds to 5 minutes)
    - Trigger mode selection jumper (Single/Repeatable)

    Wiring to Raspberry Pi 5 (4GB) with polarity markings:
    - [+] VCC (Power)  -> Orange wire -> Pin 1 (3.3V) !! NOT 5V !!
    - [S] OUT (Signal) -> Brown wire  -> Pin 11 (GPIO17)
    - [-] GND (Ground) -> Black wire  -> Pin 6 (GND)

    !! WARNING: Do NOT connect VCC to 5V! The PIR output follows VCC voltage.
       If VCC=5V, output=5V which will DAMAGE the Raspberry Pi GPIO (3.3V max).

    Adjustments:
    - Tx (Time Delay): Turn RIGHT for longer delay (5s-300s), Blockade time: 2.5s default
    - Sx (Sensitivity): Turn RIGHT for increased range (~3m-7m)

    Note: Zener diode on board marks the positive (+) VCC side.
    """

    def __init__(
        self,
        gpio_pin: int = 17,
        trigger_mode: TriggerMode = TriggerMode.REPEATABLE,
        debounce_time_ms: int = 200,
        callback: Optional[Callable[[MotionEvent], None]] = None,
        logger=None
    ):
        """
        Initialize PIR motion sensor.

        Args:
            gpio_pin: BCM GPIO pin number connected to sensor OUT
            trigger_mode: Single (L) or Repeatable (H) trigger mode
            debounce_time_ms: Debounce time to prevent false triggers
            callback: Optional callback function for motion events
            logger: Optional logger instance
        """
        self.gpio_pin = gpio_pin
        self.trigger_mode = trigger_mode
        self.debounce_time_ms = debounce_time_ms
        self.callback = callback
        self._motion_start_time: Optional[datetime] = None
        self._last_state = MotionState.NO_MOTION
        self._event_history: List[MotionEvent] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._initialized = False

        # Setup logger
        if logger:
            self.logger = logger
        else:
            try:
                from src.utils.logger import setup_logger
                self.logger = setup_logger("MotionSensor", "logs/sensors.log")
            except ImportError:
                import logging
                self.logger = logging.getLogger("MotionSensor")

    def initialize(self) -> bool:
        """
        Initialize GPIO for PIR sensor.

        Returns:
            True if initialization successful, False otherwise
        """
        if not RPI_AVAILABLE:
            self.logger.error("RPi.GPIO not available. Install with: pip install RPi.GPIO")
            return False

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self._initialized = True
            self.logger.info(f"PIR sensor initialized on GPIO{self.gpio_pin}")
            self.logger.info(f"Trigger mode: {self.trigger_mode.name}")
            return True
        except Exception as e:
            self.logger.error(f"GPIO initialization failed: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        self.stop_monitoring()
        if RPI_AVAILABLE and self._initialized:
            try:
                GPIO.cleanup(self.gpio_pin)
                self.logger.info("GPIO cleanup complete")
            except Exception as e:
                self.logger.warning(f"GPIO cleanup warning: {e}")
        self._initialized = False

    def read(self) -> MotionState:
        """
        Read current motion state (polling mode).

        Returns:
            MotionState.MOTION_DETECTED or MotionState.NO_MOTION
        """
        if not self._initialized:
            self.logger.warning("Sensor not initialized. Call initialize() first.")
            return MotionState.NO_MOTION

        try:
            pin_state = GPIO.input(self.gpio_pin)
            return MotionState.MOTION_DETECTED if pin_state else MotionState.NO_MOTION
        except Exception as e:
            self.logger.error(f"Read error: {e}")
            return MotionState.NO_MOTION

    def is_motion_detected(self) -> bool:
        """Check if motion is currently detected."""
        return self.read() == MotionState.MOTION_DETECTED

    def wait_for_motion(self, timeout: Optional[float] = None) -> bool:
        """
        Block until motion is detected or timeout.

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            True if motion detected, False if timeout
        """
        if not self._initialized:
            self.logger.warning("Sensor not initialized")
            return False

        start_time = time.time()
        while True:
            if self.is_motion_detected():
                event = MotionEvent(
                    state=MotionState.MOTION_DETECTED,
                    timestamp=datetime.now()
                )
                self._event_history.append(event)
                self.logger.info(str(event))
                return True

            if timeout and (time.time() - start_time) >= timeout:
                return False

            time.sleep(0.1)

    def start_monitoring(self, use_interrupt: bool = True) -> None:
        """
        Start continuous motion monitoring.

        Args:
            use_interrupt: Use GPIO interrupt (True) or polling (False)
        """
        if not self._initialized:
            self.logger.error("Sensor not initialized")
            return

        if self._monitoring:
            self.logger.warning("Already monitoring")
            return

        self._monitoring = True

        if use_interrupt and RPI_AVAILABLE:
            # Use GPIO edge detection (interrupt-driven)
            GPIO.add_event_detect(
                self.gpio_pin,
                GPIO.BOTH,
                callback=self._interrupt_callback,
                bouncetime=self.debounce_time_ms
            )
            self.logger.info("Started interrupt-driven monitoring")
        else:
            # Start polling thread
            self._monitor_thread = threading.Thread(target=self._polling_loop, daemon=True)
            self._monitor_thread.start()
            self.logger.info("Started polling-based monitoring")

    def stop_monitoring(self) -> None:
        """Stop motion monitoring."""
        self._monitoring = False
        if RPI_AVAILABLE and self._initialized:
            try:
                GPIO.remove_event_detect(self.gpio_pin)
            except Exception:
                pass
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None
        self.logger.info("Stopped monitoring")

    def _interrupt_callback(self, channel: int) -> None:
        """Handle GPIO interrupt callback."""
        current_state = self.read()
        self._handle_state_change(current_state)

    def _polling_loop(self) -> None:
        """Polling loop for motion detection."""
        while self._monitoring:
            current_state = self.read()
            if current_state != self._last_state:
                self._handle_state_change(current_state)
            time.sleep(self.debounce_time_ms / 1000.0)

    def _handle_state_change(self, new_state: MotionState) -> None:
        """Handle motion state change."""
        now = datetime.now()
        duration = None

        if new_state == MotionState.MOTION_DETECTED:
            self._motion_start_time = now
        elif self._motion_start_time:
            duration = (now - self._motion_start_time).total_seconds()
            self._motion_start_time = None

        event = MotionEvent(state=new_state, timestamp=now, duration=duration)
        self._event_history.append(event)
        self._last_state = new_state

        self.logger.info(str(event))

        if self.callback:
            try:
                self.callback(event)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    def get_event_history(self, limit: int = 100) -> List[MotionEvent]:
        """Get recent motion events."""
        return self._event_history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()

    @staticmethod
    def get_wiring_diagram() -> str:
        """Return ASCII wiring diagram for HC-SR501 to Raspberry Pi 5."""
        return """
+=====================================================================+
|         HC-SR501 PIR Sensor Wiring - Raspberry Pi 5 (4GB)           |
+=====================================================================+
|  !! WARNING: VCC must be 3.3V! Connecting to 5V will DAMAGE GPIO!   |
+=====================================================================+
|                                                                     |
|   HC-SR501 (HW-416-B)              Raspberry Pi 5                   |
|   +------------------+             +----------------------+         |
|   |  [Tx]    [Sx]    |             | 3.3V (1) o o (2) 5V  |<-Orange |
|   |  Time    Sens    |             | GPIO2(3) o o (4) 5V  |  [+]    |
|   |   Adjust   Adjust|             | GPIO3(5) o o (6) GND |<-Black  |
|   |                  |             | GPIO4(7) o o (8)     |  [-]    |
|   |   [H] [L]<-Mode  |             |   GND(9) o o (10)    |         |
|   |                  |             | GPIO17(11)o o (12)   |<-Brown  |
|   |  +     S     -   |             | GPIO27(13)o o (14)   |  [S]    |
|   |  o     o     o   |             | GPIO22(15)o o (16)   |         |
|   | VCC   OUT   GND  |             |  3.3V(17)o o (18)    |         |
|   +--+-----+-----+---+             +----------------------+         |
|      |     |     |                                                  |
|      |     |     +-- [-] Black -----------------> GND (Pin 6)       |
|      |     +-------- [S] Brown -----------------> GPIO17 (Pin 11)   |
|      +-------------- [+] Orange ----------------> 3.3V (Pin 1)      |
|                                    !! NOT 5V - DAMAGES GPIO !!      |
+=====================================================================+
|  POLARITY: [+] Orange=VCC(3.3V)  [S] Brown=OUT  [-] Black=GND       |
|  Tx: Time Delay (5s-300s)     Sx: Sensitivity (3m-7m)               |
|  Blockade Time: 2.5s (default)                                      |
|  Mode Jumper: H = Repeatable trigger, L = Single trigger            |
|  Note: Zener diode on board marks [+] VCC side                      |
+=====================================================================+
"""

