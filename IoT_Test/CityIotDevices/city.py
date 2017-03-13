#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import requests
import json
import logging
import functools
import operator

import city_commands

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
COMMAND_MATCHES = [(('l','CpuLoad', '%'), city_commands.get_cpu_load), (('u', 'UpdateCount','int'), city_commands.get_update_count)]

SERVER = '130.206.112.29'  # The IP of the MQTT, IOT and the Context Broker API

class city(object):
    """
    This class simulates weatherstations in cities. 
    Instead of measurement, the information is from OpenWeatherMap (which is real data). 
    One instance needs its own mqtt iot agent and does not know anything about context broker
    When calling the method update the city is pulling information from OpenWeatherMap, extracts the desired information and forwards it trough mqtt.
    """
    MQTT_API_KEY = 1234  # The apikey for using the MQTT API
    OWM_KEY = 'abacdae90c8800879db8e02327da1f92' # The apikey for using the openweathermap API
    OWM_URL = 'http://api.openweathermap.org/data/2.5/weather?id={}&appid={}' # The URL of the openweathermap API
    MQTT_SERVER = SERVER # The IP of the MQTT API 
    MQTT_PORT = 1883 # The Port of the MQTT API 
    DEVICE_BASISNAME = 'DevID37101' # The first part of the names of Devices in MQTT API 

    # The list of active attributes consists of tuples. The tuple contain the name of the attribute in MQTT API
    #  and the the list of keys to enter the nested dictionary of openweathermap for getting the value
    ACTIVE_ATTRIBUTES = [(name_mqtt, path_owm) for ((name_mqtt, _, _), path_owm) in ATTRIBUTE_MATCHES] 

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
        self.city_owa_id = cityOwmId # The id of the city in openweathermap
        self.device_id = city.DEVICE_BASISNAME + iata # the id of the city in MQTT
        #self.iata = iata
        self.mqtt_client = mqtt.Client()
        self.topic_command = "/{}/{}/cmd".format(city.MQTT_API_KEY, self.device_id) # topic to listen for getting commands
        self.topic_command_executed = "/{}/{}/cmdexe".format(city.MQTT_API_KEY, self.device_id) # topic to puplish the results of processed commands
        self.logger = logging.getLogger(iata)
        self.update_counter = 0

        def on_connect(client, userdata, flags, rc):
            self.logger.info("MQTT client of city {} sucessfully connected with result code {}".format(iata, rc))
            client.subscribe(self.topic_command)
        
        def on_message(client, userdata, msg):
            self.logger.info("Topic: {}, Payload: {}".format(msg.topic, msg.payload))
            if(msg.topic == self.topic_command):
                self.do_command(msg.payload)

        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        self.mqtt_client.connect(city.MQTT_SERVER, city.MQTT_PORT) 
        self.mqtt_client.loop_start();       
    
    def get_owm_json(self):
        """
        Get the weather info of your city from openweathermap
        Returns:
        Nested dictionaries with values of the weather of the city
        """
        r = requests.get(city.OWM_URL.format(self.city_owa_id, city.OWM_KEY))
        return r.json() if 200 == r.status_code else None
    
    @staticmethod
    def convert_owm_to_mqtt(dict_owm_json):
        """
        Convert weather info being returned from openweathermap into the weather info which could be pushed 
        Keyword arguments:
        dict_owm_json -- Nested dictionaries with values of the weather of the city from openweathermap
        Returns:
        A dictionary with values which could be pushed to active attributes {attribute_id : value}
        """
        # this iterates trough all active attributes and extract the value of the json of openweathermap
        # the function reduce walks along the nested dictionary dict_owm_json with the help of the path of keys (path_owm)
        return { name_mqtt : functools.reduce(operator.getitem, path_owm, dict_owm_json) for name_mqtt, path_owm in city.ACTIVE_ATTRIBUTES }

    def put_mqtt_json(self, dict_mqtt_json):
        """
        Put weather info via MQTT to IOT agent
        Keyword arguments:
        dict_owm_json -- A dictionary with values which could be pushed to active attributes {attribute_id : value}
        Returns:
        A value wich indicates wether it was successful
        """
        self.update_counter += 1
        self.mqtt_client.publish("/{}/{}/attrs/".format(city.MQTT_API_KEY, self.device_id), json.dumps(dict_mqtt_json))
        return True # how to check if it was successfull?

    def update(self):
        """
        Get weather info from openweathermap, convert it and put it via MQTT to IOT agent
        Returns:
        A value wich indicates wether it was successful
        """
        self.logger.info("Updating")
        dict_owm_json = self.get_owm_json()
        return dict_owm_json and self.put_mqtt_json(city.convert_owm_to_mqtt(dict_owm_json))
    
    def do_command(self,command):
        """
        Function wich should be called if a command is sent to the iot device.
        It selects the assigned function and carry it out.
        Keyword arguments:
        command -- The json string with the command being sent to the iot device.
        """
        dict_mqtt_json = json.loads(command.decode("utf-8"))
        self.logger.debug(dict_mqtt_json)

        def tryApply(command_name, command_value):
            """
            This function calls a function being contained in the COMMANDS
            All exceptions will be catched.
            Keyword arguments:
            command_name -- The name of the command being sent to the iot device.
            command_value -- The value of the command being sent to the iot device.
            Returns:
            The value being returned by acting out the command.
            """

            self.logger.info("Running Command: {}({})".format(command_name,command_value))
            try:
                retval = city.COMMANDS[command_name](self, command_value);
                self.logger.info("Result: {}".format(retval))
                return retval
            except ex:
                self.logger.error(ex)
                return "Error in {}({}): {}".format(command_name,command_value, ex)
        
        # process every command if known. Normaly there is only one command being carried out.
        # create a json string of pairs of the name and the resultvalue of the command
        self.mqtt_client.publish(self.topic_command_executed, 
            json.dumps({command_name : tryApply(command_name, command_value) for command_name, command_value in dict_mqtt_json.items() if command_name in city.COMMANDS}))

    def __repr__(self):
        return str((self.city_owa_id, self.device_id))

    def __str__(self):
        return 'IOT Name = {}, OWA City ID = {}'.format(self.device_id, self.city_owa_id)


def createCity(owa_id, iata, city_name = None):
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

    theCity = city(owa_id,iata)


    # get some information for the static attributes associated to this city from the from openweathermap
    dict_owm_json = theCity.get_owm_json()
    latitude = dict_owm_json['coord']['lat']
    longitude = dict_owm_json['coord']['lon']
    if not city_name:
        city_name = dict_owm_json['name']
    country = dict_owm_json['sys']['country']
        
    static_attributes = [('Position', 'geo:point',"{},{}".format(latitude, longitude)), ('Countrycode', 'string', country), ('Name', 'string', city_name)]
    name_contextbroker =  "DevEnt{}".format(iata)
    name_mqtt = "DevID37101{}".format(iata)
    
    device = { "device_id" : name_mqtt, 
                "entity_name" : name_contextbroker, 
                "entity_type" : "Device", 
                "transport" : "MQTT",
                "attributes" : [{ "object_id" : a_id, "name" : a_name, "type" : a_type } for ((a_id, a_name, a_type), _ ) in ATTRIBUTE_MATCHES],
                "commands" : [{ "object_id" : a_id, "name" : a_name, "type" : a_type } for ((a_id, a_name, a_type) , _ ) in COMMAND_MATCHES],
                "static_attributes" : [{ "name" : a_id, "type" : a_name, "value" : a_type } for a_id, a_name, a_type in static_attributes]  
            }

    device_list = {"devices" : [device]}

    # check wether city iot agent already exists. Delete if yes.
    response = requests.get(IOT_AGENT_URL + name_mqtt, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        logger.warning ("{}: IOT agent does already exist. Deleting IOT agent!".format(iata))
        response = requests.delete(IOT_AGENT_URL + name_mqtt, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
        if 204 == response.status_code:
            logger.info ("{}: IOT agent successfully deleted".format(iata))
        else:
            logger.error("{}: IOT agent could not be deleted. Http error code: {}".format(iata, response.status_code)) 


    # check wether city entity already exists. Delete if yes and REPLACE_ENTITY is true.
    response = requests.get(CONTEXTBROKER_URL + name_contextbroker, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        if REPLACE_ENTITY:
            logger.warning ("{}: Entity does already exist. Deleting entity!".format(iata))
            response = requests.delete(CONTEXTBROKER_URL + name_contextbroker, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
            if 204 == response.status_code:
                logger.info ("{}: Entity successfully deleted".format(iata))
            else:
                logger.error("{}: Entity could not be deleted. Http error code: {}".format(iata, response.status_code)) 
        else:
            logger.info ("{}: Entity does already exist.".format(iata))


    # create the iot Agent
    logger.info("{}: Create IOT agent.".format(iata))
    response = requests.post(IOT_AGENT_URL, json = device_list,
                    headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 201 == response.status_code:
        logger.info ("{}: IOT agent has been created!".format(iata))
    else:
        logger.error("{}: IOT agent could not be created. Http error code: {}".format(iata, response.status_code)) 

    # update the context broker
    logger.info("{}: Update city".format(iata))
    if theCity.put_mqtt_json(city.convert_owm_to_mqtt(dict_owm_json)):
        logger.info("{}: Update sucessfully finished".format(iata))
    else:
         logger.error("{}: city could not be updated".format(iata))

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
    owa_id = r.json()['id']
    owaName = r.json()['name']

    # get the city id of openweathermap
    r = requests.get('https://iatacodes.org/api/v6/autocomplete?query={}&api_key={}'.format(name, IATACODES_KEY))
    cities = r.json()['response']['cities']
    iata = cities[0]['code']
    iataName = cities[0]['name']
    logger.info ('IATA: {}, OWM_ID: {},'.format(owa_id,iata))
    if (not(name == owaName == iataName)):
        logger.warning('The names are different! Name: {}, OWM_Name: {}, IATA_Name: {}'.format (name, owaName, iataName))
    return (owa_id,iata)

def createCityByName(name):
    """
    Create a city object and the assotiated IOT agent.
    Keyword arguments:
    cityName -- The name of the city being stored in iot agent and found it openweathermap and in IATA database.
    Returns:
    The created city object
    """
    (cityOwmId,iata) = getCityOwmIdAndIata(name)
    return createCity(cityOwmId, iata, name)
    
def getCityByName(name):
    """
    Create a city object. The IOT agent must already exist.
    Keyword arguments:
    cityName -- The name of the city being stored in iot agent and found it openweathermap and in IATA database.
    Returns:
    The created city object
    """
    return city(*getCityOwmIdAndIata(name))