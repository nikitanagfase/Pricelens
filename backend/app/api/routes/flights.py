"""
api/routes/flights.py
─────────────────────────────────────────────
POST /api/flights/search → real Ignav search if
configured, else clearly-labeled mock data. Every
search is logged to price_snapshots so the analytics
dashboard keeps getting richer real history over time.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_optional_user
from app.services.ignav_client import search_flights
from app.db import schemas, crud
from app.utils.helpers import route_key

router = APIRouter(prefix="/api/flights", tags=["flights"])


@router.post("/search", response_model=schemas.FlightSearchResponse)
def search(
    payload: schemas.FlightSearchRequest,
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
):
    offers, source = search_flights(
        origin=payload.origin.upper(),
        destination=payload.destination.upper(),
        departure_date=payload.departure_date,
        return_date=payload.return_date,
        adults=payload.adults,
        travel_class=payload.travel_class,
        direct_only=payload.direct_only,
        max_price=payload.max_price,
    )

    route = route_key(payload.origin, payload.destination)
    cheapest = min((o["price"] for o in offers), default=None)

    # log for analytics history + search history
    try:
        travel_dt = datetime.strptime(payload.departure_date, "%Y-%m-%d")
        days_before = max((travel_dt - datetime.now()).days, 0)
    except ValueError:
        days_before = None

    for o in offers:
        crud.save_price_snapshot(
            db, route=route, airline=o["airline_name"], price=o["price"],
            days_before_travel=days_before, travel_date=payload.departure_date, source=source,
        )
        
    crud.log_search(
        db, user_id=user.id if user else None, origin=payload.origin,
        destination=payload.destination, travel_date=payload.departure_date,
        result_count=len(offers), cheapest_price=cheapest,
    )

    return schemas.FlightSearchResponse(
        count=len(offers),
        source=source,
        results=[schemas.FlightOffer(**o) for o in offers],
    )
