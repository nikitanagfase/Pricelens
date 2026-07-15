"""
api/routes/alerts.py
─────────────────────────────────────────────
Smart Fare Alerts — full CRUD, backed by real DB
rows (not the in-memory array the old prototype used).

GET /api/alerts        → list the user's alerts,
                          refreshing each one's current
                          price via the flight-search
                          service and flipping status to
                          "triggered" + firing a
                          notification when the target is met.
POST /api/alerts        → create
DELETE /api/alerts/{id} → remove
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db import schemas, crud
from app.services.ignav_client import search_flights
from app.services.notification_service import send_email_alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _refresh_alert_price(db: Session, alert):
    """Looks up today's cheapest fare for the alert's route and
    updates status/current_price. Fires a notification exactly
    once when it crosses into 'triggered'."""
    travel_date = alert.date_from or datetime.now().strftime("%Y-%m-%d")
    offers, _source = search_flights(alert.origin, alert.destination, travel_date)
    if not offers:
        return alert

    cheapest = min(o["price"] for o in offers)
    was_active = alert.status == "active"
    alert.current_price = cheapest
    alert.last_checked = datetime.utcnow()

    should_trigger = (
        (alert.notify_below_budget and cheapest <= alert.target_price)
        or (alert.notify_on_drop and cheapest <= alert.target_price * 0.95)
    )
    alert.status = "triggered" if should_trigger else "active"

    if was_active and alert.status == "triggered" and alert.notify_email:
        send_email_alert(
            to_email=alert.owner.email,
            subject=f"Fare alert: {alert.origin} → {alert.destination}",
            body=f"Price dropped to ₹{cheapest:.0f}, below your target of ₹{alert.target_price:.0f}!",
        )

    db.commit()
    return alert


@router.get("", response_model=list[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    alerts = crud.list_alerts(db, user.id)
    for a in alerts:
        _refresh_alert_price(db, a)
    return alerts


@router.post("", response_model=schemas.AlertOut)
def create_alert(
    payload: schemas.AlertCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    alert = crud.create_alert(db, user.id, payload)
    _refresh_alert_price(db, alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(alert_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ok = crud.delete_alert(db, user.id, alert_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"deleted": True}
