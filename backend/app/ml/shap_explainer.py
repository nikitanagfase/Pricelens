"""
ml/shap_explainer.py
─────────────────────────────────────────────
Explainable AI (XAI) module — answers "why this price?"

Uses SHAP's TreeExplainer (built for exactly this kind of
gradient-boosted tree model) on the first ensemble member
to get per-feature contribution for THIS SPECIFIC prediction
(not just global importance — this is what makes it genuinely
explainable rather than a fixed bar chart).

We group the 7 raw model features into the 5 human-readable
categories the UI shows, since "route_base_price" means
nothing to an end user but "Route demand index" does.
"""
import numpy as np
import pandas as pd
import shap

from app.ml.model import _load_artifact

FEATURE_GROUPS = {
    "Days before travel": ["days_before_travel"],
    "Season / Time of year": ["day_of_week", "month"],
    "Route demand index": ["route_base_price", "demand_index"],
    "Festival & holiday impact": ["festival_surge"],
    "Airline carrier": ["airline_factor"],
}

GROUP_COLORS = {
    "Days before travel": "#6C63FF",
    "Season / Time of year": "#43D9A5",
    "Route demand index": "#38BDF8",
    "Festival & holiday impact": "#FF6584",
    "Airline carrier": "#FFB347",
}

_explainer_cache = {}


def _get_explainer():
    if "explainer" not in _explainer_cache:
        artifact = _load_artifact()
        first_model = artifact["models"][0]
        _explainer_cache["explainer"] = shap.TreeExplainer(first_model)
        _explainer_cache["cols"] = artifact["feature_columns"]
    return _explainer_cache["explainer"], _explainer_cache["cols"]


def explain_prediction(feature_row: dict) -> list[dict]:
    explainer, cols = _get_explainer()
    X = pd.DataFrame([feature_row])[cols]

    shap_values = explainer.shap_values(X)[0]   # one row -> array of per-feature contributions
    abs_values = dict(zip(cols, np.abs(shap_values)))

    grouped = {}
    for label, feature_names in FEATURE_GROUPS.items():
        grouped[label] = sum(abs_values.get(f, 0) for f in feature_names)

    total = sum(grouped.values()) or 1.0
    result = []
    for label, value in sorted(grouped.items(), key=lambda kv: -kv[1]):
        pct = round((value / total) * 100, 1)
        result.append({"label": label, "pct": pct, "color": GROUP_COLORS[label]})

    return result
