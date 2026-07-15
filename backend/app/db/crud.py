"""
db/crud.py
─────────────────────────────────────────────
Plain functions that talk to the database.
Routes call these instead of writing raw
SQLAlchemy queries inline — keeps routes thin.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.db import models
from app.core.security import hash_password


# ── Users ─────────────────────────────────────────────
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, full_name: str, email: str, password: str) -> models.User:
    user = models.User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Fare Alerts ───────────────────────────────────────
def create_alert(db: Session, user_id: str, payload) -> models.FareAlert:
    alert = models.FareAlert(user_id=user_id, **payload.dict())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_alerts(db: Session, user_id: str) -> List[models.FareAlert]:
    return (
        db.query(models.FareAlert)
        .filter(models.FareAlert.user_id == user_id)
        .order_by(models.FareAlert.created_at.desc())
        .all()
    )


def delete_alert(db: Session, user_id: str, alert_id: str) -> bool:
    alert = (
        db.query(models.FareAlert)
        .filter(models.FareAlert.id == alert_id, models.FareAlert.user_id == user_id)
        .first()
    )
    if not alert:
        return False
    db.delete(alert)
    db.commit()
    return True


# ── Price Snapshots (analytics history) ──────────────
def save_price_snapshot(db: Session, route: str, airline: str, price: float,
                         days_before_travel: int, travel_date: str, source: str):
    snap = models.PriceSnapshot(
        route=route, airline=airline, price=price,
        days_before_travel=days_before_travel,
        travel_date=travel_date, source=source,
    )
    db.add(snap)
    db.commit()


def get_recent_snapshots(db: Session, route: str, limit: int = 200):
    return (
        db.query(models.PriceSnapshot)
        .filter(models.PriceSnapshot.route == route)
        .order_by(models.PriceSnapshot.recorded_at.desc())
        .limit(limit)
        .all()
    )


# ── Search History ────────────────────────────────────
def log_search(db: Session, user_id: Optional[str], origin: str, destination: str,
                travel_date: str, result_count: int, cheapest_price: Optional[float]):
    record = models.SearchHistory(
        user_id=user_id, origin=origin, destination=destination,
        travel_date=travel_date, result_count=result_count,
        cheapest_price=cheapest_price,
    )
    db.add(record)
    db.commit()
