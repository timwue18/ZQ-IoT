import { useEffect, useState } from "react";
import type { Publish } from "./useMQTT";

const PUMPE_TOPIC = "p";
const GIESS_SEKUNDEN = 4; // Maximum: die Pumpe läuft nie länger als 4 Sekunden

// Der ESP32 schläft 15 s und holt Nachrichten nur beim Aufwachen ab. Mit QoS 1 merkt
// sich der Broker jeden Klick und liefert ihn nach. Ohne Sperre würde mehrfaches
// Klicken mehrere Gießvorgänge hintereinander auslösen.
const SPERRE_SEKUNDEN = 20;

type Props = {
  publish: Publish;
  verbunden: boolean;
};

export function PumpButton({ publish, verbunden }: Props) {
  const [sendet, setSendet] = useState(false);
  const [sperre, setSperre] = useState(0);
  const [fehler, setFehler] = useState<string | null>(null);

  useEffect(() => {
    if (sperre <= 0) return;
    const id = setTimeout(() => setSperre((s) => s - 1), 1000);
    return () => clearTimeout(id);
  }, [sperre]);

  async function giessen() {
    setFehler(null);
    setSendet(true);
    try {
      await publish(PUMPE_TOPIC, String(GIESS_SEKUNDEN), 1);
      setSperre(SPERRE_SEKUNDEN);
    } catch {
      setFehler("Gießbefehl konnte nicht gesendet werden. Ist der Broker erreichbar?");
    } finally {
      setSendet(false);
    }
  }

  const deaktiviert = !verbunden || sendet || sperre > 0;

  let text = `${GIESS_SEKUNDEN} Sekunden gießen`;
  if (sendet) text = "Sende …";
  else if (sperre > 0) text = `Gießbefehl gesendet (wieder möglich in ${sperre} s)`;

  return (
    <div style={{ marginTop: 32 }}>
      <button
        type="button"
        onClick={giessen}
        disabled={deaktiviert}
        style={{
          padding: "12px 20px",
          fontSize: 16,
          borderRadius: 8,
          border: "none",
          background: deaktiviert ? "#9ca3af" : "#2563eb",
          color: "white",
          cursor: deaktiviert ? "not-allowed" : "pointer",
        }}
      >
        {text}
      </button>

      {sperre > 0 && (
        <p style={{ fontSize: 14, color: "#6b7280" }}>
          Die Pumpe startet, sobald der ESP32 das nächste Mal aufwacht (bis zu 15 s).
        </p>
      )}
      {!verbunden && <p style={{ fontSize: 14, color: "#6b7280" }}>Keine Verbindung zum Broker.</p>}
      {fehler && (
        <p role="alert" style={{ color: "#dc2626" }}>
          {fehler}
        </p>
      )}
    </div>
  );
}
