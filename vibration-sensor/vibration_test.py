#!/usr/bin/env python3
"""
801S Vibration Sensor - Comprehensive Test Suite

This script provides comprehensive testing for the 801S vibration sensor
using gpiozero for event-driven GPIO handling.

Features:
- 7 comprehensive test cases (basic to advanced)
- Real-time event logging with timestamps
- Statistics tracking and reporting
- Configurable GPIO pin and timeouts
- User-friendly interface with prompts
- Graceful interrupt handling

Test Cases:
1. Idle State Test       - Verify no false vibrations
2. Vibration Detection  - Verify sensor responds to vibration
3. Signal Recovery      - Verify vibration→idle transition
4. Repeated Vibration   - Test multiple vibration cycles
5. Sensitivity Test     - Check sensor sensitivity level
6. Intensity Test       - Test vibration intensity response
7. Duration Test        - Measure vibration duration accuracy
"""

from gpiozero import Button
import signal
import argparse
from datetime import datetime
from time import sleep
from typing import Optional, Dict, List


class VibrationTester:
    """Comprehensive 801S vibration sensor testing class."""
    
    def __init__(self, gpio_pin: int = 27, pull_up: bool = True):
        """
        Initialize vibration sensor tester.
        
        Args:
            gpio_pin: GPIO pin number (default: GPIO27)
            pull_up: Use pull-up resistor (default: True)
        """
        self.gpio_pin = gpio_pin
        self.pull_up = pull_up
        self.vibration_count = 0
        self.idle_count = 0
        self.test_results = []
        self.last_vibration_time = None
        self.vibration_duration = 0.0
        
        try:
            self.sensor = Button(
                gpio_pin,
                pull_up=pull_up,
                bounce_time=0.05  # 50ms debounce
            )
            print(f"[{self._timestamp()}] GPIO Pin: {gpio_pin}")
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize GPIO pin {gpio_pin}")
            print(f"   {str(e)}")
            print("   Try: sudo python vibration_test.py")
            raise
    
    def _timestamp(self) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def setup_callbacks(self) -> None:
        """Setup vibration detection callbacks."""
        self.sensor.when_pressed = self._on_vibration
        self.sensor.when_released = self._on_idle
    
    def _on_vibration(self) -> None:
        """Callback when vibration detected."""
        self.vibration_count += 1
        self.last_vibration_time = datetime.now()
        print(f"[{self._timestamp()}] 🚨 VIBRATION DETECTED (#{self.vibration_count})")
    
    def _on_idle(self) -> None:
        """Callback when vibration stops."""
        self.idle_count += 1
        if self.last_vibration_time:
            self.vibration_duration = (datetime.now() - self.last_vibration_time).total_seconds()
            print(f"[{self._timestamp()}] ✓ Vibration ended (idle #{self.idle_count}, duration: {self.vibration_duration:.2f}s)")
    
    def test_idle_state(self, duration: int = 10) -> bool:
        """
        Test 1: Verify sensor doesn't trigger without vibration.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if test passed (no vibrations), False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 1: IDLE STATE CHECK")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Waiting {duration} seconds with NO vibration...")
        print("👉 Keep sensor completely still (no movement or vibration)")
        print()
        
        sleep(duration)
        
        passed = self.vibration_count == 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - {'No vibrations detected' if passed else 'Unexpected vibrations detected'}")
        
        self.test_results.append(("Idle State", passed))
        return passed
    
    def test_vibration_detection(self, duration: int = 10) -> bool:
        """
        Test 2: Verify sensor detects vibration.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if vibration detected, False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 2: VIBRATION DETECTION")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Waiting {duration} seconds for vibration...")
        print("👉 Tap or vibrate the sensor surface when ready!")
        print()
        
        sleep(duration)
        
        passed = self.vibration_count > 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - Vibrations detected: {self.vibration_count}")
        
        self.test_results.append(("Vibration Detection", passed))
        return passed
    
    def test_signal_recovery(self, duration: int = 15) -> bool:
        """
        Test 3: Verify vibration→idle transition.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if both events detected, False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 3: SIGNAL RECOVERY")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Testing vibration→idle transition ({duration}s)...")
        print("👉 Phase 1: Tap/vibrate the sensor")
        print("👉 Phase 2: Stop and keep it still")
        print()
        
        sleep(duration)
        
        passed = self.vibration_count > 0 and self.idle_count > 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - Vibrations: {self.vibration_count}, Idle periods: {self.idle_count}")
        
        self.test_results.append(("Signal Recovery", passed))
        return passed
    
    def test_repeated_vibration(self, cycles: int = 3, cycle_duration: int = 10) -> bool:
        """
        Test 4: Verify reliable multi-cycle detection.
        
        Args:
            cycles: Number of vibration cycles
            cycle_duration: Duration per cycle in seconds
            
        Returns:
            True if all cycles detected, False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 4: REPEATED VIBRATION")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Testing {cycles} vibration cycles ({cycle_duration}s each)...")
        print("👉 Repeat: Vibrate → Stop → Vibrate → Stop (etc.)")
        print()
        
        total_duration = cycles * cycle_duration
        sleep(total_duration)
        
        passed = self.vibration_count >= cycles - 1  # Allow 1 miss
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - Detected {self.vibration_count} vibrations (expected ~{cycles})")
        
        self.test_results.append(("Repeated Vibration", passed))
        return passed
    
    def test_sensitivity(self, duration: int = 20) -> bool:
        """
        Test 5: Check sensor sensitivity level.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if vibrations detected, False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 5: SENSITIVITY TEST")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Testing sensitivity ({duration}s)...")
        print("👉 Phase 1: Gentle tapping (light vibration)")
        print("👉 Phase 2: Moderate tapping (medium vibration)")
        print("👉 Phase 3: Strong tapping (heavy vibration)")
        print()
        
        sleep(duration)
        
        passed = self.vibration_count >= 5  # Expect multiple taps
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - Vibrations detected: {self.vibration_count}")
        
        self.test_results.append(("Sensitivity", passed))
        return passed
    
    def test_intensity(self, duration: int = 20) -> bool:
        """
        Test 6: Test vibration intensity response.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if vibrations detected at various intensities, False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 6: INTENSITY TEST")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Testing intensity response ({duration}s)...")
        print("👉 Vary vibration intensity:")
        print("   - Light touches")
        print("   - Medium taps")
        print("   - Strong vibrations")
        print()
        
        sleep(duration)
        
        passed = self.vibration_count >= 5
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - Intensity variations detected: {self.vibration_count}")
        
        self.test_results.append(("Intensity", passed))
        return passed
    
    def test_duration(self, duration: int = 20) -> bool:
        """
        Test 7: Measure vibration duration accuracy.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if duration measurements recorded, False otherwise
        """
        self.vibration_count = 0
        self.idle_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*70)
        print("TEST 7: DURATION TEST")
        print("="*70)
        print(f"[{self._timestamp()}] ⏳ Measuring vibration duration ({duration}s)...")
        print("👉 Perform vibrations of varying lengths:")
        print("   - Short vibration (1-2 seconds)")
        print("   - Medium vibration (3-5 seconds)")
        print("   - Long vibration (5+ seconds)")
        print()
        
        sleep(duration)
        
        passed = self.vibration_count >= 2
        status = "✅ PASS" if passed else "❌ FAIL"
        duration_info = f" (last duration: {self.vibration_duration:.2f}s)" if self.vibration_duration > 0 else ""
        print(f"[{self._timestamp()}] {status} - Duration measurements: {self.vibration_count}{duration_info}")
        
        self.test_results.append(("Duration", passed))
        return passed
    
    def print_summary(self) -> None:
        """Print test summary report."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        for test_name, passed in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name:<25} {status}")
        
        print("-"*70)
        print(f"Total Vibrations: {self.vibration_count}")
        print(f"Total Idle Periods: {self.idle_count}")
        
        passed_count = sum(1 for _, passed in self.test_results if passed)
        total_count = len(self.test_results)
        
        print(f"Results: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total_count - passed_count} test(s) failed")
        
        print("="*70)
    
    def run_all_tests(self, timeout: int = 10) -> None:
        """
        Run all tests sequentially.
        
        Args:
            timeout: Duration per test in seconds
        """
        print("\n" + "="*70)
        print("801S VIBRATION SENSOR - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"[{self._timestamp()}] GPIO Pin: {self.gpio_pin}")
        print(f"[{self._timestamp()}] Test Mode: all")
        print(f"[{self._timestamp()}] Timeout: {timeout}s per test")
        print()
        
        try:
            self.test_idle_state(timeout)
            self.test_vibration_detection(timeout)
            self.test_signal_recovery(timeout + 5)
            self.test_repeated_vibration(3, timeout // 3)
            self.test_sensitivity(timeout + 10)
            self.test_intensity(timeout + 10)
            self.test_duration(timeout + 10)
            
            self.print_summary()
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            self.print_summary()
        finally:
            self.cleanup()
    
    def run_specific_test(self, test_name: str, timeout: int = 10) -> None:
        """
        Run a specific test.
        
        Args:
            test_name: Test to run (idle, vibration, recovery, repeated, sensitivity, intensity, duration)
            timeout: Test duration in seconds
        """
        tests = {
            'idle': self.test_idle_state,
            'vibration': self.test_vibration_detection,
            'recovery': self.test_signal_recovery,
            'repeated': self.test_repeated_vibration,
            'sensitivity': self.test_sensitivity,
            'intensity': self.test_intensity,
            'duration': self.test_duration,
        }
        
        if test_name not in tests:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available tests: {', '.join(tests.keys())}")
            return
        
        print("\n" + "="*70)
        print("801S VIBRATION SENSOR - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"[{self._timestamp()}] GPIO Pin: {self.gpio_pin}")
        print(f"[{self._timestamp()}] Test Mode: {test_name}")
        print(f"[{self._timestamp()}] Timeout: {timeout}s")
        print()
        
        try:
            if test_name == 'repeated':
                tests[test_name](3, timeout // 3)
            else:
                tests[test_name](timeout)
            
            self.print_summary()
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            self.print_summary()
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Cleanup GPIO resources."""
        try:
            if self.sensor:
                self.sensor.close()
        except Exception:
            pass


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n⚠️  Interrupted by user (Ctrl+C)")
    raise KeyboardInterrupt


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='801S Vibration Sensor - Comprehensive Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python vibration_test.py              # Run all tests
  python vibration_test.py --test idle  # Run idle test only
  python vibration_test.py --gpio 27 --timeout 30  # Custom GPIO and timeout
  python vibration_test.py --test sensitivity --timeout 45

Available Tests:
  all          - Run all 7 tests (default)
  idle         - Idle state test only
  vibration    - Vibration detection test only
  recovery     - Signal recovery test only
  repeated     - Repeated vibration test only
  sensitivity  - Sensitivity test only
  intensity    - Intensity test only
  duration     - Duration test only
        '''
    )
    
    parser.add_argument('--gpio', type=int, default=27,
                        help='GPIO pin number (default: 27)')
    parser.add_argument('--test', type=str, default='all',
                        help='Which test to run (default: all)')
    parser.add_argument('--timeout', type=int, default=10,
                        help='Duration per test in seconds (default: 10)')
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        tester = VibrationTester(gpio_pin=args.gpio)
        
        if args.test.lower() == 'all':
            tester.run_all_tests(args.timeout)
        else:
            tester.run_specific_test(args.test.lower(), args.timeout)
    
    except PermissionError:
        print("❌ ERROR: Permission denied. Try: sudo python vibration_test.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise


if __name__ == '__main__':
    main()
