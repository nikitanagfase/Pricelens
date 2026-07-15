import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import Predictor from "../components/Predictor";
import BudgetPlanner from "../components/BudgetPlanner";
import AlertsPanel from "../components/AlertsPanel";

const TABS = [
  { id: "predictor", label: "🔮 Predictor", eyebrow: "", title: "Price Predictor", desc: "Explainable machine learning — not just predictions, but reasons" },
  { id: "budget", label: "💰 Budget Planner", eyebrow: "", title: "Budget Planner", desc: "Enter your budget — we'll find the best dates, airlines, and alternatives" },
  { id: "alerts", label: "🔔 Smart Alerts", eyebrow: "", title: "Smart Fare Alerts", desc: "Get notified only when it truly matters — no noise, just signals" },
];

export default function Dashboard() {
  const [params, setParams] = useSearchParams();
  const initialTab = params.get("tab") || "predictor";
  const [tab, setTab] = useState(TABS.some((t) => t.id === initialTab) ? initialTab : "predictor");

  const active = TABS.find((t) => t.id === tab);

  const selectTab = (id) => {
    setTab(id);
    setParams({ tab: id });
  };

  return (
    <div className="page">
      <section className="section">
        <div className="container">
          <div className="section-header">
            <span className="section-eyebrow">{active.eyebrow}</span>
            <h2 className="section-title">{active.title}</h2>
            <p className="section-desc">{active.desc}</p>
          </div>

          <div className="tab-bar" style={{ margin: "0 auto 40px" }}>
            {TABS.map((t) => (
              <button key={t.id} className={`tab-btn ${tab === t.id ? "active" : ""}`} onClick={() => selectTab(t.id)}>
                {t.label}
              </button>
            ))}
          </div>

          {tab === "predictor" && <Predictor />}
          {tab === "budget" && <BudgetPlanner />}
          {tab === "alerts" && <AlertsPanel />}
        </div>
      </section>
    </div>
  );
}
