#!/usr/bin/env python3
"""
LM393 Sound Sensor Interactive Hardware Test.

Run this script directly on Raspberry Pi to test the sound sensor.

Usage:
    sudo python3 tests/test_sensors/test_sound_interactive.py

Wiring (with polarity markings):
    [+] Orange wire -> Pin 1 (3.3V) - Power
    [-] Black wire  -> Pin 6 (GND) - Ground
    [S] White wire  -> Pin 15 (GPIO22) - Signal (D0)
    [A] A0          -> Not connected (RPi has no native ADC)

Behavior (ACTIVE LOW):
    - Quiet:          D0 = HIGH, LED OFF
    - Sound detected: D0 = LOW,  LED ON
"""
import sys
import time
import os
from datetime import datetime

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.sensors.sound import SoundSensor, SoundState


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_interactive_test(gpio_pin=22):
    """Run interactive sound sensor test."""
    print()
    print("+====================================================================+")
    print("|        LM393 SOUND SENSOR INTERACTIVE TEST                         |")
    print("|                    Raspberry Pi 5 (4GB)                            |")
    print("+====================================================================+")
    print("|  Wiring Check:                                                     |")
    print("|    [+] Orange wire -> Pin 1 (3.3V) - Power                         |")
    print("|    [-] Black wire  -> Pin 6 (GND) - Ground                         |")
    print("|    [S] White wire  -> Pin 15 (GPIO22) - Signal (D0)                |")
    print("+====================================================================+")
    print("|  Output: LOW when sound detected (ACTIVE LOW), LED turns ON        |")
    print("|  Sensitivity: Anti-clockwise = reduce, Clockwise = increase        |")
    print("|  Orientation: Keep microphone facing DOWN (bottom side up)         |")
    print("+====================================================================+")
    print()

    sensor = SoundSensor(gpio_pin=gpio_pin)
    print(f"[{ts()}] Initializing GPIO{gpio_pin}...")

    if not sensor.initialize():
        print(f"[{ts()}] FAILED - Cannot initialize GPIO!")
        return False

    print(f"[{ts()}] GPIO{gpio_pin} ready\n")

    # TEST 1: Idle State
    print("=" * 60)
    print("TEST 1: QUIET STATE CHECK")
    print("=" * 60)
    print("Keep quiet for a few seconds...")
    time.sleep(2)
    
    state = sensor.read_state()
    if state == SoundState.QUIET:
        print(f"[{ts()}] PASS - No sound detected (quiet state correct)")
        print("         LED should be OFF when quiet")
    else:
        print(f"[{ts()}] NOTE - Sound detected at idle!")
        print("         Reduce sensitivity (turn potentiometer counter-clockwise)")
    print()

    # TEST 2: Sound Detection
    print("=" * 60)
    print("TEST 2: SOUND DETECTION")
    print("=" * 60)
    print("Make a sound (clap, snap, speak loudly) within 10 seconds...")
    print("Waiting for sound...")

    event = sensor.wait_for_sound(timeout_sec=10.0)
    if event:
        print(f"[{ts()}] PASS - Sound detected!")
        print("         LED should have turned ON momentarily")
    else:
        print(f"[{ts()}] TIMEOUT - No sound detected")
        print("         Increase sensitivity (turn potentiometer clockwise)")
    print()

    # TEST 3: Continuous Monitoring
    print("=" * 60)
    print("TEST 3: CONTINUOUS MONITORING (30 seconds)")
    print("=" * 60)
    print("Make various sounds (clap, speak, whistle)...")
    print("Monitoring sounds...\n")

    event_count = 0
    start_time = time.time()
    last_state = SoundState.QUIET
    
    try:
        while (time.time() - start_time) < 30:
            current_state = sensor.read_state()
            elapsed = int(time.time() - start_time)
            
            # Detect falling edge (sound started)
            if current_state == SoundState.SOUND_DETECTED and last_state == SoundState.QUIET:
                event_count += 1
                print(f"[{ts()}] SOUND #{event_count} detected! (t={elapsed}s)")
            
            last_state = current_state
            time.sleep(0.005)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total sounds detected: {event_count}")
    print()

    # Cleanup
    sensor.cleanup()
    print(f"[{ts()}] GPIO cleanup complete")
    print()
    
    # Print wiring diagram
    print(SoundSensor.get_wiring_diagram())
    
    return True


if __name__ == "__main__":
    try:
        run_interactive_test()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

