"""
Voice Alert Player for audio notifications.

Handles audio playback for voice alerts and emergency notifications
using pygame mixer.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pygame


class VoiceAlertPlayer:
    """
    Voice alert player using pygame mixer.

    Plays audio alerts for fall detection and other events.
    Supports volume control and multiple audio files.

    Args:
        config: Voice configuration dictionary

    Example:
        config = {
            'audio_file': 'assets/are_you_ok.wav',
            'volume': 0.8,
            'trigger_on_fall': True
        }

        player = VoiceAlertPlayer(config)
        player.play_alert('fall')
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize voice alert player."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.audio_file = config.get('audio_file', 'assets/are_you_ok.wav')
        self.volume = config.get('volume', 0.8)
        self.trigger_on_fall = config.get('trigger_on_fall', True)
        self.trigger_on_motion = config.get('trigger_on_motion', False)

        self._validate_config()

        self._initialized = False
        self._sound = None
        self._play_count = 0
        self._last_play_time = None

        self._initialize_pygame()

    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        if not isinstance(self.volume, (int, float)):
            raise ValueError("Volume must be a number")

        if not 0.0 <= self.volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")

        if not isinstance(self.audio_file, str):
            raise ValueError("Audio file must be a string path")

    def _initialize_pygame(self) -> None:
        """Initialize pygame mixer."""
        try:
            pygame.mixer.init()
            self._initialized = True
            self.logger.info("Pygame mixer initialized")

            if os.path.exists(self.audio_file):
                self._sound = pygame.mixer.Sound(self.audio_file)
                self._sound.set_volume(self.volume)
                self.logger.info(f"Loaded audio file: {self.audio_file}")
            else:
                self.logger.warning(f"Audio file not found: {self.audio_file}")

        except Exception as e:
            self.logger.error(f"Failed to initialize pygame: {e}")
            self._initialized = False

    def play_alert(self, event_type: str = 'fall') -> bool:
        """
        Play voice alert for event.

        Args:
            event_type: Type of event ('fall', 'motion', etc.)

        Returns:
            True if alert played successfully, False otherwise
        """
        if not self._initialized or self._sound is None:
            self.logger.warning("Voice player not initialized or no audio loaded")
            return False

        if event_type == 'fall' and not self.trigger_on_fall:
            return False

        if event_type == 'motion' and not self.trigger_on_motion:
            return False

        try:
            self._sound.play()
            self._play_count += 1
            import time
            self._last_play_time = time.time()
            self.logger.info(f"Playing voice alert for {event_type}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to play alert: {e}")
            return False

    def set_volume(self, volume: float) -> None:
        """
        Set playback volume.

        Args:
            volume: Volume level (0.0 to 1.0)

        Raises:
            ValueError: If volume is out of range
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")

        self.volume = volume

        if self._sound:
            self._sound.set_volume(volume)
            self.logger.info(f"Volume set to {volume}")

    def get_volume(self) -> float:
        """
        Get current volume level.

        Returns:
            Current volume (0.0 to 1.0)
        """
        return self.volume

    def get_stats(self) -> Dict[str, Any]:
        """
        Get playback statistics.

        Returns:
            Dictionary with play count and last play time
        """
        return {
            'play_count': self._play_count,
            'last_play_time': self._last_play_time,
            'initialized': self._initialized,
            'audio_file': self.audio_file,
            'volume': self.volume
        }

    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.

        Returns:
            True if audio is playing, False otherwise
        """
        if not self._initialized:
            return False

        return pygame.mixer.get_busy()

    def stop(self) -> None:
        """Stop currently playing audio."""
        if self._initialized:
            pygame.mixer.stop()
            self.logger.info("Stopped audio playback")

    def load_audio(self, audio_file: str) -> bool:
        """
        Load a different audio file.

        Args:
            audio_file: Path to audio file

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self._initialized:
            self.logger.error("Pygame not initialized")
            return False

        if not os.path.exists(audio_file):
            self.logger.error(f"Audio file not found: {audio_file}")
            return False

        try:
            self._sound = pygame.mixer.Sound(audio_file)
            self._sound.set_volume(self.volume)
            self.audio_file = audio_file
            self.logger.info(f"Loaded new audio file: {audio_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load audio file: {e}")
            return False

    def cleanup(self) -> None:
        """Cleanup pygame resources."""
        if hasattr(self, '_initialized') and self._initialized:
            pygame.mixer.quit()
            self._initialized = False
            self.logger.info("Pygame mixer cleaned up")

    def __del__(self):
        """Destructor to cleanup resources."""
        self.cleanup()

