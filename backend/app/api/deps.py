"""
api/deps.py
─────────────────────────────────────────────
Shared dependencies injected into route handlers
via FastAPI's Depends(). Two jobs:
  1. get_db        → a DB session per-request, closed after
  2. get_current_user → decodes the JWT bearer token
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import crud
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Raises 401 if no/invalid token. Use for protected routes."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Like get_current_user but never raises — returns None if not logged in.
    Used on routes (like search) that work for guests too."""
    if not token:
        return None
    email = decode_access_token(token)
    if not email:
        return None
    return crud.get_user_by_email(db, email)
