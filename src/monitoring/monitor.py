#!/usr/bin/env python3
"""
Main Monitoring Script - Raspberry Pi Smart Monitoring Kit.

Runs the unified sensor monitoring system with:
- All 5 sensors (PIR, Sound, Door, Vibration, Temperature)
- Pattern detection and anomaly alerts
- LINE notifications
- Webhook command support
- OTA update support

Usage:
    python3 -m src.monitoring.monitor

Author: A.R. Ansari
Project: Raspberry Pi Smart Monitoring Kit
Client: Yoshinori Ueda
"""

import os
import sys
import time
import signal
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from .sensor_hub import SensorHub, SensorType
from .pattern_engine import PatternEngine, PatternConfig, EventType, Alert
from .alert_manager import AlertManager, AlertConfig

try:
    from src.line_api.messaging import LINEMessenger
except ImportError:
    LINEMessenger = None

try:
    from src.line_api.webhook import WebhookServer
except ImportError:
    WebhookServer = None

try:
    from src.ota.updater import OTAUpdater
except ImportError:
    OTAUpdater = None


class SmartMonitor:
    """
    Main monitoring system that integrates all components.

    Components:
    - SensorHub: Manages all 5 sensors
    - PatternEngine: Detects anomalies
    - AlertManager: Sends LINE notifications
    - WebhookServer: Remote control via LINE commands
    - OTAUpdater: Automatic updates from GitHub
    """

    def __init__(
        self,
        line_token: Optional[str] = None,
        line_user_id: Optional[str] = None,
        line_secret: Optional[str] = None,
        temperature_port: str = "/dev/ttyUSB0",
        webhook_port: int = 5000,
        enable_webhook: bool = True,
        enable_ota: bool = True,
        github_repo: Optional[str] = None
    ):
        """
        Initialize the smart monitoring system.

        Args:
            line_token: LINE channel access token
            line_user_id: LINE user ID for notifications
            line_secret: LINE channel secret for webhook
            temperature_port: Serial port for temperature sensor
            webhook_port: Port for webhook server
            enable_webhook: Enable webhook server
            enable_ota: Enable OTA updates
            github_repo: GitHub repo for OTA (e.g., 'user/repo')
        """
        self.running = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Get credentials from environment if not provided
        self.line_token = line_token or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.line_user_id = line_user_id or os.getenv("LINE_USER_ID")
        self.line_secret = line_secret or os.getenv("LINE_CHANNEL_SECRET")
        self.github_repo = github_repo or os.getenv("GITHUB_REPO")

        # Initialize sensor hub and pattern engine
        self.sensor_hub = SensorHub(temperature_port=temperature_port)
        self.pattern_engine = PatternEngine(
            config=PatternConfig(),
            alert_callback=self._on_alert
        )

        # Initialize LINE messenger and alert manager
        if self.line_token and self.line_user_id and LINEMessenger:
            self.messenger = LINEMessenger(
                channel_access_token=self.line_token,
                user_id=self.line_user_id
            )
            self.alert_manager = AlertManager(
                line_messenger=self.messenger,
                config=AlertConfig()
            )
            print("✅ LINE notifications enabled")
        else:
            self.messenger = None
            self.alert_manager = AlertManager(config=AlertConfig())
            if not LINEMessenger:
                print("⚠️ LINE SDK not installed (notifications disabled)")
            else:
                print("⚠️ LINE notifications disabled (no credentials)")

        # Initialize webhook server for remote control
        self.webhook_server: Optional[Any] = None
        if enable_webhook and WebhookServer and self.line_token and self.line_secret:
            try:
                self.webhook_server = WebhookServer(
                    channel_access_token=self.line_token,
                    channel_secret=self.line_secret,
                    command_callback=self._handle_command,
                    port=webhook_port
                )
                print(f"✅ Webhook server ready (port {webhook_port})")
            except Exception as e:
                print(f"⚠️ Webhook server failed: {e}")
        else:
            if not WebhookServer:
                print("⚠️ Webhook server not available (LINE SDK not installed)")
            elif not self.line_secret:
                print("⚠️ Webhook disabled (no LINE_CHANNEL_SECRET)")

        # Initialize OTA updater
        self.ota_updater: Optional[Any] = None
        if enable_ota and OTAUpdater and self.github_repo:
            try:
                ota_config = {
                    'github_repo': self.github_repo,
                    'check_interval': 3600,  # Check every hour
                    'auto_update': False,  # Manual approval required
                    'backup_enabled': True
                }
                self.ota_updater = OTAUpdater(ota_config)
                print(f"✅ OTA updater ready (repo: {self.github_repo})")
            except Exception as e:
                print(f"⚠️ OTA updater failed: {e}")
        else:
            if not OTAUpdater:
                print("⚠️ OTA updater not available")
            elif not self.github_repo:
                print("⚠️ OTA disabled (no GITHUB_REPO)")

        # State tracking
        self._last_temp_check = 0
        self._temp_check_interval = 60  # Check temperature every 60 seconds

    def _on_alert(self, alert: Alert) -> None:
        """Callback when pattern engine generates an alert."""
        print(f"🚨 ALERT: {alert}")
        if self.alert_manager:
            self.alert_manager.send_alert(alert)

    def initialize(self) -> bool:
        """Initialize all sensors."""
        print("\n" + "=" * 50)
        print("🚀 Initializing Smart Monitoring System")
        print("=" * 50)

        results = self.sensor_hub.initialize()

        print("\nSensor Initialization Results:")
        for sensor_type, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {sensor_type.value}")

        all_ok = all(results.values())
        if all_ok:
            print("\n✅ All sensors initialized successfully!")
        else:
            print("\n⚠️ Some sensors failed to initialize")

        return all_ok

    def start(self) -> None:
        """Start the monitoring system."""
        if self.running:
            print("Already running!")
            return

        self.running = True

        # Arm the sensor hub
        self.sensor_hub.arm()

        # Start sensor monitoring
        self.sensor_hub.start_monitoring(callback=self._on_sensor_event)

        # Start main monitoring loop in background
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        # Start webhook server if available
        if self.webhook_server:
            self.webhook_server.start()
            print("🌐 Webhook server started")

        # Start OTA updater if available
        if self.ota_updater:
            self.ota_updater.start()
            print("🔄 OTA updater started")

        print("\n" + "=" * 50)
        print("🟢 Smart Monitoring System ACTIVE")
        print("=" * 50)
        print("Press Ctrl+C to stop\n")

        # Send startup notification
        if self.alert_manager:
            self.alert_manager.send_status_update(self.get_status())

    def _on_sensor_event(self, sensor_type: SensorType, value: bool) -> None:
        """Handle sensor events from SensorHub."""
        # Map sensor type to event type
        event_map = {
            SensorType.MOTION: EventType.MOTION.value,
            SensorType.SOUND: EventType.SOUND.value,
            SensorType.VIBRATION: EventType.VIBRATION.value
        }

        # Handle door sensor specially (open/close)
        if sensor_type == SensorType.DOOR:
            event_type = EventType.DOOR_OPENED.value if value else EventType.DOOR_CLOSED.value
            self.pattern_engine.process_event(event_type, {"door_open": value})
        elif sensor_type in event_map and value:  # Only process when triggered
            self.pattern_engine.process_event(event_map[sensor_type], {})

    def _monitor_loop(self) -> None:
        """Main monitoring loop for periodic checks."""
        while self.running:
            try:
                now = time.time()

                # Periodic temperature check
                if now - self._last_temp_check >= self._temp_check_interval:
                    self._check_temperature()
                    self._last_temp_check = now

                time.sleep(1)

            except Exception as e:
                print(f"Monitor loop error: {e}")
                time.sleep(5)

    def _check_temperature(self) -> None:
        """Check temperature sensor and generate alerts if needed."""
        if not self.sensor_hub.temperature_sensor:
            return

        try:
            reading = self.sensor_hub.temperature_sensor.read()
            if reading:
                alert = self.pattern_engine.check_temperature(reading.temperature, reading.humidity)
                if alert and self.alert_manager:
                    self.alert_manager.send_alert(alert)

        except Exception as e:
            print(f"Temperature check error: {e}")

    def _handle_command(self, command: str) -> None:
        """Handle commands from webhook server."""
        command = command.lower().strip()
        print(f"📨 Command received: {command}")

        if command in ("stop", "pause", "disarm"):
            self.sensor_hub.disarm()
            print("🔓 System DISARMED")
            if self.messenger:
                self.messenger.send_message("🔓 System disarmed")

        elif command in ("resume", "start", "arm"):
            self.sensor_hub.arm()
            print("🔒 System ARMED")
            if self.messenger:
                self.messenger.send_message("🔒 System armed")

        elif command == "update":
            if self.ota_updater:
                has_update = self.ota_updater.check_for_updates()
                msg = f"🔄 Update available!" if has_update else "✅ Up to date"
                if self.messenger:
                    self.messenger.send_message(msg)

    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        sensor_status = self.sensor_hub.get_status()
        status = {
            "running": self.running,
            "armed": self.sensor_hub._armed,
            "motion": sensor_status.motion_detected,
            "sound": sensor_status.sound_detected,
            "door_open": sensor_status.door_open,
            "vibration": sensor_status.vibration_detected,
        }
        if self.sensor_hub.temperature_sensor:
            try:
                reading = self.sensor_hub.temperature_sensor.read()
                if reading:
                    status["temp"] = reading.temperature
                    status["humidity"] = reading.humidity
            except:
                pass
        return status

    def stop(self) -> None:
        """Stop the monitoring system."""
        print("\n🛑 Stopping Smart Monitoring System...")
        self.running = False
        if self.webhook_server:
            self.webhook_server.stop()
        if self.ota_updater:
            self.ota_updater.stop()
        self.sensor_hub.stop_monitoring()
        self.sensor_hub.cleanup()
        print("✅ System stopped")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🏠 Raspberry Pi Smart Monitoring Kit                     ║
║     Client: Yoshinori Ueda                                   ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Create monitor instance
    monitor = SmartMonitor()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize and start
    if monitor.initialize():
        monitor.start()

        # Keep running until stopped
        try:
            while monitor.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            monitor.stop()
    else:
        print("❌ Failed to initialize sensors")
        sys.exit(1)


if __name__ == "__main__":
    main()
