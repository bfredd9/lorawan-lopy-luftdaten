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
import adafruit_gps

class GPSSensor:
    """A class to handle the GPS.

    :param uart: The `UART` object to use.
    """
    def __init__(self, uart):
        #Declare an GPS object
        self._gps = adafruit_gps.GPS(uart)

        #Attributes
        self._time = None
        self._latitude = None
        self._longitude = None

        self.started = False

    def start_gps(self):
        #Turn on the basic GGA and RMC info (what you typically want)
        self._gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        #Set update rate to once a second (1hz).
        self._gps.send_command('PMTK220,1000')
        # Set started "True"
        self.started = True

    def stop_gps(self):
        # Turn off GPS
        gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Set started "False"
        self.started = False

    # Work function, return True when values available
    def work(self):
        """Polls the GPS and checks if it has fix to take the measures
        returns True or False
        """
        if(self.started is False):
            self.start_gps()

        self._gps.update()

        if self._gps.has_fix:
            # Update GPS values
            self._latitude = self._gps.latitude
            self._longitude = self._gps.longitude
            self._time = self._gps.timestamp_utc
            # Stop GPS
            self.stop_gps()

            return True

        return False


    def get_latitude(self):
        """Return last read latitude and longitude or None if last reading
        failed.
        """
        ret_val = self._latitude
        self._latitude = None
        return ret_val

    def get_longitude(self):
        """Return last read latitude and longitude or None if last reading
        failed.
        """
        ret_val = self._longitude
        self._longitude = None
        return ret_val

    def get_time(self):
        """Return last read time or None if last reading failed.
        """
        ret_val = self._time
        self._time = None
        return ret_val
