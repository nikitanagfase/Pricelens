"""
api/routes/predict.py
─────────────────────────────────────────────
POST /api/predict → predicted price + confidence
                    + book/wait verdict + SHAP-based
                    feature importance (the XAI panel)
"""
from fastapi import APIRouter

from app.db import schemas
from app.ml.model import build_feature_row, predict_price
from app.ml.shap_explainer import explain_prediction

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=schemas.PredictionResponse)
def predict(payload: schemas.PredictionRequest):
    feature_row = build_feature_row(
        origin=payload.origin,
        destination=payload.destination,
        travel_date=payload.travel_date,
        days_before_travel=payload.days_before_travel,
        airline=payload.airline or "Any",
    )

    result = predict_price(feature_row)
    importance = explain_prediction(feature_row)

    verdict = "wait" if payload.days_before_travel >= 45 else "book"
    if verdict == "book":
        verdict_message = "✅ Recommended: Book now — prices likely to rise as the date approaches"
    else:
        verdict_message = "⏳ You can wait — there's still room for prices to drop before booking"

    return schemas.PredictionResponse(
        predicted_price=result["predicted_price"],
        confidence=result["confidence"],
        lower_bound=result["lower_bound"],
        upper_bound=result["upper_bound"],
        verdict=verdict,
        verdict_message=verdict_message,
        feature_importance=[schemas.FeatureImportance(**f) for f in importance],
    )
