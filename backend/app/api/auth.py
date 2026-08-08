from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DbSession
from app.models.schemas import Token, UserCreate, UserLogin, UserRead
from app.security import create_access_token
from app.services.auth import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: DbSession):
    try:
        user = create_user(db, str(payload.email), payload.password, payload.full_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Token(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: DbSession):
    user = authenticate_user(db, str(payload.email), payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user
