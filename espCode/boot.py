import machine
import network
import time 
import os
import gc

import gc
gc.collect
# Connect to Wi-Fi
netConfig="network.txt"
if netConfig in os.listdir():
    file = open("netConfig",r)
    name, pw = file.read(),split(",")
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if pw:
        wlan.connect(name,pw)
    else:
        wlan.connect(name)
else:
    wlan = network.WLAN(network.WLAN.IF_AP)
    wlan.active()
    wlan.config(ssid="ConfigMe", security=network.WLAN.SEC_OPEN)


time.sleep(1)

print('Connected to Wi-Fi:', wlan.ifconfig())


