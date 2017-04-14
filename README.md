# smartsystems
This repository includes the python scripts for simulating IoT-Devices for weather measurement working with FIWARE.

In the Visual Studio 2015 solution Prac1 are three projects. The most important one is CityIotDevices.
The starting point of this scripts it the file main.py.
The most important script is city.py. This class simulates weatherstations in cities. Instead of measurement, the information is from OpenWeatherMap (which is real data). One instance needs its own mqtt iot agent and does not know anything about context broker. When calling the method update the city is pulling information from OpenWeatherMap, extracts the desired information and forwards it trough mqtt.
The script city_creators.py is for getting the city objects by only knowing the name of the city. Furhtermore it can create IoT-Agents for a certain city.
The script city_scheduller.py forces the cities to regularly push active attributes.

The Project CityWatchdog containts the script watchdog wich requires the city_definitions of the Project CityIotDevices
The script watchdog.py monitors if every city to monitor updates the required attributes regularly. It subscribes the attributes of cities in mqtt. For monitoring a city, you have to call the AddCity command in ContextBroker and insert there the name of the Name of the IoT device in mqtt.

The Project GUI containts a pyQT gui for diyplaying the last updated values of the selected city
