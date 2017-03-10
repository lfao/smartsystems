#import json
import paho.mqtt.client as mqtt
import requests
from functools import reduce
import operator
import json

#mucowm = {"coord":{"lon":11.58,"lat":48.14},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":282.16,"pressure":1019,"humidity":93,"temp_min":281.15,"temp_max":283.15},"visibility":10000,"wind":{"speed":4.1,"deg":240},"clouds":{"all":75},"dt":1489083600,"sys":{"type":1,"id":4914,"message":0.2293,"country":"DE","sunrise":1489037842,"sunset":1489079481},"id":6940463,"name":"Altstadt","cod":200}


FIELD_MATCHES = [(('t', 'Temperatur', 'Kelvin'),[u'main', u'temp']), 
                (('h', 'Humidity', '%'),[u'main', u'humidity']),
                (('w', 'Windspeed', 'mph'),[u'wind',u'speed'])]

SERVER = '130.206.112.29'

class city(object):
    """description of class"""
    IOT_API_KEY = 1234
    OWM_KEY = 'abacdae90c8800879db8e02327da1f92'
    OWM_URL = 'http://api.openweathermap.org/data/2.5/weather?id={}&appid={}'
    UPDATE_FIELDS = [(iotName, owmPath) for ((iotName, _, _), owmPath) in FIELD_MATCHES]
    MQTT_SERVER = SERVER
    MQTT_PORT = 1883
    DEVICE_BASISNAME = 'DevID37101'

    def __init__(self, cityOwaId, cityId):
        self.cityOwaId = cityOwaId
        self.deviceId = city.DEVICE_BASISNAME + cityId
        self.mqttClient = mqtt.Client()
        #print "asdf"
        self.mqttClient.connect(city.MQTT_SERVER, city.MQTT_PORT)
        #print "asd"        

    def getOwmJsonInfo(self):
        url = city.OWM_URL.format(self.cityOwaId, city.OWM_KEY)
        #print (url)
        r = requests.get(url)
        #print( r.json() )
        return r.json() if 200 == r.status_code else None
    
    @staticmethod
    def convertOwmToIot(jsonDict):
        #print jsonDict
        #print jsonDict[u'temperature']
        #print operator.getitem(jsonDict,u'temperature')
        newDict = { iotName : reduce(operator.getitem, owmPath, jsonDict) for iotName, owmPath in city.UPDATE_FIELDS }
        #print(newDict)
        return newDict

    def putIotJson(self, jsonDict):
        #print jsonDict
        #print json.dumps(jsonDict)
        self.mqttClient.publish("/{}/{}/attrs/".format(city.IOT_API_KEY, self.deviceId), json.dumps(jsonDict))

    def update(self):
        jsonDict = self.getOwmJsonInfo()
        if jsonDict:
            self.putIotJson(city.convertOwmToIot(jsonDict))
        return jsonDict

    #def __repr__(self):
    #    return "<Test a:%s b:%s>" % (self.a, self.b)

    def __str__(self):
        return 'IOT Name = {}, OWA City ID = {}'.format(self.deviceId, self.cityOwaId)

def createCity(cityOwaId = 6940463, cityId = 'muc', cityName = None):
    FIWARE_SERVICE_PATH = '/environment'
    FIWARE_SERVICE = 'icai31701'
    IOT_AGENT_URL = 'http://130.206.112.29:5050/iot/devices/'
    
    theCity = city(cityOwaId,cityId)

    jsonDict = theCity.getOwmJsonInfo()
    latitude = jsonDict['coord']['lat']
    longitude = jsonDict['coord']['lon']
    if not cityName:
        cityName = jsonDict['name']
    country = jsonDict['sys']['country']
        
    #('contextBrokerName', 'mqttName', 'type', ['owmCathegory', 'owmField']) 

        
    static_attributes = [('Position', 'geo:point',"{},{}".format(latitude, longitude)), ('Countrycode', 'string', country), ('Name', 'string', cityName)]
    commands = []

    device = { "device_id" : "DevID37101{}".format(cityId), 
                "entity_name" : "DevEnt{}".format(cityId), 
                "entity_type" : "Device", 
                "transport" : "MQTT",
                "attributes" : [{ "object_id" : aId, "name" : aName, "type" : aType } for ((aId, aName, aType), _ ) in FIELD_MATCHES],
                "commands" : [{ "object_id" : aId, "name" : aName, "type" : aType } for aId, aName, aType in commands ],
                "static_attributes" : [{ "name" : aId, "type" : aName, "value" : aType } for aId, aName, aType in static_attributes ]  
            }

    deviceList = {"devices" : [device]}
            
    #print "request"
    #print deviceList
    response = requests.post(IOT_AGENT_URL, json = deviceList,
                    headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    r = response.json()
    #print "response"
    #print r #('{}: "{}"'.format(r['name'], r['message']))

    theCity.putIotJson(theCity.convertOwmToIot(jsonDict))    

    return theCity


if __name__ == '__main__':
    test = city(cityOwaId = 6940463, cityId = 'Muc', cityName = 'Munich')