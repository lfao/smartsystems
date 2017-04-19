import paho.mqtt.client as mqtt
import sys
from PyQt4 import QtCore, QtGui, uic
import json
import collections
from functools import partial

try:
    import city_definitions
except:
    sys.path.append('../Common')
    import city_definitions

# get city definitions
MQTT_API_KEY = city_definitions.MQTT_API_KEY
MQTT_SERVER = city_definitions.SERVER
host = MQTT_SERVER

# load ui-file from file
qtCreatorFile = "GUI.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
ACTIVE_ATTRIBUTES = [name_tupel for (name_tupel, _) in city_definitions.ATTRIBUTE_MATCHES]

print (ACTIVE_ATTRIBUTES)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))
            client.subscribe("/{}/#".format(MQTT_API_KEY))

        # define callback functions for every city
        def on_message_BER(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 1:
                self.update(json.loads(msg.payload))

        def on_message_BUE(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 2:
                self.update(json.loads(msg.payload))

        def on_message_CPT(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 3:
                self.update(json.loads(msg.payload))

        def on_message_MAD(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 4:
                self.update(json.loads(msg.payload))

        def on_message_MUC(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 5:
                print(self.cityBox.currentIndex())
                self.update(json.loads(msg.payload))

        def on_message_NYC(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 6:
                self.update(json.loads(msg.payload))

        def on_message_SHA(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 7:
                self.update(json.loads(msg.payload))

        def on_message_SYD(client, userdata, msg):
            if int(self.cityBox.currentIndex()) == 8:
                self.update(json.loads(msg.payload))

        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # set up and connect MQTT client
        client = mqtt.Client()
        client.on_connect = on_connect
        # add callback functions for every city
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701BER'), on_message_BER)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701BUE'), on_message_BUE)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701CPT'), on_message_CPT)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701MAD'), on_message_MAD)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701MUC'), on_message_MUC)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701NYC'), on_message_NYC)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701SHA'), on_message_SHA)
        client.message_callback_add("/{}/{}/#".format(MQTT_API_KEY, 'DevID31701SYD'), on_message_SYD)
        client.connect(host, port=1883, keepalive=60)
        print("Connecting to " + host)
        client.loop_start()

    # update subscribed data in GUI
    def update(self, data):
        self.temperature.setText(str(data['t']) + " K")
        self.humidity.setText(str(data['h']) + " %")
        self.windspeed.setText(str(data['w']) + " mph")
        self.pressure.setText(str(data['p']) + " hPa")
        self.clouds.setText(str(data['c']) + " %")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())