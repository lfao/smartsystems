#import IoTAgent
#IoTAgent.CreateIotAgent(IoTAgent.CreateIotDeviceJson(id = 3, attributes = [('a', 'WertA', 'int'),('b', 'WertB', 'float')], commands = [('e', 'CommandE', 'int'),('f', 'CommandF', 'float')], static_attributes = [('WertC', 'int', 1),('WertD', 'float', 99.9)]))

#import mqtt_test

#import command_test

import city
import cityScheduler

#muc = city.createCity(cityOwaId = 6940463, cityId = 'MUC', cityName = 'Munich')
#print (muc)
#mad = city.createCity(cityOwaId = 3117735, cityId = 'MAD')
#print (mad)
#nyc = city.createCity(cityOwaId = 5128581, cityId = 'NYC')
#print (nyc)
#sha = city.createCity(cityOwaId = 1796236, cityId = 'SHA')
#print sha

muc = city.city(cityOwaId = 6940463, cityId = 'MUC')
mad = city.city(cityOwaId = 3117735, cityId = 'MAD')
nyc = city.city(cityOwaId = 5128581, cityId = 'NYC')
sha = city.city(cityOwaId = 1796236, cityId = 'SHA')

cityScheduler.repeat([muc, mad, nyc, sha], 1.0/6)


#muc.update()
