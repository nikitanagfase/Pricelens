import { useMemo, useState } from "react";

const AIRLINE_COLORS = {
  "6E": "#6C63FF", AI: "#FF6584", SG: "#FFB347", UK: "#43D9A5", I5: "#38BDF8",
};

function fmt(n) {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

export default function FlightResults({ data, onBook }) {
  const [sortBy, setSortBy] = useState("price");
  const [timeFilter, setTimeFilter] = useState("all");

  const filtered = useMemo(() => {
    if (!data) return [];
    let list = [...data.results];

    if (timeFilter !== "all") {
      const ranges = { morning: [5, 12], afternoon: [12, 18], night: [18, 24] };
      const [h1, h2] = ranges[timeFilter];
      list = list.filter((f) => {
        const h = parseInt(f.departure_time.split(":")[0], 10);
        return h >= h1 && h < h2;
      });
    }

    list.sort((a, b) => {
      if (sortBy === "price") return a.price - b.price;
      if (sortBy === "duration") return parseInt(a.duration) - parseInt(b.duration);
      if (sortBy === "departure") return a.departure_time.localeCompare(b.departure_time);
      if (sortBy === "prediction") return b.confidence - a.confidence;
      return 0;
    });
    return list;
  }, [data, sortBy, timeFilter]);

  if (!data) return null;

  return (
    <div className="results-section">
      <div className="results-header">
        <div className="results-count">
          <span>{filtered.length} flights found</span>
          <span className={`source-badge ${data.source}`}>
            {data.source === "ignav" ? "Live · Ignav" : "Demo data"}
          </span>
        </div>
        <div className="results-filters">
          <select className="filter-select" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="price">Sort: Lowest Price</option>
            <option value="duration">Sort: Duration</option>
            <option value="departure">Sort: Departure Time</option>
            <option value="prediction">Sort: Best Confidence</option>
          </select>
        </div>
      </div>

      <div className="filter-panel">
        <div className="filter-group">
          <label>Departure Time</label>
          <div className="time-filters">
            {["all", "morning", "afternoon", "night"].map((t) => (
              <button
                key={t}
                className={`time-btn ${timeFilter === t ? "active" : ""}`}
                onClick={() => setTimeFilter(t)}
              >
                {t[0].toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛫</div>
          <p>No flights match these filters. Try widening your search.</p>
        </div>
      ) : (
        <div className="flight-list">
          {filtered.map((f, i) => {
            const color = AIRLINE_COLORS[f.airline_code] || "#6C63FF";
            return (
              <div className="flight-result" key={i}>
                <div className="fr-airline">
                  <div className="airline-logo" style={{ background: `linear-gradient(135deg, ${color}, ${color}99)` }}>
                    {f.airline_code}
                  </div>
                  <div>
                    <div className="airline-name">{f.airline_name}</div>
                    <div className="flight-number">{f.flight_number}</div>
                  </div>
                </div>

                <div className="fr-times">
                  <div className="time-range">
                    {f.departure_time} <span className="time-sep">──✈──</span> {f.arrival_time}
                  </div>
                  <div className="flight-duration">{f.duration} · <span className="stop-badge">{f.stops}</span></div>
                </div>

                <div>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Confidence: {f.confidence}%</div>
                  <div className={`fr-predict-badge ${f.prediction_trend}`}>
                    {f.prediction_trend === "rise" ? "↑" : f.prediction_trend === "drop" ? "↓" : "→"} {f.prediction_label}
                  </div>
                </div>

                <div className="fr-price-block">
                  <div className="fr-price">{fmt(f.price)}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>per person</div>
                </div>

                <button className="btn-book" onClick={() => onBook?.(f)}>Book →</button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
