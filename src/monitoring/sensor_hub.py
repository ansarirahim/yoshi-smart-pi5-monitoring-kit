#!/usr/bin/env python3
"""
Sensor Hub - Unified Sensor Manager for Raspberry Pi Smart Monitoring Kit.

Manages all connected sensors and provides a unified interface for:
- Reading sensor states
- Monitoring for events
- Coordinating sensor data

Sensors Supported:
- PIR Motion Sensor (HC-SR501) - GPIO17
- Sound Sensor (LM393) - GPIO22
- Door Sensor (MC-38) - GPIO23
- Vibration Sensor (801S) - GPIO27
- Temperature Sensor (XY-MD02) - USB-RS485

Author: A.R. Ansari
Project: Raspberry Pi Smart Monitoring Kit
Client: Yoshinori Ueda
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Dict, List, Any
from enum import Enum

# Import sensor modules
from src.sensors.motion import MotionSensor
from src.sensors.sound import SoundSensor
from src.sensors.door import DoorSensor
from src.sensors.vibration import VibrationSensor
from src.sensors.temperature import TemperatureSensor


class SensorType(Enum):
    """Sensor types in the monitoring kit."""
    PIR_MOTION = "pir_motion"
    SOUND = "sound"
    DOOR = "door"
    VIBRATION = "vibration"
    TEMPERATURE = "temperature"


@dataclass
class SensorStatus:
    """Current status of all sensors."""
    motion_detected: bool = False
    sound_detected: bool = False
    door_open: bool = False
    vibration_detected: bool = False
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "motion": self.motion_detected,
            "sound": self.sound_detected,
            "door_open": self.door_open,
            "vibration": self.vibration_detected,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "timestamp": self.timestamp.isoformat()
        }


class SensorHub:
    """
    Unified sensor manager for all monitoring sensors.

    Provides centralized access to all sensors with:
    - Unified initialization
    - Coordinated monitoring
    - Event callbacks
    - Status reporting
    """

    # Default GPIO assignments (no conflicts)
    DEFAULT_GPIO = {
        SensorType.PIR_MOTION: 17,
        SensorType.SOUND: 22,
        SensorType.DOOR: 23,
        SensorType.VIBRATION: 27
    }

    def __init__(
        self,
        gpio_config: Optional[Dict[SensorType, int]] = None,
        temperature_port: str = "/dev/ttyUSB0",
        event_callback: Optional[Callable] = None,
        logger=None
    ):
        """
        Initialize sensor hub.

        Args:
            gpio_config: Optional custom GPIO assignments
            temperature_port: Serial port for temperature sensor
            event_callback: Callback for sensor events
            logger: Optional logger instance
        """
        self.gpio_config = gpio_config or self.DEFAULT_GPIO
        self.temperature_port = temperature_port
        self.event_callback = event_callback
        self.logger = logger

        # Sensor instances
        self.motion_sensor: Optional[MotionSensor] = None
        self.sound_sensor: Optional[SoundSensor] = None
        self.door_sensor: Optional[DoorSensor] = None
        self.vibration_sensor: Optional[VibrationSensor] = None
        self.temperature_sensor: Optional[TemperatureSensor] = None

        # State
        self._initialized = False
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._armed = True  # System armed/disarmed

        # Last known status
        self._last_status = SensorStatus()

    def initialize(self) -> Dict[SensorType, bool]:
        """
        Initialize all sensors.

        Returns:
            Dict with initialization status for each sensor
        """
        results = {}

        # Initialize PIR Motion Sensor
        try:
            self.motion_sensor = MotionSensor(
                gpio_pin=self.gpio_config[SensorType.PIR_MOTION]
            )
            results[SensorType.PIR_MOTION] = self.motion_sensor.initialize()
        except Exception as e:
            self._log(f"PIR init failed: {e}")
            results[SensorType.PIR_MOTION] = False

        # Initialize Sound Sensor
        try:
            self.sound_sensor = SoundSensor(
                gpio_pin=self.gpio_config[SensorType.SOUND]
            )
            results[SensorType.SOUND] = self.sound_sensor.initialize()
        except Exception as e:
            self._log(f"Sound init failed: {e}")
            results[SensorType.SOUND] = False

        # Initialize Door Sensor
        try:
            self.door_sensor = DoorSensor(
                gpio_pin=self.gpio_config[SensorType.DOOR]
            )
            results[SensorType.DOOR] = self.door_sensor.initialize()
        except Exception as e:
            self._log(f"Door init failed: {e}")
            results[SensorType.DOOR] = False

        # Initialize Vibration Sensor
        try:
            self.vibration_sensor = VibrationSensor(
                gpio_pin=self.gpio_config[SensorType.VIBRATION]
            )
            results[SensorType.VIBRATION] = self.vibration_sensor.initialize()
        except Exception as e:
            self._log(f"Vibration init failed: {e}")
            results[SensorType.VIBRATION] = False

        # Initialize Temperature Sensor
        try:
            self.temperature_sensor = TemperatureSensor(port=self.temperature_port)
            results[SensorType.TEMPERATURE] = self.temperature_sensor.connect()
        except Exception as e:
            self._log(f"Temperature init failed: {e}")
            results[SensorType.TEMPERATURE] = False

        self._initialized = any(results.values())
        self._log(f"Sensor hub initialized: {results}")
        return results

    def get_status(self) -> SensorStatus:
        """Get current status of all sensors."""
        status = SensorStatus(timestamp=datetime.now())

        if self.motion_sensor:
            try:
                status.motion_detected = self.motion_sensor.is_motion_detected()
            except Exception:
                pass

        if self.sound_sensor:
            try:
                status.sound_detected = self.sound_sensor.is_sound_detected()
            except Exception:
                pass

        if self.door_sensor:
            try:
                status.door_open = self.door_sensor.is_door_open()
            except Exception:
                pass

        if self.vibration_sensor:
            try:
                status.vibration_detected = self.vibration_sensor.is_vibration_detected()
            except Exception:
                pass

        if self.temperature_sensor:
            try:
                temp, hum = self.temperature_sensor.read()
                status.temperature = temp
                status.humidity = hum
            except Exception:
                pass

        self._last_status = status
        return status

    def start_monitoring(
        self,
        poll_interval: float = 0.1,
        callback: Optional[Callable[[SensorType, bool], None]] = None
    ) -> None:
        """
        Start continuous sensor monitoring in background.

        Args:
            poll_interval: Time between sensor polls in seconds
            callback: Optional callback function(sensor_type, value) for events
        """
        if self._monitoring:
            return

        if callback:
            self.event_callback = callback

        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(poll_interval,),
            daemon=True
        )
        self._monitor_thread.start()
        self._log("Sensor monitoring started")

    def stop_monitoring(self) -> None:
        """Stop sensor monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        self._log("Sensor monitoring stopped")

    def _monitor_loop(self, poll_interval: float) -> None:
        """Main monitoring loop."""
        last_motion = False
        last_sound = False
        last_door = False
        last_vibration = False

        while self._monitoring:
            try:
                status = self.get_status()

                # Detect state changes and trigger callbacks
                if self._armed and self.event_callback:
                    if status.motion_detected and not last_motion:
                        self.event_callback(SensorType.MOTION, True)
                    if status.sound_detected and not last_sound:
                        self.event_callback(SensorType.SOUND, True)
                    if status.door_open != last_door:
                        self.event_callback(SensorType.DOOR, status.door_open)
                    if status.vibration_detected and not last_vibration:
                        self.event_callback(SensorType.VIBRATION, True)

                last_motion = status.motion_detected
                last_sound = status.sound_detected
                last_door = status.door_open
                last_vibration = status.vibration_detected

            except Exception as e:
                self._log(f"Monitor error: {e}")

            time.sleep(poll_interval)

    def arm(self) -> None:
        """Arm the monitoring system."""
        self._armed = True
        self._log("System ARMED")

    def disarm(self) -> None:
        """Disarm the monitoring system."""
        self._armed = False
        self._log("System DISARMED")

    def is_armed(self) -> bool:
        """Check if system is armed."""
        return self._armed

    def cleanup(self) -> None:
        """Cleanup all sensors."""
        self.stop_monitoring()

        if self.motion_sensor:
            self.motion_sensor.cleanup()
        if self.sound_sensor:
            self.sound_sensor.cleanup()
        if self.door_sensor:
            self.door_sensor.cleanup()
        if self.vibration_sensor:
            self.vibration_sensor.cleanup()
        if self.temperature_sensor:
            self.temperature_sensor.disconnect()

        self._initialized = False
        self._log("Sensor hub cleanup complete")

    def _log(self, message: str) -> None:
        """Log message."""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[SensorHub] {message}")

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
