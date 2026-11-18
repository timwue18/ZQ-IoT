import machine
import network
import time 
import os
import gc

import gc
import json
gc.collect

# Connect to Wi-Fi

wlan = network.WLAN(network.WLAN.IF_STA)
if not wlan.isconnected():
	config="config.json"
	if config in os.listdir():
		print("Config found")
		f=open(config, "r")
		config=json.load(f)
		f.close()
		wlan.active(True)
		time.sleep(1)	
		for i in range(3):
			if config["wlan"]["password"]:
				wlan.connect(config["wlan"]["ssid"], config["wlan"]["password"])
			else:
				wlan.connect(config["wlan"]["ssid"])
			time.sleep(2)
			if wlan.isconnected():
				print("wifi is connected")
				print(wlan.ifconfig())
				break
	else:
		print("no Config")
		wlan = network.WLAN(network.WLAN.IF_AP)
		wlan.active(True)
		wlan.config(ssid="ConfigMe", security=network.WLAN.SEC_OPEN)
		import configserver
		configserver.startserver()
else:
	print("wlan already connected")
	print(wlan.ifconfig())

