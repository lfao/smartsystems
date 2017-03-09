import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
	print("Connected with result code " + str(rc))
	client.subscribe("/1234/DevID3710115/cmd")
#client.subscribe("/1234/DevID3710117/#")

topic1 = "/1234/DevID3710117/attrs/commandE_info"
topic2 = "/1234/DevID3710117/attrs/commandE_status"

def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload))
	client.publish(topic1, int(s))
	client.publish(topic2, "OK")
	
	
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

host = "130.206.112.29"
print("Connecting to " + host)
client.connect(host, port=1883, keepalive=60)

client.loop_forever()