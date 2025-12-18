"""
Unit tests for BackgroundSubtractor.

Test suite for background subtraction algorithms including
MOG2 and KNN methods.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import numpy as np
import cv2
from src.detection.background_subtractor import BackgroundSubtractor


class TestBackgroundSubtractor:
    """Test cases for BackgroundSubtractor class."""
    
    def test_initialization_mog2(self):
        """Test MOG2 initialization."""
        subtractor = BackgroundSubtractor(method="MOG2")
        assert subtractor.method == "MOG2"
        assert subtractor.history == 500
        assert subtractor.var_threshold == 16
        assert subtractor.detect_shadows == True
    
    def test_initialization_knn(self):
        """Test KNN initialization."""
        subtractor = BackgroundSubtractor(method="KNN")
        assert subtractor.method == "KNN"
        assert subtractor.history == 500
    
    def test_initialization_invalid_method(self):
        """Test initialization with invalid method."""
        with pytest.raises(ValueError, match="Unknown method"):
            BackgroundSubtractor(method="INVALID")
    
    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        subtractor = BackgroundSubtractor(
            method="MOG2",
            history=1000,
            var_threshold=32,
            detect_shadows=False
        )
        assert subtractor.history == 1000
        assert subtractor.var_threshold == 32
        assert subtractor.detect_shadows == False
    
    def test_apply_valid_frame(self):
        """Test apply with valid frame."""
        subtractor = BackgroundSubtractor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        mask = subtractor.apply(frame)
        
        assert mask is not None
        assert mask.shape == (480, 640)
        assert mask.dtype == np.uint8
    
    def test_apply_invalid_frame(self):
        """Test apply with invalid frame."""
        subtractor = BackgroundSubtractor()
        
        with pytest.raises(ValueError, match="Invalid frame"):
            subtractor.apply(None)
    
    def test_apply_empty_frame(self):
        """Test apply with empty frame."""
        subtractor = BackgroundSubtractor()
        empty_frame = np.array([])
        
        with pytest.raises(ValueError, match="Invalid frame"):
            subtractor.apply(empty_frame)
    
    def test_apply_learning_rate(self):
        """Test apply with custom learning rate."""
        subtractor = BackgroundSubtractor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        mask = subtractor.apply(frame, learning_rate=0.5)
        
        assert mask is not None
    
    def test_static_background(self):
        """Test background subtraction with static frames."""
        subtractor = BackgroundSubtractor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed same frame multiple times
        for _ in range(10):
            mask = subtractor.apply(frame)
        
        # After learning, static frame should produce mostly background
        foreground_pixels = np.count_nonzero(mask)
        total_pixels = mask.size
        foreground_ratio = foreground_pixels / total_pixels
        
        assert foreground_ratio < 0.1  # Less than 10% foreground
    
    def test_moving_object_detection(self):
        """Test detection of moving object."""
        subtractor = BackgroundSubtractor()
        
        # Create static background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Feed background frames
        for _ in range(20):
            subtractor.apply(bg)
        
        # Create frame with moving object
        frame = bg.copy()
        cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)
        
        mask = subtractor.apply(frame)
        
        # Should detect foreground in the rectangle area
        roi = mask[100:200, 100:200]
        foreground_pixels = np.count_nonzero(roi)
        
        assert foreground_pixels > 0
    
    def test_shadow_detection(self):
        """Test shadow detection when enabled."""
        subtractor = BackgroundSubtractor(detect_shadows=True)

        # Create background
        bg = np.zeros((480, 640, 3), dtype=np.uint8)

        # Feed background frames to build model
        for _ in range(20):
            subtractor.apply(bg)

        # After learning, background should be detected
        mask = subtractor.apply(bg)

        # Background pixels should be 0
        unique_values = np.unique(mask)
        assert 0 in unique_values  # Background
        # Note: Shadows (127) may not appear without actual shadow in frame
    
    def test_reset(self):
        """Test reset functionality."""
        subtractor = BackgroundSubtractor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process some frames
        for _ in range(10):
            subtractor.apply(frame)
        
        # Reset
        subtractor.reset()
        
        # After reset, should behave like new instance
        mask = subtractor.apply(frame)
        assert mask is not None

