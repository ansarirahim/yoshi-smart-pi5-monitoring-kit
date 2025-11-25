"""
Unit tests for VersionManager.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import tempfile
from pathlib import Path

from src.ota.version_manager import VersionManager


class TestVersionManager:
    """Test suite for VersionManager class."""
    
    @pytest.fixture
    def temp_version_file(self):
        """Create temporary version file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("1.0.0\n")
            temp_path = f.name
        
        yield temp_path
        
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def version_manager(self, temp_version_file):
        """Create VersionManager instance with temp file."""
        return VersionManager(version_file=temp_version_file)
    
    def test_initialization(self, temp_version_file):
        """Test VersionManager initialization."""
        vm = VersionManager(version_file=temp_version_file)
        assert vm.version_file == Path(temp_version_file)
    
    def test_get_current_version(self, version_manager):
        """Test getting current version."""
        version = version_manager.get_current_version()
        assert version == "1.0.0"
    
    def test_get_current_version_file_not_found(self):
        """Test getting version when file doesn't exist."""
        vm = VersionManager(version_file="nonexistent.txt")
        
        with pytest.raises(FileNotFoundError):
            vm.get_current_version()
    
    def test_get_current_version_invalid_format(self, temp_version_file):
        """Test getting version with invalid format."""
        Path(temp_version_file).write_text("invalid\n")
        vm = VersionManager(version_file=temp_version_file)
        
        with pytest.raises(ValueError):
            vm.get_current_version()
    
    def test_set_current_version(self, version_manager, temp_version_file):
        """Test setting current version."""
        version_manager.set_current_version("2.0.0")
        
        content = Path(temp_version_file).read_text()
        assert content.strip() == "2.0.0"
    
    def test_set_current_version_invalid(self, version_manager):
        """Test setting invalid version."""
        with pytest.raises(ValueError):
            version_manager.set_current_version("invalid")
    
    def test_is_valid_version(self, version_manager):
        """Test version validation."""
        assert version_manager.is_valid_version("1.0.0") is True
        assert version_manager.is_valid_version("0.1.0") is True
        assert version_manager.is_valid_version("10.20.30") is True
        assert version_manager.is_valid_version("invalid") is False
        assert version_manager.is_valid_version("1.0") is False
        assert version_manager.is_valid_version("1.0.0.0") is False
        assert version_manager.is_valid_version("v1.0.0") is False
    
    def test_parse_version(self, version_manager):
        """Test version parsing."""
        assert version_manager.parse_version("1.0.0") == (1, 0, 0)
        assert version_manager.parse_version("2.5.10") == (2, 5, 10)
        assert version_manager.parse_version("0.0.1") == (0, 0, 1)
    
    def test_parse_version_invalid(self, version_manager):
        """Test parsing invalid version."""
        with pytest.raises(ValueError):
            version_manager.parse_version("invalid")
    
    def test_compare_versions(self, version_manager):
        """Test version comparison."""
        assert version_manager.compare_versions("1.0.0", "1.0.0") == 0
        assert version_manager.compare_versions("2.0.0", "1.0.0") == 1
        assert version_manager.compare_versions("1.0.0", "2.0.0") == -1
        assert version_manager.compare_versions("1.1.0", "1.0.0") == 1
        assert version_manager.compare_versions("1.0.1", "1.0.0") == 1
        assert version_manager.compare_versions("1.0.0", "1.0.1") == -1
    
    def test_is_newer(self, version_manager):
        """Test checking if version is newer."""
        assert version_manager.is_newer("2.0.0", "1.0.0") is True
        assert version_manager.is_newer("1.0.0", "2.0.0") is False
        assert version_manager.is_newer("1.0.0", "1.0.0") is False
        assert version_manager.is_newer("1.1.0", "1.0.0") is True
        assert version_manager.is_newer("1.0.1", "1.0.0") is True
    
    def test_get_next_version_patch(self, version_manager):
        """Test getting next patch version."""
        assert version_manager.get_next_version("1.0.0", "patch") == "1.0.1"
        assert version_manager.get_next_version("1.0.9", "patch") == "1.0.10"
    
    def test_get_next_version_minor(self, version_manager):
        """Test getting next minor version."""
        assert version_manager.get_next_version("1.0.0", "minor") == "1.1.0"
        assert version_manager.get_next_version("1.9.5", "minor") == "1.10.0"
    
    def test_get_next_version_major(self, version_manager):
        """Test getting next major version."""
        assert version_manager.get_next_version("1.0.0", "major") == "2.0.0"
        assert version_manager.get_next_version("9.5.3", "major") == "10.0.0"
    
    def test_get_next_version_invalid_bump(self, version_manager):
        """Test getting next version with invalid bump type."""
        with pytest.raises(ValueError):
            version_manager.get_next_version("1.0.0", "invalid")

