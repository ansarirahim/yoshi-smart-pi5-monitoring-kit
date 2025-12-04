"""
RTSP Stream Handler with automatic reconnection.

This module handles video stream connection, frame extraction, and error recovery
for RTSP, MJPEG, and HTTP snapshot streams.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import cv2
import time
import threading
from typing import Optional, Callable
import numpy as np
from src.utils.logger import setup_logger


class RTSPStreamHandler:
    """
    Manages RTSP stream connection with automatic reconnection logic
    """
    
    def __init__(
        self,
        rtsp_url: str,
        reconnect_delay: int = 5,
        max_reconnect_attempts: int = 10,
        frame_callback: Optional[Callable] = None,
        logger_name: str = "RTSPStreamHandler"
    ):
        """
        Initialize RTSP stream handler
        
        Args:
            rtsp_url: RTSP stream URL (e.g., rtsp://user:pass@ip:port/stream)
            reconnect_delay: Initial delay between reconnection attempts (seconds)
            max_reconnect_attempts: Maximum reconnection attempts (0 = infinite)
            frame_callback: Optional callback function for each frame
            logger_name: Logger name
        """
        self.rtsp_url = rtsp_url
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        self.frame_callback = frame_callback
        
        self.logger = setup_logger(logger_name)
        
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_connected = False
        self.reconnect_count = 0
        
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Stream statistics
        self.frame_count = 0
        self.error_count = 0
        self.last_frame_time = 0
        self.fps = 0
    
    def connect(self) -> bool:
        """
        Connect to RTSP stream
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to RTSP stream: {self._mask_credentials(self.rtsp_url)}")
            
            self.capture = cv2.VideoCapture(self.rtsp_url)
            
            # Set buffer size to reduce latency
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test connection by reading one frame
            ret, frame = self.capture.read()
            
            if ret and frame is not None:
                self.is_connected = True
                self.reconnect_count = 0
                self.logger.info("Successfully connected to RTSP stream")
                
                # Get stream properties
                width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(self.capture.get(cv2.CAP_PROP_FPS))
                
                self.logger.info(f"Stream properties: {width}x{height} @ {fps} FPS")
                
                return True
            else:
                self.logger.error("Failed to read frame from RTSP stream")
                self._cleanup_capture()
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to RTSP stream: {e}")
            self._cleanup_capture()
            return False
    
    def disconnect(self):
        """Disconnect from RTSP stream"""
        self.logger.info("Disconnecting from RTSP stream")
        self.is_connected = False
        self._cleanup_capture()
    
    def start(self):
        """Start streaming in background thread"""
        if self.is_running:
            self.logger.warning("Stream already running")
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._thread.start()
        self.logger.info("Stream thread started")
    
    def stop(self):
        """Stop streaming"""
        self.logger.info("Stopping stream")
        self.is_running = False
        
        if self._thread:
            self._thread.join(timeout=5)
        
        self.disconnect()
    
    def read_frame(self) -> tuple[bool, Optional[np.ndarray]]:
        """
        Read single frame from stream
        
        Returns:
            Tuple of (success, frame)
        """
        with self._lock:
            if not self.is_connected or self.capture is None:
                return False, None
            
            try:
                ret, frame = self.capture.read()
                
                if ret and frame is not None:
                    self.frame_count += 1
                    self._update_fps()
                    return True, frame
                else:
                    self.error_count += 1
                    return False, None
                    
            except Exception as e:
                self.logger.error(f"Error reading frame: {e}")
                self.error_count += 1
                return False, None
    
    def _stream_loop(self):
        """Main streaming loop with automatic reconnection"""
        while self.is_running:
            # Connect if not connected
            if not self.is_connected:
                if not self._attempt_reconnect():
                    time.sleep(self.reconnect_delay)
                    continue
            
            # Read and process frame
            ret, frame = self.read_frame()
            
            if ret and frame is not None:
                # Call frame callback if provided
                if self.frame_callback:
                    try:
                        self.frame_callback(frame)
                    except Exception as e:
                        self.logger.error(f"Error in frame callback: {e}")
            else:
                # Connection lost, trigger reconnection
                self.logger.warning("Frame read failed, triggering reconnection")
                self.is_connected = False
                self._cleanup_capture()
            
            # Small delay to prevent CPU overload
            time.sleep(0.001)
    
    def _attempt_reconnect(self) -> bool:
        """
        Attempt to reconnect with exponential backoff
        
        Returns:
            True if reconnection successful
        """
        if self.max_reconnect_attempts > 0 and self.reconnect_count >= self.max_reconnect_attempts:
            self.logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            self.is_running = False
            return False
        
        self.reconnect_count += 1
        delay = min(self.reconnect_delay * (2 ** (self.reconnect_count - 1)), 60)
        
        self.logger.info(f"Reconnection attempt {self.reconnect_count}, waiting {delay}s...")
        time.sleep(delay)
        
        return self.connect()
    
    def _cleanup_capture(self):
        """Clean up VideoCapture object"""
        if self.capture:
            try:
                self.capture.release()
            except:
                pass
            self.capture = None
    
    def _update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        if self.last_frame_time > 0:
            delta = current_time - self.last_frame_time
            if delta > 0:
                self.fps = 1.0 / delta
        self.last_frame_time = current_time
    
    def _mask_credentials(self, url: str) -> str:
        """Mask credentials in RTSP URL for logging"""
        if '@' in url:
            parts = url.split('@')
            if '://' in parts[0]:
                protocol = parts[0].split('://')[0]
                return f"{protocol}://***:***@{parts[1]}"
        return url
    
    def get_stats(self) -> dict:
        """
        Get stream statistics
        
        Returns:
            Dictionary with stream stats
        """
        return {
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "frame_count": self.frame_count,
            "error_count": self.error_count,
            "reconnect_count": self.reconnect_count,
            "fps": round(self.fps, 2)
        }

