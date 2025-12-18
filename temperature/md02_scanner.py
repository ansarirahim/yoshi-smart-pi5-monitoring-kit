#!/usr/bin/env python3
"""
XY-MD02 Modbus Register Scanner - Diagnostic Tool

Scans all possible register addresses to find temperature and humidity data.

Usage:
    python md02_scanner.py [--port PORT] [--slave SLAVE]
"""

import sys
import time
import argparse
import serial

try:
    import minimalmodbus
except ImportError:
    print("ERROR: minimalmodbus not installed")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="XY-MD02 Register Scanner")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--slave", type=int, default=1)
    parser.add_argument("--baudrate", type=int, default=9600)

    args = parser.parse_args()

    try:
        instrument = minimalmodbus.Instrument(args.port, args.slave)
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.serial.baudrate = args.baudrate
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1.5
        instrument.clear_buffers_before_each_transaction = True

        print("=" * 70)
        print("XY-MD02 MODBUS REGISTER SCANNER")
        print("=" * 70)
        print(f"Port: {args.port}, Slave: {args.slave}, Baudrate: {args.baudrate}\n")

        print("Scanning registers 0x0000-0x000F...")
        print("=" * 70)
        print(f"{'Addr':<8} {'Reg0':<8} {'Reg1':<8} {'Temp(÷10)':<15} {'Hum(÷10)':<15}")
        print("-" * 70)

        for start_addr in range(0, 16):
            try:
                regs = instrument.read_registers(
                    registeraddress=start_addr,
                    number_of_registers=2,
                    functioncode=4
                )

                # Try different parsing combinations
                temp1 = regs[0] / 10.0
                temp2 = regs[1] / 10.0
                hum1 = regs[0] / 10.0
                hum2 = regs[1] / 10.0

                # Handle signed for temp
                t1_raw = regs[0]
                if t1_raw > 32767:
                    t1_raw -= 65536
                temp1_signed = t1_raw / 10.0

                t2_raw = regs[1]
                if t2_raw > 32767:
                    t2_raw -= 65536
                temp2_signed = t2_raw / 10.0

                print(
                    f"0x{start_addr:04X}   {regs[0]:<8} {regs[1]:<8} "
                    f"{temp1_signed:>6.1f}°C(R0)    {hum2:>6.1f}%RH(R1)"
                )

            except Exception as e:
                print(f"0x{start_addr:04X}   Error: {str(e)[:40]}")

        print("=" * 70)
        print("\nInstructions:")
        print("1. Look for Temp in range -40 to 80°C")
        print("2. Look for Humidity in range 0 to 100%")
        print("3. Note the register address (Addr column)")
        print("4. Update md02.py with found address")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
