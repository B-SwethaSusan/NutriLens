from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import uuid4

from app.database.session import get_db
from app.models import User
from app.security import decode_access_token, hash_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]
_GUEST_EMAIL = "guest@nutritionrag.internal"
_GUEST_DISPLAY_NAME = "Guest Workspace"
_GUEST_PASSWORD = "guest-password"


def _get_or_create_guest_user(db: DbSession) -> User:
    guest = db.scalar(select(User).where(User.email == _GUEST_EMAIL))
    if guest:
        return guest
    candidate = User(id=str(uuid4()), email=_GUEST_EMAIL, full_name=_GUEST_DISPLAY_NAME, password_hash=hash_password(_GUEST_PASSWORD))
    db.add(candidate)
    try:
        db.commit()
        db.refresh(candidate)
        return candidate
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(User).where(User.email == _GUEST_EMAIL))
        if not existing:
            raise
        return existing


def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)], db: DbSession) -> User:
    if not token:
        return _get_or_create_guest_user(db)
    user_id = decode_access_token(token)
    user = db.get(User, user_id) if user_id else None
    if not user or not user.is_active:
        return _get_or_create_guest_user(db)
    return user


def get_current_user_or_guest(token: Annotated[str | None, Depends(oauth2_scheme)], db: DbSession) -> User | None:
    return get_current_user(token, db)


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOrGuest = Annotated[User | None, Depends(get_current_user_or_guest)]
