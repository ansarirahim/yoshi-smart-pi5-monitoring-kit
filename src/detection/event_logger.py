#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Logging Module.

@file       event_logger.py
@brief      Logs motion detection events with metadata.
@details    Maintains event logs with timestamps, snapshots, and metadata
            for analysis and notification purposes.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.

@dependencies
    - opencv-python >= 4.5.0
"""

import os
import cv2
import json
import time
from datetime import datetime
from typing import Optional, List, Dict
import numpy as np


class EventLogger:
    """
    Log motion detection events with snapshots.
    
    Maintains a JSON log of all events and optionally saves
    frame snapshots for each event.
    """
    
    def __init__(
        self,
        log_dir: str = "logs/events",
        snapshot_dir: str = "logs/snapshots",
        save_snapshots: bool = True,
        max_events: int = 1000
    ):
        """
        Initialize event logger.
        
        Args:
            log_dir: Directory for event logs
            snapshot_dir: Directory for snapshots
            save_snapshots: Whether to save frame snapshots
            max_events: Maximum events to keep in memory
            
        Note:
            Directories are created automatically if they don't exist
        """
        self.log_dir = log_dir
        self.snapshot_dir = snapshot_dir
        self.save_snapshots = save_snapshots
        self.max_events = max_events
        
        # Create directories
        os.makedirs(log_dir, exist_ok=True)
        if save_snapshots:
            os.makedirs(snapshot_dir, exist_ok=True)
        
        self.log_file = os.path.join(log_dir, "motion_events.json")
        self.events = []
        
        # Load existing events
        self._load_events()
    
    def log_event(
        self,
        event_type: str,
        frame: Optional[np.ndarray] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Log motion event.
        
        Args:
            event_type: Type of event ("motion", "fall", etc.)
            frame: Frame to save as snapshot (BGR format)
            metadata: Additional event metadata
            
        Returns:
            Event ID (unique identifier)
            
        Note:
            Events are automatically saved to disk
        """
        timestamp = time.time()
        event_id = f"{event_type}_{int(timestamp * 1000)}"
        
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "metadata": metadata or {}
        }
        
        # Save snapshot
        if self.save_snapshots and frame is not None:
            snapshot_path = os.path.join(
                self.snapshot_dir,
                f"{event_id}.jpg"
            )
            cv2.imwrite(snapshot_path, frame)
            event["snapshot"] = snapshot_path
        
        # Add to events list
        self.events.append(event)
        
        # Trim old events if exceeding max
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Save to file
        self._save_events()
        
        return event_id
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get logged events with optional filtering.
        
        Args:
            event_type: Filter by event type
            start_time: Filter by start timestamp (Unix time)
            end_time: Filter by end timestamp (Unix time)
            limit: Maximum number of events to return
            
        Returns:
            List of events matching criteria (newest first)
        """
        filtered = self.events.copy()
        
        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]
        
        if start_time:
            filtered = [e for e in filtered if e["timestamp"] >= start_time]
        
        if end_time:
            filtered = [e for e in filtered if e["timestamp"] <= end_time]
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered

    def get_event_count(self, event_type: Optional[str] = None) -> int:
        """
        Get count of logged events.

        Args:
            event_type: Filter by event type

        Returns:
            Number of events
        """
        if event_type:
            return len([e for e in self.events if e["event_type"] == event_type])
        return len(self.events)

    def clear_events(self, event_type: Optional[str] = None):
        """
        Clear logged events.

        Args:
            event_type: Clear only events of this type (None = clear all)
        """
        if event_type:
            self.events = [e for e in self.events if e["event_type"] != event_type]
        else:
            self.events = []

        self._save_events()

    def _load_events(self):
        """Load events from JSON file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.events = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.events = []

    def _save_events(self):
        """Save events to JSON file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.events, f, indent=2)
        except IOError as e:
            print(f"Error saving events: {e}")

