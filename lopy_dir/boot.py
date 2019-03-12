# -*- coding: utf-8 -*-
#
#    Project : "Station de qualité de l'air Lora"
#
#    Copyright (C) 2019  Yohann LE GALL & Sergio QUINTERO
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
In this module is the configuration of the LoPy4 when it boots, the interfaces and hardware features availables at the booting
"""
# boot.py -- run on boot-up
from machine import UART
from machine import I2C
from machine import Pin
import network
import pycom
from lib import sds011

#Turn off heartbeat for built-in LED
pycom.heartbeat(False)

#Turn off bluetooth
bt = network.Bluetooth()
bt.deinit()

#Turn OFF WiFi if Vcc on Pin13
p_wifi = Pin('P13', mode=Pin.IN)
if(p_wifi.value() == 1):
    wlan = network.WLAN(mode=network.WLAN.STA)
    wlan.deinit()

#Initialize UARTs and I2C, just so that the LoPy do not use these pins for
#something else and bring instabilities...

#UART for GPS on pins P3, P4
uart_gps = UART(1, baudrate=9600, timeout_chars=3000)

#UART for SDS011 on pins P22, P21 => (pins=(TX,RX))
uart_sds011 = UART(2, baudrate=9600, pins=('P22','P21'))

#I2C bus for every I2C devices on pins P9, P10
i2c = I2C(0, I2C.MASTER)
i2c.init(I2C.MASTER, baudrate=100000)

#Stop SDS011 fan
dust_sensor = sds011.SDS011(uart_sds011)
dust_sensor.sleep()

print('Ending boot file')
