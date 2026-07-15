import { useEffect, useState } from "react";
import SearchForm from "../components/SearchForm";
import FlightResults from "../components/FlightResults";
import { searchFlights } from "../services/api";
import { useToast } from "../context/ToastContext";

function AnimatedStat({ target, suffix = "", prefix = "" }) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    let current = 0;
    const step = target / 60;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      setVal(Math.round(current));
      if (current >= target) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [target]);
  return <span>{prefix}{val.toLocaleString("en-IN")}{suffix}</span>;
}

export default function Home() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const { show } = useToast();

  const handleSearch = async (payload) => {
    setLoading(true);
    try {
      const data = await searchFlights(payload);
      setResults(data);
      show(`Found ${data.count} flights (${data.source === "mock" ? "demo data" : "live Ignav data"})`, "success");
      setTimeout(() => {
        document.getElementById("results-anchor")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      show("Search failed — is the backend running?", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <section className="hero" id="hero">
        <div className="hero-bg" />
        <div className="hero-content">
          <div className="hero-badge">
            <span className="pulse-dot" />
            Price Intelligence Engine
          </div>
          <h1 className="hero-title">
            See Through<br />
            <span className="title-gradient">Every Fare.</span>
          </h1>
          <p className="hero-subtitle">
            Predict prices, decode trends, and travel at exactly the right moment —
            powered by an explainable machine learning model.
          </p>
          <div className="hero-cta">
            <button className="btn-hero" onClick={() => document.getElementById("search")?.scrollIntoView({ behavior: "smooth" })}>
              Analyse Flights
            </button>
          </div>
          <div className="hero-stats">
            <div className="stat-item"><span><AnimatedStat target={94} suffix="%" /></span><span className="stat-label">Prediction Accuracy*</span></div>
            <div className="stat-divider" />
            <div className="stat-item"><span><AnimatedStat target={8} /></span><span className="stat-label">Routes Covered</span></div>
            <div className="stat-divider" />
            <div className="stat-item"><span><AnimatedStat target={3200} prefix="₹" /></span><span className="stat-label">Avg. Savings/Booking*</span></div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="flight-card floating">
            <div className="fc-header">
              <span className="fc-route">BOM → DEL</span>
              <span className="fc-badge good">Book Now</span>
            </div>
            <div className="fc-price">₹4,820</div>
            <div className="fc-meta">IndiGo · 2h 05m · Non-stop</div>
            <div className="fc-predict">
              <span className="predict-label">Prediction</span>
              <div className="predict-bar"><div className="predict-fill" style={{ width: "78%" }} /></div>
              <span className="predict-conf">92% confident — prices rise in 3 days</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="search">
        <div className="container">
          <div className="section-header">
            
            <h2 className="section-title">Search Flights</h2>
            <p className="section-desc">Find and compare fares with ML-backed predictions on every result</p>
          </div>
          <SearchForm onSearch={handleSearch} loading={loading} />
          <div id="results-anchor" />
          <FlightResults data={results} onBook={() => show("Redirecting to booking...", "info")} />
        </div>
      </section>
    </div>
  );
}
