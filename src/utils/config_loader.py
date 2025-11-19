"""
Configuration loader utility
"""

import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration from YAML and JSON files"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to main configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.secrets: Dict[str, Any] = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration files
        self._load_config()
        self._load_secrets()
    
    def _load_config(self):
        """Load main configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def _load_secrets(self):
        """Load secrets from JSON file"""
        secrets_path = Path("config/secrets.json")
        
        if secrets_path.exists():
            with open(secrets_path, 'r') as f:
                self.secrets = json.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'camera.rtsp_url')
            default: Default value if key not found
        
        Returns:
            Configuration value
        
        Examples:
            >>> config = ConfigLoader()
            >>> config.get('camera.rtsp_url')
            'rtsp://192.168.1.100:554/stream'
            >>> config.get('motion_detection.enabled')
            True
        """
        # Try to get from environment variable first
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Try to get from secrets
        value = self._get_nested(self.secrets, key)
        if value is not None:
            return value
        
        # Try to get from config
        value = self._get_nested(self.config, key)
        if value is not None:
            return value
        
        return default
    
    def _get_nested(self, data: Dict, key: str) -> Optional[Any]:
        """
        Get nested dictionary value using dot notation
        
        Args:
            data: Dictionary to search
            key: Dot-separated key path
        
        Returns:
            Value if found, None otherwise
        """
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        data = self.config
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """
        Save configuration to file
        
        Args:
            path: Path to save to (defaults to original config path)
        """
        save_path = Path(path) if path else self.config_path
        
        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def reload(self):
        """Reload configuration from files"""
        self._load_config()
        self._load_secrets()

