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
import adafruit_sgp30

class GasSensor:
    """A class to handle the CO2 and TVOC sensor.

    :param i2c_bus: The `I2C` object to use.
    :param meas_intvl: The minimal amount of time between two measurements (in ms).
    """
    def __init__(self, i2c_bus, meas_intvl):
        #Declare an SGP30 object
        self._sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c_bus)

        #Initialize SGP-30 internal drift compensation algorithm.
        self._sgp30.iaq_init()

        #Retrieve previously stored baselines, if any (helps the compensation algorithm).
        try:
            f_co2 = open('ressources/co2eq_baseline.txt', 'r')
            f_tvoc = open('ressources/tvoc_baseline.txt', 'r')

            co2_baseline = int(f_co2.read())
            tvoc_baseline = int(f_tvoc.read())
            #Use them to calibrate the sensor
            self._sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

            f_co2.close()
            f_tvoc.close()
        except:
            print('Impossible to read SGP30 baselines!')

        #Store the time at which last baseline has been saved
        self._baseline_time = time.time()

        self._meas_intvl = meas_intvl
        self._last_meas_time = None

        #Attributes for CO2 and TVOC
        self._co2 = None
        self._tvoc = None

    def work(self, n_try_max):
        """Perform a measurement (every minute, if possible), and save baseline
        (every hour, if possible).

        :param n_try_max: Number of reading tentatives.
        """

        #Do measurements
        if(self._last_meas_time is None) \
        or (time.ticks_diff(self._last_meas_time, time.ticks_ms()) >= self._meas_intvl):
            self._last_meas_time = time.ticks_ms()

            for i in range(0, n_try_max):
                try:
                    self._co2 = self._sgp30.co2eq
                    self._tvoc = self._sgp30.tvoc
                    break
                except:
                    pass


        '''
        #Baselines should be saved every hour, according to the doc.
        if(time.time() - self._baseline_time >= 3600):
            print('Saving baseline!')
            self._baseline_time = time.time()

            f_co2 = open('ressources/co2eq_baseline.txt', 'w')
            f_tvoc = open('ressources/tvoc_baseline.txt', 'w')

            f_co2.write(str(self._sgp30.baseline_co2eq))
            f_tvoc.write(str(self._sgp30.baseline_tvoc))

            f_co2.close()
            f_tvoc.close()
        '''

    def get_co2(self):
        """Return last read CO2 concentration (in ppm) or None is last reading
        failed.
        """
        ret_val = self._co2
        self._co2 = None
        return ret_val

    def get_tvoc(self):
        """Return last read TVOC (in ppm) or None is last reading failed.
        """
        ret_val = self._tvoc
        self._tvoc = None
        return ret_val
