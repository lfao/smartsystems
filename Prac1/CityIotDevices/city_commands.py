#!/usr/bin/env python3
import psutil
import time

def get_cpu_load(_, time):
    return psutil.cpu_percent(interval=float(time))

def get_update_count(obj, _):
    return obj.update_counter

#def getTimezone(city, _):
#    logger = logging.getLogger(__name__)
#    KEY =  AIzaSyAnDJngQwBMUz-hPGl7eSkrqnGhcIS_K_s 
#    r = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address={}'.format(city.iata))
#    location = r.json()['geometry']['location']
#    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(name, city.OWM_KEY))
#    cityOwaId = r.json()['id']
    