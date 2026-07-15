import { useState } from "react";
import { planBudget } from "../services/api";

function fmt(n) {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

export default function BudgetPlanner() {
  const [budget, setBudget] = useState(8000);
  const [origin, setOrigin] = useState("Mumbai");
  const [destination, setDestination] = useState("Flexible");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const find = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await planBudget({ budget: Number(budget), origin, destination });
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="budget-layout">
      <form className="budget-form-card" onSubmit={find}>
        <div className="budget-field">
          <label>Your Total Budget</label>
          <div className="budget-input-wrap">
            <span className="currency">₹</span>
            <input type="number" className="budget-input" value={budget} onChange={(e) => setBudget(e.target.value)} />
          </div>
        </div>
        <div className="budget-field">
          <label>From</label>
          <select className="pred-input" value={origin} onChange={(e) => setOrigin(e.target.value)}>
            {["Mumbai", "Delhi", "Bangalore", "Nagpur", "Kolkata"].map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div className="budget-field">
          <label>To (or Flexible)</label>
          <select className="pred-input" value={destination} onChange={(e) => setDestination(e.target.value)}>
            {["Flexible", "Delhi", "Goa", "Bangalore", "Hyderabad", "Jaipur"].map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
        <button className="btn-predict" type="submit" disabled={loading}>
          {loading ? <span className="loading-spinner" /> : null} {loading ? "Finding options..." : "Find Best Options"}
        </button>
      </form>

      <div className="budget-results">
        {!result ? (
          <div className="pred-placeholder">
            <div className="pred-placeholder-icon">💰</div>
            <p>Set your budget and preferences to see the best travel options within your range</p>
          </div>
        ) : (
          <>
            <h4 style={{ fontFamily: "var(--font-display)", fontWeight: 600, marginBottom: 20 }}>
              Options within {fmt(budget)}
            </h4>
            {result.options.length === 0 && (
              <p style={{ color: "var(--text-muted)" }}>No routes fit this budget yet — try raising it a little.</p>
            )}
            {result.options.map((o, i) => (
              <div className="budget-option" key={i}>
                <div>
                  <div className="bo-route">{o.route}</div>
                  <div className="bo-meta">{o.date} · {o.airline}</div>
                  <span className="bo-badge">{o.badge}</span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="bo-price">{fmt(o.price)}</div>
                  <div className="bo-saving">Save {fmt(o.saving)}</div>
                </div>
              </div>
            ))}
            <div className="budget-alt-section">
              <h4>Alternative Routes (with Connecting Travel)</h4>
              {result.alternatives.map((alt, i) => (
                <div className="alt-route" key={i}>
                  <span>{alt.label}</span>
                  <span className="alt-saving">Save {fmt(alt.saving)}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
