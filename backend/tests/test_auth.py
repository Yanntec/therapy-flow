from conftest import PASSWORD


def test_register_creates_user(client):
    r = client.post(
        "/register",
        json={"name": "Anna", "email": "Anna@Example.com", "password": PASSWORD},
    )
    assert r.status_code == 201
    assert r.json()["email"] == "anna@example.com"  # wird lowercased
    assert "password" not in r.json()
    assert "hashed_password" not in r.json()


def test_register_duplicate_email_rejected(client):
    payload = {"name": "A", "email": "dup@example.com", "password": PASSWORD}
    assert client.post("/register", json=payload).status_code == 201
    assert client.post("/register", json=payload).status_code == 400


def test_login_wrong_password(client):
    client.post(
        "/register",
        json={"name": "A", "email": "a@example.com", "password": PASSWORD},
    )
    r = client.post("/login", json={"email": "a@example.com", "password": "falsch"})
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post("/login", json={"email": "x@example.com", "password": PASSWORD})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/me").status_code in (401, 403)


def test_me_returns_profile(client, user_headers):
    r = client.get("/me", headers=user_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "user@example.com"


def test_inactive_user_cannot_login(client, db_session):
    import models

    client.post(
        "/register",
        json={"name": "A", "email": "off@example.com", "password": PASSWORD},
    )
    u = db_session.query(models.User).filter_by(email="off@example.com").one()
    u.is_active = False
    db_session.commit()
    r = client.post("/login", json={"email": "off@example.com", "password": PASSWORD})
    assert r.status_code == 403