import { useState } from "react";

const CITIES = [
  { name: "Mumbai", code: "BOM" }, { name: "Delhi", code: "DEL" },
  { name: "Bangalore", code: "BLR" }, { name: "Goa", code: "GOI" },
  { name: "Hyderabad", code: "HYD" }, { name: "Kolkata", code: "CCU" },
  { name: "Chennai", code: "MAA" }, { name: "Jaipur", code: "JAI" },
  { name: "Nagpur", code: "NAG" }, { name: "Pune", code: "PNQ" },
];

function defaultDate(daysAhead) {
  const d = new Date();
  d.setDate(d.getDate() + daysAhead);
  return d.toISOString().split("T")[0];
}

export default function SearchForm({ onSearch, loading }) {
  const [tripType, setTripType] = useState("oneway");
  const [origin, setOrigin] = useState("BOM");
  const [destination, setDestination] = useState("DEL");
  const [departureDate, setDepartureDate] = useState(defaultDate(7));
  const [returnDate, setReturnDate] = useState(defaultDate(14));
  const [adults, setAdults] = useState(1);
  const [travelClass, setTravelClass] = useState("ECONOMY");
  const [directOnly, setDirectOnly] = useState(false);

  const swap = () => {
    setOrigin(destination);
    setDestination(origin);
  };

  const submit = (e) => {
    e.preventDefault();
    onSearch({
      origin,
      destination,
      departure_date: departureDate,
      return_date: tripType === "roundtrip" ? returnDate : null,
      adults: Number(adults),
      travel_class: travelClass,
      direct_only: directOnly,
    });
  };

  return (
    <div className="search-card">
      <div className="trip-toggle">
        {["oneway", "roundtrip", "multicity"].map((t) => (
          <button
            key={t}
            type="button"
            className={`toggle-btn ${tripType === t ? "active" : ""}`}
            onClick={() => setTripType(t)}
          >
            {t === "oneway" ? "One Way" : t === "roundtrip" ? "Round Trip" : "Multi-City"}
          </button>
        ))}
      </div>

      <form onSubmit={submit}>
        <div className="search-grid">
          <div className="input-group">
            <label>From</label>
            <div className="input-with-icon">
              <span className="inp-icon">🛫</span>
              <select className="search-input" value={origin} onChange={(e) => setOrigin(e.target.value)}>
                {CITIES.map((c) => <option key={c.code} value={c.code}>{c.name} ({c.code})</option>)}
              </select>
            </div>
          </div>

          <button type="button" className="swap-btn" onClick={swap} title="Swap cities">⇄</button>

          <div className="input-group">
            <label>To</label>
            <div className="input-with-icon">
              <span className="inp-icon">🛬</span>
              <select className="search-input" value={destination} onChange={(e) => setDestination(e.target.value)}>
                {CITIES.map((c) => <option key={c.code} value={c.code}>{c.name} ({c.code})</option>)}
              </select>
            </div>
          </div>

          <div className="input-group">
            <label>Departure</label>
            <div className="input-with-icon">
              <span className="inp-icon">📅</span>
              <input type="date" className="search-input" value={departureDate}
                     onChange={(e) => setDepartureDate(e.target.value)} required />
            </div>
          </div>

          {tripType === "roundtrip" && (
            <div className="input-group">
              <label>Return</label>
              <div className="input-with-icon">
                <span className="inp-icon">📅</span>
                <input type="date" className="search-input" value={returnDate}
                       onChange={(e) => setReturnDate(e.target.value)} />
              </div>
            </div>
          )}

          <div className="input-group">
            <label>Passengers</label>
            <div className="input-with-icon">
              <span className="inp-icon">👤</span>
              <select className="search-input" value={adults} onChange={(e) => setAdults(e.target.value)}>
                {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n} Adult{n > 1 ? "s" : ""}</option>)}
              </select>
            </div>
          </div>

          <div className="input-group">
            <label>Class</label>
            <div className="input-with-icon">
              <span className="inp-icon">💺</span>
              <select className="search-input" value={travelClass} onChange={(e) => setTravelClass(e.target.value)}>
                <option value="ECONOMY">Economy</option>
                <option value="PREMIUM_ECONOMY">Premium Economy</option>
                <option value="BUSINESS">Business</option>
                <option value="FIRST">First Class</option>
              </select>
            </div>
          </div>
        </div>

        <div className="search-extras">
          <label className="checkbox-label">
            <input type="checkbox" checked={directOnly} onChange={(e) => setDirectOnly(e.target.checked)} />
            <span>Direct flights only</span>
          </label>
        </div>

        <button className="btn-search" type="submit" disabled={loading}>
          {loading ? <span className="loading-spinner" /> : <span>🔍</span>}
          {loading ? "Searching..." : "Search & Analyse Fares"}
        </button>
      </form>
    </div>
  );
}
