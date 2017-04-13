import paho.mqtt.client as mqtt
import city_definitions
import sys

MQTT_API_KEY = city_definitions.MQTT_API_KEY
MQTT_SERVER = city_definitions.SERVER
host = MQTT_SERVER

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/{}/{}/attrs/#".format(MQTT_API_KEY, 'DevID31701MUC'))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    return msg.payload

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

host = MQTT_SERVER
print("Connecting to " + host)
client.connect(host, port=1883, keepalive=60)

client.loop_forever()