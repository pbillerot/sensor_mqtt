
#!/usr/bin/python
# -*- coding:Utf-8 -*-
"""
    Sensor for desktop with multible batterys
    sudo apt install python3-paho-mqtt
"""
import paho.mqtt.client as mqtt
import time
import json
import psutil

def load_config(file="config.json") -> dict:
    print(f'Reading configuration file {file}')
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.critical("Config file not found %s, exiting now", file)
        exit(1)

def sensor_publish(topic, message):
    print(f'{topic}: {message}')
    client.publish(topic, message)

config = load_config()

client = mqtt.Client(config["device_id"])
client.username_pw_set(config["mqtt_user"], config["mqtt_pwd"])
client.connect(config["mqtt_server"], 1883, 60)

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

    time.sleep(config["refresh_interval"])

client.loop_stop()
client.loop_forever()

