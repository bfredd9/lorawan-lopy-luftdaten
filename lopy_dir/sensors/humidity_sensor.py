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


import time
import adafruit_am2320

class TempHumiditySensor:
    """A class to handle the temperature and humidity sensor.

    :param i2c_bus: The `I2C` object to use.
    :param meas_intvl: The minimal amount of time between two measurements (in ms).
    """
    def __init__(self, i2c_bus, meas_intvl):
        #Declare an AM2320 object
        self._am = adafruit_am2320.AM2320(i2c_bus)

        self._meas_intvl = meas_intvl
        self._last_meas_time = None

        #Attributes for temperature and humidity
        self._temperature = None
        self._humidity = None

    def work(self, n_try_max):
        """Perform a measurement.
        :param n_try_max: Number of reading tentative (this sensor does not always respond...)
        """
        if(self._last_meas_time is None) \
        or (time.ticks_diff(self._last_meas_time, time.ticks_ms()) >= self._meas_intvl):
            self._last_meas_time = time.ticks_ms()

            for i in range(0, n_try_max):
                try:
                    self._temperature = self._am.temperature
                    self._humidity = self._am.relative_humidity
                    break
                except:
                    pass

    def get_temperature(self):
        """Return last read temperature or None is last reading failed.
        """
        ret_val = self._temperature
        self._temperature = None
        return ret_val

    def get_humidity(self):
        """Return last read temperature or None is last reading failed.
        """
        ret_val = self._humidity
        self._humidity = None
        return ret_val
