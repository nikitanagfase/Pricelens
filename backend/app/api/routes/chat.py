"""
api/routes/chat.py
─────────────────────────────────────────────
Bonus module. Pulls LIVE flight data from Ignav
(via the same search_flights() used in flights.py)
and feeds it to Claude as context, so answers are
grounded in real current prices — not just canned
historical text. Falls back to keyword-matched
canned answers only if Ignav + Claude both fail.
"""
import httpx

from fastapi import APIRouter

from app.core.config import settings
from app.db import schemas
from app.services.ignav_client import search_flights

router = APIRouter(prefix="/api/chat", tags=["chat"])

CITY_CODES = {
    "mumbai": "BOM", "delhi": "DEL", "goa": "GOI", "bangalore": "BLR",
    "bengaluru": "BLR", "pune": "PNQ", "hyderabad": "HYD", "chennai": "MAA",
    "kolkata": "CCU", "jaipur": "JAI",
}

FALLBACK_RESPONSES = {
    "goa": "For Mumbai → Goa, the cheapest days are Tuesday and Wednesday. Budget airlines often have fares as low as ₹2,800 if you book 3–4 weeks ahead. Avoid booking during Diwali or Christmas — prices surge 60–70%.",
    "delhi": "Mumbai → Delhi is a high-demand corridor with 40+ daily flights. Best strategy: book 3 weeks ahead on a Tuesday morning for the lowest fares.",
    "diwali": "Diwali will cause a ~62% fare surge on most Indian routes. Prices start rising 2 weeks before and stay high for a week after — book early if you must travel then.",
    "cheap": "To find cheaper flights: book 21–45 days ahead, fly Tuesday/Wednesday, use early-morning flights (5–7 AM), and set a fare alert for your route.",
}
DEFAULT_REPLY = "Based on historical patterns, booking 21–45 days before travel and flying on a Tuesday or Wednesday usually gets the lowest fares. Ask me about a specific route or festival for more detail!"


def _fallback_reply(message: str) -> str:
    m = message.lower()
    for key, reply in FALLBACK_RESPONSES.items():
        if key in m:
            return reply
    return DEFAULT_REPLY


def _extract_route(payload: schemas.ChatRequest):
    origin = getattr(payload, "origin", None)
    destination = getattr(payload, "destination", None)
    if origin and destination:
        return origin.upper(), destination.upper()

    m = payload.message.lower()
    found = [code for city, code in CITY_CODES.items() if city in m]
    if len(found) >= 2:
        return found[0], found[1]
    return None, None


def _live_context(payload: schemas.ChatRequest) -> str:
    origin, destination = _extract_route(payload)
    if not origin or not destination:
        return ""

    travel_date = getattr(payload, "travel_date", None) or "2026-08-15"

    try:
        offers, source = search_flights(
            origin=origin,
            destination=destination,
            departure_date=travel_date,
            return_date=None,
            adults=1,
            travel_class="ECONOMY",
            direct_only=False,
            max_price=None,
        )
    except Exception as e:
        print("IGNAV LIVE CONTEXT FAILED:", repr(e), flush=True)
        return ""

    if not offers:
        return ""

    top = sorted(offers, key=lambda o: o["price"])[:5]
    lines = [f"- {o['airline_name']}: ₹{o['price']}" for o in top]
    return (
        f"\n\nLive Ignav data for {origin} → {destination} on {travel_date} "
        f"(source: {source}):\n" + "\n".join(lines)
    )


@router.post("", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest):
    live_context = _live_context(payload)

    if settings.ANTHROPIC_API_KEY:
        try:
            system_prompt = (
                "You are SkyFare Insights' travel assistant. Answer briefly "
                "(2-4 sentences) and practically about Indian domestic flight "
                "prices, booking timing, and travel planning. If live flight "
                "data is provided below, base your answer on it and mention "
                "actual prices instead of only general trends."
                + live_context
            )
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-5",
                    "max_tokens": 400,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": payload.message}],
                },
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(
                b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
            )
            if text:
                return schemas.ChatResponse(
                    reply=text,
                    source="claude+ignav" if live_context else "claude",
                )
        except httpx.HTTPStatusError as e:
            print("CLAUDE API CALL FAILED:", repr(e), flush=True)
            print("ANTHROPIC RESPONSE BODY:", e.response.text, flush=True)
        except Exception as e:
            print("CLAUDE API CALL FAILED:", repr(e), flush=True)

    # Fallback: Claude API key missing, or the call above failed / returned no text
    return schemas.ChatResponse(
        reply=_fallback_reply(payload.message),
        source="fallback",
    )