#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frame Buffer for video streams.

@file       frame_buffer.py
@brief      Thread-safe circular buffer for video frames.
@details    Provides thread-safe storage and retrieval of video frames
            with automatic overflow handling.

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

import threading
from collections import deque
from typing import Optional
import numpy as np
import time
from src.utils.logger import setup_logger


class FrameBuffer:
    """
    Thread-safe circular buffer for video frames
    """
    
    def __init__(self, max_size: int = 30, logger_name: str = "FrameBuffer"):
        """
        Initialize frame buffer
        
        Args:
            max_size: Maximum number of frames to store
            logger_name: Logger name
        """
        self.max_size = max_size
        self.logger = setup_logger(logger_name)
        
        self._buffer = deque(maxlen=max_size)
        self._lock = threading.Lock()
        
        # Statistics
        self.frames_added = 0
        self.frames_retrieved = 0
        self.frames_dropped = 0
        
        self.logger.info(f"Frame buffer initialized with max size: {max_size}")
    
    def add_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> bool:
        """
        Add frame to buffer
        
        Args:
            frame: Video frame (numpy array)
            timestamp: Optional timestamp (defaults to current time)
        
        Returns:
            True if frame added successfully
        """
        if frame is None:
            self.logger.warning("Attempted to add None frame to buffer")
            return False
        
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            # Check if buffer is full
            if len(self._buffer) >= self.max_size:
                self.frames_dropped += 1
            
            self._buffer.append({
                'frame': frame.copy(),  # Copy to avoid reference issues
                'timestamp': timestamp,
                'index': self.frames_added
            })
            
            self.frames_added += 1
        
        return True
    
    def get_latest_frame(self) -> Optional[dict]:
        """
        Get the most recent frame from buffer
        
        Returns:
            Dictionary with 'frame', 'timestamp', 'index' or None if buffer empty
        """
        with self._lock:
            if len(self._buffer) == 0:
                return None
            
            frame_data = self._buffer[-1]
            self.frames_retrieved += 1
            
            return {
                'frame': frame_data['frame'].copy(),
                'timestamp': frame_data['timestamp'],
                'index': frame_data['index']
            }
    
    def get_oldest_frame(self) -> Optional[dict]:
        """
        Get the oldest frame from buffer
        
        Returns:
            Dictionary with 'frame', 'timestamp', 'index' or None if buffer empty
        """
        with self._lock:
            if len(self._buffer) == 0:
                return None
            
            frame_data = self._buffer[0]
            self.frames_retrieved += 1
            
            return {
                'frame': frame_data['frame'].copy(),
                'timestamp': frame_data['timestamp'],
                'index': frame_data['index']
            }
    
    def get_frame_at_index(self, index: int) -> Optional[dict]:
        """
        Get frame at specific buffer index (0 = oldest, -1 = newest)
        
        Args:
            index: Buffer index
        
        Returns:
            Dictionary with frame data or None if index out of range
        """
        with self._lock:
            if len(self._buffer) == 0:
                return None
            
            try:
                frame_data = self._buffer[index]
                self.frames_retrieved += 1
                
                return {
                    'frame': frame_data['frame'].copy(),
                    'timestamp': frame_data['timestamp'],
                    'index': frame_data['index']
                }
            except IndexError:
                self.logger.warning(f"Frame index {index} out of range")
                return None
    
    def get_all_frames(self) -> list:
        """
        Get all frames in buffer (oldest to newest)
        
        Returns:
            List of frame dictionaries
        """
        with self._lock:
            frames = []
            for frame_data in self._buffer:
                frames.append({
                    'frame': frame_data['frame'].copy(),
                    'timestamp': frame_data['timestamp'],
                    'index': frame_data['index']
                })
            
            self.frames_retrieved += len(frames)
            return frames
    
    def clear(self):
        """Clear all frames from buffer"""
        with self._lock:
            self._buffer.clear()
            self.logger.info("Frame buffer cleared")
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        with self._lock:
            return len(self._buffer) == 0
    
    def is_full(self) -> bool:
        """Check if buffer is full"""
        with self._lock:
            return len(self._buffer) >= self.max_size
    
    def size(self) -> int:
        """Get current number of frames in buffer"""
        with self._lock:
            return len(self._buffer)
    
    def get_stats(self) -> dict:
        """
        Get buffer statistics
        
        Returns:
            Dictionary with buffer stats
        """
        with self._lock:
            return {
                'current_size': len(self._buffer),
                'max_size': self.max_size,
                'frames_added': self.frames_added,
                'frames_retrieved': self.frames_retrieved,
                'frames_dropped': self.frames_dropped,
                'is_full': len(self._buffer) >= self.max_size,
                'is_empty': len(self._buffer) == 0
            }
    
    def get_frame_rate(self, window_size: int = 10) -> float:
        """
        Calculate frame rate based on timestamps of recent frames
        
        Args:
            window_size: Number of recent frames to analyze
        
        Returns:
            Estimated frame rate (FPS)
        """
        with self._lock:
            if len(self._buffer) < 2:
                return 0.0
            
            # Get timestamps of recent frames
            recent_frames = list(self._buffer)[-window_size:]
            
            if len(recent_frames) < 2:
                return 0.0
            
            # Calculate time difference
            time_diff = recent_frames[-1]['timestamp'] - recent_frames[0]['timestamp']
            
            if time_diff <= 0:
                return 0.0
            
            # Calculate FPS
            fps = (len(recent_frames) - 1) / time_diff
            return round(fps, 2)

