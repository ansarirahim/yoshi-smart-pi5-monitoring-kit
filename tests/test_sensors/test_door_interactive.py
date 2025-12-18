#!/usr/bin/env python3
"""
MC-38 Door Sensor Interactive Hardware Test.

Run this script directly on Raspberry Pi to test the magnetic door sensor.

Usage:
    sudo python3 tests/test_sensors/test_door_interactive.py

Wiring:
    Wire 1 (White) -> Pin 16 (GPIO23)
    Wire 2 (White) -> Pin 6 (GND)
    
    No polarity - wires are interchangeable.

Behavior (NC type with internal pull-up):
    - Magnet NEAR (door closed): GPIO reads LOW (0)
    - Magnet AWAY (door open):   GPIO reads HIGH (1)
"""
import sys
import time
import os
from datetime import datetime

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.sensors.door import DoorSensor, DoorState


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_interactive_test(gpio_pin=23):
    """Run interactive door sensor test."""
    print()
    print("+====================================================================+")
    print("|        MC-38 MAGNETIC DOOR SENSOR INTERACTIVE TEST                 |")
    print("|                    Raspberry Pi 5 (4GB)                            |")
    print("+====================================================================+")
    print("|  Wiring Check:                                                     |")
    print("|    Wire 1 (White) -> Pin 16 (GPIO23)                               |")
    print("|    Wire 2 (White) -> Pin 6 (GND)                                   |")
    print("|    No polarity - wires are interchangeable                         |")
    print("+====================================================================+")
    print("|  Type: Reed Switch (Normally Closed - NC)                          |")
    print("|  Magnet NEAR = CLOSED (LOW)  |  Magnet AWAY = OPEN (HIGH)          |")
    print("+====================================================================+")
    print()

    sensor = DoorSensor(gpio_pin=gpio_pin)
    print(f"[{ts()}] Initializing GPIO{gpio_pin}...")

    if not sensor.initialize():
        print(f"[{ts()}] FAILED - Cannot initialize GPIO!")
        return False

    print(f"[{ts()}] GPIO{gpio_pin} ready\n")

    # TEST 1: Initial State
    print("=" * 60)
    print("TEST 1: INITIAL STATE CHECK")
    print("=" * 60)
    
    state = sensor.read_state()
    if state == DoorState.CLOSED:
        print(f"[{ts()}] Door is CLOSED (magnet near switch)")
    else:
        print(f"[{ts()}] Door is OPEN (magnet away from switch)")
    print()

    # TEST 2: State Change Detection
    print("=" * 60)
    print("TEST 2: STATE CHANGE DETECTION")
    print("=" * 60)
    current = "close" if sensor.is_door_open() else "open"
    print(f"Please {current} the door/move magnet within 15 seconds...")
    print("Waiting for state change...")

    event = sensor.wait_for_change(timeout_sec=15.0)
    if event:
        print(f"[{ts()}] PASS - {event}")
    else:
        print(f"[{ts()}] TIMEOUT - No state change detected")
    print()

    # TEST 3: Continuous Monitoring
    print("=" * 60)
    print("TEST 3: CONTINUOUS MONITORING (30 seconds)")
    print("=" * 60)
    print("Open and close the door multiple times...")
    print("Monitoring door state...\n")

    event_count = 0
    start_time = time.time()
    last_state = sensor.read_state()
    
    # Show initial state
    status = "CLOSED" if last_state == DoorState.CLOSED else "OPEN"
    print(f"[{ts()}] Initial state: Door {status}")
    
    try:
        while (time.time() - start_time) < 30:
            current_state = sensor.read_state()
            elapsed = int(time.time() - start_time)
            
            if current_state != last_state:
                event_count += 1
                status = "OPENED" if current_state == DoorState.OPEN else "CLOSED"
                print(f"[{ts()}] Door {status}! (event #{event_count}, t={elapsed}s)")
                last_state = current_state
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total state changes detected: {event_count}")
    
    final_state = sensor.read_state()
    status = "CLOSED" if final_state == DoorState.CLOSED else "OPEN"
    print(f"Final door state: {status}")
    print()

    # Cleanup
    sensor.cleanup()
    print(f"[{ts()}] GPIO cleanup complete")
    print()
    
    # Print wiring diagram
    print(DoorSensor.get_wiring_diagram())
    
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

