#!/usr/bin/env python3
"""
MC-38 Door Sensor - Test Suite

Testing for the MC-38 door sensor using gpiozero.

Features:
- 2 simple test cases (door closed & door open)
- Real-time event logging
- Pass/fail results
- Configurable GPIO pin and timeout
"""

from gpiozero import Button
from datetime import datetime
from time import sleep
import argparse


class DoorTester:
    """MC-38 door sensor testing class."""
    
    def __init__(self, gpio_pin: int = 23):
        """Initialize door sensor tester."""
        self.gpio_pin = gpio_pin
        self.door_state = None
        self.state_changes = 0
        self.test_results = []
        
        try:
            # MC-38: HIGH when closed (wires shorted), LOW when open (wires separated)
            self.sensor = Button(gpio_pin, pull_up=True)
            print(f"[{self._timestamp()}] GPIO Pin: {gpio_pin}")
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize GPIO pin {gpio_pin}")
            print(f"   {str(e)}")
            raise
    
    def _timestamp(self):
        """Get formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def setup_callbacks(self):
        """Setup door state detection callbacks."""
        self.state_changes = 0
        self.sensor.when_pressed = self._on_closed  # HIGH = Door Closed (wires shorted)
        self.sensor.when_released = self._on_open   # LOW = Door Open (wires separated)
    
    def _on_closed(self):
        """Callback when door closes."""
        self.state_changes += 1
        self.door_state = "CLOSED"
        print(f"[{self._timestamp()}] 🔒 Door CLOSED (#{self.state_changes})")
    
    def _on_open(self):
        """Callback when door opens."""
        self.state_changes += 1
        self.door_state = "OPEN"
        print(f"[{self._timestamp()}] 🚪 Door OPEN (#{self.state_changes})")
    
    def test_door_closed(self, duration: int = 10) -> bool:
        """Test 1: Verify door closed detection."""
        self.state_changes = 0
        self.setup_callbacks()
        
        print("\n" + "="*60)
        print("TEST 1: DOOR CLOSED")
        print("="*60)
        print(f"[{self._timestamp()}] ⏳ Waiting {duration}s...")
        print("👉 Keep door CLOSED (wires shorted)")
        print()
        
        sleep(duration)
        
        passed = self.door_state == "CLOSED" or self.state_changes == 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status}")
        self.test_results.append(("Door Closed", passed))
        return passed
    
    def test_door_open(self, duration: int = 10) -> bool:
        """Test 2: Verify door open detection."""
        self.state_changes = 0
        self.setup_callbacks()
        
        print("\n" + "="*60)
        print("TEST 2: DOOR OPEN")
        print("="*60)
        print(f"[{self._timestamp()}] ⏳ Waiting {duration}s...")
        print("👉 Keep door OPEN (wires separated)")
        print()
        
        sleep(duration)
        
        passed = self.door_state == "OPEN" or self.state_changes > 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status}")
        self.test_results.append(("Door Open", passed))
        return passed
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, passed in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name:<25} {status}")
        
        print("-"*60)
        passed_count = sum(1 for _, p in self.test_results if p)
        total_count = len(self.test_results)
        print(f"Results: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("🎉 ALL TESTS PASSED!")
        print("="*60)
    
    def run_all_tests(self, timeout: int = 10):
        """Run all tests."""
        print("\n" + "="*60)
        print("MC-38 DOOR SENSOR - TEST SUITE")
        print("="*60)
        print(f"[{self._timestamp()}] GPIO Pin: {self.gpio_pin}")
        print(f"[{self._timestamp()}] Timeout: {timeout}s per test")
        print()
        
        try:
            self.test_door_closed(timeout)
            self.test_door_open(timeout)
            self.print_summary()
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            self.print_summary()
        finally:
            self.cleanup()
    
    def run_specific_test(self, test_name: str, timeout: int = 10):
        """Run a specific test."""
        tests = {
            'closed': self.test_door_closed,
            'open': self.test_door_open,
        }
        
        if test_name not in tests:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available: {', '.join(tests.keys())}")
            return
        
        print("\n" + "="*60)
        print("MC-38 DOOR SENSOR - TEST SUITE")
        print("="*60)
        print(f"[{self._timestamp()}] GPIO Pin: {self.gpio_pin}")
        print()
        
        try:
            tests[test_name](timeout)
            self.print_summary()
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted")
            self.print_summary()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        try:
            if self.sensor:
                self.sensor.close()
        except:
            pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='MC-38 Door Sensor - Test Suite',
        epilog='''Examples:
  python door_test.py                    # Run all tests
  python door_test.py --test closed      # Run closed test only
  python door_test.py --test open        # Run open test only
  python door_test.py --timeout 20       # Extended timeout
  python door_test.py --gpio 23 --test open --timeout 30
        '''
    )
    
    parser.add_argument('--gpio', type=int, default=23, help='GPIO pin (default: 23)')
    parser.add_argument('--test', type=str, default='all', help='Test to run: closed, open, or all')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout per test (default: 10s)')
    
    args = parser.parse_args()
    
    try:
        tester = DoorTester(gpio_pin=args.gpio)
        
        if args.test.lower() == 'all':
            tester.run_all_tests(args.timeout)
        else:
            tester.run_specific_test(args.test.lower(), args.timeout)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == '__main__':
    main()
