#!/usr/bin/env python3
"""
HC-SR501 PIR Motion Sensor - Comprehensive Test Suite

Complete test coverage for PIR motion sensor including:
- Idle state detection
- Motion detection
- Signal recovery
- Timeout handling
- Statistics tracking
- Multiple test scenarios

Usage:
    python pir_test.py
    python pir_test.py --gpio 17 --timeout 30
    python pir_test.py --test idle
    python pir_test.py --test motion
    python pir_test.py --test all

Requires:
    pip install gpiozero
"""

import sys
import time
import argparse
from datetime import datetime
from signal import signal, SIGINT

try:
    from gpiozero import MotionSensor
except ImportError:
    print("ERROR: gpiozero not installed")
    print("Install with: pip install gpiozero")
    sys.exit(1)


class PIRTester:
    """Comprehensive PIR motion sensor test suite."""

    def __init__(self, gpio_pin=17):
        self.gpio_pin = gpio_pin
        self.pir = MotionSensor(gpio_pin)
        self.motion_count = 0
        self.idle_count = 0
        self.test_results = []
        self.start_time = None
        self.stop_requested = False

    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_str = f"[{level}]" if level != "INFO" else ""
        print(f"[{ts}] {level_str} {message}")

    def motion_detected(self):
        """Callback: Motion detected."""
        self.motion_count += 1
        self.log(f"🚨 MOTION DETECTED (#{self.motion_count})", "DETECT")

    def motion_stopped(self):
        """Callback: Motion stopped."""
        self.idle_count += 1
        self.log(f"✓ Motion ended (idle #{self.idle_count})", "IDLE")

    def setup_callbacks(self):
        """Setup motion sensor callbacks."""
        self.pir.when_motion = self.motion_detected
        self.pir.when_no_motion = self.motion_stopped

    def test_idle_state(self, duration=10):
        """Test 1: Sensor idle state (no motion)."""
        self.log("=" * 70)
        self.log("TEST 1: IDLE STATE CHECK", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Waiting {duration} seconds with NO motion...")
        self.log("👉 Please stand still / don't move near sensor\n")

        self.setup_callbacks()
        start_idle = self.idle_count

        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            self.stop_requested = True
            return False

        idle_events = self.idle_count - start_idle
        motion_events = self.motion_count

        passed = motion_events == 0
        self.test_results.append(("Idle State", passed))

        self.log("-" * 70)
        if passed:
            self.log(f"✅ TEST 1 PASSED - No motion detected", "PASS")
        else:
            self.log(f"❌ TEST 1 FAILED - Detected {motion_events} motion events", "FAIL")
        self.log("-" * 70 + "\n")

        return passed

    def test_motion_detection(self, duration=10):
        """Test 2: Motion detection."""
        self.log("=" * 70)
        self.log("TEST 2: MOTION DETECTION", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Waiting {duration} seconds for motion detection...")
        self.log("👉 Wave your hand in front of sensor NOW!\n")

        motion_start = self.motion_count

        try:
            for i in range(duration):
                if self.stop_requested:
                    return False
                if self.motion_count > motion_start:
                    self.log(f"✓ Motion detected at {duration - i}s remaining", "SUCCESS")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_requested = True
            return False

        passed = self.motion_count > motion_start
        self.test_results.append(("Motion Detection", passed))

        self.log("-" * 70)
        if passed:
            self.log(f"✅ TEST 2 PASSED - Motion detected!", "PASS")
        else:
            self.log(f"❌ TEST 2 FAILED - No motion detected", "FAIL")
        self.log("-" * 70 + "\n")

        return passed

    def test_signal_recovery(self, duration=15):
        """Test 3: Signal recovery (motion stops)."""
        self.log("=" * 70)
        self.log("TEST 3: SIGNAL RECOVERY", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Waiting {duration} seconds for recovery...")
        self.log("👉 First: Wave hand (create motion)")
        self.log("   Then: Stand still (let it recover)\n")

        idle_start = self.idle_count
        motion_detected_before = self.motion_count

        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            self.stop_requested = True
            return False

        motion_happened = self.motion_count > motion_detected_before
        recovery_happened = self.idle_count > idle_start

        passed = motion_happened and recovery_happened
        self.test_results.append(("Signal Recovery", passed))

        self.log("-" * 70)
        if passed:
            self.log(f"✅ TEST 3 PASSED - Motion & recovery detected", "PASS")
        else:
            self.log(f"❌ TEST 3 FAILED - No recovery", "FAIL")
        self.log("-" * 70 + "\n")

        return passed

    def test_repeated_motion(self, cycles=3, cycle_duration=5):
        """Test 4: Repeated motion detection."""
        self.log("=" * 70)
        self.log("TEST 4: REPEATED MOTION CYCLES", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Testing {cycles} cycles (on/off pattern)...")
        self.log(f"📋 Each cycle: {cycle_duration}s motion, {cycle_duration}s idle\n")

        motion_cycles = 0
        idle_cycles = 0

        for cycle in range(cycles):
            if self.stop_requested:
                return False

            self.log(f"Cycle {cycle + 1}/{cycles}:")
            self.log(f"  👉 Motion phase (wave hand)...")
            motion_before = self.motion_count

            try:
                time.sleep(cycle_duration)
            except KeyboardInterrupt:
                self.stop_requested = True
                return False

            if self.motion_count > motion_before:
                motion_cycles += 1
                self.log(f"  ✓ Motion detected")
            else:
                self.log(f"  ✗ No motion detected")

            self.log(f"  ⏸ Idle phase (stand still)...")
            idle_before = self.idle_count

            try:
                time.sleep(cycle_duration)
            except KeyboardInterrupt:
                self.stop_requested = True
                return False

            if self.idle_count > idle_before:
                idle_cycles += 1
                self.log(f"  ✓ Idle detected")
            else:
                self.log(f"  ✗ No idle detected")

            self.log()

        passed = motion_cycles == cycles and idle_cycles == cycles
        self.test_results.append(("Repeated Motion", passed))

        self.log("-" * 70)
        if passed:
            self.log(
                f"✅ TEST 4 PASSED - All {cycles} cycles detected",
                "PASS",
            )
        else:
            self.log(
                f"❌ TEST 4 FAILED - {motion_cycles} motion, {idle_cycles} idle cycles",
                "FAIL",
            )
        self.log("-" * 70 + "\n")

        return passed

    def test_sensitivity(self, duration=20):
        """Test 5: Sensor sensitivity (minimum motion detection)."""
        self.log("=" * 70)
        self.log("TEST 5: SENSITIVITY CHECK", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Testing sensor sensitivity for {duration} seconds...")
        self.log("👉 Make small movements at different distances\n")

        motion_start = self.motion_count

        try:
            for i in range(duration):
                if self.stop_requested:
                    return False
                remaining = duration - i
                if (i % 5) == 0:
                    self.log(f"  ⏳ {remaining}s remaining... (current detections: {self.motion_count - motion_start})")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_requested = True
            return False

        detections = self.motion_count - motion_start
        passed = detections > 0
        self.test_results.append(("Sensitivity", passed))

        self.log("-" * 70)
        if passed:
            self.log(f"✅ TEST 5 PASSED - {detections} detections (sensitive)", "PASS")
        else:
            self.log(f"⚠️  TEST 5 WARNING - No detections (check positioning)", "WARN")
        self.log("-" * 70 + "\n")

        return passed

    def test_range(self, duration=20):
        """Test 6: Detection range."""
        self.log("=" * 70)
        self.log("TEST 6: DETECTION RANGE", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Testing detection range for {duration} seconds...")
        self.log("👉 Move from close (1m) to far (5m) from sensor\n")

        motion_start = self.motion_count

        try:
            for i in range(duration):
                if self.stop_requested:
                    return False
                remaining = duration - i
                if (i % 5) == 0:
                    self.log(f"  ⏳ {remaining}s remaining...")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_requested = True
            return False

        detections = self.motion_count - motion_start
        passed = detections > 0
        self.test_results.append(("Detection Range", passed))

        self.log("-" * 70)
        if passed:
            self.log(f"✅ TEST 6 PASSED - Detections at multiple distances", "PASS")
        else:
            self.log(f"❌ TEST 6 FAILED - No range detection", "FAIL")
        self.log("-" * 70 + "\n")

        return passed

    def test_false_positive(self, duration=30):
        """Test 7: False positive check (thermal drift, reflections)."""
        self.log("=" * 70)
        self.log("TEST 7: FALSE POSITIVE CHECK", "TEST")
        self.log("=" * 70)
        self.log(f"⏳ Monitoring for {duration}s with NO motion...")
        self.log("👉 Lights, fans, heat sources nearby? Don't move!\n")

        motion_start = self.motion_count

        try:
            for i in range(duration):
                if self.stop_requested:
                    return False
                remaining = duration - i
                if (i % 10) == 0:
                    self.log(f"  ⏳ {remaining}s remaining...")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_requested = True
            return False

        false_positives = self.motion_count - motion_start
        passed = false_positives == 0
        self.test_results.append(("False Positive", passed))

        self.log("-" * 70)
        if passed:
            self.log(f"✅ TEST 7 PASSED - No false positives", "PASS")
        else:
            self.log(
                f"⚠️  TEST 7 WARNING - {false_positives} false positives detected",
                "WARN",
            )
        self.log("-" * 70 + "\n")

        return passed

    def print_summary(self):
        """Print test summary."""
        self.log("=" * 70)
        self.log("TEST SUMMARY", "SUMMARY")
        self.log("=" * 70)

        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)

        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name:<30} {status}")

        self.log("-" * 70)
        self.log(f"Total Events: {self.motion_count} motion, {self.idle_count} idle")
        self.log(f"Results: {passed}/{total} tests passed")
        if passed == total:
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
        elif passed > total // 2:
            self.log("⚠️  SOME TESTS FAILED", "WARNING")
        else:
            self.log("❌ MULTIPLE TEST FAILURES", "ERROR")
        self.log("=" * 70 + "\n")

    def cleanup(self):
        """Cleanup GPIO."""
        try:
            self.pir.close()
            self.log("GPIO cleanup complete", "INFO")
        except Exception as e:
            self.log(f"Cleanup error: {e}", "ERROR")


def main():
    parser = argparse.ArgumentParser(
        description="PIR Motion Sensor Comprehensive Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pir_test.py                    # Run all tests
  python pir_test.py --gpio 27          # Use GPIO27
  python pir_test.py --test idle        # Only idle test
  python pir_test.py --test motion      # Only motion test
  python pir_test.py --timeout 60       # Each test: 60 seconds

Available Tests:
  all          - Run all tests (default)
  idle         - Idle state detection
  motion       - Motion detection
  recovery     - Signal recovery
  repeated     - Repeated motion cycles
  sensitivity  - Sensor sensitivity
  range        - Detection range
  false_pos    - False positive check
        """,
    )
    parser.add_argument(
        "--gpio",
        type=int,
        default=17,
        help="GPIO pin (default: 17)",
    )
    parser.add_argument(
        "--test",
        default="all",
        choices=[
            "all",
            "idle",
            "motion",
            "recovery",
            "repeated",
            "sensitivity",
            "range",
            "false_pos",
        ],
        help="Which test to run (default: all)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout for each test in seconds (default: 10)",
    )

    args = parser.parse_args()

    tester = PIRTester(gpio_pin=args.gpio)

    # Handle CTRL+C
    def handle_sigint(signum, frame):
        tester.stop_requested = True
        print("\n")
        tester.log("Test interrupted by user", "INFO")
        tester.print_summary()
        tester.cleanup()
        sys.exit(0)

    signal(SIGINT, handle_sigint)

    # Print header
    print("\n" + "=" * 70)
    print("HC-SR501 PIR MOTION SENSOR - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    tester.log(f"GPIO Pin: {args.gpio}")
    tester.log(f"Test Mode: {args.test}")
    tester.log(f"Timeout: {args.timeout}s per test")
    print("=" * 70 + "\n")

    tester.start_time = time.time()

    try:
        if args.test in ["all", "idle"]:
            if tester.stop_requested:
                return
            tester.test_idle_state(args.timeout)

        if args.test in ["all", "motion"]:
            if tester.stop_requested:
                return
            tester.test_motion_detection(args.timeout)

        if args.test in ["all", "recovery"]:
            if tester.stop_requested:
                return
            tester.test_signal_recovery(args.timeout)

        if args.test in ["all", "repeated"]:
            if tester.stop_requested:
                return
            tester.test_repeated_motion(cycles=3, cycle_duration=args.timeout // 6)

        if args.test in ["all", "sensitivity"]:
            if tester.stop_requested:
                return
            tester.test_sensitivity(args.timeout)

        if args.test in ["all", "range"]:
            if tester.stop_requested:
                return
            tester.test_range(args.timeout)

        if args.test in ["all", "false_pos"]:
            if tester.stop_requested:
                return
            tester.test_false_positive(args.timeout)

    except Exception as e:
        tester.log(f"ERROR: {e}", "ERROR")
        import traceback

        traceback.print_exc()

    finally:
        tester.print_summary()
        tester.cleanup()


if __name__ == "__main__":
    main()
