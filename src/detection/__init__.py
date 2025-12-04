#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detection Module.

@file       __init__.py
@brief      Package initialization for detection algorithms.
@details    Motion and fall detection algorithms using OpenCV
            for smart monitoring applications.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.
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

