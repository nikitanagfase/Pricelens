"""
core/config.py
─────────────────────────────────────────────
Loads every environment variable in ONE place.
Every other module imports `settings` from here —
never reads os.environ directly. Keeps config sane.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./pricelens.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Ignav Flight Fares API
    IGNAV_API_KEY: str = ""

    # Anthropic (optional AI assistant)
    ANTHROPIC_API_KEY: str = ""

    # Firebase (optional push notifications)
    FIREBASE_SERVER_KEY: str = ""

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def ignav_configured(self) -> bool:
        return bool(self.IGNAV_API_KEY)


settings = Settings()