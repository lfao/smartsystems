#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import logging
import time
import datetime
import re
import collections

try:
    import city_definitions
except:
    import sys
    sys.path.append('../Common')
    import city_definitions


class watchdog(object):
    """
    This class ...
    """
    MQTT_API_KEY = city_definitions.MQTT_API_KEY  # The apikey for using the MQTT API
    MQTT_SERVER = city_definitions.SERVER # The IP of the MQTT API 
    MQTT_PORT = city_definitions.MQTT_PORT # The Port of the MQTT API 
    DEVICE_BASISNAME = city_definitions.DEVICE_BASISNAME_MQTT # The first part of the names of Devices in MQTT API
    COMMANDS = dict()
    
    TIME_DELTA = datetime.timedelta(minutes = 15)

    ATTRIBUTE_CITY_ERRORS = "CityErrors"
    ATTRIBUTE_CITY_ERRORS_MQTT = "ec"
    ATTRIBUTE_SENSOR_ERRORS = "SensorErrors:"   
    ATTRIBUTE_SENSOR_ERRORS_MQTT = "es"

    WATCHDOG_ATTRIBUTES = { name_mqtt: name_rest for ((name_mqtt, name_rest, _), _) in city_definitions.ATTRIBUTE_MATCHES}
    
    
    COMBOUND_ATTRIBUT_LAST_NAME = "LastUpdate"
    COMBOUND_ATTRIBUT_MQTT_NAME = "MQTT"
    COMBOUND_ATTRIBUT_REST_NAME = "REST"

    TOPIC_CITIES = "/" + str(MQTT_API_KEY) + "/{}/attrs/#"
    TOPIC_CITIES_REGEX =  '/\d*/(\w*)/attrs/'

    CITIES = ['DevID31701MUC']    
    
    def __init__(self):
        """
        Constructor of Watchdog
        """
       
        self.device_id = watchdog.DEVICE_BASISNAME + "Watchdog" # the id of the watchdog in MQTT
        self.mqtt_client = mqtt.Client()
        self.topic_command = "/{}/{}/cmd".format(watchdog.MQTT_API_KEY, self.device_id) # topic to listen for getting commands
        self.topic_command_executed = "/{}/{}/cmdexe".format(watchdog.MQTT_API_KEY, self.device_id) # topic to puplish the results of processed commands
        self.logger = logging.getLogger(__name__)
        self.city_names_dict = dict()
        def on_connect(client, userdata, flags, rc):
            self.logger.info("MQTT client sucessfully connected with result code {}".format(rc))
            client.subscribe(self.topic_command)
            
            for city in watchdog.CITIES:
                self.add_city(city)
        
        def on_message(client, userdata, msg):
            print (msg.topic)
            self.logger.info("Topic: {}, Payload: {}".format(msg.topic, msg.payload))
            if(msg.topic == self.topic_command):
                self.do_command(msg.payload)
            else:
                #
                match = re.match(watchdog.TOPIC_CITIES_REGEX, msg.topic)
                if match:
                    self.register_update(match.groups()[0], msg.payload)

        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        self.mqtt_client.connect(watchdog.MQTT_SERVER, watchdog.MQTT_PORT) 
        self.mqtt_client.loop_start()      

   
    def update(self):
        """

        """
        now = datetime.datetime.now()
        city_errors = { city_mqtt_name : str(max(city_attributes.values()))
            for city_mqtt_name, city_attributes in self.city_names_dict.items() 
            if all(update_time + watchdog.TIME_DELTA < now for update_time in city_attributes.values())}
        
        sensor_errors = [{ COMBOUND_CITY_NAME : city_mqtt_name, COMBOUND_ATTRIBUT_LAST_UPDATE : str(update_time),
            COMBOUND_ATTRIBUT_REST_NAME : watchdog.WATCHDOG_ATTRIBUTES[attribute_name], COMBOUND_ATTRIBUT_MQTT_NAME : attribute_name } 
            for city_mqtt_name, city_attributes in self.city_names_dict.items() if city_mqtt_name not in city_errors
            for attribute_name , update_time in city_attributes if update_time + watchdog.TIME_DELTA < now]
        
        #print (self.city_names_dict)
        
        #sensor_errors = [{"adf" : 2}, {"asdf" : 3}]

        #print (json.dumps(city_errors))
        #print (json.dumps(sensor_errors))
        
        #self.mqtt_client.publish("/{}/{}/attrs/{}".format(watchdog.MQTT_API_KEY, self.device_id, watchdog.ATTRIBUTE_CITY_ERRORS_MQTT), json.dumps(city_errors))
        #self.mqtt_client.publish("/{}/{}/attrs/{}".format(watchdog.MQTT_API_KEY, self.device_id, watchdog.ATTRIBUTE_SENSOR_ERRORS_MQTT), json.dumps(sensor_errors))
        #self.mqtt_client.publish("/{}/{}/attrs".format(watchdog.MQTT_API_KEY, self.device_id), json.dumps({watchdog.ATTRIBUTE_SENSOR_ERRORS_MQTT : sensor_errors}))
        
        #self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs/es", '{3 : 4}')
        self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs/es", '{3 : 4')
        #self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs/es", '{5 : 4}')
        #self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs/es", 'asdf')
        self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs", '{"ec": replace }') #{"left": 4, "right" : 5}
        print (json.dumps({watchdog.ATTRIBUTE_SENSOR_ERRORS_MQTT : "ASDF"}))
        return True # how to check if it was successfull?
    
    def add_city(self, city_mqtt_name):
        if city_mqtt_name not in self.city_names_dict:
            self.city_names_dict[city_mqtt_name] = { name : datetime.datetime.min for name in watchdog.WATCHDOG_ATTRIBUTES.keys() }
            self.mqtt_client.subscribe(watchdog.TOPIC_CITIES.format(city_mqtt_name))
            return True
        else:
            return False

    def remove_city(self, city_mqtt_name):
        if city_mqtt_name in self.city_names_dict:
            self.city_names_dict.pop(city_mqtt_name)
            self.mqtt_client.unsubscribe(watchdog.TOPIC_CITIES.format(city_mqtt_name))
            return True
        else:
            return False

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
                retval = watchdog.COMMANDS[command_name](self, command_value);
                self.logger.info("Result: {}".format(retval))
                return retval
            except Exception as ex:
                self.logger.error(ex)
                return "Error in {}({}): {}".format(command_name,command_value, ex)
        
        # process every command if known. Normaly there is only one command being carried out.
        # create a json string of pairs of the name and the resultvalue of the command
        self.mqtt_client.publish(self.topic_command_executed, 
            json.dumps({command_name : tryApply(command_name, command_value) for command_name, command_value in dict_mqtt_json.items() if command_name in watchdog.COMMANDS}))

    def register_update(self, city, payload):
        print(city)
        payload_dict = json.loads(payload.decode("utf-8"))
        if city in self.city_names_dict:
            for attribute in payload_dict.keys():
                if attribute in self.city_names_dict[city]:
                    self.city_names_dict[city][attribute] = datetime.datetime.now()



watchdog.COMMANDS['AddCity'] =  watchdog.add_city
watchdog.COMMANDS['RemoveCity'] =  watchdog.remove_city
#watchdog.COMMAND_MATCHES.append( (('a','AddCity', 'Name'), watchdog.add_city))
#watchdog.COMMAND_MATCHES.append( (('r','RemoveCity', 'Name'), watchdog.remove_city))

if __name__ is '__main__':
    import time
    w = watchdog();
    while True:
        w.update()
        time.sleep(15 * 60)