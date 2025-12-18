import minimalmodbus
import serial
import time

# ---------------- CONFIG ----------------
PORT = '/dev/ttyUSB0'     # change if needed
SLAVE_ID = 1
BAUDRATE = 9600
INTERVAL = 2.0            # seconds between reads
# ----------------------------------------

instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
instrument.serial.baudrate = BAUDRATE
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 1
instrument.mode = minimalmodbus.MODE_RTU

print("XY-MD02 Continuous Modbus Test Started")
print("Press CTRL+C to stop\n")

while True:
    try:
        temp_raw = instrument.read_register(0x0000, 1)
        hum_raw  = instrument.read_register(0x0001, 1)

        temperature = temp_raw / 10.0
        humidity = hum_raw / 10.0

        print(f"Temperature: {temperature:.1f} °C | Humidity: {humidity:.1f} %RH")

    except Exception as e:
        print("Read error:", e)

    time.sleep(INTERVAL)
