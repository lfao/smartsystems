import requests
import logging

from city import city
import city_definitions

FIWARE_SERVICE_PATH = city_definitions.FIWARE_SERVICE_PATH
FIWARE_SERVICE = city_definitions.FIWARE_SERVICE
IOT_AGENT_URL = 'http://{}:{}/iot/devices/'.format(city_definitions.IOT_SERVER, city_definitions.IOT_PORT)
CONTEXTBROKER_URL = 'http://{}:{}/v2/entities/'.format(city_definitions.CONTEXTBROKER_SERVER, city_definitions.CONTEXTBROKER_PORT)

DEVICE_BASISNAME_MQTT = city_definitions.DEVICE_BASISNAME_MQTT
DEVICE_BASISNAME_CONTEXTBROKER = city_definitions.DEVICE_BASISNAME_CONTEXTBROKER

def create_city(owa_id, iata, city_name = None, replace_entity = True):
    """
    Create a city object and the assotiated IOT agent.
    Keyword arguments:
    cityOwmId -- the city id of openweathermap
    iata -- the IATA code of the city
    cityName (optional) -- The name of the city being stored in iot agent. Default is the name being stored in openweathermap.
    Returns:
    The created city object
    """
    
    IOT_ACTIVE_ATTRIBUTES = city_definitions.IOT_ACTIVE_ATTRIBUTES
    IOT_ACTIVE_ATTRIBUTES = city_definitions.IOT_ACTIVE_ATTRIBUTES   

    logger = logging.getLogger(__name__)

    the_city = city(owa_id,iata)


    # get some information for the static attributes associated to this city from the from openweathermap
    dict_owm_json = the_city.get_owm_json()
    latitude = dict_owm_json['coord']['lat']
    longitude = dict_owm_json['coord']['lon']
    if not city_name:
        city_name = dict_owm_json['name']
    country = dict_owm_json['sys']['country']
        
    iot_static_attributes = [('Position', 'geo:point',"{},{}".format(latitude, longitude)), ('Countrycode', 'string', country), ('Name', 'string', city_name)]
    
    device = { "device_id" : DEVICE_BASISNAME_MQTT + iata, 
                "entity_name" : DEVICE_BASISNAME_CONTEXTBROKER + iata, 
                "entity_type" : "Device", 
                "transport" : "MQTT",
                "attributes" : [{ "object_id" : a_id, "name" : a_name, "type" : a_type } for (a_id, a_name, a_type) in IOT_ACTIVE_ATTRIBUTES],
                "commands" : [{ "object_id" : a_id, "name" : a_name, "type" : a_type } for (a_id, a_name, a_type) in IOT_ACTIVE_ATTRIBUTES],
                "static_attributes" : [{ "name" : a_id, "type" : a_name, "value" : a_type } for a_id, a_name, a_type in iot_static_attributes]  
            }

    device_list = {"devices" : [device]}

    delete_iot_agent(iata)
    delete_contextbroker_entity(iata, delete = replace_entity)

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
    if the_city.put_mqtt_json(city.convert_owm_to_mqtt(dict_owm_json)):
        logger.info("{}: Update sucessfully finished".format(iata))
    else:
         logger.error("{}: city could not be updated".format(iata))

    return the_city

def delete_iot_agent(iata):
    '''
    check wether city iot agent already exists. Delete if yes.
    Keyword arguments:
    iata -- the IATA code of the city
    '''

    logger = logging.getLogger(__name__)
    name_mqtt = DEVICE_BASISNAME_MQTT + iata
    response = requests.get(IOT_AGENT_URL + name_mqtt, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        logger.warning ("{}: IOT agent does already exist. Deleting IOT agent!".format(iata))
        response = requests.delete(IOT_AGENT_URL + name_mqtt, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
        if 204 == response.status_code:
            logger.info ("{}: IOT agent successfully deleted".format(iata))
        else:
            logger.error("{}: IOT agent could not be deleted. Http error code: {}".format(iata, response.status_code)) 

def delete_contextbroker_entity(iata, delete = True):
    '''
    check wether city entity already exists. Delete if yes and delete is true.
    Keyword arguments:
    iata -- the IATA code of the city
    '''

    logger = logging.getLogger(__name__)
    name_contextbroker = DEVICE_BASISNAME_CONTEXTBROKER + iata
    response = requests.get(CONTEXTBROKER_URL + name_contextbroker, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
    if 200 == response.status_code:
        if delete:
            logger.warning ("{}: Entity does already exist. Deleting entity!".format(iata))
            response = requests.delete(CONTEXTBROKER_URL + name_contextbroker, headers = {'Fiware-Service': FIWARE_SERVICE, 'Fiware-ServicePath' : FIWARE_SERVICE_PATH})
            if 204 == response.status_code:
                logger.info ("{}: Entity successfully deleted".format(iata))
            else:
                logger.error("{}: Entity could not be deleted. Http error code: {}".format(iata, response.status_code)) 
        else:
            logger.info ("{}: Entity does already exist.".format(iata))

def get_city_owm_id_and_iata(name):
    """
    Gets the city id of openweathermap and the IATA code of the city
    Returns a tuple of:
    cityOwmId,iata -- the city id of openweathermap, the IATA code of the city
    """
    logger = logging.getLogger(__name__)
    
    # get the IATA code
    IATACODES_KEY = city_definitions.IATACODES_KEY
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(name, city.OWM_KEY))
    owa_id = r.json()['id']
    owa_name = r.json()['name']

    # get the city id of openweathermap
    r = requests.get('https://iatacodes.org/api/v6/autocomplete?query={}&api_key={}'.format(name, IATACODES_KEY))
    cities = r.json()['response']['cities']
    iata = cities[0]['code']
    iata_name = cities[0]['name']
    logger.info ('IATA: {}, OWM_ID: {},'.format(owa_id,iata))
    if (not(name == owa_name == iata_name)):
        logger.warning('The names are different! Name: {}, OWM_Name: {}, IATA_Name: {}'.format (name, owa_name, iata_name))
    return (owa_id,iata)

def create_city_by_name(name):
    """
    Create a city object and the assotiated IOT agent.
    Keyword arguments:
    cityName -- The name of the city being stored in iot agent and found it openweathermap and in IATA database.
    Returns:
    The created city object
    """
    (city_owm_id, iata) = get_city_owm_id_and_iata(name)
    return create_city(city_owm_id, iata, name)
    
def get_city_by_name(name):
    """
    Create a city object. The IOT agent must already exist.
    Keyword arguments:
    cityName -- The name of the city being stored in iot agent and found it openweathermap and in IATA database.
    Returns:
    The created city object
    """
    return city(*get_city_owm_id_and_iata(name))