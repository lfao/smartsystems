import paho.mqtt.client as mqtt
from time import sleep
devid = 1

topic1 = "/1234/DevID37101{0:02}/cmd".format(devid)
topic3 = "/1234/DevID37101{0:02}/cmdexe".format(devid)

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	client.subscribe(topic1)
	print (topic1)


def on_message(client, userdata, msg):
	sleep(0.4);
	print(msg.topic + " " + str(msg.payload))
	client.publish(topic3, '{"CommandE":"6"}')	


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

host = "130.206.112.29"
print("Connecting to " + host)
client.connect(host, port=1883, keepalive=60)

client.loop_forever()

#import paho.mqtt.client as mqtt

#def on_connect(client, userdata, flags, rc):
#    print("Connected with result code " + str(rc))
#    client.subscribe("/1234/DevID3710115/attrs/b")
#    client.subscribe("/1234/DevID3710117/configuration/commands/e")


#client.subscribe("/1234/DevID3710115/#")

#def on_message(client, userdata, msg):
#	print(msg.topic + " " + str(msg.payload))
	
#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_message = on_message

#host = "130.206.112.29"
#print("Connecting to " + host)
#client.connect(host, port=1883, keepalive=60)

#client.loop_forever()