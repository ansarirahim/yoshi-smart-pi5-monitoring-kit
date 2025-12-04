"""
Unit tests for FrameBuffer.

Comprehensive test suite for frame buffer including thread safety,
overflow handling, and statistics tracking.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import numpy as np
import time
from src.rtsp.frame_buffer import FrameBuffer


class TestFrameBuffer:
    """Test cases for FrameBuffer class"""
    
    def test_initialization(self):
        """Test buffer initialization"""
        buffer = FrameBuffer(max_size=10)
        
        assert buffer.max_size == 10
        assert buffer.is_empty()
        assert not buffer.is_full()
        assert buffer.size() == 0
    
    def test_add_frame(self):
        """Test adding frames to buffer"""
        buffer = FrameBuffer(max_size=5)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = buffer.add_frame(frame)
        
        assert result is True
        assert buffer.size() == 1
        assert not buffer.is_empty()
    
    def test_add_none_frame(self):
        """Test adding None frame returns False"""
        buffer = FrameBuffer(max_size=5)
        
        result = buffer.add_frame(None)
        
        assert result is False
        assert buffer.size() == 0
    
    def test_get_latest_frame(self):
        """Test retrieving latest frame"""
        buffer = FrameBuffer(max_size=5)
        
        # Add multiple frames
        for i in range(3):
            frame = np.ones((480, 640, 3), dtype=np.uint8) * i
            buffer.add_frame(frame)
        
        # Get latest frame
        frame_data = buffer.get_latest_frame()
        
        assert frame_data is not None
        assert frame_data['index'] == 2
        assert np.all(frame_data['frame'] == 2)
    
    def test_get_oldest_frame(self):
        """Test retrieving oldest frame"""
        buffer = FrameBuffer(max_size=5)
        
        # Add multiple frames
        for i in range(3):
            frame = np.ones((480, 640, 3), dtype=np.uint8) * i
            buffer.add_frame(frame)
        
        # Get oldest frame
        frame_data = buffer.get_oldest_frame()
        
        assert frame_data is not None
        assert frame_data['index'] == 0
        assert np.all(frame_data['frame'] == 0)
    
    def test_get_frame_at_index(self):
        """Test retrieving frame at specific index"""
        buffer = FrameBuffer(max_size=5)
        
        # Add frames
        for i in range(3):
            frame = np.ones((480, 640, 3), dtype=np.uint8) * i
            buffer.add_frame(frame)
        
        # Get middle frame
        frame_data = buffer.get_frame_at_index(1)
        
        assert frame_data is not None
        assert frame_data['index'] == 1
        assert np.all(frame_data['frame'] == 1)
    
    def test_get_frame_invalid_index(self):
        """Test retrieving frame with invalid index"""
        buffer = FrameBuffer(max_size=5)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        buffer.add_frame(frame)
        
        # Try to get frame at invalid index
        frame_data = buffer.get_frame_at_index(10)
        
        assert frame_data is None
    
    def test_buffer_overflow(self):
        """Test buffer behavior when max size exceeded"""
        buffer = FrameBuffer(max_size=3)
        
        # Add more frames than max size
        for i in range(5):
            frame = np.ones((480, 640, 3), dtype=np.uint8) * i
            buffer.add_frame(frame)
        
        # Buffer should only contain last 3 frames
        assert buffer.size() == 3
        assert buffer.is_full()
        
        # Oldest frame should be frame 2 (frames 0 and 1 dropped)
        oldest = buffer.get_oldest_frame()
        assert oldest['index'] == 2
    
    def test_get_all_frames(self):
        """Test retrieving all frames"""
        buffer = FrameBuffer(max_size=5)
        
        # Add frames
        for i in range(3):
            frame = np.ones((480, 640, 3), dtype=np.uint8) * i
            buffer.add_frame(frame)
        
        # Get all frames
        all_frames = buffer.get_all_frames()
        
        assert len(all_frames) == 3
        assert all_frames[0]['index'] == 0
        assert all_frames[2]['index'] == 2
    
    def test_clear_buffer(self):
        """Test clearing buffer"""
        buffer = FrameBuffer(max_size=5)
        
        # Add frames
        for i in range(3):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            buffer.add_frame(frame)
        
        assert buffer.size() == 3
        
        # Clear buffer
        buffer.clear()
        
        assert buffer.size() == 0
        assert buffer.is_empty()
    
    def test_get_stats(self):
        """Test getting buffer statistics"""
        buffer = FrameBuffer(max_size=5)
        
        # Add frames
        for i in range(3):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            buffer.add_frame(frame)
        
        # Get one frame
        buffer.get_latest_frame()
        
        stats = buffer.get_stats()
        
        assert stats['current_size'] == 3
        assert stats['max_size'] == 5
        assert stats['frames_added'] == 3
        assert stats['frames_retrieved'] == 1
        assert stats['is_empty'] is False
        assert stats['is_full'] is False
    
    def test_frame_rate_calculation(self):
        """Test frame rate calculation"""
        buffer = FrameBuffer(max_size=10)
        
        # Add frames with known timestamps
        base_time = time.time()
        for i in range(5):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            timestamp = base_time + (i * 0.1)  # 10 FPS
            buffer.add_frame(frame, timestamp=timestamp)
        
        fps = buffer.get_frame_rate(window_size=5)
        
        # Should be approximately 10 FPS
        assert 9.0 <= fps <= 11.0
    
    def test_empty_buffer_operations(self):
        """Test operations on empty buffer"""
        buffer = FrameBuffer(max_size=5)
        
        assert buffer.get_latest_frame() is None
        assert buffer.get_oldest_frame() is None
        assert buffer.get_all_frames() == []
        assert buffer.get_frame_rate() == 0.0
    
    def test_thread_safety(self):
        """Test thread-safe operations"""
        import threading
        
        buffer = FrameBuffer(max_size=100)
        
        def add_frames():
            for i in range(50):
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                buffer.add_frame(frame)
        
        def get_frames():
            for i in range(50):
                buffer.get_latest_frame()
        
        # Run operations in parallel threads
        t1 = threading.Thread(target=add_frames)
        t2 = threading.Thread(target=get_frames)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Should complete without errors
        assert buffer.frames_added == 50

