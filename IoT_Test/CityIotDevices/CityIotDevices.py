#!/usr/bin/env python3
import time
import logging

import city
import cityScheduler

logging.basicConfig(level=logging.INFO)

#muc = city.createCity(cityOwaId = 6940463, cityId = 'MUC', cityName = 'Munich')
#print (muc)
#mad = city.createCity(cityOwaId = 3117735, cityId = 'MAD')
#print (mad)
#nyc = city.createCity(cityOwaId = 5128581, cityId = 'NYC')
#print (nyc)
#sha = city.createCity(cityOwaId = 1796236, cityId = 'SHA')
#print sha

#muc = city.city(cityOwmId = 6940463, cityId = 'MUC')
#mad = city.city(cityOwmId = 3117735, cityId = 'MAD')
#nyc = city.city(cityOwmId = 5128581, cityId = 'NYC')
#sha = city.city(cityOwmId = 1796236, cityId = 'SHA')

#city.createCityByName('Berlin')



cityScheduler.repeat(1.0/6,
    city.createCityByName('Berlin'),
    city.createCityByName('Munich'),
    city.createCityByName('New York'),
    city.createCityByName('Shanghai'),
    city.createCityByName('Madrid'), 
    city.createCityByName('Sydney'), 
    city.createCityByName('Cape Town'))


#print muc.update()
#while True:
#    time.sleep(1);
