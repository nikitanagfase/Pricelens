"""
ml/model.py
─────────────────────────────────────────────
Loads the trained ensemble (once, cached in memory)
and exposes predict_price() — the single function
api/routes/predict.py calls.

Confidence score = how much the 7 ensemble members
agree with each other. Low spread → high confidence.
"""
import os
from datetime import datetime
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from app.ml.train import (
    FEATURE_COLUMNS, AIRLINE_FACTORS, MODEL_PATH, train_and_save,
)
from app.utils.helpers import (
    ROUTE_BASE_PRICE, DAY_OF_WEEK_MULTIPLIER, nearest_festival_surge, route_key,
)


@lru_cache(maxsize=1)
def _load_artifact():
    if not os.path.exists(MODEL_PATH):
        # First-run convenience: auto-train if nobody has run train.py yet.
        print("[model.py] No trained model found — training now (one-time, ~10s)...")
        train_and_save()
    return joblib.load(MODEL_PATH)


def build_feature_row(origin: str, destination: str, travel_date: str,
                       days_before_travel: int, airline: str = "Any") -> dict:
    route = route_key(origin, destination)
    base_price = ROUTE_BASE_PRICE.get(route, 4800)

    try:
        dt = datetime.strptime(travel_date, "%Y-%m-%d")
        dow = dt.weekday()
        month = dt.month
    except ValueError:
        dow, month = 4, datetime.now().month

    festival_surge = nearest_festival_surge(travel_date)
    airline_factor = AIRLINE_FACTORS.get(airline, np.mean(list(AIRLINE_FACTORS.values())))

    # demand_index: simple heuristic — weekends + festival windows = higher demand
    demand_index = 55 + DAY_OF_WEEK_MULTIPLIER.get(dow, 1.0) * 15 + festival_surge * 100
    demand_index = float(np.clip(demand_index, 5, 100))

    return {
        "days_before_travel": days_before_travel,
        "day_of_week": dow,
        "month": month,
        "route_base_price": base_price,
        "festival_surge": festival_surge,
        "airline_factor": airline_factor,
        "demand_index": demand_index,
    }


def predict_price(feature_row: dict) -> dict:
    artifact = _load_artifact()
    models = artifact["models"]
    cols = artifact["feature_columns"]

    X = pd.DataFrame([feature_row])[cols]
    preds = np.array([m.predict(X)[0] for m in models])

    mean_pred = float(np.mean(preds))
    std_pred = float(np.std(preds))

    # Confidence: tight ensemble agreement -> high score.
    # Typical std is ~2-6% of price for this dataset; we map that to 60-97%.
    rel_spread = std_pred / max(mean_pred, 1)
    confidence = int(np.clip(97 - rel_spread * 600, 60, 97))

    return {
        "predicted_price": round(mean_pred, -1),     # round to nearest 10
        "confidence": confidence,
        "lower_bound": round(mean_pred - 1.64 * std_pred, -1),
        "upper_bound": round(mean_pred + 1.64 * std_pred, -1),
        "std": std_pred,
    }
