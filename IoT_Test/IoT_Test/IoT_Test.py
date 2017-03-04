import IoTAgent
IoTAgent.CreateIotAgent(IoTAgent.CreateIotDeviceJson(id = 17, attributes = [('a', 'WertA', 'int'),('b', 'WertB', 'float')], lazy = [('c', 'WertC', 'int'),('d', 'WertD', 'float')], commands = [('e', 'CommandE', 'int'),('f', 'CommandF', 'float')], static_attributes = [('WertG', 'int', 1),('WertH', 'float', 99.9)]))

#import mqtt_test