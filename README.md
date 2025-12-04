# Raspberry Pi Smart Monitoring Kit

**Client:** Yoshinori Ueda (Japan)  
**Budget:** $450 Fixed Price  
**Timeline:** 3-4 weeks  
**Platform:** Raspberry Pi 4 (4GB)

## Project Overview

An optional Raspberry Pi 4 upgrade kit for Wi-Fi indoor cameras (ImCam Pro / ICSee app) that adds intelligent monitoring capabilities with complete local processing and privacy-first design.

## Key Features

- **Smart Motion/Fall Detection**: OpenCV-based detection (70-80% accuracy target)
- **LINE Notifications**: Real-time alerts with snapshots via LINE Messaging API
- **Two-Way Control**: Stop/Resume commands via LINE webhook
- **OTA Updates**: Automatic updates from GitHub repository
- **Voice Alerts**: Optional "Are you OK?" voice message on anomaly detection
- **Pan-Tilt Support**: Maintains existing ICSee app control + optional auto-tracking
- **Privacy-First**: 100% local processing, no cloud dependency

## Technical Stack

- **Hardware**: Raspberry Pi 4 (4GB), Pan-Tilt servos (SG90/MG90S), PCA9685 servo driver
- **OS**: Raspberry Pi OS (Debian-based)
- **Language**: Python 3.9+
- **Computer Vision**: OpenCV 4.x
- **Communication**: RTSP, LINE Messaging API, Webhooks
- **Services**: systemd for auto-start and management

## Project Structure

```
.
├── src/                    # Source code
│   ├── rtsp/              # RTSP stream handling
│   ├── detection/         # Motion and fall detection
│   ├── line_api/          # LINE messaging integration
│   ├── ota/               # OTA update system
│   ├── voice/             # Voice alert system
│   ├── pan_tilt/          # Pan-tilt control
│   └── utils/             # Shared utilities
├── tests/                 # Unit and integration tests
├── config/                # Configuration files
├── scripts/               # Setup and deployment scripts
├── docs/                  # Documentation
│   ├── architecture/      # Architecture diagrams
│   └── manual/            # Setup manual
├── .github/               # GitHub Actions workflows
└── requirements.txt       # Python dependencies
```

## Milestones

### Milestone 1: RTSP & Environment Setup ($40, 3-4 days) ✅ COMPLETE
- ✅ Raspberry Pi environment configuration
- ✅ OpenCV installation and optimization
- ✅ RTSP stream integration
- ✅ Frame extraction pipeline
- ✅ Thread-safe frame buffer
- ✅ Automatic reconnection
- ✅ 35 unit tests (100% pass rate, 87% coverage)

### Milestone 2: Motion Detection Engine ($55, 4-5 days) ✅ COMPLETE
- ✅ Background subtraction (MOG2/KNN algorithms)
- ✅ Contour-based motion detection
- ✅ False-positive reduction (shadows, noise, lighting)
- ✅ Event logging and snapshot capture
- ✅ Motion callback system
- ✅ Configurable sensitivity
- ✅ 45 unit tests (100% pass rate, 91% coverage)

### Milestone 3: Fall Detection Algorithm ($70, 5-6 days) ✅ COMPLETE
- ✅ Aspect ratio analysis (height/width)
- ✅ Vertical-to-horizontal collapse detection
- ✅ Rapid transition detection (velocity-based)
- ✅ Prolonged inactivity detection
- ✅ Person state tracking (standing/sitting/lying/fallen)
- ✅ Fall callback system
- ✅ 21 unit tests (100% pass rate, 97% coverage)

### Milestone 4: LINE Alerts ($45, 2-3 days) ✅ COMPLETE
- ✅ LINE Messaging API v3 integration
- ✅ Push notifications for motion/fall events
- ✅ Message formatting with timestamps and metadata
- ✅ Retry logic with configurable parameters
- ✅ Statistics tracking (message count, error count)
- ✅ 18 unit tests (100% pass rate, 93% coverage)

### Milestone 5: LINE Webhook Commands ($45, 2-3 days) ✅ COMPLETE
- ✅ Flask-based webhook server with signature verification
- ✅ Stop/Resume/Status command handling
- ✅ Integration with motion and fall detection pause/resume
- ✅ systemd service configuration for auto-start
- ✅ Health check endpoint
- ✅ 21 unit tests (100% pass rate, 94% coverage)
- ✅ Complete documentation and demo script

### Milestone 6: OTA Update System ($60, 3-4 days) ✅
- ✅ GitHub-based version checking
- ✅ Auto-update script
- ✅ Rollback protection
- ✅ Update logging
- ✅ 30 unit tests (100% pass rate, 70% coverage)
- ✅ Complete documentation and demo script

### Milestone 7: Voice Alert ($30, 1-2 days)
- Audio playback system
- "Are you OK?" trigger
- Volume control

### Milestone 8: Pan-Tilt Integration ($60, 3-4 days)
- ICSee app compatibility
- Python-based PT control
- Centroid tracking
- Smooth movement control

### Milestone 9: Final Delivery ($45, 3-4 days)
- SD card image (.img)
- English setup manual
- Test report (elderly/pet/baby scenarios)

## Development Workflow

1. Each milestone has its own branch from `main`
2. Feature development with unit tests
3. CI/CD pipeline runs tests automatically
4. Code review and merge to `main`
5. Tagged releases for each milestone

## Getting Started

See [docs/manual/SETUP.md](docs/manual/SETUP.md) for installation instructions.

## Documentation

**API Documentation:** Built with Sphinx (Python industry standard)

Build documentation locally:
```bash
pip install -r docs/requirements.txt
cd docs
make html
open _build/html/index.html
```

**Documentation includes:**
- Complete API reference
- Module documentation
- Code examples
- Architecture diagrams

## License

Proprietary - Client: Yoshinori Ueda

## Developer Contact

**A.R. Ansari**
Email: ansarirahim1@gmail.com
WhatsApp: +919024304883
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
GitHub: https://github.com/ansarirahim

