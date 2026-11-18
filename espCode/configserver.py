import socket
import re
import json


def web_page():
	html = """
<html>
	<head>
		<title>ESP Client Configuration</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<meta charset="utf-8">
		<link rel="icon" href="data:,">
		<style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
			h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;
			border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
			.button2{background-color: #4286f4;}
		</style>
	</head>
	<body>
		<h1>ESP Client Configurator</h1>
	<p>Hallo, über diese Website muss der ESP32 beim ersten Start oder nach einem reset eingerichtet werden.</p>
	<p><form method="post", action="submit", type="submit">
	<p><label id="wlan_name">Bitte gib die SSID des Wlans ein: </label><input type="text" name="wlanName"></p>
	<p><label id="wlan_password">Bitte gib das Wlan Passwort ein(Fall das Wlan keins hat, bitte freilassen): <input type="text" name="wlanPassword"</p>
	<p><label id="mqtt_broker_ip">Bitte gib die IP des MQTT Brokers ein</label> <input type="test" name="brokerIP"></p>
	<p><input type="submit" id="submit">senden</p>
	</form>
</html>"""
	return html

def startserver():
	wlan_name=""
	wlan_password=""
	broker_ip=""

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 80))
	s.listen(5)

	while True:
		conn, addr = s.accept()
		print('Got a connection from %s' % str(addr))
		request = conn.recv(1024)
		request = str(request)
		print('Content = %s' % request)
		if "POST" in request:
			print("Hello From Post request")
			pattern=re.compile(r"wlanName=(.*)&wlanPassword=(.*)&brokerIP=(.*)'")
			match=pattern.search(request)
			print(match.group(1), match.group(2), match.group(3))
			config={"wlan": {"ssid": match.group(1).replace("+", " "), "password": match.group(2).replace("+", " ")}, "broker":{"IP": match.group(3)}}
			f=open("config.json", "w")
			json.dump(config,f)
			f.close()
			print(config)
			import machine
			machine.reset()
		response = web_page()
		conn.send('HTTP/1.1 200 OK\n')
		conn.send('Content-Type: text/html\n')
		conn.send('Connection: close\n\n')
		conn.sendall(response)

		conn.close()
