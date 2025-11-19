# Changelog

All notable changes to the Raspberry Pi Smart Monitoring Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Project Setup
- Initial project structure created
- CI/CD workflows configured
- Branching strategy defined
- Architecture diagram created

## [Milestone-1] - 2025-11-19

### Added
- RTSP stream handler with automatic reconnection logic
- Frame buffer with thread-safe circular buffer implementation
- Comprehensive unit tests (27 tests, 100% pass rate)
- Test coverage: 84% for stream_handler, 97% for frame_buffer
- LINE Messaging API credentials configured
- Utility modules: logger and config_loader

### Features
- Automatic reconnection with exponential backoff
- Thread-safe frame buffering
- FPS calculation and stream statistics
- Credential masking in logs for security
- Configurable buffer size and reconnection attempts

### Testing
- 14 tests for FrameBuffer (all passing)
- 13 tests for RTSPStreamHandler (all passing)
- Thread safety tests included
- Mock-based testing for RTSP connections

## [Milestone-2] - TBD

### Added
- Motion detection engine
- Background subtraction algorithm
- False-positive reduction
- Event logging system
- Unit tests for motion detection

## [Milestone-3] - TBD

### Added
- Fall detection algorithm
- Body angle estimation
- Vertical collapse detection
- Inactivity monitoring
- Unit tests for fall detection

## [Milestone-4] - TBD

### Added
- LINE Messaging API integration
- Push notification system
- Snapshot attachment feature
- Integration tests for LINE API

## [Milestone-5] - TBD

### Added
- Webhook server (Flask)
- Stop/Resume command handling
- systemd service configuration
- Unit tests for webhook

## [Milestone-6] - TBD

### Added
- OTA update manager
- GitHub version checking
- Auto-update script
- Rollback protection
- Unit tests for OTA system

## [Milestone-7] - TBD

### Added
- Voice alert player
- Audio playback system
- "Are you OK?" trigger
- Unit tests for voice alerts

## [Milestone-8] - TBD

### Added
- Pan-tilt controller
- PCA9685 servo driver integration
- Auto-tracking engine
- Centroid tracking algorithm
- Unit tests for pan-tilt system

## [Milestone-9] - TBD

### Added
- SD card image (.img)
- English setup manual
- Test report (elderly/pet/baby scenarios)
- Final documentation

