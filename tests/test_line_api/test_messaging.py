"""
Tests for LINE Messaging Module.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch

from src.line_api.messaging import LINEMessenger


class TestLINEMessenger(unittest.TestCase):
    """Test cases for LINEMessenger class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.token = "test_channel_access_token"
        self.user_id = "test_user_id"
    
    def test_initialization(self):
        """Test messenger initialization with default parameters"""
        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id
        )
        
        self.assertEqual(messenger.channel_access_token, self.token)
        self.assertEqual(messenger.user_id, self.user_id)
        self.assertTrue(messenger.send_snapshots)
        self.assertEqual(messenger.snapshot_quality, 85)
        self.assertEqual(messenger.max_retries, 3)
        self.assertEqual(messenger.retry_delay, 2.0)
    
    def test_initialization_custom_params(self):
        """Test messenger initialization with custom parameters"""
        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False,
            snapshot_quality=70,
            max_retries=5,
            retry_delay=1.0
        )
        
        self.assertFalse(messenger.send_snapshots)
        self.assertEqual(messenger.snapshot_quality, 70)
        self.assertEqual(messenger.max_retries, 5)
        self.assertEqual(messenger.retry_delay, 1.0)
    
    def test_initialization_empty_token(self):
        """Test initialization with empty token"""
        with self.assertRaises(ValueError) as context:
            LINEMessenger(
                channel_access_token="",
                user_id=self.user_id
            )
        self.assertIn("channel_access_token", str(context.exception))
    
    def test_initialization_empty_user_id(self):
        """Test initialization with empty user ID"""
        with self.assertRaises(ValueError) as context:
            LINEMessenger(
                channel_access_token=self.token,
                user_id=""
            )
        self.assertIn("user_id", str(context.exception))
    
    def test_initialization_invalid_quality(self):
        """Test initialization with invalid snapshot quality"""
        with self.assertRaises(ValueError) as context:
            LINEMessenger(
                channel_access_token=self.token,
                user_id=self.user_id,
                snapshot_quality=150
            )
        self.assertIn("snapshot_quality", str(context.exception))
    
    def test_initialization_negative_retries(self):
        """Test initialization with negative max retries"""
        with self.assertRaises(ValueError) as context:
            LINEMessenger(
                channel_access_token=self.token,
                user_id=self.user_id,
                max_retries=-1
            )
        self.assertIn("max_retries", str(context.exception))
    
    def test_initialization_negative_delay(self):
        """Test initialization with negative retry delay"""
        with self.assertRaises(ValueError) as context:
            LINEMessenger(
                channel_access_token=self.token,
                user_id=self.user_id,
                retry_delay=-1.0
            )
        self.assertIn("retry_delay", str(context.exception))
    
    @patch('src.line_api.messaging.MessagingApi')
    def test_send_alert_text_only(self, mock_messaging_api):
        """Test sending alert with text only"""
        mock_api = Mock()
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False
        )

        result = messenger.send_alert("motion")

        self.assertTrue(result)
        self.assertEqual(mock_api.push_message.call_count, 1)
        self.assertEqual(messenger.get_stats()["message_count"], 1)
    
    @patch('src.line_api.messaging.MessagingApi')
    def test_send_alert_with_metadata(self, mock_messaging_api):
        """Test sending alert with metadata"""
        mock_api = Mock()
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False
        )

        metadata = {"velocity": 0.5, "confidence": 0.85}
        result = messenger.send_alert("fall", metadata=metadata)

        self.assertTrue(result)
        self.assertEqual(messenger.get_stats()["message_count"], 1)

    @patch('src.line_api.messaging.MessagingApi')
    def test_send_alert_empty_event_type(self, mock_messaging_api):
        """Test sending alert with empty event type"""
        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id
        )

        with self.assertRaises(ValueError) as context:
            messenger.send_alert("")
        self.assertIn("event_type", str(context.exception))

    @patch('src.line_api.messaging.MessagingApi')
    def test_send_alert_with_frame(self, mock_messaging_api):
        """Test sending alert with image frame"""
        mock_api = Mock()
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=True
        )

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = messenger.send_alert("motion", frame=frame)

        self.assertTrue(result)
        self.assertEqual(messenger.get_stats()["message_count"], 1)

    @patch('src.line_api.messaging.MessagingApi')
    def test_send_text(self, mock_messaging_api):
        """Test sending plain text message"""
        mock_api = Mock()
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id
        )

        result = messenger.send_text("Test message")

        self.assertTrue(result)
        mock_api.push_message.assert_called_once()

    @patch('src.line_api.messaging.MessagingApi')
    def test_send_text_empty(self, mock_messaging_api):
        """Test sending empty text message"""
        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id
        )

        with self.assertRaises(ValueError) as context:
            messenger.send_text("")
        self.assertIn("text", str(context.exception))

    @patch('src.line_api.messaging.MessagingApi')
    def test_send_alert_api_error(self, mock_messaging_api):
        """Test handling LINE API error"""
        mock_api = Mock()
        mock_api.push_message.side_effect = Exception("API Error")
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False,
            max_retries=1,
            retry_delay=0.1
        )

        result = messenger.send_alert("motion")

        self.assertFalse(result)
        self.assertGreater(messenger.get_stats()["error_count"], 0)

    @patch('src.line_api.messaging.MessagingApi')
    def test_send_alert_retry_success(self, mock_messaging_api):
        """Test successful retry after initial failure"""
        mock_api = Mock()
        mock_api.push_message.side_effect = [
            Exception("Temporary error"),
            None
        ]
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False,
            max_retries=2,
            retry_delay=0.1
        )

        result = messenger.send_alert("motion")

        self.assertTrue(result)
        self.assertEqual(mock_api.push_message.call_count, 2)

    @patch('src.line_api.messaging.MessagingApi')
    def test_format_message(self, mock_messaging_api):
        """Test message formatting"""
        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id
        )

        message = messenger._format_message("motion", {"area": 1500})

        self.assertIn("MOTION", message)
        self.assertIn("Time:", message)
        self.assertIn("Area:", message)

    @patch('src.line_api.messaging.MessagingApi')
    def test_get_stats(self, mock_messaging_api):
        """Test getting messenger statistics"""
        mock_api = Mock()
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False
        )

        messenger.send_alert("motion")
        stats = messenger.get_stats()

        self.assertEqual(stats["message_count"], 1)
        self.assertEqual(stats["error_count"], 0)
        self.assertIsNotNone(stats["last_message_time"])

    @patch('src.line_api.messaging.MessagingApi')
    def test_reset(self, mock_messaging_api):
        """Test resetting statistics"""
        mock_api = Mock()
        mock_messaging_api.return_value = mock_api

        messenger = LINEMessenger(
            channel_access_token=self.token,
            user_id=self.user_id,
            send_snapshots=False
        )

        messenger.send_alert("motion")
        messenger.reset()
        stats = messenger.get_stats()

        self.assertEqual(stats["message_count"], 0)
        self.assertEqual(stats["error_count"], 0)
        self.assertIsNone(stats["last_message_time"])


if __name__ == "__main__":
    unittest.main()

