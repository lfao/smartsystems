import city
import cityScheduler
import time
import logging

logging.basicConfig(level=logging.INFO)

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


#print muc.update()
#while True:
#    time.sleep(1);
