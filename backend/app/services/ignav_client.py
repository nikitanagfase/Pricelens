"""
services/ignav_client.py
─────────────────────────────────────────────
Thin wrapper around the Ignav Flight Fares API.

IMPORTANT — how this behaves:
  • If IGNAV_API_KEY is set in .env → real calls go
    to Ignav's live fare search.
  • If it's blank (default) → search_flights()
    returns clearly-labeled MOCK data instead of
    crashing. This means the project runs end-to-end
    on day one, before you've even signed up for a key.

Get free key (1,000 free requests, no card): https://ignav.com
"""
import random
from typing import Optional

import httpx

from app.core.config import settings
from app.services.cache_service import cache_get, cache_set

AIRLINES = [
    {"code": "6E", "name": "IndiGo"},
    {"code": "AI", "name": "Air India"},
    {"code": "SG", "name": "SpiceJet"},
    {"code": "UK", "name": "Vistara"},
    {"code": "I5", "name": "AirAsia India"},
]

USD_TO_INR = 88  # fallback conversion rate, used only if Ignav returns non-INR


def _calc_arrival(dep_time: str, duration_minutes: int) -> str:
    h, m = map(int, dep_time.split(":"))
    total = h * 60 + m + duration_minutes
    return f"{(total // 60) % 24:02d}:{total % 60:02d}"


def _predict_label(price: float, avg_price: float) -> tuple[str, str]:
    diff_pct = (price - avg_price) / avg_price if avg_price else 0
    if diff_pct < -0.05:
        return "drop", "Price dropping"
    if diff_pct > 0.05:
        return "rise", "Price rising — Book now"
    return "stable", "Price stable"


def _generate_mock_offers(origin: str, destination: str, departure_date: str,
                           direct_only: bool = False, max_price: Optional[int] = None) -> list[dict]:
    """Deterministic-ish, realistic mock flight list.
    Seeded by route+date so the same search returns
    consistent results within a session (not pure noise)."""
    seed_str = f"{origin}-{destination}-{departure_date}"
    rng = random.Random(seed_str)

    base_prices = [4100, 4380, 4820, 5200, 5650, 5900, 6200]
    times = ["05:30", "06:15", "07:45", "09:00", "11:30", "13:15", "15:00", "17:30", "19:00", "21:45"]
    avg_price = sum(base_prices) / len(base_prices)

    offers = []
    for ai, airline in enumerate(AIRLINES):
        n_flights = rng.randint(1, 3)
        for _ in range(n_flights):
            dep = rng.choice(times)
            dur = rng.randint(100, 180)
            price = base_prices[rng.randrange(len(base_prices))] + ai * 120 + rng.randint(-200, 300)
            price = max(2500, price)
            stops = "Non-stop" if rng.random() > 0.45 else "1 Stop"
            if direct_only and stops != "Non-stop":
                continue
            if max_price and price > max_price:
                continue
            trend, label = _predict_label(price, avg_price)
            offers.append({
                "airline_code": airline["code"],
                "airline_name": airline["name"],
                "flight_number": f"{airline['code']}{rng.randint(100, 999)}",
                "departure_time": dep,
                "arrival_time": _calc_arrival(dep, dur),
                "duration": f"{dur // 60}h {dur % 60}m",
                "stops": stops,
                "price": float(price),
                "currency": "INR",
                "confidence": rng.randint(76, 97),
                "prediction_label": label,
                "prediction_trend": trend,
            })
    offers.sort(key=lambda o: o["price"])
    return offers


def _parse_ignav_offers(raw: dict) -> list[dict]:
    """Maps Ignav's response shape down to our flat FlightOffer shape."""
    offers = []
    itineraries = raw.get("itineraries", [])
    prices = [float(it["price"]["amount"]) for it in itineraries] or [0]
    avg_price = sum(prices) / len(prices)

    for it in itineraries:
        try:
            outbound = it["outbound"]
            segments = outbound["segments"]
            first_seg, last_seg = segments[0], segments[-1]
            carrier_code = first_seg.get("marketing_carrier_code", "")
            carrier_name = first_seg.get("operating_carrier_name", carrier_code)

            price_val = float(it["price"]["amount"])
            currency = it["price"].get("currency", "USD")
            price_inr = price_val if currency == "INR" else round(price_val * USD_TO_INR)

            trend, label = _predict_label(price_inr, avg_price if currency == "INR" else avg_price * USD_TO_INR)
            dur_min = outbound.get("duration_minutes", 0)

            offers.append({
                "airline_code": carrier_code,
                "airline_name": carrier_name,
                "flight_number": f"{carrier_code}{first_seg.get('flight_number', '')}",
                "departure_time": first_seg["departure_time_local"][11:16],
                "arrival_time": last_seg["arrival_time_local"][11:16],
                "duration": f"{dur_min // 60}h {dur_min % 60}m",
                "stops": "Non-stop" if len(segments) == 1 else f"{len(segments) - 1} Stop",
                "price": float(price_inr),
                "currency": "INR",
                "confidence": 90,   # Ignav doesn't give this — predictor route owns confidence math
                "prediction_label": label,
                "prediction_trend": trend,
            })
        except (KeyError, IndexError, ValueError):
            continue
    return offers


def search_flights(origin: str, destination: str, departure_date: str,
                    return_date: Optional[str] = None, adults: int = 1,
                    travel_class: str = "ECONOMY", direct_only: bool = False,
                    max_price: Optional[int] = None) -> tuple[list[dict], str]:
    """Returns (offers, source) where source is 'ignav' or 'mock'."""
    cache_key = f"flights:{origin}:{destination}:{departure_date}:{adults}:{travel_class}:{direct_only}:{max_price}"
    cached = cache_get(cache_key)
    if cached:
        return cached["offers"], cached["source"]

    if settings.ignav_configured:
        try:
            body = {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "market": "IN",
                "adults": adults,
                "cabin_class": travel_class.lower(),
            }
            if direct_only:
                body["max_stops"] = 0
            if max_price:
                body["max_price"] = max_price

            resp = httpx.post(
                "https://ignav.com/api/fares/one-way",
                headers={"X-Api-Key": settings.IGNAV_API_KEY},
                json=body,
                timeout=15,
            )
            resp.raise_for_status()
            offers = _parse_ignav_offers(resp.json())
            if offers:
                cache_set(cache_key, {"offers": offers, "source": "ignav"}, ttl_seconds=900)
                return offers, "ignav"
        except Exception:
            pass   # fall through to mock

    offers = _generate_mock_offers(origin, destination, departure_date, direct_only, max_price)
    cache_set(cache_key, {"offers": offers, "source": "mock"}, ttl_seconds=900)
    return offers, "mock"