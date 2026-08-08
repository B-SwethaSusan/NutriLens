import os

os.environ["DATABASE_URL"] = "sqlite:///./test_nutrition_rag.db"
os.environ["SECRET_KEY"] = "test-secret-key-123456789"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
