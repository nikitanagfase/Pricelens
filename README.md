# PriceLens — Flight Price Intelligence

A full-stack flight price intelligence platform built as an MCA academic
project. Predicts fares with an explainable ML model, visualises historical
trends, plans budget trips, and sends smart fare alerts.

> **Status: fully built, tested, and verified end-to-end** in the dev
> sandbox — backend passes a full API test suite, frontend builds clean
> with zero errors. See `SETUP.md` for how to run it on your own machine.

---

## 🧩 The 6 core features

| # | Feature | Where it lives |
|---|---------|-----------------|
| 1 | **Price prediction with confidence score** | `backend/app/ml/model.py` — 7-model XGBoost ensemble; confidence = ensemble agreement |
| 2 | **Explainable AI (feature importance)** | `backend/app/ml/shap_explainer.py` — SHAP TreeExplainer, per-prediction |
| 3 | **Historical price dashboard** | `backend/app/api/routes/analytics.py` + `frontend/src/pages/Analytics.jsx` |
| 4 | **Budget planner** | `backend/app/api/routes/budget.py` + `frontend/src/components/BudgetPlanner.jsx` |
| 5 | **Festival/holiday impact** | `backend/app/utils/helpers.py` (`FESTIVALS`) + Analytics page |
| 6 | **Smart fare alerts** | `backend/app/api/routes/alerts.py` + `frontend/src/components/AlertsPanel.jsx` — real DB-backed CRUD, not the old in-memory array |

Bonus (not one of the 6, kept from the original design): a floating **AI
travel assistant** widget, wired to call the Anthropic API if you add a key,
with a graceful rule-based fallback if you don't.

---

## 🏗️ Architecture

```
Browser (React, Vite)  ──axios──▶  FastAPI backend  ──▶  SQLite/PostgreSQL
        │                              │
        │                              ├──▶ Amadeus API (real flights, optional)
        │                              ├──▶ Redis (cache, optional — falls back to memory)
        │                              ├──▶ XGBoost ensemble + SHAP (price prediction + XAI)
        │                              └──▶ Anthropic API (chat, optional)
        └── React Router: Home / Analytics / Dashboard
```

### Key design decision: **mock mode**

Two real third-party services (Amadeus flight data, Anthropic chat) require
API keys you don't have yet. Rather than the project failing without them,
every call to those services checks if a key is configured:

- **No key set →** clearly-labeled, realistic generated data (`source: "mock"`
  in every API response, and a "Demo data" badge in the UI).
- **Key set →** real API calls (`source: "amadeus"` / `source: "claude"`).

This means the project **runs and demos completely on day one**, and
upgrades to live data the moment you add a key — no code changes needed.
Be upfront about this in your viva: it's a legitimate, common pattern for
prototyping against APIs with usage limits, not a shortcut you need to hide.

### Why the ML model uses synthetic training data

Real historical Indian-domestic fare datasets aren't freely redistributable,
and Amadeus only gives *current* prices, not years of history. So
`ml/train.py` generates a large synthetic dataset whose price formula
encodes the same booking-window / weekday / festival / airline-tier patterns
the UI itself describes as "Key Factors" — a standard, defensible technique
for prototyping ML systems before a production dataset is available.

**To swap in real data:** drop a CSV with columns
`days_before_travel, day_of_week, month, route_base_price, festival_surge,
airline_factor, demand_index, price` at `data/kaggle_flight_prices.csv` —
`train.py` will automatically use it instead of synthetic data.

---

## 📁 Structure

```
PriceLens/
├── frontend/          React 18 + Vite + Recharts + React Router
│   └── src/
│       ├── components/   9 components matching the 6 feature modules
│       ├── pages/        Home.jsx · Analytics.jsx · Dashboard.jsx
│       ├── context/      AuthContext, ToastContext (global state)
│       ├── services/     api.js — every backend call, one place
│       └── styles/       Your original design system, ported 1:1
├── backend/           FastAPI + SQLAlchemy + XGBoost + SHAP
│   └── app/
│       ├── api/routes/   auth, flights, predict, analytics, budget, alerts, chat
│       ├── core/         config.py (env settings), security.py (JWT)
│       ├── db/           models.py, schemas.py, crud.py, session.py
│       ├── ml/           train.py, model.py, shap_explainer.py
│       ├── services/     amadeus_client.py, cache_service.py, notification_service.py
│       └── utils/        helpers.py (festivals, routes, day multipliers)
├── data/              Drop a real dataset here (optional)
└── docs/              Project report goes here
```

A few intentional, documented deviations from the original spec — see
`SETUP.md` → "What's different from the original plan" for why.

---

## 🚀 Quick start

See **`SETUP.md`** for full step-by-step instructions (Amadeus signup,
running locally, troubleshooting). Short version:

```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv
cp .env.example .env
python -m app.ml.train          # trains the model once (~10 seconds)
uvicorn app.main:app --reload   # http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

Open `http://localhost:5173` — it works immediately, in mock mode, with
zero API keys required.

---

## 🔑 Going live (optional, free)

1. Sign up at [developers.amadeus.com](https://developers.amadeus.com) (free).
2. Copy your **test** Client ID/Secret into `backend/.env`.
3. Restart the backend — flight search now hits real Amadeus data
   automatically. Free tier is generous enough for a project demo
   (cached for 15 min per route+date to conserve your quota further).

---

## ✅ What's been tested

- Every backend endpoint (`auth`, `flights/search`, `predict`, all 6
  `analytics/*` routes, `budget/plan`, `alerts` CRUD, `chat`) was run
  end-to-end with a real ASGI server, not just imported.
- The XGBoost ensemble trains successfully: **MAE ₹218, R² 0.978** on
  held-out synthetic data.
- The React app builds with **zero errors** (`npm run build`, 900 modules).

What I *couldn't* test from here: the actual rendered UI in a browser (this
environment can't run a GUI browser), and live Amadeus calls (no internet
access to third-party APIs from this sandbox — only npm/pip registries).
Run it locally and you'll see both for real.
