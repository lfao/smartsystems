#from __future__ import print_function
#from __future__ import unicode_literals
import paho.mqtt.client as mqtt
import requests
import functools
import operator
import json
import commands
import logging

FIELD_MATCHES = [(('t', 'Temperatur', 'Kelvin'),[u'main', u'temp']), 
                (('h', 'Humidity', '%'),[u'main', u'humidity']),
                (('w', 'Windspeed', 'mph'),[u'wind',u'speed']),
                (('p', 'Pressure', 'hPa'),[u'main',u'pressure']),
                (('c', 'Clouds', '%'),[u'clouds',u'all'])]

COMMAND_MATCHES = [(('l','CpuLoad', 'int'), commands.getCpuLoad)]

SERVER = '130.206.112.29' 

class city(object):
    """Class to Map OpenWeatherMap to MQTT"""
    IOT_API_KEY = 1234
    OWM_KEY = 'abacdae90c8800879db8e02327da1f92'
    OWM_URL = 'http://api.openweathermap.org/data/2.5/weather?id={}&appid={}'
    ACTIVE_ATTRIBUTES = [(iotName, owmPath) for ((iotName, _, _), owmPath) in FIELD_MATCHES]
    COMMANDS = { key : value for ((_ , key , _ ), value) in COMMAND_MATCHES }
    MQTT_SERVER = SERVER
    MQTT_PORT = 1883
    DEVICE_BASISNAME = 'DevID37101'

    def __init__(self, cityOwaId, cityId):
        self.cityOwaId = cityOwaId
        self.deviceId = city.DEVICE_BASISNAME + cityId
        self.mqttClient = mqtt.Client()
        self.commandTopic = "/{}/{}/cmd".format(city.IOT_API_KEY, self.deviceId)
        self.commandExecutedTopic = "/{}/{}/cmdexe".format(city.IOT_API_KEY, self.deviceId)
        self.logger = logging.getLogger(cityId)

        def on_connect(client, userdata, flags, rc):
            self.logger.info("MQTT client of city {} sucessfully connected with result code {}".format(cityId, rc))
            client.subscribe(self.commandTopic)
        
        def on_message(client, userdata, msg):
            self.logger.info("Topic: {}, Payload: {}".format(msg.topic, msg.payload))
            if(msg.topic == self.commandTopic):
                self.doCommand(msg.payload)

        self.mqttClient.on_connect = on_connect
        self.mqttClient.on_message = on_message
        self.mqttClient.connect(city.MQTT_SERVER, city.MQTT_PORT) 
        self.mqttClient.loop_start();       

    def getOwmJsonInfo(self):
        r = requests.get(city.OWM_URL.format(self.cityOwaId, city.OWM_KEY))
        return r.json() if 200 == r.status_code else None
    
    @staticmethod
    def convertOwmToIot(jsonDict):
        return { iotName : functools.reduce(operator.getitem, owmPath, jsonDict) for iotName, owmPath in city.ACTIVE_ATTRIBUTES }

    def putIotJson(self, jsonDict):
        self.mqttClient.publish("/{}/{}/attrs/".format(city.IOT_API_KEY, self.deviceId), json.dumps(jsonDict))
        return True # how to check if it was successfull?

    def update(self):
        self.logger.info("Updating")
        jsonDict = self.getOwmJsonInfo()
        return jsonDict and self.putIotJson(city.convertOwmToIot(jsonDict))
    
    def doCommand(self,command):
        jsonload = json.loads(command.decode("utf-8"))
        self.logger.debug(jsonload)

        def tryApply(commandName, commandValue):
            self.logger.info("Running Command: {}({})".format(commandName,commandValue))
            try:
                retval = city.COMMANDS[commandName](commandValue);
                self.logger.info("Result: {}".format(retval))
                return retval
            except ex:
                self.logger.error(ex)
                return "Error in {}({}): {}".format(commandName,commandValue, ex)
        
        self.mqttClient.publish(self.commandExecutedTopic, 
            json.dumps({commandName : tryApply(commandName, commandValue) for commandName, commandValue in jsonload.items() if commandName in city.COMMANDS}))

    def __repr__(self):
        return str((self.cityOwaId, self.deviceId))

    def __str__(self):
        return 'IOT Name = {}, OWA City ID = {}'.format(self.deviceId, self.cityOwaId)

def createCity(cityOwaId, cityId, cityName = None):
    REPLACE_ENTITY = True
    FIWARE_SERVICE_PATH = '/environment'
    FIWARE_SERVICE = 'icai31701'
    IOT_SERVER = SERVER
    IOT_PORT = 5050
    CONTEXTBROKER_SERVER = SERVER
    CONTEXTBROKER_PORT = 1026
    IOT_AGENT_URL = 'http://{}:{}/iot/devices/'.format(IOT_SERVER, IOT_PORT)
    CONTEXTBROKER_URL = 'http://{}:{}/v2/entities/'.format(CONTEXTBROKER_SERVER,CONTEXTBROKER_PORT)
    
    logger = logging.getLogger(__name__)

    theCity = city(cityOwaId,cityId)

    jsonDict = theCity.getOwmJsonInfo()
    latitude = jsonDict['coord']['lat']
    longitude = jsonDict['coord']['lon']
    if not cityName:
        cityName = jsonDict['name']
    country = jsonDict['sys']['country']
        
    static_attributes = [('Position', 'geo:point',"{},{}".format(latitude, longitude)), ('Countrycode', 'string', country), ('Name', 'string', cityName)]
    iotAgentName =  "DevEnt{}".format(cityId)
    iotAgentId = "DevID37101{}".format(cityId)
    
    device = { "device_id" : iotAgentId, 
                "entity_name" : iotAgentName, 
                "entity_type" : "Device", 
                "transport" : "MQTT",
                "attributes" : [{ "object_id" : aId, "name" : aName, "type" : aType } for ((aId, aName, aType), _ ) in FIELD_MATCHES],
                "commands" : [{ "object_id" : aId, "name" : aName, "type" : aType } for ((aId, aName, aType) , _ ) in COMMAND_MATCHES],
                "static_attributes" : [{ "name" : aId, "type" : aName, "value" : aType } for aId, aName, aType in static_attributes]  
            }

    deviceList = {"devices" : [device]}

    response = requests.get(IOT_AGENT_URL + iotAgentId, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        logger.info ("{}: IOT agent does already exist. Deleting IOT agent!".format(cityId))
        response = requests.delete(IOT_AGENT_URL + iotAgentId, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
        if 204 == response.status_code:
            logger.info ("{}: IOT agent successfully deleted".format(cityId))
        else:
            logger.error("{}: IOT agent could not be deleted. Http error code: {}".format(cityId, response.status_code)) 


    response = requests.get(CONTEXTBROKER_URL + iotAgentName, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        if REPLACE_ENTITY:
            logger.info ("{}: Entity does already exist. Deleting entity!".format(cityId))
            response = requests.delete(CONTEXTBROKER_URL + iotAgentName, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
            if 204 == response.status_code:
                logger.info ("{}: Entity successfully deleted".format(cityId))
            else:
                logger.error("{}: Entity could not be deleted. Http error code: {}".format(cityId, response.status_code)) 
        else:
            logger.info ("{}: Entity does already exist.".format(cityId))



    logger.info("{}: Create IOT agent.".format(cityId))
    response = requests.post(IOT_AGENT_URL, json = deviceList,
                    headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 201 == response.status_code:
        logger.info ("{}: IOT agent has been created!".format(cityId))
    else:
        logger.error("{}: IOT agent could not be created. Http error code: {}".format(cityId, response.status_code)) 

    logger.info("{}: Update city".format(cityId))
    if theCity.putIotJson(city.convertOwmToIot(jsonDict)):
        logger.info("{}: Update sucessfully finished".format(cityId))
    else:
         logger.error("{}: city could not be updated".format(cityId))

    return theCity


if __name__ == '__main__':
    test = city(cityOwaId = 6940463, cityId = 'Muc')