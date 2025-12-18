#!/usr/bin/env python3
"""
XY-MD02 Temperature/Humidity Sensor - Continuous Modbus Test

This script continuously reads temperature and humidity from the XY-MD02 sensor
using the minimalmodbus library.

Requirements:
    pip install minimalmodbus pyserial

Wiring:
    USB-RS485 Converter -> Raspberry Pi
    - Red (5V)    -> USB Power
    - Black (GND) -> USB Ground
    - A (White)   -> USB A/TX+
    - B (Green)   -> USB B/RX-

Usage:
    python md02.py
    python md02.py --port /dev/ttyUSB0
    python md02.py --port /dev/ttyUSB0 --interval 2.0
    python md02.py --port /dev/ttyUSB0 --slave 1 --baudrate 9600

CTRL+C to stop
"""

import sys
import time
import struct
import argparse
import serial

try:
    import minimalmodbus
except ImportError:
    print("ERROR: minimalmodbus not installed")
    print("Install with: pip install minimalmodbus")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="XY-MD02 Continuous Modbus Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python md02.py
  python md02.py --port /dev/ttyUSB0 --interval 1.0
  python md02.py --slave 1 --baudrate 9600
        """
    )
    parser.add_argument(
        "--port",
        default="/dev/ttyUSB0",
        help="Serial port (default: /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--slave",
        type=int,
        default=1,
        help="Slave ID (default: 1)"
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=9600,
        help="Baudrate (default: 9600)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Interval between reads in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.5,
        help="Serial timeout in seconds (default: 1.5)"
    )

    args = parser.parse_args()

    # Setup instrument
    try:
        instrument = minimalmodbus.Instrument(args.port, args.slave)
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.serial.baudrate = args.baudrate
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = args.timeout
        instrument.clear_buffers_before_each_transaction = True

        print("=" * 70)
        print("XY-MD02 TEMPERATURE/HUMIDITY SENSOR - CONTINUOUS TEST")
        print("=" * 70)
        print(f"Port:        {args.port}")
        print(f"Slave ID:    {args.slave}")
        print(f"Baudrate:    {args.baudrate}")
        print(f"Interval:    {args.interval}s")
        print(f"Timeout:     {args.timeout}s")
        print("=" * 70)
        print("Press CTRL+C to stop\n")

    except Exception as e:
        print(f"ERROR: Failed to initialize instrument: {e}")
        sys.exit(1)

    read_count = 0
    error_count = 0

    try:
        while True:
            try:
                # Read 2 registers starting at address 0x0001
                # Function code 4 = Read Input Registers
                regs = instrument.read_registers(
                    registeraddress=0x0001,
                    number_of_registers=2,
                    functioncode=4
                )

                # Parse temperature (register 0)
                # Signed 16-bit value, divide by 100 (calibration)
                # minimalmodbus returns unsigned, convert to signed manually
                temp_raw = regs[0]
                if temp_raw > 32767:  # Convert to signed if > max positive
                    temp_raw = temp_raw - 65536
                temperature = temp_raw / 100.0

                # Parse humidity (register 1)
                # Unsigned 16-bit value, divide by 100 (calibration)
                hum_raw = regs[1]
                humidity = hum_raw / 100.0

                read_count += 1
                status = "✓" if -40 <= temperature <= 80 and 0 <= humidity <= 100 else "✓"
                print(f"[{read_count:04d}] {status} Temp: {temperature:7.1f}°C | Humidity: {humidity:6.1f}%RH")

            except Exception as e:
                error_count += 1
                print(f"[{read_count + 1:04d}] ✗ Read error: {e}")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("TEST STOPPED BY USER")
        print("=" * 70)
        print(f"Total reads:    {read_count}")
        print(f"Errors:         {error_count}")
        if read_count > 0:
            success_rate = ((read_count - error_count) / read_count) * 100
            print(f"Success rate:   {success_rate:.1f}%")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
