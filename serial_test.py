#!/usr/bin/env python
import os
import sys
import serial
from dotenv import load_dotenv

load_dotenv()

serial_port = os.getenv("SERIAL_PORT")
baud_rate = os.getenv("BAUD_RATE")

if serial_port is None or baud_rate is None:
    print("Please set your serial port and baud rate in .env")
    sys.exit(1)

with serial.Serial(
        port=serial_port, #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = baud_rate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
) as ser:     # read up to ten bytes (timeout)
    try:
        while ser.is_open:
            line = ser.readline().decode().rstrip()
            print(line)
    except KeyboardInterrupt:
        ser.close()