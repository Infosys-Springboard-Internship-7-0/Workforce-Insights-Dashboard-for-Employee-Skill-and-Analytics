"""Auth flow: only the seeded admin can log in; wrong creds are rejected; protected routes require a token."""


def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login_success(client):
    r = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "TestPassword123"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["admin"]["email"] == "admin@test.com"
    assert body["admin"]["is_super_admin"] is True


def test_login_wrong_password_rejected(client):
    r = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_email_rejected(client):
    r = client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "whatever"})
    assert r.status_code == 401


def test_protected_route_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    r = client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "admin@test.com"


def test_change_password_flow(client, auth_headers):
    # Use a dedicated throwaway admin for this test rather than mutating the
    # shared seeded admin, since other test files' fixtures depend on the
    # seeded admin's original password staying valid for the whole session.
    create = client.post(
        "/api/admins",
        headers=auth_headers,
        json={"name": "Pw Test Admin", "email": "pwtest@test.com", "password": "OriginalPass123"},
    )
    assert create.status_code == 201

    login = client.post("/api/auth/login", json={"email": "pwtest@test.com", "password": "OriginalPass123"})
    assert login.status_code == 200
    pw_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r = client.post(
        "/api/auth/me/change-password",
        headers=pw_headers,
        json={"current_password": "OriginalPass123", "new_password": "NewPassword456"},
    )
    assert r.status_code == 200

    # old password no longer works
    r = client.post("/api/auth/login", json={"email": "pwtest@test.com", "password": "OriginalPass123"})
    assert r.status_code == 401

    # new password works
    r = client.post("/api/auth/login", json={"email": "pwtest@test.com", "password": "NewPassword456"})
    assert r.status_code == 200
