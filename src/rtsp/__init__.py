#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTSP Stream Handler Module.

@file       __init__.py
@brief      Package initialization for RTSP stream handling.
@details    Handles RTSP stream connection, frame extraction, and buffering
            for video surveillance applications.

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

from .stream_handler import RTSPStreamHandler
from .frame_buffer import FrameBuffer

__all__ = ['RTSPStreamHandler', 'FrameBuffer']

