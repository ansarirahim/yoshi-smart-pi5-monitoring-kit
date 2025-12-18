#!/usr/bin/env python3
"""
801S Vibration Sensor - Simple Yes/No Test
GPIO27 - 10 second monitoring
"""

import RPi.GPIO as GPIO
import time

# Configuration
VIBRATION_PIN = 27
TIMEOUT = 10

def main():
    print("=" * 50)
    print("  VIBRATION SENSOR TEST")
    print("  GPIO27 (Pin 13)")
    print("  Duration: 10 seconds")
    print("=" * 50)
    
    vibration_detected = False
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print("\nMonitoring vibration...")
        print("👉 Tap or shake the sensor!\n")
        
        start_time = time.time()
        
        while (time.time() - start_time) < TIMEOUT:
            if GPIO.input(VIBRATION_PIN) == GPIO.LOW:
                vibration_detected = True
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] 📳 VIBRATION DETECTED!")
                time.sleep(0.2)  # Brief pause to avoid spam
            
            time.sleep(0.01)  # 10ms polling
        
        # Result
        print("\n" + "=" * 50)
        if vibration_detected:
            print("  ✅ YES - Vibration detected!")
        else:
            print("  ❌ NO - No vibration detected")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    finally:
        GPIO.cleanup()
        print("GPIO cleanup done\n")

if __name__ == "__main__":
    main()

