#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alert Manager - LINE Notification Integration for Raspberry Pi Smart Monitoring Kit.

@file       alert_manager.py
@brief      Manages alert notifications via LINE Messaging API.
@details    Provides notification management including:
            - Sends sensor event alerts
            - Formats messages with emoji and status
            - Rate limiting to prevent spam
            - Alert history tracking

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import deque

try:
    from src.line_api.messaging import LINEMessenger
except ImportError:
    LINEMessenger = None  # LINE SDK not installed

from .pattern_engine import Alert, AlertLevel


@dataclass
class AlertConfig:
    """Configuration for alert manager."""
    # Rate limiting
    min_alert_interval: float = 10.0  # Minimum seconds between alerts
    max_alerts_per_hour: int = 30

    # Alert levels to send
    send_info: bool = False  # Send INFO level alerts
    send_warning: bool = True
    send_alert: bool = True
    send_critical: bool = True

    # Quiet hours (no alerts during these hours)
    quiet_hours_enabled: bool = False
    quiet_start_hour: int = 23  # 11 PM
    quiet_end_hour: int = 7    # 7 AM


class AlertManager:
    """
    Manages LINE notifications for sensor alerts.

    Features:
    - Rate limiting to prevent notification spam
    - Alert level filtering
    - Quiet hours support
    - Alert history tracking
    """

    def __init__(
        self,
        line_messenger: Optional[LINEMessenger] = None,
        channel_access_token: Optional[str] = None,
        user_id: Optional[str] = None,
        config: Optional[AlertConfig] = None,
        logger=None
    ):
        """
        Initialize alert manager.

        Args:
            line_messenger: Existing LINEMessenger instance (preferred)
            channel_access_token: LINE channel access token (if no messenger)
            user_id: LINE user ID (if no messenger)
            config: Alert configuration
            logger: Optional logger
        """
        self.config = config or AlertConfig()
        self.logger = logger

        # Initialize LINE messenger
        if line_messenger:
            self.messenger = line_messenger
        elif channel_access_token and user_id and LINEMessenger:
            self.messenger = LINEMessenger(
                channel_access_token=channel_access_token,
                user_id=user_id
            )
        else:
            self.messenger = None
            if not LINEMessenger:
                self._log("WARNING: LINE SDK not installed")
            else:
                self._log("WARNING: No LINE messenger configured")

        # Rate limiting state
        self._last_alert_time: Optional[datetime] = None
        self._hourly_alerts: deque = deque(maxlen=100)

        # Alert history
        self._sent_alerts: List[Alert] = []
        self._failed_alerts: List[Alert] = []

    def send_alert(self, alert: Alert) -> bool:
        """
        Send alert notification via LINE.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        # Check if messenger is configured
        if not self.messenger:
            self._log("Cannot send alert: LINE messenger not configured")
            return False

        # Check alert level filter
        if not self._should_send_level(alert.level):
            self._log(f"Alert level {alert.level.value} filtered out")
            return False

        # Check quiet hours
        if self._is_quiet_hours():
            self._log("Alert suppressed: quiet hours active")
            return False

        # Check rate limiting
        if not self._check_rate_limit():
            self._log("Alert rate limited")
            return False

        # Format and send message
        try:
            message = self._format_alert(alert)
            success = self.messenger.send_text(message)

            if success:
                self._last_alert_time = datetime.now()
                self._hourly_alerts.append(datetime.now())
                self._sent_alerts.append(alert)
                self._log(f"Alert sent: {alert.message}")
            else:
                self._failed_alerts.append(alert)
                self._log(f"Failed to send alert: {alert.message}")

            return success

        except Exception as e:
            self._log(f"Error sending alert: {e}")
            self._failed_alerts.append(alert)
            return False

    def _format_alert(self, alert: Alert) -> str:
        """Format alert for LINE message."""
        # Level prefix
        level_prefix = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ALERT: "🚨",
            AlertLevel.CRITICAL: "🆘"
        }

        prefix = level_prefix.get(alert.level, "")
        timestamp = alert.timestamp.strftime("%H:%M:%S")

        lines = [
            f"{prefix} {alert.message}",
            f"🕐 {timestamp}"
        ]

        # Add details if present
        if alert.details:
            for key, value in alert.details.items():
                if key != "pattern":  # Skip internal keys
                    lines.append(f"  • {key}: {value}")

        return "\n".join(lines)

    def _should_send_level(self, level: AlertLevel) -> bool:
        """Check if alert level should be sent."""
        if level == AlertLevel.INFO:
            return self.config.send_info
        elif level == AlertLevel.WARNING:
            return self.config.send_warning
        elif level == AlertLevel.ALERT:
            return self.config.send_alert
        elif level == AlertLevel.CRITICAL:
            return self.config.send_critical
        return True

    def _is_quiet_hours(self) -> bool:
        """Check if current time is during quiet hours."""
        if not self.config.quiet_hours_enabled:
            return False

        hour = datetime.now().hour
        start = self.config.quiet_start_hour
        end = self.config.quiet_end_hour

        if start > end:
            # Spans midnight (e.g., 23:00 - 07:00)
            return hour >= start or hour < end
        else:
            return start <= hour < end

    def _check_rate_limit(self) -> bool:
        """Check if alert can be sent based on rate limiting."""
        now = datetime.now()

        # Check minimum interval
        if self._last_alert_time:
            elapsed = (now - self._last_alert_time).total_seconds()
            if elapsed < self.config.min_alert_interval:
                return False

        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        recent_count = sum(1 for t in self._hourly_alerts if t > hour_ago)

        if recent_count >= self.config.max_alerts_per_hour:
            return False

        return True

    def send_status_update(self, status: Dict[str, Any]) -> bool:
        """Send system status update via LINE."""
        if not self.messenger:
            return False

        lines = [
            "📊 System Status Update",
            f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            "",
            f"🚶 Motion: {'Detected' if status.get('motion') else 'Clear'}",
            f"🔊 Sound: {'Detected' if status.get('sound') else 'Quiet'}",
            f"🚪 Door: {'Open' if status.get('door_open') else 'Closed'}",
            f"📳 Vibration: {'Detected' if status.get('vibration') else 'None'}"
        ]

        if status.get('temperature') is not None:
            lines.append(f"🌡️ Temp: {status['temperature']:.1f}°C")
        if status.get('humidity') is not None:
            lines.append(f"💧 Humidity: {status['humidity']:.1f}%")

        message = "\n".join(lines)
        return self.messenger.send_text(message)

    def get_stats(self) -> Dict[str, Any]:
        """Get alert manager statistics."""
        return {
            "sent_count": len(self._sent_alerts),
            "failed_count": len(self._failed_alerts),
            "last_alert_time": self._last_alert_time.isoformat() if self._last_alert_time else None
        }

    def _log(self, message: str) -> None:
        """Log message."""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[AlertManager] {message}")
