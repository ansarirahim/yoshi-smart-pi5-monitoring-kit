#!/usr/bin/env python3
"""
801S Vibration Shock Sensor Interactive Hardware Test.

Run this script directly on Raspberry Pi to test the vibration sensor.

Usage:
    python3 tests/test_sensors/test_vibration_interactive.py

Wiring (with polarity markings):
    [+] Orange wire -> Pin 1 (3.3V) - Power
    [S] Gray wire   -> Pin 13 (GPIO27) - Signal (Digital Output)
    [-] Black wire  -> Pin 6 (GND) - Ground

Note: GPIO17 is reserved for PIR Motion Sensor. Vibration uses GPIO27.

Behavior:
    - No vibration: Output LOW, LED ON
    - Vibration detected: Output HIGH, LED OFF
"""
import sys
import time
import os
from datetime import datetime

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.sensors.vibration import VibrationSensor, VibrationState


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_interactive_test(gpio_pin=27):
    """Run interactive vibration sensor test."""
    print()
    print("+====================================================================+")
    print("|      801S VIBRATION SHOCK SENSOR INTERACTIVE TEST                  |")
    print("|                    Raspberry Pi 5 (4GB)                            |")
    print("+====================================================================+")
    print("|  Wiring Check:                                                     |")
    print("|    [+] Orange wire -> Pin 1 (3.3V) - Power                         |")
    print("|    [S] Gray wire   -> Pin 13 (GPIO27) - Signal                     |")
    print("|    [-] Black wire  -> Pin 6 (GND) - Ground                         |")
    print("+====================================================================+")
    print("|  Output: HIGH when vibration detected (LED turns OFF)              |")
    print("|  Sensitivity: Adjust potentiometer to set threshold                |")
    print("+====================================================================+")
    print()

    sensor = VibrationSensor(gpio_pin=gpio_pin)
    print(f"[{ts()}] Initializing GPIO{gpio_pin}...")

    if not sensor.initialize():
        print(f"[{ts()}] FAILED - Cannot initialize GPIO!")
        return False

    print(f"[{ts()}] GPIO{gpio_pin} ready\n")

    # TEST 1: Idle State
    print("=" * 60)
    print("TEST 1: IDLE STATE CHECK")
    print("=" * 60)
    print("Keep the sensor completely still...")
    time.sleep(2)
    
    state = sensor.read_state()
    if state == VibrationState.NO_VIBRATION:
        print(f"[{ts()}] PASS - No vibration detected (idle state correct)")
        print("         LED should be ON when idle")
    else:
        print(f"[{ts()}] NOTE - Vibration detected at idle!")
        print("         Try adjusting sensitivity potentiometer")
    print()

    # TEST 2: Vibration Detection
    print("=" * 60)
    print("TEST 2: VIBRATION DETECTION")
    print("=" * 60)
    print("Tap the sensor or table within 10 seconds...")
    print("Waiting for vibration...")

    event = sensor.wait_for_vibration(timeout_sec=10.0)
    if event:
        print(f"[{ts()}] PASS - Vibration detected!")
        print("         LED should have turned OFF momentarily")
    else:
        print(f"[{ts()}] TIMEOUT - No vibration detected")
        print("         Try increasing sensitivity (turn potentiometer)")
    print()

    # TEST 3: Continuous Monitoring
    print("=" * 60)
    print("TEST 3: CONTINUOUS MONITORING (30 seconds)")
    print("=" * 60)
    print("Tap the sensor multiple times...")
    print("Monitoring vibrations...\n")

    event_count = 0
    start_time = time.time()
    last_state = VibrationState.NO_VIBRATION
    
    try:
        while (time.time() - start_time) < 30:
            current_state = sensor.read_state()
            elapsed = int(time.time() - start_time)
            
            # Detect rising edge
            if current_state == VibrationState.VIBRATION_DETECTED and last_state == VibrationState.NO_VIBRATION:
                event_count += 1
                print(f"[{ts()}] VIBRATION #{event_count} detected! (t={elapsed}s)")
            
            last_state = current_state
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total vibrations detected: {event_count}")
    print()

    # Cleanup
    sensor.cleanup()
    print(f"[{ts()}] GPIO cleanup complete")
    print()
    
    # Print wiring diagram
    print(VibrationSensor.get_wiring_diagram())
    
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

