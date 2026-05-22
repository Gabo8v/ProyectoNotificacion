import os
import uuid
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["DATABASE_URL"] = "postgresql+psycopg2://user:password@localhost:5432/notificaciones_test"

from app.database import Base, get_db
from app.routers import dashboard, health, notifications, templates, whatsapp

TEST_APP = FastAPI()
TEST_APP.include_router(health.router)
TEST_APP.include_router(notifications.router)
TEST_APP.include_router(templates.router)
TEST_APP.include_router(whatsapp.router)
TEST_APP.include_router(dashboard.router)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    engine = create_engine(os.environ["DATABASE_URL"])
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db

    TEST_APP.dependency_overrides[get_db] = override_get_db
    with TestClient(TEST_APP) as c:
        yield c
    TEST_APP.dependency_overrides.clear()


@pytest.fixture
def create_user(db: Session, request: pytest.FixtureRequest):
    from app.models.user import User
    import uuid
    suffix = uuid.uuid4().hex[:8]
    user = User(
        name=f"Test User {suffix}",
        email=f"testuser_{suffix}@example.com",
        phone=f"5493875360{suffix[:4]}",
    )
    db.add(user)
    db.commit()
    return user
