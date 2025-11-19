# Getting Started - Raspberry Pi Smart Monitoring Kit

## Quick Start Guide

This guide will help you get started with the project development.

## Prerequisites

### Hardware
- Raspberry Pi 4 (4GB) - **Required for final testing**
- Raspberry Pi 3 B+ or Pi 5 - Can be used for initial development
- MicroSD Card (32GB or larger)
- Development computer (Windows/Mac/Linux)

### Software
- Git
- Python 3.9 or higher
- Code editor (VS Code recommended)
- GitHub account

## Initial Setup

### 1. Clone or Initialize Repository

If starting fresh:
```bash
cd "Raspberry Pi Smart Monitoring Kit"
chmod +x scripts/init_git.sh
./scripts/init_git.sh
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `raspberry-pi-smart-monitoring`
3. Do NOT initialize with README (we already have one)
4. Copy the repository URL

### 3. Connect to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/raspberry-pi-smart-monitoring.git
git push -u origin main
```

### 4. Setup Development Environment

#### On Your Development Computer:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### On Raspberry Pi (when ready):

```bash
# Make install script executable
chmod +x scripts/install.sh

# Run installation
sudo ./scripts/install.sh
```

## Development Workflow

### Starting Milestone 1

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Create milestone branch
git checkout -b milestone-1-rtsp-setup

# Push branch to GitHub
git push -u origin milestone-1-rtsp-setup
```

### Daily Development Cycle

1. **Write Code**
   ```bash
   # Edit files in src/rtsp/
   # Add unit tests in tests/test_rtsp/
   ```

2. **Test Locally**
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Check code quality
   flake8 src/
   black src/ --check
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: implement RTSP reconnection logic"
   git push origin milestone-1-rtsp-setup
   ```

4. **Monitor CI/CD**
   - Check GitHub Actions for test results
   - Fix any failing tests

### Completing a Milestone

```bash
# Ensure all tests pass
pytest tests/ -v --cov=src

# Merge to main
git checkout main
git pull origin main
git merge --no-ff milestone-1-rtsp-setup

# Tag the milestone
git tag -a milestone-1 -m "Milestone 1: RTSP & Environment Setup"

# Push to GitHub
git push origin main
git push origin milestone-1

# Update MILESTONES.md status
# Update CHANGELOG.md
```

## Project Structure Overview

```
src/
├── rtsp/           # Milestone 1: RTSP stream handling
├── detection/      # Milestone 2-3: Motion and fall detection
├── line_api/       # Milestone 4-5: LINE integration
├── ota/            # Milestone 6: OTA updates
├── voice/          # Milestone 7: Voice alerts
├── pan_tilt/       # Milestone 8: Pan-tilt control
└── utils/          # Shared utilities

tests/              # Mirror structure of src/
config/             # Configuration files
docs/               # Documentation
scripts/            # Utility scripts
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Module
```bash
pytest tests/test_rtsp/ -v
```

### With Coverage
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### View Coverage Report
```bash
# Open htmlcov/index.html in browser
```

## Configuration

### Development Configuration

1. Copy example files:
   ```bash
   cp config/secrets.example.json config/secrets.json
   cp .env.example .env
   ```

2. Edit `config/config.yaml` for your setup

3. Edit `config/secrets.json` with actual credentials (DO NOT COMMIT)

### Environment Variables

Set in `.env` file:
```bash
LINE_CHANNEL_ACCESS_TOKEN=your_token
CAMERA_RTSP_URL=rtsp://camera_ip:554/stream
LOG_LEVEL=DEBUG
```

## Client Communication

### After Each Milestone

Send update to Yoshinori Ueda:

```
Subject: Milestone [X] Completed - [Milestone Name]

Hello Yoshi,

I have completed Milestone [X]: [Name]

Deliverables:
- [List deliverables]
- [Include screenshots/videos if applicable]

The code has been tested and all unit tests are passing.
Branch: milestone-[X]-[name]
Tag: milestone-[X]

Next milestone will be: [Next milestone name]
Estimated completion: [Date]

Please let me know if you have any questions or need any changes.

Best regards,
Rahim
```

## Troubleshooting

### Tests Failing
- Check Python version: `python --version` (should be 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Clear pytest cache: `pytest --cache-clear`

### Import Errors
- Ensure virtual environment is activated
- Check PYTHONPATH includes src directory
- Run from project root directory

### Git Issues
- Check current branch: `git branch`
- Check remote: `git remote -v`
- Pull latest changes: `git pull origin main`

## Useful Commands

### Git
```bash
# View all branches
git branch -a

# View commit history
git log --oneline --graph

# View changes
git status
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

### Python
```bash
# Check installed packages
pip list

# Update package
pip install --upgrade package_name

# Freeze dependencies
pip freeze > requirements.txt
```

### Testing
```bash
# Run specific test
pytest tests/test_utils/test_config_loader.py::TestConfigLoader::test_load_config_file

# Run with markers
pytest -m unit
pytest -m integration

# Stop on first failure
pytest -x
```

## Resources

- **Project Documentation**: See `docs/` folder
- **Architecture Diagram**: `docs/architecture/system-architecture.drawio`
- **Setup Manual**: `docs/manual/SETUP.md`
- **Branching Strategy**: `BRANCHING_STRATEGY.md`
- **Milestones**: `MILESTONES.md`
- **Project Guide**: `PROJECT_GUIDE.md`

## Next Steps

1. ✅ Review project structure
2. ✅ Setup development environment
3. ✅ Initialize Git repository
4. ✅ Push to GitHub
5. ⏭️ Start Milestone 1: RTSP & Environment Setup
6. ⏭️ Implement RTSP stream handler
7. ⏭️ Write unit tests
8. ⏭️ Complete and merge Milestone 1

## Support

For questions or issues:
- Review documentation in `docs/`
- Check `PROJECT_GUIDE.md` for detailed instructions
- Review `MILESTONES.md` for milestone details

---

**Good luck with the development!** 🚀

