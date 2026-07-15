"""
api/routes/budget.py
─────────────────────────────────────────────
POST /api/budget/plan → given a budget, suggests
destinations/dates that fit, plus multi-modal
alternative routes for extra savings.
"""
from fastapi import APIRouter

from app.db import schemas
from app.utils.helpers import ROUTE_BASE_PRICE, seeded_rng
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/budget", tags=["budget"])

DEST_OPTIONS = [
    {"city": "Delhi", "airline": "IndiGo", "badge": "Best Value"},
    {"city": "Goa", "airline": "SpiceJet", "badge": "Cheapest"},
    {"city": "Jaipur", "airline": "IndiGo", "badge": "Most Savings"},
    {"city": "Pune", "airline": "Air India", "badge": "Premium Pick"},
]


@router.post("/plan", response_model=schemas.BudgetPlanResponse)
def plan_budget(payload: schemas.BudgetPlanRequest):
    rng = seeded_rng(payload.origin, payload.budget, datetime.now().date())
    options = []
    today = datetime.now()

    for i, dest in enumerate(DEST_OPTIONS):
        price_ratio = 0.55 + i * 0.08
        price = round(payload.budget * price_ratio)
        if price > payload.budget:
            continue
        date = today + timedelta(days=14 + i * 2)
        options.append(schemas.BudgetOption(
            route=f"{payload.origin} → {dest['city']}",
            date=date.strftime("%a, %d %b"),
            airline=dest["airline"],
            price=price,
            saving=round(payload.budget - price),
            badge=dest["badge"],
        ))

    alternatives = [
        {"label": f"{payload.origin} → Jaipur + Train to Delhi", "saving": round(payload.budget * 0.18)},
        {"label": f"{payload.origin} → Ahmedabad + Bus to Udaipur", "saving": round(payload.budget * 0.22)},
    ]

    return schemas.BudgetPlanResponse(options=options, alternatives=alternatives)
