# Voice Alert System

Voice alert system for the Raspberry Pi Smart Monitoring Kit. Plays audio notifications when events are detected.

**Author:** A.R. Ansari  
**Email:** ansarirahim1@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

## Overview

The voice alert system uses pygame to play audio files when specific events occur, such as fall detection or motion detection. It provides volume control, playback management, and configurable trigger settings.

## Features

- Audio playback using pygame mixer
- Volume control (0.0 to 1.0)
- Configurable event triggers
- Playback statistics tracking
- Support for multiple audio formats (WAV recommended)
- Thread-safe operation
- Error handling and logging

## Installation

The voice alert system requires pygame:

```bash
pip install pygame
```

This dependency is included in `requirements.txt`.

## Configuration

Configure voice alerts in `config/voice_config.yaml`:

```yaml
voice:
  enabled: true
  audio_file: "assets/are_you_ok.wav"
  volume: 0.8
  trigger_on_fall: true
  trigger_on_motion: false
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | true | Enable/disable voice alerts |
| `audio_file` | str | assets/are_you_ok.wav | Path to audio file |
| `volume` | float | 0.8 | Playback volume (0.0 to 1.0) |
| `trigger_on_fall` | bool | true | Play alert on fall detection |
| `trigger_on_motion` | bool | false | Play alert on motion detection |

## Usage

### Basic Usage

```python
from src.voice import VoiceAlertPlayer

config = {
    'audio_file': 'assets/are_you_ok.wav',
    'volume': 0.8,
    'trigger_on_fall': True
}

player = VoiceAlertPlayer(config)

# Play alert
player.play_alert('fall')

# Check if playing
if player.is_playing():
    print("Audio is playing")

# Stop playback
player.stop()

# Cleanup
player.cleanup()
```

### Volume Control

```python
# Set volume
player.set_volume(0.5)

# Get current volume
volume = player.get_volume()
print(f"Current volume: {volume}")
```

### Loading Different Audio Files

```python
# Load new audio file
success = player.load_audio('assets/motion_detected.wav')

if success:
    player.play_alert('motion')
```

### Getting Statistics

```python
stats = player.get_stats()

print(f"Play count: {stats['play_count']}")
print(f"Last play time: {stats['last_play_time']}")
print(f"Initialized: {stats['initialized']}")
```

## Audio File Requirements

### Recommended Format

- **Format:** WAV (PCM)
- **Sample Rate:** 44100 Hz or 22050 Hz
- **Channels:** Mono or Stereo
- **Bit Depth:** 16-bit
- **Duration:** 2-5 seconds

### Creating Audio Files

See `assets/README.md` for detailed instructions on creating or obtaining audio files.

**Quick method using gTTS:**

```bash
pip install gtts
python -c "from gtts import gTTS; tts = gTTS('Are you okay?', lang='en'); tts.save('assets/are_you_ok.mp3')"
ffmpeg -i assets/are_you_ok.mp3 -acodec pcm_s16le -ar 44100 assets/are_you_ok.wav
```

## Integration with Detection System

The voice alert system integrates with the fall detection system:

```python
from src.detection import FallDetector
from src.voice import VoiceAlertPlayer

# Initialize components
fall_detector = FallDetector(fall_config)
voice_player = VoiceAlertPlayer(voice_config)

# Define callback
def on_fall_detected(event):
    print("Fall detected!")
    voice_player.play_alert('fall')

# Register callback
fall_detector.register_callback(on_fall_detected)

# Start detection
fall_detector.start()
```

## Demo Script

Test the voice alert system using the demo script:

```bash
# Test audio playback
python examples/voice_demo.py test

# Play specific event alert
python examples/voice_demo.py play --event fall

# Test volume control
python examples/voice_demo.py volume --level 0.5

# Show statistics
python examples/voice_demo.py stats
```

## API Reference

### VoiceAlertPlayer

Main class for voice alert playback.

#### Methods

**`__init__(config: Dict[str, Any])`**
- Initialize voice alert player
- Args: Configuration dictionary
- Raises: ValueError for invalid configuration

**`play_alert(event_type: str = 'fall') -> bool`**
- Play voice alert for event
- Args: Event type ('fall', 'motion', etc.)
- Returns: True if played successfully

**`set_volume(volume: float) -> None`**
- Set playback volume
- Args: Volume level (0.0 to 1.0)
- Raises: ValueError if out of range

**`get_volume() -> float`**
- Get current volume level
- Returns: Volume (0.0 to 1.0)

**`is_playing() -> bool`**
- Check if audio is currently playing
- Returns: True if playing

**`stop() -> None`**
- Stop currently playing audio

**`load_audio(audio_file: str) -> bool`**
- Load a different audio file
- Args: Path to audio file
- Returns: True if loaded successfully

**`get_stats() -> Dict[str, Any]`**
- Get playback statistics
- Returns: Dictionary with stats

**`cleanup() -> None`**
- Cleanup pygame resources

## Troubleshooting

### Audio Not Playing

1. Check if audio file exists:
   ```bash
   ls -la assets/are_you_ok.wav
   ```

2. Verify pygame is installed:
   ```bash
   pip show pygame
   ```

3. Test audio device:
   ```bash
   # Linux
   aplay assets/are_you_ok.wav
   
   # Check volume
   alsamixer
   ```

4. Check logs for errors:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Audio Too Quiet/Loud

- Adjust volume in configuration file
- Or use `set_volume()` method
- Normalize audio file using Audacity

### Pygame Initialization Failed

- Check audio device is available
- Verify no other application is using audio
- Try reinitializing pygame

## Performance Considerations

- Audio playback uses minimal CPU
- pygame mixer runs in separate thread
- No blocking during playback
- Suitable for real-time monitoring

## Testing

Run unit tests:

```bash
pytest tests/test_voice/ -v
```

Run with coverage:

```bash
pytest tests/test_voice/ --cov=src/voice --cov-report=html
```

## License

Part of the Raspberry Pi Smart Monitoring Kit project.

