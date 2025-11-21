"""
Pan-Tilt Control Module.

Handles servo control and auto-tracking
for camera positioning and motion following.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

from .controller import PanTiltController
from .tracker import AutoTracker

__all__ = ['PanTiltController', 'AutoTracker']

