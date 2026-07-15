import { useEffect, useState } from "react";
import { HistoryLineChart, DayOfWeekChart, AirlineChart } from "../components/PriceChart";
import Heatmap from "../components/Heatmap";
import {
  getPriceHistory, getDayOfWeek, getAirlineComparison,
  getFestivals, getRouteStats, getHeatmap,
} from "../services/api";
import { useToast } from "../context/ToastContext";

const ROUTES = [
  { label: "Mumbai → Delhi", origin: "BOM", destination: "DEL" },
  { label: "Mumbai → Goa", origin: "BOM", destination: "GOI" },
  { label: "Delhi → Bangalore", origin: "DEL", destination: "BLR" },
  { label: "Mumbai → Bangalore", origin: "BOM", destination: "BLR" },
  { label: "Delhi → Hyderabad", origin: "DEL", destination: "HYD" },
  { label: "Kolkata → Delhi", origin: "CCU", destination: "DEL" },
];

function fmt(n) { return "₹" + Math.round(n).toLocaleString("en-IN"); }

export default function Analytics() {
  const [routeIdx, setRouteIdx] = useState(0);
  const [period, setPeriod] = useState("30d");
  const [history, setHistory] = useState(null);
  const [dow, setDow] = useState(null);
  const [airlines, setAirlines] = useState(null);
  const [festivals, setFestivals] = useState([]);
  const [stats, setStats] = useState(null);
  const [heatmap, setHeatmapData] = useState(null);
  const { show } = useToast();

  const route = ROUTES[routeIdx];

  useEffect(() => {
    getFestivals().then(setFestivals).catch(() => {});
  }, []);

  useEffect(() => {
    const { origin, destination } = route;
    getPriceHistory(origin, destination, period).then(setHistory).catch(() => {});
  }, [routeIdx, period]);

  useEffect(() => {
    const { origin, destination } = route;
    Promise.all([
      getDayOfWeek(origin, destination),
      getAirlineComparison(origin, destination),
      getRouteStats(origin, destination),
      getHeatmap(origin, destination),
    ])
      .then(([d, a, s, h]) => {
        setDow(d); setAirlines(a); setStats(s); setHeatmapData(h);
      })
      .catch(() => show("Couldn't load analytics — is the backend running?", "error"));
  }, [routeIdx]);

  return (
    <div className="page">
      <section className="section" id="analytics">
        <div className="container">
          <div className="section-header">
            
            <h2 className="section-title">Price Analytics & Festival Impact</h2>
            <p className="section-desc">Historical trends, demand patterns, and holiday surge analysis</p>
          </div>

          <div className="analytics-controls">
            <select className="analytics-select" value={routeIdx} onChange={(e) => setRouteIdx(Number(e.target.value))}>
              {ROUTES.map((r, i) => <option key={r.label} value={i}>{r.label}</option>)}
            </select>
            <div className="period-tabs">
              {["30d", "6m", "1y"].map((p) => (
                <button key={p} className={`period-btn ${period === p ? "active" : ""}`} onClick={() => setPeriod(p)}>
                  {p === "30d" ? "30 Days" : p === "6m" ? "6 Months" : "1 Year"}
                </button>
              ))}
            </div>
          </div>

          <div className="analytics-grid">
            <div className="chart-card big">
              <div className="chart-card-header">
                <h3>Historical Price Trend</h3>
                <div className="chart-legend">
                  <span><span className="legend-dot" style={{ background: "#6C63FF" }} />Avg</span>
                  <span><span className="legend-dot" style={{ background: "#FF6584" }} />Min</span>
                  <span><span className="legend-dot" style={{ background: "#43D9A5" }} />Max</span>
                </div>
              </div>
              <div className="chart-wrap">
                {history && <HistoryLineChart points={history.points} />}
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-card-header"><h3>Price by Day of Week</h3></div>
              <div className="chart-wrap">
                {dow && <DayOfWeekChart days={dow.days} prices={dow.prices} />}
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-card-header"><h3>Airline Price Comparison</h3></div>
              <div className="chart-wrap">
                {airlines && <AirlineChart airlines={airlines.airlines} prices={airlines.prices} />}
              </div>
            </div>

            <div className="chart-card festival-card">
              <div className="chart-card-header"><h3>Festival & Holiday Impact</h3></div>
              <div className="festival-list">
                {festivals.map((f) => (
                  <div className="festival-item" key={f.name}>
                    <div className="festival-info">
                      <span className="festival-icon">{f.icon}</span>
                      <div>
                        <div className="festival-name">{f.name}</div>
                        <div className="festival-date">{f.date}</div>
                      </div>
                    </div>
                    <span className={`festival-impact impact-${f.impact}`}>+{f.surge_pct}% surge</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="chart-card stats-card">
              <div className="chart-card-header"><h3>Route Intelligence</h3></div>
              {stats && (
                <div className="route-stats">
                  <div className="rs-item"><span className="rs-label">Popularity Score</span><span className="rs-value" style={{ color: "var(--teal)" }}>{stats.popularity_score}/100</span></div>
                  <div className="rs-item"><span className="rs-label">Average Fare</span><span className="rs-value">{fmt(stats.average_fare)}</span></div>
                  <div className="rs-item"><span className="rs-label">Cheapest Day</span><span className="rs-value" style={{ color: "var(--teal)" }}>{stats.cheapest_day}</span></div>
                  <div className="rs-item"><span className="rs-label">Best Booking Window</span><span className="rs-value">{stats.best_booking_window}</span></div>
                  <div className="rs-item"><span className="rs-label">Price Volatility</span><span className="rs-value" style={{ color: "var(--amber)" }}>{stats.price_volatility}</span></div>
                  <div className="rs-item"><span className="rs-label">Flights/Day</span><span className="rs-value">{stats.flights_per_day}</span></div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="section section-dark" id="heatmap">
        <div className="container">
          <div className="section-header">
         
            <h2 className="section-title">Price Heatmap Calendar</h2>
            <p className="section-desc">Visualise cheapest and costliest days for {route.label} at a glance</p>
          </div>
          <div className="heatmap-controls">
            <div />
            <div className="heatmap-legend">
              <span className="heat-key" style={{ background: "#43D9A5" }}>Cheap</span>
              <span className="heat-key" style={{ background: "#FFB347" }}>Average</span>
              <span className="heat-key" style={{ background: "#FF6584" }}>Expensive</span>
            </div>
          </div>
          <Heatmap data={heatmap} onSelectDay={(d) => show(`${d.day} — ${fmt(d.price)}`, "info")} />
        </div>
      </section>
    </div>
  );
}
