"""
Unit tests for ConfigLoader.

Test suite for configuration loading from YAML, JSON, and environment variables.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import yaml
import json
from pathlib import Path
from src.utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Test cases for ConfigLoader class"""
    
    def test_load_config_file(self, tmp_path):
        """Test loading configuration from YAML file"""
        # Create temporary config file
        config_file = tmp_path / "config.yaml"
        config_data = {
            "camera": {
                "rtsp_url": "rtsp://test:test@localhost:554/stream",
                "fps": 15
            },
            "motion_detection": {
                "enabled": True,
                "sensitivity": 0.5
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        loader = ConfigLoader(str(config_file))
        
        # Verify values
        assert loader.get("camera.rtsp_url") == "rtsp://test:test@localhost:554/stream"
        assert loader.get("camera.fps") == 15
        assert loader.get("motion_detection.enabled") is True
        assert loader.get("motion_detection.sensitivity") == 0.5
    
    def test_get_nested_value(self, tmp_path):
        """Test getting nested configuration values"""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                }
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(str(config_file))
        assert loader.get("level1.level2.level3") == "deep_value"
    
    def test_get_default_value(self, tmp_path):
        """Test getting default value for missing key"""
        config_file = tmp_path / "config.yaml"
        config_data = {"existing_key": "value"}
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(str(config_file))
        assert loader.get("missing_key", "default") == "default"
        assert loader.get("missing.nested.key", 42) == 42
    
    def test_set_value(self, tmp_path):
        """Test setting configuration value"""
        config_file = tmp_path / "config.yaml"
        config_data = {"key": "old_value"}
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(str(config_file))
        loader.set("key", "new_value")
        
        assert loader.get("key") == "new_value"
    
    def test_set_nested_value(self, tmp_path):
        """Test setting nested configuration value"""
        config_file = tmp_path / "config.yaml"
        config_data = {}
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(str(config_file))
        loader.set("new.nested.key", "value")
        
        assert loader.get("new.nested.key") == "value"
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to file"""
        config_file = tmp_path / "config.yaml"
        config_data = {"key": "value"}
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(str(config_file))
        loader.set("new_key", "new_value")
        
        save_file = tmp_path / "saved_config.yaml"
        loader.save(str(save_file))
        
        # Verify saved file
        with open(save_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data["new_key"] == "new_value"
    
    def test_reload_config(self, tmp_path):
        """Test reloading configuration"""
        config_file = tmp_path / "config.yaml"
        config_data = {"key": "original"}
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(str(config_file))
        assert loader.get("key") == "original"
        
        # Modify file
        config_data["key"] = "modified"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Reload
        loader.reload()
        assert loader.get("key") == "modified"
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        with pytest.raises(FileNotFoundError):
            ConfigLoader("nonexistent_config.yaml")

