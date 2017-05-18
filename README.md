### smartsystems
This repository includes the python scripts for simulating IoT-Devices for weather measurement working with FIWARE.

## Solution Pract1
In the Visual Studio 2015 solution Prac1 are three projects. 

### Project CityIotDevices
The most important one is CityIotDevices.
The starting point of these scripts is the file main.py.
The most important script is city.py. This class simulates weather stations in cities. Instead of measurement, the information comes from OpenWeatherMap (which is real data). One instance needs its own mqtt iot agent and is not aware of the context broker. When calling the method update the city is pulling information from OpenWeatherMap, extracts the desired information and forwards it through mqtt.
The script city_creators.py helps to get the city objects by only knowing the name of the city. Furhtermore it can create IoT-Agents for a certain city.
The script city_scheduller.py forces the cities to regularly push active attributes.

### Project CityWatchdog
The Project CityWatchdog containts the script watchdog which requires the city_definitions of the Project CityIotDevices.
The script watchdog.py monitors if every city updates the required attributes regularly. It subscribes the attributes of cities in mqtt. For monitoring a city, you have to call the AddCity command in ContextBroker and insert there the name of the IoT device in mqtt.

### Project GUI
The Project GUI containts a pyQT GUI for displaying the last updated values of the selected city. As the subscribes to the relevant data, it makes sense to modify the script main.py in order to achieve a greater frequency of published data.

## Pract3
In the folder widget there are all necessary components of the newly developed widget including the .wgt file. 
Furthermore there can be found the documentation of the whole dashboard and a website (index.htlm) with the dashboard included.
