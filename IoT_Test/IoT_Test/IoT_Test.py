#import IoTAgent
#IoTAgent.CreateIotAgent(IoTAgent.CreateIotDeviceJson(id = 3, attributes = [('a', 'WertA', 'int'),('b', 'WertB', 'float')], commands = [('e', 'CommandE', 'int'),('f', 'CommandF', 'float')], static_attributes = [('WertC', 'int', 1),('WertD', 'float', 99.9)]))

#import mqtt_test

#import command_test

import city

muc = city.createCity(cityOwaId = 6940463, cityId = 'Muc', cityName = 'Munich')
print (muc)

#muc = city.city(cityOwaId = 6940463, cityId = 'Muc')
#muc.update()
