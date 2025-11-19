# Raspberry Pi Smart Monitoring Kit - Project Guide

## Overview

This document provides a comprehensive guide for developing the Raspberry Pi Smart Monitoring Kit project across all 9 milestones.

## Project Structure

```
Raspberry Pi Smart Monitoring Kit/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI pipeline
│       └── milestone-release.yml     # Release workflow
├── config/
│   ├── config.yaml                   # Main configuration
│   └── secrets.example.json          # Secrets template
├── docs/
│   ├── architecture/
│   │   └── system-architecture.drawio # Architecture diagram (QML)
│   └── manual/
│       └── SETUP.md                  # Setup manual
├── scripts/
│   ├── install.sh                    # Installation script
│   └── create_image.sh               # SD card image creation
├── src/
│   ├── rtsp/                         # RTSP stream handling
│   ├── detection/                    # Motion & fall detection
│   ├── line_api/                     # LINE messaging
│   ├── ota/                          # OTA updates
│   ├── voice/                        # Voice alerts
│   ├── pan_tilt/                     # Pan-tilt control
│   └── utils/                        # Utilities
├── tests/                            # Unit & integration tests
├── main.py                           # Main application
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package setup
├── pytest.ini                        # Pytest configuration
├── .gitignore                        # Git ignore rules
├── README.md                         # Project README
├── CHANGELOG.md                      # Change log
├── BRANCHING_STRATEGY.md             # Git workflow
└── PROJECT_GUIDE.md                  # This file
```

## Development Workflow

### 1. Initialize Git Repository

```bash
# Initialize repository
git init
git add .
git commit -m "chore: initial project setup"

# Create main branch
git branch -M main

# Add remote (update with your GitHub repo)
git remote add origin https://github.com/username/rpi-smart-monitoring.git
git push -u origin main
```

### 2. Milestone Development Process

For each milestone:

#### Step 1: Create Branch
```bash
git checkout main
git pull origin main
git checkout -b milestone-1-rtsp-setup
```

#### Step 2: Develop Features
- Implement module functionality
- Write unit tests
- Update documentation

#### Step 3: Test Locally
```bash
# Run tests
pytest tests/ -v --cov=src

# Run linting
flake8 src/
black src/ --check

# Run type checking
mypy src/
```

#### Step 4: Commit Changes
```bash
git add .
git commit -m "feat: implement RTSP stream handler with reconnection logic"
```

#### Step 5: Push and Create PR
```bash
git push origin milestone-1-rtsp-setup
# Create Pull Request on GitHub
```

#### Step 6: Merge to Main
```bash
git checkout main
git merge --no-ff milestone-1-rtsp-setup
git tag -a milestone-1 -m "Milestone 1: RTSP & Environment Setup"
git push origin main
git push origin milestone-1
```

## Milestone Details

### Milestone 1: RTSP & Environment Setup
**Branch:** `milestone-1-rtsp-setup`  
**Duration:** 3-4 days  
**Budget:** $40

**Tasks:**
- [ ] Setup Raspberry Pi development environment
- [ ] Install and configure OpenCV
- [ ] Implement RTSP stream handler (`src/rtsp/stream_handler.py`)
- [ ] Implement frame buffer (`src/rtsp/frame_buffer.py`)
- [ ] Add reconnection logic for stream failures
- [ ] Write unit tests (`tests/test_rtsp/`)
- [ ] Update documentation

**Deliverables:**
- Working RTSP pipeline
- Unit tests with >80% coverage
- Documentation

### Milestone 2: Motion Detection Engine
**Branch:** `milestone-2-motion-detection`  
**Duration:** 4-5 days  
**Budget:** $55

**Tasks:**
- [ ] Implement background subtraction
- [ ] Add motion vector analysis
- [ ] Implement area/size filtering
- [ ] Add false-positive reduction
- [ ] Implement snapshot capture
- [ ] Add event logging
- [ ] Write unit tests
- [ ] Performance optimization

**Deliverables:**
- Motion detection module
- Event snapshots
- Unit tests
- Performance benchmarks

### Milestone 3: Fall Detection Algorithm
**Branch:** `milestone-3-fall-detection`  
**Duration:** 5-6 days  
**Budget:** $70

**Tasks:**
- [ ] Implement body angle estimation
- [ ] Add vertical-to-horizontal collapse detection
- [ ] Implement inactivity monitoring
- [ ] Tune thresholds for 70-80% accuracy
- [ ] Add confidence scoring
- [ ] Write unit tests
- [ ] Test with sample scenarios

**Deliverables:**
- Fall detection module
- Accuracy report
- Unit tests
- Sample test videos

### Milestone 4: LINE Messaging API Integration
**Branch:** `milestone-4-line-alerts`  
**Duration:** 2-3 days  
**Budget:** $45

**Tasks:**
- [ ] Setup LINE Messaging API client
- [ ] Implement push notification
- [ ] Add snapshot attachment
- [ ] Format messages properly
- [ ] Add error handling
- [ ] Write integration tests

**Deliverables:**
- LINE messenger module
- Integration tests
- Configuration guide

### Milestone 5: LINE Webhook Commands
**Branch:** `milestone-5-line-webhook`  
**Duration:** 2-3 days  
**Budget:** $45

**Tasks:**
- [ ] Implement Flask webhook server
- [ ] Add stop/resume command parsing
- [ ] Integrate with detection modules
- [ ] Create systemd service
- [ ] Add SSL support (optional)
- [ ] Write unit tests

**Deliverables:**
- Webhook server
- systemd service file
- Unit tests

### Milestone 6: OTA Update System
**Branch:** `milestone-6-ota-updates`  
**Duration:** 3-4 days  
**Budget:** $60

**Tasks:**
- [ ] Implement GitHub version checker
- [ ] Add auto-update script
- [ ] Implement rollback protection
- [ ] Add update logging
- [ ] Test update scenarios
- [ ] Write unit tests

**Deliverables:**
- OTA update module
- Update scripts
- Unit tests
- Update documentation

### Milestone 7: Voice Alert Feature
**Branch:** `milestone-7-voice-alert`  
**Duration:** 1-2 days  
**Budget:** $30

**Tasks:**
- [ ] Implement audio playback system
- [ ] Add "Are you OK?" trigger
- [ ] Implement volume control
- [ ] Test audio output
- [ ] Write unit tests

**Deliverables:**
- Voice alert module
- Audio files
- Unit tests

### Milestone 8: Pan-Tilt Integration & Auto Tracking
**Branch:** `milestone-8-pan-tilt`  
**Duration:** 3-4 days  
**Budget:** $60

**Tasks:**
- [ ] Implement PCA9685 servo driver
- [ ] Add pan-tilt controller
- [ ] Implement centroid tracking
- [ ] Add smooth movement control
- [ ] Ensure ICSee app compatibility
- [ ] Write unit tests
- [ ] Hardware testing

**Deliverables:**
- Pan-tilt controller
- Auto-tracking module
- Unit tests
- Wiring diagram

### Milestone 9: Final Image & Documentation
**Branch:** `milestone-9-final-delivery`  
**Duration:** 3-4 days  
**Budget:** $45

**Tasks:**
- [ ] Create SD card image
- [ ] Write English setup manual
- [ ] Conduct elderly fall testing
- [ ] Conduct pet movement testing
- [ ] Conduct baby monitoring testing
- [ ] Write test report
- [ ] Final code cleanup
- [ ] Package deliverables

**Deliverables:**
- SD card image (.img)
- English setup manual
- Test report
- Final documentation

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Aim for >80% code coverage

### Integration Tests
- Test component interactions
- Test with real RTSP streams (if available)
- Test LINE API integration

### Hardware Tests
- Test on actual Raspberry Pi 4
- Test with real camera
- Test servo movements
- Test audio output

## CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

1. **On Push/PR**: Runs tests, linting, type checking
2. **On Tag**: Creates release with artifacts
3. **Coverage Reports**: Uploaded to Codecov

## Best Practices

1. **Code Quality**
   - Follow PEP 8 style guide
   - Use type hints
   - Write docstrings
   - Keep functions small and focused

2. **Testing**
   - Write tests before or alongside code
   - Test edge cases
   - Use fixtures for common setups

3. **Documentation**
   - Update README for major changes
   - Document configuration options
   - Add inline comments for complex logic

4. **Git Workflow**
   - Use conventional commits
   - Keep commits atomic
   - Write descriptive commit messages

## Client Communication

Update client after each milestone:
- Share progress screenshots/videos
- Demonstrate working features
- Request feedback
- Confirm next milestone scope

## Hardware Shopping List

See README.md for complete hardware requirements.

## Support and Troubleshooting

For issues during development:
1. Check logs: `sudo journalctl -u rpi-monitoring -f`
2. Verify configuration: `config/config.yaml`
3. Test components individually
4. Check hardware connections

## Final Delivery Checklist

- [ ] All 9 milestones completed
- [ ] All tests passing
- [ ] SD card image created and tested
- [ ] English manual completed
- [ ] Test report completed
- [ ] Code well-commented
- [ ] Documentation complete
- [ ] Client approval received

