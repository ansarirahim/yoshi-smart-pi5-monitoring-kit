# OTA Update System

Over-the-air (OTA) update system for automatic software updates from GitHub releases.

**Author:** A.R. Ansari  
**Email:** ansarirahim1@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/  
**Project:** Raspberry Pi Smart Monitoring Kit

## Overview

The OTA update system automatically checks for new releases on GitHub and applies updates with backup and rollback protection.

### Features

- Automatic version checking from GitHub releases
- Configurable check interval
- Auto-update or manual update mode
- Backup before update
- Rollback on failure
- Update logging and status tracking
- Semantic versioning support

## Architecture

### Components

1. **VersionManager** - Version tracking and comparison
2. **OTAUpdater** - GitHub integration, download, backup, and update

### Version File

Current version is stored in `VERSION` file at project root:

```
0.1.0
```

### GitHub Releases

Updates are distributed via GitHub releases with semantic version tags:

- Tag format: `v1.0.0`, `v1.1.0`, `v2.0.0`
- Release includes tarball with source code
- Changelog in release description

## Setup

### 1. GitHub Repository Configuration

Create releases on GitHub with version tags:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Then create a release on GitHub from the tag.

### 2. Environment Variables

For private repositories, set GitHub token:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
export GITHUB_REPO=username/repository
```

Add to `.env` file:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=ansarirahim/raspberry-pi-smart-monitoring
```

### 3. Configuration

Edit `config/ota_config.yaml`:

```yaml
github_repo: "${GITHUB_REPO}"
check_interval: 3600  # 1 hour
auto_update: true
backup_enabled: true
backup_path: "/tmp/monitoring_backup"
max_backups: 3
```

## Usage

### Basic Usage

```python
from src.ota import OTAUpdater
import yaml

# Load configuration
with open('config/ota_config.yaml') as f:
    config = yaml.safe_load(f)

# Create updater
updater = OTAUpdater(config)

# Start background checker
updater.start()

# Check status
status = updater.get_status()
print(f"Current version: {status['current_version']}")
print(f"Update available: {status['update_available']}")
```

### Manual Update Check

```python
# Check for updates manually
if updater.check_for_updates():
    print(f"Update available: {updater._latest_version}")
    
    # Apply update manually
    if updater.apply_update():
        print("Update successful")
    else:
        print("Update failed")
```

### Version Management

```python
from src.ota import VersionManager

vm = VersionManager()

# Get current version
current = vm.get_current_version()
print(f"Current version: {current}")

# Compare versions
if vm.is_newer("2.0.0", current):
    print("Update available")

# Parse version
major, minor, patch = vm.parse_version("1.2.3")

# Get next version
next_patch = vm.get_next_version("1.0.0", "patch")  # "1.0.1"
next_minor = vm.get_next_version("1.0.0", "minor")  # "1.1.0"
next_major = vm.get_next_version("1.0.0", "major")  # "2.0.0"
```

### Integration with Main System

```python
from src.ota import OTAUpdater

class MonitoringSystem:
    def __init__(self, config):
        self.config = config
        self.ota_updater = None
    
    def setup(self):
        if self.config.get('ota.enabled'):
            self.ota_updater = OTAUpdater(self.config.get('ota'))
            self.ota_updater.start()
    
    def shutdown(self):
        if self.ota_updater:
            self.ota_updater.stop()
```

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `github_repo` | string | required | GitHub repository (owner/repo) |
| `check_interval` | int | 3600 | Check interval in seconds |
| `auto_update` | bool | true | Enable automatic updates |
| `backup_enabled` | bool | true | Enable backup before update |
| `backup_path` | string | /tmp/monitoring_backup | Backup directory path |
| `max_backups` | int | 3 | Maximum backups to keep |
| `download_timeout` | int | 30 | Download timeout in seconds |
| `max_retries` | int | 3 | Download retry attempts |
| `retry_delay` | int | 5 | Delay between retries |

## Update Process

### Automatic Update Flow

1. Background thread checks for updates every `check_interval` seconds
2. Fetches latest release from GitHub API
3. Compares version with current version
4. If newer version available and `auto_update` enabled:
   - Creates backup of current installation
   - Downloads update tarball
   - Extracts and applies update
   - Updates VERSION file
   - Cleans up temporary files
5. On failure, automatically rolls back to backup

### Manual Update Flow

```python
# Check for updates
if updater.check_for_updates():
    # Download update
    download_path = updater.download_update()

    # Create backup
    backup_dir = updater.create_backup()

    # Apply update
    if updater.apply_update():
        print("Update successful")
    else:
        # Rollback on failure
        updater.rollback(backup_dir)
```

## Backup and Rollback

### Backup Creation

Backups include:
- `src/` directory - All source code
- `config/` directory - Configuration files
- `VERSION` file - Current version

Backup naming: `backup_{version}_{timestamp}`

Example: `backup_1.0.0_20231125_143022`

### Rollback

Rollback is automatic on update failure. Manual rollback:

```python
from pathlib import Path

backup_dir = Path("/tmp/monitoring_backup/backup_1.0.0_20231125_143022")
updater.rollback(backup_dir)
```

## Troubleshooting

### Update Check Fails

**Problem:** Cannot fetch latest release from GitHub

**Solutions:**
1. Check internet connection
2. Verify `github_repo` configuration
3. For private repos, verify `GITHUB_TOKEN` is set
4. Check GitHub API rate limits

### Download Fails

**Problem:** Update download fails or times out

**Solutions:**
1. Increase `download_timeout` in configuration
2. Check network bandwidth
3. Verify release has tarball available
4. Check disk space

### Update Fails

**Problem:** Update application fails

**Solutions:**
1. Check logs for specific error
2. Verify file permissions
3. Check disk space
4. Manually rollback to previous version

### Rollback Fails

**Problem:** Automatic rollback fails

**Solutions:**
1. Manually restore from backup directory
2. Check backup directory exists and is readable
3. Verify file permissions

## Security Considerations

### GitHub Token

- Store token in environment variable, not in code
- Use `.env` file for local development
- Add `.env` to `.gitignore`
- For production, use system environment variables

### Release Verification

- Only download from official GitHub releases
- Verify repository ownership
- Use HTTPS for all API calls

### Backup Protection

- Store backups on persistent storage in production
- Set appropriate file permissions on backup directory
- Regularly test rollback procedure

## Testing

### Unit Tests

Run OTA tests:

```bash
pytest tests/test_ota/ -v --cov=src/ota --cov-report=term-missing
```

Expected results:
- 30 tests passing
- 70%+ coverage for updater
- 100% coverage for version manager

### Manual Testing

Test update process:

```bash
python examples/ota_demo.py --check
python examples/ota_demo.py --update
python examples/ota_demo.py --status
```

## Production Deployment

### Systemd Service

For automatic updates in production, run as systemd service:

```ini
[Unit]
Description=Monitoring System with OTA Updates
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/monitoring
Environment="GITHUB_TOKEN=your_token"
Environment="GITHUB_REPO=username/repo"
ExecStart=/usr/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Persistent Backup Storage

Change backup path to persistent storage:

```yaml
backup_path: "/var/backups/monitoring"
```

Create directory:

```bash
sudo mkdir -p /var/backups/monitoring
sudo chown pi:pi /var/backups/monitoring
```

## API Reference

### OTAUpdater

#### Methods

- `start()` - Start background update checker
- `stop()` - Stop background update checker
- `check_for_updates()` - Check for available updates
- `download_update()` - Download update tarball
- `create_backup()` - Create backup of current installation
- `apply_update()` - Apply downloaded update
- `rollback(backup_dir)` - Rollback to previous version
- `get_status()` - Get current OTA status

### VersionManager

#### Methods

- `get_current_version()` - Get current version from file
- `set_current_version(version)` - Set current version
- `is_valid_version(version)` - Validate version format
- `parse_version(version)` - Parse version into components
- `compare_versions(v1, v2)` - Compare two versions
- `is_newer(v1, v2)` - Check if v1 is newer than v2
- `get_next_version(version, bump)` - Get next version

## Changelog

### Version 0.1.0 (Initial Release)

- GitHub-based OTA update system
- Automatic version checking
- Backup and rollback support
- Semantic versioning
- 30 unit tests with 70%+ coverage


