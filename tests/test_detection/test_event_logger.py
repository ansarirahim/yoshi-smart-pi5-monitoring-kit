"""
Unit tests for EventLogger.

Test suite for event logging functionality including
snapshot saving and event filtering.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import numpy as np
import os
import json
import time
import tempfile
import shutil
from src.detection.event_logger import EventLogger


class TestEventLogger:
    """Test cases for EventLogger class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_initialization(self, temp_dir):
        """Test event logger initialization."""
        log_dir = os.path.join(temp_dir, "logs")
        snapshot_dir = os.path.join(temp_dir, "snapshots")
        
        logger = EventLogger(log_dir=log_dir, snapshot_dir=snapshot_dir)
        
        assert logger.log_dir == log_dir
        assert logger.snapshot_dir == snapshot_dir
        assert logger.save_snapshots == True
        assert os.path.exists(log_dir)
        assert os.path.exists(snapshot_dir)
    
    def test_initialization_no_snapshots(self, temp_dir):
        """Test initialization without snapshot saving."""
        log_dir = os.path.join(temp_dir, "logs")
        
        logger = EventLogger(log_dir=log_dir, save_snapshots=False)
        
        assert logger.save_snapshots == False
    
    def test_log_event_basic(self, temp_dir):
        """Test logging basic event."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        event_id = logger.log_event("motion")
        
        assert event_id.startswith("motion_")
        assert len(logger.events) == 1
        assert logger.events[0]["event_type"] == "motion"
    
    def test_log_event_with_metadata(self, temp_dir):
        """Test logging event with metadata."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        metadata = {"boxes": 3, "confidence": 0.95}
        event_id = logger.log_event("motion", metadata=metadata)
        
        assert logger.events[0]["metadata"] == metadata
    
    def test_log_event_with_snapshot(self, temp_dir):
        """Test logging event with snapshot."""
        snapshot_dir = os.path.join(temp_dir, "snapshots")
        logger = EventLogger(log_dir=temp_dir, snapshot_dir=snapshot_dir)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        event_id = logger.log_event("motion", frame=frame)
        
        assert "snapshot" in logger.events[0]
        snapshot_path = logger.events[0]["snapshot"]
        assert os.path.exists(snapshot_path)
        assert snapshot_path.endswith(".jpg")
    
    def test_log_event_timestamp(self, temp_dir):
        """Test event timestamp."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        before_time = time.time()
        logger.log_event("motion")
        after_time = time.time()
        
        event = logger.events[0]
        assert "timestamp" in event
        assert "datetime" in event
        assert before_time <= event["timestamp"] <= after_time
    
    def test_get_events_all(self, temp_dir):
        """Test getting all events."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        logger.log_event("motion")
        logger.log_event("fall")
        logger.log_event("motion")
        
        events = logger.get_events()
        
        assert len(events) == 3
    
    def test_get_events_by_type(self, temp_dir):
        """Test filtering events by type."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        logger.log_event("motion")
        logger.log_event("fall")
        logger.log_event("motion")
        
        motion_events = logger.get_events(event_type="motion")
        fall_events = logger.get_events(event_type="fall")
        
        assert len(motion_events) == 2
        assert len(fall_events) == 1
    
    def test_get_events_by_time_range(self, temp_dir):
        """Test filtering events by time range."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        logger.log_event("motion")
        time.sleep(0.1)
        
        mid_time = time.time()
        time.sleep(0.1)
        
        logger.log_event("motion")
        
        events_before = logger.get_events(end_time=mid_time)
        events_after = logger.get_events(start_time=mid_time)
        
        assert len(events_before) == 1
        assert len(events_after) == 1
    
    def test_get_events_with_limit(self, temp_dir):
        """Test limiting number of returned events."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        for _ in range(10):
            logger.log_event("motion")
        
        events = logger.get_events(limit=5)
        
        assert len(events) == 5
    
    def test_get_event_count(self, temp_dir):
        """Test getting event count."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)
        
        logger.log_event("motion")
        logger.log_event("fall")
        logger.log_event("motion")
        
        total_count = logger.get_event_count()
        motion_count = logger.get_event_count(event_type="motion")
        
        assert total_count == 3
        assert motion_count == 2

    def test_clear_events_all(self, temp_dir):
        """Test clearing all events."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)

        logger.log_event("motion")
        logger.log_event("fall")

        logger.clear_events()

        assert len(logger.events) == 0
        assert logger.get_event_count() == 0

    def test_clear_events_by_type(self, temp_dir):
        """Test clearing events by type."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)

        logger.log_event("motion")
        logger.log_event("fall")
        logger.log_event("motion")

        logger.clear_events(event_type="motion")

        assert logger.get_event_count() == 1
        assert logger.get_event_count(event_type="fall") == 1

    def test_persistence(self, temp_dir):
        """Test event persistence to disk."""
        log_dir = os.path.join(temp_dir, "logs")

        # Create logger and log events
        logger1 = EventLogger(log_dir=log_dir, save_snapshots=False)
        logger1.log_event("motion")
        logger1.log_event("fall")

        # Create new logger instance (should load existing events)
        logger2 = EventLogger(log_dir=log_dir, save_snapshots=False)

        assert len(logger2.events) == 2

    def test_max_events_limit(self, temp_dir):
        """Test maximum events limit."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False, max_events=10)

        # Log more than max_events
        for i in range(15):
            logger.log_event("motion")

        # Should keep only last 10 events
        assert len(logger.events) == 10

    def test_events_sorted_newest_first(self, temp_dir):
        """Test events are returned newest first."""
        logger = EventLogger(log_dir=temp_dir, save_snapshots=False)

        logger.log_event("motion", metadata={"id": 1})
        time.sleep(0.1)
        logger.log_event("motion", metadata={"id": 2})
        time.sleep(0.1)
        logger.log_event("motion", metadata={"id": 3})

        events = logger.get_events()

        # Newest first
        assert events[0]["metadata"]["id"] == 3
        assert events[1]["metadata"]["id"] == 2
        assert events[2]["metadata"]["id"] == 1

