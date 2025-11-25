"""
OTA Update Module.

Handles over-the-air updates from GitHub
for seamless software deployment.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

from .updater import OTAUpdater
from .version_manager import VersionManager

__all__ = ['OTAUpdater', 'VersionManager']
