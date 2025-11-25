"""
Version Manager for OTA Updates.

Handles version tracking, comparison, and changelog management.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import re
from typing import Tuple
from pathlib import Path


class VersionManager:
    """
    Version manager for tracking and comparing software versions.

    Supports semantic versioning (MAJOR.MINOR.PATCH) format.
    Provides version comparison and validation.

    Args:
        version_file: Path to version file (default: VERSION)

    Example:
        vm = VersionManager()
        current = vm.get_current_version()

        if vm.is_newer("1.2.0", current):
            print("Update available!")
    """

    def __init__(self, version_file: str = "VERSION"):
        """Initialize version manager."""
        self.version_file = Path(version_file)
        self._version_pattern = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')

    def get_current_version(self) -> str:
        """
        Get current version from version file.

        Returns:
            Current version string (e.g., "1.0.0")

        Raises:
            FileNotFoundError: If version file doesn't exist
            ValueError: If version format is invalid
        """
        if not self.version_file.exists():
            raise FileNotFoundError(f"Version file not found: {self.version_file}")

        version = self.version_file.read_text().strip()

        if not self.is_valid_version(version):
            raise ValueError(f"Invalid version format: {version}")

        return version

    def set_current_version(self, version: str) -> None:
        """
        Set current version in version file.

        Args:
            version: Version string to set

        Raises:
            ValueError: If version format is invalid
        """
        if not self.is_valid_version(version):
            raise ValueError(f"Invalid version format: {version}")

        self.version_file.write_text(version + "\n")

    def is_valid_version(self, version: str) -> bool:
        """
        Check if version string is valid.

        Args:
            version: Version string to validate

        Returns:
            True if version is valid, False otherwise
        """
        return self._version_pattern.match(version) is not None

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """
        Parse version string into components.

        Args:
            version: Version string to parse

        Returns:
            Tuple of (major, minor, patch)

        Raises:
            ValueError: If version format is invalid
        """
        match = self._version_pattern.match(version)

        if not match:
            raise ValueError(f"Invalid version format: {version}")

        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2

        Raises:
            ValueError: If either version format is invalid
        """
        v1 = self.parse_version(version1)
        v2 = self.parse_version(version2)

        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0

    def is_newer(self, version1: str, version2: str) -> bool:
        """
        Check if version1 is newer than version2.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            True if version1 is newer than version2
        """
        return self.compare_versions(version1, version2) > 0

    def get_next_version(self, version: str, bump: str = "patch") -> str:
        """
        Get next version by bumping major, minor, or patch.

        Args:
            version: Current version string
            bump: Version component to bump ("major", "minor", or "patch")

        Returns:
            Next version string

        Raises:
            ValueError: If version format is invalid or bump type is invalid
        """
        major, minor, patch = self.parse_version(version)

        if bump == "major":
            return f"{major + 1}.0.0"
        elif bump == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump}. Must be 'major', 'minor', or 'patch'")
