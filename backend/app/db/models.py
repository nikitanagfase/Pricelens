"""
db/models.py
─────────────────────────────────────────────
SQLAlchemy ORM models — the real tables behind
users, fare alerts, and search history.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("FareAlert", back_populates="owner", cascade="all, delete-orphan")
    searches = relationship("SearchHistory", back_populates="owner", cascade="all, delete-orphan")


class FareAlert(Base):
    __tablename__ = "fare_alerts"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    date_from = Column(String, nullable=True)
    date_to = Column(String, nullable=True)
    target_price = Column(Float, nullable=False)

    notify_on_drop = Column(Boolean, default=True)
    notify_below_budget = Column(Boolean, default=True)
    notify_below_average = Column(Boolean, default=False)
    notify_predicted_rise = Column(Boolean, default=False)
    notify_email = Column(Boolean, default=True)

    status = Column(String, default="active")     # active | triggered
    current_price = Column(Float, nullable=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="alerts")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    travel_date = Column(String, nullable=False)
    result_count = Column(Integer, default=0)
    cheapest_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="searches")


class PriceSnapshot(Base):
    """Cached historical price point — feeds the analytics dashboard
    even before/without live Ignav calls, and is what gets written
    to every time a real search happens (so the dashboard grows
    richer with real data over time)."""
    __tablename__ = "price_snapshots"

    id = Column(String, primary_key=True, default=gen_uuid)
    route = Column(String, index=True, nullable=False)   # e.g. "BOM-DEL"
    airline = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    days_before_travel = Column(Integer, nullable=True)
    travel_date = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String, default="mock")    # "ignav" | "mock"
