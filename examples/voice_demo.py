"""
Voice Alert Demo Script.

Demonstrates voice alert functionality for the monitoring system.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit

Usage:
    python examples/voice_demo.py test
    python examples/voice_demo.py play --event fall
    python examples/voice_demo.py volume --level 0.5
"""

import sys
import os
import argparse
import yaml
import logging
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.voice import VoiceAlertPlayer  # noqa: E402


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config(config_file: str = 'config/voice_config.yaml'):
    """Load voice configuration."""
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        print("Using default configuration")
        return {
            'audio_file': 'assets/are_you_ok.wav',
            'volume': 0.8,
            'trigger_on_fall': True,
            'trigger_on_motion': False
        }

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
        return config.get('voice', {})


def test_audio(player: VoiceAlertPlayer):
    """Test audio playback."""
    print("\n=== Testing Voice Alert System ===\n")

    print(f"Audio file: {player.audio_file}")
    print(f"Volume: {player.get_volume()}")
    print(f"Trigger on fall: {player.trigger_on_fall}")
    print(f"Trigger on motion: {player.trigger_on_motion}")

    if not os.path.exists(player.audio_file):
        print(f"\nWARNING: Audio file not found: {player.audio_file}")
        print("Please add an audio file to test playback.")
        print("See assets/README.md for instructions.")
        return

    print("\nPlaying test alert...")
    result = player.play_alert('fall')

    if result:
        print("Alert played successfully!")

        while player.is_playing():
            time.sleep(0.1)

        print("Playback complete.")
    else:
        print("Failed to play alert.")

    stats = player.get_stats()
    print(f"\nStatistics:")
    print(f"  Play count: {stats['play_count']}")
    print(f"  Initialized: {stats['initialized']}")


def play_alert(player: VoiceAlertPlayer, event_type: str):
    """Play alert for specific event."""
    print(f"\nPlaying {event_type} alert...")

    result = player.play_alert(event_type)

    if result:
        print(f"{event_type.capitalize()} alert triggered!")

        while player.is_playing():
            time.sleep(0.1)

        print("Playback complete.")
    else:
        print(f"Alert not triggered (check trigger settings for {event_type})")


def set_volume(player: VoiceAlertPlayer, level: float):
    """Set playback volume."""
    try:
        player.set_volume(level)
        print(f"Volume set to {level}")

        print("\nPlaying test alert at new volume...")
        player.play_alert('fall')

        while player.is_playing():
            time.sleep(0.1)

    except ValueError as e:
        print(f"Error: {e}")


def show_stats(player: VoiceAlertPlayer):
    """Display player statistics."""
    stats = player.get_stats()

    print("\n=== Voice Alert Statistics ===\n")
    print(f"Audio file: {stats['audio_file']}")
    print(f"Volume: {stats['volume']}")
    print(f"Initialized: {stats['initialized']}")
    print(f"Play count: {stats['play_count']}")

    if stats['last_play_time']:
        print(f"Last played: {time.ctime(stats['last_play_time'])}")
    else:
        print("Last played: Never")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description='Voice Alert Demo')
    parser.add_argument('command', choices=['test', 'play', 'volume', 'stats'],
                        help='Command to execute')
    parser.add_argument('--event', default='fall',
                        help='Event type (fall, motion)')
    parser.add_argument('--level', type=float, default=0.8,
                        help='Volume level (0.0 to 1.0)')
    parser.add_argument('--config', default='config/voice_config.yaml',
                        help='Configuration file path')

    args = parser.parse_args()

    setup_logging()

    config = load_config(args.config)
    player = VoiceAlertPlayer(config)

    if args.command == 'test':
        test_audio(player)
    elif args.command == 'play':
        play_alert(player, args.event)
    elif args.command == 'volume':
        set_volume(player, args.level)
    elif args.command == 'stats':
        show_stats(player)

    player.cleanup()


if __name__ == '__main__':
    main()

