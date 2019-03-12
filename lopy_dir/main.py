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
Main module:\n
Contains the main execution, the constants to create a message to be sent and the creation of the sensors.
"""

import time
import utime
from lib import cbor
from sensors import humidity_sensor
from sensors import gas_sensor
from sensors import gps_sensor
from sensors import pm_sensor
from sensors import battery_sensor
from pycom import rgbled
from network import LoRa
from machine import I2C
from machine import UART
import socket
import binascii
import loraconnection
from loraconnection import *

###Constants###
_FIELD_TIME = 'time'
_FIELD_LATITUDE = 'lat'
_FIELD_LONGITUDE = 'lon'
_FIELD_BATTERY_ENERGY= 'battery'
_FIELD_TEMPERATURE = 'temperature'
_FIELD_HUMIDITY = 'humidity'
_FIELD_CO2 = 'co2'    #calculated carbon-dioxide (0-60000 ppm)
_FIELD_TVOC = 'TVOC'  #total volatile organic compound (0-60000 ppm)
_FIELD_PM25 = 'pm2.5'
_FIELD_PM10 = 'pm10'


def isTimeToTakeMeasure(sensorLastMeasure, sensorMeasureInterval):
    """
    Verifies if the measure interval of a given sensor is completed and returns True or False
    Arguments:\n
    :sensorLastMeasure: Time of the last measure taken in miliseconds\n
    :sensorMeasureInterval: Interval of time predefined between each measure in miliseconds
    """
    if ((sensorLastMeasure is None) or (time.ticks_diff(sensorLastMeasure,time.ticks_ms()) >= sensorMeasureInterval)):
        return True
    return False

def main():
    """
    Contains the Main while loop, where in each iteration
    based on measurement predefined intervals takes a measure and stores it.
    When the send time interval is achieved, all the measures taken at that moment
    are saved in a message and are sent to the server.
    You can modify the diferent intervals here
    """
    #INTERVALS OF MEASUREMENT AND SENDING MESSAGE
    #Keep track of last time we sent a message
    # /!\ Warning : The sending interval depends of the maxmimum Payload, and this Payload is defined by the dataRate used. (setting in loraconnection.py) /!\
    last_send_time = None
    send_intvl = 90000
    #Define dust Inter measure interval (in ms) (time between each startFanfor30sec-takemeasure-stopFan)
    dust_measure_interval = 30000
    dust_last_measure = None
    #Define Co2 measure interval (in ms)
    co2_measure_interval = 89000
    co2_last_measure = None
    #Define GPS measure interval (in ms)
    gps_measure_interval = 89000
    gps_last_measure = None
    #Define Temperature measure interval (in ms)
    temp_measure_interval = 89000
    temp_last_measure = None

    #message to be send at the end of the last send time
    global_message = {}
    #current measures taken before the last send interval is achieved
    current_message = {}

    #Principal Loop
    while True:

        # Init Current message
        current_message = {}
        message_info = 0

        #Connection trigger if it's not stablished and checking before sending the message
        if not lora.has_joined():
            rgbled(0x43142f) #LED Violet
            print("Lora connection lost or not started")
            loraconnection.joinLNS()

        rgbled(0x000000) #LED Off

        # Dust measure
        try:
            if isTimeToTakeMeasure(dust_last_measure, dust_measure_interval):
                dust_last_measure = time.ticks_ms()
                if(dust_sensor.work() is True):
                    current_message[_FIELD_PM25] = dust_sensor.get_pm25()
                    current_message[_FIELD_PM10] = dust_sensor.get_pm10()
                    message_info = message_info + 2
        except Exception as e:
            print("DUST Sensor exception : " + str(e))

        # Co2 & TVOC measure
        try:
            if isTimeToTakeMeasure(co2_last_measure, co2_measure_interval):
                co2_last_measure = time.ticks_ms()
                gas_sensor.work(5)
                current_message[_FIELD_CO2] = gas_sensor.get_co2()
                current_message[_FIELD_TVOC] = gas_sensor.get_tvoc()
                message_info = message_info + 2
        except Exception as e:
            print("Co2 & TVOC sensor exception : " + str(e))

        # Temperature & Humidity measure
        try:
            if isTimeToTakeMeasure(temp_last_measure, temp_measure_interval):
                temp_last_measure = time.ticks_ms()
                temp_sensor.work(5)
                current_message[_FIELD_TEMPERATURE] = temp_sensor.get_temperature()
                current_message[_FIELD_HUMIDITY] = temp_sensor.get_humidity()
                message_info = message_info + 2
        except Exception as e:
            print("Temperature & Humidity sensor exception : " + str(e))

        # GPS position
        try:
            if isTimeToTakeMeasure(gps_last_measure, gps_measure_interval):
                gps_last_measure = time.ticks_ms()
                if(gps_sen.work() is True):
                    current_message[_FIELD_LATITUDE] = gps_sen.get_latitude()
                    current_message[_FIELD_LONGITUDE] = gps_sen.get_longitude()
                    message_info = message_info + 2
        except Exception as e:
            print("GPS sensor exception : " + str(e))

        try:
            if(message_info > 0):
                Date = str(utime.mktime(utime.localtime()))
                global_message[Date] = current_message
                print("Current : " + str(current_message))
        except Exception as e:
            print("Update current message exception : " + str(e))

        #checks if the time is not equal to None and if the difference between the last_send_time and actual time
        #is bigger than the send_intvl time
        try:

            if ( (last_send_time is None) or (time.ticks_diff(last_send_time,time.ticks_ms()) >= send_intvl) ):
                last_send_time = time.ticks_ms()

                #Make message and save it to a dictionary type variable
                print("Global : " + str(global_message))

                #Transform to CBOR
                msg_cbor = cbor.dumps(global_message)
                print("Message en cbor : " + str(msg_cbor))

                #Sending the message (FOR CORRECTLY SENDING THE MESSAGE: MAXIMUM MESSAGE SIZE = 93)
                loraconnection.sendMessage(msg_cbor)
                rgbled(0x000000) #LED Off

                # Delete old informations
                global_message = {}

        except Exception as e:
            print("Send global message exception : " + str(e))



if __name__ == '__main__':
    ##########INITIALIZATION OF THE SENSORS##########
    #Initialize I2C bus
    i2c = I2C(0, I2C.MASTER)
    i2c.init(I2C.MASTER, baudrate=100000)

    #Create a temperature sensor object
    try:
        temp_sensor = humidity_sensor.TempHumiditySensor(i2c, 1000)
    except Exception as e:
        print("Exception : " + str(e))


    #Create a gas sensor object
    try:
        gas_sensor = gas_sensor.GasSensor(i2c, 1000)
    except Exception as e:
        print("Exception : " + str(e))

    #Initialize dust sensor
    try:
        #UART for SDS011 on pins P22, P21 => (pins=(TX,RX))
        uart_dust = UART(2, baudrate=9600, pins=('P22','P21'))
        dust_sensor = pm_sensor.PMSensor(uart_dust, 30000)
    except Exception as e:
        print("Exception : " + str(e))

    #Initialize GPS
    try:
        #UART for GPS we use default uart pin
        uart_gps = UART(1, baudrate=9600, timeout_chars=3000)
        gps_sen = gps_sensor.GPSSensor(uart_gps)
    except Exception as e:
        print("Exception : " + str(e))

    #Init Battery
    try:
        battery_sen = battery_sensor.Battery_sensor()
    except Exception as e:
        print("Exception : " + str(e))

    #Executing the main function
    main()
