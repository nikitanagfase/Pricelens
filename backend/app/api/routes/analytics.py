"""
api/routes/analytics.py
─────────────────────────────────────────────
Powers the Historical Price Dashboard + Festival/
Holiday Impact module + the Price Heatmap Calendar.

Every endpoint now blends REAL data from the
price_snapshots table (logged on every live/mock
flight search — see flights.py) with the original
formula/seeded-random fallback. The more real samples
we have for a route/day/airline, the more the real
average is trusted; with little or no real data yet,
it gracefully falls back to the formula so charts
never look empty or broken.
"""
from datetime import datetime, timedelta
import calendar

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db import schemas, models
from app.utils.helpers import (
    ROUTE_BASE_PRICE, DAY_OF_WEEK_MULTIPLIER, DAY_NAMES, FESTIVALS,
    AIRLINE_NAMES, route_key, seeded_rng,
)
from app.ml.train import AIRLINE_FACTORS, _month_seasonality

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _route_or_default(origin: str | None, destination: str | None) -> str:
    if origin and destination:
        r = route_key(origin, destination)
        if r in ROUTE_BASE_PRICE:
            return r
    return "BOM-DEL"


def _parse_date(value) -> datetime | None:
    """travel_date / recorded_at may come back as str or datetime
    depending on DB driver — normalize to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(value)[: len(fmt) if fmt.count("%") <= 3 else 19], fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _blend(real_avg: float | None, real_count: int, formula_value: float,
           max_weight: float = 0.8, sample_cap: int = 5) -> float:
    """Blend a real DB average with the formula fallback. More real
    samples => more trust in real data, capped so a couple of stray
    searches can't swing a chart wildly."""
    if not real_avg or not real_count:
        return formula_value
    weight = min(real_count / sample_cap, 1.0) * max_weight
    return real_avg * weight + formula_value * (1 - weight)


def _recent_snapshots(db: Session, route: str, days_back: int = 180) -> list[models.PriceSnapshot]:
    since = datetime.now() - timedelta(days=days_back)
    return (
        db.query(models.PriceSnapshot)
        .filter(models.PriceSnapshot.route == route)
        .filter(models.PriceSnapshot.recorded_at >= since)
        .all()
    )


@router.get("/history", response_model=schemas.PriceHistoryResponse)
def price_history(
    origin: str = Query("BOM"), destination: str = Query("DEL"),
    period: str = Query("30d", pattern="^(30d|6m|1y)$"),
    db: Session = Depends(get_db),
):
    route = _route_or_default(origin, destination)
    base = ROUTE_BASE_PRICE[route]
    rng = seeded_rng(route, period)
    today = datetime.now()

    days_back = 30 if period == "30d" else (183 if period == "6m" else 366)
    rows = _recent_snapshots(db, route, days_back)

    points = []
    if period == "30d":
        by_day: dict[str, list[float]] = {}
        for r in rows:
            rec = _parse_date(r.recorded_at)
            if rec:
                by_day.setdefault(rec.strftime("%Y-%m-%d"), []).append(r.price)

        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            mult = DAY_OF_WEEK_MULTIPLIER[d.weekday()] * _month_seasonality(d.month)
            f_avg = base * mult * rng.uniform(0.96, 1.04)
            f_min = f_avg * rng.uniform(0.78, 0.85)
            f_max = f_avg * rng.uniform(1.18, 1.3)

            real_prices = by_day.get(d.strftime("%Y-%m-%d"), [])
            if real_prices:
                r_avg = sum(real_prices) / len(real_prices)
                avg = _blend(r_avg, len(real_prices), f_avg)
                mn = _blend(min(real_prices), len(real_prices), f_min)
                mx = _blend(max(real_prices), len(real_prices), f_max)
            else:
                avg, mn, mx = f_avg, f_min, f_max

            points.append(schemas.HistoryPoint(
                label=d.strftime("%d %b"), avg=round(avg), min=round(mn), max=round(mx),
            ))
    else:
        months = 6 if period == "6m" else 12
        by_month: dict[str, list[float]] = {}
        for r in rows:
            rec = _parse_date(r.recorded_at)
            if rec:
                by_month.setdefault(rec.strftime("%Y-%m"), []).append(r.price)

        for i in range(months - 1, -1, -1):
            d = today - timedelta(days=30 * i)
            mult = _month_seasonality(d.month)
            f_avg = base * mult * rng.uniform(0.95, 1.05)
            f_min = f_avg * rng.uniform(0.75, 0.85)
            f_max = f_avg * rng.uniform(1.2, 1.35)

            real_prices = by_month.get(d.strftime("%Y-%m"), [])
            if real_prices:
                r_avg = sum(real_prices) / len(real_prices)
                avg = _blend(r_avg, len(real_prices), f_avg)
            else:
                avg = f_avg

            points.append(schemas.HistoryPoint(
                label=d.strftime("%b '%y"), avg=round(avg), min=round(f_min), max=round(f_max),
            ))

    return schemas.PriceHistoryResponse(period=period, route=route, points=points)


@router.get("/day-of-week", response_model=schemas.DayOfWeekResponse)
def day_of_week(
    origin: str = Query("BOM"), destination: str = Query("DEL"),
    db: Session = Depends(get_db),
):
    route = _route_or_default(origin, destination)
    base = ROUTE_BASE_PRICE[route]
    rows = _recent_snapshots(db, route)

    by_weekday: dict[int, list[float]] = {i: [] for i in range(7)}
    for r in rows:
        travel = _parse_date(r.travel_date)
        if travel:
            by_weekday[travel.weekday()].append(r.price)

    prices = []
    for i in range(7):
        f_price = base * DAY_OF_WEEK_MULTIPLIER[i]
        real = by_weekday[i]
        if real:
            r_avg = sum(real) / len(real)
            prices.append(round(_blend(r_avg, len(real), f_price)))
        else:
            prices.append(round(f_price))

    return schemas.DayOfWeekResponse(route=route, days=DAY_NAMES, prices=prices)


@router.get("/airlines", response_model=schemas.AirlinePriceResponse)
def airline_comparison(
    origin: str = Query("BOM"), destination: str = Query("DEL"),
    db: Session = Depends(get_db),
):
    route = _route_or_default(origin, destination)
    base = ROUTE_BASE_PRICE[route]
    rows = _recent_snapshots(db, route)

    by_airline: dict[str, list[float]] = {}
    for r in rows:
        if r.airline:
            by_airline.setdefault(r.airline, []).append(r.price)

    prices = []
    for a in AIRLINE_NAMES:
        f_price = base * AIRLINE_FACTORS[a]
        real = by_airline.get(a, [])
        if real:
            r_avg = sum(real) / len(real)
            prices.append(round(_blend(r_avg, len(real), f_price)))
        else:
            prices.append(round(f_price))

    return schemas.AirlinePriceResponse(route=route, airlines=AIRLINE_NAMES, prices=prices)


@router.get("/festivals", response_model=list[schemas.FestivalImpact])
def festival_impact():
    return [schemas.FestivalImpact(**f) for f in FESTIVALS]


@router.get("/route-stats", response_model=schemas.RouteStats)
def route_stats(
    origin: str = Query("BOM"), destination: str = Query("DEL"),
    db: Session = Depends(get_db),
):
    route = _route_or_default(origin, destination)
    base = ROUTE_BASE_PRICE[route]
    rng = seeded_rng(route, "stats")
    rows = _recent_snapshots(db, route)

    formula_prices = [base * DAY_OF_WEEK_MULTIPLIER[i] for i in range(7)]
    f_avg_fare = sum(formula_prices) / 7
    f_cheapest_idx = formula_prices.index(min(formula_prices))

    real_prices = [r.price for r in rows]

    if real_prices:
        r_avg = sum(real_prices) / len(real_prices)
        average_fare = round(_blend(r_avg, len(real_prices), f_avg_fare))
        volatility_ratio = max(real_prices) / min(real_prices) if min(real_prices) else 1
    else:
        average_fare = round(f_avg_fare)
        volatility_ratio = max(formula_prices) / min(formula_prices)

    # cheapest day: use real per-weekday averages if we have enough samples, else formula
    by_weekday: dict[int, list[float]] = {i: [] for i in range(7)}
    for r in rows:
        travel = _parse_date(r.travel_date)
        if travel:
            by_weekday[travel.weekday()].append(r.price)
    if any(len(v) >= 3 for v in by_weekday.values()):
        day_avgs = [
            (sum(v) / len(v)) if v else formula_prices[i]
            for i, v in by_weekday.items()
        ]
        cheapest_idx = day_avgs.index(min(day_avgs))
    else:
        cheapest_idx = f_cheapest_idx

    return schemas.RouteStats(
        popularity_score=min(98, 60 + len(rows)) if rows else rng.randint(72, 98),
        average_fare=average_fare,
        cheapest_day=DAY_NAMES[cheapest_idx],
        best_booking_window="21–45 days",
        price_volatility="Medium" if volatility_ratio < 1.6 else "High",
        flights_per_day=rng.randint(14, 32),
    )


@router.get("/heatmap", response_model=schemas.HeatmapResponse)
def heatmap(
    origin: str = Query("BOM"), destination: str = Query("DEL"),
    db: Session = Depends(get_db),
):
    route = _route_or_default(origin, destination)
    base = ROUTE_BASE_PRICE[route]
    rng = seeded_rng(route, "heatmap", datetime.now().strftime("%Y-%m"))

    now = datetime.now()
    first_weekday, days_in_month = calendar.monthrange(now.year, now.month)
    first_weekday = (first_weekday + 1) % 7

    rows = _recent_snapshots(db, route, days_back=60)
    by_day_of_month: dict[int, list[float]] = {}
    for r in rows:
        travel = _parse_date(r.travel_date)
        if travel and travel.year == now.year and travel.month == now.month:
            by_day_of_month.setdefault(travel.day, []).append(r.price)

    days = []
    for day_num in range(1, days_in_month + 1):
        d = datetime(now.year, now.month, day_num)
        mult = DAY_OF_WEEK_MULTIPLIER[d.weekday()] * _month_seasonality(d.month)
        f_price = base * mult * rng.uniform(0.85, 1.15)

        real = by_day_of_month.get(day_num, [])
        if real:
            r_avg = sum(real) / len(real)
            price = round(_blend(r_avg, len(real), f_price))
        else:
            price = round(f_price)
        days.append({"day": day_num, "price": price})

    prices_only = [d["price"] for d in days]
    lo, hi = min(prices_only), max(prices_only)
    q1, q2 = lo + (hi - lo) * 0.33, lo + (hi - lo) * 0.66

    def level(p):
        return "cheap" if p < q1 else "average" if p < q2 else "expensive"

    full_days = [schemas.HeatmapDay(day=d["day"], price=d["price"], level=level(d["price"])) for d in days]
    cheapest = sorted(full_days, key=lambda x: x.price)[:5]

    return schemas.HeatmapResponse(
        month_label=now.strftime("%B %Y"),
        first_weekday=first_weekday,
        days=full_days,
        cheapest=cheapest,
    )