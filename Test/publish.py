import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	
def on_publish(client, userdata, mid):
	print("publish finished")
	pass
	
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

host = "130.206.112.29"
client.connect(host, port=1883, keepalive=60)

client.loop_start()
#time.sleep(5)
topic = "/1234/DevID3710117/attrs/b"

s = ""
while s != "exit":
	s = input("payload >")
	client.publish(topic, int(s))
#	time.sleep(5)
	
client.loop_start()