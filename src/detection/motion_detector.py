#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motion Detection Module.

@file       motion_detector.py
@brief      Detects motion in video streams.
@details    Uses background subtraction and contour analysis
            with false positive reduction for reliable detection.

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
    - opencv-python >= 4.5.0
"""

import cv2
import numpy as np
import time
from typing import List, Tuple, Optional, Callable
from .background_subtractor import BackgroundSubtractor


class MotionDetector:
    """
    Motion detection using background subtraction and contour analysis.

    Detects moving objects in video frames and filters false positives
    caused by lighting changes, shadows, and noise.
    """

    def __init__(
        self,
        min_area: int = 500,
        blur_size: int = 21,
        threshold: int = 25,
        dilate_iterations: int = 2,
        motion_callback: Optional[Callable] = None
    ):
        """
        Initialize motion detector.

        Args:
            min_area: Minimum contour area to consider as motion (pixels)
            blur_size: Gaussian blur kernel size (must be odd)
            threshold: Binary threshold value (0-255)
            dilate_iterations: Morphological dilation iterations
            motion_callback: Callback function(frame, boxes) when motion detected

        Raises:
            ValueError: If blur_size is not odd or parameters are invalid
        """
        if blur_size % 2 == 0:
            raise ValueError("blur_size must be odd")
        if threshold < 0 or threshold > 255:
            raise ValueError("threshold must be between 0 and 255")
        if min_area < 0:
            raise ValueError("min_area must be positive")

        self.min_area = min_area
        self.blur_size = blur_size
        self.threshold = threshold
        self.dilate_iterations = dilate_iterations
        self.motion_callback = motion_callback

        self.bg_subtractor = BackgroundSubtractor(method="MOG2")
        self.motion_detected = False
        self.last_motion_time = None
        self.motion_count = 0
        self.total_frames = 0
        self.paused = False

    def detect(self, frame: np.ndarray) -> Tuple[bool, List[Tuple[int, int, int, int]]]:
        """
        Detect motion in frame.

        Args:
            frame: Input frame in BGR format

        Returns:
            Tuple of (motion_detected, bounding_boxes)
            bounding_boxes: List of (x, y, w, h) tuples for each detected motion

        Raises:
            ValueError: If frame is None or invalid
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is None or empty")

        # If paused, return no motion
        if self.paused:
            return False, []

        self.total_frames += 1

        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Remove shadows (value 127) - set to background (0)
        fg_mask[fg_mask == 127] = 0

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(fg_mask, (self.blur_size, self.blur_size), 0)

        # Apply binary threshold
        _, thresh = cv2.threshold(blurred, self.threshold, 255, cv2.THRESH_BINARY)

        # Dilate to fill holes in detected objects
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=self.dilate_iterations)

        # Find contours of moving objects
        contours, _ = cv2.findContours(
            dilated,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter contours by minimum area
        bounding_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))

        # Update motion status
        motion_detected = len(bounding_boxes) > 0

        if motion_detected:
            self.motion_detected = True
            self.last_motion_time = time.time()
            self.motion_count += 1

            if self.motion_callback:
                self.motion_callback(frame, bounding_boxes)
        else:
            self.motion_detected = False

        return motion_detected, bounding_boxes

    def draw_motion(
        self,
        frame: np.ndarray,
        bounding_boxes: List[Tuple[int, int, int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw bounding boxes on frame.

        Args:
            frame: Input frame
            bounding_boxes: List of (x, y, w, h) tuples
            color: Box color in BGR format
            thickness: Box line thickness

        Returns:
            Frame with bounding boxes and labels drawn
        """
        output = frame.copy()

        for (x, y, w, h) in bounding_boxes:
            # Draw rectangle
            cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)

            # Draw label
            label = f"Motion {w}x{h}"
            cv2.putText(
                output,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                thickness
            )

        return output

    def get_stats(self) -> dict:
        """
        Get motion detection statistics.

        Returns:
            Dictionary with motion statistics including:
            - motion_detected: Current motion status
            - last_motion_time: Timestamp of last detected motion
            - motion_count: Total number of motion events
            - total_frames: Total frames processed
        """
        return {
            "motion_detected": self.motion_detected,
            "last_motion_time": self.last_motion_time,
            "motion_count": self.motion_count,
            "total_frames": self.total_frames
        }

    def reset(self):
        """
        Reset motion detection statistics.

        Clears all counters and resets background model.
        """
        self.motion_detected = False
        self.last_motion_time = None
        self.motion_count = 0
        self.total_frames = 0
        self.bg_subtractor.reset()

    def pause(self):
        """
        Pause motion detection.

        When paused, detect() will return False without processing frames.
        """
        self.paused = True

    def resume(self):
        """
        Resume motion detection.

        Resumes normal motion detection after being paused.
        """
        self.paused = False

    def is_paused(self) -> bool:
        """
        Check if motion detection is paused.

        Returns:
            True if paused, False otherwise
        """
        return self.paused
