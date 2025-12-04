"""
Unit tests for MotionDetector.

Comprehensive test suite for motion detection including
contour analysis, false positive reduction, and callbacks.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import numpy as np
import cv2
import time
from src.detection.motion_detector import MotionDetector


class TestMotionDetector:
    """Test cases for MotionDetector class."""
    
    def test_initialization(self):
        """Test motion detector initialization."""
        detector = MotionDetector(min_area=500)
        assert detector.min_area == 500
        assert detector.blur_size == 21
        assert detector.threshold == 25
        assert detector.motion_count == 0
        assert detector.total_frames == 0
    
    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        detector = MotionDetector(
            min_area=1000,
            blur_size=15,
            threshold=30,
            dilate_iterations=3
        )
        assert detector.min_area == 1000
        assert detector.blur_size == 15
        assert detector.threshold == 30
        assert detector.dilate_iterations == 3
    
    def test_initialization_invalid_blur_size(self):
        """Test initialization with even blur size."""
        with pytest.raises(ValueError, match="blur_size must be odd"):
            MotionDetector(blur_size=20)
    
    def test_initialization_invalid_threshold(self):
        """Test initialization with invalid threshold."""
        with pytest.raises(ValueError, match="threshold must be between"):
            MotionDetector(threshold=300)
    
    def test_initialization_invalid_min_area(self):
        """Test initialization with negative min_area."""
        with pytest.raises(ValueError, match="min_area must be positive"):
            MotionDetector(min_area=-100)
    
    def test_detect_invalid_frame(self):
        """Test detect with invalid frame."""
        detector = MotionDetector()
        
        with pytest.raises(ValueError, match="Invalid frame"):
            detector.detect(None)
    
    def test_detect_empty_frame(self):
        """Test detect with empty frame."""
        detector = MotionDetector()
        empty_frame = np.array([])
        
        with pytest.raises(ValueError, match="Invalid frame"):
            detector.detect(empty_frame)
    
    def test_no_motion_static_frame(self):
        """Test no motion detected in static frame."""
        detector = MotionDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed same frame multiple times
        for _ in range(15):
            motion, boxes = detector.detect(frame)
        
        assert motion == False
        assert len(boxes) == 0
        assert detector.motion_detected == False
    
    def test_motion_detected(self):
        """Test motion detection with moving object."""
        detector = MotionDetector(min_area=100)
        
        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed background frames
        for _ in range(20):
            detector.detect(bg)
        
        # Create frame with moving object
        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (250, 250), (255, 255, 255), -1)
        
        motion, boxes = detector.detect(frame)
        
        assert motion == True
        assert len(boxes) > 0
        assert detector.motion_detected == True
        assert detector.motion_count > 0
    
    def test_motion_callback(self):
        """Test motion callback is called."""
        callback_called = False
        callback_frame = None
        callback_boxes = None
        
        def callback(frame, boxes):
            nonlocal callback_called, callback_frame, callback_boxes
            callback_called = True
            callback_frame = frame
            callback_boxes = boxes
        
        detector = MotionDetector(min_area=100, motion_callback=callback)
        
        # Create motion
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)
        
        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)
        detector.detect(frame)
        
        assert callback_called == True
        assert callback_frame is not None
        assert callback_boxes is not None
        assert len(callback_boxes) > 0
    
    def test_min_area_filtering(self):
        """Test minimum area filtering."""
        detector = MotionDetector(min_area=5000)
        
        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)
        
        # Create small moving object (below min_area)
        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (120, 120), (255, 255, 255), -1)
        
        motion, boxes = detector.detect(frame)
        
        # Small object should be filtered out
        assert motion == False
        assert len(boxes) == 0

    def test_draw_motion(self):
        """Test drawing bounding boxes on frame."""
        detector = MotionDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        boxes = [(100, 100, 50, 50), (200, 200, 60, 60)]

        output = detector.draw_motion(frame, boxes)

        assert output is not None
        assert output.shape == frame.shape
        assert not np.array_equal(output, frame)  # Should be different

    def test_draw_motion_custom_color(self):
        """Test drawing with custom color."""
        detector = MotionDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        boxes = [(100, 100, 50, 50)]

        output = detector.draw_motion(frame, boxes, color=(0, 0, 255), thickness=3)

        assert output is not None

    def test_get_stats(self):
        """Test getting motion statistics."""
        detector = MotionDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        detector.detect(frame)
        stats = detector.get_stats()

        assert "motion_detected" in stats
        assert "last_motion_time" in stats
        assert "motion_count" in stats
        assert "total_frames" in stats
        assert stats["total_frames"] == 1

    def test_reset(self):
        """Test reset functionality."""
        detector = MotionDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Process some frames
        for _ in range(10):
            detector.detect(frame)

        assert detector.total_frames == 10

        # Reset
        detector.reset()

        assert detector.total_frames == 0
        assert detector.motion_count == 0
        assert detector.motion_detected == False
        assert detector.last_motion_time is None

    def test_last_motion_time(self):
        """Test last motion time tracking."""
        detector = MotionDetector(min_area=100)

        # Create motion
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)

        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)

        before_time = time.time()
        detector.detect(frame)
        after_time = time.time()

        assert detector.last_motion_time is not None
        assert before_time <= detector.last_motion_time <= after_time

    def test_multiple_objects(self):
        """Test detection of multiple moving objects."""
        detector = MotionDetector(min_area=100)

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)

        # Create frame with multiple objects
        frame = bg.copy()
        cv2.rectangle(frame, (50, 50), (100, 100), (255, 255, 255), -1)
        cv2.rectangle(frame, (300, 300), (350, 350), (255, 255, 255), -1)

        motion, boxes = detector.detect(frame)

        assert motion == True
        assert len(boxes) >= 2  # Should detect both objects

    def test_pause_detection(self):
        """Test pausing motion detection."""
        detector = MotionDetector()

        # Create test frame with motion
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)

        # Detect motion normally
        detector.detect(bg)
        motion, boxes = detector.detect(frame)
        assert motion == True

        # Pause detection
        detector.pause()
        assert detector.is_paused() == True

        # Should not detect motion when paused
        motion, boxes = detector.detect(frame)
        assert motion == False
        assert len(boxes) == 0

    def test_resume_detection(self):
        """Test resuming motion detection."""
        detector = MotionDetector()

        # Create test frame with motion
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)

        # Pause and verify no detection
        detector.pause()
        detector.detect(bg)
        motion, boxes = detector.detect(frame)
        assert motion == False

        # Resume detection
        detector.resume()
        assert detector.is_paused() == False

        # Should detect motion again
        detector.detect(bg)
        motion, boxes = detector.detect(frame)
        assert motion == True

    def test_is_paused_initial_state(self):
        """Test is_paused returns False initially."""
        detector = MotionDetector()
        assert detector.is_paused() == False

