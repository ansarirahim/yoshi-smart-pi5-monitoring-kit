"""
Detection Module.

Motion and fall detection algorithms using OpenCV
for smart monitoring applications.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

from .background_subtractor import BackgroundSubtractor
from .motion_detector import MotionDetector
from .event_logger import EventLogger
from .fall_detector import FallDetector, PersonState

__all__ = [
    'BackgroundSubtractor',
    'MotionDetector',
    'EventLogger',
    'FallDetector',
    'PersonState'
]

