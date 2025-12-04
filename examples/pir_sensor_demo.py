#!/usr/bin/env python3
"""
PIR Motion Sensor Demo (HC-SR501).

Demonstrates motion detection using the HC-SR501 PIR sensor
connected to Raspberry Pi GPIO.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit

Wiring:
    HC-SR501 VCC  → Raspberry Pi Pin 2 (5V)
    HC-SR501 OUT  → Raspberry Pi Pin 11 (GPIO17)
    HC-SR501 GND  → Raspberry Pi Pin 6 (GND)
"""

import sys
import time
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, '..')

from src.sensors.motion import (
    MotionSensor,
    MotionEvent,
    MotionState,
    TriggerMode
)


def on_motion_detected(event: MotionEvent) -> None:
    """Callback function for motion events."""
    if event.state == MotionState.MOTION_DETECTED:
        print(f"\n🚨 MOTION DETECTED at {event.timestamp.strftime('%H:%M:%S')}")
    else:
        duration = f" (lasted {event.duration:.1f}s)" if event.duration else ""
        print(f"✓  Motion ended at {event.timestamp.strftime('%H:%M:%S')}{duration}")


def demo_polling_mode(sensor: MotionSensor, duration: int = 30) -> None:
    """Demonstrate polling-based motion detection."""
    print("\n" + "=" * 60)
    print("POLLING MODE DEMO")
    print("=" * 60)
    print(f"Monitoring for {duration} seconds...")
    print("Move in front of the sensor to test detection.\n")

    start_time = time.time()
    last_state = MotionState.NO_MOTION

    while (time.time() - start_time) < duration:
        current_state = sensor.read()

        if current_state != last_state:
            if current_state == MotionState.MOTION_DETECTED:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 Motion detected!")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓  No motion")
            last_state = current_state

        # Show status dot every second
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)

    print(f"\n\nPolling demo complete. Detected {len(sensor.get_event_history())} events.")


def demo_interrupt_mode(sensor: MotionSensor, duration: int = 30) -> None:
    """Demonstrate interrupt-driven motion detection."""
    print("\n" + "=" * 60)
    print("INTERRUPT MODE DEMO")
    print("=" * 60)
    print(f"Monitoring for {duration} seconds using GPIO interrupts...")
    print("Move in front of the sensor to test detection.\n")

    sensor.start_monitoring(use_interrupt=True)

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        pass

    sensor.stop_monitoring()

    events = sensor.get_event_history()
    print(f"\n\nInterrupt demo complete. Captured {len(events)} events.")

    if events:
        print("\nEvent History:")
        for event in events[-10:]:  # Show last 10 events
            print(f"  {event}")


def demo_wait_for_motion(sensor: MotionSensor) -> None:
    """Demonstrate blocking wait for motion."""
    print("\n" + "=" * 60)
    print("WAIT FOR MOTION DEMO")
    print("=" * 60)
    print("Waiting for motion (30 second timeout)...")
    print("Wave your hand in front of the sensor.\n")

    if sensor.wait_for_motion(timeout=30):
        print("✓ Motion was detected!")
    else:
        print("✗ Timeout - no motion detected")


def main():
    """Main demo entry point."""
    parser = argparse.ArgumentParser(
        description="HC-SR501 PIR Motion Sensor Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python pir_sensor_demo.py                    # Run all demos
    python pir_sensor_demo.py --gpio 27          # Use GPIO27 instead
    python pir_sensor_demo.py --mode polling     # Polling mode only
    python pir_sensor_demo.py --mode interrupt   # Interrupt mode only
    python pir_sensor_demo.py --wiring           # Show wiring diagram
        """
    )
    parser.add_argument("--gpio", type=int, default=17,
                       help="GPIO pin number (BCM) default: 17")
    parser.add_argument("--mode", choices=["polling", "interrupt", "wait", "all"],
                       default="all", help="Demo mode to run")
    parser.add_argument("--duration", type=int, default=30,
                       help="Duration for each demo in seconds")
    parser.add_argument("--wiring", action="store_true",
                       help="Show wiring diagram and exit")
    args = parser.parse_args()

    # Show wiring diagram if requested
    if args.wiring:
        print(MotionSensor.get_wiring_diagram())
        return

    print("=" * 60)
    print("   HC-SR501 PIR Motion Sensor Demo")
    print("   Raspberry Pi Smart Monitoring Kit")
    print("=" * 60)

    # Create sensor instance
    sensor = MotionSensor(
        gpio_pin=args.gpio,
        trigger_mode=TriggerMode.REPEATABLE,
        debounce_time_ms=200,
        callback=on_motion_detected
    )

    # Show wiring diagram
    print(sensor.get_wiring_diagram())

    # Initialize sensor
    print(f"\nInitializing sensor on GPIO{args.gpio}...")
    if not sensor.initialize():
        print("ERROR: Failed to initialize sensor!")
        print("Make sure you're running on Raspberry Pi with RPi.GPIO installed.")
        return

    print("✓ Sensor initialized successfully!")
    print("\n⏳ Sensor warmup period (10 seconds)...")
    print("   HC-SR501 requires 30-60s warmup for optimal performance.")
    time.sleep(10)
    print("✓ Ready for detection!\n")

    try:
        if args.mode in ["polling", "all"]:
            demo_polling_mode(sensor, args.duration)
            sensor.clear_history()

        if args.mode in ["interrupt", "all"]:
            demo_interrupt_mode(sensor, args.duration)
            sensor.clear_history()

        if args.mode in ["wait", "all"]:
            demo_wait_for_motion(sensor)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    finally:
        sensor.cleanup()
        print("\n✓ Cleanup complete. Goodbye!")


if __name__ == "__main__":
    main()

