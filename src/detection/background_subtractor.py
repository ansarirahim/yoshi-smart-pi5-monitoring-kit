"""
Background Subtraction Module.

Implements background subtraction using OpenCV MOG2/KNN algorithms
for motion detection in video streams.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import cv2
import numpy as np
from typing import Optional


class BackgroundSubtractor:
    """
    Background subtraction for motion detection.
    
    Uses OpenCV's MOG2 or KNN algorithms to separate foreground
    (moving objects) from background (static scene).
    """
    
    def __init__(
        self,
        method: str = "MOG2",
        history: int = 500,
        var_threshold: float = 16,
        detect_shadows: bool = True
    ):
        """
        Initialize background subtractor.
        
        Args:
            method: Algorithm to use ("MOG2" or "KNN")
            history: Number of frames for background model
            var_threshold: Threshold for pixel classification
            detect_shadows: Whether to detect shadows
            
        Raises:
            ValueError: If method is not "MOG2" or "KNN"
        """
        self.method = method
        self.history = history
        self.var_threshold = var_threshold
        self.detect_shadows = detect_shadows
        
        if method == "MOG2":
            self.subtractor = cv2.createBackgroundSubtractorMOG2(
                history=history,
                varThreshold=var_threshold,
                detectShadows=detect_shadows
            )
        elif method == "KNN":
            self.subtractor = cv2.createBackgroundSubtractorKNN(
                history=history,
                dist2Threshold=var_threshold,
                detectShadows=detect_shadows
            )
        else:
            raise ValueError(f"Unknown method: {method}. Use 'MOG2' or 'KNN'")
    
    def apply(self, frame: np.ndarray, learning_rate: float = -1) -> np.ndarray:
        """
        Apply background subtraction to frame.
        
        Args:
            frame: Input frame in BGR format
            learning_rate: Learning rate for background model (-1 for automatic)
            
        Returns:
            Binary mask with detected foreground (255) and background (0)
            
        Note:
            Shadows are marked as 127 if detect_shadows is True
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is None or empty")
        
        return self.subtractor.apply(frame, learningRate=learning_rate)
    
    def get_background(self) -> Optional[np.ndarray]:
        """
        Get current background model.
        
        Returns:
            Background image or None if not available
        """
        try:
            return self.subtractor.getBackgroundImage()
        except cv2.error:
            return None
    
    def reset(self):
        """
        Reset background model.
        
        Recreates the background subtractor with original parameters.
        """
        if self.method == "MOG2":
            self.subtractor = cv2.createBackgroundSubtractorMOG2(
                history=self.history,
                varThreshold=self.var_threshold,
                detectShadows=self.detect_shadows
            )
        elif self.method == "KNN":
            self.subtractor = cv2.createBackgroundSubtractorKNN(
                history=self.history,
                dist2Threshold=self.var_threshold,
                detectShadows=self.detect_shadows
            )

