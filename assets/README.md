# Audio Assets

This directory contains audio files for voice alerts.

## Required Files

### are_you_ok.wav
Voice alert file that plays when fall is detected.

**Specifications:**
- Format: WAV (PCM)
- Sample Rate: 44100 Hz or 22050 Hz
- Channels: Mono or Stereo
- Bit Depth: 16-bit
- Duration: 2-5 seconds recommended

## How to Add Audio Files

### Option 1: Text-to-Speech (TTS) Generation

Use online TTS services or command-line tools:

**Using gTTS (Google Text-to-Speech):**
```bash
pip install gtts
python -c "from gtts import gTTS; tts = gTTS('Are you okay?', lang='en'); tts.save('assets/are_you_ok.mp3')"

# Convert MP3 to WAV using ffmpeg
ffmpeg -i assets/are_you_ok.mp3 -acodec pcm_s16le -ar 44100 assets/are_you_ok.wav
```

**Using pyttsx3 (Offline TTS):**
```python
import pyttsx3

engine = pyttsx3.init()
engine.save_to_file('Are you okay?', 'assets/are_you_ok.wav')
engine.runAndWait()
```

### Option 2: Record Your Own Voice

1. Use Audacity or any audio recording software
2. Record "Are you okay?" message
3. Export as WAV file (44100 Hz, 16-bit, Mono)
4. Save to `assets/are_you_ok.wav`

### Option 3: Download Pre-made Audio

Download from free audio libraries:
- Freesound.org
- Zapsplat.com
- BBC Sound Effects

Ensure the audio is royalty-free for your use case.

## Testing Audio

Test the audio file:

```bash
python examples/voice_demo.py test
```

## File Naming Convention

- `are_you_ok.wav` - Default fall detection alert
- `motion_detected.wav` - Motion detection alert (optional)
- `system_ready.wav` - System startup notification (optional)

## Audio Quality Guidelines

- Keep file size small (< 500 KB)
- Use clear, loud voice
- Avoid background noise
- Test on actual Raspberry Pi speakers
- Adjust volume in config if needed

## Troubleshooting

**Audio not playing:**
- Check file exists: `ls -la assets/are_you_ok.wav`
- Verify format: `file assets/are_you_ok.wav`
- Test with: `aplay assets/are_you_ok.wav` (Linux)
- Check volume: `alsamixer` (Linux)

**Audio too quiet/loud:**
- Adjust volume in `config/voice_config.yaml`
- Or normalize audio file using Audacity

## License

Ensure any audio files you use comply with licensing requirements.
For commercial use, verify the audio is royalty-free or properly licensed.

