#!/usr/bin/env python3
import time
import logging

import city
import city_scheduler

logging.basicConfig(level=logging.INFO)

# two ways to create city object
#muc = city.city(cityOwmId = 6940463, cityId = 'MUC') 
#muc = city.getCityByName('Munich')

# two ways to create city object and iot Agent
#muc = city.createCity(cityOwaId = 6940463, cityId = 'MUC', cityName = 'Munich')
#muc = city.createCityByName('Munich') #create city object and iot Agent

#print (muc)

#create city objects in a list 
#pair_owmid_iata_list = [(6940463, 'MUC'), (3117735, 'MAD'), (5128581, 'NYC'),  (1796236, 'SHA')]
#city_list = ([city.city(*pair_owmid_iata) for pair_owmid_iata in pair_owmid_iata_list]



# create city with or without iot agent by an list of city names
city_name_list = ['Berlin', 'Munich', 'New York', 'Shanghai', 'Madrid', 'Sydney', 'Cape Town']
city_list = [city.getCityByName(name) for name in city_name_list] 
#city_list = [city.createCityByName(name) for name in city_name_list] 

#start updating the cities constantly
city_scheduler.repeat(1.0/6, *city_list)
