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


"""This Module handles the configuration of the socket to create the LoRa
connection to the server.
You have to modify the app_eui & the app_key for the OTAA authentication with your Lora Gateway
"""

from network import LoRa
from sensors import humidity_sensor
from sensors import gas_sensor
from sensors import gps_sensor
from sensors import pm_sensor
from pycom import rgbled
import time
import pycom
import binascii
import socket
import utime
from lib import cbor

############ CONFIGURATION OF THE CONNECTION WITH SERVER LNS ############

#Initialize LoRa
lora = LoRa(mode=LoRa.LORAWAN)

### Create an OTAA authentication parameters

# app_eui format : '00 00 00 00 00 00 00 00'
app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))

# app_key format : '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
app_key = binascii.unhexlify('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'.replace(' ',''))

############ SOCKET LORA CONFIGURATION ############
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
#s.bind(5)

# SO_DR, DATA RATE USED 0-5 (5 FASTER BUT SENSIBLE, 0 SLOWER BUT ROBUST, EACH LEVEL DOUBLES TRANSMISION TIME)
#
#
#    0: SF = 12, BW = 125 kHz, BitRate =  250 bps, maxPayload = 51 Bytes
#    1: SF = 11, BW = 125 kHz, BitRate =  440 bps, maxPayload = 51 Bytes
#    2: SF = 10, BW = 125 kHz, BitRate =  980 bps, maxPayload = 51 Bytes
#    3: SF =  9, BW = 125 kHz, BitRate = 1760 bps, maxPayload = 115 Bytes
#    4: SF =  8, BW = 125 kHz, BitRate = 3125 bps, maxPayload = 222 Bytes
#    5: SF =  7, BW = 125 kHz, BitRate = 5470 bps, maxPayload = 222 Bytes
#
#
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)
# SO_CONFIRMED, ACK FOR EACH FRAME
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)


# Function for join LNS gateway
def joinLNS():
    """
    Creation of the LoRa Connection
    """
    print('Starting Join Function')
    pycom.heartbeat(False)
    pycom.rgbled(0x00FF00)

    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(8)
        print('Not yet joined...')

    print('Joined Successfully')
    pycom.rgbled(0xFFFFFF)
    time.sleep(3)
    get_time()

def get_time():
    """Sending of the Messages to the LoRa SERVER for getting the datetime
    """
    pycom.heartbeat(False)
    # LED IN BLUE (TRYING TO SEND MESSAGE)
    pycom.rgbled(0x0000FF)
    s.setblocking(True)
    s.settimeout(20)

    print('Trying to send message')
    try:
        s.send(cbor.dumps("get_time"))
        print('Message sent!')
    except:
        print('Failed to send message!')
        rgbled(0xFF0000) #LED RED

    pycom.rgbled(0x00FF00) #LED GREEN

    #LED IN BLUE (WAITING FOR DATA)
    print('Waiting for Data...')
    pycom.rgbled(0x0000FF)

    msg_nb_try = 0
    msg_send_ok = False

    while((msg_send_ok == False) and (msg_nb_try < 3)):
        # If retry, wait before retrying
        if(msg_nb_try > 1):
            time.sleep(10)

        msg_nb_try = msg_nb_try + 1

        try:
            data = s.recv(64)
            print('Data Received:')
            print(cbor.loads(data))

            if 'datetime' in data.keys():
                utime.timezone((data['datetime'] - utime.time()))
                print('datetime updated : ' + str(data['datetime']))
                msg_send_ok = True

        except:
            print ('timeout in receive')
            pycom.rgbled(0xFF0000)

        #LED IN GREEN (DATA RECEIVED)
        pycom.rgbled(0x00FF00)
        s.setblocking(False)


# Function for sending the cbor message to the LNS gateway
def sendMessage(msg_cbor):
    """Sending of the Messages to the LoRa SERVER\n
    :msg_cbor: Message Encoded in Cbor with the measures taken.
    """
    pycom.heartbeat(False)
    # LED IN BLUE (TRYING TO SEND MESSAGE)
    pycom.rgbled(0x0000FF)
    s.setblocking(True)
    s.settimeout(20)

    msg_nb_try = 0
    msg_send_ok = False

    while((msg_send_ok == False) and (msg_nb_try < 3)):
        # If retry, wait before retrying
        if(msg_nb_try > 1):
            time.sleep(10)

        print('Trying to send message')
        msg_nb_try = msg_nb_try + 1
        try:
            s.send(msg_cbor)
            print('Message sent!')
        except:
            print('Failed to send message!')
            rgbled(0xFF0000) #LED RED

        pycom.rgbled(0x00FF00) #LED GREEN

        #LED IN BLUE (WAITING FOR DATA)
        print('Waiting for Data...')
        pycom.rgbled(0x0000FF)

        try:
            data = s.recv(64)
            msg_receive = cbor.loads(data)

            if 'status' in msg_receive.keys():
                if msg_receive['status'] == 'ok':
                    msg_send_ok = True

        except:
            print ('timeout in receive')
            pycom.rgbled(0xFF0000)

    #LED IN GREEN (DATA RECEIVED)
    pycom.rgbled(0x00FF00)

    s.setblocking(False)
