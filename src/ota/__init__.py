#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTA Update Module.

@file       __init__.py
@brief      Package initialization for OTA update system.
@details    Handles over-the-air updates from GitHub
            for seamless software deployment.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.
"""

from .updater import OTAUpdater
from .version_manager import VersionManager

__all__ = ['OTAUpdater', 'VersionManager']
