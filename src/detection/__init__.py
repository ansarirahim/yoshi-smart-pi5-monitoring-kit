"""
Detection Module.

Motion and fall detection algorithms using OpenCV
for smart monitoring applications.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

from .motion_detector import MotionDetector
from .fall_detector import FallDetector

__all__ = ['MotionDetector', 'FallDetector']

