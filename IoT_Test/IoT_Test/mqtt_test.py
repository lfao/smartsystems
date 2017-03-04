import json
import paho.mqtt.client as mqtt

#print(2314)

#"icai31701"
#"Fiware-Service: icai31701" 
#ContextBroker API (port 1026) 
#IOTAgent API (port 5050)



#def on_connect(client, userdata, flags, rc):
#    print("connencted with coude " + str( rc))

#def on_publish(client, userdata, mid):
#    pass

#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_publish = on_publish

#host = "192.168.99.1"
#client.connect(host, port = 1883, keepalive = 60)
#client.loop_start()

#topic = "acceleration"

#s = ""
#while s != "exit": 
#    s = input("payload >")
#    client.publish(topic,s)

#client.loop_stop()

mqttc = mqtt.Client()
mqttc.connect('130.206.112.29', 1883)
device = 'DevID3710115'

mqttc.publish("/1234/{}/attrs/a".format(device), str(10))


mqttc.publish("/1234/{}/attrs/".format(device), '{"a":"11","b":"9"}')
#mqttc.publish("/1234/{}/attrs/".format(device), 'a|13|b|8')