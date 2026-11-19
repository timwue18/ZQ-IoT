from machine import Pin, ADC
from time import sleep
from lib.umqtt.simple import *
import json
import network

pump = Pin(5, Pin.OUT, value=0)
adc = ADC(0)      # ESP8266 hat nur einen ADC-Eingang: A0

f = open("config.json", "r")
config = json.load(f)
f.close()

def on_message(topic, msg):
    print("Nachricht angekommen: " + str(msg))
    try:
        seconds = max(0, min(float(msg.decode()), 10))
    except Exception:
        print("Ungueltiger Wert")
        return
    pump.on()
    sleep(seconds)
    pump.off()


mqtt = MQTTClient("esp8266", config["broker"]["IP"])
mqtt.set_callback(on_message)

while True:
    print("session resumed: " + str(mqtt.connect(clean_session=False)))
    mqtt.subscribe(config["broker"]["subscriber"], qos=1)
    print("subscribe to: " + config["broker"]["subscriber"])
    for i in range(10):
        mqtt.check_msg()
        sleep(0.1)

    mqtt.publish(config["broker"]["publisher"], str(adc.read()))
    print("send message to: " + config["broker"]["publisher"])
    mqtt.disconnect()
    sleep(15)
