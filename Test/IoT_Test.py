#import IoTAgent
#IoTAgent.CreateIotAgent(IoTAgent.CreateIotDeviceJson(id = 3, attributes = [('a', 'WertA', 'int'),('b', 'WertB', 'float')], commands = [('e', 'CommandE', 'int'),('f', 'CommandF', 'float')], static_attributes = [('WertC', 'int', 1),('WertD', 'float', 99.9)]))
#import mqtt_test
#import command_test
#import command_test2


import IoTAgent
IoTAgent.CreateIotAgent(IoTAgent.CreateIotDeviceJson(
    id = 'Watchdog',  entity_type = "Watchdog", entity_basisname = "",
    attributes = [('ec', 'CityErrors', 'Compound'),('es', 'SensorsErrors', 'Compound')], 
    commands = [('a','AddCity', 'Name'), ('r','RemoveCity', 'Name')]))