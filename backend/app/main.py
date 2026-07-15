"""
main.py
─────────────────────────────────────────────
FastAPI application entry point.
Run with:  uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db
from app.services.cache_service import cache_status

from app.api.routes import auth, flights, predict, analytics, budget, alerts, chat

app = FastAPI(
    title="SkyFare Insights / PriceLens API",
    description="Flight price intelligence — search, ML prediction, explainable AI, analytics, budget planning, and smart fare alerts.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(predict.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(alerts.router)
app.include_router(chat.router)


@app.on_event("startup")
def on_startup():
    init_db()
    print(f"[startup] DB ready. Cache backend: {cache_status()}. "
          f"Ignav configured: {settings.ignav_configured}")


@app.get("/")
def root():
    return {
        "service": "SkyFare Insights / PriceLens API",
        "status": "running",
        "ignav_mode": "live" if settings.ignav_configured else "mock",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
