# Fall Detection Module

Author: A.R. Ansari  
Email: ansarirahim1@gmail.com  
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

---

## Overview

The fall detection module identifies falls by analyzing body aspect ratio and motion patterns. It detects vertical-to-horizontal collapse transitions and prolonged inactivity in horizontal positions.

## Features

- **Aspect Ratio Analysis**: Determines person state (standing/sitting/lying)
- **Fall Transition Detection**: Detects standing-to-lying transitions
- **Velocity Analysis**: Measures vertical movement speed
- **Inactivity Detection**: Identifies prolonged lying periods
- **State Tracking**: Monitors person state changes over time
- **Real-time Performance**: Optimized for Raspberry Pi

## How It Works

### Person State Detection

The detector classifies person state based on bounding box aspect ratio (height/width):

- **Standing**: Aspect ratio >= 1.5 (tall and narrow)
- **Sitting**: Aspect ratio between 1.0 and 1.5 (moderate)
- **Lying**: Aspect ratio < 1.0 (wide and short)
- **Fallen**: Detected fall event

### Fall Detection Methods

**Method 1: Rapid Transition**
- Detects standing-to-lying state change
- Calculates vertical velocity of centroid movement
- Triggers if velocity exceeds threshold

**Method 2: Prolonged Inactivity**
- Monitors time spent in lying position
- Triggers if lying exceeds inactivity timeout
- Useful for gradual falls or delayed detection

## Usage

### Basic Fall Detection

```python
from src.detection import FallDetector, PersonState

# Initialize detector
detector = FallDetector()

# Process frame
fall_detected, person_state, bbox = detector.detect(frame)

if fall_detected:
    print("FALL DETECTED!")
    print(f"Person state: {person_state.value}")
```

### With Callback

```python
from src.detection import FallDetector

def on_fall(frame, bbox, velocity):
    print(f"Fall detected! Velocity: {velocity:.2f}")
    # Send alert, save snapshot, etc.

detector = FallDetector(fall_callback=on_fall)

fall, state, bbox = detector.detect(frame)
```

### With Visualization

```python
from src.detection import FallDetector

detector = FallDetector()

fall, state, bbox = detector.detect(frame)

# Draw detection
annotated = detector.draw_detection(frame, bbox, state)
cv2.imshow("Fall Detection", annotated)
```

### Integration with Motion Detection

```python
from src.detection import MotionDetector, FallDetector, EventLogger

motion_detector = MotionDetector()
fall_detector = FallDetector()
logger = EventLogger()

# Process frame
motion, boxes = motion_detector.detect(frame)

if motion:
    # Motion detected, check for fall
    fall, state, bbox = fall_detector.detect(frame)
    
    if fall:
        logger.log_event("fall", frame, {"state": state.value})
```

## Configuration

Edit `config/detection_config.yaml`:

```yaml
fall_detection:
  aspect_ratio_threshold: 1.5      # Height/width threshold
  fall_velocity_threshold: 0.3     # Vertical velocity (0.0-1.0)
  inactivity_timeout: 10.0         # Seconds before timeout
  min_person_area: 2000            # Minimum person size (pixels)
```

## Parameters

### FallDetector

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aspect_ratio_threshold` | float | 1.5 | Threshold for height/width ratio |
| `fall_velocity_threshold` | float | 0.3 | Minimum vertical velocity (0.0-1.0) |
| `inactivity_timeout` | float | 10.0 | Seconds of inactivity to trigger fall |
| `min_person_area` | int | 2000 | Minimum contour area for person |
| `fall_callback` | callable | None | Callback when fall detected |

## Person States

```python
from src.detection import PersonState

PersonState.STANDING  # Vertical position (AR >= 1.5)
PersonState.SITTING   # Moderate position (1.0 <= AR < 1.5)
PersonState.LYING     # Horizontal position (AR < 1.0)
PersonState.FALLEN    # Fall detected
PersonState.UNKNOWN   # No person detected
```

## Accuracy

Target accuracy: 70-80%

**True Positives:**
- Standing to lying transitions
- Prolonged lying periods
- Rapid vertical movements

**False Positives:**
- Person intentionally lying down
- Person sitting on floor
- Camera angle changes

**False Negatives:**
- Very slow falls
- Falls outside camera view
- Occlusions

## Tuning Guide

### High Sensitivity (Detect More Falls)

```python
detector = FallDetector(
    aspect_ratio_threshold=1.3,   # Lower threshold
    fall_velocity_threshold=0.2,  # More sensitive
    inactivity_timeout=5.0        # Shorter timeout
)
```

### Low Sensitivity (Reduce False Positives)

```python
detector = FallDetector(
    aspect_ratio_threshold=2.0,   # Higher threshold
    fall_velocity_threshold=0.5,  # Less sensitive
    inactivity_timeout=15.0       # Longer timeout
)
```

### For Elderly Care

```python
detector = FallDetector(
    aspect_ratio_threshold=1.5,
    fall_velocity_threshold=0.25,  # Detect slower falls
    inactivity_timeout=8.0,        # Moderate timeout
    min_person_area=1500           # Smaller person size
)
```

## Testing

Run unit tests:

```bash
pytest tests/test_detection/test_fall_detector.py -v
```

Run with coverage:

```bash
pytest tests/test_detection/test_fall_detector.py --cov=src/detection --cov-report=html
```

## Performance

Tested on Raspberry Pi 4 (4GB RAM):

| Resolution | FPS | CPU Usage | Accuracy |
|------------|-----|-----------|----------|
| 640x480 | 20-25 | 45-55% | 75-80% |
| 1280x720 | 12-18 | 65-75% | 70-75% |
| 1920x1080 | 6-10 | 85-95% | 65-70% |

## Limitations

1. **Single Person**: Designed for single-person monitoring
2. **Camera Angle**: Works best with side or angled view
3. **Lighting**: Requires adequate lighting for person detection
4. **Occlusions**: Cannot detect falls behind furniture
5. **Intentional Lying**: May trigger false positives

## Improvements for Future

- Multi-person tracking
- Pose estimation with MediaPipe (more accurate)
- Machine learning classifier
- Camera angle compensation
- Activity recognition

## Integration Example

Complete example with RTSP stream, motion detection, and fall detection:

```python
from src.rtsp import RTSPStreamHandler
from src.detection import MotionDetector, FallDetector, EventLogger

# Initialize components
stream = RTSPStreamHandler(url="rtsp://camera_ip/stream")
motion_detector = MotionDetector(min_area=500)
fall_detector = FallDetector()
logger = EventLogger()

# Start stream
stream.start()

while True:
    frame = stream.read_frame()
    if frame is None:
        continue

    # First check for motion
    motion, boxes = motion_detector.detect(frame)

    if motion:
        # Motion detected, check for fall
        fall, state, bbox = fall_detector.detect(frame)

        if fall:
            # Fall detected!
            logger.log_event("fall", frame, {
                "state": state.value,
                "bbox": bbox
            })
            print("FALL DETECTED! Sending alert...")

            # Draw visualization
            annotated = fall_detector.draw_detection(frame, bbox, state)
            cv2.imshow("Fall Detection", annotated)
        else:
            # Just motion, no fall
            annotated = motion_detector.draw_motion(frame, boxes)
            cv2.imshow("Motion Detection", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.stop()
```

## Troubleshooting

### Too Many False Positives

- Increase `aspect_ratio_threshold`
- Increase `fall_velocity_threshold`
- Increase `inactivity_timeout`
- Increase `min_person_area`

### Missing Fall Events

- Decrease `aspect_ratio_threshold`
- Decrease `fall_velocity_threshold`
- Decrease `inactivity_timeout`
- Check camera angle and lighting

### Performance Issues

- Reduce input frame resolution
- Process every Nth frame instead of all frames
- Disable visualization during processing

## References

- Fall Detection Survey: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6359483/
- Aspect Ratio Method: Rougier, C., et al. (2011). "Robust Video Surveillance for Fall Detection"
- OpenCV Background Subtraction: https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html

## License

Part of Raspberry Pi Smart Monitoring Kit
Copyright (c) 2024 A.R. Ansari

