
#!/usr/bin/python
# -*- coding:Utf-8 -*-
"""
    Sensor for desktop with multible batterys
    sudo apt install python3-paho-mqtt
"""
import paho.mqtt.client as mqtt
import json
import os
import psutil
import time

def load_config(file="config.json") -> dict:
    print(f'Reading configuration file {file}')
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.critical("Config file not found %s, exiting now", file)
        exit(1)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe(config["subscribe_topic"],0)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))    
    if msg.topic == config["subscribe_topic"]:
        # commande shell
        os.system(msg.payload)

def on_subscribe(client, userdata, mid, reason_code):
    print(f"Subscribe with result code {reason_code}")

def sensor_publish(topic, message):
    print(f'{topic}: {message}')
    client.publish(topic, message)

config = load_config()

client = mqtt.Client(config["device_id"])
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.username_pw_set(config["mqtt_user"], config["mqtt_pwd"])
client.connect_async(config["mqtt_server"], 1883, 60)

client.loop_start()

while True:
    # charging / discharging
    data = psutil.sensors_battery()
    if data is not None:
        if data.power_plugged:
            state = "charging"
            sensor_publish(config["sensors"]["battery_state"]["topic"], state)
        else:
            state = "discharging"
            sensor_publish(config["sensors"]["battery_state"]["topic"], state)

    # percent battery
    try:
        # batterie 1    
        f = open('/sys/class/power_supply/BAT0/capacity')
        bat0 = int(f.read().strip('\n'))
        f.close()
        # batterie 1    
        f = open('/sys/class/power_supply/BAT1/capacity')
        bat1 = int(f.read().strip('\n'))
        f.close()
        # moyenne
        percent = round((bat0+bat1)/2)
        sensor_publish(config["sensors"]["battery_percent"]["topic"], percent)
    except Exception as inst:
        print (inst)

    rc = client.loop(timeout=1.0)
    if rc != 0:
        # need to handle error, possible reconnecting or stopping the application
        print(f"Error loop {rc}")
    time.sleep(config["refresh_interval"])

client.loop_stop()


