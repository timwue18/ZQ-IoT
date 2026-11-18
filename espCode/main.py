from machine import Pin, ADC, deepsleep
import machine
from time import sleep
import esp32
import os
from lib.umqtt.simple import *
import json
import network
pin=Pin(..., Pin.OUT)
reset_btn=Pin(...,Pin.IN)

esp32.wake_on_ext0(reset_btn,1)
f=open("config.json", "r")
config=json.load(f)
f.close()

def resetConfiguration():
	while reset_btn.value()==1:
		pin.on()
		sleep(0.3)
		pin.off()
		sleep(0.3)
	try:
		os.remove("config.json")
	except:
		pass
	machine.reset()		

def on_message(topic, msg):
	#TODO: activate pump for ... sec
	print("Nachricht angekommen: " + str(msg))

adc=ADC(Pin(...))
mqtt=MQTTClient("esp32", config["broker"]["IP"])
mqtt.set_callback(on_message)

while True:
	if reset_btn.value() == 1:
		print("RESET")	
		resetConfiguration()
	else:
		print("WAKEUP no reset")
		print("test session resumed: " +str(mqtt.connect(clean_session=False)))
		mqtt.subscribe(config["broker"]["subscriber"], qos=1)
		print("subscribe to: " + config["broker"]["subscriber"])
		for i in range(10):
			mqtt.check_msg()
			time.sleep(0.1)
		
		#TODO: read moisture sensor and publish
		mqtt.publish(config["broker"]["publisher"],"Hallo Welt")
		print("send message to: "+ config["broker"]["publisher"])
		mqtt.disconnect()
	deepsleep(15000)

