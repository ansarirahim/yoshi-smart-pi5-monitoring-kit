"""
Fall Detection Module.

Detects falls using pose estimation and body angle analysis.
Identifies vertical-to-horizontal collapse patterns and abnormal inactivity.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple, Dict, Callable
from enum import Enum


class PersonState(Enum):
    """Person state enumeration."""
    STANDING = "standing"
    SITTING = "sitting"
    LYING = "lying"
    FALLEN = "fallen"
    UNKNOWN = "unknown"


class FallDetector:
    """
    Fall detection using aspect ratio analysis and motion patterns.

    Detects falls by analyzing:
    - Body aspect ratio (height/width)
    - Vertical-to-horizontal transitions
    - Sudden position changes
    - Prolonged inactivity in horizontal position
    """

    def __init__(
        self,
        aspect_ratio_threshold: float = 1.5,
        fall_velocity_threshold: float = 0.3,
        inactivity_timeout: float = 10.0,
        min_person_area: int = 2000,
        fall_callback: Optional[Callable] = None
    ):
        """
        Initialize fall detector.

        Args:
            aspect_ratio_threshold: Threshold for height/width ratio
                                   (below this = horizontal/lying)
            fall_velocity_threshold: Minimum vertical velocity for fall detection
            inactivity_timeout: Seconds of inactivity to confirm fall
            min_person_area: Minimum contour area to consider as person
            fall_callback: Callback function when fall detected
        """
        if aspect_ratio_threshold <= 0:
            raise ValueError("aspect_ratio_threshold must be positive")
        if fall_velocity_threshold < 0 or fall_velocity_threshold > 1:
            raise ValueError("fall_velocity_threshold must be between 0 and 1")
        if inactivity_timeout <= 0:
            raise ValueError("inactivity_timeout must be positive")
        if min_person_area <= 0:
            raise ValueError("min_person_area must be positive")

        self.aspect_ratio_threshold = aspect_ratio_threshold
        self.fall_velocity_threshold = fall_velocity_threshold
        self.inactivity_timeout = inactivity_timeout
        self.min_person_area = min_person_area
        self.fall_callback = fall_callback

        # State tracking
        self.previous_state = PersonState.UNKNOWN
        self.current_state = PersonState.UNKNOWN
        self.previous_centroid = None
        self.state_start_time = None
        self.fall_detected = False
        self.fall_time = None

        # Statistics
        self.total_frames = 0
        self.fall_count = 0

        # Control state
        self.paused = False

        # Background subtractor for person detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )

    def detect(
        self,
        frame: np.ndarray
    ) -> Tuple[bool, PersonState, Optional[Tuple[int, int, int, int]]]:
        """
        Detect fall in frame.

        Args:
            frame: Input frame in BGR format

        Returns:
            Tuple of (fall_detected, person_state, bounding_box)
            bounding_box is (x, y, w, h) or None if no person detected
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is None or empty")

        # If paused, return no fall
        if self.paused:
            return False, PersonState.UNKNOWN, None

        self.total_frames += 1

        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Remove shadows
        fg_mask[fg_mask == 127] = 0

        # Noise reduction
        blurred = cv2.GaussianBlur(fg_mask, (21, 21), 0)
        _, thresh = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)

        # Morphological operations
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=3)

        # Find contours
        contours, _ = cv2.findContours(
            dilated,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Find largest contour (assume it's the person)
        person_contour = None
        max_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area and area >= self.min_person_area:
                max_area = area
                person_contour = contour

        if person_contour is None:
            # No person detected
            self.current_state = PersonState.UNKNOWN
            return False, PersonState.UNKNOWN, None

        # Get bounding box
        x, y, w, h = cv2.boundingRect(person_contour)
        bbox = (x, y, w, h)

        # Calculate aspect ratio
        aspect_ratio = h / w if w > 0 else 0

        # Calculate centroid
        M = cv2.moments(person_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            current_centroid = (cx, cy)
        else:
            current_centroid = (x + w // 2, y + h // 2)

        # Determine person state based on aspect ratio
        if aspect_ratio >= self.aspect_ratio_threshold:
            new_state = PersonState.STANDING
        elif aspect_ratio < 1.0:
            new_state = PersonState.LYING
        else:
            new_state = PersonState.SITTING

        # Detect fall transition
        fall_detected = False

        if self.previous_state != new_state:
            # State changed
            if self.previous_state == PersonState.STANDING and new_state == PersonState.LYING:
                # Potential fall: standing to lying
                if self.previous_centroid is not None:
                    # Calculate vertical velocity
                    dy = current_centroid[1] - self.previous_centroid[1]
                    vertical_velocity = abs(dy) / frame.shape[0]

                    if vertical_velocity >= self.fall_velocity_threshold:
                        # Fast vertical movement detected
                        fall_detected = True
                        self.fall_detected = True
                        self.fall_time = time.time()
                        self.fall_count += 1
                        self.current_state = PersonState.FALLEN

                        if self.fall_callback:
                            self.fall_callback(frame, bbox, vertical_velocity)

            self.previous_state = new_state
            self.state_start_time = time.time()

        # Check for prolonged inactivity in lying position
        if new_state == PersonState.LYING and not fall_detected:
            if self.state_start_time is not None:
                time_in_state = time.time() - self.state_start_time
                if time_in_state >= self.inactivity_timeout:
                    # Person lying down for too long
                    if not self.fall_detected:
                        fall_detected = True
                        self.fall_detected = True
                        self.fall_time = time.time()
                        self.fall_count += 1
                        self.current_state = PersonState.FALLEN

                        if self.fall_callback:
                            self.fall_callback(frame, bbox, 0.0)

        # Update state
        if not fall_detected and self.current_state != PersonState.FALLEN:
            self.current_state = new_state

        self.previous_centroid = current_centroid

        return fall_detected, self.current_state, bbox

    def draw_detection(
        self,
        frame: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]],
        state: PersonState,
        color: Optional[Tuple[int, int, int]] = None,
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw fall detection visualization on frame.

        Args:
            frame: Input frame
            bbox: Bounding box (x, y, w, h) or None
            state: Person state
            color: Box color (BGR), auto-selected if None
            thickness: Line thickness

        Returns:
            Annotated frame
        """
        output = frame.copy()

        if bbox is None:
            return output

        x, y, w, h = bbox

        # Auto-select color based on state
        if color is None:
            if state == PersonState.FALLEN:
                color = (0, 0, 255)  # Red for fall
            elif state == PersonState.LYING:
                color = (0, 165, 255)  # Orange for lying
            elif state == PersonState.STANDING:
                color = (0, 255, 0)  # Green for standing
            else:
                color = (255, 255, 0)  # Cyan for sitting/unknown

        # Draw bounding box
        cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)

        # Draw state label
        label = f"{state.value.upper()}"
        if state == PersonState.FALLEN:
            label = "FALL DETECTED!"

        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(
            output,
            (x, y - label_size[1] - 10),
            (x + label_size[0], y),
            color,
            -1
        )
        cv2.putText(
            output,
            label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Draw aspect ratio
        aspect_ratio = h / w if w > 0 else 0
        cv2.putText(
            output,
            f"AR: {aspect_ratio:.2f}",
            (x, y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1
        )

        return output

    def get_stats(self) -> Dict:
        """
        Get fall detection statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "fall_detected": self.fall_detected,
            "current_state": self.current_state.value,
            "fall_time": self.fall_time,
            "fall_count": self.fall_count,
            "total_frames": self.total_frames
        }

    def reset(self):
        """Reset fall detector state."""
        self.previous_state = PersonState.UNKNOWN
        self.current_state = PersonState.UNKNOWN
        self.previous_centroid = None
        self.state_start_time = None
        self.fall_detected = False
        self.fall_time = None
        self.total_frames = 0
        self.fall_count = 0
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )

    def pause(self):
        """
        Pause fall detection.

        When paused, detect() will return False without processing frames.
        """
        self.paused = True

    def resume(self):
        """
        Resume fall detection.

        Resumes normal fall detection after being paused.
        """
        self.paused = False

    def is_paused(self) -> bool:
        """
        Check if fall detection is paused.

        Returns:
            True if paused, False otherwise
        """
        return self.paused
