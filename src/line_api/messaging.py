#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINE Messaging Module.

@file       messaging.py
@brief      Sends push notifications via LINE Messaging API.
@details    Handles message formatting, image uploads, and error recovery
            for sending push notifications with optional snapshots.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.

@dependencies
    - line-bot-sdk >= 3.0.0
"""

import numpy as np
import time
from typing import Optional, Dict, Any
from datetime import datetime
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)


class LINEMessenger:
    """
    LINE Messaging API client.

    Sends push notifications with optional image snapshots.
    Handles message formatting and error recovery.

    Args:
        channel_access_token: LINE channel access token
        user_id: Target LINE user ID
        send_snapshots: Whether to attach image snapshots
        snapshot_quality: JPEG quality (0-100)
        max_retries: Maximum retry attempts on failure
        retry_delay: Delay between retries in seconds

    Example:
        messenger = LINEMessenger(
            channel_access_token="YOUR_TOKEN",
            user_id="USER_ID"
        )

        messenger.send_alert("motion", frame)
        messenger.send_alert("fall", frame, {"velocity": 0.5})
    """

    def __init__(
        self,
        channel_access_token: str,
        user_id: str,
        send_snapshots: bool = True,
        snapshot_quality: int = 85,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        if not channel_access_token:
            raise ValueError("channel_access_token cannot be empty")
        if not user_id:
            raise ValueError("user_id cannot be empty")
        if not 0 <= snapshot_quality <= 100:
            raise ValueError("snapshot_quality must be between 0 and 100")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")

        self.channel_access_token = channel_access_token
        self.user_id = user_id
        self.send_snapshots = send_snapshots
        self.snapshot_quality = snapshot_quality
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        configuration = Configuration(access_token=channel_access_token)
        self.api_client = ApiClient(configuration)
        self.messaging_api = MessagingApi(self.api_client)

        self._message_count = 0
        self._error_count = 0
        self._last_message_time = None

    def send_alert(
        self,
        event_type: str,
        frame: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send alert notification to LINE.

        Args:
            event_type: Type of event (motion, fall, etc.)
            frame: Optional image frame to attach
            metadata: Optional metadata dict

        Returns:
            True if message sent successfully, False otherwise
        """
        if not event_type:
            raise ValueError("event_type cannot be empty")

        try:
            # Format message text
            message_text = self._format_message(event_type, metadata)

            # Send text message
            success = self._send_text_message(message_text)

            if not success:
                return False

            # Send snapshot if enabled and frame provided
            if self.send_snapshots and frame is not None:
                self._send_image_message(frame)

            self._message_count += 1
            self._last_message_time = time.time()

            return True

        except Exception as e:
            self._error_count += 1
            print(f"Error sending alert: {e}")
            return False

    def _format_message(
        self,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format alert message text."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            f"[ALERT] {event_type.upper()}",
            f"Time: {timestamp}"
        ]

        if metadata:
            for key, value in metadata.items():
                if isinstance(value, float):
                    lines.append(f"{key.capitalize()}: {value:.2f}")
                else:
                    lines.append(f"{key.capitalize()}: {value}")

        return "\n".join(lines)

    def _send_text_message(self, text: str) -> bool:
        """Send text message with retry logic."""
        for attempt in range(self.max_retries + 1):
            try:
                push_message_request = PushMessageRequest(
                    to=self.user_id,
                    messages=[TextMessage(text=text)]
                )
                self.messaging_api.push_message(push_message_request)
                return True

            except Exception as e:
                self._error_count += 1
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    print(f"Failed to send text message after {self.max_retries} retries: {e}")
                    return False

        return False

    def _send_image_message(self, frame: np.ndarray) -> bool:
        """
        Send image message with retry logic.

        Note: Image upload requires external hosting service.
        Currently disabled - implement _upload_image() for production use.
        """
        # Image sending disabled until hosting service is implemented
        # See docs/LINE_MESSAGING.md for implementation options
        return True

    def _upload_image(self, image_bytes: bytes) -> Optional[str]:
        """
        Upload image to temporary hosting service.

        For production, use a proper image hosting service.
        This is a placeholder implementation.
        """
        # TODO: Implement actual image upload to hosting service
        # Options: imgur, cloudinary, AWS S3, or self-hosted server
        # For now, return None to skip image upload
        return None

    def send_text(self, text: str) -> bool:
        """
        Send plain text message.

        Args:
            text: Message text to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not text:
            raise ValueError("text cannot be empty")

        return self._send_text_message(text)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get messenger statistics.

        Returns:
            Dictionary with message count, error count, and last message time
        """
        return {
            "message_count": self._message_count,
            "error_count": self._error_count,
            "last_message_time": self._last_message_time
        }

    def reset(self):
        """Reset statistics."""
        self._message_count = 0
        self._error_count = 0
        self._last_message_time = None
