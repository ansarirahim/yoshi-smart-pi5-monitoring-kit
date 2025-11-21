"""
RTSP Stream Handler Module.

Handles RTSP stream connection, frame extraction, and buffering
for video surveillance applications.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

from .stream_handler import RTSPStreamHandler
from .frame_buffer import FrameBuffer

__all__ = ['RTSPStreamHandler', 'FrameBuffer']

