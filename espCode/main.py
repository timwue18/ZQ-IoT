from machine import Pin, ADC, deepsleep
import machine
from time import sleep
import esp32
import os

pin=Pin(2, Pin.OUT)
reset_btn=Pin(39,Pin.IN)
esp32.wake_on_ext0(reset_btn,1)

# Haus/Zimmer/PflanzenID/gießen/
# Haus/Zimmer/PflanzenID/moisture/

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


adc=ADC(Pin(36))

while True:
	if reset_btn.value() == 1:
		print("RESET")	
		resetConfiguration()
	else:
		print("WAKEUP no reset")
	deepsleep()

