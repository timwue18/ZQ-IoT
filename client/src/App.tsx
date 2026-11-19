import { HealthBar } from "./HealthBar";
import { PumpButton } from "./PumpButton";
import { useMqtt } from "./useMQTT";

const MQTT_URL = import.meta.env.VITE_MQTT_URL;

export default function App() {
  const { werte, status, publish } = useMqtt(MQTT_URL, "s");

  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <p>Status: {status}</p>

      <HealthBar wert={werte["s"]} nass={620} trocken={797} />

      <PumpButton publish={publish} verbunden={status === "verbunden"} />
    </main>
  );
}
