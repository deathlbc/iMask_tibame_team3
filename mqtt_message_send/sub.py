# python as a subscriber

from datetime import datetime
import pymysql
import pymysql.cursors
import paho.mqtt.client as mqtt


def insertslog(msg):
    datalist = msg.payload.decode("utf-8").split(",")
    aiotno, rdate, rtime, cpin, cpout, nowin = datalist

    # connect mysql
    connection = pymysql.connect(host="hostname",
                                 user="username",
                                 password="password",
                                 database="database name",
                                 charset='charset',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        # remember '' for date/time data
        sql = f"insert into slog (aiotno, rdate, rtime, cpin, cpout, nowin) values ('{aiotno}', '{rdate}', '{rtime}', '{cpin}', '{cpout}', '{nowin}')"
        cursor.execute(sql)
    connection.commit()

    # disconnect mysql, db will thank you so much
    cursor.close()
    connection.close()
    print("DONE")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Your_Topic/#")  # setup subscribe topic


# do while receiving msg
def on_message(client, userdata, msg):
    print(str(msg.payload))
    print(msg.payload.decode("utf-8").split(","))  # decode utf-8 for chinese
    insertslog(msg)

brokerID = 'Broker IP'  # the public of your VM


# connection setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(brokerID, 1883, 60)  # TCP settings
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()