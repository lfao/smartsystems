#!/usr/bin/env python3

import city_commands

#common defintions

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
USER = '37101'

## Definitions for cities only
MQTT_API_KEY = 1234  # The apikey for using the MQTT API
OWM_KEY = 'abacdae90c8800879db8e02327da1f92' # The apikey for using the openweathermap API
MQTT_SERVER = SERVER # The IP of the MQTT API 
MQTT_PORT = 1883 # The Port of the MQTT API 
DEVICE_BASISNAME_MQTT = 'DevID' + USER # The first part of the names of Devices in MQTT API 

# The list of active attributes consists of tuples. The tuple contain the name of the attribute in MQTT API
#  and the the list of keys to enter the nested dictionary of openweathermap for getting the value
ACTIVE_ATTRIBUTES = [(name_mqtt, path_owm) for ((name_mqtt, _, _), path_owm) in ATTRIBUTE_MATCHES] 

# The list of commands consists of tuples. The tuple contain the name of the attribute in context broker api (NGSIv2 not ready)
#  and pointer to the function which should be called when the command is triggerd.
COMMANDS = { key : value for ((_ , key , _ ), value) in COMMAND_MATCHES }


# Definitons for city_creators only
FIWARE_SERVICE_PATH = '/environment'
FIWARE_SERVICE = 'icai' + USER
IOT_SERVER = SERVER
IOT_PORT = 5050
CONTEXTBROKER_SERVER = SERVER
CONTEXTBROKER_PORT = 1026

DEVICE_BASISNAME_CONTEXTBROKER ='DevEnt'
IOT_ACTIVE_ATTRIBUTES = [(a_id, a_name, a_type) for ((a_id, a_name, a_type), _ ) in ATTRIBUTE_MATCHES]
IOT_COMMANDS = [(a_id, a_name, a_type) for ((a_id, a_name, a_type) , _ ) in COMMAND_MATCHES]

IATACODES_KEY = '32320f7b-58ee-46a7-847e-468b451eb083'