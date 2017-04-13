#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import requests
import json
import logging
import functools
import operator

import city_definitions

class city(object):
    """
    This class simulates weatherstations in cities. 
    Instead of measurement, the information is from OpenWeatherMap (which is real data). 
    One instance needs its own mqtt iot agent and does not know anything about context broker
    When calling the method update the city is pulling information from OpenWeatherMap, extracts the desired information and forwards it trough mqtt.
    """
    MQTT_API_KEY = city_definitions.MQTT_API_KEY  # The apikey for using the MQTT API
    OWM_KEY = city_definitions.OWM_KEY # The apikey for using the openweathermap API
    
    MQTT_SERVER = city_definitions.SERVER # The IP of the MQTT API 
    MQTT_PORT = city_definitions.MQTT_PORT # The Port of the MQTT API 
    DEVICE_BASISNAME = city_definitions.DEVICE_BASISNAME_MQTT # The first part of the names of Devices in MQTT API 

    # The list of active attributes consists of tuples. The tuple contain the name of the attribute in MQTT API
    #  and the the list of keys to enter the nested dictionary of openweathermap for getting the value
    ACTIVE_ATTRIBUTES = city_definitions.ACTIVE_ATTRIBUTES

    # The list of commands consists of tuples. The tuple contain the name of the attribute in context broker api (NGSIv2 not ready)
    #  and pointer to the function which should be called when the command is triggerd.
    COMMANDS = city_definitions.COMMANDS

    OWM_URL = 'http://api.openweathermap.org/data/2.5/weather?id={}&appid={}' # The URL of the openweathermap API

    def __init__(self, city_owm_id, iata):
        """
        Constructor of city
        Keyword arguments:
        cityOwmId -- the city id of openweathermap
        iata -- the IATA code of the city
        """
        self.city_owm_id = city_owm_id # The id of the city in openweathermap
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
        r = requests.get(city.OWM_URL.format(self.city_owm_id, city.OWM_KEY))
        return r.json() if 200 == r.status_code else None
    
    @classmethod
    def convert_owm_to_mqtt(cls, dict_owm_json):
        """
        Convert weather info being returned from openweathermap into the weather info which could be pushed 
        Keyword arguments:
        dict_owm_json -- Nested dictionaries with values of the weather of the city from openweathermap
        Returns:
        A dictionary with values which could be pushed to active attributes {attribute_id : value}
        """
        # this iterates trough all active attributes and extract the value of the json of openweathermap
        # the function reduce walks along the nested dictionary dict_owm_json with the help of the path of keys (path_owm)
        return { name_mqtt : functools.reduce(operator.getitem, path_owm, dict_owm_json) for name_mqtt, path_owm in cls.ACTIVE_ATTRIBUTES }

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
            except Exception as ex:
                self.logger.error(ex)
                return "Error in {}({}): {}".format(command_name,command_value, ex)
        
        # process every command if known. Normaly there is only one command being carried out.
        # create a json string of pairs of the name and the resultvalue of the command
        self.mqtt_client.publish(self.topic_command_executed, 
            json.dumps({command_name : tryApply(command_name, command_value) for command_name, command_value in dict_mqtt_json.items() if command_name in city.COMMANDS}))

    def __repr__(self):
        return str((self.city_owm_id, self.device_id))

    def __str__(self):
        return 'IOT Name = {}, OWA City ID = {}'.format(self.device_id, self.city_owm_id)