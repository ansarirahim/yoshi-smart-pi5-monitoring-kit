"""
Unit tests for RTSPStreamHandler
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.rtsp.stream_handler import RTSPStreamHandler
import time


class TestRTSPStreamHandler:
    """Test cases for RTSPStreamHandler class"""
    
    def test_initialization(self):
        """Test stream handler initialization"""
        handler = RTSPStreamHandler(
            rtsp_url="rtsp://test:test@localhost:554/stream",
            reconnect_delay=5,
            max_reconnect_attempts=10
        )
        
        assert handler.rtsp_url == "rtsp://test:test@localhost:554/stream"
        assert handler.reconnect_delay == 5
        assert handler.max_reconnect_attempts == 10
        assert handler.is_running is False
        assert handler.is_connected is False
    
    def test_mask_credentials(self):
        """Test credential masking in URLs"""
        handler = RTSPStreamHandler("rtsp://user:pass@192.168.1.100:554/stream")
        
        masked = handler._mask_credentials(handler.rtsp_url)
        
        assert "user" not in masked
        assert "pass" not in masked
        assert "***:***" in masked
        assert "192.168.1.100" in masked
    
    @patch('cv2.VideoCapture')
    def test_connect_success(self, mock_capture_class):
        """Test successful connection to RTSP stream"""
        # Mock VideoCapture
        mock_capture = MagicMock()
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_capture.get.side_effect = [640, 480, 15]  # width, height, fps
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        result = handler.connect()
        
        assert result is True
        assert handler.is_connected is True
        assert handler.reconnect_count == 0
    
    @patch('cv2.VideoCapture')
    def test_connect_failure(self, mock_capture_class):
        """Test failed connection to RTSP stream"""
        # Mock VideoCapture that fails to read
        mock_capture = MagicMock()
        mock_capture.read.return_value = (False, None)
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        result = handler.connect()
        
        assert result is False
        assert handler.is_connected is False
    
    @patch('cv2.VideoCapture')
    def test_disconnect(self, mock_capture_class):
        """Test disconnection from stream"""
        mock_capture = MagicMock()
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        handler.connect()
        
        assert handler.is_connected is True
        
        handler.disconnect()
        
        assert handler.is_connected is False
        mock_capture.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_read_frame_success(self, mock_capture_class):
        """Test reading frame successfully"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture = MagicMock()
        mock_capture.read.return_value = (True, test_frame)
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture

        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        handler.connect()

        ret, frame = handler.read_frame()

        assert ret is True
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        assert handler.frame_count >= 1  # At least 1 frame read
    
    @patch('cv2.VideoCapture')
    def test_read_frame_failure(self, mock_capture_class):
        """Test reading frame failure"""
        mock_capture = MagicMock()
        # First read succeeds (for connect), second fails
        mock_capture.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (False, None)
        ]
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        handler.connect()
        
        ret, frame = handler.read_frame()
        
        assert ret is False
        assert frame is None
        assert handler.error_count == 1
    
    @patch('cv2.VideoCapture')
    def test_frame_callback(self, mock_capture_class):
        """Test frame callback functionality"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture = MagicMock()
        mock_capture.read.return_value = (True, test_frame)
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture
        
        callback_mock = Mock()
        handler = RTSPStreamHandler(
            "rtsp://test:test@localhost:554/stream",
            frame_callback=callback_mock
        )
        handler.connect()
        
        # Start and let it run briefly
        handler.start()
        time.sleep(0.5)
        handler.stop()
        
        # Callback should have been called
        assert callback_mock.call_count > 0
    
    def test_get_stats(self):
        """Test getting stream statistics"""
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        
        stats = handler.get_stats()
        
        assert 'is_connected' in stats
        assert 'is_running' in stats
        assert 'frame_count' in stats
        assert 'error_count' in stats
        assert 'reconnect_count' in stats
        assert 'fps' in stats
        
        assert stats['is_connected'] is False
        assert stats['frame_count'] == 0
    
    @patch('cv2.VideoCapture')
    def test_start_stop_stream(self, mock_capture_class):
        """Test starting and stopping stream"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture = MagicMock()
        mock_capture.read.return_value = (True, test_frame)
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        
        assert handler.is_running is False
        
        handler.start()
        time.sleep(0.2)
        
        assert handler.is_running is True
        
        handler.stop()
        
        assert handler.is_running is False
    
    @patch('cv2.VideoCapture')
    @patch('time.sleep')
    def test_reconnection_logic(self, mock_sleep, mock_capture_class):
        """Test automatic reconnection logic"""
        mock_capture = MagicMock()
        # First attempt fails, second succeeds
        mock_capture.read.side_effect = [
            (False, None),  # First connect fails
            (True, np.zeros((480, 640, 3), dtype=np.uint8))  # Second connect succeeds
        ]
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture

        handler = RTSPStreamHandler(
            "rtsp://test:test@localhost:554/stream",
            reconnect_delay=1,
            max_reconnect_attempts=3
        )

        # First connection fails
        result1 = handler.connect()
        assert result1 is False
        assert handler.reconnect_count == 0  # Connect doesn't increment reconnect_count

        # Attempt reconnection
        result2 = handler._attempt_reconnect()
        assert result2 is True
        # After successful reconnect, count is reset to 0
        assert handler.reconnect_count == 0
    
    @patch('cv2.VideoCapture')
    def test_max_reconnect_attempts(self, mock_capture_class):
        """Test max reconnection attempts limit"""
        mock_capture = MagicMock()
        mock_capture.read.return_value = (False, None)
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler(
            "rtsp://test:test@localhost:554/stream",
            reconnect_delay=0.1,
            max_reconnect_attempts=2
        )
        
        # Exhaust reconnection attempts
        for i in range(3):
            handler._attempt_reconnect()
        
        # Should stop trying after max attempts
        assert handler.reconnect_count >= 2
        assert handler.is_running is False
    
    @patch('cv2.VideoCapture')
    def test_fps_calculation(self, mock_capture_class):
        """Test FPS calculation"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture = MagicMock()
        mock_capture.read.return_value = (True, test_frame)
        mock_capture.get.side_effect = [640, 480, 15]
        mock_capture_class.return_value = mock_capture
        
        handler = RTSPStreamHandler("rtsp://test:test@localhost:554/stream")
        handler.connect()
        
        # Read multiple frames
        for i in range(5):
            handler.read_frame()
            time.sleep(0.1)
        
        stats = handler.get_stats()
        
        # FPS should be calculated
        assert stats['fps'] > 0

