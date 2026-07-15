"""
db/schemas.py
─────────────────────────────────────────────
Pydantic models — define the exact JSON shape
the frontend sends and receives. This is the
single source of truth for field names, so
frontend/backend never drift apart again.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────
class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    full_name: str
    email: str

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()


# ── Flight Search ─────────────────────────────────────
class FlightSearchRequest(BaseModel):
    origin: str            # IATA code, e.g. "BOM"
    destination: str       # IATA code, e.g. "DEL"
    departure_date: str    # YYYY-MM-DD
    return_date: Optional[str] = None
    adults: int = 1
    travel_class: str = "ECONOMY"
    direct_only: bool = False
    max_price: Optional[int] = None


class FlightOffer(BaseModel):
    airline_code: str
    airline_name: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: str
    price: float
    currency: str = "INR"
    confidence: int
    prediction_label: str
    prediction_trend: str   # "rise" | "drop" | "stable"


class FlightSearchResponse(BaseModel):
    count: int
    source: str             # "ignav" | "mock"
    results: List[FlightOffer]


# ── Price Prediction ───────────────────────────────────
class PredictionRequest(BaseModel):
    origin: str
    destination: str
    travel_date: str
    days_before_travel: int = Field(ge=0, le=365)
    airline: Optional[str] = "Any"
    travel_class: str = "Economy"


class FeatureImportance(BaseModel):
    label: str
    pct: float
    color: str


class PredictionResponse(BaseModel):
    predicted_price: float
    confidence: int
    lower_bound: float
    upper_bound: float
    verdict: str             # "book" | "wait"
    verdict_message: str
    feature_importance: List[FeatureImportance]


# ── Analytics ──────────────────────────────────────────
class HistoryPoint(BaseModel):
    label: str
    avg: float
    min: float
    max: float


class PriceHistoryResponse(BaseModel):
    period: str
    route: str
    points: List[HistoryPoint]


class DayOfWeekResponse(BaseModel):
    route: str
    days: List[str]
    prices: List[float]


class AirlinePriceResponse(BaseModel):
    route: str
    airlines: List[str]
    prices: List[float]


class FestivalImpact(BaseModel):
    name: str
    date: str
    icon: str
    impact: str          # "high" | "med" | "low"
    surge_pct: float


class RouteStats(BaseModel):
    popularity_score: int
    average_fare: float
    cheapest_day: str
    best_booking_window: str
    price_volatility: str
    flights_per_day: int


# ── Budget Planner ──────────────────────────────────────
class BudgetPlanRequest(BaseModel):
    budget: float
    origin: str
    destination: Optional[str] = "Flexible"
    travel_month: Optional[str] = None


class BudgetOption(BaseModel):
    route: str
    date: str
    airline: str
    price: float
    saving: float
    badge: str


class BudgetPlanResponse(BaseModel):
    options: List[BudgetOption]
    alternatives: List[dict]


# ── Smart Fare Alerts ───────────────────────────────────
class AlertCreate(BaseModel):
    origin: str
    destination: str
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    target_price: float
    notify_on_drop: bool = True
    notify_below_budget: bool = True
    notify_below_average: bool = False
    notify_predicted_rise: bool = False
    notify_email: bool = True


class AlertOut(BaseModel):
    id: str
    origin: str
    destination: str
    date_from: Optional[str]
    date_to: Optional[str]
    target_price: float
    status: str
    current_price: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Heatmap ──────────────────────────────────────────────
class HeatmapDay(BaseModel):
    day: int
    price: float
    level: str    # cheap | average | expensive


class HeatmapResponse(BaseModel):
    month_label: str
    first_weekday: int
    days: List[HeatmapDay]
    cheapest: List[HeatmapDay]


# ── AI Chat (bonus) ──────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    origin: str | None = None
    destination: str | None = None
    travel_date: str | None = None

    
class ChatResponse(BaseModel):
    reply: str
    source: str   # "claude" | "fallback"
