#!/usr/bin/env python3
import time
import logging

import city
import city_creators
import city_scheduler

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename='city_emulator.log',level=logging.INFO)


# two ways to create city object
#muc = city.city(city_owm_id = 6940463, iata = 'MUC') 
#muc = city_creators.get_city_by_name('Munich')

# two ways to create city object and iot Agent
#muc = city_creators.create_city(city_owm_id = 6940463, iata = 'MUC', city_name = 'Munich')
#muc = city_creators.create_city_by_name('Munich') #create city object and iot Agent

#print (muc)

#create city objects in a list 
#pair_owmid_iata_list = [(6940463, 'MUC'), (3117735, 'MAD'), (5128581, 'NYC'),  (1796236, 'SHA')]
#city_list = ([city.city(*pair_owmid_iata) for pair_owmid_iata in pair_owmid_iata_list]

#create and delete a city
#city_creators.create_city_by_name('Singapore')
#city_creators.delete_iot_agent('SIN')
#city_creators.delete_contextbroker_entity('SIN')

# create city with or without iot agent by an list of city names
city_name_list = ['Berlin', 'Munich', 'New York', 'Shanghai', 'Madrid', 'Sydney', 'Cape Town', 'Buenos Aires']
city_list = [city_creators.get_city_by_name(name) for name in city_name_list] 
#city_list = [city_creators.create_city_by_name(name) for name in city_name_list] 

#start updating the cities constantly
city_scheduler.repeat(1.0/60,cities_delay_seconds = 0, *city_list)

