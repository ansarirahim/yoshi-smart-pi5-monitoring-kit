# Motion Detection Module

Author: A.R. Ansari  
Email: ansarirahim1@gmail.com  
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

---

## Overview

The motion detection module uses background subtraction algorithms to detect moving objects in video streams. It provides robust motion detection with false positive reduction and event logging capabilities.

## Features

- **Background Subtraction**: MOG2 and KNN algorithms
- **Contour Analysis**: Detects moving objects using contour detection
- **False Positive Reduction**: Filters out shadows, lighting changes, and noise
- **Event Logging**: Logs motion events with timestamps and snapshots
- **Configurable Sensitivity**: Adjustable parameters for different scenarios
- **Real-time Performance**: Optimized for Raspberry Pi

## Architecture

```
src/detection/
├── background_subtractor.py  # Background subtraction (MOG2/KNN)
├── motion_detector.py         # Motion detection logic
└── event_logger.py            # Event logging and snapshots
```

## Usage

### Basic Motion Detection

```python
from src.detection import MotionDetector

# Initialize detector
detector = MotionDetector(min_area=500)

# Process frame
motion_detected, bounding_boxes = detector.detect(frame)

if motion_detected:
    print(f"Motion detected! Objects: {len(bounding_boxes)}")
```

### With Event Logging

```python
from src.detection import MotionDetector, EventLogger

# Initialize components
event_logger = EventLogger()

def motion_callback(frame, boxes):
    event_logger.log_event("motion", frame, {"boxes": len(boxes)})

detector = MotionDetector(motion_callback=motion_callback)

# Process frames
motion, boxes = detector.detect(frame)
```

### With Visualization

```python
from src.detection import MotionDetector

detector = MotionDetector()

motion, boxes = detector.detect(frame)

if motion:
    # Draw bounding boxes
    annotated = detector.draw_motion(frame, boxes)
    cv2.imshow("Motion Detection", annotated)
```

## Configuration

Edit `config/detection_config.yaml`:

```yaml
motion_detection:
  method: "MOG2"           # Background subtraction method
  min_area: 500            # Minimum object size (pixels)
  blur_size: 21            # Noise reduction
  threshold: 25            # Sensitivity (lower = more sensitive)
  dilate_iterations: 2     # Fill holes in detected objects
```

## Parameters

### MotionDetector

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_area` | int | 500 | Minimum contour area to consider as motion |
| `blur_size` | int | 21 | Gaussian blur kernel size (must be odd) |
| `threshold` | int | 25 | Binary threshold value (0-255) |
| `dilate_iterations` | int | 2 | Morphological dilation iterations |
| `motion_callback` | callable | None | Callback function when motion detected |

### BackgroundSubtractor

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | str | "MOG2" | Algorithm: "MOG2" or "KNN" |
| `history` | int | 500 | Number of frames for background model |
| `var_threshold` | float | 16 | Threshold for pixel classification |
| `detect_shadows` | bool | True | Whether to detect shadows |

### EventLogger

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_dir` | str | "logs/events" | Directory for event logs |
| `snapshot_dir` | str | "logs/snapshots" | Directory for snapshots |
| `save_snapshots` | bool | True | Whether to save frame snapshots |
| `max_events` | int | 1000 | Maximum events to keep in memory |

## Algorithms

### MOG2 (Mixture of Gaussians)

- Adaptive background model
- Handles gradual lighting changes
- Detects shadows
- Good for outdoor scenes

### KNN (K-Nearest Neighbors)

- More robust to sudden changes
- Better for indoor scenes
- Faster adaptation
- Less sensitive to shadows

## Performance

Tested on Raspberry Pi 4 (4GB RAM):

| Resolution | FPS | CPU Usage |
|------------|-----|-----------|
| 640x480 | 25-30 | 40-50% |
| 1280x720 | 15-20 | 60-70% |
| 1920x1080 | 8-12 | 80-90% |

## Tuning Guide

### High Sensitivity (Detect Small Movements)

```python
detector = MotionDetector(
    min_area=200,        # Lower threshold
    threshold=15,        # More sensitive
    blur_size=11         # Less noise reduction
)
```

### Low Sensitivity (Reduce False Positives)

```python
detector = MotionDetector(
    min_area=1000,       # Higher threshold
    threshold=40,        # Less sensitive
    blur_size=31         # More noise reduction
)
```

### Outdoor (Lighting Changes)

```python
detector = MotionDetector(
    min_area=800,
    threshold=30,
    dilate_iterations=3  # Fill more holes
)
```

## Testing

Run unit tests:

```bash
pytest tests/test_detection/ -v
```

Run with coverage:

```bash
pytest tests/test_detection/ --cov=src/detection --cov-report=html
```

## Integration

### With RTSP Stream Handler

```python
from src.rtsp import RTSPStreamHandler
from src.detection import MotionDetector, EventLogger

# Initialize components
stream = RTSPStreamHandler(url="rtsp://camera_ip/stream")
detector = MotionDetector()
logger = EventLogger()

# Start stream
stream.start()

while True:
    frame = stream.read_frame()
    if frame is not None:
        motion, boxes = detector.detect(frame)
        
        if motion:
            logger.log_event("motion", frame, {"boxes": len(boxes)})
            annotated = detector.draw_motion(frame, boxes)
            cv2.imshow("Motion", annotated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.stop()
```

## Troubleshooting

### Too Many False Positives

- Increase `min_area` parameter
- Increase `threshold` parameter
- Increase `blur_size` for more noise reduction
- Use MOG2 with shadow detection enabled

### Missing Motion Events

- Decrease `min_area` parameter
- Decrease `threshold` parameter
- Decrease `blur_size` for less noise reduction
- Check camera positioning and lighting

### Performance Issues

- Reduce input frame resolution
- Increase `blur_size` (faster processing)
- Use KNN instead of MOG2 (slightly faster)
- Process every Nth frame instead of all frames

## References

- OpenCV Background Subtraction: https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html
- MOG2 Paper: Zivkovic, Z. (2004). Improved adaptive Gaussian mixture model for background subtraction
- KNN Paper: Zivkovic, Z., & van der Heijden, F. (2006). Efficient adaptive density estimation per image pixel

## License

Part of Raspberry Pi Smart Monitoring Kit  
Copyright (c) 2024 A.R. Ansari

