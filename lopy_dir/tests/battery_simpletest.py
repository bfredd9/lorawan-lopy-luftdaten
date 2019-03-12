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
from sensors import battery_sensor
from lib import battery

#Initialize the battery sensor
batt = battery_sensor.Battery_sensor()

batt2 = battery.Battery()

while True:
    print('Battery voltage is: ' + str(batt.get_voltage(10)) + ' V (new version)')
    print('Battery voltage is: ' + str(batt2.voltage()) + ' V (old version)')
    time.sleep(1)
