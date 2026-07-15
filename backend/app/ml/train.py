"""
ml/train.py
─────────────────────────────────────────────
OFFLINE script — run this once (`python -m app.ml.train`)
to (re)build the price-prediction model.

Why synthetic data?
Real historical Indian domestic fare datasets are not
freely redistributable, and the live Ignav API only
gives *current* prices, not years of history. So we
generate a large synthetic dataset whose price formula
encodes well-documented real-world patterns (booking
window, weekday, festival surges, airline tier, seasonal
demand) — exactly what's described in the project's
own "Key Factors" UI. This is a standard, legitimate
technique for prototyping ML systems before swapping in
a production dataset (e.g. a Kaggle flight-price corpus
dropped into data/kaggle_flight_prices.csv — see
load_kaggle_dataset_if_present() below).

The model is an ENSEMBLE of 7 XGBoost regressors trained
on different bootstrap samples. We use the *disagreement*
between ensemble members as our confidence signal — if all
7 trees agree, we're confident; if they scatter, we're not.
This is a simple, defensible, classroom-explainable way to
get uncertainty estimates out of a model that doesn't
natively produce them.
"""
import os
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from datetime import datetime
from sqlalchemy import func
from app.db.session import SessionLocal
from app.db.models import PriceSnapshot
from app.utils.helpers import nearest_festival_surge

from app.utils.helpers import ROUTE_BASE_PRICE, DAY_OF_WEEK_MULTIPLIER, AIRLINE_NAMES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "price_model.pkl")

FEATURE_COLUMNS = [
    "days_before_travel", "day_of_week", "month",
    "route_base_price", "festival_surge", "airline_factor", "demand_index",
]

AIRLINE_FACTORS = {  # budget vs premium carrier price multiplier
    "IndiGo": 0.95, "SpiceJet": 0.90, "AirAsia India": 0.88,
    "Air India": 1.08, "Vistara": 1.22,
}


def _days_before_multiplier(days: int) -> float:
    if days < 7:
        return 1.32
    if days < 14:
        return 1.18
    if days < 30:
        return 1.0
    if days < 60:
        return 0.88
    return 0.82


def _month_seasonality(month: int) -> float:
    # Oct-Dec (festival/winter holidays) and May-Jun (summer holidays) cost more
    peak_months = {10: 1.25, 11: 1.15, 12: 1.30, 5: 1.12, 6: 1.10}
    return peak_months.get(month, 1.0)


def generate_synthetic_dataset(n_samples: int = 25000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    routes = list(ROUTE_BASE_PRICE.keys())

    rows = []
    for _ in range(n_samples):
        route = routes[rng.integers(0, len(routes))]
        base_price = ROUTE_BASE_PRICE[route]
        days_before = int(rng.integers(0, 120))
        dow = int(rng.integers(0, 7))
        month = int(rng.integers(1, 13))
        airline = AIRLINE_NAMES[rng.integers(0, len(AIRLINE_NAMES))]
        airline_factor = AIRLINE_FACTORS[airline]
        festival_surge = max(0.0, rng.normal(0.05, 0.12))   # mostly small, occasionally big
        festival_surge = min(festival_surge, 0.7)
        demand_index = float(np.clip(rng.normal(60, 20), 5, 100))

        price = (
            base_price
            * DAY_OF_WEEK_MULTIPLIER[dow]
            * _month_seasonality(month)
            * _days_before_multiplier(days_before)
            * airline_factor
            * (1 + festival_surge)
            * (0.85 + demand_index / 200)   # demand nudges price up/down slightly
        )
        price *= float(rng.normal(1.0, 0.04))   # small random noise
        price = max(1800, round(price, 0))

        rows.append({
            "route": route,
            "days_before_travel": days_before,
            "day_of_week": dow,
            "month": month,
            "route_base_price": base_price,
            "festival_surge": festival_surge,
            "airline": airline,
            "airline_factor": airline_factor,
            "demand_index": demand_index,
            "price": price,
        })

    return pd.DataFrame(rows)


def load_kaggle_dataset_if_present() -> pd.DataFrame | None:
    """If you drop a real dataset at data/kaggle_flight_prices.csv with
    columns matching FEATURE_COLUMNS + 'price', this will use it instead
    of synthetic data. Optional — purely a convenience hook."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "kaggle_flight_prices.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if "price" in df.columns and all(c in df.columns for c in FEATURE_COLUMNS):
                print(f"[train.py] Using real dataset from {path} ({len(df)} rows)")
                return df
        except Exception as e:
            print(f"[train.py] Could not load Kaggle dataset ({e}), falling back to synthetic.")
    return None

MIN_LIVE_SAMPLES = 300  # below this, real data too thin to train reliably — fallback to synthetic


def load_live_snapshots_if_sufficient() -> pd.DataFrame | None:
    """Pulls real Ignav-sourced price_snapshots from the DB and converts
    them into the same feature shape the model expects. Only used once
    enough real searches have accumulated (see MIN_LIVE_SAMPLES)."""
    db = SessionLocal()
    try:
        count = (
            db.query(func.count(PriceSnapshot.id))
            .filter(PriceSnapshot.source == "ignav")
            .filter(PriceSnapshot.days_before_travel.isnot(None))
            .scalar()
        )
        if count < MIN_LIVE_SAMPLES:
            print(f"[train.py] Only {count} live snapshots (need {MIN_LIVE_SAMPLES}+) — using synthetic data.")
            return None

        rows = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.source == "ignav")
            .filter(PriceSnapshot.days_before_travel.isnot(None))
            .all()
        )

        records = []
        for r in rows:
            try:
                dt = datetime.strptime(r.travel_date, "%Y-%m-%d") if r.travel_date else None
                dow = dt.weekday() if dt else 4
                month = dt.month if dt else datetime.now().month
            except ValueError:
                dow, month = 4, datetime.now().month

            base_price = ROUTE_BASE_PRICE.get(r.route, 4800)
            airline_factor = AIRLINE_FACTORS.get(r.airline, sum(AIRLINE_FACTORS.values()) / len(AIRLINE_FACTORS))
            festival_surge = nearest_festival_surge(r.travel_date) if r.travel_date else 0.0
            demand_index = float(np.clip(55 + DAY_OF_WEEK_MULTIPLIER.get(dow, 1.0) * 15 + festival_surge * 100, 5, 100))

            records.append({
                "days_before_travel": r.days_before_travel,
                "day_of_week": dow,
                "month": month,
                "route_base_price": base_price,
                "festival_surge": festival_surge,
                "airline_factor": airline_factor,
                "demand_index": demand_index,
                "price": r.price,
            })

        print(f"[train.py] Using {len(records)} REAL live snapshots from price_snapshots table.")
        return pd.DataFrame(records)
    finally:
        db.close()

def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)

    df = load_live_snapshots_if_sufficient()
    if df is None:
        df = load_kaggle_dataset_if_present()
    if df is None:
        print("[train.py] Generating synthetic training dataset...")
        df = generate_synthetic_dataset()

    X = df[FEATURE_COLUMNS]
    y = df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    print("[train.py] Training 7-member XGBoost ensemble...")
    models = []
    for i in range(7):
        model = XGBRegressor(
            n_estimators=180,
            max_depth=5,
            learning_rate=0.07,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=i,
            objective="reg:squarederror",
        )
        # bootstrap resample for ensemble diversity
        boot_idx = np.random.default_rng(i).integers(0, len(X_train), len(X_train))
        model.fit(X_train.iloc[boot_idx], y_train.iloc[boot_idx])
        models.append(model)

    preds = np.mean([m.predict(X_test) for m in models], axis=0)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"[train.py] Validation MAE: ₹{mae:.0f}   R²: {r2:.3f}")

    artifact = {
        "models": models,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": {"mae": float(mae), "r2": float(r2)},
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"[train.py] Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()
