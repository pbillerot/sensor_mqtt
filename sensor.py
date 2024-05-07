
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

state = ""
percent1 = 0
percent2 = 0
while True:
    # charging / discharging
    data = psutil.sensors_battery()
    if data is not None:
        if data.power_plugged:
            state = "charging"
        else:
            state = "discharging"
    sensor_publish(config["sensors"]["battery_state"]["topic"], state)

    # percent battery
    # data = psutil.sensors_battery()
    f = open('/sys/class/power_supply/BAT0/capacity')
    percent1 = round(int(f.read().strip('\n')))
    f.close()
    if percent1 is not None:
        sensor_publish(config["sensors"]["battery1_percent"]["topic"], percent1)

    f = open('/sys/class/power_supply/BAT1/capacity')
    percent2 = round(int(f.read().strip('\n')))
    f.close()
    if percent2 is not None:
        sensor_publish(config["sensors"]["battery2_percent"]["topic"], percent2)

    time.sleep(config["refresh_interval"])

client.loop_stop()
client.loop_forever()

