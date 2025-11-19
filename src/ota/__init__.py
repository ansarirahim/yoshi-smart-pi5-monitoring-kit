"""
OTA Update Module
Handles over-the-air updates from GitHub
"""

from .updater import OTAUpdater
from .version_manager import VersionManager

__all__ = ['OTAUpdater', 'VersionManager']

