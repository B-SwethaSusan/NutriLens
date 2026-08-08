from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password, verify_password


def create_user(db: Session, email: str, password: str, full_name: str | None = None) -> User:
    normalized = email.strip().lower()
    if db.scalar(select(User).where(User.email == normalized)):
        raise ValueError("An account with this email already exists")
    user = User(email=normalized, password_hash=hash_password(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    return user if user and verify_password(password, user.password_hash) else None
