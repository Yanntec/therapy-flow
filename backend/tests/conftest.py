import os

# Muss VOR dem Import von main/auth/database gesetzt werden
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./ci_test.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import get_db
from main import app

PASSWORD = "StrongPass123!"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register_and_login(client, email, name="Test User"):
    r = client.post(
        "/register",
        json={"name": name, "email": email, "password": PASSWORD},
    )
    assert r.status_code == 201, r.text
    r = client.post("/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def user_headers(client):
    return register_and_login(client, "user@example.com")


@pytest.fixture()
def other_user_headers(client):
    return register_and_login(client, "other@example.com", name="Other")


@pytest.fixture()
def admin_headers(client, db_session):
    headers = register_and_login(client, "admin@example.com", name="Admin")
    user = db_session.query(models.User).filter_by(email="admin@example.com").one()
    user.is_admin = True
    db_session.commit()
    return headers