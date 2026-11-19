type Props = {
  wert?: number;
  nass: number;    // Rohwert bei komplett nasser Erde (z. B. Sensor im Wasser)
  trocken: number; // Rohwert bei komplett trockener Erde (z. B. Sensor in der Luft)
};

export function HealthBar({ wert, nass, trocken }: Props) {
  if (wert === undefined) return <p>Warte auf Werte …</p>;

  // 0 = trocken (rot), 1 = feucht (grün)
  const anteil = Math.min(1, Math.max(0, (trocken - wert) / (trocken - nass)));
  const prozent = Math.round(anteil * 100);

  const status =
    prozent > 66 ? "Gut bewässert" : prozent > 33 ? "Bald gießen" : "Zu trocken!";

  return (
    <div style={{ maxWidth: 420 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <strong>{status}</strong>
        <span>{prozent} %</span>
      </div>

      <div
        role="meter"
        aria-label="Pflanzengesundheit"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={prozent}
        style={{
          position: "relative",
          height: 16,
          borderRadius: 8,
          background: "linear-gradient(to right, #dc2626, #facc15, #16a34a)",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: `${prozent}%`,
            width: 26,
            height: 26,
            borderRadius: "50%",
            background: "white",
            border: "3px solid #1f2937",
            transform: "translate(-50%, -50%)",
            transition: "left 0.5s ease",
          }}
        />
      </div>

      <small style={{ display: "block", marginTop: 8, color: "#6b7280" }}>
        Rohwert: {wert}
      </small>
    </div>
  );
}
