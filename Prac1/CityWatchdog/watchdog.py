#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import logging
import time
import datetime
import re
import collections
import sched

try:
    import city_definitions
except:
    import sys
    sys.path.append('../Common')
    import city_definitions


class watchdog(object):
    """
    This class is inteted to monitor cities. Therefor it subscribes every city being monitored and stores the date times of the last update of each attribute.
    """
    MQTT_API_KEY = city_definitions.MQTT_API_KEY  # The apikey for using the MQTT API
    MQTT_SERVER = city_definitions.SERVER # The IP of the MQTT API 
    MQTT_PORT = city_definitions.MQTT_PORT # The Port of the MQTT API 
    DEVICE_BASISNAME = city_definitions.DEVICE_BASISNAME_MQTT # The first part of the names of Devices in MQTT API
    COMMANDS = dict() # However the commands 'AddCity' and 'RemoveCity' are added after the class because of some reasons 

    ATTRIBUTE_CITY_ERRORS = "CityErrors"
    ATTRIBUTE_CITY_ERRORS_MQTT = "ec"
    ATTRIBUTE_SENSOR_ERRORS = "SensorErrors:"   
    ATTRIBUTE_SENSOR_ERRORS_MQTT = "es"

    WATCHDOG_ATTRIBUTES = { name_mqtt: name_rest for ((name_mqtt, name_rest, _), _) in city_definitions.ATTRIBUTE_MATCHES}
    #WATCHDOG_ATTRIBUTES["er"] = "Doesnotexist" # Add not existing command for debug reasons
    
    COMBOUND_ATTRIBUT_LAST_NAME = "LastUpdate"
    COMBOUND_ATTRIBUT_MQTT_NAME = "MQTT"
    COMBOUND_ATTRIBUT_REST_NAME = "REST"

    TOPIC_CITIES = "/" + str(MQTT_API_KEY) + "/{}/attrs/#"
    TOPIC_CITIES_REGEX =  '/\d*/(\w*)/attrs/'
    
    def __init__(self, time_delta = 15 * 60, initial_cities = []):
        """
        Constructor of Watchdog
        """
        self.TIME_DELTA = datetime.timedelta(seconds = time_delta)
        self.device_id = watchdog.DEVICE_BASISNAME + "Watchdog" # the id of the watchdog in MQTT
        self.mqtt_client = mqtt.Client()
        self.topic_command = "/{}/{}/cmd".format(watchdog.MQTT_API_KEY, self.device_id) # topic to listen for getting commands
        self.topic_command_executed = "/{}/{}/cmdexe".format(watchdog.MQTT_API_KEY, self.device_id) # topic to puplish the results of processed commands
        self.logger = logging.getLogger(self.device_id)
        self.city_names_dict = dict()

        def on_connect(client, userdata, flags, rc):
            self.logger.info("MQTT client sucessfully connected with result code {}".format(rc))
            client.subscribe(self.topic_command)
            
            for city in initial_cities:
                self.add_city(city)
        
        def on_message(client, userdata, msg):
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
    
    def check_cities_forever(self, repeat_every_seconds = None):
        """
        triggers update in each given city every given time interval
        Keyword arguments:
        minutes -- time delay between two updates in minutes
        """
        if repeat_every_seconds == None:
            repeat_every_seconds = float(self.TIME_DELTA.total_seconds())

        the_scheduler = sched.scheduler(time.time, time.sleep)

        def do_check_cities(): 
            """
            triggers one update and enter a new time to scheduler
            """
            self.check_cities()
            the_scheduler.enter(repeat_every_seconds, 1, do_check_cities, ())

        # start every city at the beginning with an offset
        the_scheduler.enter(repeat_every_seconds, 1, do_check_cities, ())

        # start the scheduler to run forever
        the_scheduler.run()

    def check_cities(self):
        """
        checks if every sensor of every subscribed city is has been updated
        pushes the result of this checks in context broker

        every city with no update is a city_error
        every city with incomplete updates (not every sensor is a sensor_error)
        """
        now = datetime.datetime.now()

        # every city with a lack of update for a defined time
        city_errors = [ (city_mqtt_name , str(max(city_attributes.values())))
            for city_mqtt_name, city_attributes in self.city_names_dict.items() 
            if all(update_time + self.TIME_DELTA < now for update_time in city_attributes.values())]
        
        # everey sensors with a lack of update for a defined time in cities, wich got some updates in time
        sensor_errors = [(city_mqtt_name, attribute_name, str(update_time), watchdog.WATCHDOG_ATTRIBUTES[attribute_name])
            for city_mqtt_name, city_attributes in self.city_names_dict.items() if not all(update_time + self.TIME_DELTA < now for update_time in city_attributes.values())
            for attribute_name , update_time in city_attributes.items() if update_time + self.TIME_DELTA < now]
        
        city_errors_str   = str(city_errors  ).replace("'","").replace('(','[').replace(')',']') # This is a fast implemented workaround because compounds do not work
        sensor_errors_str = str(sensor_errors).replace("'","").replace('(','[').replace(')',']') # This is a fast implemented workaround because compounds do not work
        self.logger.info("Pushing following city errors: {}".format(city_errors_str))
        self.logger.info("Pushing following sensor errors: {}".format(sensor_errors_str))

        # The watchdog was intented to use compunds! since compounds do not work over mqtt and we don't have the time left to implement using rest, we push strings
        # With rest interface, we even could had used the metadata in this application instead of subscribtion
        self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs/ec", city_errors_str)
        self.mqtt_client.publish("/1234/DevID31701Watchdog/attrs/es", sensor_errors_str) 

        # If we had some LEDs, we would have implemented an errorboard with the raspy :)

        return True # how to check if it was successfull?
    
    def add_city(self, city_mqtt_name):
        '''
        Function to subscribe a new city and add the city for regular update checks
        Keyword arguments:
        city_mqtt_name -- the mqtt name of the city
        '''

        if city_mqtt_name not in self.city_names_dict:
            self.city_names_dict[city_mqtt_name] = { name : datetime.datetime.min for name in watchdog.WATCHDOG_ATTRIBUTES.keys() }
            self.mqtt_client.subscribe(watchdog.TOPIC_CITIES.format(city_mqtt_name))
            return True
        else:
            return False

    def remove_city(self, city_mqtt_name):
        '''
        Function to unsubscribe a registerd city and remove the city from regular update checks
        Keyword arguments:
        city_mqtt_name -- the mqtt name of the city
        '''
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
        '''
        Function for registering active attribute updates for a subscribed city
        Keyword arguments:
        city -- The mqtt name of city
        payload -- the dictionary with active attributs
        '''
        payload_dict = json.loads(payload.decode("utf-8"))
        self.logger.info('Registered update from "{}" for following attributs "{}"'.format(city, list(payload_dict.keys())))
        if city in self.city_names_dict:
            for attribute in payload_dict.keys():
                if attribute in self.city_names_dict[city]:
                    self.city_names_dict[city][attribute] = datetime.datetime.now()



watchdog.COMMANDS['AddCity'] =  watchdog.add_city
watchdog.COMMANDS['RemoveCity'] =  watchdog.remove_city



if __name__ is '__main__':
    logging.basicConfig(level=logging.INFO)
    w = watchdog(initial_cities = ['DevID31701MUC']);
    w.check_cities_forever(1)
