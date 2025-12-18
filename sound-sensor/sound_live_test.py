#!/usr/bin/env python3
"""
LM393 Sound Sensor - Live Continuous Monitoring
GPIO22 - Real-time sound detection with visual feedback
"""

import RPi.GPIO as GPIO
import time
from datetime import datetime

# Configuration
SOUND_PIN = 22
TEST_DURATION = 30  # 30 seconds

def timestamp():
    """Get formatted timestamp."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def main():
    print("=" * 60)
    print("  LM393 SOUND SENSOR - LIVE MONITORING")
    print("  GPIO22 (Pin 15)")
    print(f"  Duration: {TEST_DURATION} seconds")
    print("=" * 60)
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(SOUND_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print(f"\n[{timestamp()}] GPIO initialized successfully")
        print(f"[{timestamp()}] Monitoring sound on GPIO22...")
        print("\n👉 Make some noise: clap, snap, speak, whistle!\n")
        
        last_state = None
        sound_count = 0
        silence_count = 0
        start_time = time.time()
        
        while (time.time() - start_time) < TEST_DURATION:
            current_state = GPIO.input(SOUND_PIN)
            elapsed = time.time() - start_time
            
            # Detect state changes
            if current_state != last_state and last_state is not None:
                if current_state == GPIO.HIGH:
                    sound_count += 1
                    print(f"[{timestamp()}] 🔊 SOUND DETECTED! (#{sound_count})")
                else:
                    silence_count += 1
                    print(f"[{timestamp()}] ✓ Silence (#{silence_count})")
            
            last_state = current_state
            time.sleep(0.01)  # 10ms polling
        
        # Summary
        print("\n" + "=" * 60)
        print("  TEST COMPLETE")
        print("=" * 60)
        print(f"  Sound events:    {sound_count}")
        print(f"  Silence events:  {silence_count}")
        print(f"  Total events:    {sound_count + silence_count}")
        
        if sound_count > 0:
            print("\n  ✅ SENSOR IS WORKING!")
        else:
            print("\n  ⚠️  NO SOUNDS DETECTED")
            print("  Check:")
            print("  - Sensor wiring (VCC, GND, OUT)")
            print("  - Sensitivity potentiometer adjustment")
            print("  - Make louder sounds")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    finally:
        GPIO.cleanup()
        print(f"\n[{timestamp()}] GPIO cleanup done")

if __name__ == "__main__":
    main()

