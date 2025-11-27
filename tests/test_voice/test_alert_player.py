"""
Unit tests for VoiceAlertPlayer.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile

from src.voice.alert_player import VoiceAlertPlayer


class TestVoiceAlertPlayer(unittest.TestCase):
    """Test cases for VoiceAlertPlayer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'audio_file': 'test_audio.wav',
            'volume': 0.8,
            'trigger_on_fall': True,
            'trigger_on_motion': False
        }

    @patch('src.voice.alert_player.pygame')
    def test_initialization(self, mock_pygame):
        """Test VoiceAlertPlayer initialization"""
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)

        self.assertEqual(player.audio_file, 'test_audio.wav')
        self.assertEqual(player.volume, 0.8)
        self.assertTrue(player.trigger_on_fall)
        self.assertFalse(player.trigger_on_motion)
        mock_pygame.mixer.init.assert_called_once()

    @patch('src.voice.alert_player.pygame')
    def test_initialization_default_values(self, mock_pygame):
        """Test initialization with default values"""
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer({})

        self.assertEqual(player.audio_file, 'assets/are_you_ok.wav')
        self.assertEqual(player.volume, 0.8)
        self.assertTrue(player.trigger_on_fall)
        self.assertFalse(player.trigger_on_motion)

    def test_initialization_invalid_volume(self):
        """Test initialization with invalid volume"""
        config = {'volume': 1.5}

        with self.assertRaises(ValueError) as context:
            VoiceAlertPlayer(config)

        self.assertIn("Volume must be between 0.0 and 1.0", str(context.exception))

    def test_initialization_negative_volume(self):
        """Test initialization with negative volume"""
        config = {'volume': -0.5}

        with self.assertRaises(ValueError):
            VoiceAlertPlayer(config)

    def test_initialization_invalid_volume_type(self):
        """Test initialization with invalid volume type"""
        config = {'volume': 'loud'}

        with self.assertRaises(ValueError) as context:
            VoiceAlertPlayer(config)

        self.assertIn("Volume must be a number", str(context.exception))

    def test_initialization_invalid_audio_file_type(self):
        """Test initialization with invalid audio file type"""
        config = {'audio_file': 123}

        with self.assertRaises(ValueError) as context:
            VoiceAlertPlayer(config)

        self.assertIn("Audio file must be a string path", str(context.exception))

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_play_alert_fall(self, mock_exists, mock_pygame):
        """Test playing fall alert"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        result = player.play_alert('fall')

        self.assertTrue(result)
        mock_sound.play.assert_called_once()
        self.assertEqual(player._play_count, 1)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_play_alert_motion_disabled(self, mock_exists, mock_pygame):
        """Test motion alert when disabled"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        result = player.play_alert('motion')

        self.assertFalse(result)
        mock_sound.play.assert_not_called()

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_play_alert_motion_enabled(self, mock_exists, mock_pygame):
        """Test motion alert when enabled"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        config = self.config.copy()
        config['trigger_on_motion'] = True

        player = VoiceAlertPlayer(config)
        result = player.play_alert('motion')

        self.assertTrue(result)
        mock_sound.play.assert_called_once()

    @patch('src.voice.alert_player.pygame')
    def test_play_alert_not_initialized(self, mock_pygame):
        """Test playing alert when not initialized"""
        mock_pygame.mixer.init.side_effect = Exception("Init failed")

        player = VoiceAlertPlayer(self.config)
        result = player.play_alert('fall')

        self.assertFalse(result)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_set_volume(self, mock_exists, mock_pygame):
        """Test setting volume"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        player.set_volume(0.5)

        self.assertEqual(player.volume, 0.5)
        mock_sound.set_volume.assert_called_with(0.5)

    @patch('src.voice.alert_player.pygame')
    def test_set_volume_invalid(self, mock_pygame):
        """Test setting invalid volume"""
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)

        with self.assertRaises(ValueError):
            player.set_volume(1.5)

        with self.assertRaises(ValueError):
            player.set_volume(-0.1)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_get_volume(self, mock_exists, mock_pygame):
        """Test getting volume"""
        mock_exists.return_value = True
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)

        self.assertEqual(player.get_volume(), 0.8)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_get_stats(self, mock_exists, mock_pygame):
        """Test getting statistics"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        player.play_alert('fall')

        stats = player.get_stats()

        self.assertEqual(stats['play_count'], 1)
        self.assertIsNotNone(stats['last_play_time'])
        self.assertTrue(stats['initialized'])
        self.assertEqual(stats['audio_file'], 'test_audio.wav')
        self.assertEqual(stats['volume'], 0.8)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_is_playing(self, mock_exists, mock_pygame):
        """Test checking if audio is playing"""
        mock_exists.return_value = True
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.get_busy.return_value = True

        player = VoiceAlertPlayer(self.config)
        result = player.is_playing()

        self.assertTrue(result)
        mock_pygame.mixer.get_busy.assert_called_once()

    @patch('src.voice.alert_player.pygame')
    def test_is_playing_not_initialized(self, mock_pygame):
        """Test is_playing when not initialized"""
        mock_pygame.mixer.init.side_effect = Exception("Init failed")

        player = VoiceAlertPlayer(self.config)
        result = player.is_playing()

        self.assertFalse(result)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_stop(self, mock_exists, mock_pygame):
        """Test stopping audio playback"""
        mock_exists.return_value = True
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        player.stop()

        mock_pygame.mixer.stop.assert_called_once()

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_load_audio(self, mock_exists, mock_pygame):
        """Test loading new audio file"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        result = player.load_audio('new_audio.wav')

        self.assertTrue(result)
        self.assertEqual(player.audio_file, 'new_audio.wav')

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_load_audio_file_not_found(self, mock_exists, mock_pygame):
        """Test loading non-existent audio file"""
        mock_exists.side_effect = [True, False]
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        result = player.load_audio('missing.wav')

        self.assertFalse(result)

    @patch('src.voice.alert_player.pygame')
    def test_load_audio_not_initialized(self, mock_pygame):
        """Test loading audio when not initialized"""
        mock_pygame.mixer.init.side_effect = Exception("Init failed")

        player = VoiceAlertPlayer(self.config)
        result = player.load_audio('new_audio.wav')

        self.assertFalse(result)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_cleanup(self, mock_exists, mock_pygame):
        """Test cleanup of pygame resources"""
        mock_exists.return_value = True
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        player.cleanup()

        mock_pygame.mixer.quit.assert_called_once()
        self.assertFalse(player._initialized)

    @patch('src.voice.alert_player.pygame')
    @patch('src.voice.alert_player.os.path.exists')
    def test_play_alert_error_handling(self, mock_exists, mock_pygame):
        """Test error handling during playback"""
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_sound.play.side_effect = Exception("Playback error")
        mock_pygame.mixer.Sound.return_value = mock_sound
        mock_pygame.mixer.init.return_value = None

        player = VoiceAlertPlayer(self.config)
        result = player.play_alert('fall')

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

