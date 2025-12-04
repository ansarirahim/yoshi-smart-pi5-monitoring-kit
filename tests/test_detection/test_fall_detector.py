"""
Unit tests for FallDetector.

Comprehensive test suite for fall detection including
aspect ratio analysis, state transitions, and fall patterns.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import numpy as np
import cv2
import time
from src.detection.fall_detector import FallDetector, PersonState


class TestFallDetector:
    """Test cases for FallDetector class."""
    
    def test_initialization(self):
        """Test fall detector initialization."""
        detector = FallDetector()
        assert detector.aspect_ratio_threshold == 1.5
        assert detector.fall_velocity_threshold == 0.3
        assert detector.inactivity_timeout == 10.0
        assert detector.min_person_area == 2000
        assert detector.fall_detected == False
        assert detector.current_state == PersonState.UNKNOWN
    
    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        detector = FallDetector(
            aspect_ratio_threshold=2.0,
            fall_velocity_threshold=0.5,
            inactivity_timeout=15.0,
            min_person_area=3000
        )
        assert detector.aspect_ratio_threshold == 2.0
        assert detector.fall_velocity_threshold == 0.5
        assert detector.inactivity_timeout == 15.0
        assert detector.min_person_area == 3000
    
    def test_initialization_invalid_aspect_ratio(self):
        """Test initialization with invalid aspect ratio."""
        with pytest.raises(ValueError, match="aspect_ratio_threshold must be positive"):
            FallDetector(aspect_ratio_threshold=-1.0)
    
    def test_initialization_invalid_velocity(self):
        """Test initialization with invalid velocity threshold."""
        with pytest.raises(ValueError, match="fall_velocity_threshold must be between"):
            FallDetector(fall_velocity_threshold=1.5)
    
    def test_initialization_invalid_timeout(self):
        """Test initialization with invalid timeout."""
        with pytest.raises(ValueError, match="inactivity_timeout must be positive"):
            FallDetector(inactivity_timeout=-5.0)
    
    def test_initialization_invalid_min_area(self):
        """Test initialization with invalid min area."""
        with pytest.raises(ValueError, match="min_person_area must be positive"):
            FallDetector(min_person_area=-100)
    
    def test_detect_invalid_frame(self):
        """Test detect with invalid frame."""
        detector = FallDetector()
        
        with pytest.raises(ValueError, match="Invalid frame"):
            detector.detect(None)
    
    def test_detect_empty_frame(self):
        """Test detect with empty frame."""
        detector = FallDetector()
        empty_frame = np.array([])
        
        with pytest.raises(ValueError, match="Invalid frame"):
            detector.detect(empty_frame)
    
    def test_no_person_detected(self):
        """Test detection with no person in frame."""
        detector = FallDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed same frame multiple times
        for _ in range(20):
            fall, state, bbox = detector.detect(frame)
        
        assert fall == False
        assert state == PersonState.UNKNOWN
        assert bbox is None
    
    def test_standing_person_detection(self):
        """Test detection of standing person."""
        detector = FallDetector(min_person_area=1000)
        
        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed background frames
        for _ in range(20):
            detector.detect(bg)
        
        # Create frame with tall vertical person (standing)
        frame = bg.copy()
        cv2.rectangle(frame, (250, 100), (350, 400), (255, 255, 255), -1)
        
        fall, state, bbox = detector.detect(frame)
        
        assert fall == False
        assert state == PersonState.STANDING
        assert bbox is not None
    
    def test_lying_person_detection(self):
        """Test detection of lying person."""
        detector = FallDetector(min_person_area=1000)
        
        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed background frames
        for _ in range(20):
            detector.detect(bg)
        
        # Create frame with horizontal person (lying)
        frame = bg.copy()
        cv2.rectangle(frame, (100, 300), (400, 350), (255, 255, 255), -1)
        
        fall, state, bbox = detector.detect(frame)
        
        assert fall == False
        assert state == PersonState.LYING
        assert bbox is not None
    
    def test_sitting_person_detection(self):
        """Test detection of sitting person."""
        detector = FallDetector(min_person_area=1000)
        
        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed background frames
        for _ in range(20):
            detector.detect(bg)
        
        # Create frame with square-ish person (sitting)
        frame = bg.copy()
        cv2.rectangle(frame, (250, 250), (350, 380), (255, 255, 255), -1)
        
        fall, state, bbox = detector.detect(frame)
        
        assert fall == False
        assert state == PersonState.SITTING
        assert bbox is not None

    def test_fall_detection_standing_to_lying(self):
        """Test fall detection from standing to lying transition."""
        detector = FallDetector(
            min_person_area=1000,
            fall_velocity_threshold=0.2
        )

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)

        # Feed background frames
        for _ in range(20):
            detector.detect(bg)

        # Create standing person
        frame1 = bg.copy()
        cv2.rectangle(frame1, (250, 100), (350, 400), (255, 255, 255), -1)

        # Process standing frames
        for _ in range(5):
            detector.detect(frame1)

        # Create lying person (simulating fall)
        frame2 = bg.copy()
        cv2.rectangle(frame2, (100, 350), (400, 400), (255, 255, 255), -1)

        fall, state, bbox = detector.detect(frame2)

        # Should detect fall due to standing->lying transition
        assert fall == True
        assert state == PersonState.FALLEN
        assert detector.fall_count == 1

    def test_fall_callback(self):
        """Test fall callback is called."""
        callback_called = False
        callback_frame = None
        callback_bbox = None
        callback_velocity = None

        def callback(frame, bbox, velocity):
            nonlocal callback_called, callback_frame, callback_bbox, callback_velocity
            callback_called = True
            callback_frame = frame
            callback_bbox = bbox
            callback_velocity = velocity

        detector = FallDetector(
            min_person_area=1000,
            fall_velocity_threshold=0.2,
            fall_callback=callback
        )

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)

        # Standing person
        frame1 = bg.copy()
        cv2.rectangle(frame1, (250, 100), (350, 400), (255, 255, 255), -1)
        for _ in range(5):
            detector.detect(frame1)

        # Lying person (fall)
        frame2 = bg.copy()
        cv2.rectangle(frame2, (100, 350), (400, 400), (255, 255, 255), -1)
        detector.detect(frame2)

        assert callback_called == True
        assert callback_frame is not None
        assert callback_bbox is not None
        assert callback_velocity >= 0

    def test_inactivity_timeout(self):
        """Test fall detection via inactivity timeout."""
        detector = FallDetector(
            min_person_area=1000,
            inactivity_timeout=0.5  # Short timeout for testing
        )

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)

        # Create lying person
        frame = bg.copy()
        cv2.rectangle(frame, (100, 300), (400, 350), (255, 255, 255), -1)

        # First detection - no fall yet
        fall, state, bbox = detector.detect(frame)
        assert fall == False
        assert state == PersonState.LYING

        # Wait for timeout
        time.sleep(0.6)

        # Should detect fall due to prolonged inactivity
        fall, state, bbox = detector.detect(frame)
        assert fall == True
        assert state == PersonState.FALLEN

    def test_draw_detection(self):
        """Test drawing detection visualization."""
        detector = FallDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = (100, 100, 50, 150)

        output = detector.draw_detection(frame, bbox, PersonState.STANDING)

        assert output is not None
        assert output.shape == frame.shape
        assert not np.array_equal(output, frame)

    def test_draw_detection_fall_state(self):
        """Test drawing with fall state."""
        detector = FallDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = (100, 100, 200, 50)

        output = detector.draw_detection(frame, bbox, PersonState.FALLEN)

        assert output is not None

    def test_draw_detection_no_bbox(self):
        """Test drawing with no bounding box."""
        detector = FallDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        output = detector.draw_detection(frame, None, PersonState.UNKNOWN)

        assert np.array_equal(output, frame)

    def test_get_stats(self):
        """Test getting fall detection statistics."""
        detector = FallDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        detector.detect(frame)
        stats = detector.get_stats()

        assert "fall_detected" in stats
        assert "current_state" in stats
        assert "fall_time" in stats
        assert "fall_count" in stats
        assert "total_frames" in stats
        assert stats["total_frames"] == 1

    def test_reset(self):
        """Test reset functionality."""
        detector = FallDetector(min_person_area=1000)

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)

        # Process some frames
        frame = bg.copy()
        cv2.rectangle(frame, (250, 100), (350, 400), (255, 255, 255), -1)
        for _ in range(10):
            detector.detect(frame)

        assert detector.total_frames > 0

        # Reset
        detector.reset()

        assert detector.total_frames == 0
        assert detector.fall_count == 0
        assert detector.fall_detected == False
        assert detector.current_state == PersonState.UNKNOWN

    def test_aspect_ratio_calculation(self):
        """Test aspect ratio determines correct state."""
        detector = FallDetector(
            min_person_area=1000,
            aspect_ratio_threshold=1.5
        )

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        for _ in range(20):
            detector.detect(bg)

        # Tall person (AR > 1.5) - should be standing
        frame1 = bg.copy()
        cv2.rectangle(frame1, (250, 100), (350, 400), (255, 255, 255), -1)
        fall, state, bbox = detector.detect(frame1)
        assert state == PersonState.STANDING

        # Wide person (AR < 1.0) - should be lying
        frame2 = bg.copy()
        cv2.rectangle(frame2, (100, 300), (400, 350), (255, 255, 255), -1)
        fall, state, bbox = detector.detect(frame2)
        assert state == PersonState.LYING

    def test_pause_detection(self):
        """Test pausing fall detection."""
        detector = FallDetector()

        # Create test frame with person
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = bg.copy()
        cv2.rectangle(frame, (250, 100), (350, 400), (255, 255, 255), -1)

        # Detect normally
        detector.detect(bg)
        fall, state, bbox = detector.detect(frame)
        assert state != PersonState.UNKNOWN

        # Pause detection
        detector.pause()
        assert detector.is_paused() == True

        # Should not detect when paused
        fall, state, bbox = detector.detect(frame)
        assert fall == False
        assert state == PersonState.UNKNOWN
        assert bbox is None

    def test_resume_detection(self):
        """Test resuming fall detection."""
        detector = FallDetector()

        # Create test frame with person
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = bg.copy()
        cv2.rectangle(frame, (250, 100), (350, 400), (255, 255, 255), -1)

        # Pause and verify no detection
        detector.pause()
        detector.detect(bg)
        fall, state, bbox = detector.detect(frame)
        assert state == PersonState.UNKNOWN

        # Resume detection
        detector.resume()
        assert detector.is_paused() == False

        # Should detect again
        detector.detect(bg)
        fall, state, bbox = detector.detect(frame)
        assert state != PersonState.UNKNOWN

    def test_is_paused_initial_state(self):
        """Test is_paused returns False initially."""
        detector = FallDetector()
        assert detector.is_paused() == False

