"""
Unit tests for OTAUpdater.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ota.updater import OTAUpdater
from src.ota.version_manager import VersionManager


class TestOTAUpdater:
    """Test suite for OTAUpdater class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        version_file = temp_dir / "VERSION"
        version_file.write_text("1.0.0\n")
        backup_dir = temp_dir / "backups"
        backup_dir.mkdir()
        
        yield {
            'root': temp_dir,
            'version_file': version_file,
            'backup_dir': backup_dir
        }
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def config(self, temp_dirs):
        """Create test configuration."""
        return {
            'github_repo': 'test/repo',
            'check_interval': 10,
            'auto_update': False,
            'backup_enabled': True,
            'backup_path': str(temp_dirs['backup_dir']),
            'max_backups': 3
        }
    
    @pytest.fixture
    def version_manager(self, temp_dirs):
        """Create VersionManager instance."""
        return VersionManager(version_file=str(temp_dirs['version_file']))
    
    @pytest.fixture
    def updater(self, config, version_manager):
        """Create OTAUpdater instance."""
        return OTAUpdater(config, version_manager)
    
    def test_initialization(self, updater, config):
        """Test OTAUpdater initialization."""
        assert updater.github_repo == 'test/repo'
        assert updater.check_interval == 10
        assert updater.auto_update is False
        assert updater.backup_enabled is True
        assert updater.max_backups == 3
        assert updater._running is False
    
    def test_start_stop(self, updater):
        """Test starting and stopping updater."""
        updater.start()
        assert updater._running is True
        assert updater._check_thread is not None
        
        updater.stop()
        assert updater._running is False
    
    def test_start_already_running(self, updater):
        """Test starting updater when already running."""
        updater.start()
        updater.start()
        assert updater._running is True
        updater.stop()
    
    @patch('src.ota.updater.requests.get')
    def test_get_latest_release_success(self, mock_get, updater):
        """Test getting latest release successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': 'v2.0.0',
            'tarball_url': 'https://example.com/tarball'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        release = updater._get_latest_release()
        
        assert release is not None
        assert release['tag_name'] == 'v2.0.0'
        mock_get.assert_called_once()
    
    @patch('src.ota.updater.requests.get')
    def test_get_latest_release_error(self, mock_get, updater):
        """Test getting latest release with error."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        release = updater._get_latest_release()

        assert release is None
    
    @patch('src.ota.updater.OTAUpdater._get_latest_release')
    def test_check_for_updates_available(self, mock_get_release, updater):
        """Test checking for updates when update is available."""
        mock_get_release.return_value = {
            'tag_name': 'v2.0.0',
            'tarball_url': 'https://example.com/tarball'
        }
        
        result = updater.check_for_updates()
        
        assert result is True
        assert updater._update_available is True
        assert updater._latest_version == '2.0.0'
    
    @patch('src.ota.updater.OTAUpdater._get_latest_release')
    def test_check_for_updates_not_available(self, mock_get_release, updater):
        """Test checking for updates when no update available."""
        mock_get_release.return_value = {
            'tag_name': 'v1.0.0',
            'tarball_url': 'https://example.com/tarball'
        }
        
        result = updater.check_for_updates()
        
        assert result is False
        assert updater._update_available is False
    
    @patch('src.ota.updater.OTAUpdater._get_latest_release')
    def test_check_for_updates_no_release(self, mock_get_release, updater):
        """Test checking for updates when no release found."""
        mock_get_release.return_value = None
        
        result = updater.check_for_updates()
        
        assert result is False
    
    @patch('src.ota.updater.requests.get')
    @patch('builtins.open', new_callable=MagicMock)
    def test_download_update_success(self, mock_open, mock_get, updater):
        """Test downloading update successfully."""
        updater._latest_release = {
            'tarball_url': 'https://example.com/tarball'
        }
        updater._latest_version = '2.0.0'

        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        download_path = updater.download_update()

        assert download_path is not None
        assert download_path.name == 'update_2.0.0.tar.gz'
    
    def test_download_update_no_release(self, updater):
        """Test downloading update with no release data."""
        updater._latest_release = None

        download_path = updater.download_update()

        assert download_path is None

    def test_create_backup_success(self, updater, temp_dirs):
        """Test creating backup successfully."""
        src_dir = temp_dirs['root'] / 'src'
        src_dir.mkdir()
        (src_dir / 'test.py').write_text('test')

        with patch('pathlib.Path.cwd', return_value=temp_dirs['root']):
            backup_dir = updater.create_backup()

        assert backup_dir is not None
        assert backup_dir.exists()

    def test_create_backup_disabled(self, updater):
        """Test creating backup when disabled."""
        updater.backup_enabled = False

        backup_dir = updater.create_backup()

        assert backup_dir is None

    def test_cleanup_old_backups(self, updater, temp_dirs):
        """Test cleanup of old backups."""
        for i in range(5):
            backup = temp_dirs['backup_dir'] / f'backup_{i}'
            backup.mkdir()

        updater._cleanup_old_backups()

        remaining = list(temp_dirs['backup_dir'].iterdir())
        assert len(remaining) == 3

    def test_rollback_success(self, updater, temp_dirs):
        """Test rollback successfully."""
        backup_dir = temp_dirs['backup_dir'] / 'test_backup'
        backup_dir.mkdir()

        src_backup = backup_dir / 'src'
        src_backup.mkdir()
        (src_backup / 'test.py').write_text('backup content')

        version_backup = backup_dir / 'VERSION'
        version_backup.write_text('1.0.0\n')

        with patch('pathlib.Path.cwd', return_value=temp_dirs['root']):
            result = updater.rollback(backup_dir)

        assert result is True

    def test_get_status(self, updater):
        """Test getting OTA status."""
        status = updater.get_status()

        assert 'current_version' in status
        assert 'update_available' in status
        assert 'latest_version' in status
        assert 'last_check' in status
        assert 'auto_update' in status
        assert 'running' in status

        assert status['current_version'] == '1.0.0'
        assert status['update_available'] is False
        assert status['auto_update'] is False
        assert status['running'] is False

