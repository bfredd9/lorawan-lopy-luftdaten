# -*- coding: utf-8 -*-
#
#    Project : "Station meteo connectée Lora"
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
This module provides the functions and configurations of the server when it receives information from the LoRa Network Server
"""
import sys, getopt
from flask import Flask
from flask import request
from flask import Response
import base64
import pprint
import json
import cbor2 as cbor
import urllib
import time

app = Flask(__name__)

app.debug = True

@app.route('/lns', methods=['POST'])
def get_from_LNS():
    """
    This method receives the information from the LNS, decodes the data and stores it. Provides the possibility to send the values
    to an external cloud server using a post request.
    """

    fromGW = request.get_json(force=True)
    print ("_________________________________________________________________________________________________________________________________")
    print ("HTTP POST RECEIVED :")
    pprint.pprint(fromGW)
    if "data" in fromGW:
        payload = base64.b64decode(fromGW["data"])
        data = cbor.loads(payload)
        datajson = json.dumps(data)
        filedata = open('data.txt','a+')
        filedata.write(datajson+"\n")
        print (data)


        print ("\n")

        rep = {}
        
        if(data == 'get_time'):
            print("get Time")
            rep['datetime'] = str(time.time())
            print("Time : " + rep['datetime'] + "")
            
        else:
            for key in data.keys():

                print("Date  [", time.strftime("%D %H:%M", time.localtime(int(key))), "] :")

                if('pm2.5' in data[key]):
                    print ("pm2.5 : ", data[key]['pm2.5'], " µg/m3")

                if('pm10' in data[key]):
                    print ("pm10  : ", data[key]['pm10'], " µg/m3")

                if('temperature' in data[key]):
                    print ("temp  : ", data[key]['temperature'], " °C")

                if('humidity' in data[key]):
                            print ("hum   : ", data[key]['humidity'], " %")

                if('co2' in data[key]):
                    print ("CO2   : ", data[key]['co2'], " ppm")

                if('TVOC' in data[key]):
                    print ("TVOC  : ", data[key]['TVOC'], " ppb")

            rep['status'] = "ok"
            
            print("Starting Process to send data to Luftdaten\n\n")

            #sensor ID to send information to luftdaten
            sensorID = 'LoPy4-xxxxxxxxxxxxxxxxxx'

            #Sending the data to luftdaten
            sendPostLuftdaten(1, sensorID, data)
            sendPostLuftdaten(7, sensorID, data)

        answer = {
          "fPort" : fromGW["fPort"],
          "devEUI": fromGW["devEUI"],
          "data" : base64.b64encode(bytes(str(cbor.dumps(rep)), 'utf-8')).decode('utf-8')
        }

        
        print("\n\n\n")
        print ("HTTP POST REPLY FROM LNS:")
        pprint.pprint(answer)
        resp = Response(response=json.dumps(answer), status=200, mimetype="plain/text")
        return resp


def sendPostLuftdaten(pinNumber, sensorID, data):
    """
    This method will create the header, data and request used to send the values to luftdaten and sends the post request\n
    arguments:\n
    :pinNumber: (integer) Luftdaten's parameter, determines the type of data that will be sent in the post.\n
      'x-Pin':'1' SDS011 (Dust sensor in pm2.5 and pm10 in µg/m )\n
      'x-Pin':'7' DHT22 or AM2320  (Temperature and Humidity)\n
    :X-Sensor: (string) ID for the card used to fill the form in luftdaten website
       for pycom LoPy4 it has the format 'LoPy4-<LoRadevEUI>'\n
    :data: (dictionary) the values received from the LoPy4.
    """
    # defining the api-endpoint for luftdaten
    API_ENDPOINT_LD = "https://api.luftdaten.info/v1/push-sensor-data/"

    #Header Creation
    header = {
           'Content-Type': 'application/json',
           'X-Pin':str(pinNumber),
           'X-Sensor': str(sensorID)
          }

    #Depending on the pinNumber, a different structure of data is created and filled with the data
    if (pinNumber == 1):
      datald = {
         "software_version": "1",
         "sensordatavalues": [
                               {"value_type": "P1", "value": "0"},
                               {"value_type": "P2", "value": "0"}
                             ]
               }

      for k in data.keys():
         values = data[k]
         try:
            datald["sensordatavalues"][0]["value"]=str(values["pm10"])
            datald["sensordatavalues"][1]["value"]=str(values["pm2.5"])
         except:
            continue

    elif (pinNumber == 7):
      datald = {
         "software_version": "1",
         "sensordatavalues": [
                               {"value_type": "temperature", "value": "0"},
                               {"value_type": "humidity", "value": "0"}
                             ]
               }

      for k in data.keys():
         values = data[k]
         try:
            datald["sensordatavalues"][0]["value"]=str(values["temperature"])
            datald["sensordatavalues"][1]["value"]=str(values["humidity"])
         except:
            continue
    else:
      sys.exit("Warning! not recognize type for data, please enter 1 or 7 as pinNumber \n\n")

    request = urllib.request.Request(API_ENDPOINT_LD, data=json.dumps(datald).encode('utf-8'), headers=header)
    response = urllib.request.urlopen(request).read()
    print(response)

if __name__ == '__main__':
    print (sys.argv)

    defPort=8231
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:",["port="])
    except getopt.GetoptError:
        print ("{0} -p <port> -h".format(sys.argv[0]))
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ("{0} -p <port> -h".format(sys.argv[0]))
            sys.exit()
        elif opt in ("-p", "--port"):
            defPort = int(arg)

    app.run(host="0.0.0.0", port=defPort)
