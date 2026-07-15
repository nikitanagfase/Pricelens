import { useState } from "react";
import { predictPrice } from "../services/api";

const ROUTES = [
  { label: "Mumbai → Delhi", origin: "BOM", destination: "DEL" },
  { label: "Mumbai → Goa", origin: "BOM", destination: "GOI" },
  { label: "Delhi → Bangalore", origin: "DEL", destination: "BLR" },
  { label: "Mumbai → Bangalore", origin: "BOM", destination: "BLR" },
  { label: "Delhi → Hyderabad", origin: "DEL", destination: "HYD" },
];

function fmt(n) {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

function defaultDate(daysAhead) {
  const d = new Date();
  d.setDate(d.getDate() + daysAhead);
  return d.toISOString().split("T")[0];
}

export default function Predictor() {
  const [routeIdx, setRouteIdx] = useState(0);
  const [travelDate, setTravelDate] = useState(defaultDate(14));
  const [daysBefore, setDaysBefore] = useState(14);
  const [airline, setAirline] = useState("Any");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runPrediction = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const route = ROUTES[routeIdx];
      const data = await predictPrice({
        origin: route.origin,
        destination: route.destination,
        travel_date: travelDate,
        days_before_travel: Number(daysBefore),
        airline,
      });
      setResult(data);
    } catch (err) {
      setError("Couldn't get a prediction — check that the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="predictor-layout">
        <div className="predictor-form-card">
          <h3>Enter Flight Details</h3>
          <form className="pred-form" onSubmit={runPrediction}>
            <div className="pred-field">
              <label>Route</label>
              <select className="pred-input" value={routeIdx} onChange={(e) => setRouteIdx(Number(e.target.value))}>
                {ROUTES.map((r, i) => <option key={r.label} value={i}>{r.label}</option>)}
              </select>
            </div>
            <div className="pred-field">
              <label>Travel Date</label>
              <input type="date" className="pred-input" value={travelDate} onChange={(e) => setTravelDate(e.target.value)} />
            </div>
            <div className="pred-field">
              <label>Days Before Travel</label>
              <input type="number" className="pred-input" value={daysBefore} min={0} max={365}
                     onChange={(e) => setDaysBefore(e.target.value)} />
            </div>
            <div className="pred-field">
              <label>Preferred Airline</label>
              <select className="pred-input" value={airline} onChange={(e) => setAirline(e.target.value)}>
                {["Any", "IndiGo", "Air India", "SpiceJet", "Vistara", "AirAsia India"].map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>
            <button className="btn-predict" type="submit" disabled={loading}>
              {loading ? <span className="loading-spinner" /> : "🔮"} {loading ? "Analysing..." : "Run Prediction"}
            </button>
            {error && <div className="form-error">{error}</div>}
          </form>
        </div>

        <div className="predictor-result-card">
          {!result ? (
            <div className="pred-placeholder">
              <div className="pred-placeholder-icon">🔮</div>
              <p>Enter flight details and run prediction to see price forecast with confidence score and feature analysis</p>
            </div>
          ) : (
            <div>
              <div className="pred-price-block">
                <div className="pred-price-label">Predicted Price</div>
                <div className="pred-price-value">{fmt(result.predicted_price)}</div>
                <div className="pred-price-range">Likely range: {fmt(result.lower_bound)} – {fmt(result.upper_bound)}</div>
                <div className="pred-confidence">🎯 {result.confidence}% Confidence</div>
              </div>
              <div className={`pred-verdict ${result.verdict}`}>{result.verdict_message}</div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 12, fontWeight: 500 }}>
                Key Factors
              </div>
              {result.feature_importance.map((f) => (
                <div className="pred-factor" key={f.label}>
                  <span className="pf-label">{f.label}</span>
                  <div className="pf-bar-wrap">
                    <div className="pf-bar" style={{ width: `${f.pct}%`, background: f.color }} />
                  </div>
                  <span className="pf-pct">{f.pct}%</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {result && (
        <div className="xai-section">
          <div className="xai-header">
            <h3>Why this price? — Explainable Factors</h3>
            <span className="xai-badge">SHAP-Powered XAI</span>
          </div>
          <div className="xai-bars">
            {result.feature_importance.map((f) => (
              <div className="pred-factor" key={f.label}>
                <span className="pf-label" style={{ color: "var(--text-primary)" }}>{f.label}</span>
                <div className="pf-bar-wrap" style={{ height: 10 }}>
                  <div className="pf-bar" style={{ width: `${f.pct}%`, background: f.color, height: "100%" }} />
                </div>
                <span className="pf-pct" style={{ color: f.color }}>{f.pct}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
