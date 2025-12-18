#!/usr/bin/env python3
"""
Door Sensor Test - 10 Second Live Test
GPIO23 (Pin 16) - MC-38 Reed Switch (Normally Closed)

Author: A.R. Ansari
"""

import RPi.GPIO as GPIO
import time

# Configuration
DOOR_PIN = 23
TEST_DURATION = 10
DEBOUNCE_MS = 200

def main():
    print("=" * 50)
    print("  MC-38 DOOR SENSOR TEST")
    print("  GPIO23 (Pin 16)")
    print("  Duration: 10 seconds")
    print("=" * 50)
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print("\nGPIO initialized successfully")
        print("Monitoring door state...\n")
        
        last_state = None
        last_change_time = 0
        start_time = time.time()
        event_count = 0
        
        while (time.time() - start_time) < TEST_DURATION:
            current_state = GPIO.input(DOOR_PIN)
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Debounce check
            if current_state != last_state:
                if (current_time - last_change_time) > (DEBOUNCE_MS / 1000):
                    last_state = current_state
                    last_change_time = current_time
                    event_count += 1
                    
                    # MC-38 NC: LOW = magnet near = CLOSED, HIGH = magnet away = OPEN
                    if current_state == GPIO.LOW:
                        status = "CLOSED"
                        indicator = "[ CLOSED ]"
                    else:
                        status = "OPEN"
                        indicator = "[  OPEN  ]"
                    
                    print(f"[{elapsed:5.1f}s] {indicator} Door {status}")
            
            time.sleep(0.05)
        
        print("\n" + "=" * 50)
        print(f"  TEST COMPLETE")
        print(f"  Events detected: {event_count}")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    finally:
        GPIO.cleanup()
        print("GPIO cleanup done")

if __name__ == "__main__":
    main()
