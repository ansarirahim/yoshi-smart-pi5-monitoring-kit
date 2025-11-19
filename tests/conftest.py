"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "camera": {
            "rtsp_url": "rtsp://test:test@localhost:554/stream",
            "frame_width": 640,
            "frame_height": 480,
            "fps": 15
        },
        "motion_detection": {
            "enabled": True,
            "sensitivity": 0.5,
            "min_area": 500
        },
        "fall_detection": {
            "enabled": True,
            "sensitivity": 0.7,
            "aspect_ratio_threshold": 1.5
        }
    }


@pytest.fixture
def mock_frame():
    """Create a mock video frame for testing"""
    import numpy as np
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def temp_snapshot_dir(tmp_path):
    """Create temporary directory for snapshots"""
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    return snapshot_dir

