#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensors Module - Hardware Sensor Drivers for Raspberry Pi Smart Monitoring Kit.

@file       __init__.py
@brief      Package initialization for sensor drivers.
@details    Provides unified access to all sensor modules:
            - Temperature/Humidity (XY-MD02 via Modbus RTU)
            - PIR Motion (HC-SR501)
            - Vibration (801S)
            - Sound (LM393)
            - Door (MC-38 Reed Switch)

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.
"""

from .temperature import TemperatureSensor, modbus_crc
from .motion import MotionSensor, MotionEvent, MotionState, TriggerMode

__all__ = [
    # Temperature Sensor
    'TemperatureSensor',
    'modbus_crc',
    # Motion Sensor (PIR)
    'MotionSensor',
    'MotionEvent',
    'MotionState',
    'TriggerMode',
]

