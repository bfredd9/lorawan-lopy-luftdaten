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


from machine import ADC

class Battery_sensor:
    """A  class to handle the Battery sensor.
    """

    def __init__(self):
        self.adc = ADC()
        self.batt = self.adc.channel(pin='P16', attn=ADC.ATTN_2_5DB)

    '''
        The tension is given after resistor : 56k / (56k + 115k)
        So the tension range : [0 * (56/(56+115)) ; 4.1 * (56/(56+115)) ]
                               [0 ; 1.342]
        So with attn of
            2.5 dB the range of the adc is [0 ; 1.334 V]
            6 dB the range of the adc is   [0 ; 1.995 V]

        So we need to use 2.5dB of attenuation

        Table of values is [0 ; 4095] <=> [0 ; 1.334 V]
    '''
    def get_voltage(self, nb_values):
        """
        Returns the voltage value
        """
        sum = 0
        for i in range (1,nb_values):
            sum = sum + self.batt.value()

        voltage = (sum / nb_values) * (1.334/4095) * (1 / (56/(56+115)))

        return voltage
