import socket
import json


def web_page():
    html = """<!DOCTYPE html>
<html>
    <head>
        <title>ESP Client Configuration</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta charset="utf-8">
        <link rel="icon" href="data:,">
        <style>
            html {font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
            h1 {color: #0F3376; padding: 2vh;}
            p {font-size: 1.5rem;}
            .button {display: inline-block; background-color: #e7bd3b; border: none;
            border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
            font-size: 30px; margin: 2px; cursor: pointer;}
            .button2 {background-color: #4286f4;}
        </style>
    </head>
    <body>
        <h1>ESP Client Configurator</h1>
        <p>Hallo, über diese Website muss der ESP32 beim ersten Start oder nach einem Reset eingerichtet werden.</p>
        <form method="post" action="submit">
            <p><label for="wlan_name">Bitte gib die SSID des Wlans ein: </label><input type="text" id="wlan_name" name="wlanName"></p>
            <p><label for="wlan_password">Bitte gib das Wlan Passwort ein (falls das Wlan keins hat, bitte freilassen): </label><input type="text" id="wlan_password" name="wlanPassword"></p>
            <p><label for="mqtt_broker_ip">Bitte gib die IP des MQTT Brokers ein: </label><input type="text" id="mqtt_broker_ip" name="brokerIP"></p>
            <p><label for="mqtt_broker_sub">Bitte gib den Subscriber Pfad ein (Pumpe): </label><input type="text" id="mqtt_broker_sub" name="brokerSubscriber"></p>
            <p><label for="mqtt_broker_pub">Bitte gib den Publish Pfad ein (Sensor): </label><input type="text" id="mqtt_broker_pub" name="brokerPublisher"></p>
            <p><input type="submit" id="submit" value="senden"></p>
        </form>
    </body>
</html>"""
    return html


def url_decode(value):
    """Dekodiert application/x-www-form-urlencoded-Daten."""
    value = value.replace(b"+", b" ")
    result = bytearray()
    i = 0

    while i < len(value):
        if value[i:i + 1] == b"%" and i + 2 < len(value):
            try:
                result.append(int(value[i + 1:i + 3], 16))
                i += 3
                continue
            except ValueError:
                pass

        result.append(value[i])
        i += 1

    return result.decode("utf-8")


def parse_form(body):
    data = {}

    for pair in body.split(b"&"):
        if b"=" in pair:
            key, value = pair.split(b"=", 1)
            data[url_decode(key)] = url_decode(value)

    return data


def read_request(conn):
    """Liest Header und vollständigen Body gemäß Content-Length."""
    request_data = bytearray()
    header_end = -1

    # Erst den vollständigen HTTP-Header empfangen.
    while header_end < 0:
        chunk = conn.recv(512)
        if not chunk:
            raise OSError("Verbindung geschlossen, bevor der Header vollständig war")
        request_data.extend(chunk)
        header_end = request_data.find(b"\r\n\r\n")

    header_bytes = bytes(request_data[:header_end])
    body = bytearray(request_data[header_end + 4:])

    content_length = 0
    headers = header_bytes.split(b"\r\n")

    for header in headers[1:]:
        if b":" in header:
            name, value = header.split(b":", 1)
            if name.strip().lower() == b"content-length":
                content_length = int(value.strip())
                break

    # Weiter lesen, bis der gesamte POST-Body angekommen ist.
    while len(body) < content_length:
        chunk = conn.recv(min(512, content_length - len(body)))
        if not chunk:
            raise OSError("Verbindung geschlossen, bevor der Body vollständig war")
        body.extend(chunk)

    request_line = headers[0].decode("utf-8")
    return request_line, bytes(body[:content_length])


def send_response(conn, status, content_type, body):
    if isinstance(body, str):
        body = body.encode("utf-8")

    headers = (
        "HTTP/1.1 " + status + "\r\n"
        "Content-Type: " + content_type + "\r\n"
        "Content-Length: " + str(len(body)) + "\r\n"
        "Connection: close\r\n\r\n"
    )
    conn.sendall(headers.encode("utf-8") + body)


def startserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print("Got a connection from %s" % str(addr))
        should_reset = False

        try:
            request_line, body = read_request(conn)
            print("Request:", request_line)

            if request_line.startswith("POST "):
                form = parse_form(body)

                config = {
                    "wlan": {
                        "ssid": form.get("wlanName", ""),
                        "password": form.get("wlanPassword", "")
                    },
                    "broker": {
                        "IP": form.get("brokerIP", ""),
                        "subscriber": form.get("brokerSubscriber", ""),
                        "publisher": form.get("brokerPublisher", "")
                    }
                }

                # Datei sicher schließen, bevor der ESP zurückgesetzt wird.
                with open("config.json", "w") as f:
                    json.dump(config, f)
                    f.flush()

                print("Config gespeichert:", config)
                send_response(
                    conn,
                    "200 OK",
                    "text/html; charset=utf-8",
                    "<html><body><p>Konfiguration gespeichert. ESP32 startet neu.</p></body></html>"
                )
                should_reset = True
            else:
                send_response(
                    conn,
                    "200 OK",
                    "text/html; charset=utf-8",
                    web_page()
                )

        except Exception as e:
            print("Fehler:", e)
            try:
                send_response(
                    conn,
                    "400 Bad Request",
                    "text/plain; charset=utf-8",
                    "Request konnte nicht verarbeitet werden."
                )
            except Exception:
                pass
        finally:
            conn.close()

        if should_reset:
            import time
            import machine
            time.sleep(1)
            machine.reset()

