#!/usr/bin/env python3
"""
LM393 Sound Sensor - Simple Test Suite

Basic testing for the LM393 sound sensor using gpiozero.

Features:
- 2 simple test cases (silent & non-silent)
- Real-time event logging
- Pass/fail results
- Configurable GPIO pin and timeout
"""

from gpiozero import Button
from datetime import datetime
from time import sleep
import argparse


class SoundTester:
    """LM393 sound sensor testing class."""
    
    def __init__(self, gpio_pin: int = 22):
        """Initialize sound sensor tester."""
        self.gpio_pin = gpio_pin
        self.sound_count = 0
        self.test_results = []
        
        try:
            self.sensor = Button(gpio_pin, pull_up=True, bounce_time=0.1)
            print(f"[{self._timestamp()}] GPIO Pin: {gpio_pin}")
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize GPIO pin {gpio_pin}")
            print(f"   {str(e)}")
            raise
    
    def _timestamp(self):
        """Get formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def setup_callbacks(self):
        """Setup sound detection callbacks."""
        self.sound_count = 0
        self.sensor.when_pressed = self._on_sound
    
    def _on_sound(self):
        """Callback when sound detected."""
        self.sound_count += 1
        print(f"[{self._timestamp()}] 🔊 Sound detected (#{self.sound_count})")
    
    def test_silent(self, duration: int = 10) -> bool:
        """Test 1: Verify no sound (silent)."""
        self.sound_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*60)
        print("TEST 1: SILENT (No Sound)")
        print("="*60)
        print(f"[{self._timestamp()}] ⏳ Waiting {duration}s... keep quiet")
        print()
        
        sleep(duration)
        
        passed = self.sound_count == 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status}")
        self.test_results.append(("Silent", passed))
        return passed
    
    def test_non_silent(self, duration: int = 10) -> bool:
        """Test 2: Verify sound detection (non-silent)."""
        self.sound_count = 0
        self.setup_callbacks()
        
        print("\n" + "="*60)
        print("TEST 2: NON-SILENT (With Sound)")
        print("="*60)
        print(f"[{self._timestamp()}] ⏳ Waiting {duration}s for sound...")
        print("👉 Clap, snap, or speak!")
        print()
        
        sleep(duration)
        
        passed = self.sound_count > 0
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{self._timestamp()}] {status} - {self.sound_count} sounds detected")
        self.test_results.append(("Non-Silent", passed))
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
        print("LM393 SOUND SENSOR - TEST SUITE")
        print("="*60)
        print(f"[{self._timestamp()}] GPIO Pin: {self.gpio_pin}")
        print(f"[{self._timestamp()}] Timeout: {timeout}s per test")
        print()
        
        try:
            self.test_silent(timeout)
            self.test_non_silent(timeout)
            self.print_summary()
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            self.print_summary()
        finally:
            self.cleanup()
    
    def run_specific_test(self, test_name: str, timeout: int = 10):
        """Run a specific test."""
        tests = {
            'silent': self.test_silent,
            'non-silent': self.test_non_silent,
        }
        
        if test_name not in tests:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available: {', '.join(tests.keys())}")
            return
        
        print("\n" + "="*60)
        print("LM393 SOUND SENSOR - TEST SUITE")
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
        description='LM393 Sound Sensor - Test Suite',
        epilog='''Examples:
  python sound_test.py                      # Run all tests
  python sound_test.py --test silent        # Run silent test only
  python sound_test.py --test non-silent    # Run non-silent test only
  python sound_test.py --timeout 20         # Extended timeout
  python sound_test.py --gpio 22 --test silent --timeout 30
        '''
    )
    
    parser.add_argument('--gpio', type=int, default=22, help='GPIO pin (default: 22)')
    parser.add_argument('--test', type=str, default='all', help='Test to run: silent, non-silent, or all')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout per test (default: 10s)')
    
    args = parser.parse_args()
    
    try:
        tester = SoundTester(gpio_pin=args.gpio)
        
        if args.test.lower() == 'all':
            tester.run_all_tests(args.timeout)
        else:
            tester.run_specific_test(args.test.lower(), args.timeout)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == '__main__':
    main()
