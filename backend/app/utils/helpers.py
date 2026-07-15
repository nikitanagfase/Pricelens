"""
utils/helpers.py
─────────────────────────────────────────────
Static reference data + small helpers shared
across analytics/predict/budget routes.
"""
import random
from datetime import datetime, timedelta

CITIES = {
    "BOM": "Mumbai", "DEL": "Delhi", "BLR": "Bangalore", "GOI": "Goa",
    "HYD": "Hyderabad", "CCU": "Kolkata", "MAA": "Chennai", "JAI": "Jaipur",
    "NAG": "Nagpur", "PNQ": "Pune",
}

AIRLINE_NAMES = ["IndiGo", "Air India", "SpiceJet", "Vistara", "AirAsia India"]

# Festival impact data — 2026 dates (update yearly)
FESTIVALS = [
    {"name": "Holi", "date": "2026-03-14", "icon": "🎨", "impact": "low", "surge_pct": 15},
    {"name": "Eid", "date": "2026-03-30", "icon": "🌙", "impact": "med", "surge_pct": 28},
    {"name": "Independence Day", "date": "2026-08-15", "icon": "🇮🇳", "impact": "med", "surge_pct": 22},
    {"name": "Dussehra", "date": "2026-10-02", "icon": "🎆", "impact": "med", "surge_pct": 34},
    {"name": "Diwali", "date": "2026-10-20", "icon": "🪔", "impact": "high", "surge_pct": 62},
    {"name": "Christmas", "date": "2026-12-25", "icon": "🎄", "impact": "high", "surge_pct": 58},
]

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Base weekly price curve per route (used to seed both the ML
# training set AND the analytics endpoints, so charts + predictor
# stay internally consistent)
ROUTE_BASE_PRICE = {
    "BOM-DEL": 5400, "BOM-GOI": 4000, "DEL-BLR": 5100, "BOM-BLR": 4600,
    "DEL-HYD": 3900, "CCU-DEL": 4500, "NAG-DEL": 4200, "NAG-BOM": 3200,
}

DAY_OF_WEEK_MULTIPLIER = {
    0: 1.05, 1: 0.92, 2: 0.95, 3: 1.0, 4: 1.28, 5: 1.42, 6: 1.18,
}  # Mon..Sun — Fri/Sat priciest, Tue cheapest (realistic Indian domestic pattern)


def route_key(origin: str, destination: str) -> str:
    return f"{origin.upper()}-{destination.upper()}"


def base_price_for_route(route: str) -> float:
    return ROUTE_BASE_PRICE.get(route, 4800)


def nearest_festival_surge(travel_date_str: str) -> float:
    """Returns the surge multiplier (0 if no festival within 10 days)."""
    try:
        travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d")
    except ValueError:
        return 0.0
    best = 0.0
    for f in FESTIVALS:
        f_date = datetime.strptime(f["date"], "%Y-%m-%d")
        diff_days = abs((f_date - travel_date).days)
        if diff_days <= 10:
            decay = max(0, 1 - diff_days / 10)
            best = max(best, f["surge_pct"] * decay / 100)
    return best


def seeded_rng(*parts) -> random.Random:
    return random.Random("-".join(str(p) for p in parts))
