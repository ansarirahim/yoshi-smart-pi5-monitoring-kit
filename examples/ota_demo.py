"""
OTA Update System Demo.

Demonstrates OTA update functionality including version checking,
manual updates, and status monitoring.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit

Usage:
    python examples/ota_demo.py --check
    python examples/ota_demo.py --update
    python examples/ota_demo.py --status
    python examples/ota_demo.py --version
"""

import sys
import os
import argparse
import yaml
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ota import OTAUpdater, VersionManager  # noqa: E402


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config():
    """Load OTA configuration."""
    config_path = Path('config/ota_config.yaml')

    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    github_repo = os.getenv('GITHUB_REPO')
    if github_repo:
        config['github_repo'] = github_repo

    return config


def check_version(args):
    """Display current version."""
    try:
        vm = VersionManager()
        current = vm.get_current_version()

        print("\n" + "=" * 50)
        print("VERSION INFORMATION")
        print("=" * 50)
        print(f"Current Version: {current}")

        major, minor, patch = vm.parse_version(current)
        print(f"  Major: {major}")
        print(f"  Minor: {minor}")
        print(f"  Patch: {patch}")

        print("\nNext Versions:")
        print(f"  Next Patch: {vm.get_next_version(current, 'patch')}")
        print(f"  Next Minor: {vm.get_next_version(current, 'minor')}")
        print(f"  Next Major: {vm.get_next_version(current, 'major')}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def check_updates(args):
    """Check for available updates."""
    try:
        config = load_config()
        updater = OTAUpdater(config)

        print("\n" + "=" * 50)
        print("CHECKING FOR UPDATES")
        print("=" * 50)
        print(f"Repository: {config['github_repo']}")

        vm = VersionManager()
        current = vm.get_current_version()
        print(f"Current Version: {current}")

        print("\nChecking GitHub releases...")

        if updater.check_for_updates():
            print(f"\nUpdate Available: {updater._latest_version}")
            print(f"Release Name: {updater._latest_release.get('name', 'N/A')}")
            print(f"Published: {updater._latest_release.get('published_at', 'N/A')}")

            body = updater._latest_release.get('body', '')
            if body:
                print("\nChangelog:")
                print("-" * 50)
                print(body[:500])
                if len(body) > 500:
                    print("...")
        else:
            print("\nNo updates available")
            print("You are running the latest version")

        print("=" * 50 + "\n")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def apply_update(args):
    """Apply available update."""
    try:
        config = load_config()
        config['auto_update'] = False
        updater = OTAUpdater(config)

        print("\n" + "=" * 50)
        print("APPLYING UPDATE")
        print("=" * 50)

        if not updater.check_for_updates():
            print("No updates available")
            print("=" * 50 + "\n")
            return

        print(f"Update Version: {updater._latest_version}")

        if not args.yes:
            response = input("\nProceed with update? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Update cancelled")
                print("=" * 50 + "\n")
                return

        print("\nApplying update...")

        if updater.apply_update():
            print("\nUpdate successful!")
            print(f"New version: {updater._latest_version}")
        else:
            print("\nUpdate failed!")
            print("System rolled back to previous version")

        print("=" * 50 + "\n")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def show_status(args):
    """Show OTA system status."""
    try:
        config = load_config()
        updater = OTAUpdater(config)

        status = updater.get_status()

        print("\n" + "=" * 50)
        print("OTA SYSTEM STATUS")
        print("=" * 50)
        print(f"Current Version: {status['current_version']}")
        print(f"Update Available: {status['update_available']}")
        print(f"Latest Version: {status['latest_version'] or 'N/A'}")
        print(f"Last Check: {status['last_check'] or 'Never'}")
        print(f"Auto Update: {status['auto_update']}")
        print(f"Running: {status['running']}")
        print("\nConfiguration:")
        print(f"  Repository: {config['github_repo']}")
        print(f"  Check Interval: {config['check_interval']}s")
        print(f"  Backup Enabled: {config['backup_enabled']}")
        print(f"  Backup Path: {config['backup_path']}")
        print(f"  Max Backups: {config['max_backups']}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='OTA Update System Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    subparsers.add_parser('version', help='Show current version')
    subparsers.add_parser('check', help='Check for updates')

    update_parser = subparsers.add_parser('update', help='Apply update')
    update_parser.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')

    subparsers.add_parser('status', help='Show OTA status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    setup_logging()

    if args.command == 'version':
        check_version(args)
    elif args.command == 'check':
        check_updates(args)
    elif args.command == 'update':
        apply_update(args)
    elif args.command == 'status':
        show_status(args)


if __name__ == '__main__':
    main()
