import paho.mqtt.client as mqtt
from time import sleep

topic1 = "/1234/DevID37101MUC/cmd"
#topic1 = "/1234/DevID37101MUC"
topic3 = "/1234/DevID37101MUC/cmdexe"

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	client.subscribe(topic1)
	print (topic1)

def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload))
	sleep(0.4);
	client.publish(topic3, '{"CpuLoad":"6"}')	


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

host = "130.206.112.29"
print("Connecting to " + host)
client.connect(host, port=1883, keepalive=60)

client.loop_forever()