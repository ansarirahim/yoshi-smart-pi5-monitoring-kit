#!/usr/bin/env python3
"""
Unified Sensor Monitoring System

Monitors all sensors simultaneously:
- Temperature (XY-MD02)
- Motion (HC-SR501 PIR)
- Vibration (801S)
- Sound (LM393)
- Door (MC-38)

Real-time event logging and activity tracking with dashboard.
"""

import threading
import minimalmodbus
import serial
import RPi.GPIO as GPIO
from gpiozero import Button, MotionSensor
from datetime import datetime
from time import sleep
import signal
import sys
import argparse
import os
from collections import defaultdict


class UnifiedMonitor:
    """Unified sensor monitoring system with dashboard."""
    
    def __init__(self, sensors=['temperature', 'motion', 'vibration', 'sound', 'door'], use_dashboard=True):
        """Initialize unified monitor."""
        self.sensors = sensors
        self.running = True
        self.event_count = {}
        self.sensor_status = {}
        self.lock = threading.Lock()
        self.use_dashboard = use_dashboard
        self.last_event = {}
        self.last_temp = None
        self.last_humidity = None
        
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        
        # Sensor objects
        self.motion_sensor = None
        self.vibration_sensor = None
        self.sound_sensor = None
        self.door_sensor = None
        self.modbus_sensor = None
        
        print("="*70)
        print("UNIFIED SENSOR MONITORING SYSTEM - DASHBOARD")
        print("="*70)
        print(f"[{self._timestamp()}] Initializing sensors...")
        print()
        
        # Initialize enabled sensors
        self._init_sensors()
        
    def _timestamp(self):
        """Get formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _init_sensors(self):
        """Initialize enabled sensors."""
        try:
            if 'motion' in self.sensors:
                try:
                    # Use Button instead of MotionSensor for non-blocking init
                    self.motion_sensor = Button(17, pull_up=True, bounce_time=0.05)
                    self.motion_sensor.when_pressed = self._on_motion
                    self.motion_sensor.when_released = self._on_no_motion
                    self.event_count['motion'] = 0
                    self.sensor_status['motion'] = 'No Motion'
                    self.last_event['motion'] = None
                    print(f"✓ Motion sensor (GPIO17) initialized")
                except Exception as e:
                    print(f"✗ Motion sensor failed: {str(e)}")
                    self.sensor_status['motion'] = '--'
        except Exception as e:
            print(f"✗ Motion sensor failed: {str(e)}")
        
        try:
            if 'vibration' in self.sensors:
                self.vibration_sensor = Button(27, pull_up=True, bounce_time=0.05)
                self.vibration_sensor.when_pressed = self._on_vibration
                self.event_count['vibration'] = 0
                self.sensor_status['vibration'] = 'Stable'
                self.last_event['vibration'] = None
                print(f"✓ Vibration sensor (GPIO27) initialized")
        except Exception as e:
            print(f"✗ Vibration sensor failed: {str(e)}")
            self.sensor_status['vibration'] = '--'
        
        try:
            if 'sound' in self.sensors:
                self.sound_sensor = Button(22, pull_up=True, bounce_time=0.05)
                self.sound_sensor.when_pressed = self._on_sound_detected
                self.sound_sensor.when_released = self._on_sound_stopped
                self.event_count['sound'] = 0
                self.sensor_status['sound'] = 'Silent'
                self.last_event['sound'] = None
                print(f"✓ Sound sensor (GPIO22) initialized")
        except Exception as e:
            print(f"✗ Sound sensor failed: {str(e)}")
            self.sensor_status['sound'] = '--'
        
        try:
            if 'door' in self.sensors:
                self.door_sensor = Button(23, pull_up=True)
                self.door_sensor.when_pressed = self._on_door_closed
                self.door_sensor.when_released = self._on_door_open
                self.event_count['door'] = 0
                self.sensor_status['door'] = 'Open'
                self.last_event['door'] = None
                print(f"✓ Door sensor (GPIO23) initialized")
        except Exception as e:
            print(f"✗ Door sensor failed: {str(e)}")
            self.sensor_status['door'] = '--'
        
        try:
            if 'temperature' in self.sensors:
                self.modbus_sensor = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
                self.modbus_sensor.mode = minimalmodbus.MODE_RTU
                self.modbus_sensor.serial.baudrate = 9600
                self.modbus_sensor.serial.bytesize = 8
                self.modbus_sensor.serial.parity = serial.PARITY_NONE
                self.modbus_sensor.serial.stopbits = 1
                self.modbus_sensor.serial.timeout = 1.5
                self.modbus_sensor.clear_buffers_before_each_transaction = True
                self.event_count['temperature'] = 0
                self.sensor_status['temperature'] = '--°C / --%'
                self.last_event['temperature'] = None
                print(f"✓ Temperature sensor (Modbus) initialized")
        except Exception as e:
            print(f"✗ Temperature sensor failed: {str(e)}")
        
        print()
    
    def _on_motion(self):
        """Motion detected."""
        with self.lock:
            self.event_count['motion'] += 1
            self.sensor_status['motion'] = 'MOTION!'
            self.last_event['motion'] = self._timestamp()
            print(f"[{self._timestamp()}] 🚨 MOTION DETECTED (#{self.event_count['motion']})")
    
    def _on_no_motion(self):
        """Motion stopped."""
        with self.lock:
            self.sensor_status['motion'] = 'No Motion'
        print(f"[{self._timestamp()}] ✓ Motion stopped")
    
    def _on_vibration(self):
        """Vibration detected."""
        with self.lock:
            self.event_count['vibration'] += 1
            self.sensor_status['vibration'] = 'VIBRATION!'
            self.last_event['vibration'] = self._timestamp()
            print(f"[{self._timestamp()}] 📳 VIBRATION DETECTED (#{self.event_count['vibration']})")
    
    def _on_sound_detected(self):
        """Sound detected."""
        with self.lock:
            self.event_count['sound'] += 1
            self.sensor_status['sound'] = 'SOUND!'
            self.last_event['sound'] = self._timestamp()
            print(f"[{self._timestamp()}] 🔊 SOUND DETECTED (#{self.event_count['sound']})")
    
    def _on_sound_stopped(self):
        """Sound stopped."""
        with self.lock:
            self.sensor_status['sound'] = 'Silent'
    
    def _on_door_closed(self):
        """Door closed."""
        with self.lock:
            self.event_count['door'] += 1
            self.sensor_status['door'] = 'CLOSED'
            self.last_event['door'] = self._timestamp()
            print(f"[{self._timestamp()}] 🔒 DOOR CLOSED (#{self.event_count['door']})")
    
    def _on_door_open(self):
        """Door opened."""
        with self.lock:
            self.event_count['door'] += 1
            self.sensor_status['door'] = 'OPEN'
            self.last_event['door'] = self._timestamp()
            print(f"[{self._timestamp()}] 🚪 DOOR OPEN (#{self.event_count['door']})")
    
    def _read_temperature(self):
        """Read temperature from Modbus sensor."""
        if not self.modbus_sensor:
            return None
        
        try:
            # Read 2 registers starting at address 0x0001
            # Function code 4 = Read Input Registers
            regs = self.modbus_sensor.read_registers(
                registeraddress=0x0001,
                number_of_registers=2,
                functioncode=4
            )
            
            # Parse temperature (register 0)
            # Signed 16-bit value, divide by 100
            temp_raw = regs[0]
            if temp_raw > 32767:
                temp_raw = temp_raw - 65536
            temperature = temp_raw / 100.0
            
            # Parse humidity (register 1)
            # Unsigned 16-bit value, divide by 100
            humidity = regs[1] / 100.0
            
            return temperature, humidity
        except Exception as e:
            # Silently return None on error (don't print every time)
            return None
    
    def monitor_temperature(self):
        """Temperature monitoring thread."""
        print(f"[{self._timestamp()}] Starting temperature monitoring...")
        last_valid_temp = None
        last_valid_humidity = None
        
        while self.running:
            try:
                result = self._read_temperature()
                if result:
                    temp, humidity = result
                    last_valid_temp = temp
                    last_valid_humidity = humidity
                    with self.lock:
                        self.event_count['temperature'] += 1
                        self.sensor_status['temperature'] = f'{temp:.1f}°C / {humidity:.1f}%'
                        self.last_event['temperature'] = self._timestamp()
                        self.last_temp = temp
                        self.last_humidity = humidity
                        print(f"[{self._timestamp()}] 🌡️  TEMPERATURE: {temp:.1f}°C | Humidity: {humidity:.1f}%")
                else:
                    # If read failed, keep last valid reading if available
                    if last_valid_temp is not None:
                        with self.lock:
                            self.sensor_status['temperature'] = f'{last_valid_temp:.1f}°C / {last_valid_humidity:.1f}%'
                sleep(5)  # Read every 5 seconds
            except Exception as e:
                sleep(5)
    
    def _print_dashboard(self):
        """Print sensor status dashboard."""
        try:
            os.system('clear') if os.name == 'posix' else os.system('cls')
        except:
            pass  # Clear might fail in some environments
        
        print("╔" + "═" * 68 + "╗")
        print("║" + " UNIFIED SENSOR MONITORING DASHBOARD ".center(68) + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        
        # Create table data
        table_data = []
        headers = ["Sensor", "Status", "Events", "Last Event"]
        
        with self.lock:
            for sensor in ['door', 'motion', 'sound', 'temperature', 'vibration']:
                if sensor in self.sensors:
                    status = self.sensor_status.get(sensor, '--')
                    events = str(self.event_count.get(sensor, 0))
                    last = self.last_event.get(sensor)
                    last = last if last else 'Never'
                    
                    table_data.append([sensor.upper(), status, events, last])
        
        # Print formatted table
        print("┌─────────────┬──────────────────────┬────────┬──────────────────────┐")
        print("│    Sensor   │      Status          │ Events │    Last Event        │")
        print("├─────────────┼──────────────────────┼────────┼──────────────────────┤")
        
        for row in table_data:
            sensor, status, events, last_time = row
            print(f"│ {sensor:<11} │ {status:<20} │ {events:>6} │ {str(last_time):>20} │")
        
        print("└─────────────┴──────────────────────┴────────┴──────────────────────┘")
        print()
        print(f"Current Time: {self._timestamp()}")
        print("(Updating every 2 seconds... Press CTRL+C to stop)")
        print()
    
    def print_summary(self):
        """Print monitoring summary."""
        print("\n" + "="*70)
        print("MONITORING SUMMARY")
        print("="*70)
        
        with self.lock:
            for sensor, count in sorted(self.event_count.items()):
                print(f"{sensor.upper():<20} Events: {count}")
        
        print("="*70)
    
    def run(self, duration=None, dashboard=True):
        """Run monitoring system."""
        print(f"[{self._timestamp()}] Monitoring started...")
        if duration:
            print(f"[{self._timestamp()}] Duration: {duration} seconds")
        
        if dashboard:
            print("Dashboard mode enabled - updating display every 2 seconds")
            sleep(1)
        else:
            print("(Press CTRL+C to stop)\n")
        
        # Start temperature monitoring thread if enabled
        if 'temperature' in self.sensors:
            temp_thread = threading.Thread(target=self.monitor_temperature, daemon=True)
            temp_thread.start()
        
        dashboard_update_count = 0
        
        try:
            start_time = datetime.now()
            while self.running:
                if dashboard:
                    self._print_dashboard()
                    dashboard_update_count += 1
                    sleep(2)  # Update dashboard every 2 seconds
                else:
                    sleep(1)
                
                if duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration:
                        break
        except KeyboardInterrupt:
            print("\n⚠️  Monitoring stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        self.running = False
        print(f"[{self._timestamp()}] Cleaning up...")
        
        try:
            if self.motion_sensor:
                self.motion_sensor.close()
            if self.vibration_sensor:
                self.vibration_sensor.close()
            if self.sound_sensor:
                self.sound_sensor.close()
            if self.door_sensor:
                self.door_sensor.close()
            GPIO.cleanup()
        except:
            pass
        
        self.print_summary()


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n⚠️  Interrupted (Ctrl+C)")
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Unified Sensor Monitoring System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  python monitor.py                                # Monitor all sensors
  python monitor.py --sensors motion vibration    # Monitor specific sensors
  python monitor.py --duration 60                  # Monitor for 60 seconds
  python monitor.py --sensors temperature door    # Monitor temp & door only

Available sensors:
  temperature, motion, vibration, sound, door
        '''
    )
    
    parser.add_argument('--sensors', nargs='+', default=['temperature', 'motion', 'vibration', 'sound', 'door'],
                        help='Sensors to monitor (default: all)')
    parser.add_argument('--duration', type=int, default=None,
                        help='Monitoring duration in seconds (default: infinite)')
    parser.add_argument('--no-dashboard', action='store_true',
                        help='Disable dashboard display (show events only)')
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        monitor = UnifiedMonitor(sensors=args.sensors)
        monitor.run(duration=args.duration, dashboard=not args.no_dashboard)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == '__main__':
    main()
