#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pan-Tilt Control Module.

@file       __init__.py
@brief      Package initialization for pan-tilt servo control.
@details    Handles servo control and auto-tracking
            for camera positioning and motion following.

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

from .controller import PanTiltController
from .tracker import AutoTracker

__all__ = ['PanTiltController', 'AutoTracker']

