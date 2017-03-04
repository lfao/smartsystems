import requests
import logging
#import http.client as http_client
#import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1

def CreateIotAgent(*devices) :
    #deviceList = json.dumps({"devices" : devices}) #,indent=4, separators=(',', ': ')
    deviceList = {"devices" : devices}
    firewareService = 'icai31701'

    #logging.basicConfig()
    #logging.getLogger().setLevel(logging.DEBUG)
    #requests_log = logging.getLogger("requests.packages.urllib3")
    #requests_log.setLevel(logging.DEBUG)
    #requests_log.propagate = True

    response = requests.post('http://130.206.112.29:5050/iot/devices/', json = deviceList,
                  headers = {'Fiware-Service': firewareService, 'Fiware-ServicePath' : '/environment'}) #, 'Content-Type' : 'application/json'
    r = response.json()
    print r #('{}: "{}"'.format(r['name'], r['message']))


def CreateIotDeviceJson(id, attributes = [], lazy = [], commands = [], static_attributes = []):
    def convertAttributes(attributes):
        return [{ "object_id" : aId, "name" : aName, "type" : aType } for aId, aName, aType in attributes ]

    device = { "device_id" : "DevID37101{0:02}".format(id), 
                "entity_name" : "DevEnt{}".format(id), 
                "entity_type" : "Device", 
                "transport" : "MQTT"
            }

    if attributes:
        device["attributes"] = convertAttributes(attributes)
    if lazy:
        device["lazy"] = convertAttributes(lazy)
    if commands:
        device["commands"] = convertAttributes(commands)
    if static_attributes:
        device["static_attributes"] = [{ "name" : aId, "type" : aName, "value" : aType } for aId, aName, aType in static_attributes ]
    
    return device 
   
if __name__ == "__main__":
     CreateIotAgent(CreateIotDeviceJson(id = 17, attributes = [('a', 'WertA', 'int'),('b', 'WertB', 'float')], lazy = [('c', 'WertC', 'int'),('d', 'WertD', 'float')], commands = [('e', 'CommandE', 'int'),('f', 'CommandF', 'float')], static_attributes = [('WertG', 'int', 1),('WertH', 'float', 99.9)]))
