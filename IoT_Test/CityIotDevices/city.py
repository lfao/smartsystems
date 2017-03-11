#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import requests
import json
import logging
import functools
import operator

import commands

# This is a list of the active atributes of the iot devices
# One tuple consist of a tuple and a list
# ((object_id, object_name, type), [keylist])
# object_id -- the ID being used for MQTT communication
# object_name -- the name of the attribute in context broker (only used for creating an iot agent)
# type -- the type of the value being stored in this attribute (only used for creating an iot agent)
# keylist -- the list of keys to enter the nested dictionary of openweathermap for getting the value
ATTRIBUTE_MATCHES = [(('t', 'Temperatur', 'Kelvin'),[u'main', u'temp']), 
                     (('h', 'Humidity', '%'),[u'main', u'humidity']),
                     (('w', 'Windspeed', 'mph'),[u'wind',u'speed']),
                     (('p', 'Pressure', 'hPa'),[u'main',u'pressure']),
                     (('c', 'Clouds', '%'),[u'clouds',u'all'])]


# This is a list of the active atributes of the iot devices
# One tuple consist of a tuple and a list
# ((object_id, object_name, type), functionpointer)
# object_id -- the ID being should for MQTT communication if NGSIv2 would be finished
# object_name -- the name of the command in context broker (only used for creating an iot agent)
# type -- the type of the value assotiated to this command (only used for creating an iot agent)
# functionpointer -- a function wich should be carried out when command is called.
#                    the function should be in in the folowing signature
# retvalue = function(cityObject, paramvalue)
# retvalue -- the value being pushed to context broker after finishing this command (use dummy if not required)
# cityObject -- the city which is ordered to carry out the commmand (use dummy if not required)
# paramvalue -- the value being handed over by context broker when triggering the command (use dummy if not required)
COMMAND_MATCHES = [(('l','CpuLoad', '%'), commands.getCpuLoad), (('u', 'UpdateCount','int'), commands.getUpdateCount)]

SERVER = '130.206.112.29'  # The IP of the MQTT, IOT and the Context Broker API

class city(object):
    """
    to Map OpenWeatherMap to MQTT.
    Does not know anything about context broker
    """
    MQTT_API_KEY = 1234  # The apikey for using the MQTT API
    OWM_KEY = 'abacdae90c8800879db8e02327da1f92' # The apikey for using the openweathermap API
    OWM_URL = 'http://api.openweathermap.org/data/2.5/weather?id={}&appid={}' # The URL of the openweathermap API
    MQTT_SERVER = SERVER # The IP of the MQTT API 
    MQTT_PORT = 1883 # The Port of the MQTT API 
    DEVICE_BASISNAME = 'DevID37101' # The first part of the names of Devices in MQTT API 

    # The list of active attributes consists of tuples. The tuple contain the name of the attribute in MQTT API
    #  and the the list of keys to enter the nested dictionary of openweathermap for getting the value
    ACTIVE_ATTRIBUTES = [(iotName, owmPath) for ((iotName, _, _), owmPath) in ATTRIBUTE_MATCHES] 

    # The list of commands consists of tuples. The tuple contain the name of the attribute in context broker api (NGSIv2 not ready)
    #  and pointer to the function which should be called when the command is triggerd.
    COMMANDS = { key : value for ((_ , key , _ ), value) in COMMAND_MATCHES }


    def __init__(self, cityOwmId, iata):
        """
        Constructor of city
        Keyword arguments:
        cityOwmId -- the city id of openweathermap
        iata -- the IATA code of the city
        """
        self.cityOwaId = cityOwmId # The id of the city in openweathermap
        self.deviceId = city.DEVICE_BASISNAME + iata # the id of the city in MQTT
        #self.iata = iata
        self.mqttClient = mqtt.Client()
        self.commandTopic = "/{}/{}/cmd".format(city.MQTT_API_KEY, self.deviceId) # topic to listen for getting commands
        self.commandExecutedTopic = "/{}/{}/cmdexe".format(city.MQTT_API_KEY, self.deviceId) # topic to puplish the results of processed commands
        self.logger = logging.getLogger(iata)
        self.updateCounter = 0

        def on_connect(client, userdata, flags, rc):
            self.logger.info("MQTT client of city {} sucessfully connected with result code {}".format(iata, rc))
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
        """
        Get the weather info of your city from openweathermap
        Returns:
        Nested dictionaries with values of the weather of the city
        """
        r = requests.get(city.OWM_URL.format(self.cityOwaId, city.OWM_KEY))
        return r.json() if 200 == r.status_code else None
    
    @staticmethod
    def convertOwmToIot(jsonDict):
        """
        Convert weather info being returned from openweathermap into the weather info which could be pushed 
        Keyword arguments:
        jsonDict -- Nested dictionaries with values of the weather of the city from openweathermap
        Returns:
        A dictionary with values which could be pushed to active attributes {attribute_id : value}
        """
        # this iterates trough all active attributes and extract the value of the json of openweathermap
        # the function reduce walks along the nested dictionary jsonDict with the help of the path of keys (owmPath)
        return { iotName : functools.reduce(operator.getitem, owmPath, jsonDict) for iotName, owmPath in city.ACTIVE_ATTRIBUTES }

    def putIotJson(self, jsonDict):
        """
        Put weather info via MQTT to IOT agent
        Keyword arguments:
        jsonDict -- A dictionary with values which could be pushed to active attributes {attribute_id : value}
        Returns:
        A value wich indicates wether it was successful
        """
        self.updateCounter += 1
        self.mqttClient.publish("/{}/{}/attrs/".format(city.MQTT_API_KEY, self.deviceId), json.dumps(jsonDict))
        return True # how to check if it was successfull?

    def update(self):
        """
        Get weather info from openweathermap, convert it and put it via MQTT to IOT agent
        Returns:
        A value wich indicates wether it was successful
        """
        self.logger.info("Updating")
        jsonDict = self.getOwmJsonInfo()
        return jsonDict and self.putIotJson(city.convertOwmToIot(jsonDict))
    
    def doCommand(self,command):
        """
        Function wich should be called if a command is sent to the iot device.
        It selects the assigned function and carry it out.
        Keyword arguments:
        command -- The json string with the command being sent to the iot device.
        """
        jsonload = json.loads(command.decode("utf-8"))
        self.logger.debug(jsonload)

        def tryApply(commandName, commandValue):
            """
            This function calls a function being contained in the COMMANDS
            All exceptions will be catched.
            Keyword arguments:
            commandName -- The name of the command being sent to the iot device.
            commandValue -- The value of the command being sent to the iot device.
            Returns:
            The value being returned by acting out the command.
            """

            self.logger.info("Running Command: {}({})".format(commandName,commandValue))
            try:
                retval = city.COMMANDS[commandName](self, commandValue);
                self.logger.info("Result: {}".format(retval))
                return retval
            except ex:
                self.logger.error(ex)
                return "Error in {}({}): {}".format(commandName,commandValue, ex)
        
        # process every command if known. Normaly there is only one command being carried out.
        # create a json string of pairs of the name and the resultvalue of the command
        self.mqttClient.publish(self.commandExecutedTopic, 
            json.dumps({commandName : tryApply(commandName, commandValue) for commandName, commandValue in jsonload.items() if commandName in city.COMMANDS}))

    def __repr__(self):
        return str((self.cityOwaId, self.deviceId))

    def __str__(self):
        return 'IOT Name = {}, OWA City ID = {}'.format(self.deviceId, self.cityOwaId)


def createCity(cityOwaId, cityId, cityName = None):
    """
    Create a city object and the assotiated IOT agent.
    Keyword arguments:
    cityOwmId -- the city id of openweathermap
    iata -- the IATA code of the city
    cityName (optional) -- The name of the city being stored in iot agent. Default is the name being stored in openweathermap.
    Returns:
    The created city object
    """
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


    # get some information for the static attributes associated to this city from the from openweathermap
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
                "attributes" : [{ "object_id" : aId, "name" : aName, "type" : aType } for ((aId, aName, aType), _ ) in ATTRIBUTE_MATCHES],
                "commands" : [{ "object_id" : aId, "name" : aName, "type" : aType } for ((aId, aName, aType) , _ ) in COMMAND_MATCHES],
                "static_attributes" : [{ "name" : aId, "type" : aName, "value" : aType } for aId, aName, aType in static_attributes]  
            }

    deviceList = {"devices" : [device]}

    # check wether city iot agent already exists. Delete if yes.
    response = requests.get(IOT_AGENT_URL + iotAgentId, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        logger.warning ("{}: IOT agent does already exist. Deleting IOT agent!".format(cityId))
        response = requests.delete(IOT_AGENT_URL + iotAgentId, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
        if 204 == response.status_code:
            logger.info ("{}: IOT agent successfully deleted".format(cityId))
        else:
            logger.error("{}: IOT agent could not be deleted. Http error code: {}".format(cityId, response.status_code)) 


    # check wether city entity already exists. Delete if yes and REPLACE_ENTITY is true.
    response = requests.get(CONTEXTBROKER_URL + iotAgentName, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        if REPLACE_ENTITY:
            logger.warning ("{}: Entity does already exist. Deleting entity!".format(cityId))
            response = requests.delete(CONTEXTBROKER_URL + iotAgentName, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
            if 204 == response.status_code:
                logger.info ("{}: Entity successfully deleted".format(cityId))
            else:
                logger.error("{}: Entity could not be deleted. Http error code: {}".format(cityId, response.status_code)) 
        else:
            logger.info ("{}: Entity does already exist.".format(cityId))


    # create the iot Agent
    logger.info("{}: Create IOT agent.".format(cityId))
    response = requests.post(IOT_AGENT_URL, json = deviceList,
                    headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 201 == response.status_code:
        logger.info ("{}: IOT agent has been created!".format(cityId))
    else:
        logger.error("{}: IOT agent could not be created. Http error code: {}".format(cityId, response.status_code)) 

    # update the context broker
    logger.info("{}: Update city".format(cityId))
    if theCity.putIotJson(city.convertOwmToIot(jsonDict)):
        logger.info("{}: Update sucessfully finished".format(cityId))
    else:
         logger.error("{}: city could not be updated".format(cityId))

    return theCity

def getCityOwmIdAndIata(name):
    """
    Gets the city id of openweathermap and the IATA code of the city
    Returns a tuple of:
    cityOwmId,iata -- the city id of openweathermap, the IATA code of the city
    """
    logger = logging.getLogger(__name__)
    
    # get the IATA code
    IATACODES_KEY = '32320f7b-58ee-46a7-847e-468b451eb083'
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(name, city.OWM_KEY))
    cityOwaId = r.json()['id']
    owaName = r.json()['name']

    # get the city id of openweathermap
    r = requests.get('https://iatacodes.org/api/v6/autocomplete?query={}&api_key={}'.format(name, IATACODES_KEY))
    cities = r.json()['response']['cities']
    cityId = cities[0]['code']
    iataName = cities[0]['name']
    logger.info ('IATA: {}, OWM_ID: {},'.format(cityOwaId,cityId))
    if (not(name == owaName == iataName)):
        logger.warning('The names are different! Name: {}, OWM_Name: {}, IATA_Name: {}'.format (name, owaName, iataName))
    return (cityOwaId,cityId)

def createCityByName(name):
    """
    Create a city object and the assotiated IOT agent.
    Keyword arguments:
    cityName -- The name of the city being stored in iot agent and found it openweathermap and in IATA database.
    Returns:
    The created city object
    """
    (cityOwmId,cityId) = getCityOwmIdAndIata(name)
    return createCity(cityOwmId, cityId, name)
    
def getCityByName(name):
    """
    Create a city object. The IOT agent must already exist.
    Keyword arguments:
    cityName -- The name of the city being stored in iot agent and found it openweathermap and in IATA database.
    Returns:
    The created city object
    """
    return city(*getCityOwmIdAndIata(name))