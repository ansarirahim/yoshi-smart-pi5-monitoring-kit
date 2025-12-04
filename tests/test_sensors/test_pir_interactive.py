#!/usr/bin/env python3
"""
HC-SR501 PIR Motion Sensor Interactive Hardware Test.

Run this script directly on Raspberry Pi to test the PIR sensor.

Usage:
    python3 tests/test_sensors/test_pir_interactive.py

Wiring:
    [+] Orange wire -> Pin 1 (3.3V) !! NOT 5V !!
    [S] Brown wire  -> Pin 11 (GPIO17)
    [-] Black wire  -> Pin 6 (GND)

!! WARNING: Do NOT connect VCC to 5V!
   The PIR output voltage follows VCC. If VCC=5V, output=5V which will
   DAMAGE the Raspberry Pi GPIO pins (max 3.3V tolerant).
"""
import sys
import time
import os
from datetime import datetime

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.sensors.motion import MotionSensor


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_interactive_test(gpio_pin=17):
    """Run interactive PIR sensor test."""
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         HC-SR501 PIR MOTION SENSOR INTERACTIVE TEST            ║")
    print("║                    Raspberry Pi 5 (4GB)                        ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print("║  Wiring Check:                                                 ║")
    print("║    [+] Orange wire -> Pin 1 (3.3V) !! NOT 5V !!                    ║")
    print("║    [S] Brown wire  -> Pin 11 (GPIO17)                         ║")
    print("║    [-] Black wire  -> Pin 6 (GND)                             ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print("║  !! WARNING: VCC must be 3.3V! 5V will damage GPIO pins!       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    sensor = MotionSensor(gpio_pin=gpio_pin)
    print(f"[{ts()}] Initializing GPIO{gpio_pin}...")

    if not sensor.initialize():
        print(f"[{ts()}] ❌ FAILED - Cannot initialize GPIO!")
        return False

    print(f"[{ts()}] ✓ GPIO{gpio_pin} ready\n")

    # TEST 1: Idle State
    print("━" * 65)
    print("TEST 1: IDLE STATE CHECK")
    print("━" * 65)
    print("👉 Please stand still / don't move near the sensor...")
    
    idle_readings = [sensor.is_motion_detected() for _ in range(30) if not time.sleep(0.1)]
    idle_ratio = sum(idle_readings) / len(idle_readings) if idle_readings else 0
    test1_pass = idle_ratio < 0.3
    
    if test1_pass:
        print(f"[{ts()}] ✅ TEST 1 PASSED - Sensor is IDLE")
    else:
        print(f"[{ts()}] ⚠️  TEST 1 WARNING - Sensor showing motion during idle")
    print()

    # TEST 2: Motion Detection
    print("━" * 65)
    print("TEST 2: MOTION DETECTION")
    print("━" * 65)
    print("👉 Wave your hand in front of the sensor NOW!")
    
    motion_detected = False
    for remaining in range(100, 0, -1):
        print(f"\r   ⏳ Waiting... {remaining//10}s", end="", flush=True)
        if sensor.is_motion_detected():
            motion_detected = True
            print(f"\r[{ts()}] 🚨 MOTION DETECTED!                    ")
            break
        time.sleep(0.1)
    
    test2_pass = motion_detected
    if test2_pass:
        print(f"[{ts()}] ✅ TEST 2 PASSED - Motion detection working!")
    else:
        print(f"\r[{ts()}] ❌ TEST 2 FAILED - No motion detected")
    print()

    # TEST 3: Signal Recovery
    print("━" * 65)
    print("TEST 3: SIGNAL RECOVERY")
    print("━" * 65)
    print("👉 Stop moving and stay still...")
    
    signal_recovered = False
    for remaining in range(150, 0, -1):
        state = "HIGH 🔴" if sensor.is_motion_detected() else "LOW  🟢"
        print(f"\r   Signal: {state} | {remaining//10}s", end="", flush=True)
        if not sensor.is_motion_detected():
            signal_recovered = True
            print(f"\r[{ts()}] ✓ Signal returned to LOW                ")
            break
        time.sleep(0.1)
    
    test3_pass = signal_recovered
    if test3_pass:
        print(f"[{ts()}] ✅ TEST 3 PASSED - Signal recovery working!")
    else:
        print(f"\r[{ts()}] ⚠️  TEST 3 WARNING - Signal still HIGH (Tx delay high)")
    print()

    sensor.cleanup()

    # Final Result
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                      FINAL TEST RESULT                         ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    
    if test1_pass and test2_pass and test3_pass:
        print("║         ✅✅✅  ALL TESTS PASSED  ✅✅✅                       ║")
    elif test2_pass:
        print("║              ⚠️  PARTIAL PASS  ⚠️                              ║")
    else:
        print("║              ❌❌❌  TEST FAILED  ❌❌❌                        ║")
    
    print("╠════════════════════════════════════════════════════════════════╣")
    print(f"║  Test 1 (Idle State):     {'✅ PASS' if test1_pass else '⚠️  WARN'}                              ║")
    print(f"║  Test 2 (Motion Detect):  {'✅ PASS' if test2_pass else '❌ FAIL'}                              ║")
    print(f"║  Test 3 (Signal Recovery):{'✅ PASS' if test3_pass else '⚠️  WARN'}                              ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    return test2_pass


if __name__ == "__main__":
    gpio = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    success = run_interactive_test(gpio_pin=gpio)
    sys.exit(0 if success else 1)

