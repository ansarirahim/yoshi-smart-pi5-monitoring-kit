"""
OTA Updater for GitHub-based updates.

Handles version checking, downloading, backup, and update application.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import os
import shutil
import tarfile
import logging
import requests
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .version_manager import VersionManager


class OTAUpdater:
    """
    OTA updater for GitHub-based updates.

    Checks for updates from GitHub releases, downloads updates,
    creates backups, and applies updates with rollback support.

    Args:
        config: OTA configuration dictionary
        version_manager: VersionManager instance (optional)

    Example:
        config = {
            'github_repo': 'username/repo',
            'check_interval': 3600,
            'auto_update': True,
            'backup_enabled': True
        }

        updater = OTAUpdater(config)
        updater.start()
    """

    def __init__(
        self,
        config: Dict[str, Any],
        version_manager: Optional[VersionManager] = None
    ):
        """Initialize OTA updater."""
        self.config = config
        self.version_manager = version_manager or VersionManager()
        self.logger = logging.getLogger(__name__)

        self.github_repo = config.get('github_repo', '')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.check_interval = config.get('check_interval', 3600)
        self.auto_update = config.get('auto_update', True)
        self.backup_enabled = config.get('backup_enabled', True)
        self.backup_path = Path(config.get('backup_path', '/tmp/monitoring_backup'))
        self.max_backups = config.get('max_backups', 3)

        self._running = False
        self._check_thread = None
        self._last_check = None
        self._update_available = False
        self._latest_version = None
        self._latest_release = None

    def start(self) -> None:
        """Start background update checker."""
        if self._running:
            self.logger.warning("OTA updater already running")
            return

        self._running = True
        self._check_thread = threading.Thread(target=self._check_loop, daemon=True)
        self._check_thread.start()
        self.logger.info("OTA updater started")

    def stop(self) -> None:
        """Stop background update checker."""
        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=5)
        self.logger.info("OTA updater stopped")

    def _check_loop(self) -> None:
        """Background loop for checking updates."""
        while self._running:
            try:
                self.check_for_updates()

                if self._update_available and self.auto_update:
                    msg = "Auto-update enabled, applying update to "
                    msg += f"{self._latest_version}"
                    self.logger.info(msg)
                    self.apply_update()

            except Exception as e:
                self.logger.error(f"Error in update check loop: {e}")

            time.sleep(self.check_interval)

    def check_for_updates(self) -> bool:
        """
        Check for available updates from GitHub.

        Returns:
            True if update is available, False otherwise
        """
        try:
            current_version = self.version_manager.get_current_version()
            self.logger.info(f"Checking for updates (current: {current_version})")

            release = self._get_latest_release()

            if not release:
                self.logger.warning("No releases found")
                self._last_check = datetime.now()
                return False

            latest_version = release['tag_name'].lstrip('v')

            if self.version_manager.is_newer(latest_version, current_version):
                self.logger.info(f"Update available: {latest_version}")
                self._update_available = True
                self._latest_version = latest_version
                self._latest_release = release
                self._last_check = datetime.now()
                return True
            else:
                self.logger.info("No updates available")
                self._update_available = False
                self._last_check = datetime.now()
                return False

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return False

    def _get_latest_release(self) -> Optional[Dict[str, Any]]:
        """
        Get latest release from GitHub API.

        Returns:
            Release data dictionary or None if error
        """
        url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        headers = {}

        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching latest release: {e}")
            return None

    def download_update(self) -> Optional[Path]:
        """
        Download update tarball from GitHub.

        Returns:
            Path to downloaded tarball or None if error
        """
        if not self._latest_release:
            self.logger.error("No release data available")
            return None

        tarball_url = self._latest_release.get('tarball_url')

        if not tarball_url:
            self.logger.error("No tarball URL in release")
            return None

        download_path = Path(f"/tmp/update_{self._latest_version}.tar.gz")

        try:
            self.logger.info(f"Downloading update from {tarball_url}")

            headers = {}
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"

            response = requests.get(tarball_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Downloaded update to {download_path}")
            return download_path

        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return None

    def create_backup(self) -> Optional[Path]:
        """
        Create backup of current installation.

        Returns:
            Path to backup directory or None if error
        """
        if not self.backup_enabled:
            self.logger.info("Backup disabled, skipping")
            return None

        try:
            current_version = self.version_manager.get_current_version()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_path / f"backup_{current_version}_{timestamp}"

            self.logger.info(f"Creating backup at {backup_dir}")

            backup_dir.mkdir(parents=True, exist_ok=True)

            src_dir = Path("src")
            if src_dir.exists():
                shutil.copytree(src_dir, backup_dir / "src", dirs_exist_ok=True)

            config_dir = Path("config")
            if config_dir.exists():
                shutil.copytree(config_dir, backup_dir / "config", dirs_exist_ok=True)

            version_file = Path("VERSION")
            if version_file.exists():
                shutil.copy2(version_file, backup_dir / "VERSION")

            self._cleanup_old_backups()

            self.logger.info("Backup created successfully")
            return backup_dir

        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return None

    def _cleanup_old_backups(self) -> None:
        """Remove old backups exceeding max_backups limit."""
        if not self.backup_path.exists():
            return

        backups = sorted(
            [d for d in self.backup_path.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        for old_backup in backups[self.max_backups:]:
            self.logger.info(f"Removing old backup: {old_backup}")
            shutil.rmtree(old_backup)

    def apply_update(self) -> bool:
        """
        Apply downloaded update.

        Returns:
            True if update successful, False otherwise
        """
        try:
            backup_dir = self.create_backup()

            download_path = self.download_update()
            if not download_path:
                return False

            self.logger.info("Extracting update")
            extract_dir = Path("/tmp/update_extract")

            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True)

            with tarfile.open(download_path, 'r:gz') as tar:
                tar.extractall(extract_dir)

            extracted_dirs = list(extract_dir.iterdir())
            if not extracted_dirs:
                self.logger.error("No content in extracted tarball")
                return False

            source_dir = extracted_dirs[0]

            self.logger.info("Applying update")

            src_dir = source_dir / "src"
            if src_dir.exists():
                shutil.copytree(src_dir, Path("src"), dirs_exist_ok=True)

            config_dir = source_dir / "config"
            if config_dir.exists():
                shutil.copytree(config_dir, Path("config"), dirs_exist_ok=True)

            version_file = source_dir / "VERSION"
            if version_file.exists():
                shutil.copy2(version_file, Path("VERSION"))

            self.version_manager.set_current_version(self._latest_version)

            shutil.rmtree(extract_dir)
            download_path.unlink()

            self.logger.info(f"Update to {self._latest_version} applied successfully")
            self._update_available = False

            return True

        except Exception as e:
            self.logger.error(f"Error applying update: {e}")

            if backup_dir:
                self.logger.info("Attempting rollback")
                self.rollback(backup_dir)

            return False

    def rollback(self, backup_dir: Path) -> bool:
        """
        Rollback to previous version from backup.

        Args:
            backup_dir: Path to backup directory

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            self.logger.info(f"Rolling back from {backup_dir}")

            src_backup = backup_dir / "src"
            if src_backup.exists():
                shutil.copytree(src_backup, Path("src"), dirs_exist_ok=True)

            config_backup = backup_dir / "config"
            if config_backup.exists():
                shutil.copytree(config_backup, Path("config"), dirs_exist_ok=True)

            version_backup = backup_dir / "VERSION"
            if version_backup.exists():
                shutil.copy2(version_backup, Path("VERSION"))

            self.logger.info("Rollback successful")
            return True

        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get current OTA status.

        Returns:
            Status dictionary with version info and update status
        """
        try:
            current_version = self.version_manager.get_current_version()
        except Exception:
            current_version = "unknown"

        return {
            'current_version': current_version,
            'update_available': self._update_available,
            'latest_version': self._latest_version,
            'last_check': self._last_check.isoformat() if self._last_check else None,
            'auto_update': self.auto_update,
            'running': self._running
        }
