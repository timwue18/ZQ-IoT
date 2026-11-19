import { useCallback, useEffect, useRef, useState } from "react";
import mqtt, { type MqttClient } from "mqtt";

type Status = "verbinde" | "verbunden" | "getrennt" | "fehler";

export type Publish = (topic: string, message: string, qos?: 0 | 1 | 2) => Promise<void>;

export function useMqtt(url: string, topic: string) {
  const [werte, setWerte] = useState<Record<string, number>>({});
  const [status, setStatus] = useState<Status>("verbinde");
  const clientRef = useRef<MqttClient | null>(null);

  useEffect(() => {
    const client = mqtt.connect(url, { reconnectPeriod: 2000 });
    clientRef.current = client;

    // Nach dem Aufräumen (z. B. Hot-Reload) darf die alte Verbindung
    // den Status der neuen nicht mehr überschreiben
    let aktiv = true;
    const setze = (neu: Status) => {
      if (aktiv) setStatus(neu);
    };

    client.on("connect", () => {
      setze("verbunden");
      client.subscribe(topic);
    });
    client.on("reconnect", () => setze("verbinde"));
    client.on("close", () => setze("getrennt"));
    client.on("error", () => setze("fehler"));

    client.on("message", (t, payload) => {
      if (!aktiv) return;
      // Der Pi kann eine reine Zahl ("612") oder JSON ({"value": 612}) senden
      const text = payload.toString().trim();
      let value = Number(text);
      if (Number.isNaN(value)) {
        try {
          value = Number((JSON.parse(text) as { value: unknown }).value);
        } catch {
          return;
        }
      }
      if (Number.isNaN(value)) return;
      setWerte((alt) => ({ ...alt, [t]: value }));
    });

    return () => {
      aktiv = false;
      clientRef.current = null;
      client.end();
    };
  }, [url, topic]);

  // Wird erst erfüllt, wenn der Broker die Nachricht bestätigt hat (bei QoS 1: PUBACK)
  const publish = useCallback<Publish>(
    (zielTopic, message, qos = 0) =>
      new Promise((resolve, reject) => {
        const client = clientRef.current;
        if (!client?.connected) {
          reject(new Error("Nicht mit dem Broker verbunden"));
          return;
        }
        client.publish(zielTopic, message, { qos }, (err) => (err ? reject(err) : resolve()));
      }),
    [],
  );

  return { werte, status, publish };
}
