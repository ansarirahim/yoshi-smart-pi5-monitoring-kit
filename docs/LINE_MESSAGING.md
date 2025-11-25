# LINE Messaging Module

Author: A.R. Ansari  
Email: ansarirahim1@gmail.com  
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

---

## Overview

The LINE messaging module sends push notifications with optional image snapshots via LINE Messaging API. It handles message formatting, error recovery, and retry logic for reliable alert delivery.

## Features

- **Push Notifications**: Send text alerts to LINE users
- **Image Snapshots**: Attach JPEG images to alerts
- **Message Formatting**: Automatic timestamp and metadata formatting
- **Error Recovery**: Automatic retry with exponential backoff
- **Statistics Tracking**: Monitor message count and error rate
- **Rate Limiting**: Prevent notification spam

## Setup

### 1. Create LINE Messaging API Channel

1. Visit [LINE Developers Console](https://developers.line.biz/console/)
2. Create a new provider (or use existing)
3. Create a Messaging API channel
4. Note your Channel Access Token and Channel Secret

### 2. Get Your LINE User ID

1. Add your bot as a friend using QR code
2. Send any message to the bot
3. Check webhook logs to find your User ID
4. Alternatively, use LINE's Profile API

### 3. Set Environment Variables

```bash
export LINE_CHANNEL_ACCESS_TOKEN="your_channel_access_token"
export LINE_CHANNEL_SECRET="your_channel_secret"
export LINE_USER_ID="your_user_id"
```

Or create a `.env` file:

```
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret
LINE_USER_ID=your_user_id
```

### 4. Update Configuration

Edit `config/line_config.yaml`:

```yaml
line:
  channel_access_token: ""  # Set via env var
  user_id: ""  # Set via env var
  send_snapshots: true
  snapshot_quality: 85
  max_retries: 3
  retry_delay: 2.0
```

## Usage

### Basic Usage

```python
from src.line_api import LINEMessenger
import os

# Initialize messenger
messenger = LINEMessenger(
    channel_access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),
    user_id=os.getenv("LINE_USER_ID")
)

# Send simple alert
messenger.send_alert("motion")

# Send alert with metadata
messenger.send_alert("fall", metadata={"velocity": 0.5})
```

### With Image Snapshot

```python
import cv2
from src.line_api import LINEMessenger

messenger = LINEMessenger(
    channel_access_token=token,
    user_id=user_id,
    send_snapshots=True,
    snapshot_quality=85
)

# Capture frame
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Send alert with snapshot
messenger.send_alert("motion", frame=frame)
```

### Integration with Detection

```python
from src.rtsp import RTSPStreamHandler
from src.detection import MotionDetector, FallDetector
from src.line_api import LINEMessenger

# Initialize components
stream = RTSPStreamHandler(url="rtsp://camera/stream")
motion_detector = MotionDetector()
fall_detector = FallDetector()
messenger = LINEMessenger(token, user_id)

stream.start()

while True:
    frame = stream.read_frame()
    if frame is None:
        continue
    
    # Check for motion
    motion, boxes = motion_detector.detect(frame)
    if motion:
        messenger.send_alert("motion", frame=frame)
    
    # Check for fall
    fall, state, bbox = fall_detector.detect(frame)
    if fall:
        messenger.send_alert("fall", frame=frame, metadata={
            "state": state.value
        })
```

### Custom Message Formatting

```python
messenger = LINEMessenger(token, user_id)

# Send custom text
messenger.send_text("System started successfully")

# Send alert with detailed metadata
messenger.send_alert("fall", metadata={
    "velocity": 0.75,
    "confidence": 0.92,
    "location": "Living Room"
})
```

## Configuration Parameters

### Required Parameters

- `channel_access_token` (str): LINE channel access token
- `user_id` (str): Target LINE user ID

### Optional Parameters

- `send_snapshots` (bool): Attach image snapshots (default: True)
- `snapshot_quality` (int): JPEG quality 0-100 (default: 85)
- `max_retries` (int): Maximum retry attempts (default: 3)
- `retry_delay` (float): Delay between retries in seconds (default: 2.0)

## Message Format

Alert messages are automatically formatted:

```
[ALERT] MOTION
Time: 2025-11-25 14:30:45
Area: 1500
Confidence: 0.85
```

Fall alerts:

```
[ALERT] FALL
Time: 2025-11-25 14:31:20
Velocity: 0.75
State: fallen
```

## Error Handling

The messenger includes automatic retry logic:

1. First attempt fails → Wait 2 seconds
2. Second attempt fails → Wait 2 seconds
3. Third attempt fails → Return False

Errors are logged and counted in statistics.

## Statistics

Track messenger performance:

```python
stats = messenger.get_stats()
print(f"Messages sent: {stats['message_count']}")
print(f"Errors: {stats['error_count']}")
print(f"Last message: {stats['last_message_time']}")
```

Reset statistics:

```python
messenger.reset()
```

## Rate Limiting

To prevent notification spam, implement rate limiting:

```python
import time

last_alert_time = 0
min_interval = 30  # seconds

def send_rate_limited_alert(messenger, event_type, frame=None):
    global last_alert_time
    current_time = time.time()
    
    if current_time - last_alert_time >= min_interval:
        messenger.send_alert(event_type, frame=frame)
        last_alert_time = current_time
```

## Troubleshooting

### Issue: "Invalid channel access token"

**Solution**: Verify token is correct and not expired. Regenerate if needed.

### Issue: "User not found"

**Solution**: Ensure user has added bot as friend. Check user ID is correct.

### Issue: "Failed to send message"

**Solution**: Check internet connection. Verify LINE API status. Check retry settings.

### Issue: "Image not attached"

**Solution**: Image upload requires external hosting service. Implement `_upload_image()` method.

## Image Hosting

For production use, implement image hosting:

### Option 1: Imgur

```python
def _upload_image(self, image_bytes):
    response = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {imgur_client_id}"},
        files={"image": image_bytes}
    )
    return response.json()["data"]["link"]
```

### Option 2: AWS S3

```python
def _upload_image(self, image_bytes):
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"snapshots/{timestamp}.jpg",
        Body=image_bytes
    )
    return f"https://{bucket_name}.s3.amazonaws.com/snapshots/{timestamp}.jpg"
```

### Option 3: Self-Hosted

Run a simple HTTP server on Raspberry Pi with public URL (ngrok, etc.)

## Performance

- Text message: ~200-500ms delivery time
- Image message: ~1-2s delivery time (depends on upload)
- Memory usage: ~10MB
- CPU usage: <5% on Raspberry Pi 4

## Limitations

- LINE API rate limit: 500 messages/hour
- Image size limit: 10MB
- Supported image formats: JPEG, PNG
- Requires internet connection
- User must add bot as friend

## Security

- Store tokens in environment variables
- Never commit tokens to git
- Use HTTPS for image hosting
- Validate user IDs before sending
- Implement rate limiting

## Next Steps

After M4 completion, M5 will add:
- Webhook server for receiving commands
- Two-way communication (stop/resume)
- Command parsing and validation

## References

- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [line-bot-sdk-python](https://github.com/line/line-bot-sdk-python)
- [LINE Developers Console](https://developers.line.biz/console/)

