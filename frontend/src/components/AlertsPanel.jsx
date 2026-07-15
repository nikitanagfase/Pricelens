import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { listAlerts, createAlert, deleteAlert } from "../services/api";

const CITIES = ["BOM", "DEL", "BLR", "GOI", "HYD", "CCU", "MAA", "JAI", "NAG", "PNQ"];

export default function AlertsPanel() {
  const { user } = useAuth();
  const { show } = useToast();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [origin, setOrigin] = useState("BOM");
  const [destination, setDestination] = useState("DEL");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [targetPrice, setTargetPrice] = useState(5000);
  const [notifyDrop, setNotifyDrop] = useState(true);
  const [notifyBudget, setNotifyBudget] = useState(true);
  const [notifyEmail, setNotifyEmail] = useState(true);

  const refresh = async () => {
    if (!user) return;
    setLoading(true);
    try {
      setAlerts(await listAlerts());
    } catch {
      // silently ignore — likely a stale token
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, [user]);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await createAlert({
        origin, destination,
        date_from: dateFrom || null, date_to: dateTo || null,
        target_price: Number(targetPrice),
        notify_on_drop: notifyDrop, notify_below_budget: notifyBudget,
        notify_below_average: false, notify_predicted_rise: false,
        notify_email: notifyEmail,
      });
      show("Fare alert created!", "success");
      refresh();
    } catch {
      show("Couldn't create alert. Try again.", "error");
    }
  };

  const remove = async (id) => {
    try {
      await deleteAlert(id);
      setAlerts((a) => a.filter((x) => x.id !== id));
      show("Alert removed", "info");
    } catch {
      show("Couldn't remove alert.", "error");
    }
  };

  if (!user) {
    return (
      <div className="login-required-note">
        <div className="empty-state-icon">🔔</div>
        <p>Smart fare alerts are saved to your account — please log in or sign up to create one.</p>
      </div>
    );
  }

  return (
    <div className="alerts-layout">
      <div className="alert-form-card">
        <h3>Create Fare Alert</h3>
        <form className="alert-form" onSubmit={submit}>
          <div className="alert-field">
            <label>Route</label>
            <div className="route-inputs">
              <select className="alert-input" value={origin} onChange={(e) => setOrigin(e.target.value)}>
                {CITIES.map((c) => <option key={c}>{c}</option>)}
              </select>
              <span>→</span>
              <select className="alert-input" value={destination} onChange={(e) => setDestination(e.target.value)}>
                {CITIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
          </div>
          <div className="alert-field">
            <label>Date Range</label>
            <div className="route-inputs">
              <input type="date" className="alert-input" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
              <span>to</span>
              <input type="date" className="alert-input" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
            </div>
          </div>
          <div className="alert-field">
            <label>Target Price</label>
            <div className="budget-input-wrap">
              <span className="currency">₹</span>
              <input type="number" className="budget-input" value={targetPrice} onChange={(e) => setTargetPrice(e.target.value)} />
            </div>
          </div>
          <div className="alert-field">
            <label>Notify When</label>
            <div className="notify-options">
              <label className="checkbox-label">
                <input type="checkbox" checked={notifyDrop} onChange={(e) => setNotifyDrop(e.target.checked)} /> Price drops 5%+
              </label>
              <label className="checkbox-label">
                <input type="checkbox" checked={notifyBudget} onChange={(e) => setNotifyBudget(e.target.checked)} /> Below my target
              </label>
            </div>
          </div>
          <div className="alert-field">
            <label>Notification Via</label>
            <div className="notify-options">
              <label className="checkbox-label">
                <input type="checkbox" checked={notifyEmail} onChange={(e) => setNotifyEmail(e.target.checked)} /> Email
              </label>
            </div>
          </div>
          <button className="btn-predict" type="submit">🔔 Create Alert</button>
        </form>
      </div>

      <div className="active-alerts-card">
        <h3>Active Alerts</h3>
        {loading ? (
          <p style={{ color: "var(--text-muted)" }}>Loading...</p>
        ) : alerts.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>No active alerts. Create one to get notified.</p>
        ) : (
          <div className="alerts-list">
            {alerts.map((a) => (
              <div className="alert-item" key={a.id}>
                <div className="alert-item-header">
                  <div className="alert-route">{a.origin} → {a.destination}</div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span className={`alert-status-badge ${a.status}`}>
                      {a.status === "active" ? "🟢 Active" : "🔔 Triggered"}
                    </span>
                    <button className="delete-alert-btn" onClick={() => remove(a.id)}>✕</button>
                  </div>
                </div>
                <div className="alert-meta">
                  <span>📅 {a.date_from || "Any date"}{a.date_to ? ` – ${a.date_to}` : ""}</span>
                  <span>🎯 Target: ₹{a.target_price.toLocaleString("en-IN")}</span>
                  {a.current_price != null && <span>💰 Current: ₹{Math.round(a.current_price).toLocaleString("en-IN")}</span>}
                </div>
                {a.status === "triggered" && (
                  <div className="alert-triggered-msg">🔔 Price is at or below your target — book now!</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
